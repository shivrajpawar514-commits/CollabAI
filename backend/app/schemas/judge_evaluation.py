from typing import List, Optional
from pydantic import BaseModel, Field
from ai.agents.judge_evaluator import CriteriaScore, JudgePersonaCritique, HackathonJudgeEvaluation


class CriteriaScoreResponse(BaseModel):
    name: str
    score: int
    weight: float = 1.0
    strengths: List[str]
    areas_for_improvement: List[str]
    judge_tips: str


class JudgePersonaCritiqueResponse(BaseModel):
    judge_role: str
    verdict_score: int
    overall_impression: str
    key_positive: str
    hard_question_to_prepare: str


class HackathonJudgeEvaluationResponse(BaseModel):
    project_title: str
    overall_score: int
    percentile_rank_estimate: str
    verdict_badge: str
    criteria_breakdown: List[CriteriaScoreResponse]
    judge_personas: List[JudgePersonaCritiqueResponse]
    top_action_items_before_pitch: List[str]
    raw_executive_critique: str
