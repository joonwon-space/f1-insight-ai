"""Unified LLM service with provider abstraction and auto-fallback."""

from __future__ import annotations

import logging

from app.core.config import settings
from app.llm.models import LLMConfig, LLMProvider, LLMResponse
from app.llm.ollama_client import OllamaClient
from app.llm.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class LLMService:
    """High-level LLM service that abstracts over multiple providers.

    Provider priority (auto-fallback):
      1. Ollama  (local, free)
      2. OpenAI  (cloud, requires API key)
      3. Anthropic (cloud, requires API key — uses OpenAI-compatible wrapper)
    """

    def __init__(self) -> None:
        self._clients: dict[LLMProvider, OllamaClient | OpenAIClient] = {}
        self._active_provider: LLMProvider = LLMProvider(settings.llm_provider)
        self._init_clients()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_clients(self) -> None:
        """Create client instances for every configured provider."""
        # Ollama — always configured (local service)
        self._clients[LLMProvider.OLLAMA] = OllamaClient(
            LLMConfig(
                provider=LLMProvider.OLLAMA,
                model_name=settings.llm_model,
                base_url=settings.ollama_base_url,
            )
        )

        # OpenAI — only when API key is present
        if settings.openai_api_key:
            self._clients[LLMProvider.OPENAI] = OpenAIClient(
                LLMConfig(
                    provider=LLMProvider.OPENAI,
                    model_name="gpt-4o-mini",
                    base_url="https://api.openai.com",
                    api_key=settings.openai_api_key,
                )
            )

        # Anthropic — via OpenAI-compatible proxy (e.g. LiteLLM)
        if settings.anthropic_api_key:
            self._clients[LLMProvider.ANTHROPIC] = OpenAIClient(
                LLMConfig(
                    provider=LLMProvider.ANTHROPIC,
                    model_name="claude-sonnet-4-20250514",
                    base_url="https://api.anthropic.com",
                    api_key=settings.anthropic_api_key,
                )
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_active_provider(self) -> LLMProvider:
        """Return the currently configured active provider."""
        return self._active_provider

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Generate text using the active provider with auto-fallback.

        Tries the active provider first. If it fails, falls back through the
        remaining configured providers in priority order.
        """
        temp = temperature if temperature is not None else settings.llm_temperature
        tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens

        # Build ordered list: active provider first, then others
        ordered = [self._active_provider] + [
            p for p in LLMProvider if p != self._active_provider and p in self._clients
        ]

        last_error: Exception | None = None
        for provider in ordered:
            client = self._clients.get(provider)
            if client is None:
                continue
            try:
                response = await client.generate(
                    prompt=prompt,
                    model=model,
                    temperature=temp,
                    max_tokens=tokens,
                )
                if provider != self._active_provider:
                    logger.info("Fell back to provider %s", provider.value)
                return response
            except Exception as exc:
                logger.warning("Provider %s failed: %s", provider.value, exc)
                last_error = exc

        msg = "All LLM providers failed"
        raise RuntimeError(msg) from last_error

    async def health_check(self) -> dict[str, object]:
        """Check connectivity for every configured provider."""
        results: dict[str, object] = {}

        for provider, client in self._clients.items():
            if isinstance(client, OllamaClient):
                healthy = await client.health_check()
                models = await client.list_models() if healthy else []
                results[provider.value] = {
                    "healthy": healthy,
                    "models": models,
                }
            else:
                # OpenAI-compatible clients — lightweight check
                try:
                    await client.generate(
                        prompt="ping",
                        max_tokens=1,
                        temperature=0.0,
                    )
                    results[provider.value] = {"healthy": True}
                except Exception as exc:
                    logger.debug("Health check failed for %s: %s", provider.value, exc)
                    results[provider.value] = {"healthy": False, "error": str(exc)}

        return {
            "active_provider": self._active_provider.value,
            "providers": results,
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """Return the module-level LLMService singleton (lazy init)."""
    global _llm_service  # noqa: PLW0603
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
