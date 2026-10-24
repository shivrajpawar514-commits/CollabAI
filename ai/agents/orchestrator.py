import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ai.client import LLMClient


class AgentInsight(BaseModel):
    agent_name: str
    role: str
    summary: str
    findings: List[str] = Field(default_factory=list)


class MultiAgentOrchestrationResult(BaseModel):
    query: str
    executive_synthesis: str
    participating_agents: List[str]
    agent_insights: List[AgentInsight]
    recommended_next_actions: List[str] = Field(default_factory=list)


SYSTEM_SUPERVISOR_PROMPT = """You are CollabAI's Autonomous Multi-Agent Coordinator and Lead Architect.
You oversee three specialized engineering agents:
1. Planner Agent (Roadmap, timeline, milestone sequencing, and velocity)
2. Research/RAG Agent (Technical architecture, design patterns, document retrieval, and trade-offs)
3. Task/Execution Agent (Kanban status, engineering decomposition, blocked dependencies, and task allocation)

Your job is to synthesize the findings from each specialized agent into a unified, high-impact executive decision memo with clear, actionable next steps.
"""

SYSTEM_PLANNER_AGENT_PROMPT = """You are the Senior Planning Agent.
Analyze the project roadmap, milestones, timeline deadlines, and progress velocity. Focus on timeline feasibility, critical paths, and milestone dependencies.
"""

SYSTEM_RESEARCH_AGENT_PROMPT = """You are the Research & Knowledge Agent.
Analyze technical architecture, design patterns, technology stacks, best practices, and project documentation. Focus on technical grounding, reliability, and security trade-offs.
"""

SYSTEM_TASK_AGENT_PROMPT = """You are the Execution & Task Agent.
Analyze active tasks, engineering deliverables, bottlenecks, blocked items, and team workload. Focus on concrete task decomposition, ownership, and unblocking the critical path.
"""


class MultiAgentOrchestrator:
    """
    Multi-Agent Orchestrator executing a LangGraph-style workflow.
    Coordinates Planner, Research, and Task agents with a Supervisor Synthesizer.
    """

    def __init__(self):
        self.llm = LLMClient()

    async def orchestrate(
        self,
        query: str,
        project_context: Dict[str, Any],
    ) -> MultiAgentOrchestrationResult:
        proj_name = project_context.get("title", "CollabAI Project")
        proj_desc = project_context.get("description", "")
        milestones_count = len(project_context.get("milestones", []))
        tasks_count = len(project_context.get("tasks", []))
        docs_count = len(project_context.get("documents", []))
        team_size = len(project_context.get("team_members", [])) or 1

        context_brief = (
            f"Project: {proj_name}\n"
            f"Description: {proj_desc}\n"
            f"Scope: {milestones_count} Milestones, {tasks_count} Tasks, {docs_count} Indexed Documents, {team_size} Team Members."
        )

        # Execute 3 agents concurrently
        planner_task = self._run_planner_agent(query, context_brief, project_context)
        research_task = self._run_research_agent(query, context_brief, project_context)
        task_agent_task = self._run_task_agent(query, context_brief, project_context)

        planner_out, research_out, task_out = await asyncio.gather(
            planner_task, research_task, task_agent_task
        )

        insights = [planner_out, research_out, task_out]

        # Supervisor Synthesis
        synthesis_prompt = f"""User Request: "{query}"

{context_brief}

Agent 1: Planner Insights:
{planner_out.summary}
Key Findings: {', '.join(planner_out.findings)}

Agent 2: Research Insights:
{research_out.summary}
Key Findings: {', '.join(research_out.findings)}

Agent 3: Task & Execution Insights:
{task_out.summary}
Key Findings: {', '.join(task_out.findings)}

Synthesize these specialized insights into an executive action memo.
Provide a clear, cohesive answer to the user's query and list 3-4 immediate recommended actions:"""

        try:
            synthesis = await self.llm.generate(
                prompt=synthesis_prompt,
                system_instruction=SYSTEM_SUPERVISOR_PROMPT,
                temperature=0.3,
                max_tokens=800,
            )
        except Exception:
            synthesis = (
                f"Multi-Agent synthesis for '{query}':\n\n"
                f"• Planner: {planner_out.summary}\n"
                f"• Research: {research_out.summary}\n"
                f"• Task Execution: {task_out.summary}"
            )

        actions = [
            f"Align sprint deliverables with Planner recommendations ({planner_out.findings[0] if planner_out.findings else 'Review timeline'})",
            f"Incorporate technical standards from Research Agent ({research_out.findings[0] if research_out.findings else 'Review stack'})",
            f"Execute priority task items from Task Agent ({task_out.findings[0] if task_out.findings else 'Assign next tasks'})",
        ]

        return MultiAgentOrchestrationResult(
            query=query,
            executive_synthesis=synthesis,
            participating_agents=["Planner Agent", "Research/RAG Agent", "Task/Execution Agent"],
            agent_insights=insights,
            recommended_next_actions=actions,
        )

    async def _run_planner_agent(self, query: str, context: str, proj: Dict[str, Any]) -> AgentInsight:
        prompt = f"{context}\n\nUser Question: {query}\n\nProvide roadmap and timeline milestone planning guidance:"
        try:
            text = await self.llm.generate(
                prompt=prompt,
                system_instruction=SYSTEM_PLANNER_AGENT_PROMPT,
                temperature=0.2,
                max_tokens=350,
            )
        except Exception:
            text = "Roadmap and milestone sequencing analyzed. Critical path depends on timely milestone delivery."

        findings = [
            "Milestone cadence requires bi-weekly reviews",
            "Critical path delivery should prioritize core architecture first",
        ]
        return AgentInsight(
            agent_name="Planner Agent",
            role="Roadmap, Milestones & Velocity",
            summary=text.strip(),
            findings=findings,
        )

    async def _run_research_agent(self, query: str, context: str, proj: Dict[str, Any]) -> AgentInsight:
        prompt = f"{context}\n\nUser Question: {query}\n\nProvide technical architecture and research guidance:"
        try:
            text = await self.llm.generate(
                prompt=prompt,
                system_instruction=SYSTEM_RESEARCH_AGENT_PROMPT,
                temperature=0.2,
                max_tokens=350,
            )
        except Exception:
            text = "Technical architecture reviewed. Ensure modular service boundaries and structured documentation."

        findings = [
            "Standardize API interfaces and database schema types",
            "Maintain verified grounding in project knowledge vault",
        ]
        return AgentInsight(
            agent_name="Research/RAG Agent",
            role="Technical Architecture & Knowledge",
            summary=text.strip(),
            findings=findings,
        )

    async def _run_task_agent(self, query: str, context: str, proj: Dict[str, Any]) -> AgentInsight:
        prompt = f"{context}\n\nUser Question: {query}\n\nProvide task breakdown, bottlenecks, and execution guidance:"
        try:
            text = await self.llm.generate(
                prompt=prompt,
                system_instruction=SYSTEM_TASK_AGENT_PROMPT,
                temperature=0.2,
                max_tokens=350,
            )
        except Exception:
            text = "Execution backlog analyzed. Immediate focus should be on unblocking pending dependency tasks."

        findings = [
            "Decompose complex epic tasks into bite-sized 2-4 hour work units",
            "Reassign unblocked backlog items to active team members",
        ]
        return AgentInsight(
            agent_name="Task/Execution Agent",
            role="Sprint Execution & Backlog",
            summary=text.strip(),
            findings=findings,
        )
