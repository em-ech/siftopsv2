"""
Chat Routes
Handles conversational AI endpoints with RAG.
Includes security: injection detection, input sanitization, output validation.
Supports image-based search via GPT-4V.
"""

import base64
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import logging

from app.services.chat_service import chat_service
from app.services.rag.image_search import image_search_service
from app.core.config import settings
from app.core.security import injection_detector, sanitizer, output_validator

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    tenant_id: str
    store_name: str = "our store"
    session_id: Optional[str] = None
    history: Optional[list[ChatMessage]] = None
    # Image search support (Phase 3)
    image_data: Optional[str] = None  # Base64 encoded
    image_mime_type: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    products: list[dict]
    products_count: int
    security_flags: Optional[dict] = None  # Only populated if issues detected


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RAG-powered chat endpoint with security validation.

    Security pipeline:
    1. Check for prompt injection attempts
    2. Sanitize user input
    3. Process request
    4. Validate output for prompt leakage

    RAG pipeline:
    1. Converts user message to vector
    2. Retrieves relevant products (tenant-filtered)
    3. Generates response using ONLY retrieved products

    This ensures zero hallucination - the AI can only reference
    real products from this specific retailer.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if not request.tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id is required")

    # Step 1: Check for prompt injection
    detection = injection_detector.detect(request.message)
    if detection.risk_level == "high":
        logger.warning(
            f"High-risk injection attempt blocked for tenant {request.tenant_id}: "
            f"{detection.message}"
        )
        raise HTTPException(
            status_code=400,
            detail="Your message contains invalid content. Please rephrase your query."
        )

    # Log medium risk but allow (with sanitization)
    if detection.risk_level == "medium":
        logger.info(
            f"Medium-risk input detected for tenant {request.tenant_id}: "
            f"{detection.message}"
        )

    # Step 2: Sanitize input
    safe_message = sanitizer.sanitize_for_prompt(request.message)

    # Also sanitize history if provided
    history = None
    if request.history:
        history = [
            {
                "role": m.role,
                "content": sanitizer.sanitize_for_prompt(m.content)
            }
            for m in request.history
        ]

    try:
        # Step 3: Process the chat request
        result = await chat_service.chat(
            query=safe_message,
            tenant_id=request.tenant_id,
            store_name=request.store_name,
            conversation_history=history,
            session_id=request.session_id,
        )

        # Step 4: Validate output
        validation = output_validator.validate_response(
            result["response"],
            result["products"]
        )

        security_flags = None
        if not validation.is_valid:
            logger.warning(
                f"Output validation issues for tenant {request.tenant_id}: "
                f"{validation.issues}"
            )
            security_flags = {"issues": validation.issues}
            result["response"] = validation.sanitized_response

        return ChatResponse(
            response=result["response"],
            products=result["products"],
            products_count=result["products_count"],
            security_flags=security_flags,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error for tenant {request.tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== IMAGE SEARCH ENDPOINT ====================


class ImageSearchResponse(BaseModel):
    """Response from image-based search."""
    results: list[dict]
    count: int
    image_analysis: dict
    generated_query: str
    latency_ms: int


@router.post("/image", response_model=ImageSearchResponse)
async def chat_with_image(
    image: UploadFile = File(...),
    tenant_id: str = Form(...),
    context: Optional[str] = Form(None),
    top_k: int = Form(10),
):
    """
    Image-based product search.

    Upload an image to find similar products. The image is analyzed using
    GPT-4V to extract product attributes (category, color, style, etc.),
    then a search query is generated and executed.

    Args:
        image: Image file (JPEG, PNG, WebP, GIF)
        tenant_id: Tenant identifier
        context: Optional additional context (e.g., "find similar but cheaper")
        top_k: Number of results to return

    Returns:
        Search results with image analysis details
    """
    if not settings.IMAGE_SEARCH_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Image search is not enabled"
        )

    if not tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id is required")

    # Validate MIME type early
    content_type = image.content_type or "application/octet-stream"
    if content_type not in settings.IMAGE_ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image type: {content_type}. Allowed: {settings.IMAGE_ALLOWED_TYPES}"
        )

    try:
        # Read image data
        image_data = await image.read()

        # Sanitize context if provided
        safe_context = None
        if context:
            # Check for injection in context
            detection = injection_detector.detect(context)
            if detection.risk_level == "high":
                logger.warning(f"Injection attempt in image search context: {detection.message}")
                raise HTTPException(
                    status_code=400,
                    detail="Context contains invalid content."
                )
            safe_context = sanitizer.sanitize_for_prompt(context)

        # Perform image search
        results, analysis = await image_search_service.search_by_image(
            image_data=image_data,
            mime_type=content_type,
            tenant_id=tenant_id,
            context=safe_context,
            top_k=top_k,
        )

        return ImageSearchResponse(
            results=results.results,
            count=results.count,
            image_analysis=analysis.model_dump(),
            generated_query=analysis.generated_query,
            latency_ms=results.latency_ms,
        )

    except ValueError as e:
        # Validation errors from image_search_service
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image search error for tenant {tenant_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
