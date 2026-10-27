from typing import List, Optional
from pydantic import BaseModel, Field


class PitchDeckSlideResponse(BaseModel):
    slide_number: int
    title: str
    subtitle: Optional[str] = None
    key_points: List[str]
    visual_suggestion: str
    presenter_notes: str


class HackathonPitchDeckResponse(BaseModel):
    project_title: str
    tagline: str
    target_hackathon_track: str
    slides: List[PitchDeckSlideResponse]
    executive_pitch_30s: str
    key_metrics_summary: List[str]


class ProjectPortfolioExportResponse(BaseModel):
    project_title: str
    one_liner: str
    problem_statement: str
    solution_overview: str
    tech_stack_highlights: List[str]
    architecture_decisions: List[str]
    milestone_timeline: List[str]
    devpost_markdown: str
