import re
from typing import Type, TypeVar, List, Dict, Any
from pydantic import BaseModel

from ai.prompts.project_generator import ProjectProposal, RoleNeed, MilestonePlan
from ai.prompts.milestone_planner import MilestoneDecomposition, MilestoneItem, MilestoneTaskItem
from ai.prompts.task_decomposer import TaskBreakdown, SubTaskItem
from ai.prompts.copilot import CopilotResponse, ActionSuggestion

T = TypeVar("T", bound=BaseModel)


def extract_keywords(text: str) -> List[str]:
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    words = [w for w in cleaned.split() if len(w) > 3]
    return words


def generate_heuristic_proposal(prompt: str) -> ProjectProposal:
    text = prompt.lower()
    
    # Domain heuristics
    if any(k in text for k in ["agri", "crop", "farm", "plant", "soil"]):
        domain = "Agriculture & Smart Farming"
        title = "AgriVision: Edge AI Crop Disease Diagnosis & Yield Optimization"
        problem = "Smallholder farmers experience up to 40% crop losses due to delayed detection of leaf blight, pest infestations, and improper fertilizer scheduling."
        techs = ["PyTorch", "MobileNetV3", "FastAPI", "React Native", "PostgreSQL", "Edge TPU"]
        roles = [
            RoleNeed(role_name="Computer Vision Engineer", capacity=1, skills_required=["PyTorch", "OpenCV", "TensorFlow Lite"], responsibilities="Train lightweight leaf disease classification and bounding box segmentation models."),
            RoleNeed(role_name="Full-Stack Developer", capacity=1, skills_required=["FastAPI", "React", "TypeScript", "Tailwind"], responsibilities="Build farmer advisory dashboard, offline sync, and REST API."),
            RoleNeed(role_name="IoT / Hardware Specialist", capacity=1, skills_required=["ESP32", "MQTT", "Python"], responsibilities="Calibrate soil moisture, humidity sensors and edge inference nodes.")
        ]
        datasets = ["PlantVillage Dataset (54k images)", "USDA Soil Moisture Sensor Feeds", "Kaggle Rice Leaf Disease Dataset"]
    elif any(k in text for k in ["health", "med", "doctor", "patient", "heart", "cancer"]):
        domain = "Healthcare & MedTech"
        title = "PulseGuard: AI-Powered Remote Patient Triage & Vitals Monitoring"
        problem = "Understaffed rural clinics struggle with continuous patient vitals monitoring and early warning alerts for cardiac arrhythmias."
        techs = ["Python", "FastAPI", "PyTorch", "Next.js", "WebSockets", "TimescaleDB"]
        roles = [
            RoleNeed(role_name="Biomedical ML Engineer", capacity=1, skills_required=["PyTorch", "Signal Processing", "Scikit-Learn"], responsibilities="Develop ECG arrhythmia anomaly detection and vitals trend forecasting models."),
            RoleNeed(role_name="Cloud & Security Architect", capacity=1, skills_required=["FastAPI", "PostgreSQL", "Docker", "HIPAA Compliance"], responsibilities="Design end-to-end encrypted medical data pipelines and authenticated APIs."),
            RoleNeed(role_name="Frontend UI/UX Designer", capacity=1, skills_required=["Next.js", "Tailwind CSS", "Chart.js"], responsibilities="Create clinician telemetry dashboards with low-latency alerts.")
        ]
        datasets = ["PhysioNet MIT-BIH Arrhythmia Database", "MIMIC-IV Clinical Trials Subset"]
    elif any(k in text for k in ["crypto", "block", "web3", "chain", "dao"]):
        domain = "Web3 & Decentralized Systems"
        title = "VeriProof: Decentralized Academic Credential & Identity Verification"
        problem = "Credential forgery and slow background check verifications delay university admissions and graduate employment verification."
        techs = ["Solidity", "Hardhat", "Next.js", "IPFS", "FastAPI", "Ethers.js"]
        roles = [
            RoleNeed(role_name="Smart Contract Engineer", capacity=1, skills_required=["Solidity", "Hardhat", "OpenZeppelin"], responsibilities="Implement ERC-721 Soulbound credential minting and revocable authorization contracts."),
            RoleNeed(role_name="Frontend Web3 Integrator", capacity=1, skills_required=["Next.js", "Wagmi", "RainbowKit", "Tailwind"], responsibilities="Develop student wallet connection and university credential management portal."),
            RoleNeed(role_name="Backend Verification Specialist", capacity=1, skills_required=["Python", "FastAPI", "PostgreSQL"], responsibilities="Build cryptographic proof hashing services and indexing pipelines.")
        ]
        datasets = ["Ethereum Sepolia Testnet Records", "IPFS Pinata Metadata Stores"]
    else:
        domain = "AI & Collaborative Engineering"
        title = "NovaFlow: Autonomous Multi-Agent Workspace for Hackathons"
        problem = "Student teams struggle to coordinate complex multi-disciplinary software projects, balance task distribution, and track milestone blockers."
        techs = ["Next.js 14", "FastAPI", "PostgreSQL", "pgvector", "Redis", "LangGraph"]
        roles = [
            RoleNeed(role_name="Full-Stack Engineer", capacity=1, skills_required=["Next.js", "TypeScript", "Tailwind", "React Query"], responsibilities="Build reactive Kanban workflows and interactive collaborative canvas."),
            RoleNeed(role_name="Backend & Systems Developer", capacity=1, skills_required=["Python", "FastAPI", "SQLAlchemy", "WebSockets"], responsibilities="Implement real-time pub/sub, message persistence, and token-efficient APIs."),
            RoleNeed(role_name="AI / RAG Engineer", capacity=1, skills_required=["LangChain", "Embeddings", "pgvector", "Gemini API"], responsibilities="Build document chunking, semantic retrieval, and agentic task planner.")
        ]
        datasets = ["GitHub Open-Source Issue Repositories", "HuggingFace StackExchange Tech Discussions"]

    return ProjectProposal(
        title=title,
        problem_statement=problem,
        objectives=[
            "Design and implement scalable modular architecture using modern free open-source tools.",
            "Deploy functional machine learning and real-time collaborative prototypes with sub-second response times.",
            "Conduct end-to-end user evaluation with peer student teams and benchmark latency and accuracy."
        ],
        technologies=techs,
        roles_needed=roles,
        architecture="Three-tier decoupled architecture: Next.js 14 frontend communicating via REST and WebSockets with an async FastAPI backend, backed by PostgreSQL with pgvector for relational data and embeddings, and Redis for real-time pub/sub channels.",
        datasets=datasets,
        risks=[
            "Free-tier API rate limiting during high concurrency testing.",
            "Sparse initial training data requiring data augmentation and synthetic bootstrapping.",
            "Complex real-time state synchronization across concurrent collaborative users."
        ],
        metrics=[
            "Task completion rate and team onboarding velocity (>80% on-schedule).",
            "Model inference latency under 250ms on standard consumer hardware.",
            "Zero data loss with automated relational foreign key cascades and transactional rollbacks."
        ],
        timeline_weeks=[
            MilestonePlan(week_number=1, title="Phase 1: Research, Architecture & Monorepo Setup", deliverables=["Technical specification document", "Database schema definition", "Git repository and CI setup"]),
            MilestonePlan(week_number=2, title="Phase 2: Core Data Models & Authentication Engine", deliverables=["JWT authentication", "User profile wizard", "Initial API endpoints"]),
            MilestonePlan(week_number=3, title="Phase 3: Core AI Logic & Backend Pipeline", deliverables=["Model fine-tuning or prompt template integration", "Vector embeddings pipeline"]),
            MilestonePlan(week_number=4, title="Phase 4: Frontend Reactive Interface & Workspace", deliverables=["Responsive UI layouts", "Interactive Kanban and real-time state synchronization"]),
            MilestonePlan(week_number=5, title="Phase 5: End-to-End Testing & Integration", deliverables=["Integration test suite", "Performance and security audit"]),
            MilestonePlan(week_number=6, title="Phase 6: Final Deployment & Video Showcase", deliverables=["Cloud deployment", "Interactive demo video", "Comprehensive README documentation"])
        ]
    )


