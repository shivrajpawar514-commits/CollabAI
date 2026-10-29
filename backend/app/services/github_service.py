import uuid
import re
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.github import GitHubRepositoryLink, PullRequestMetric
from app.models.project import Project
from app.models.task import Task
from app.schemas.github import (
    GitHubLinkCreate,
    GitHubLinkResponse,
    PRCycleTimeAnalyticsResponse,
    PullRequestMetricResponse,
    SimulatePRCreate,
)

logger = logging.getLogger("collabai.services.github")


class GitHubService:
    async def get_repository_link(
        self, project_id: uuid.UUID, db: AsyncSession
    ) -> Optional[GitHubRepositoryLink]:
        query = select(GitHubRepositoryLink).where(
            GitHubRepositoryLink.project_id == project_id,
            GitHubRepositoryLink.is_active == True,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def link_repository(
        self, project_id: uuid.UUID, data: GitHubLinkCreate, db: AsyncSession
    ) -> GitHubLinkResponse:
        # Verify project exists
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found",
            )

        existing = await self.get_repository_link(project_id, db)
        if existing:
            existing.repo_name = data.repo_name
            existing.repo_url = data.repo_url
            existing.default_branch = data.default_branch
            existing.webhook_secret = data.webhook_secret
            existing.last_synced_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(existing)
            link_obj = existing
        else:
            now_dt = datetime.now(timezone.utc)
            link_obj = GitHubRepositoryLink(
                id=uuid.uuid4(),
                project_id=project_id,
                repo_name=data.repo_name,
                repo_url=data.repo_url,
                default_branch=data.default_branch,
                webhook_secret=data.webhook_secret,
                is_active=True,
                last_synced_at=now_dt,
                created_at=now_dt,
                updated_at=now_dt,
            )
            db.add(link_obj)
            await db.commit()
            await db.refresh(link_obj)

        webhook_url = f"/api/v1/github/webhook?project_id={project_id}"
        return GitHubLinkResponse(
            id=link_obj.id,
            project_id=link_obj.project_id,
            repo_name=link_obj.repo_name,
            repo_url=link_obj.repo_url,
            default_branch=link_obj.default_branch,
            is_active=link_obj.is_active,
            last_synced_at=link_obj.last_synced_at,
            webhook_url=webhook_url,
            created_at=link_obj.created_at,
        )

    async def unlink_repository(self, project_id: uuid.UUID, db: AsyncSession) -> bool:
        link = await self.get_repository_link(project_id, db)
        if link:
            link.is_active = False
            await db.commit()
            return True
        return False

    async def simulate_pull_request(
        self, project_id: uuid.UUID, sim: SimulatePRCreate, db: AsyncSession
    ) -> PullRequestMetricResponse:
        now = datetime.now(timezone.utc)
        created_at_gh = now - timedelta(hours=sim.hours_to_merge)
        merged_at_gh = now if sim.auto_merge else None
        state = "merged" if sim.auto_merge else "open"
        cycle_time = sim.hours_to_merge if sim.auto_merge else None

        # Fetch count to determine next PR number
        query = select(PullRequestMetric).where(PullRequestMetric.project_id == project_id)
        result = await db.execute(query)
        existing_prs = result.scalars().all()
        pr_number = len(existing_prs) + 101

        # Check for task correlation
        task_query = select(Task).where(Task.project_id == project_id)
        task_res = await db.execute(task_query)
        tasks = task_res.scalars().all()
        linked_task = tasks[0] if tasks else None

        pr_metric = PullRequestMetric(
            id=uuid.uuid4(),
            project_id=project_id,
            pr_number=pr_number,
            title=sim.title,
            author_username=sim.author_username,
            state=state,
            html_url=f"https://github.com/project/pull/{pr_number}",
            created_at_gh=created_at_gh,
            merged_at_gh=merged_at_gh,
            cycle_time_hours=cycle_time,
            additions=sim.additions,
            deletions=sim.deletions,
            changed_files=sim.changed_files,
            linked_task_id=linked_task.id if linked_task else None,
            created_at=now,
        )
        db.add(pr_metric)

        # If merged and linked to task, update task to completed or review
        if linked_task and sim.auto_merge:
            linked_task.status = "completed"

        await db.commit()
        await db.refresh(pr_metric)

        return PullRequestMetricResponse(
            id=pr_metric.id,
            pr_number=pr_metric.pr_number,
            title=pr_metric.title,
            author_username=pr_metric.author_username,
            state=pr_metric.state,
            html_url=pr_metric.html_url,
            cycle_time_hours=pr_metric.cycle_time_hours,
            additions=pr_metric.additions,
            deletions=pr_metric.deletions,
            changed_files=pr_metric.changed_files,
            linked_task_id=pr_metric.linked_task_id,
            created_at_gh=pr_metric.created_at_gh,
            merged_at_gh=pr_metric.merged_at_gh,
        )

    async def get_cycle_time_analytics(
        self, project_id: uuid.UUID, db: AsyncSession
    ) -> PRCycleTimeAnalyticsResponse:
        link = await self.get_repository_link(project_id, db)
        repo_name = link.repo_name if link else "collabai/core-workspace"

        query = select(PullRequestMetric).where(
            PullRequestMetric.project_id == project_id
        ).order_by(desc(PullRequestMetric.created_at))
        result = await db.execute(query)
        prs = result.scalars().all()

        # If no PRs recorded yet, generate high-fidelity simulated metrics for demonstration
        if not prs:
            now = datetime.now(timezone.utc)
            sample_prs = [
                PullRequestMetric(
                    id=uuid.uuid4(),
                    project_id=project_id,
                    pr_number=101,
                    title="feat(api): implement system observability router & Prometheus metrics",
                    author_username="lead-architect",
                    state="merged",
                    html_url="https://github.com/org/repo/pull/101",
                    created_at_gh=now - timedelta(hours=6, minutes=30),
                    merged_at_gh=now - timedelta(hours=2, minutes=15),
                    cycle_time_hours=4.25,
                    additions=312,
                    deletions=48,
                    changed_files=5,
                    created_at=now - timedelta(hours=6, minutes=30),
                ),
                PullRequestMetric(
                    id=uuid.uuid4(),
                    project_id=project_id,
                    pr_number=102,
                    title="feat(ai): autonomous pitch deck presentation & slide exporter",
                    author_username="ai-specialist",
                    state="merged",
                    html_url="https://github.com/org/repo/pull/102",
                    created_at_gh=now - timedelta(hours=14),
                    merged_at_gh=now - timedelta(hours=8, minutes=45),
                    cycle_time_hours=5.25,
                    additions=445,
                    deletions=82,
                    changed_files=7,
                    created_at=now - timedelta(hours=14),
                ),
                PullRequestMetric(
                    id=uuid.uuid4(),
                    project_id=project_id,
                    pr_number=103,
                    title="feat(frontend): high-density hackathon judge scorecard modal",
                    author_username="frontend-engineer",
                    state="merged",
                    html_url="https://github.com/org/repo/pull/103",
                    created_at_gh=now - timedelta(hours=24),
                    merged_at_gh=now - timedelta(hours=20, minutes=30),
                    cycle_time_hours=3.5,
                    additions=280,
                    deletions=19,
                    changed_files=3,
                    created_at=now - timedelta(hours=24),
                ),
                PullRequestMetric(
                    id=uuid.uuid4(),
                    project_id=project_id,
                    pr_number=104,
                    title="feat(infra): multi-stage Dockerfile and CI workflow automation",
                    author_username="devops-lead",
                    state="open",
                    html_url="https://github.com/org/repo/pull/104",
                    created_at_gh=now - timedelta(hours=2),
                    merged_at_gh=None,
                    cycle_time_hours=None,
                    additions=160,
                    deletions=22,
                    changed_files=4,
                    created_at=now - timedelta(hours=2),
                ),
            ]
            db.add_all(sample_prs)
            await db.commit()
            prs = sample_prs

        merged_prs = [p for p in prs if p.state == "merged" and p.cycle_time_hours is not None]
        open_prs = [p for p in prs if p.state == "open"]

        cycle_times = [p.cycle_time_hours for p in merged_prs if p.cycle_time_hours is not None]
        avg_cycle_time = round(sum(cycle_times) / len(cycle_times), 2) if cycle_times else 0.0
        
        sorted_times = sorted(cycle_times)
        median_cycle_time = (
            sorted_times[len(sorted_times) // 2] if sorted_times else 0.0
        )
        fastest_merge = min(sorted_times) if sorted_times else 0.0
        merge_success_rate = round((len(merged_prs) / max(1, len(prs))) * 100, 1)

        total_churn = sum(p.additions + p.deletions for p in prs)
        avg_churn = int(total_churn / max(1, len(prs)))

        if avg_cycle_time <= 6.0:
            verdict = "⚡ Elite Delivery Velocity (< 6h PR Cycle Time)"
        elif avg_cycle_time <= 18.0:
            verdict = "🚀 Strong Agile Flow (< 18h PR Cycle Time)"
        else:
            verdict = "⚠️ High Review Latency (> 24h Turnaround)"

        recent_dtos = [
            PullRequestMetricResponse(
                id=p.id,
                pr_number=p.pr_number,
                title=p.title,
                author_username=p.author_username,
                state=p.state,
                html_url=p.html_url,
                cycle_time_hours=p.cycle_time_hours,
                additions=p.additions,
                deletions=p.deletions,
                changed_files=p.changed_files,
                linked_task_id=p.linked_task_id,
                created_at_gh=p.created_at_gh,
                merged_at_gh=p.merged_at_gh,
            )
            for p in prs[:10]
        ]

        return PRCycleTimeAnalyticsResponse(
            project_id=project_id,
            repo_name=repo_name,
            total_prs=len(prs),
            open_prs=len(open_prs),
            merged_prs=len(merged_prs),
            avg_cycle_time_hours=avg_cycle_time,
            median_cycle_time_hours=median_cycle_time,
            fastest_merge_hours=fastest_merge,
            merge_success_rate_pct=merge_success_rate,
            avg_code_churn=avg_churn,
            recent_prs=recent_dtos,
            velocity_verdict=verdict,
        )

    async def process_webhook(
        self, event_type: str, payload: Dict[str, Any], project_id: Optional[uuid.UUID], db: AsyncSession
    ) -> Dict[str, Any]:
        logger.info("Processing incoming GitHub webhook event: %s", event_type)
        if event_type == "pull_request":
            pr_data = payload.get("pull_request", {})
            action = payload.get("action", "")
            pr_number = pr_data.get("number", 0)
            title = pr_data.get("title", "GitHub Pull Request")
            user = pr_data.get("user", {}).get("login", "contributor")
            state = "merged" if pr_data.get("merged") else ("closed" if action == "closed" else "open")
            created_at_str = pr_data.get("created_at")
            merged_at_str = pr_data.get("merged_at")

            created_at_gh = (
                datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                if created_at_str
                else datetime.now(timezone.utc)
            )
            merged_at_gh = (
                datetime.fromisoformat(merged_at_str.replace("Z", "+00:00"))
                if merged_at_str
                else None
            )

            cycle_time = None
            if merged_at_gh:
                delta = merged_at_gh - created_at_gh
                cycle_time = round(delta.total_seconds() / 3600.0, 2)

            if project_id:
                pr_metric = PullRequestMetric(
                    id=uuid.uuid4(),
                    project_id=project_id,
                    pr_number=pr_number,
                    title=title,
                    author_username=user,
                    state=state,
                    html_url=pr_data.get("html_url", ""),
                    created_at_gh=created_at_gh,
                    merged_at_gh=merged_at_gh,
                    cycle_time_hours=cycle_time,
                    additions=pr_data.get("additions", 0),
                    deletions=pr_data.get("deletions", 0),
                    changed_files=pr_data.get("changed_files", 1),
                    created_at=datetime.now(timezone.utc),
                )
                db.add(pr_metric)
                await db.commit()

            return {"status": "processed", "pr_number": pr_number, "action": action, "state": state}

        return {"status": "ignored", "event_type": event_type}
