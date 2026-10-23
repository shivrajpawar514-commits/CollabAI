from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from ai.ml.matching_v2 import CandidateMatchV2
from ai.ml.deadline_risk import DeadlineRiskReport
from ai.ml.skill_graph import SkillGapAnalysis, LearningStep, FreeResource


class RecommendationFeedbackCreate(BaseModel):
    candidate_id: UUID
    action: str = Field(..., description="Action taken: 'accepted', 'invited', 'dismissed', or 'viewed'")
    match_score: int = Field(0, ge=0, le=100)
    ml_rank_score: int = Field(0, ge=0, le=100)
    feature_vector_json: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RecommendationFeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    reviewer_id: UUID
    candidate_id: UUID
    action: str
    match_score: int
    ml_rank_score: int
    created_at: datetime


class TeammateMatchV2Response(BaseModel):
    project_id: UUID
    project_title: str
    recommendations: List[CandidateMatchV2]
    total_analyzed: int
