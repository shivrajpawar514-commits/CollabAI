import asyncio
import os
import sys

# Ensure root is on path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from ai.agents.meeting_assistant import MeetingAssistant
from ai.agents.memory_graph import ProjectMemoryEngine
from ai.agents.orchestrator import MultiAgentOrchestrator
from ai.agents.code_assistant import CodeAssistant


async def run_tests():
    print("=== Testing Phase 7 Advanced AI Engines ===")

    # 1. Meeting Assistant Test
    print("\n1. Testing MeetingAssistant...")
    assistant = MeetingAssistant()
    transcript = """Alex: Let's finalize our vector database choice. We tested Pinecone vs PostgreSQL pgvector.
Maya: pgvector is cost-effective, runs in Docker with no cloud bill, and latency is under 30ms for 1536-dim embeddings.
Alex: Approved. Decision made: Use PostgreSQL pgvector extension for all semantic vector storage.
Maya: I'll complete the pgvector migration by Thursday. Estimated time: 6 hours, high priority.
Alex: I'll wire up the FastAPI vector search endpoint. Estimated time: 4 hours, medium priority."""

    analysis = await assistant.analyze_transcript(
        transcript_text=transcript,
        project_title="CollabAI",
        meeting_title="Vector DB Alignment",
    )
    assert analysis.meeting_title == "Vector DB Alignment", f"Unexpected title: {analysis.meeting_title}"
    assert len(analysis.action_items) >= 2, f"Expected at least 2 action items, got {len(analysis.action_items)}"
    assert len(analysis.decisions) >= 1, f"Expected at least 1 decision, got {len(analysis.decisions)}"
    print(f"✓ MeetingAssistant extracted {len(analysis.action_items)} action items & {len(analysis.decisions)} decisions")
    print(f"  Summary: {analysis.executive_summary[:100]}...")

    # 2. Decision Memory Engine Test
    print("\n2. Testing ProjectMemoryEngine...")
    memory = ProjectMemoryEngine()
    decisions = [
        {
            "id": "dec-1",
            "project_id": "proj-1",
            "what": "Use PostgreSQL pgvector for vector embeddings",
            "why": "Eliminates third-party cloud costs, runs in local Docker, and provides ACID compliance alongside relational data.",
            "who": "Architecture Team",
            "when": "2026-10-15",
            "alternatives_considered": ["Pinecone", "ChromaDB"],
            "tags": ["postgres", "pgvector", "database"],
        },
        {
            "id": "dec-2",
            "project_id": "proj-1",
            "what": "Use FastAPI for backend services",
            "why": "Async native support, automatic OpenAPI docs, and clean Pydantic type validation.",
            "who": "Backend Lead",
            "when": "2026-10-10",
            "alternatives_considered": ["Flask", "Django"],
            "tags": ["fastapi", "python", "backend"],
        },
    ]

    query_res = await memory.query_memory(
        query="Why did we choose PostgreSQL pgvector over Pinecone?",
        decisions=decisions,
        project_title="CollabAI",
    )
    assert query_res.matched_decisions, "Expected matched decisions"
    assert "pgvector" in query_res.matched_decisions[0].what.lower()
    print(f"✓ ProjectMemoryEngine answered: {query_res.answer[:120]}...")
    print(f"  Confidence score: {query_res.confidence_score:.2f}")

    # 3. Multi-Agent Orchestrator Test
    print("\n3. Testing MultiAgentOrchestrator...")
    orchestrator = MultiAgentOrchestrator()
    context = {
        "title": "CollabAI Production Launch",
        "description": "Collaborative project management with autonomous engineering AI.",
        "tasks": [
            {"title": "Implement pgvector similarity", "status": "done", "priority": "high", "estimated_hours": 6},
            {"title": "Setup JWT refresh rotation", "status": "blocked", "priority": "urgent", "estimated_hours": 5},
            {"title": "Deploy to Vercel and Railway", "status": "in_progress", "priority": "high", "estimated_hours": 8},
        ],
        "milestones": [
            {"title": "Phase 1: Foundation", "status": "completed"},
            {"title": "Phase 2: RAG & ML", "status": "in_progress"},
        ],
        "documents": ["Architecture Spec", "API Documentation"],
        "decisions": ["PostgreSQL pgvector chosen", "FastAPI chosen"],
        "tasks_summary": {"total": 3, "completed": 1, "blocked": 1},
        "team_size": 3,
    }

    orch_res = await orchestrator.orchestrate(
        query="Synthesize roadmap velocity and critical bottlenecks for demo launch.",
        project_context=context,
    )
    assert len(orch_res.participating_agents) == 3, f"Expected 3 agents, got {len(orch_res.participating_agents)}"
    assert len(orch_res.agent_insights) == 3, f"Expected 3 insights, got {len(orch_res.agent_insights)}"
    assert orch_res.executive_synthesis, "Executive synthesis should not be empty"
    print(f"✓ MultiAgentOrchestrator synchronized {len(orch_res.participating_agents)} agents")
    print(f"  Recommended next actions count: {len(orch_res.recommended_next_actions)}")

    # 4. Code Assistant & Readiness Test
    print("\n4. Testing CodeAssistant...")
    code_assistant = CodeAssistant()
    sample_code = """async def query_user(user_id: str, db):
    # Missing input validation
    q = f"SELECT * FROM users WHERE id = '{user_id}'"
    return await db.execute(q)
"""
    review = await code_assistant.review_code(sample_code, "user_repo.py", "python")
    assert review.score <= 85, f"Vulnerable code should get <= 85 score, got {review.score}"
    assert any("sql" in item.issue.lower() or "injection" in item.issue.lower() or "validation" in item.issue.lower() or "security" in item.category.lower() for item in review.review_items)
    print(f"✓ CodeAssistant detected security issue: score={review.score}")

    readiness = await code_assistant.audit_project_readiness(
        project_title="CollabAI",
        project_description="Next-gen AI Collaboration",
        tasks_stats={"total": 20, "completed": 16},
        milestones_stats={"total": 4},
        docs_count=5,
    )
    assert readiness.readiness_score >= 50
    assert readiness.letter_grade in ["A", "B", "C", "D", "Needs Work"]
    print(f"✓ Project Readiness Audit: {readiness.readiness_score}/100 (Grade: {readiness.letter_grade})")
    print(f"  Architecture: {readiness.architecture_score}%, Code Quality: {readiness.code_quality_score}%")

    print("\n=== ALL PHASE 7 ADVANCED AI TESTS PASSED! ===")


if __name__ == "__main__":
    asyncio.run(run_tests())
