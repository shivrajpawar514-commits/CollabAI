from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from ai.agents.memory_graph import DecisionRecord
from ai.agents.orchestrator import AgentInsight
from ai.agents.code_assistant import CodeReviewItem, GeneratedTestsResult, ProjectReadinessReport
from app.schemas.task import TaskResponse


class MeetingTranscriptRequest(BaseModel):
    meeting_title: Optional[str] = None
    transcript_text: str = Field(..., min_length=10)


class MeetingActionItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    meeting_id: UUID
    project_id: UUID
    title: str
    description: str
    suggested_assignee: Optional[str] = None
    priority: str
    estimated_hours: int
    is_converted: bool
    converted_task_id: Optional[UUID] = None
    created_at: datetime


class MeetingNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    organizer_id: UUID
    title: str
    executive_summary: str
    key_topics_json: Optional[List[str]] = Field(default_factory=list)
    overall_sentiment: str
    action_items: List[MeetingActionItemResponse] = Field(default_factory=list)
    created_at: datetime


class ConvertActionItemsRequest(BaseModel):
    action_item_ids: List[UUID]
    target_milestone_id: Optional[UUID] = None


class ConvertActionItemsResponse(BaseModel):
    converted_count: int
    created_tasks: List[TaskResponse]


class DecisionCreate(BaseModel):
    what: str = Field(..., min_length=3)
    why: str = Field(..., min_length=3)
    who: str = "Team Consensus"
    alternatives: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    linked_task_id: Optional[UUID] = None
    linked_document_id: Optional[UUID] = None


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    recorder_id: UUID
    what: str
    why: str
    who: str
    alternatives_json: Optional[List[str]] = Field(default_factory=list)
    tags_json: Optional[List[str]] = Field(default_factory=list)
    linked_task_id: Optional[UUID] = None
    linked_document_id: Optional[UUID] = None
    created_at: datetime


class DecisionQueryRequest(BaseModel):
    query: str = Field(..., min_length=3)


class DecisionQueryResponse(BaseModel):
    query: str
    answer: str
    confidence_score: float
    matched_decisions: List[DecisionRecord]


class OrchestratorRequest(BaseModel):
    query: str = Field(..., min_length=3)


class OrchestratorResponse(BaseModel):
    query: str
    executive_synthesis: str
    participating_agents: List[str]
    agent_insights: List[AgentInsight]
    recommended_next_actions: List[str]


class CodeReviewRequest(BaseModel):
    code: str = Field(..., min_length=5)
    file_name: Optional[str] = "main.py"
    language: Optional[str] = "python"


class CodeReviewResponse(BaseModel):
    score: int
    summary: str
    review_items: List[CodeReviewItem]
    suggested_refactor: Optional[str] = None


class GenerateTestsRequest(BaseModel):
    code: str = Field(..., min_length=5)
    file_name: Optional[str] = "main.py"
    framework: Optional[str] = "pytest"