def generate_heuristic_milestones(project_title: str, description: str) -> MilestoneDecomposition:
    return MilestoneDecomposition(
        project_title=project_title or "CollabAI Student Project",
        overview=f"Automated 6-phase engineering milestone roadmap for '{project_title}'. Each phase delivers tangible working software.",
        total_weeks=8,
        milestones=[
            MilestoneItem(
                title="Phase 1: Architecture & Environment Setup",
                description="Establish repository structure, Docker environment, database schemas, and API scaffolding.",
                target_week=1,
                deliverables=["PostgreSQL schema migrations", "FastAPI foundation", "Next.js client boilerplate"],
                suggested_tasks=[
                    MilestoneTaskItem(title="Configure database models and async engine", description="Write SQLAlchemy models and configure connection pool.", priority="high", estimated_hours=8, recommended_skills=["Python", "SQLAlchemy", "PostgreSQL"]),
                    MilestoneTaskItem(title="Setup frontend layout and design system tokens", description="Define typography, color palette, and reusable button/input primitives.", priority="medium", estimated_hours=6, recommended_skills=["Next.js", "Tailwind CSS"])
                ]
            ),
            MilestoneItem(
                title="Phase 2: Core Backend Engine & Data Pipelines",
                description="Implement primary business logic, CRUD endpoints, and asynchronous workers.",
                target_week=3,
                deliverables=["RESTful API endpoints", "Data ingestion pipeline", "Unit test coverage"],
                suggested_tasks=[
                    MilestoneTaskItem(title="Build service layer and repository pattern", description="Encapsulate database queries with clean dependency injection.", priority="high", estimated_hours=10, recommended_skills=["FastAPI", "Python"]),
                    MilestoneTaskItem(title="Implement payload validation and exception handlers", description="Ensure proper HTTP status codes and detailed validation error schemas.", priority="medium", estimated_hours=4, recommended_skills=["Pydantic", "FastAPI"])
                ]
            ),
            MilestoneItem(
                title="Phase 3: AI/ML Model Integration & Inference",
                description="Connect machine learning pipeline, prompt templates, and vector similarity search.",
                target_week=5,
                deliverables=["Working inference pipeline", "pgvector similarity queries", "Fallback heuristic mechanisms"],
                suggested_tasks=[
                    MilestoneTaskItem(title="Integrate LLM adapters and structured output schemas", description="Connect swappable Gemini/Groq/Ollama client with Pydantic validation.", priority="urgent", estimated_hours=12, recommended_skills=["Python", "LLMs", "Prompt Engineering"]),
                    MilestoneTaskItem(title="Benchmarking latency and token efficiency", description="Evaluate prompt tokens, caching layers, and rate limit handling.", priority="medium", estimated_hours=6, recommended_skills=["Python", "Redis"])
                ]
            ),
            MilestoneItem(
                title="Phase 4: Interactive Client Workspace & Real-Time Sync",
                description="Deliver the responsive UI components, Kanban board, and WebSocket client.",
                target_week=6,
                deliverables=["Interactive Kanban board", "Real-time chat room", "Notification center"],
                suggested_tasks=[
                    MilestoneTaskItem(title="Implement drag-and-drop Kanban state manager", description="Wire up column moves with optimistic UI updates and backend sync.", priority="high", estimated_hours=10, recommended_skills=["React", "TypeScript", "TanStack Query"]),
                    MilestoneTaskItem(title="WebSocket live event listeners", description="Handle room join, live message push, and typing indicators.", priority="medium", estimated_hours=8, recommended_skills=["WebSockets", "JavaScript"])
                ]
            ),
            MilestoneItem(
                title="Phase 5: Polishing, Security & Deployment",
                description="Conduct security audits, optimize bundle size, write documentation, and deploy live.",
                target_week=8,
                deliverables=["Production deployment", "Comprehensive README with architecture diagrams", "Demo presentation slide deck"],
                suggested_tasks=[
                    MilestoneTaskItem(title="Run lighthouse performance & accessibility audit", description="Achieve >90 score across performance, accessibility, and SEO.", priority="medium", estimated_hours=6, recommended_skills=["Web Performance", "DevTools"]),
                    MilestoneTaskItem(title="Draft project showcase walkthrough and demo video", description="Record 3-minute video pitch highlighting the team's engineering contributions.", priority="high", estimated_hours=8, recommended_skills=["Technical Writing", "Presentation"])
                ]
            )
        ]
    )


