from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ai.prompts.project_generator import ProjectProposal, RoleNeed, MilestonePlan
from ai.prompts.milestone_planner import MilestoneDecomposition, MilestoneItem, MilestoneTaskItem
from ai.prompts.task_decomposer import TaskBreakdown, SubTaskItem
from ai.prompts.copilot import CopilotResponse, ActionSuggestion
from ai.matching import CandidateMatch


class ProjectGenerateRequest(BaseModel):
    idea: str = Field(min_length=5, description="Natural language project concept or problem description")
    constraints: Optional[str] = Field(default="", description="Optional preferences, tech stack or domain constraints")


class PlanMilestonesRequest(BaseModel):
    timeline_weeks: int = Field(default=8, ge=2, le=24, description="Target project duration in weeks")


class ApplyMilestonesRequest(BaseModel):
    milestones: List[MilestoneItem] = Field(description="List of AI-generated milestones to apply to the project")


class DecomposeTaskRequest(BaseModel):
    additional_context: Optional[str] = Field(default="", description="Specific guidelines or focus areas for the decomposition")


class ApplyDecompositionRequest(BaseModel):
    milestone_id: Optional[str] = None
    subtasks: List[SubTaskItem] = Field(description="Subtasks to create as actual Kanban tasks on the project board")


class CopilotChatRequest(BaseModel):
    project_id: str
    message: str = Field(min_length=1, description="Student's query or prompt for the Project Copilot")
    chat_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)


class TeammateRecommendationResponse(BaseModel):
    project_id: str
    project_title: str
    recommendations: List[CandidateMatch]
    total_analyzed: int
