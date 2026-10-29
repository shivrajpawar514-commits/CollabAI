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

from ai.agents.architecture_designer import (
    ArchitectureDesigner,
    SystemArchitectureBlueprint,
)
from app.services.architecture_service import ArchitectureService
from app.schemas.architecture import (
    SystemArchitectureBlueprintResponse,
    ArchitectureExportResponse,
    LatencyBudgetSummaryResponse,
)


async def test_architecture_blueprint_suite():
    print("=== Testing System Architecture Blueprint Suite ===")

    # 1. Test ArchitectureDesigner Generator
    print("\n1. Testing ArchitectureDesigner synthesis & Mermaid generation...")
    designer = ArchitectureDesigner()
    sample_context = {
        "title": "CollabAI Production Platform",
        "description": "Multi-agent real-time collaborative workspace for hackathons",
        "tags": ["FullStack", "FastAPI", "Next.js", "AI Agents"],
        "skills_needed": ["Python", "TypeScript", "PostgreSQL", "Docker"],
        "total_tasks_count": 24,
        "decisions": [
            {"what": "PostgreSQL with pgvector for unified storage", "why": "Eliminates third-party vector SaaS latency"},
            {"what": "FastAPI WebSockets for room sync", "why": "Immediate cross-client state updates"},
        ],
    }

    blueprint = await designer.generate_blueprint(sample_context)
    assert isinstance(blueprint, SystemArchitectureBlueprint)
    assert blueprint.project_title == "CollabAI Production Platform"
    assert len(blueprint.components) >= 4, f"Expected >= 4 components, got {len(blueprint.components)}"
    assert len(blueprint.data_flows) >= 4, f"Expected >= 4 flows, got {len(blueprint.data_flows)}"

    # Validate Mermaid Diagram strings
    assert "graph TD" in blueprint.mermaid_diagram, "Mermaid graph must start with 'graph TD'"
    assert "Next.js" in blueprint.mermaid_diagram or "Frontend" in blueprint.mermaid_diagram
    assert "sequenceDiagram" in blueprint.mermaid_sequence, "Sequence diagram must start with 'sequenceDiagram'"
    print(f"  ✓ Components: {len(blueprint.components)}")
    print(f"  ✓ Data Flows: {len(blueprint.data_flows)}")
    print(f"  ✓ Mermaid Graph length: {len(blueprint.mermaid_diagram)} chars")
    print(f"  ✓ Mermaid Sequence length: {len(blueprint.mermaid_sequence)} chars")

    # 2. Test Component SLAs and Latencies
    print("\n2. Validating component latency budgets and responsibilities...")
    for comp in blueprint.components:
        assert comp.latency_budget_ms > 0, f"Component {comp.name} latency must be > 0"
        assert comp.responsibilities, f"Component {comp.name} must have responsibilities"
        print(f"  ✓ {comp.name} ({comp.category}): {comp.latency_budget_ms} ms SLA [{comp.tech_stack[:35]}...]")

    # 3. Test Service Caching, Latency Aggregation & Markdown Export
    print("\n3. Testing ArchitectureService caching, latency budget & export...")
    service = ArchitectureService()
    test_id = uuid.uuid4()
    service._cache[str(test_id)] = blueprint

    # Latency budget check
    latency = await service.calculate_latency_budget(test_id, db=None)
    assert latency["component_count"] == len(blueprint.components)
    assert latency["total_budget_ms"] > 0
    assert latency["critical_path_ms"] > 0
    assert "Passed" in latency["sla_compliance"]
    print(f"  ✓ Total Budget: {latency['total_budget_ms']} ms | Critical Path: {latency['critical_path_ms']} ms")
    print(f"  ✓ SLA Status: {latency['sla_compliance']}")

    # Export markdown check
    export = await service.export_blueprint_markdown(test_id, db=None)
    assert export["export_filename"].endswith("-ARCHITECTURE.md")
    assert "```mermaid" in export["markdown_content"]
    assert "# CollabAI Production Platform" in export["markdown_content"]
    print(f"  ✓ Export Filename: {export['export_filename']}")
    print(f"  ✓ Export Markdown length: {len(export['markdown_content'])} bytes")

    # 4. Schema validation
    print("\n4. Testing Pydantic Schema Serialization...")
    resp = SystemArchitectureBlueprintResponse(
        project_title=blueprint.project_title,
        architecture_pattern=blueprint.architecture_pattern,
        executive_summary=blueprint.executive_summary,
        components=[c.model_dump() for c in blueprint.components],
        data_flows=[f.model_dump() for f in blueprint.data_flows],
        mermaid_diagram=blueprint.mermaid_diagram,
        mermaid_sequence=blueprint.mermaid_sequence,
        security_isolation_notes=blueprint.security_isolation_notes,
        scaling_bottlenecks_and_mitigations=blueprint.scaling_bottlenecks_and_mitigations,
    )
    assert resp.project_title == blueprint.project_title

    print("\n=== ALL SYSTEM ARCHITECTURE BLUEPRINT TESTS PASSED! ===")


if __name__ == "__main__":
    asyncio.run(test_architecture_blueprint_suite())