def generate_heuristic_task_breakdown(task_title: str, task_description: str) -> TaskBreakdown:
    title_lower = task_title.lower()
    
    if any(k in title_lower for k in ["auth", "login", "signup", "jwt", "oauth"]):
        subtasks = [
            SubTaskItem(title="Design user credential schema and hashing utilities", description="Implement Argon2/PBKDF2 password hashing and verification helper functions.", priority="high", estimated_hours=4, required_skills=["Python", "Security"], suggested_role="Backend Developer"),
            SubTaskItem(title="Generate JWT access and refresh token handlers", description="Create encode/decode functions with expiration checks and secret key signing.", priority="high", estimated_hours=4, required_skills=["FastAPI", "JWT"], suggested_role="Backend Developer"),
            SubTaskItem(title="Build responsive login & registration modal UI", description="Implement form inputs, client-side validation, and error alert banners.", priority="medium", estimated_hours=5, required_skills=["React", "Tailwind CSS"], suggested_role="Frontend Developer"),
            SubTaskItem(title="Implement token storage and Axios/Fetch request interceptors", description="Store JWT in secure cookies or localStorage and attach Authorization Bearer headers.", priority="medium", estimated_hours=3, required_skills=["TypeScript", "Next.js"], suggested_role="Frontend Developer")
        ]
    elif any(k in title_lower for k in ["model", "ml", "train", "dataset", "ai"]):
        subtasks = [
            SubTaskItem(title="Data collection, cleaning & exploratory data analysis", description="Ingest raw data, filter outliers, remove duplicates, and normalize text/features.", priority="high", estimated_hours=8, required_skills=["Pandas", "Python"], suggested_role="ML Engineer"),
            SubTaskItem(title="Build baseline model pipeline and validation split", description="Construct cross-validation benchmark and log accuracy, precision, and recall.", priority="high", estimated_hours=6, required_skills=["PyTorch", "Scikit-Learn"], suggested_role="ML Engineer"),
            SubTaskItem(title="Export quantized model for lightweight API serving", description="Convert trained weights to ONNX or TorchScript for sub-100ms inference.", priority="medium", estimated_hours=5, required_skills=["ONNX", "Docker"], suggested_role="MLOps / Backend"),
            SubTaskItem(title="Wrap model inside asynchronous FastAPI prediction route", description="Define Pydantic input/output schemas with batching and error fallbacks.", priority="high", estimated_hours=4, required_skills=["FastAPI", "Pydantic"], suggested_role="Backend Developer")
        ]
    elif any(k in title_lower for k in ["ui", "frontend", "page", "component", "dashboard"]):
        subtasks = [
            SubTaskItem(title="Draft wireframes and component state specifications", description="Define required user states (loading, empty, populated, error).", priority="medium", estimated_hours=3, required_skills=["Figma", "UI/UX"], suggested_role="Frontend Developer"),
            SubTaskItem(title="Implement responsive layout with Tailwind CSS grid & flex", description="Ensure seamless adaptability across mobile, tablet, and widescreen monitors.", priority="medium", estimated_hours=5, required_skills=["Tailwind CSS", "Next.js"], suggested_role="Frontend Developer"),
            SubTaskItem(title="Connect TanStack Query hooks to backend endpoints", description="Add automated caching, background refetching, and optimistic mutations.", priority="high", estimated_hours=4, required_skills=["React Query", "TypeScript"], suggested_role="Frontend Developer"),
            SubTaskItem(title="Add accessibility (a11y) labels and micro-interactions", description="Incorporate focus rings, ARIA roles, and hover transition effects.", priority="low", estimated_hours=3, required_skills=["a11y", "CSS"], suggested_role="Frontend Developer")
        ]
    else:
        subtasks = [
            SubTaskItem(title=f"Research requirements & technical dependencies for {task_title[:30]}", description="Identify libraries, architecture patterns, and potential bottlenecks.", priority="medium", estimated_hours=3, required_skills=["Software Engineering"], suggested_role="Lead Architect"),
            SubTaskItem(title=f"Implement core logic and data structures for {task_title[:30]}", description="Develop the primary implementation with modular, reusable functions.", priority="high", estimated_hours=6, required_skills=["Full-Stack"], suggested_role="Developer"),
            SubTaskItem(title=f"Write automated unit and integration tests for {task_title[:30]}", description="Ensure test coverage for edge cases, invalid inputs, and happy paths.", priority="medium", estimated_hours=4, required_skills=["Testing", "Python/JS"], suggested_role="QA / Developer"),
            SubTaskItem(title=f"Review code, documentation, and merge into main branch", description="Perform peer review and update the relevant README section.", priority="low", estimated_hours=2, required_skills=["Git", "Documentation"], suggested_role="Lead Architect")
        ]

    total_hours = sum(s.estimated_hours for s in subtasks)
    return TaskBreakdown(
        original_task_title=task_title,
        analysis=f"The task '{task_title}' encompasses multiple engineering facets that are best tackled sequentially to avoid bottlenecking other teammates.",
        estimated_total_hours=total_hours,
        subtasks=subtasks,
        potential_risks=[
            "Unclear API contract between frontend and backend before implementation begins.",
            "Underestimating edge-case handling and asynchronous error states."
        ],
        duplicate_or_conflict_warnings=[
            "Ensure coordination with existing database models to avoid schema migration conflicts."
        ]
    )


