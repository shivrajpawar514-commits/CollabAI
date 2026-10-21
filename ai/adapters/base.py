from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Any, Dict, AsyncGenerator
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMAdapter(ABC):
    """Abstract interface for swappable free-tier LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        """Generate freeform plain text response."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.2
    ) -> T:
        """Generate guaranteed structured JSON response validated against Pydantic schema."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> AsyncGenerator[str, None]:
        """Generate streaming token chunks."""
        pass
