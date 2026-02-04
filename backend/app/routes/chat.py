"""
Chat Routes
Handles conversational AI endpoints with RAG.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    tenant_id: str
    store_name: str = "our store"
    session_id: Optional[str] = None
    history: Optional[list[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str
    products: list[dict]
    products_count: int


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RAG-powered chat endpoint.

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

    # Convert history to dict format if provided
    history = None
    if request.history:
        history = [{"role": m.role, "content": m.content} for m in request.history]

    try:
        result = await chat_service.chat(
            query=request.message,
            tenant_id=request.tenant_id,
            store_name=request.store_name,
            conversation_history=history,
            session_id=request.session_id,
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