def generate_heuristic_copilot_response(query: str, project_title: str) -> CopilotResponse:
    q = query.lower()
    
    if any(k in q for k in ["next", "priority", "what should i do", "start"]):
        answer = f"""### 🎯 Recommended Immediate Priorities for **{project_title}**

1. **Lock Down API Contracts:** Make sure your team has agreed on Pydantic schemas and TypeScript interfaces before coding features.
2. **Setup the Database Foundation:** Run migrations and verify table relationships in PostgreSQL.
3. **Assign Core Kanban Tasks:** Check the Backlog and move high-priority items into **To Do** or **In Progress** to avoid team idle time.
4. **Regular Sync:** Use the real-time project chat room to post quick daily updates.
"""
        actions = [
            ActionSuggestion(action_type="create_task", label="Draft API Schema Task", detail="Create task for API contract definition", payload={"title": "Draft API Schemas & Data Contracts", "priority": "high", "hours": 4}),
            ActionSuggestion(action_type="create_milestone", label="Plan Architecture Milestone", detail="Add architecture setup milestone", payload={"title": "Phase 1: Architecture Blueprint", "target_week": 1})
        ]
    elif any(k in q for k in ["tech", "stack", "database", "postgres", "fastapi", "react"]):
        answer = f"""### 🛠 Tech Stack Recommendations for **{project_title}**

- **Backend:** FastAPI (Python 3.11+) with async SQLAlchemy 2.0. This gives your team fast execution, automated OpenAPI documentation, and native Pydantic v2 validation.
- **Frontend:** Next.js 14 App Router with Tailwind CSS and TanStack Query for smart caching and fast SSR.
- **Database:** PostgreSQL with `pgvector` for semantic search and fast vector indexing.
- **Real-Time:** WebSockets managed by FastAPI with Redis pub/sub for scaling across team chat rooms.
"""
        actions = [
            ActionSuggestion(action_type="tech_tip", label="Check FastAPI Docs", detail="Open API Swagger UI at /api/v1/docs"),
            ActionSuggestion(action_type="create_task", label="Setup pgvector Indexing", detail="Create task for vector similarity index", payload={"title": "Setup pgvector IVFFlat / HNSW Index", "priority": "medium", "hours": 5})
        ]
    elif any(k in q for k in ["teammate", "team", "who", "member", "assign", "match"]):
        answer = f"""### 👥 Team Collaboration & Assignment Strategy

To maximize team output:
- **Pair Programming:** Pair frontend and backend teammates during API integration to eliminate communication lag.
- **Skill Alignment:** Assign ML/data engineering tasks to teammates comfortable with PyTorch/Pandas, while full-stack members handle the UI and routing.
- **Workload Balance:** Keep each student's active tasks to at most 2 in **In Progress** simultaneously.
"""
        actions = [
            ActionSuggestion(action_type="invite_teammate", label="Find Matching Teammates", detail="Open the AI Teammate Recommender tool")
        ]
    else:
        answer = f"""### 💡 Copilot Guidance for **{project_title}**

I am monitoring your project workspace context. Here are 3 tactical recommendations for your team:
- **Decompose Large Tasks:** Use the **Decompose with AI** button on any large Kanban card to split it into 3–5 bite-sized student subtasks.
- **Maintain Clear Milestones:** Keep your roadmap updated under the **Roadmap** tab so peer mentors and hackathon judges can track progress.
- **Leverage AI Code Generation:** Use structured schemas for your data contracts to ensure type safety between Python and TypeScript.
"""
        actions = [
            ActionSuggestion(action_type="advice", label="Explore AI Milestone Planner", detail="Generate full project roadmap"),
            ActionSuggestion(action_type="create_task", label="Add Project Documentation Task", detail="Create README & demo task", payload={"title": "Write Technical Architecture README", "priority": "medium", "hours": 3})
        ]

    return CopilotResponse(
        answer=answer,
        suggested_actions=actions,
        relevant_skills=["FastAPI", "Next.js", "PostgreSQL", "System Architecture", "Git"]
    )
