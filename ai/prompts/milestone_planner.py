from typing import List
from pydantic import BaseModel, Field


class MilestoneTaskItem(BaseModel):
    title: str
    description: str
    priority: str = Field(default="medium", description="low, medium, high, urgent")
    estimated_hours: int = 10
    recommended_skills: List[str] = Field(default_factory=list)


class MilestoneItem(BaseModel):
    title: str
    description: str
    target_week: int
    deliverables: List[str] = Field(default_factory=list)
    suggested_tasks: List[MilestoneTaskItem] = Field(default_factory=list)


class MilestoneDecomposition(BaseModel):
    project_title: str
    overview: str
    total_weeks: int
    milestones: List[MilestoneItem] = Field(default_factory=list)


SYSTEM_MILESTONE_PLANNER_PROMPT = """You are CollabAI's Technical Project Manager and Milestone Planner.
Break down university and hackathon student projects into clean, logical, sequential engineering phases:
1. Research & Architecture Setup
2. Core Backend & Database Infrastructure
3. AI/ML Modeling or Core Logic
4. Frontend Client & UI Interactions
5. Integration, Security & Testing
6. Deployment, Demo & Documentation
Ensure each milestone has explicit deliverables and actionable tasks with reasonable hour estimates for student teams.
"""


def format_milestone_planning_prompt(
    project_title: str,
    description: str,
    tech_stack: List[str],
    timeline_weeks: int = 8
) -> str:
    techs = ", ".join(tech_stack) if tech_stack else "Standard modern web stack"
    return f"""Please create a comprehensive {timeline_weeks}-week development roadmap and milestone decomposition for the following project:

Project Title: {project_title}
Project Overview:
\"\"\"{description}\"\"\"

Technologies: {techs}
Planned Duration: {timeline_weeks} weeks

Generate {min(6, max(3, timeline_weeks // 2))} structured milestones with associated actionable student tasks and deliverables.
"""
