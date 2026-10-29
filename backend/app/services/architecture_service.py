import uuid
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.project_repo import ProjectRepository
from app.repositories.task_repo import TaskRepository
from app.repositories.advanced_ai_repo import AdvancedAIRepository
from ai.agents.architecture_designer import ArchitectureDesigner, SystemArchitectureBlueprint

logger = logging.getLogger("collabai.services.architecture")


class ArchitectureService:
    def __init__(self):
        self.designer = ArchitectureDesigner()
        self._cache: Dict[str, SystemArchitectureBlueprint] = {}

    async def _build_project_context(self, project_id: uuid.UUID, db: AsyncSession) -> Dict[str, Any]:
        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found",
            )

        task_repo = TaskRepository(db)
        tasks = await task_repo.list_by_project(project_id)

        adv_repo = AdvancedAIRepository(db)
        decisions = await adv_repo.list_decisions(project_id)

        return {
            "title": project.title,
            "description": project.description or "",
            "tags": project.tags or [],
            "skills_needed": project.skills_needed or [],
            "total_tasks_count": len(tasks),
            "decisions": [{"what": d.what, "why": d.why} for d in decisions],
        }

    async def get_project_blueprint(
        self, project_id: uuid.UUID, db: AsyncSession, force_refresh: bool = False
    ) -> SystemArchitectureBlueprint:
        cache_key = str(project_id)
        if not force_refresh and cache_key in self._cache:
            return self._cache[cache_key]

        context = await self._build_project_context(project_id, db)
        blueprint = await self.designer.generate_blueprint(context)
        self._cache[cache_key] = blueprint
        return blueprint

    async def calculate_latency_budget(
        self, project_id: uuid.UUID, db: AsyncSession
    ) -> Dict[str, Any]:
        blueprint = await self.get_project_blueprint(project_id, db)
        budgets = [c.latency_budget_ms for c in blueprint.components]
        total = sum(budgets)
        critical_path = max(budgets) if budgets else 100
        sla = "Passed (Under 800ms SLA)" if critical_path < 800 else "Warning (High Latency)"

        return {
            "project_title": blueprint.project_title,
            "total_budget_ms": total,
            "critical_path_ms": critical_path,
            "component_count": len(blueprint.components),
            "sla_compliance": sla,
        }

    async def export_blueprint_markdown(
        self, project_id: uuid.UUID, db: AsyncSession
    ) -> Dict[str, Any]:
        blueprint = await self.get_project_blueprint(project_id, db)
        title = blueprint.project_title

        md = f"""# {title} — System Architecture & Technical Specification

> **Architecture Pattern**: {blueprint.architecture_pattern}

## 🏛️ Executive Overview
{blueprint.executive_summary}

---

## 📐 System Architecture Diagram
```mermaid
{blueprint.mermaid_diagram}
```

---

## ⚡ Core Data Flow & Interaction Sequence
```mermaid
{blueprint.mermaid_sequence}
```

---

## 🧩 Subsystem & Component Matrix

| Component | Category | Tech Stack | Latency SLA | Key Responsibilities |
| :--- | :---: | :--- | :---: | :--- |
"""
        for comp in blueprint.components:
            resps = "; ".join(comp.responsibilities)
            md += f"| **{comp.name}** | `{comp.category}` | {comp.tech_stack} | {comp.latency_budget_ms} ms | {resps} |\n"

        md += "\n---\n\n## 🔒 Security & Isolation Policies\n"
        for note in blueprint.security_isolation_notes:
            md += f"- [x] {note}\n"

        md += "\n## 📈 Scalability Mitigations\n"
        for mit in blueprint.scaling_bottlenecks_and_mitigations:
            md += f"- **Scaling Consideration**: {mit}\n"

        slug = title.lower().replace(" ", "-")
        return {
            "project_title": title,
            "export_filename": f"{slug}-ARCHITECTURE.md",
            "markdown_content": md,
        }

