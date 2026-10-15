import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.ai_service import AIService
from app.schemas.ai import (
    ProjectGenerateRequest,
    PlanMilestonesRequest,
    ApplyMilestonesRequest,
    DecomposeTaskRequest,
    ApplyDecompositionRequest,
    CopilotChatRequest,
    TeammateRecommendationResponse,
)
from app.schemas.task import MilestoneResponse, TaskResponse
from ai.prompts.project_generator import ProjectProposal
from ai.prompts.milestone_planner import MilestoneDecomposition
from ai.prompts.task_decomposer import TaskBreakdown
from ai.prompts.copilot import CopilotResponse

router = APIRouter(prefix="/ai", tags=["AI & Machine Learning"])
ai_service = AIService()


@router.post("/generate-project", response_model=ProjectProposal, status_code=status.HTTP_200_OK)
async def generate_project_proposal(
    request: ProjectGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a full structured project proposal from a natural-language idea.
    Includes title, problem statement, objectives, technologies, required roles, architecture, datasets, risks, metrics, and timeline.
    """
    return await ai_service.generate_project_proposal(
        idea=request.idea,
        constraints=request.constraints or ""
    )


@router.post("/projects/{project_id}/plan-milestones", response_model=MilestoneDecomposition, status_code=status.HTTP_200_OK)
async def plan_project_milestones(
    project_id: uuid.UUID,
    request: PlanMilestonesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a project and automatically generate structured, sequential engineering milestones with deliverables and tasks.
    """
    return await ai_service.plan_milestones(
        project_id=project_id,
        timeline_weeks=request.timeline_weeks,
        db=db
    )


@router.post("/projects/{project_id}/apply-milestones", response_model=List[MilestoneResponse], status_code=status.HTTP_201_CREATED)
async def apply_project_milestones(
    project_id: uuid.UUID,
    request: ApplyMilestonesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Commit AI-generated milestones and suggested tasks to the project roadmap and Kanban backlog.
    """
    return await ai_service.apply_milestones(
        project_id=project_id,
        milestones=request.milestones,
        current_user_id=current_user.id,
        db=db
    )


@router.post("/tasks/{task_id}/decompose", response_model=TaskBreakdown, status_code=status.HTTP_200_OK)
async def decompose_task(
    task_id: uuid.UUID,
    request: DecomposeTaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Break down an ambiguous or large task into 3-5 concrete, bite-sized student subtasks with effort estimation and duplicate warnings.
    """
    return await ai_service.decompose_task(
        task_id=task_id,
        additional_context=request.additional_context or "",
        db=db
    )


@router.post("/tasks/{task_id}/apply-decomposition", response_model=List[TaskResponse], status_code=status.HTTP_201_CREATED)
async def apply_task_decomposition(
    task_id: uuid.UUID,
    request: ApplyDecompositionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create the decomposed subtasks as actual active tasks on the Kanban board.
    """
    return await ai_service.apply_decomposition(
        task_id=task_id,
        milestone_id=uuid.UUID(request.milestone_id) if request.milestone_id else None,
        subtasks=request.subtasks,
        current_user_id=current_user.id,
        db=db
    )


@router.get("/projects/{project_id}/recommend-teammates", response_model=TeammateRecommendationResponse)
async def recommend_teammates(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    AI Teammate Recommender: Matches available students based on skill complementarity, domain interest, availability, and roles.
    """
    matches = await ai_service.recommend_teammates(project_id=project_id, db=db)
    return TeammateRecommendationResponse(
        project_id=str(project_id),
        project_title="Project Teammates",
        recommendations=matches,
        total_analyzed=len(matches)
    )


@router.post("/copilot/chat", response_model=CopilotResponse)
async def copilot_chat(
    request: CopilotChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Context-aware Project Copilot: Answers questions about architecture, tasks, roadmap, or engineering bottlenecks.
    """
    return await ai_service.copilot_chat(
        project_id=uuid.UUID(request.project_id),
        user_query=request.message,
        chat_history=request.chat_history or [],
        db=db
    )


@router.post("/copilot/stream")
async def copilot_stream(
    request: CopilotChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Real-time streaming Server-Sent Events (SSE) response for Project Copilot.
    """
    return StreamingResponse(
        ai_service.copilot_stream(
            project_id=uuid.UUID(request.project_id),
            user_query=request.message,
            chat_history=request.chat_history or [],
            db=db
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
