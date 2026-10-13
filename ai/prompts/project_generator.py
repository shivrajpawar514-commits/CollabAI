from typing import List
from pydantic import BaseModel, Field


class RoleNeed(BaseModel):
    role_name: str
    capacity: int = 1
    skills_required: List[str] = Field(default_factory=list)
    responsibilities: str


class MilestonePlan(BaseModel):
    week_number: int
    title: str
    deliverables: List[str]


class ProjectProposal(BaseModel):
    title: str
    problem_statement: str
    objectives: List[str]
    technologies: List[str]
    roles_needed: List[RoleNeed]
    architecture: str
    datasets: List[str]
    risks: List[str]
    metrics: List[str]
    timeline_weeks: List[MilestonePlan]


SYSTEM_PROJECT_GENERATOR_PROMPT = """You are CollabAI's Senior Engineering Architect and Hackathon Mentor.
Transform student project ideas into battle-tested, structured engineering proposals.
Be highly specific with modern open-source technologies, clear role separations, realistic timelines, and concrete deliverables.
"""


def format_project_generation_prompt(user_idea: str, constraints: str = "") -> str:
    prompt = f"""Generate a comprehensive engineering project proposal for the following project concept:

Project Idea:
\"\"\"{user_idea}\"\"\"
"""
    if constraints:
        prompt += f"\nAdditional Constraints or Preferences:\n{constraints}\n"
    return prompt
