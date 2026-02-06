"""
Enhanced Retriever
Orchestrates the full retrieval pipeline with validation and optional reranking.

Strategies:
- fast: Vector search only (no validation, no reranking)
- validated: Vector search + LLM validation of results
- full: Vector search + validation + LLM reranking
"""

import time
import logging
from typing import Optional, Literal
from pydantic import BaseModel

from app.core.config import settings
from app.core.cache import search_cache, cached
from app.core.security import sanitizer, injection_detector
from app.services.vector_service import vector_service
from app.services.query_service import query_service, QueryConstraints as QSConstraints
from app.services.rag.validator import ResultValidator, ValidationSummary, QueryConstraints
from app.services.rag.reranker import LLMReranker

logger = logging.getLogger(__name__)


class RetrievalResult(BaseModel):
    """Result of enhanced retrieval."""
    results: list[dict]
    count: int
    query_understanding: Optional[dict] = None
    validation_summary: Optional[dict] = None
    strategy_used: str
    latency_ms: int
    cache_hit: bool = False


class EnhancedRetriever:
    """
    Orchestrates the full retrieval pipeline.

    Pipeline stages:
    1. Security check (injection detection, sanitization)
    2. Query understanding (extract constraints)
    3. Cache check
    4. Vector search (with extra candidates for validation buffer)
    5. LLM Validation (optional based on strategy)
    6. LLM Reranking (optional based on strategy)

    Usage:
        retriever = EnhancedRetriever()
        result = await retriever.retrieve(
            query="blue hoodie under $30",
            tenant_id="pullbear",
            top_k=5,
            strategy="validated",
        )
    """

    def __init__(self):
        self.validator = ResultValidator()
        self.reranker = LLMReranker()

    def _convert_constraints(self, qs_constraints: QSConstraints) -> QueryConstraints:
        """Convert QueryService constraints to validator constraints."""
        return QueryConstraints(
            budget_min=qs_constraints.budget_min,
            budget_max=qs_constraints.budget_max,
            category=qs_constraints.category,
            brand=qs_constraints.brand,
            color=qs_constraints.color,
            material=qs_constraints.material,
            style=qs_constraints.style,
            occasion=qs_constraints.occasion,
            gender=qs_constraints.gender,
        )

    def _generate_cache_key(
        self,
        query: str,
        tenant_id: str,
        top_k: int,
        strategy: str,
    ) -> str:
        """Generate a cache key for the retrieval."""
        import hashlib
        key_data = f"{tenant_id}:{strategy}:{top_k}:{query}"
        return f"retrieve:{hashlib.sha256(key_data.encode()).hexdigest()[:32]}"

    async def retrieve(
        self,
        query: str,
        tenant_id: str,
        top_k: int = 10,
        strategy: Optional[Literal["fast", "validated", "full"]] = None,
        use_cache: bool = True,
        use_query_understanding: bool = True,
    ) -> RetrievalResult:
        """
        Execute the full retrieval pipeline.

        Args:
            query: User's search query
            tenant_id: Tenant identifier for filtering
            top_k: Number of results to return
            strategy: Override the default strategy from config
            use_cache: Whether to check/store in cache
            use_query_understanding: Whether to parse query constraints

        Returns:
            RetrievalResult with results, metadata, and timing
        """
        start_time = time.time()

        # Use configured strategy if not overridden
        strategy = strategy or settings.RAG_STRATEGY

        # Step 1: Check cache
        cache_key = self._generate_cache_key(query, tenant_id, top_k, strategy)
        if use_cache and settings.CACHE_ENABLED:
            cached_result = await search_cache.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                cached_result["cache_hit"] = True
                cached_result["latency_ms"] = int((time.time() - start_time) * 1000)
                return RetrievalResult(**cached_result)

        # Step 2: Query understanding
        constraints_dict = None
        embedding_query = query
        qs_constraints = None

        if use_query_understanding:
            query_result = query_service.understand(query)
            constraints_dict = query_result.constraints.to_dict()
            embedding_query = query_result.embedding_query
            qs_constraints = query_result.constraints

        # Step 3: Vector search
        # Get extra candidates for validation/reranking buffer
        candidates_multiplier = settings.RETRIEVAL_CANDIDATES_MULTIPLIER if strategy != "fast" else 1
        search_top_k = top_k * candidates_multiplier

        raw_results = vector_service.search(
            query=embedding_query,
            tenant_id=tenant_id,
            top_k=search_top_k,
        )

        # Step 4: Apply strategy-specific processing
        validation_summary = None

        if strategy == "fast":
            # Fast strategy: just return vector search results
            # Apply basic price filter if constraints present
            if qs_constraints and (qs_constraints.budget_max or qs_constraints.budget_min):
                filtered = []
                for r in raw_results:
                    price = r.get("price", 0)
                    if qs_constraints.budget_max and price > qs_constraints.budget_max:
                        continue
                    if qs_constraints.budget_min and price < qs_constraints.budget_min:
                        continue
                    filtered.append(r)
                raw_results = filtered

            final_results = raw_results[:top_k]

        elif strategy == "validated":
            # Validated strategy: vector search + LLM validation
            if qs_constraints:
                validator_constraints = self._convert_constraints(qs_constraints)
                validated_results, val_summary = await self.validator.validate(
                    raw_results,
                    validator_constraints,
                    use_llm=settings.VALIDATION_ENABLED,
                )
                final_results = validated_results[:top_k]
                validation_summary = val_summary.model_dump()
            else:
                final_results = raw_results[:top_k]

        elif strategy == "full":
            # Full strategy: vector search + validation + reranking
            if qs_constraints:
                validator_constraints = self._convert_constraints(qs_constraints)
                validated_results, val_summary = await self.validator.validate(
                    raw_results,
                    validator_constraints,
                    use_llm=settings.VALIDATION_ENABLED,
                )
                validation_summary = val_summary.model_dump()
            else:
                validated_results = raw_results

            # Rerank
            if settings.RERANKING_ENABLED and len(validated_results) > 1:
                final_results = await self.reranker.rerank(
                    query,
                    validated_results,
                    top_k=top_k,
                )
            else:
                final_results = validated_results[:top_k]

        else:
            # Unknown strategy, fall back to fast
            logger.warning(f"Unknown strategy: {strategy}, falling back to fast")
            final_results = raw_results[:top_k]

        latency_ms = int((time.time() - start_time) * 1000)

        result_data = {
            "results": final_results,
            "count": len(final_results),
            "query_understanding": constraints_dict,
            "validation_summary": validation_summary,
            "strategy_used": strategy,
            "latency_ms": latency_ms,
            "cache_hit": False,
        }

        # Step 5: Cache the result
        if use_cache and settings.CACHE_ENABLED:
            await search_cache.set(
                cache_key,
                result_data,
                settings.CACHE_TTL_SEARCH,
            )

        return RetrievalResult(**result_data)


# Singleton instance
enhanced_retriever = EnhancedRetriever()
