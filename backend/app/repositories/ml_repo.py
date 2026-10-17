import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Set, Tuple
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.ml import RecommendationFeedback
from app.models.project import Project, ProjectSkill
from app.models.team import Team, TeamMember
from app.models.task import Task, TaskDependency, Milestone
from app.models.user import User
from app.models.profile import Profile
from app.models.skill import UserSkill, Skill


class MLRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_feedback(
        self,
        project_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        candidate_id: uuid.UUID,
        action: str,
        match_score: int,
        ml_rank_score: int,
        feature_vector_json: Optional[Dict[str, Any]] = None,
    ) -> RecommendationFeedback:
        fb = RecommendationFeedback(
            id=uuid.uuid4(),
            project_id=project_id,
            reviewer_id=reviewer_id,
            candidate_id=candidate_id,
            action=action,
            match_score=match_score,
            ml_rank_score=ml_rank_score,
            feature_vector_json=feature_vector_json or {},
        )
        self.db.add(fb)
        await self.db.commit()
        await self.db.refresh(fb)
        return fb

    async def get_project_sprint_metrics(self, project_id: uuid.UUID) -> Dict[str, Any]:
        # 1. Fetch Project & Deadlines
        proj_stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.milestones),
                selectinload(Project.tasks).selectinload(Task.dependencies),
            )
        )
        proj_res = await self.db.execute(proj_stmt)
        project = proj_res.scalar_one_or_none()

        if not project:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "blocked_tasks": 0,
                "days_left": 30,
                "team_size": 1,
                "recent_weekly_velocity": 2.0,
            }

        # 2. Team Size
        team_stmt = select(Team).where(Team.project_id == project_id).options(selectinload(Team.members))
        team_res = await self.db.execute(team_stmt)
        team = team_res.scalar_one_or_none()
        team_size = max(1, len(team.members)) if team and team.members else 1

        # 3. Tasks & Dependencies
        all_tasks = project.tasks or []
        total_tasks = len(all_tasks)
        completed_tasks = sum(1 for t in all_tasks if t.status == "completed")

        # Create quick lookup for task statuses
        task_status_map = {t.id: t.status for t in all_tasks}

        # Blocked tasks: open tasks whose dependencies are not all completed
        blocked_tasks = 0
        now_utc = datetime.now(timezone.utc)
        completed_last_7_days = 0

        for t in all_tasks:
            if t.status != "completed":
                # Check dependencies
                deps = t.dependencies or []
                for dep in deps:
                    prereq_status = task_status_map.get(dep.prerequisite_task_id)
                    if prereq_status and prereq_status != "completed":
                        blocked_tasks += 1
                        break
            else:
                # Check recent velocity (completed in last 7 days)
                if t.updated_at and (now_utc - t.updated_at).days <= 7:
                    completed_last_7_days += 1

        # Estimate weekly velocity (at least 0.5)
        recent_velocity = max(0.5, float(completed_last_7_days))

        # 4. Calculate Days Left
        # Look for earliest milestone deadline or fallback to 30 days
        days_left = 30
        future_deadlines: List[datetime] = []

        for m in (project.milestones or []):
            if m.deadline and m.status != "completed":
                deadline_dt = m.deadline
                if deadline_dt.tzinfo is None:
                    deadline_dt = deadline_dt.replace(tzinfo=timezone.utc)
                diff_days = (deadline_dt - now_utc).days
                future_deadlines.append(deadline_dt)

        if future_deadlines:
            earliest = min(future_deadlines)
            days_left = max(-10, (earliest - now_utc).days)

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "blocked_tasks": blocked_tasks,
            "days_left": days_left,
            "team_size": team_size,
            "recent_weekly_velocity": recent_velocity,
        }

    async def get_project_skills_and_team_skills(
        self,
        project_id: uuid.UUID
    ) -> Tuple[List[str], Set[str]]:
        # Required project skills
        proj_stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.required_skills).joinedload(ProjectSkill.skill)
            )
        )
        proj_res = await self.db.execute(proj_stmt)
        project = proj_res.scalar_one_or_none()
        required_skills = [
            ps.skill.name.lower() for ps in (project.required_skills or []) if ps.skill
        ]

        # Existing team members' owned skills
        team_stmt = (
            select(Team)
            .where(Team.project_id == project_id)
            .options(selectinload(Team.members))
        )
        team_res = await self.db.execute(team_stmt)
        team = team_res.scalar_one_or_none()
        team_member_ids = [m.user_id for m in team.members] if team and team.members else []
        if project and project.owner_id not in team_member_ids:
            team_member_ids.append(project.owner_id)

        team_skills: Set[str] = set()
        if team_member_ids:
            skill_stmt = (
                select(UserSkill)
                .where(UserSkill.user_id.in_(team_member_ids))
                .options(joinedload(UserSkill.skill))
            )
            skill_res = await self.db.execute(skill_stmt)
            for us in skill_res.scalars().all():
                if us.skill:
                    team_skills.add(us.skill.name.lower())

        return required_skills, team_skills

    async def get_candidate_students(
        self,
        exclude_user_ids: List[uuid.UUID],
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(User)
            .where(and_(User.is_active == True, User.id.notin_(exclude_user_ids)))
            .options(
                joinedload(User.profile),
                selectinload(User.skills).joinedload(UserSkill.skill),
            )
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        users = res.scalars().unique().all()

        candidates: List[Dict[str, Any]] = []
        for u in users:
            prof = u.profile
            skills = [us.skill.name for us in (u.skills or []) if us.skill]
            candidates.append({
                "user_id": str(u.id),
                "full_name": u.full_name,
                "email": u.email,
                "avatar_url": u.avatar_url,
                "college": prof.college if prof else None,
                "branch": prof.branch if prof else None,
                "year": prof.year if prof else None,
                "bio": prof.bio if prof else "",
                "interests": prof.interests if prof and prof.interests else [],
                "preferred_roles": prof.preferred_roles if prof and prof.preferred_roles else [],
                "availability_hours_per_week": prof.availability_hours_per_week if prof else 10,
                "github_username": prof.github_username if prof else None,
                "skills": skills,
            })

        return candidates
