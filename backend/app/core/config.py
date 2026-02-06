import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal

load_dotenv()


class Settings(BaseModel):
    # App
    APP_NAME: str = "Sift Retail AI"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHAT_MODEL: str = "gpt-4o"
    VISION_MODEL: str = "gpt-4o"  # For image analysis
    EMBEDDING_DIMENSIONS: int = 1536

    # Qdrant
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION: str = "products"

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # WooCommerce (Van Leeuwen Ice Cream)
    WOOCOMMERCE_URL: str = os.getenv("WOOCOMMERCE_URL", "https://vanleeuwenicecream.com")
    WOOCOMMERCE_CONSUMER_KEY: str = os.getenv("WOOCOMMERCE_CONSUMER_KEY", "")
    WOOCOMMERCE_CONSUMER_SECRET: str = os.getenv("WOOCOMMERCE_CONSUMER_SECRET", "")

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.vercel.app",
    ]

    # Security - Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    RATE_LIMIT_BURST: int = int(os.getenv("RATE_LIMIT_BURST", "10"))

    # RAG Pipeline
    RAG_STRATEGY: Literal["fast", "validated", "full"] = os.getenv("RAG_STRATEGY", "validated")
    # fast: Vector search only, no validation
    # validated: Vector search + LLM validation of results
    # full: Vector search + validation + reranking

    RERANKING_ENABLED: bool = os.getenv("RERANKING_ENABLED", "false").lower() == "true"
    VALIDATION_ENABLED: bool = os.getenv("VALIDATION_ENABLED", "true").lower() == "true"

    # Retrieval settings
    RETRIEVAL_CANDIDATES_MULTIPLIER: int = int(os.getenv("RETRIEVAL_CANDIDATES_MULTIPLIER", "2"))
    # Fetch this many extra candidates for reranking/validation buffer

    # Cache
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_SEARCH: int = int(os.getenv("CACHE_TTL_SEARCH", "300"))  # 5 minutes
    CACHE_TTL_EMBEDDING: int = int(os.getenv("CACHE_TTL_EMBEDDING", "3600"))  # 1 hour
    CACHE_TTL_QUERY: int = int(os.getenv("CACHE_TTL_QUERY", "600"))  # 10 minutes

    # Image Search
    IMAGE_SEARCH_ENABLED: bool = os.getenv("IMAGE_SEARCH_ENABLED", "true").lower() == "true"
    IMAGE_MAX_SIZE_MB: int = int(os.getenv("IMAGE_MAX_SIZE_MB", "10"))
    IMAGE_ALLOWED_TYPES: list = ["image/jpeg", "image/png", "image/webp", "image/gif"]


settings = Settings()
