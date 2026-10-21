from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ActionSuggestion(BaseModel):
    action_type: str = Field(description="create_task, create_milestone, invite_teammate, advice, tech_tip")
    label: str
    detail: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class CopilotResponse(BaseModel):
    answer: str
    suggested_actions: List[ActionSuggestion] = Field(default_factory=list)
    relevant_skills: List[str] = Field(default_factory=list)


SYSTEM_COPILOT_PROMPT = """You are CollabAI Project Copilot, an intelligent AI engineering mentor embedded directly inside a student project workspace.
You have real-time visibility into the project's title, description, team roster, Kanban tasks, and roadmap milestones.
Your responsibilities:
1. Provide actionable, concise engineering guidance (architecture patterns, library suggestions, bug debugging tips, best practices).
2. Recommend immediate next steps or task delegation to unblock the team.
3. Keep answers encouraging, student-friendly, and structured with Markdown headers and bullet points.
4. When relevant, suggest concrete executable actions (like creating a recommended task or reaching out to a teammate).
"""


def format_copilot_context_prompt(
    project_title: str,
    project_description: str,
    team_members: List[Dict[str, Any]],
    current_tasks: List[Dict[str, Any]],
    milestones: List[Dict[str, Any]],
    user_query: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> str:
    members_str = ", ".join([f"{m.get('name', 'Member')} ({m.get('role', 'member')})" for m in team_members]) or "None yet"
    tasks_str = ", ".join([f"[{t.get('status', 'todo')}] {t.get('title', 'Task')}" for t in current_tasks[:10]]) or "No tasks yet"
    milestones_str = ", ".join([m.get('title', 'Milestone') for m in milestones[:5]]) or "No milestones defined"

    prompt = f"""=== PROJECT WORKSPACE CONTEXT ===
Project: {project_title}
Overview: {project_description}
Team Members: {members_str}
Recent Kanban Tasks: {tasks_str}
Roadmap Milestones: {milestones_str}
================================

"""
    if chat_history:
        prompt += "=== CONVERSATION HISTORY ===\n"
        for msg in chat_history[-6:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"{role.upper()}: {content}\n"
        prompt += "===========================\n\n"

    prompt += f"USER QUERY:\n{user_query}\n\nProvide an insightful, helpful, and technically grounded response."
    return prompt
