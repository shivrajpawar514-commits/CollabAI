import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ai.client import LLMClient

logger = logging.getLogger("collabai.ai.architecture_designer")


class ArchitectureComponent(BaseModel):
    name: str = Field(description="Component name (e.g. 'FastAPI Async Backend Gateway')")
    category: str = Field(description="'frontend', 'backend', 'database', 'ai_engine', 'messaging'")
    tech_stack: str = Field(description="Specific libraries and framework technologies used")
    description: str = Field(description="Primary architectural role and purpose")
    latency_budget_ms: int = Field(description="Target response time SLA in milliseconds")
    responsibilities: List[str] = Field(description="Key responsibilities of this module")


class ArchitectureDataFlow(BaseModel):
    flow_name: str = Field(description="Name of interaction flow, e.g. 'Real-time WebSocket Task Broadcast'")
    step_number: int = Field(description="Order of execution in pipeline")
    source_component: str = Field(description="Originating subsystem")
    target_component: str = Field(description="Receiving subsystem")
    protocol: str = Field(description="'HTTP/2', 'WebSocket', 'SQL/TCP', 'IPC'")
    payload_summary: str = Field(description="Short summary of transferred data payload")


class SystemArchitectureBlueprint(BaseModel):
    project_title: str
    architecture_pattern: str = Field(description="e.g. 'Modular Event-Driven Architecture with pgvector RAG Pipeline'")
    executive_summary: str = Field(description="Technical overview of system topology and architectural decisions")
    components: List[ArchitectureComponent] = Field(description="Core subsystems forming the engineering solution")
    data_flows: List[ArchitectureDataFlow] = Field(description="Critical paths in data lifecycle")
    mermaid_diagram: str = Field(description="Valid Mermaid graph TD markdown representation")
    mermaid_sequence: str = Field(description="Valid Mermaid sequenceDiagram markdown representation")
    security_isolation_notes: List[str] = Field(description="Key security, sandbox, and isolation principles")
    scaling_bottlenecks_and_mitigations: List[str] = Field(description="Potential scale bottlenecks and mitigations")


SYSTEM_ARCHITECTURE_PROMPT = """You are CollabAI's Principal Enterprise Solutions Architect and Systems Engineering Specialist.
Your task is to analyze project workspace parameters, backend models, RAG vector pipelines, and real-time channels to produce
a production-grade SystemArchitectureBlueprint.

Rules:
1. Output valid, highly readable Mermaid diagrams (both graph TD and sequenceDiagram).
2. Incorporate concrete components: Next.js 14 client, FastAPI async gateways, PostgreSQL + pgvector, swappable LLM adapters, WebSocket event broadcast.
3. Define strict latency budgets for each subsystem (e.g., UI < 50ms, Gateway < 30ms, Vector search < 60ms, LLM Streaming TTFT < 600ms).
4. Provide pragmatic security guidelines (JWT auth, token scoping, parameter validation, container sandbox).
"""


