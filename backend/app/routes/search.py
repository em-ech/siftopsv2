"""
Search Routes
Handles semantic search endpoints with tenant isolation.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.vector_service import vector_service

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    tenant_id: str
    top_k: int = 5


class SearchResponse(BaseModel):
    results: list[dict]
    count: int


@router.post("/", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    Semantic product search with HARD tenant isolation.

    The tenant_id filter is applied at the database level,
    ensuring zero risk of cross-tenant data leakage.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if not request.tenant_id.strip():
        raise HTTPException(status_code=400, detail="tenant_id is required")

    try:
        results = vector_service.search(
            query=request.query,
            tenant_id=request.tenant_id,
            top_k=request.top_k,
        )
        return SearchResponse(results=results, count=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
