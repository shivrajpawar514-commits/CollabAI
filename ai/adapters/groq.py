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


class GroqAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        if not self.api_key:
            copilot_resp = mock_engine.generate_heuristic_copilot_response(prompt, "Student Project")
            return copilot_resp.answer

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(self.url, headers=headers, json=payload)
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
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
        if not self.api_key:
            return self._heuristic_fallback(schema, prompt)

        schema_json = json.dumps(schema.model_json_schema())
        messages = []
        sys_msg = (system_instruction or "") + f"\nYou MUST return JSON matching this schema:\n{schema_json}"
        messages.append({"role": "system", "content": sys_msg})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(self.url, headers=headers, json=payload)
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"]
                return schema.model_validate_json(content)
        except Exception:
            return self._heuristic_fallback(schema, prompt)

    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            copilot_resp = mock_engine.generate_heuristic_copilot_response(prompt, "Student Project")
            for word in copilot_resp.answer.split(" "):
                yield word + " "
                await asyncio.sleep(0.015)
            return

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                async with client.stream("POST", self.url, headers=headers, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: ") and line != "data: [DONE]":
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                yield delta
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
