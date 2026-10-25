import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.advanced_ai_service import AdvancedAIService
from ai.agents.code_assistant import GeneratedTestsResult, ProjectReadinessReport
from app.schemas.advanced_ai import (
    MeetingTranscriptRequest,
    MeetingNoteResponse,
    ConvertActionItemsRequest,
    ConvertActionItemsResponse,
    DecisionCreate,
    DecisionResponse,
    DecisionQueryRequest,
    DecisionQueryResponse,
    OrchestratorRequest,
    OrchestratorResponse,
    CodeReviewRequest,
    CodeReviewResponse,
    GenerateTestsRequest,
)

router = APIRouter(prefix="", tags=["Advanced AI & Project Memory"])
advanced_ai_service = AdvancedAIService()


# 1. Voice & Meeting Assistant
@router.post(
    "/projects/{project_id}/meetings/analyze",
    response_model=MeetingNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def analyze_meeting(
    project_id: uuid.UUID,
    req: MeetingTranscriptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest meeting / voice standup transcript, extract executive summary, key topics, decisions,
    and structured action items with priority and estimated hours, and persist to project records.
    """
    return await advanced_ai_service.analyze_and_save_meeting(
        project_id=project_id,
        user_id=current_user.id,
        transcript_text=req.transcript_text,
        meeting_title=req.meeting_title,
        db=db,
    )


@router.get(
    "/projects/{project_id}/meetings",
    response_model=List[MeetingNoteResponse],
)
async def get_project_meetings(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List historical meetings and standup analyses for the project."""
    return await advanced_ai_service.get_project_meetings(
        project_id=project_id,
        db=db,
    )


@router.post(
    "/projects/{project_id}/meetings/convert-tasks",
    response_model=ConvertActionItemsResponse,
)
async def convert_meeting_action_items(
    project_id: uuid.UUID,
    req: ConvertActionItemsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Convert extracted meeting action items into real Kanban tasks."""
    return await advanced_ai_service.convert_meeting_action_items(
        project_id=project_id,
        user_id=current_user.id,
        action_item_ids=req.action_item_ids,
        target_milestone_id=req.target_milestone_id,
        db=db,
    )


# 2. Project Memory & Decision Knowledge Graph
@router.post(
    "/projects/{project_id}/decisions",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_decision(
    project_id: uuid.UUID,
    d_in: DecisionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a formal architectural or product decision (ADR) into the project memory graph."""
    return await advanced_ai_service.save_decision(
        project_id=project_id,
        user_id=current_user.id,
        d_in=d_in,
        db=db,
    )


@router.get(
    "/projects/{project_id}/decisions",
    response_model=List[DecisionResponse],
)
async def get_project_decisions(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all architectural decision records (ADRs) recorded for the project."""
    return await advanced_ai_service.get_project_decisions(
        project_id=project_id,
        db=db,
    )


@router.post(
    "/projects/{project_id}/decisions/query",
    response_model=DecisionQueryResponse,
)
async def query_decision_memory(
    project_id: uuid.UUID,
    req: DecisionQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Query the Project Memory Knowledge Graph ('Why did we choose X?') using semantic retrieval
    over historical architectural decisions and trade-offs.
    """
    return await advanced_ai_service.query_decision_memory(
        project_id=project_id,
        query=req.query,
        db=db,
    )


# 3. Multi-Agent Orchestrator
@router.post(
    "/projects/{project_id}/orchestrator/run",
    response_model=OrchestratorResponse,
)
async def run_orchestrator(
    project_id: uuid.UUID,
    req: OrchestratorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a multi-agent orchestration workflow coordinating Planner Agent,
    Research Agent, and Task Agent with executive supervisor synthesis.
    """
    return await advanced_ai_service.run_multi_agent_orchestrator(
        project_id=project_id,
        query=req.query,
        db=db,
    )


# 4. Code Assistant & Project Readiness
@router.post(
    "/projects/{project_id}/code/review",
    response_model=CodeReviewResponse,
)
async def review_code(
    project_id: uuid.UUID,
    req: CodeReviewRequest,
    current_user: User = Depends(get_current_user),
):
    """Review source code for vulnerabilities, anti-patterns, performance bottlenecks, and refactoring."""
    return await advanced_ai_service.review_code(
        code=req.code,
        file_name=req.file_name,
        language=req.language,
    )


@router.post(
    "/projects/{project_id}/code/tests",
    response_model=GeneratedTestsResult,
)
async def generate_unit_tests(
    project_id: uuid.UUID,
    req: GenerateTestsRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate production-ready unit tests (pytest / vitest) for given source code."""
    return await advanced_ai_service.generate_unit_tests(
        code=req.code,
        file_name=req.file_name,
        framework=req.framework,
    )


@router.get(
    "/projects/{project_id}/readiness-audit",
    response_model=ProjectReadinessReport,
)
async def audit_project_readiness(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an authoritative Project Readiness Score (0-100) and letter grade evaluated across
    4 pillars: Architecture & Security, Code Quality, Test Coverage, and Documentation.
    """
    return await advanced_ai_service.audit_project_readiness(
        project_id=project_id,
        db=db,
    )
