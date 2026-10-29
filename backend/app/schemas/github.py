import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class GitHubLinkCreate(BaseModel):
    repo_name: str = Field(description="Repository in 'owner/repo' format (e.g. 'shivrajpawar514/CollabAI')")
    repo_url: str = Field(description="Full HTTPS URL to GitHub repository")
    default_branch: str = Field(default="main", description="Primary release branch")
    webhook_secret: Optional[str] = Field(default=None, description="Optional HMAC-SHA256 secret for webhook validation")


class GitHubLinkResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    repo_name: str
    repo_url: str
    default_branch: str
    is_active: bool
    last_synced_at: Optional[datetime]
    webhook_url: str
    created_at: datetime


class PullRequestMetricResponse(BaseModel):
    id: uuid.UUID
    pr_number: int
    title: str
    author_username: str
    state: str
    html_url: str
    cycle_time_hours: Optional[float]
    additions: int
    deletions: int
    changed_files: int
    linked_task_id: Optional[uuid.UUID]
    created_at_gh: datetime
    merged_at_gh: Optional[datetime]


class PRCycleTimeAnalyticsResponse(BaseModel):
    project_id: uuid.UUID
    repo_name: str
    total_prs: int
    open_prs: int
    merged_prs: int
    avg_cycle_time_hours: float
    median_cycle_time_hours: float
    fastest_merge_hours: float
    merge_success_rate_pct: float
    avg_code_churn: int
    recent_prs: List[PullRequestMetricResponse]
    velocity_verdict: str


class SimulatePRCreate(BaseModel):
    title: str = Field(description="Pull Request title (e.g. 'feat(ai): add RAG chunking pipeline')")
    author_username: str = Field(default="student-dev", description="GitHub contributor username")
    hours_to_merge: float = Field(default=3.5, description="Simulated review and merge duration in hours")
    additions: int = Field(default=240)
    deletions: int = Field(default=35)
    changed_files: int = Field(default=4)
    auto_merge: bool = Field(default=True, description="Whether to simulate successful merge or leave open")
