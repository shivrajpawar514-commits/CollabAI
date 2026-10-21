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


class GeminiAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        self.stream_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent"

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

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self.base_url}?key={self.api_key}",
                    json=payload
                )
                resp.raise_for_status()
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
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
        # Check if fallback needed due to missing API key
        if not self.api_key:
            return self._heuristic_fallback(schema, prompt)

        schema_json = json.dumps(schema.model_json_schema())
        augmented_prompt = f"{prompt}\n\nYou MUST respond ONLY with valid JSON conforming to this schema:\n{schema_json}"

        payload = {
            "contents": [{"parts": [{"text": augmented_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json"
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{self.base_url}?key={self.api_key}",
                    json=payload
                )
                resp.raise_for_status()
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                return schema.model_validate_json(raw_text)
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
            # Stream words with slight delay to emulate natural LLM streaming
            words = copilot_resp.answer.split(" ")
            for i, word in enumerate(words):
                yield word + (" " if i < len(words) - 1 else "")
                await asyncio.sleep(0.015)
            return

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.stream_url}?alt=sse&key={self.api_key}",
                    json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str:
                                try:
                                    chunk = json.loads(data_str)
                                    text = chunk["candidates"][0]["content"]["parts"][0]["text"]
                                    yield text
                                except Exception:
                                    pass
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
