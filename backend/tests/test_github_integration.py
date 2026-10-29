import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

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
from app.services.github_service import GitHubService


async def test_github_integration_suite():
    print("=== Testing GitHub App Integration & PR Cycle Time Suite ===")

    service = GitHubService()
    test_project_id = uuid.uuid4()

    # 1. Test Schema Validation & Serialization
    print("\n1. Testing GitHub schemas...")
    create_dto = GitHubLinkCreate(
        repo_name="shivrajpawar514-commits/CollabAI",
        repo_url="https://github.com/shivrajpawar514-commits/CollabAI",
        default_branch="main",
        webhook_secret="shhh-secret-123",
    )
    assert create_dto.repo_name == "shivrajpawar514-commits/CollabAI"
    assert create_dto.default_branch == "main"
    print("  ✓ GitHubLinkCreate validated successfully")

    sim_dto = SimulatePRCreate(
        title="feat(ai): autonomous architecture blueprint generator",
        author_username="test-lead",
        hours_to_merge=4.5,
        additions=450,
        deletions=32,
        changed_files=6,
        auto_merge=True,
    )
    assert sim_dto.hours_to_merge == 4.5
    assert sim_dto.auto_merge is True
    print("  ✓ SimulatePRCreate validated successfully")

    # 2. Test Repository Linking via Mock DB Session
    print("\n2. Testing repository linking logic...")
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.add_all = MagicMock()
    mock_project = Project(
        id=test_project_id,
        title="CollabAI Workspace",
        description="Collaborative workspace platform",
        owner_id=uuid.uuid4(),
    )
    mock_db.get.return_value = mock_project
    
    # Mock get_repository_link query result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    link_res = await service.link_repository(test_project_id, create_dto, mock_db)
    assert link_res.project_id == test_project_id
    assert link_res.repo_name == "shivrajpawar514-commits/CollabAI"
    assert link_res.is_active is True
    assert f"project_id={test_project_id}" in link_res.webhook_url
    print(f"  ✓ Linked repository '{link_res.repo_name}' with webhook '{link_res.webhook_url}'")

    # 3. Test Cycle Time Analytics Computation & Velocity Verdicts
    print("\n3. Testing PR cycle time calculation & velocity categorization...")
    now = datetime.now(timezone.utc)
    mock_prs = [
        PullRequestMetric(
            id=uuid.uuid4(),
            project_id=test_project_id,
            pr_number=101,
            title="feat(infra): prometheus and grafana monitoring setup",
            author_username="devops-eng",
            state="merged",
            html_url="https://github.com/project/pull/101",
            created_at_gh=now - timedelta(hours=5),
            merged_at_gh=now - timedelta(hours=1),
            cycle_time_hours=4.0,
            additions=300,
            deletions=40,
            changed_files=4,
        ),
        PullRequestMetric(
            id=uuid.uuid4(),
            project_id=test_project_id,
            pr_number=102,
            title="feat(frontend): high-density hackathon judge scorecard",
            author_username="frontend-lead",
            state="merged",
            html_url="https://github.com/project/pull/102",
            created_at_gh=now - timedelta(hours=10),
            merged_at_gh=now - timedelta(hours=8),
            cycle_time_hours=2.0,
            additions=180,
            deletions=25,
            changed_files=3,
        ),
        PullRequestMetric(
            id=uuid.uuid4(),
            project_id=test_project_id,
            pr_number=103,
            title="feat(backend): PR cycle time telemetry router",
            author_username="backend-eng",
            state="open",
            html_url="https://github.com/project/pull/103",
            created_at_gh=now - timedelta(hours=1),
            merged_at_gh=None,
            cycle_time_hours=None,
            additions=120,
            deletions=10,
            changed_files=2,
        ),
    ]

    mock_scalars = MagicMock()
    mock_scalars.scalars.return_value.all.return_value = mock_prs
    mock_scalars.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_scalars

    analytics = await service.get_cycle_time_analytics(test_project_id, mock_db)
    assert analytics.total_prs == 3
    assert analytics.merged_prs == 2
    assert analytics.open_prs == 1
    # Average of 4.0 and 2.0 = 3.0 hours
    assert analytics.avg_cycle_time_hours == 3.0
    assert analytics.fastest_merge_hours == 2.0
    assert "Elite Delivery Velocity" in analytics.velocity_verdict
    assert len(analytics.recent_prs) == 3
    print(f"  ✓ Avg Cycle Time: {analytics.avg_cycle_time_hours} hrs")
    print(f"  ✓ Fastest Merge: {analytics.fastest_merge_hours} hrs")
    print(f"  ✓ Velocity Verdict: {analytics.velocity_verdict}")
    print(f"  ✓ Merge Success Rate: {analytics.merge_success_rate_pct}%")

    # 4. Test Webhook Processing for pull_request events
    print("\n4. Testing webhook payload processing...")
    webhook_payload = {
        "action": "closed",
        "pull_request": {
            "number": 105,
            "title": "feat(core): auto-assignee recommendation pipeline",
            "user": {"login": "ai-lead"},
            "merged": True,
            "html_url": "https://github.com/org/repo/pull/105",
            "created_at": (now - timedelta(hours=3, minutes=30)).isoformat(),
            "merged_at": now.isoformat(),
            "additions": 210,
            "deletions": 18,
            "changed_files": 3,
        },
    }

    wh_res = await service.process_webhook("pull_request", webhook_payload, test_project_id, mock_db)
    assert wh_res["status"] == "processed"
    assert wh_res["pr_number"] == 105
    assert wh_res["state"] == "merged"
    print(f"  ✓ Webhook PR #{wh_res['pr_number']} processed with state '{wh_res['state']}'")

    # Non-PR event should be cleanly ignored
    ignore_res = await service.process_webhook("ping", {"zen": "Keep it logically awesome."}, test_project_id, mock_db)
    assert ignore_res["status"] == "ignored"
    print("  ✓ Non-PR events handled safely without side effects")

    print("\n🎉 ALL GITHUB & PR CYCLE TIME TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(test_github_integration_suite())
