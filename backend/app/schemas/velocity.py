import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class BurndownPoint(BaseModel):
    day_label: str = Field(description="Sprint day or date (e.g. 'Day 1', 'Day 2')")
    ideal_remaining: int = Field(description="Linear ideal task burndown curve")
    actual_remaining: int = Field(description="Actual open tasks remaining")


class MilestoneProgressItem(BaseModel):
    milestone_id: str
    title: str
    progress_percentage: int = Field(ge=0, le=100)
    total_tasks: int
    completed_tasks: int
    status: str


class SprintVelocityMetricsResponse(BaseModel):
    project_id: uuid.UUID
    velocity_score: int = Field(ge=0, le=100, description="0-100 normalized velocity score")
    velocity_grade: str = Field(description="Performance letter grade: 'A+', 'A', 'B', 'C', 'Needs Focus'")
    sprint_completion_rate: float = Field(ge=0.0, le=1.0, description="Percentage of tasks completed")
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    backlog_tasks: int
    estimated_hours_remaining: int
    cycle_time_avg_hours: float
    burndown_chart: List[BurndownPoint]
    milestones_progress: List[MilestoneProgressItem]
    recommendations: List[str]
