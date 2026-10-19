import logging
from typing import Type, TypeVar, Optional, Dict
from pydantic import BaseModel

from ai.adapters.base import BaseLLMAdapter
from ai.adapters.gemini import GeminiAdapter
from ai.adapters.groq import GroqAdapter
from ai.adapters.ollama import OllamaAdapter
from app.core.config import settings

logger = logging.getLogger("collabai.ai")
T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    Unified LLM Client abstraction.
    Supports seamless switching between free-tier providers:
    - Google Gemini Flash (Free Tier)
    - Groq (Free Tier fast Llama models)
    - Ollama (Local free & unlimited)
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider_name = (provider or settings.DEFAULT_LLM_PROVIDER).lower()
        self.adapter = self._resolve_adapter(self.provider_name)

    def _resolve_adapter(self, provider: str) -> BaseLLMAdapter:
        if provider == "groq":
            return GroqAdapter(api_key=settings.GROQ_API_KEY or "")
        elif provider == "ollama":
            return OllamaAdapter(base_url=settings.OLLAMA_BASE_URL)
        elif provider == "gemini":
            return GeminiAdapter(api_key=settings.GEMINI_API_KEY or "")
        else:
            logger.warning(f"Unknown provider '{provider}', defaulting to Gemini.")
            return GeminiAdapter(api_key=settings.GEMINI_API_KEY or "")

    def switch_provider(self, new_provider: str):
        """Allows dynamic switching when one provider's free quota is exhausted."""
        logger.info(f"Switching LLM provider from {self.provider_name} to {new_provider}")
        self.provider_name = new_provider.lower()
        self.adapter = self._resolve_adapter(self.provider_name)

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        try:
            return await self.adapter.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            logger.error(f"Error in LLM generate with {self.provider_name}: {e}")
            # Automatic fallback to Ollama if configured or retry
            raise

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        retries: int = 1
    ) -> T:
        """
        Generate structured output adhering to a Pydantic schema with automatic retry on validation failure.
        """
        attempts = 0
        last_error = None
        while attempts <= retries:
            try:
                return await self.adapter.generate_structured(
                    prompt=prompt,
                    schema=schema,
                    system_instruction=system_instruction,
                    temperature=temperature
                )
            except Exception as e:
                attempts += 1
                last_error = e
                logger.warning(f"Structured output validation failed (attempt {attempts}/{retries+1}): {e}")
                prompt += f"\n\nPrevious attempt failed with error: {str(e)}. Please fix the JSON formatting to match the schema strictly."

        raise RuntimeError(f"Failed to generate valid structured response after {retries+1} attempts: {last_error}")
