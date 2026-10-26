#!/usr/bin/env python3
"""
CollabAI End-to-End Operational Lifecycle Test Suite
Validates the complete full-stack flow:
1. System Observability and Health Verification
2. Student Matching and Skill Complementarity scoring
3. Autonomous Meeting Assistant transcription to structured Kanban action items
4. Architectural Decision Memory Graph traversal and rationale query
5. Multi-Agent Orchestrator roadmap and bottleneck synthesis
"""

import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from ai.agents.meeting_assistant import MeetingAssistant
from ai.agents.memory_graph import ProjectMemoryEngine
from ai.agents.orchestrator import MultiAgentOrchestrator
from ai.agents.code_assistant import CodeAssistant
from ai.ml.matching_v2 import MatchingEngineV2
from app.api.v1.system import get_system_status


class MockDBSession:
    async def execute(self, q):
        return 1


async def run_e2e_operational_suite():
    print("=" * 70)
    print(" CollabAI End-to-End Operational Lifecycle Test Suite")
    print("=" * 70)

    # 1. System Health Telemetry
    print("\n[Step 1/5] Verifying System Observability & Gateway Status...")
    mock_db = MockDBSession()
    sys_status = await get_system_status(db=mock_db)
    assert sys_status["service"] == "CollabAI"
    assert sys_status["database"]["status"] == "operational"
    print(f"  ✓ Service: {sys_status['service']} (v{sys_status['version']})")
    print(f"  ✓ Active AI Provider: {sys_status['ai_engine']['active_default']}")
    print(f"  ✓ Process Memory: {sys_status['process']['memory_rss_mb']} MB")

    # 2. Student Skill Matching
    print("\n[Step 2/5] Running ML Matcher V2 on student candidate...")
    candidate = {
        "id": "alex-456",
        "name": "Alex Rivera",
        "email": "alex@uni.edu",
        "skills": ["python", "fastapi", "pgvector"],
        "interests": ["ai", "open-source", "hackathons"],
        "roles": ["Backend Developer", "ML Engineer"],
        "hours_per_week": 20,
        "experience_level": "advanced",
    }
    project = {
        "title": "CollabAI Platform",
        "description": "AI-native student project workspace with RAG and multi-agent systems",
        "skills_needed": ["python", "fastapi", "react", "typescript"],
        "tags": ["ai", "hackathons"],
        "roles_needed": ["Backend Developer"],
        "hours_per_week": 15,
    }
    matcher = MatchingEngineV2()
    match_result = matcher.compute_match_v2(project_dict=project, candidate=candidate)
    assert match_result.match_score > 0
    print(f"  ✓ Match Score: {match_result.match_score}/100")
    print(f"  ✓ ML Rank Score: {match_result.ml_rank_score}/100")
    print(f"  ✓ Acceptance Probability: {match_result.acceptance_probability:.2%}")

    # 3. Voice Standup Action Item Conversion
    print("\n[Step 3/5] Testing Autonomous Voice Standup to Kanban Action Items...")
    assistant = MeetingAssistant()
    sample_transcript = """
    Team Standup:
    Sara: We need to set up Prometheus metrics for the production API gateway.
    Leo: I will take that task. Target: under 10ms exposition latency.
    Sara: Also we chose Groq as our fast tier fallback for Copilot chat.
    Leo: Approved. Let's make sure the docker-compose includes frontend service as well.
    """
    analysis = await assistant.analyze_transcript(
        transcript_text=sample_transcript,
        project_title="CollabAI",
        meeting_title="Sprint 8 Standup",
    )
    assert len(analysis.action_items) >= 1
    print(f"  ✓ Extracted {len(analysis.action_items)} action items & {len(analysis.decisions)} decisions")
    for item in analysis.action_items:
        print(f"    • [{item.suggested_priority.upper()}] {item.title}")

    # 4. Decision Memory Graph Search
    print("\n[Step 4/5] Querying Project Decision Memory Graph...")
    memory = ProjectMemoryEngine()
    decisions = [
        {
            "id": "dec-101",
            "project_id": "p-1",
            "what": "Adopt multi-stage Dockerfile for Next.js frontend",
            "why": "Minimizes container footprint and speeds up deployment on low-memory servers.",
            "who": "DevOps Lead",
            "when": "2026-10-26",
            "alternatives_considered": ["Single stage build"],
            "tags": ["docker", "frontend", "nextjs"],
        }
    ]
    query_res = await memory.query_memory(
        query="Why are we using multi-stage Docker builds for the frontend?",
        decisions=decisions,
        project_title="CollabAI",
    )
    assert query_res.matched_decisions
    print(f"  ✓ Rationale Retrieved: {query_res.matched_decisions[0].why}")

    # 5. Multi-Agent Orchestrator Roadmap Synthesis
    print("\n[Step 5/5] Executing Multi-Agent Consensus Orchestration...")
    orchestrator = MultiAgentOrchestrator()
    orch_res = await orchestrator.orchestrate(
        query="Assess deployment readiness and key launch milestones.",
        project_context={
            "title": "CollabAI Production Release",
            "description": "Student Collaboration Platform",
            "tasks_summary": {"total": 12, "completed": 10, "blocked": 0},
            "team_size": 4,
            "milestones": [{"title": "Day 8 Observability", "status": "completed"}],
        },
    )
    assert orch_res.executive_synthesis
    print(f"  ✓ Executive Synthesis: {orch_res.executive_synthesis[:120]}...")
    print(f"  ✓ Active Agents: {len(orch_res.participating_agents)}")

    print("\n" + "=" * 70)
    print("🎉 ALL 5/5 END-TO-END OPERATIONAL LIFECYCLE CHECKS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_e2e_operational_suite())
