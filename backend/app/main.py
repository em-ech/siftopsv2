"""
Sift Retail AI - FastAPI Backend
A plug-and-play semantic discovery engine for retailers.

Features:
- Vector search with semantic understanding
- Multi-tenant security with metadata filtering
- RAG-powered chat (zero hallucination)
- WooCommerce integration
- ROI analytics
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.routes import search, chat, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📦 Debug mode: {settings.DEBUG}")
    yield
    # Shutdown
    print("👋 Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Semantic discovery engine for retail with RAG-powered recommendations",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "2.0.0",
        "status": "healthy",
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "openai": bool(settings.OPENAI_API_KEY),
            "qdrant": bool(settings.QDRANT_URL),
            "supabase": bool(settings.SUPABASE_URL),
            "woocommerce": bool(settings.WOOCOMMERCE_CONSUMER_KEY),
        },
    }
