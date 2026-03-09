"""LLM module — unified interface for local and cloud language models."""

from app.llm.models import LLMConfig, LLMProvider, LLMRequest, LLMResponse, LLMUsage
from app.llm.pipeline import PipelineSummaryResult, run_summary_pipeline
from app.llm.service import LLMService, get_llm_service
from app.llm.summarizer import summarize_article, summarize_batch, validate_summary

__all__ = [
    "LLMConfig",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "LLMService",
    "LLMUsage",
    "PipelineSummaryResult",
    "get_llm_service",
    "run_summary_pipeline",
    "summarize_article",
    "summarize_batch",
    "validate_summary",
]
