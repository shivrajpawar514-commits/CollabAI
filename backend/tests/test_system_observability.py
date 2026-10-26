import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.api.v1.system import get_system_status, get_prometheus_metrics, benchmark_llm_provider
from app.core.config import settings


class MockAsyncSession:
    async def execute(self, query):
        return 1


async def test_system_observability():
    print("=== Testing System Observability Endpoints ===")
    mock_db = MockAsyncSession()

    # 1. Test /system/status
    print("\n1. Testing get_system_status...")
    status_data = await get_system_status(db=mock_db)
    assert status_data["service"] == settings.PROJECT_NAME
    assert "version" in status_data
    assert "uptime" in status_data
    assert "process" in status_data
    assert "database" in status_data
    assert "ai_engine" in status_data
    assert len(status_data["autonomous_agents"]) == 4
    print(f"✓ System status valid. Uptime: {status_data['uptime']['seconds']}s | Memory: {status_data['process']['memory_rss_mb']}MB")
    print(f"  AI Providers configured: {list(status_data['ai_engine'].keys())}")

    # 2. Test /system/metrics (Prometheus format)
    print("\n2. Testing get_prometheus_metrics...")
    metrics_response = await get_prometheus_metrics(db=mock_db)
    content = metrics_response.body.decode("utf-8")
    assert "collabai_uptime_seconds" in content
    assert "collabai_memory_rss_bytes" in content
    assert "collabai_agent_readiness" in content
    assert metrics_response.media_type.startswith("text/plain")
    print("✓ Prometheus exposition text metrics valid:")
    for line in content.strip().splitlines()[:6]:
        print(f"  {line}")

    # 3. Test /system/benchmark-llm
    print("\n3. Testing benchmark_llm_provider...")
    benchmark_res = await benchmark_llm_provider()
    assert "status" in benchmark_res
    assert "latency_ms" in benchmark_res
    assert "provider" in benchmark_res
    print(f"✓ LLM Benchmark result: {benchmark_res['status']} | Provider: {benchmark_res['provider']} | Latency: {benchmark_res['latency_ms']}ms")

    print("\n=== ALL SYSTEM OBSERVABILITY TESTS PASSED! ===")


if __name__ == "__main__":
    asyncio.run(test_system_observability())
