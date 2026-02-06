"""
Enhanced RAG (Retrieval-Augmented Generation) Module

This module provides an improved RAG pipeline with:
- Query understanding and constraint extraction
- LLM-based result validation
- Optional LLM reranking for better relevance
- Image-to-query conversion for visual search
- Caching for performance

Components:
- retriever: Orchestrates the full retrieval pipeline
- validator: LLM validates results against user constraints
- reranker: Optional LLM-based reranking
- image_search: Image-to-query conversion using GPT-4V
"""

from app.services.rag.validator import ResultValidator, ValidationSummary
from app.services.rag.reranker import LLMReranker
from app.services.rag.retriever import EnhancedRetriever, RetrievalResult
from app.services.rag.image_search import ImageSearchService, ImageAnalysis

__all__ = [
    "EnhancedRetriever",
    "RetrievalResult",
    "ResultValidator",
    "ValidationSummary",
    "LLMReranker",
    "ImageSearchService",
    "ImageAnalysis",
]
