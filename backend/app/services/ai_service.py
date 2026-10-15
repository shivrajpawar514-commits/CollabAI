import os
import sys
import uuid
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

# Ensure root path is accessible for ai module
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ai.client import LLMClient
from ai.matching import MatchingEngine, CandidateMatch
from ai.prompts.project_generator import (
    ProjectProposal,
    SYSTEM_PROJECT_GENERATOR_PROMPT,
    format_project_generation_prompt,
)
from ai.prompts.milestone_planner import (
    MilestoneDecomposition,
    MilestoneItem,
    SYSTEM_MILESTONE_PLANNER_PROMPT,
    format_milestone_planning_prompt,
)
from ai.prompts.task_decomposer import (
    TaskBreakdown,
    SubTaskItem,
    SYSTEM_TASK_DECOMPOSER_PROMPT,
    format_task_decomposition_prompt,
)
from ai.prompts.copilot import (
    CopilotResponse,
    SYSTEM_COPILOT_PROMPT,
    format_copilot_context_prompt,
)

from app.models.project import Project, ProjectSkill, ProjectRole
from app.models.task import Milestone, Task
from app.models.team import Team, TeamMember
from app.models.user import User
from app.models.profile import Profile
from app.models.skill import UserSkill, Skill
from app.models.notification import ActivityLog


