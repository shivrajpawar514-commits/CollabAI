import json
import asyncio
from typing import Type, TypeVar, Optional, AsyncGenerator
import httpx
from pydantic import BaseModel

from ai.adapters.base import BaseLLMAdapter
from ai.prompts.project_generator import ProjectProposal
from ai.prompts.milestone_planner import MilestoneDecomposition
from ai.prompts.task_decomposer import TaskBreakdown
from ai.prompts.copilot import CopilotResponse
import ai.mock_engine as mock_engine

T = TypeVar("T", bound=BaseModel)


class OllamaAdapter(BaseLLMAdapter):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.generate_url = f"{self.base_url}/api/generate"

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_instruction or "",
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(self.generate_url, json=payload)
                resp.raise_for_status()
                return resp.json()["response"]
        except Exception:
            copilot_resp = mock_engine.generate_heuristic_copilot_response(prompt, "Student Project")
            return copilot_resp.answer

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2
    ) -> T:
        schema_json = json.dumps(schema.model_json_schema())
        augmented_prompt = f"{prompt}\n\nRespond ONLY in valid JSON matching this schema:\n{schema_json}"

        payload = {
            "model": self.model,
            "prompt": augmented_prompt,
            "system": system_instruction or "",
            "format": "json",
            "stream": False,
            "options": {"temperature": temperature}
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(self.generate_url, json=payload)
                resp.raise_for_status()
                raw_json = resp.json()["response"]
                return schema.model_validate_json(raw_json)
        except Exception:
            return self._heuristic_fallback(schema, prompt)

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_instruction or "",
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", self.generate_url, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line:
                            chunk = json.loads(line)
                            yield chunk.get("response", "")
        except Exception:
            copilot_resp = mock_engine.generate_heuristic_copilot_response(prompt, "Student Project")
            for word in copilot_resp.answer.split(" "):
                yield word + " "
                await asyncio.sleep(0.01)

    def _heuristic_fallback(self, schema: Type[T], prompt: str) -> T:
        if schema == ProjectProposal:
            return mock_engine.generate_heuristic_proposal(prompt)  # type: ignore
        elif schema == MilestoneDecomposition:
            return mock_engine.generate_heuristic_milestones(prompt, prompt)  # type: ignore
        elif schema == TaskBreakdown:
            return mock_engine.generate_heuristic_task_breakdown(prompt, prompt)  # type: ignore
        elif schema == CopilotResponse:
            return mock_engine.generate_heuristic_copilot_response(prompt, "Student Project")  # type: ignore
        else:
            dummy_dict = {f: "Mock value" for f in schema.model_fields.keys()}
            return schema.model_validate(dummy_dict)
