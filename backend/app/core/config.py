import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    # App
    APP_NAME: str = "Sift Retail AI"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHAT_MODEL: str = "gpt-4o"
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
    CORS_ORIGINS: list = ["http://localhost:3000", "https://*.vercel.app"]


settings = Settings()
