from typing import List, Optional
from pydantic import BaseModel, Field


class SubTaskItem(BaseModel):
    title: str
    description: str
    priority: str = Field(default="medium", description="low, medium, high, urgent")
    estimated_hours: int = 6
    required_skills: List[str] = Field(default_factory=list)
    suggested_role: str = "Developer"
    dependencies: List[str] = Field(default_factory=list)


class TaskBreakdown(BaseModel):
    original_task_title: str
    analysis: str
    estimated_total_hours: int
    subtasks: List[SubTaskItem] = Field(default_factory=list)
    potential_risks: List[str] = Field(default_factory=list)
    duplicate_or_conflict_warnings: List[str] = Field(default_factory=list)


SYSTEM_TASK_DECOMPOSER_PROMPT = """You are CollabAI's Senior Software Architect and Agile Task Decomposition specialist.
Students frequently get stuck on massive, ambiguous tasks (e.g. 'Build Auth' or 'Setup ML Model').
Your goal is to decompose high-level tasks into 3 to 5 bite-sized, independently testable subtasks that can be assigned directly to students.
Flag any engineering risks, bottleneck dependencies, or potential duplicate work with existing project components.
"""


def format_task_decomposition_prompt(
    task_title: str,
    task_description: str,
    project_context: str = "",
    existing_tasks: Optional[List[str]] = None
) -> str:
    prompt = f"""Decompose this task into concrete, bite-sized engineering subtasks:

Task to decompose:
Title: {task_title}
Description: {task_description or 'No extra description provided.'}
"""
    if project_context:
        prompt += f"\nProject Context:\n{project_context}\n"
    if existing_tasks:
        tasks_formatted = "\n- ".join(existing_tasks[:15])
        prompt += f"\nExisting Tasks on Board (check for duplicates):\n- {tasks_formatted}\n"

    prompt += "\nBreak this task down into 3-5 concrete subtasks with clear acceptance criteria and realistic hours."
    return prompt
