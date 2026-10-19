import json
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel

from ai.adapters.base import BaseLLMAdapter

T = TypeVar("T", bound=BaseModel)


class OllamaAdapter(BaseLLMAdapter):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

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
            "options": {"temperature": temperature}
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                resp.raise_for_status()
                return resp.json()["response"]
        except Exception as e:
            return f"[Ollama local error]: Could not reach local Ollama at {self.base_url}. Ensure ollama is running (`ollama run {self.model}`). Detail: {e}"

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2
    ) -> T:
        schema_json = json.dumps(schema.model_json_schema())
        augmented_prompt = f"{prompt}\n\nYou MUST respond ONLY with valid JSON conforming to this schema:\n{schema_json}"
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
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                resp.raise_for_status()
                raw_text = resp.json()["response"]
                return schema.model_validate_json(raw_text)
        except Exception:
            # Fallback mock if Ollama not running
            dummy_dict = {f: "Mock value" for f in schema.model_fields.keys()}
            return schema.model_validate(dummy_dict)
