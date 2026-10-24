import os
import sys
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ai.agents.meeting_assistant import MeetingAssistant, MeetingAnalysisResult
from ai.agents.memory_graph import ProjectMemoryEngine, DecisionMemoryAnswer
from ai.agents.orchestrator import MultiAgentOrchestrator, MultiAgentOrchestrationResult
from ai.agents.code_assistant import (
    CodeAssistant,
    CodeReviewResult,
    GeneratedTestsResult,
    ProjectReadinessReport,
)

from app.repositories.advanced_ai_repo import AdvancedAIRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.advanced_ai import (
    MeetingNoteResponse,
    MeetingActionItemResponse,
    ConvertActionItemsResponse,
    DecisionCreate,
    DecisionResponse,
    DecisionQueryResponse,
    OrchestratorResponse,
    CodeReviewResponse,
)
from app.schemas.task import TaskResponse


class AdvancedAIService:
    def __init__(self):
        self.meeting_assistant = MeetingAssistant()
        self.memory_engine = ProjectMemoryEngine()
        self.orchestrator = MultiAgentOrchestrator()
        self.code_assistant = CodeAssistant()

    # 1. Voice & Meeting Assistant
    async def analyze_and_save_meeting(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        transcript_text: str,
        meeting_title: Optional[str],
        db: AsyncSession,
    ) -> MeetingNoteResponse:
        p_repo = ProjectRepository(db)
        project = await p_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        ai_repo = AdvancedAIRepository(db)

        # AI analysis
        analysis: MeetingAnalysisResult = await self.meeting_assistant.analyze_transcript(
            transcript_text=transcript_text,
            project_title=project.title,
            meeting_title=meeting_title,
        )

        # Map action items
        action_items_payload = [
            {
                "title": item.title,
                "description": item.description,
                "suggested_assignee": item.suggested_assignee,
                "priority": item.suggested_priority,
                "estimated_hours": item.estimated_hours,
            }
            for item in analysis.action_items
        ]

        # Save meeting note and action items
        meeting_note = await ai_repo.create_meeting_note_with_actions(
            project_id=project_id,
            organizer_id=user_id,
            title=analysis.meeting_title,
            raw_transcript=transcript_text,
            executive_summary=analysis.executive_summary,
            key_topics=analysis.key_topics,
            overall_sentiment=analysis.overall_sentiment,
            action_items=action_items_payload,
        )

        # Automatically persist extracted decisions into project memory graph
        for dec in analysis.decisions:
            dec_in = DecisionCreate(
                what=dec.what,
                why=dec.why,
                who=dec.who or "Meeting Decision",
                alternatives=dec.alternatives_considered,
                tags=dec.tags or ["meeting"],
            )
            await ai_repo.create_decision(
                project_id=project_id,
                recorder_id=user_id,
                d_in=dec_in,
            )

        return MeetingNoteResponse.model_validate(meeting_note)

    async def get_project_meetings(
        self,
        project_id: uuid.UUID,
        db: AsyncSession,
    ) -> List[MeetingNoteResponse]:
        ai_repo = AdvancedAIRepository(db)
        notes = await ai_repo.get_project_meetings(project_id)
        return [MeetingNoteResponse.model_validate(n) for n in notes]

    async def convert_meeting_action_items(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        action_item_ids: List[uuid.UUID],
        target_milestone_id: Optional[uuid.UUID],
        db: AsyncSession,
    ) -> ConvertActionItemsResponse:
        ai_repo = AdvancedAIRepository(db)
        tasks = await ai_repo.convert_action_items_to_tasks(
            project_id=project_id,
            creator_id=user_id,
            action_item_ids=action_item_ids,
            target_milestone_id=target_milestone_id,
        )
        task_responses = [TaskResponse.model_validate(t) for t in tasks]
        return ConvertActionItemsResponse(
            converted_count=len(tasks),
            created_tasks=task_responses,
        )

    # 2. Decision Memory & Knowledge Graph
    async def save_decision(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        d_in: DecisionCreate,
        db: AsyncSession,
    ) -> DecisionResponse:
        ai_repo = AdvancedAIRepository(db)
        decision = await ai_repo.create_decision(
            project_id=project_id,
            recorder_id=user_id,
            d_in=d_in,
        )
        return DecisionResponse.model_validate(decision)

    async def get_project_decisions(
        self,
        project_id: uuid.UUID,
        db: AsyncSession,
    ) -> List[DecisionResponse]:
        ai_repo = AdvancedAIRepository(db)
        decisions = await ai_repo.get_project_decisions(project_id)
        return [DecisionResponse.model_validate(d) for d in decisions]

    async def query_decision_memory(
        self,
        project_id: uuid.UUID,
        query: str,
        db: AsyncSession,
    ) -> DecisionQueryResponse:
        p_repo = ProjectRepository(db)
        project = await p_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        ai_repo = AdvancedAIRepository(db)
        decisions = await ai_repo.get_project_decisions(project_id)

        decisions_payload = [
            {
                "id": str(d.id),
                "project_id": str(d.project_id),
                "what": d.what,
                "why": d.why,
                "who": d.who,
                "when": d.created_at.strftime("%Y-%m-%d"),
                "alternatives_considered": d.alternatives_json or [],
                "tags": d.tags_json or [],
                "linked_task_id": str(d.linked_task_id) if d.linked_task_id else None,
                "linked_document_id": str(d.linked_document_id) if d.linked_document_id else None,
            }
            for d in decisions
        ]

        result: DecisionMemoryAnswer = await self.memory_engine.query_memory(
            query=query,
            decisions=decisions_payload,
            project_title=project.title,
        )

        return DecisionQueryResponse(
            query=result.query,
            answer=result.answer,
            confidence_score=result.confidence_score,
            matched_decisions=result.matched_decisions,
        )

    # 3. Multi-Agent Orchestrator
    async def run_multi_agent_orchestrator(
        self,
        project_id: uuid.UUID,
        query: str,
        db: AsyncSession,
    ) -> OrchestratorResponse:
        ai_repo = AdvancedAIRepository(db)
        raw_ctx = await ai_repo.get_project_context(project_id)
        project = raw_ctx.get("project")
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        tasks = raw_ctx.get("tasks", [])
        milestones = raw_ctx.get("milestones", [])
        documents = raw_ctx.get("documents", [])
        decisions = raw_ctx.get("decisions", [])
        team_members = raw_ctx.get("team_members", [])

        completed_tasks = [t for t in tasks if t.status == "done"]
        blocked_tasks = [t for t in tasks if t.status == "blocked"]

        context_dict = {
            "title": project.title,
            "description": project.description or "",
            "tasks": [
                {
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority,
                    "estimated_hours": t.estimated_hours,
                }
                for t in tasks[:30]
            ],
            "milestones": [
                {
                    "title": m.title,
                    "status": m.status,
                    "deadline": m.deadline.strftime("%Y-%m-%d") if m.deadline else None,
                }
                for m in milestones
            ],
            "documents": [d.title for d in documents[:15]],
            "decisions": [d.what for d in decisions[:15]],
            "tasks_summary": {
                "total": len(tasks),
                "completed": len(completed_tasks),
                "blocked": len(blocked_tasks),
            },
            "team_size": len(team_members),
        }

        res: MultiAgentOrchestrationResult = await self.orchestrator.orchestrate(
            query=query,
            project_context=context_dict,
        )

        return OrchestratorResponse(
            query=res.query,
            executive_synthesis=res.executive_synthesis,
            participating_agents=res.participating_agents,
            agent_insights=res.agent_insights,
            recommended_next_actions=res.recommended_next_actions,
        )

    # 4. Code Assistant & Project Readiness
    async def review_code(
        self,
        code: str,
        file_name: Optional[str] = "main.py",
        language: Optional[str] = "python",
    ) -> CodeReviewResponse:
        review: CodeReviewResult = await self.code_assistant.review_code(
            code=code,
            file_name=file_name or "main.py",
            language=language or "python",
        )
        return CodeReviewResponse(
            score=review.score,
            summary=review.summary,
            review_items=review.review_items,
            suggested_refactor=review.suggested_refactor,
        )

    async def generate_unit_tests(
        self,
        code: str,
        file_name: Optional[str] = "main.py",
        framework: Optional[str] = "pytest",
    ) -> GeneratedTestsResult:
        return await self.code_assistant.generate_unit_tests(
            code=code,
            file_name=file_name or "main.py",
            framework=framework or "pytest",
        )

    async def audit_project_readiness(
        self,
        project_id: uuid.UUID,
        db: AsyncSession,
    ) -> ProjectReadinessReport:
        ai_repo = AdvancedAIRepository(db)
        raw_ctx = await ai_repo.get_project_context(project_id)
        project = raw_ctx.get("project")
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        tasks = raw_ctx.get("tasks", [])
        milestones = raw_ctx.get("milestones", [])
        documents = raw_ctx.get("documents", [])

        completed_tasks = [t for t in tasks if t.status == "done"]

        tasks_stats = {
            "total": len(tasks),
            "completed": len(completed_tasks),
        }
        milestones_stats = {
            "total": len(milestones),
        }

        return await self.code_assistant.audit_project_readiness(
            project_title=project.title,
            project_description=project.description or "",
            tasks_stats=tasks_stats,
            milestones_stats=milestones_stats,
            docs_count=len(documents),
        )
