import json
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel

from ai.adapters.base import BaseLLMAdapter

T = TypeVar("T", bound=BaseModel)


class GeminiAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        if not self.api_key:
            return "[Gemini mock]: API key not configured. Set GEMINI_API_KEY in .env."

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}?key={self.api_key}",
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2
    ) -> T:
        schema_json = json.dumps(schema.model_json_schema())
        augmented_prompt = f"{prompt}\n\nYou MUST respond ONLY with valid JSON conforming to this schema:\n{schema_json}"

        if not self.api_key:
            # Fallback mock for testing when API key is unset
            dummy_dict = {f: "Mock value" for f in schema.model_fields.keys()}
            return schema.model_validate(dummy_dict)

        payload = {
            "contents": [{"parts": [{"text": augmented_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json"
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}?key={self.api_key}",
                json=payload
            )
            resp.raise_for_status()
            raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return schema.model_validate_json(raw_text)
