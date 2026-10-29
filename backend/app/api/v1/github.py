import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.github import (
    GitHubLinkCreate,
    GitHubLinkResponse,
    PRCycleTimeAnalyticsResponse,
    PullRequestMetricResponse,
    SimulatePRCreate,
)
from app.services.github_service import GitHubService

router = APIRouter(tags=["GitHub Integration & PR Cycle Time"])
_github_service = GitHubService()


@router.post(
    "/projects/{project_id}/github/link",
    response_model=GitHubLinkResponse,
    summary="Connect GitHub repository to project workspace",
)
async def link_project_github(
    project_id: uuid.UUID,
    data: GitHubLinkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Links a GitHub repository to the project to enable automated PR tracking,
    cycle time telemetry, and task status synchronization.
    """
    return await _github_service.link_repository(project_id, data, db)


@router.get(
    "/projects/{project_id}/github/status",
    response_model=Optional[GitHubLinkResponse],
    summary="Get GitHub repository connection status",
)
async def get_project_github_status(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves the connected GitHub repository link and sync status.
    """
    link = await _github_service.get_repository_link(project_id, db)
    if not link:
        return None
    return GitHubLinkResponse(
        id=link.id,
        project_id=link.project_id,
        repo_name=link.repo_name,
        repo_url=link.repo_url,
        default_branch=link.default_branch,
        is_active=link.is_active,
        last_synced_at=link.last_synced_at,
        webhook_url=f"/api/v1/github/webhook?project_id={project_id}",
        created_at=link.created_at,
    )


@router.delete(
    "/projects/{project_id}/github/link",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink GitHub repository from project",
)
async def unlink_project_github(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _github_service.unlink_repository(project_id, db)
    return None


@router.get(
    "/projects/{project_id}/github/analytics",
    response_model=PRCycleTimeAnalyticsResponse,
    summary="Get Pull Request cycle time, review latency, and velocity metrics",
)
async def get_github_cycle_time_analytics(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculates PR cycle time (hours to merge), turnaround latency, code churn,
    and velocity benchmarks for student engineering teams.
    """
    return await _github_service.get_cycle_time_analytics(project_id, db)


@router.post(
    "/projects/{project_id}/github/simulate-pr",
    response_model=PullRequestMetricResponse,
    summary="Simulate incoming Pull Request merge for testing",
)
async def simulate_github_pr(
    project_id: uuid.UUID,
    sim: SimulatePRCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simulates a GitHub Pull Request event with custom duration and additions/deletions.
    """
    return await _github_service.simulate_pull_request(project_id, sim, db)


@router.post(
    "/github/webhook",
    summary="Incoming GitHub App Webhook Event Ingestion Endpoint",
)
async def handle_github_webhook(
    request: Request,
    project_id: Optional[uuid.UUID] = Query(default=None),
    x_github_event: str = Header(default="pull_request"),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingests GitHub webhook events (push, pull_request, pull_request_review)
    to update team delivery metrics in real time.
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return await _github_service.process_webhook(x_github_event, payload, project_id, db)
