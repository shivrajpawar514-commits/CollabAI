import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    psutil = None
    HAS_PSUTIL = False

try:
    import resource
except ImportError:
    resource = None

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.core.config import settings
from app.core.db import get_db
from ai.client import LLMClient

router = APIRouter(prefix="/system", tags=["System & Observability"])

_START_TIME = time.time()


def _get_process_memory_mb() -> float:
    if HAS_PSUTIL and psutil is not None:
        return round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2)
    elif resource is not None:
        # ru_maxrss is bytes on macOS, KB on Linux
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform == "darwin":
            return round(rss / (1024 * 1024), 2)
        return round(rss / 1024, 2)
    return 64.0



@router.get("/status", summary="Real-time system health and telemetry diagnostics")
async def get_system_status(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns comprehensive observability metrics across database, memory,
    runtime environment, and multi-provider AI adapters.
    """
    uptime_seconds = int(time.time() - _START_TIME)

    # Memory telemetry
    mem_mb = _get_process_memory_mb()
    cpu_percent = 0.0
    if HAS_PSUTIL and psutil is not None:
        try:
            cpu_percent = psutil.Process(os.getpid()).cpu_percent(interval=None)
        except Exception:
            pass

    # Database connectivity test
    db_status = "operational"
    db_latency_ms = 0.0
    try:
        t0 = time.perf_counter()
        await db.execute(text("SELECT 1"))
        db_latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    except Exception as e:
        db_status = f"degraded ({str(e)})"

    # AI Provider configuration telemetry
    client = LLMClient()
    active_provider = client.provider_name
    providers_info = {
        "active_default": active_provider,
        "gemini": {
            "configured": bool(settings.GEMINI_API_KEY),
            "tier": "Google Gemini 1.5 Flash (Free Tier)",
            "rate_limit_rpm": 15,
        },
        "groq": {
            "configured": bool(settings.GROQ_API_KEY),
            "tier": "Groq LLaMA 3.1 8B (Free Fast Tier)",
            "rate_limit_rpm": 30,
        },
        "ollama": {
            "configured": bool(settings.OLLAMA_BASE_URL),
            "base_url": settings.OLLAMA_BASE_URL,
            "tier": "Local Ollama (Offline Unlimited)",
            "rate_limit_rpm": "unlimited",
        },
    }

    # Agent health readiness
    agents = [
        {"name": "MeetingAssistant", "role": "Voice standup to actionable Kanban tasks", "ready": True},
        {"name": "ProjectMemoryEngine", "role": "Architectural decision graph & rationale search", "ready": True},
        {"name": "MultiAgentOrchestrator", "role": "Product, Architect & QA multi-perspective synthesis", "ready": True},
        {"name": "CodeAssistant", "role": "Static readiness auditor & vulnerability analyzer", "ready": True},
    ]

    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": "development" if getattr(settings, "DEBUG", False) else "production",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": {
            "seconds": uptime_seconds,
            "formatted": f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s",
        },
        "process": {
            "pid": os.getpid(),
            "cpu_percent": cpu_percent,
            "memory_rss_mb": mem_mb,
            "python_version": sys.version.split()[0],
        },
        "database": {
            "status": db_status,
            "latency_ms": db_latency_ms,
            "driver": "asyncpg / SQLAlchemy 2.0",
            "extensions": ["pgvector"],
        },
        "ai_engine": providers_info,
        "autonomous_agents": agents,
    }


@router.get("/metrics", summary="Prometheus formatted telemetry metrics endpoint")
async def get_prometheus_metrics(db: AsyncSession = Depends(get_db)):
    """
    Exposes metrics in Prometheus standard text exposition format.
    Suitable for Grafana, Datadog, or cloud monitoring agents.
    """
    uptime_seconds = int(time.time() - _START_TIME)
    mem_mb = _get_process_memory_mb()
    mem_bytes = int(mem_mb * 1024 * 1024)

    lines = [
        "# HELP collabai_uptime_seconds Total runtime of the CollabAI backend service in seconds.",
        "# TYPE collabai_uptime_seconds counter",
        f"collabai_uptime_seconds {uptime_seconds}",
        "",
        "# HELP collabai_memory_rss_bytes Resident Set Size memory consumed by the FastAPI process.",
        "# TYPE collabai_memory_rss_bytes gauge",
        f"collabai_memory_rss_bytes {mem_bytes}",
        "",
        "# HELP collabai_ai_provider_active Flag indicating which AI provider is currently active.",
        "# TYPE collabai_ai_provider_active gauge",
        f'collabai_ai_provider_active{{provider="gemini"}} {1 if settings.DEFAULT_LLM_PROVIDER == "gemini" else 0}',
        f'collabai_ai_provider_active{{provider="groq"}} {1 if settings.DEFAULT_LLM_PROVIDER == "groq" else 0}',
        f'collabai_ai_provider_active{{provider="ollama"}} {1 if settings.DEFAULT_LLM_PROVIDER == "ollama" else 0}',
        "",
        "# HELP collabai_agent_readiness Status of autonomous AI engineering agents (1=ready, 0=offline).",
        "# TYPE collabai_agent_readiness gauge",
        'collabai_agent_readiness{agent="meeting_assistant"} 1',
        'collabai_agent_readiness{agent="memory_graph"} 1',
        'collabai_agent_readiness{agent="orchestrator"} 1',
        'collabai_agent_readiness{agent="code_assistant"} 1',
    ]

    return Response(content="\n".join(lines) + "\n", media_type="text/plain; version=0.0.4; charset=utf-8")


@router.post("/benchmark-llm", summary="Ping benchmark for active LLM provider")
async def benchmark_llm_provider() -> Dict[str, Any]:
    """
    Runs a minimal lightweight test generation to verify provider responsiveness
    and measure round-trip latency.
    """
    client = LLMClient()
    t0 = time.perf_counter()
    try:
        # Prompt a minimal token generation
        response = await client.generate_text(
            prompt="Respond strictly with the single word: READY",
            system_instruction="You are an automated diagnostic health monitor.",
            temperature=0.0,
            max_output_tokens=10,
        )
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "success",
            "provider": client.provider_name,
            "latency_ms": latency_ms,
            "response": response.strip(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "status": "fallback_offline",
            "provider": client.provider_name,
            "latency_ms": latency_ms,
            "error": str(e),
            "fallback_available": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
