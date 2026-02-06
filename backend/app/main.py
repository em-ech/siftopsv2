"""
Sift Retail AI - FastAPI Backend
A plug-and-play semantic discovery engine for retailers.

Features:
- Vector search with semantic understanding
- Multi-tenant security with metadata filtering
- RAG-powered chat (zero hallucination)
- WooCommerce integration
- ROI analytics
- Security: rate limiting, injection detection, input sanitization
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.security import RateLimitMiddleware, RateLimitConfig
from app.routes import search, chat, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📦 Debug mode: {settings.DEBUG}")
    print(f"🔒 Rate limiting: {'enabled' if settings.RATE_LIMIT_ENABLED else 'disabled'}")
    yield
    # Shutdown
    print("👋 Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Semantic discovery engine for retail with RAG-powered recommendations",
    version="2.0.0",
    lifespan=lifespan,
)

# Rate limiting middleware (must be added before CORS)
if settings.RATE_LIMIT_ENABLED:
    rate_limit_config = RateLimitConfig(
        enabled=True,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
        requests_per_hour=settings.RATE_LIMIT_PER_HOUR,
        burst_limit=settings.RATE_LIMIT_BURST,
    )
    app.add_middleware(
        RateLimitMiddleware,
        config=rate_limit_config,
        exclude_paths=["/", "/health", "/docs", "/openapi.json", "/redoc"],
    )

# CORS configuration - use configured origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
