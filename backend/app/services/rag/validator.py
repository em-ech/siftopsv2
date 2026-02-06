"""
Result Validator
LLM validates that search results match user constraints.

The validator ensures that:
1. Price constraints are strictly enforced (hard filter)
2. Semantic constraints (color, style, occasion) are validated by LLM
"""

import json
import logging
from typing import Optional
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class ValidationSummary(BaseModel):
    """Summary of validation results."""
    total_candidates: int
    passed_validation: int
    failed_validation: int
    validation_details: list[dict]  # Per-product validation reasons


class QueryConstraints(BaseModel):
    """Constraints extracted from user query."""
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    style: Optional[str] = None
    occasion: Optional[str] = None
    gender: Optional[str] = None

    def has_semantic_constraints(self) -> bool:
        """Check if there are constraints that need LLM validation."""
        return any([
            self.color,
            self.material,
            self.style,
            self.occasion,
            self.category,
        ])

    def has_price_constraints(self) -> bool:
        """Check if there are price constraints."""
        return self.budget_min is not None or self.budget_max is not None


VALIDATION_PROMPT = """You are a product validation assistant. Your job is to verify if products match the user's requirements.

User's requirements:
{constraints}

Products to validate:
{products}

For each product, determine if it matches ALL the user's requirements. Be strict but reasonable:
- If the user wants "blue" items, the product should be blue (not navy, teal, etc. unless they clearly match)
- If the user wants "casual" style, the product should be casual or versatile (not formal)
- If constraints are vague, be lenient

Respond with a JSON array where each element has:
- "product_id": the product ID
- "matches": true or false
- "reason": brief explanation

Example response:
[
  {{"product_id": "123", "matches": true, "reason": "Blue cotton t-shirt matches color and casual style"}},
  {{"product_id": "456", "matches": false, "reason": "Product is red, not blue as requested"}}
]

Return ONLY the JSON array, no other text."""


class ResultValidator:
    """
    LLM validates search results against user constraints.

    Validation types:
    - Hard filters: Price (budget_min/max) - enforced strictly without LLM
    - Soft filters: Color, style, occasion - validated by LLM for semantic match
    """

    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def _apply_price_filter(
        self,
        results: list[dict],
        constraints: QueryConstraints
    ) -> list[dict]:
        """Apply hard price filtering without LLM."""
        if not constraints.has_price_constraints():
            return results

        filtered = []
        for r in results:
            price = r.get("price", 0)

            if constraints.budget_min is not None and price < constraints.budget_min:
                continue
            if constraints.budget_max is not None and price > constraints.budget_max:
                continue

            filtered.append(r)

        return filtered

    def _format_constraints_for_prompt(self, constraints: QueryConstraints) -> str:
        """Format constraints as a human-readable string for the LLM."""
        parts = []

        if constraints.color:
            parts.append(f"Color: {constraints.color}")
        if constraints.style:
            parts.append(f"Style: {constraints.style}")
        if constraints.occasion:
            parts.append(f"Occasion: {constraints.occasion}")
        if constraints.material:
            parts.append(f"Material: {constraints.material}")
        if constraints.category:
            parts.append(f"Category: {constraints.category}")
        if constraints.gender:
            parts.append(f"Gender: {constraints.gender}")

        return "\n".join(parts) if parts else "No specific constraints"

    def _format_products_for_prompt(self, products: list[dict]) -> str:
        """Format products for validation prompt."""
        formatted = []
        for p in products:
            formatted.append(
                f"- ID: {p.get('product_id', 'unknown')}\n"
                f"  Name: {p.get('name', 'Unknown')}\n"
                f"  Description: {p.get('description', 'N/A')[:200]}\n"
                f"  Categories: {', '.join(p.get('categories', []))}"
            )
        return "\n\n".join(formatted)

    async def validate(
        self,
        results: list[dict],
        constraints: QueryConstraints,
        use_llm: bool = True,
    ) -> tuple[list[dict], ValidationSummary]:
        """
        Validate search results against user constraints.

        Args:
            results: List of product dictionaries from search
            constraints: Extracted query constraints
            use_llm: Whether to use LLM for semantic validation

        Returns:
            Tuple of (validated_results, validation_summary)
        """
        total_candidates = len(results)

        # Step 1: Apply hard price filter
        price_filtered = self._apply_price_filter(results, constraints)

        # Step 2: If no semantic constraints or LLM disabled, return price-filtered results
        if not use_llm or not constraints.has_semantic_constraints():
            return price_filtered, ValidationSummary(
                total_candidates=total_candidates,
                passed_validation=len(price_filtered),
                failed_validation=total_candidates - len(price_filtered),
                validation_details=[{"type": "price_filter_only"}],
            )

        # Step 3: LLM semantic validation
        if not price_filtered:
            return [], ValidationSummary(
                total_candidates=total_candidates,
                passed_validation=0,
                failed_validation=total_candidates,
                validation_details=[{"type": "no_results_after_price_filter"}],
            )

        try:
            prompt = VALIDATION_PROMPT.format(
                constraints=self._format_constraints_for_prompt(constraints),
                products=self._format_products_for_prompt(price_filtered),
            )

            response = await self.openai.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=1000,
            )

            response_text = response.choices[0].message.content.strip()

            # Parse JSON response
            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            validations = json.loads(response_text)

            # Filter to only products that passed validation
            passed_ids = {v["product_id"] for v in validations if v.get("matches")}
            validated_results = [p for p in price_filtered if p.get("product_id") in passed_ids]

            return validated_results, ValidationSummary(
                total_candidates=total_candidates,
                passed_validation=len(validated_results),
                failed_validation=total_candidates - len(validated_results),
                validation_details=validations,
            )

        except Exception as e:
            logger.error(f"LLM validation failed: {e}")
            # On error, return price-filtered results without semantic validation
            return price_filtered, ValidationSummary(
                total_candidates=total_candidates,
                passed_validation=len(price_filtered),
                failed_validation=total_candidates - len(price_filtered),
                validation_details=[{"error": str(e), "fallback": "price_filter_only"}],
            )


# Singleton instance
result_validator = ResultValidator()
