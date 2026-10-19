import json
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel

from ai.adapters.base import BaseLLMAdapter

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
            return "[Groq mock]: API key not configured. Set GROQ_API_KEY in .env."

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

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2
    ) -> T:
        schema_json = json.dumps(schema.model_json_schema())
        messages = []
        sys_msg = (system_instruction or "") + f"\nYou MUST return JSON matching this schema:\n{schema_json}"
        messages.append({"role": "system", "content": sys_msg})
        messages.append({"role": "user", "content": prompt})

        if not self.api_key:
            dummy_dict = {f: "Mock value" for f in schema.model_fields.keys()}
            return schema.model_validate(dummy_dict)

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

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.url, headers=headers, json=payload)
            resp.raise_for_status()
            raw_text = resp.json()["choices"][0]["message"]["content"]
            return schema.model_validate_json(raw_text)
