"""
LLM Reranker
Reranks search results using LLM for better semantic relevance.

This is an optional enhancement that trades latency for relevance.
Enable with RERANKING_ENABLED=true in config.
"""

import json
import logging
from typing import Optional
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


RERANK_PROMPT = """You are a product ranking assistant. Reorder these products by how well they match the user's search query.

User's search query: "{query}"

Products to rank:
{products}

Rank these products from MOST relevant to LEAST relevant for the user's query.
Consider:
- How well the product matches the intent of the query
- Relevance of product name and description to the query
- Category match

Respond with a JSON array of product IDs in order from most to least relevant.
Example: ["product_id_1", "product_id_2", "product_id_3"]

Return ONLY the JSON array, no other text."""


class LLMReranker:
    """
    Reranks search results using LLM for better semantic relevance.

    The reranker takes initial vector search results and reorders them
    based on deeper semantic understanding of the query intent.

    Usage:
        reranker = LLMReranker()
        reranked = await reranker.rerank(query, results, top_k=5)
    """

    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def _format_products_for_prompt(self, products: list[dict]) -> str:
        """Format products for the reranking prompt."""
        formatted = []
        for p in products:
            formatted.append(
                f"- ID: {p.get('product_id', 'unknown')}\n"
                f"  Name: {p.get('name', 'Unknown')}\n"
                f"  Description: {p.get('description', 'N/A')[:150]}\n"
                f"  Price: ${p.get('price', 0)}\n"
                f"  Categories: {', '.join(p.get('categories', []))}"
            )
        return "\n\n".join(formatted)

    async def rerank(
        self,
        query: str,
        results: list[dict],
        top_k: Optional[int] = None,
    ) -> list[dict]:
        """
        Rerank search results using LLM.

        Args:
            query: Original search query
            results: List of product dictionaries from vector search
            top_k: Number of results to return (defaults to input length)

        Returns:
            Reranked list of products
        """
        if not results:
            return []

        if len(results) <= 1:
            return results

        top_k = top_k or len(results)

        try:
            prompt = RERANK_PROMPT.format(
                query=query,
                products=self._format_products_for_prompt(results),
            )

            response = await self.openai.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500,
            )

            response_text = response.choices[0].message.content.strip()

            # Parse JSON response
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            ranked_ids = json.loads(response_text)

            # Create lookup for original results
            results_by_id = {p.get("product_id"): p for p in results}

            # Build reranked list
            reranked = []
            for product_id in ranked_ids:
                if product_id in results_by_id:
                    reranked.append(results_by_id[product_id])

            # Add any products that weren't in the ranking (shouldn't happen)
            for p in results:
                if p not in reranked:
                    reranked.append(p)

            return reranked[:top_k]

        except Exception as e:
            logger.error(f"LLM reranking failed: {e}")
            # On error, return original results
            return results[:top_k] if top_k else results


# Singleton instance
llm_reranker = LLMReranker()