class ArchitectureDesigner:
    def __init__(self, client: Optional[LLMClient] = None):
        self.client = client or LLMClient()

    async def generate_blueprint(self, project_context: Dict[str, Any]) -> SystemArchitectureBlueprint:
        title = project_context.get("title", "CollabAI Platform")
        description = project_context.get("description", "")
        tags = project_context.get("tags", [])
        skills = project_context.get("skills_needed", [])
        tasks_count = project_context.get("total_tasks_count", 0)
        decisions = project_context.get("decisions", [])

        prompt = f"""Generate a comprehensive SystemArchitectureBlueprint for:
Project Title: {title}
Description: {description}
Categories: {tags}
Tech Stack: {skills}
Tasks Count: {tasks_count}
Key Decisions: {[d.get('what') for d in decisions]}

Return valid Mermaid diagrams (graph TD and sequenceDiagram), comprehensive component specifications, and latency budgets.
"""
        try:
            result = await self.client.generate_structured(
                prompt=prompt,
                schema=SystemArchitectureBlueprint,
                system_instruction=SYSTEM_ARCHITECTURE_PROMPT,
                temperature=0.2,
            )
            return result
        except Exception as e:
            logger.warning("LLM Architecture design failed (%s), generating deterministic blueprint", e)
            return self._synthesize_blueprint(project_context)

    def _synthesize_blueprint(self, project_context: Dict[str, Any]) -> SystemArchitectureBlueprint:
        title = project_context.get("title", "CollabAI Platform")

        components = [
            ArchitectureComponent(
                name="Next.js 14 Client Application",
                category="frontend",
                tech_stack="Next.js 14 (App Router), React 18, Tailwind CSS, Lucide Icons",
                description="High-density responsive web client providing real-time Kanban, AI workspace, and diagnostic telemetry.",
                latency_budget_ms=35,
                responsibilities=[
                    "Client-side optimistic state management",
                    "Persistent WebSocket connection for real-time board updates",
                    "Modal presentation for Hackathon Pitch Deck and Judge Scorecard",
                ],
            ),
            ArchitectureComponent(
                name="FastAPI Asynchronous Gateway",
                category="backend",
                tech_stack="FastAPI, Python 3.14, AsyncIO, Uvicorn, Pydantic V2",
                description="High-throughput asynchronous REST and WebSocket API gateway with dependency injection.",
                latency_budget_ms=25,
                responsibilities=[
                    "Route validation and JWT OAuth2 bearer token authentication",
                    "WebSocket connection multiplexing across project rooms",
                    "Prometheus system metrics export and latency telemetry",
                ],
            ),
            ArchitectureComponent(
                name="PostgreSQL & pgvector Store",
                category="database",
                tech_stack="PostgreSQL 16, pgvector extension, SQLAlchemy 2.0 Async, Alembic",
                description="ACID-compliant relational database and vector embedding storage for semantic retrieval.",
                latency_budget_ms=45,
                responsibilities=[
                    "Relational persistence of users, teams, tasks, and audit logs",
                    "Cosine distance indexing (HNSW/IVFFlat) for 1536-dim document embeddings",
                    "Decision memory graph storage with bidirectional node linking",
                ],
            ),
            ArchitectureComponent(
                name="Swappable Multi-Provider LLM Engine",
                category="ai_engine",
                tech_stack="Google Gemini 1.5, OpenAI GPT-4o, Anthropic Claude 3.5, Ollama",
                description="Unified inference client with automatic fallback, rate-limit backoff, and JSON schema enforcement.",
                latency_budget_ms=550,
                responsibilities=[
                    "Autonomous task decomposition and milestone synthesis",
                    "Hackathon judge evaluation and 5-criteria rubric scoring",
                    "Pitch deck 7-slide slide deck compilation and presenter notes",
                ],
            ),
            ArchitectureComponent(
                name="Real-Time WebSocket Message Broker",
                category="messaging",
                tech_stack="FastAPI WebSocket Hub, In-Memory Event Dispatcher, Redis Pub/Sub",
                description="Low-latency bidirectional push infrastructure for synchronized team collaboration.",
                latency_budget_ms=15,
                responsibilities=[
                    "Instant Kanban card drag-and-drop broadcast",
                    "Live multi-user chat message distribution",
                    "Presence detection and connection heartbeats",
                ],
            ),
        ]

        data_flows = [
            ArchitectureDataFlow(
                flow_name="Client Authentication & Handshake",
                step_number=1,
                source_component="Next.js 14 Client Application",
                target_component="FastAPI Asynchronous Gateway",
                protocol="HTTP/2 POST",
                payload_summary="Bearer token generation via JWT with claims and project permission scope.",
            ),
            ArchitectureDataFlow(
                flow_name="Live Room WebSocket Connection",
                step_number=2,
                source_component="Next.js 14 Client Application",
                target_component="Real-Time WebSocket Message Broker",
                protocol="WSS",
                payload_summary="WebSocket upgrade with project room authorization handshake.",
            ),
            ArchitectureDataFlow(
                flow_name="Semantic Knowledge Retrieval (RAG)",
                step_number=3,
                source_component="FastAPI Asynchronous Gateway",
                target_component="PostgreSQL & pgvector Store",
                protocol="SQL/TCP",
                payload_summary="Cosine distance similarity query over document chunks (threshold < 0.25).",
            ),
            ArchitectureDataFlow(
                flow_name="Autonomous AI Synthesis",
                step_number=4,
                source_component="FastAPI Asynchronous Gateway",
                target_component="Swappable Multi-Provider LLM Engine",
                protocol="HTTPS JSON",
                payload_summary="Structured prompt with Pydantic response schema enforcement.",
            ),
            ArchitectureDataFlow(
                flow_name="Broadcast State Synchronization",
                step_number=5,
                source_component="Real-Time WebSocket Message Broker",
                target_component="Next.js 14 Client Application",
                protocol="WSS Push",
                payload_summary="Delta event notification with updated task, chat, or decision payload.",
            ),
        ]

        mermaid_graph = """graph TD
    subgraph ClientLayer["🖥️ Frontend Client Layer"]
        UI["Next.js 14 Web App<br/>(React 18 + Tailwind)"]
        WSClient["WebSocket Client<br/>(Live State Sync)"]
    end

    subgraph APILayer["⚡ Asynchronous Gateway Layer"]
        Gateway["FastAPI Gateway<br/>(AsyncIO + Uvicorn)"]
        AuthMiddleware["OAuth2 & JWT Auth"]
        MetricsRouter["Observability & Prometheus<br/>(/metrics)"]
    end

    subgraph ServiceLayer["🧠 Business & AI Orchestration"]
        TaskSvc["Task & Sprint Engine"]
        RAGSvc["RAG Knowledge Vault"]
        JudgeSvc["Judge Evaluation Engine"]
        PitchSvc["Pitch Deck Generator"]
        LLMAdapter["Swappable LLM Client<br/>(Gemini / OpenAI / Ollama)"]
    end

    subgraph DataLayer["💾 Persistence & State Storage"]
        PG[("PostgreSQL 16<br/>Relational Data")]
        PGVector[("pgvector Extension<br/>HNSW Semantic Index")]
        WSHub["WebSocket Pub/Sub Hub"]
    end

    UI -->|REST API Requests| Gateway
    WSClient <-->|Bidirectional Events| WSHub
    Gateway --> AuthMiddleware
    Gateway --> MetricsRouter
    Gateway --> TaskSvc
    Gateway --> RAGSvc
    Gateway --> JudgeSvc
    Gateway --> PitchSvc
    
    RAGSvc --> PGVector
    RAGSvc --> LLMAdapter
    TaskSvc --> PG
    TaskSvc --> WSHub
    JudgeSvc --> LLMAdapter
    PitchSvc --> LLMAdapter
    
    classDef client fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef api fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef service fill:#1e1b4b,stroke:#c084fc,stroke-width:2px,color:#f8fafc;
    classDef data fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#f8fafc;
    
    class UI,WSClient client;
    class Gateway,AuthMiddleware,MetricsRouter api;
    class TaskSvc,RAGSvc,JudgeSvc,PitchSvc,LLMAdapter service;
    class PG,PGVector,WSHub data;"""

        mermaid_sequence = """sequenceDiagram
    autonumber
    actor User as Student Developer
    participant UI as Next.js Client
    participant GW as FastAPI Gateway
    participant DB as PostgreSQL + pgvector
    participant AI as Swappable LLM Engine
    participant WS as WebSocket Hub

    User->>UI: Request AI Judge Evaluation
    UI->>GW: POST /projects/{id}/judge-eval (JWT Auth)
    GW->>DB: Query Tasks, Milestones, and Decisions
    DB-->>GW: Return Project Engineering Context
    GW->>AI: Evaluate 5-Criteria Rubric (Pydantic Schema)
    AI-->>GW: Structured Verdict & Persona Critiques
    GW->>DB: Cache Evaluation Scorecard
    GW->>WS: Broadcast Evaluation Completion
    WS-->>UI: Real-Time Scorecard Update (Score: 91/100)
    UI-->>User: Display Interactive Judge Modal"""

        security_notes = [
            "Stateless JWT access tokens with short TTL and cryptographically signed claims",
            "Strict SQL injection immunity enforced via SQLAlchemy 2.0 parameterized queries",
            "Per-project room isolation preventing cross-tenant WebSocket message leakage",
            "CORS policy strictly locked to configured frontend origins",
            "Automated fallback logic shielding users from third-party LLM outages",
        ]

        scaling_bottlenecks = [
            "Vector search latency as chunks exceed 100,000 items -> Mitigated with HNSW index m=16, ef_construction=64",
            "WebSocket connection exhaustion under heavy concurrency -> Mitigated with Redis Pub/Sub horizontal multiplexing",
            "LLM API rate limits during synchronous judge evaluations -> Mitigated with in-memory TTL caching and deterministic synthesizer",
        ]

        return SystemArchitectureBlueprint(
            project_title=title,
            architecture_pattern="Event-Driven Micro-Monolith with pgvector RAG & Multi-Agent Orchestration",
            executive_summary=(
                f"{title} employs a decoupled, asynchronous micro-monolith architecture optimized for sub-50ms user interactions "
                f"and robust AI workflows. By coupling FastAPI with PostgreSQL and native pgvector embeddings, the system eliminates "
                f"external vector database subscription costs while guaranteeing ACID transactions and real-time WebSocket synchronization."
            ),
            components=components,
            data_flows=data_flows,
            mermaid_diagram=mermaid_graph,
            mermaid_sequence=mermaid_sequence,
            security_isolation_notes=security_notes,
            scaling_bottlenecks_and_mitigations=scaling_bottlenecks,
        )
