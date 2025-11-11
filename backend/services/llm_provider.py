"""
LLM Provider abstraction layer supporting multiple providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import anthropic
import openai
from utils.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a completion from the LLM."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation."""

    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.LLM_MODEL

    async def complete(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a completion using Anthropic Claude."""
        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }

            if system:
                kwargs["system"] = system

            response = self.client.messages.create(**kwargs)

            return {
                "content": response.content[0].text,
                "model": response.model,
                "token_usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"

    async def complete(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a completion using OpenAI GPT."""
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "token_usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                }
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise


def get_llm_provider() -> LLMProvider:
    """Factory function to get the configured LLM provider."""
    provider = settings.LLM_PROVIDER.lower()

    if provider == "anthropic":
        return AnthropicProvider()
    elif provider == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