class AIService:
    def __init__(self):
        self.llm = LLMClient()

    async def generate_project_proposal(self, idea: str, constraints: str = "") -> ProjectProposal:
        prompt = format_project_generation_prompt(idea, constraints)
        return await self.llm.generate_structured(
            prompt=prompt,
            schema=ProjectProposal,
            system_instruction=SYSTEM_PROJECT_GENERATOR_PROMPT,
            temperature=0.3
        )

    async def plan_milestones(
        self,
        project_id: uuid.UUID,
        timeline_weeks: int,
        db: AsyncSession
    ) -> MilestoneDecomposition:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        # Get tech stack from skills
        tech_skills: List[str] = []
        if project.required_skills:
            for ps in project.required_skills:
                if ps.skill:
                    tech_skills.append(ps.skill.name)

        prompt = format_milestone_planning_prompt(
            project_title=project.title,
            description=project.description,
            tech_stack=tech_skills,
            timeline_weeks=timeline_weeks
        )

        return await self.llm.generate_structured(
            prompt=prompt,
            schema=MilestoneDecomposition,
            system_instruction=SYSTEM_MILESTONE_PLANNER_PROMPT,
            temperature=0.2
        )

    async def apply_milestones(
        self,
        project_id: uuid.UUID,
        milestones: List[MilestoneItem],
        current_user_id: uuid.UUID,
        db: AsyncSession
    ) -> List[Milestone]:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        created_milestones: List[Milestone] = []
        for item in milestones:
            m = Milestone(
                project_id=project_id,
                title=item.title,
                description=f"{item.description}\n\nDeliverables:\n- " + "\n- ".join(item.deliverables),
                order_index=item.target_week,
                status="planned"
            )
            db.add(m)
            await db.flush()
            created_milestones.append(m)

            # Optionally create suggested tasks for the milestone
            if item.suggested_tasks:
                for t in item.suggested_tasks:
                    task = Task(
                        project_id=project_id,
                        milestone_id=m.id,
                        title=t.title,
                        description=t.description,
                        status="backlog",
                        priority=t.priority if t.priority in ["low", "medium", "high", "urgent"] else "medium",
                        estimated_hours=t.estimated_hours,
                        created_by_id=current_user_id
                    )
                    db.add(task)

        # Log activity
        log = ActivityLog(
            project_id=project_id,
            user_id=current_user_id,
            action_type="ai_plan_milestones",
            entity_type="milestone",
            description=f"Generated and applied {len(milestones)} milestones with AI Project Planner"
        )
        db.add(log)
        await db.commit()
        return created_milestones

    async def decompose_task(
        self,
        task_id: uuid.UUID,
        additional_context: str,
        db: AsyncSession
    ) -> TaskBreakdown:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalars().first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        # Fetch sibling tasks for duplicate checking
        siblings_result = await db.execute(
            select(Task.title).where(Task.project_id == task.project_id, Task.id != task_id)
        )
        sibling_titles = [row[0] for row in siblings_result.all()]

        # Project overview
        project_desc = ""
        if task.project:
            project_desc = f"{task.project.title}: {task.project.description}"

        prompt = format_task_decomposition_prompt(
            task_title=task.title,
            task_description=task.description or "",
            project_context=f"{project_desc}\n{additional_context}".strip(),
            existing_tasks=sibling_titles
        )

        return await self.llm.generate_structured(
            prompt=prompt,
            schema=TaskBreakdown,
            system_instruction=SYSTEM_TASK_DECOMPOSER_PROMPT,
            temperature=0.2
        )

    async def apply_decomposition(
        self,
        task_id: uuid.UUID,
        milestone_id: Optional[uuid.UUID],
        subtasks: List[SubTaskItem],
        current_user_id: uuid.UUID,
        db: AsyncSession
    ) -> List[Task]:
        result = await db.execute(select(Task).where(Task.id == task_id))
        parent_task = result.scalars().first()
        if not parent_task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent task not found")

        target_milestone = milestone_id or parent_task.milestone_id
        created_tasks: List[Task] = []

        for st in subtasks:
            new_task = Task(
                project_id=parent_task.project_id,
                milestone_id=target_milestone,
                title=st.title,
                description=f"{st.description}\n\n[Suggested Role: {st.suggested_role}]\n[Required Skills: {', '.join(st.required_skills)}]",
                status="todo",
                priority=st.priority if st.priority in ["low", "medium", "high", "urgent"] else "medium",
                estimated_hours=st.estimated_hours,
                created_by_id=current_user_id
            )
            db.add(new_task)
            await db.flush()
            created_tasks.append(new_task)

        # Log activity
        log = ActivityLog(
            project_id=parent_task.project_id,
            user_id=current_user_id,
            action_type="ai_decompose_task",
            entity_type="task",
            entity_id=task_id,
            description=f"Decomposed task '{parent_task.title}' into {len(subtasks)} subtasks using AI"
        )
        db.add(log)
        await db.commit()
        return created_tasks

    async def recommend_teammates(
        self,
        project_id: uuid.UUID,
        db: AsyncSession
    ) -> List[CandidateMatch]:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        # Collect required skills
        req_skills: List[str] = []
        if project.required_skills:
            for ps in project.required_skills:
                if ps.skill:
                    req_skills.append(ps.skill.name)

        # Collect project roles
        roles: List[str] = [r.title for r in project.roles] if project.roles else []

        # Find existing team member IDs
        existing_user_ids = {project.owner_id}
        if project.team:
            for tm in project.team.members:
                existing_user_ids.add(tm.user_id)

        # Fetch candidate users
        users_result = await db.execute(
            select(User).where(User.id.notin_(existing_user_ids), User.is_active == True).limit(50)
        )
        candidates = users_result.scalars().all()

        candidate_dicts: List[Dict[str, Any]] = []
        for u in candidates:
            c_skills = [us.skill.name for us in u.skills if us.skill] if u.skills else []
            profile = u.profile
            candidate_dicts.append({
                "id": str(u.id),
                "name": u.full_name,
                "email": u.email,
                "avatar_url": u.avatar_url,
                "college": profile.college if profile else None,
                "branch": profile.branch if profile else None,
                "year": profile.year if profile else None,
                "bio": profile.bio if profile else None,
                "skills": c_skills,
                "interests": profile.interests if profile and profile.interests else [],
                "preferred_roles": profile.preferred_roles if profile and profile.preferred_roles else [],
                "availability_hours_per_week": profile.availability_hours_per_week if profile else 10,
                "github_username": profile.github_username if profile else None
            })

        project_dict = {
            "title": project.title,
            "description": project.description,
            "required_skills": req_skills,
            "roles": roles
        }

        return MatchingEngine.rank_candidates(project_dict, candidate_dicts, top_k=10)

    async def copilot_chat(
        self,
        project_id: uuid.UUID,
        user_query: str,
        chat_history: List[Dict[str, str]],
        db: AsyncSession
    ) -> CopilotResponse:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        members = []
        if project.team and project.team.members:
            for tm in project.team.members:
                name = tm.user.full_name if tm.user else "Member"
                members.append({"name": name, "role": tm.role})
        else:
            members.append({"name": project.owner.full_name if project.owner else "Owner", "role": "leader"})

        tasks = [{"title": t.title, "status": t.status} for t in (project.tasks or [])[:10]]
        milestones = [{"title": m.title} for m in (project.milestones or [])[:5]]

        prompt = format_copilot_context_prompt(
            project_title=project.title,
            project_description=project.description,
            team_members=members,
            current_tasks=tasks,
            milestones=milestones,
            user_query=user_query,
            chat_history=chat_history
        )

        return await self.llm.generate_structured(
            prompt=prompt,
            schema=CopilotResponse,
            system_instruction=SYSTEM_COPILOT_PROMPT,
            temperature=0.4
        )

    async def copilot_stream(
        self,
        project_id: uuid.UUID,
        user_query: str,
        chat_history: List[Dict[str, str]],
        db: AsyncSession
    ) -> AsyncGenerator[str, None]:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()
        if not project:
            yield "data: " + json.dumps({"error": "Project not found"}) + "\n\n"
            return

        members = []
        if project.team and project.team.members:
            for tm in project.team.members:
                name = tm.user.full_name if tm.user else "Member"
                members.append({"name": name, "role": tm.role})
        else:
            members.append({"name": project.owner.full_name if project.owner else "Owner", "role": "leader"})

        tasks = [{"title": t.title, "status": t.status} for t in (project.tasks or [])[:10]]
        milestones = [{"title": m.title} for m in (project.milestones or [])[:5]]

        prompt = format_copilot_context_prompt(
            project_title=project.title,
            project_description=project.description,
            team_members=members,
            current_tasks=tasks,
            milestones=milestones,
            user_query=user_query,
            chat_history=chat_history
        )

        async for chunk in self.llm.generate_stream(
            prompt=prompt,
            system_instruction=SYSTEM_COPILOT_PROMPT,
            temperature=0.4
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        yield "data: [DONE]\n\n"
