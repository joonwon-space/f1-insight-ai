"""LLM module — unified interface for local and cloud language models."""

from app.llm.models import LLMConfig, LLMProvider, LLMRequest, LLMResponse, LLMUsage
from app.llm.pipeline import (
    PipelineFullResult,
    PipelineSummaryResult,
    PipelineTaggingResult,
    PipelineTranslationResult,
    run_full_pipeline,
    run_summary_pipeline,
    run_tagging_pipeline,
    run_translation_pipeline,
)
from app.llm.service import LLMService, get_llm_service
from app.llm.summarizer import summarize_article, summarize_batch, validate_summary
from app.llm.tagger import TagResult, auto_tag_article, tag_batch
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
    "PipelineTaggingResult",
    "PipelineTranslationResult",
    "TagResult",
    "get_llm_service",
    "auto_tag_article",
    "run_full_pipeline",
    "run_summary_pipeline",
    "run_tagging_pipeline",
    "run_translation_pipeline",
    "tag_batch",
    "summarize_article",
    "summarize_batch",
    "translate_article",
    "translate_batch",
    "validate_summary",
    "validate_translation",
]
