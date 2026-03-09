"""LLM module — unified interface for local and cloud language models."""

from app.llm.models import LLMConfig, LLMProvider, LLMRequest, LLMResponse, LLMUsage
from app.llm.pipeline import (
    PipelineFullResult,
    PipelineSummaryResult,
    PipelineTranslationResult,
    run_full_pipeline,
    run_summary_pipeline,
    run_translation_pipeline,
)
from app.llm.service import LLMService, get_llm_service
from app.llm.summarizer import summarize_article, summarize_batch, validate_summary
from app.llm.translator import translate_article, translate_batch, validate_translation

__all__ = [
    "LLMConfig",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "LLMService",
    "LLMUsage",
    "PipelineFullResult",
    "PipelineSummaryResult",
    "PipelineTranslationResult",
    "get_llm_service",
    "run_full_pipeline",
    "run_summary_pipeline",
    "run_translation_pipeline",
    "summarize_article",
    "summarize_batch",
    "translate_article",
    "translate_batch",
    "validate_summary",
    "validate_translation",
]
