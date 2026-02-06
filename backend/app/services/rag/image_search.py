"""
Image Search Service
Converts uploaded images to search queries using GPT-4V (Vision).

Flow:
1. Validate image (MIME type, size)
2. Analyze with GPT-4V to extract: category, color, style, material
3. Generate natural language search query
4. Use standard search pipeline with generated query
"""

import base64
import logging
from typing import Optional, NamedTuple
from pydantic import BaseModel
from openai import AsyncOpenAI

from app.core.config import settings
from app.services.rag.retriever import EnhancedRetriever, RetrievalResult

logger = logging.getLogger(__name__)


class ImageAnalysis(BaseModel):
    """Result of image analysis."""
    category: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None
    material: Optional[str] = None
    pattern: Optional[str] = None
    description: str
    generated_query: str
    confidence: float  # 0-1 confidence in the analysis


class ImageValidation(NamedTuple):
    """Result of image validation."""
    is_valid: bool
    error: Optional[str]


IMAGE_ANALYSIS_PROMPT = """Analyze this product image for a retail search system.

Extract the following attributes if visible:
1. Category: What type of product is this? (e.g., t-shirt, hoodie, jacket, dress, jeans, sneakers, bag)
2. Color: What is the primary color? (e.g., blue, red, black, white, multicolor)
3. Style: What style is this? (e.g., casual, formal, streetwear, athletic, vintage)
4. Material: What material does it appear to be? (e.g., cotton, denim, leather, polyester)
5. Pattern: Any pattern? (e.g., solid, striped, graphic print, floral)

Then generate a natural language search query that would find similar products.

Respond in this exact JSON format:
{
  "category": "...",
  "color": "...",
  "style": "...",
  "material": "...",
  "pattern": "...",
  "description": "Brief description of the product",
  "generated_query": "natural language search query",
  "confidence": 0.85
}

Be specific but not overly detailed. Focus on the main visual characteristics."""


class ImageSearchService:
    """
    Service for image-based product search.

    Uses GPT-4V to analyze images and convert them to search queries,
    then uses the standard search pipeline.
    """

    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.retriever = EnhancedRetriever()

    def validate_image(
        self,
        image_data: bytes,
        mime_type: str,
    ) -> ImageValidation:
        """
        Validate an uploaded image.

        Checks:
        - MIME type is allowed
        - Size is within limits
        """
        # Check MIME type
        if mime_type not in settings.IMAGE_ALLOWED_TYPES:
            return ImageValidation(
                False,
                f"Invalid image type: {mime_type}. Allowed: {settings.IMAGE_ALLOWED_TYPES}"
            )

        # Check size
        size_mb = len(image_data) / (1024 * 1024)
        if size_mb > settings.IMAGE_MAX_SIZE_MB:
            return ImageValidation(
                False,
                f"Image too large: {size_mb:.1f}MB. Max: {settings.IMAGE_MAX_SIZE_MB}MB"
            )

        return ImageValidation(True, None)

    async def analyze_image(
        self,
        image_data: bytes,
        mime_type: str,
    ) -> ImageAnalysis:
        """
        Analyze an image using GPT-4V to extract product attributes.

        Args:
            image_data: Raw image bytes
            mime_type: Image MIME type (e.g., "image/jpeg")

        Returns:
            ImageAnalysis with extracted attributes and generated query
        """
        # Encode image to base64
        base64_image = base64.b64encode(image_data).decode("utf-8")

        # Call GPT-4V
        response = await self.openai.chat.completions.create(
            model=settings.VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": IMAGE_ANALYSIS_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}",
                                "detail": "low",  # Use low detail for faster processing
                            },
                        },
                    ],
                }
            ],
            max_tokens=500,
            temperature=0.3,
        )

        response_text = response.choices[0].message.content.strip()

        # Parse JSON response
        import json

        # Handle potential markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]

        try:
            data = json.loads(response_text)
            return ImageAnalysis(
                category=data.get("category"),
                color=data.get("color"),
                style=data.get("style"),
                material=data.get("material"),
                pattern=data.get("pattern"),
                description=data.get("description", "Product image"),
                generated_query=data.get("generated_query", "product"),
                confidence=data.get("confidence", 0.5),
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse image analysis response: {e}")
            # Return a basic analysis
            return ImageAnalysis(
                description="Product image",
                generated_query="product",
                confidence=0.1,
            )

    async def search_by_image(
        self,
        image_data: bytes,
        mime_type: str,
        tenant_id: str,
        context: Optional[str] = None,
        top_k: int = 10,
    ) -> tuple[RetrievalResult, ImageAnalysis]:
        """
        Search for products similar to an uploaded image.

        Args:
            image_data: Raw image bytes
            mime_type: Image MIME type
            tenant_id: Tenant identifier
            context: Optional additional context (e.g., "find similar but cheaper")
            top_k: Number of results to return

        Returns:
            Tuple of (search_results, image_analysis)
        """
        # Step 1: Validate image
        validation = self.validate_image(image_data, mime_type)
        if not validation.is_valid:
            raise ValueError(validation.error)

        # Step 2: Analyze image
        analysis = await self.analyze_image(image_data, mime_type)

        # Step 3: Build search query
        query = analysis.generated_query

        # Add context if provided (e.g., "find similar but cheaper")
        if context:
            query = f"{query} {context}"

        logger.info(f"Image search query generated: {query}")

        # Step 4: Search using the standard pipeline
        results = await self.retriever.retrieve(
            query=query,
            tenant_id=tenant_id,
            top_k=top_k,
            strategy="validated",  # Use validation for image search
        )

        return results, analysis


# Singleton instance
image_search_service = ImageSearchService()
