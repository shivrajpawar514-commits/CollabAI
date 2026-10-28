import asyncio
import os
import sys
import uuid

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from ai.agents.judge_evaluator import JudgeEvaluator, HackathonJudgeEvaluation
from app.services.judge_evaluation_service import JudgeEvaluationService
from app.schemas.judge_evaluation import (
    HackathonJudgeEvaluationResponse,
    JudgeEvaluationSummaryResponse,
)


class DummyTask:
    def __init__(self, title, status):
        self.title = title
        self.status = status


class DummyDecision:
    def __init__(self, what, why):
        self.what = what
        self.why = why


class DummyMilestone:
    def __init__(self, title, status="in_progress"):
        self.title = title
        self.status = status


class DummyTeamMember:
    def __init__(self, name="Dev"):
        self.name = name


class DummyTeam:
    def __init__(self):
        self.members = [DummyTeamMember(), DummyTeamMember()]


class DummyProject:
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.description = "Autonomous AI-Native Student Collaboration Workspace"
        self.tags = ["AI", "Hackathon", "Collaboration"]
        self.skills_needed = ["FastAPI", "React", "PostgreSQL"]
        self.milestones = [
            DummyMilestone("Phase 1: Architecture Core", "completed"),
            DummyMilestone("Phase 2: Real-time Collaboration", "in_progress"),
        ]
        self.team = DummyTeam()


async def test_judge_evaluation_suite():
    print("=== Testing Hackathon Judge Evaluation Suite ===")

    # 1. Test JudgeEvaluator Core Engine
    print("\n1. Testing JudgeEvaluator rubric engine...")
    evaluator = JudgeEvaluator()
    sample_context = {
        "title": "CollabAI Next-Gen",
        "description": "AI agent platform for hackathons",
        "tags": ["Fullstack", "AI Agents", "FastAPI"],
        "skills_needed": ["Python", "TypeScript"],
        "total_tasks_count": 12,
        "completed_tasks_count": 9,
        "milestones": [
            {"title": "Phase 1: Core", "status": "completed"},
            {"title": "Phase 2: Polish", "status": "in_progress"},
        ],
        "decisions": [
            {"what": "Use pgvector for semantic search", "why": "Native Postgres storage"},
            {"what": "WebSocket real-time sync", "why": "Immediate cross-client state"},
        ],
        "velocity": {"velocity_score": 92, "velocity_grade": "A"},
    }

    evaluation = await evaluator.evaluate_project(sample_context)
    assert isinstance(evaluation, HackathonJudgeEvaluation)
    assert evaluation.overall_score >= 80, f"Expected overall score >= 80, got {evaluation.overall_score}"
    assert len(evaluation.criteria_breakdown) == 5, f"Expected 5 criteria, got {len(evaluation.criteria_breakdown)}"
    
    # Verify each rubric criterion has realistic bounds and tips
    criterion_names = [c.name for c in evaluation.criteria_breakdown]
    expected_criteria = [
        "Innovation & Novelty",
        "Technical Architecture & Depth",
        "Practical Impact & Market Need",
        "UI/UX Polish & Accessibility",
        "Completeness & Execution",
    ]
    for expected in expected_criteria:
        assert expected in criterion_names, f"Missing criterion: {expected}"

    for crit in evaluation.criteria_breakdown:
        assert 0 <= crit.score <= 20, f"Criterion {crit.name} score {crit.score} out of bounds"
        assert len(crit.strengths) >= 1, f"Missing strengths for {crit.name}"
        assert crit.judge_tips, f"Missing judge tips for {crit.name}"
        print(f"  ✓ {crit.name}: {crit.score}/20 (Weight: {crit.weight})")

    # 2. Test Judge Personas & Critiques
    print("\n2. Testing Judge Personas & Tough Pitch Q&A...")
    assert len(evaluation.judge_personas) == 3, f"Expected 3 personas, got {len(evaluation.judge_personas)}"
    for persona in evaluation.judge_personas:
        assert persona.verdict_score >= 70, f"Score too low: {persona.verdict_score}"
        assert persona.hard_question_to_prepare, "Missing tough pitch Q&A question"
        print(f"  ✓ [{persona.judge_role}] Score: {persona.verdict_score}/100")
        print(f"    Q&A Prep: '{persona.hard_question_to_prepare}'")

    # 3. Test Action Items and Executive Critique
    print("\n3. Testing Pitch Action Items & Verdict Badge...")
    assert len(evaluation.top_action_items_before_pitch) >= 3
    assert evaluation.verdict_badge
    print(f"  ✓ Verdict Badge: {evaluation.verdict_badge}")
    print(f"  ✓ Percentile Rank: {evaluation.percentile_rank_estimate}")

    # 4. Test Schema Serialization
    print("\n4. Testing Schema Serialization...")
    resp = HackathonJudgeEvaluationResponse(
        project_title=evaluation.project_title,
        overall_score=evaluation.overall_score,
        percentile_rank_estimate=evaluation.percentile_rank_estimate,
        verdict_badge=evaluation.verdict_badge,
        criteria_breakdown=[c.model_dump() for c in evaluation.criteria_breakdown],
        judge_personas=[p.model_dump() for p in evaluation.judge_personas],
        top_action_items_before_pitch=evaluation.top_action_items_before_pitch,
        raw_executive_critique=evaluation.raw_executive_critique,
    )
    assert resp.overall_score == evaluation.overall_score

    # 5. Test JudgeEvaluationService Summary Generation
    print("\n5. Testing JudgeEvaluationService caching & summary...")
    service = JudgeEvaluationService()
    test_id = uuid.uuid4()

    # Pre-populate cache to test fast summary extraction
    service._cache[str(test_id)] = evaluation
    summary = await service.get_evaluation_summary(test_id, db=None)
    assert summary["project_title"] == evaluation.project_title
    assert summary["overall_score"] == evaluation.overall_score
    assert len(summary["radar"]) == 5
    summary_resp = JudgeEvaluationSummaryResponse(**summary)
    assert summary_resp.overall_score == evaluation.overall_score
    print(f"  ✓ Summary Radar Items: {len(summary_resp.radar)}")
    print(f"  ✓ Top Recommendation: '{summary_resp.top_recommendation}'")

    print("\n=== ALL HACKATHON JUDGE EVALUATION TESTS PASSED! ===")


if __name__ == "__main__":
    asyncio.run(test_judge_evaluation_suite())
