"""
Vector Service
Handles embeddings and Qdrant vector database operations.
Zero-hallucination RAG with tenant isolation.
"""

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)
from typing import Optional
from app.core.config import settings


class VectorService:
    def __init__(self):
        # OpenAI client for embeddings
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Qdrant client - use cloud if configured, otherwise in-memory
        qdrant_configured = (
            settings.QDRANT_URL
            and settings.QDRANT_API_KEY
            and "your-cluster" not in settings.QDRANT_URL
            and "your-qdrant" not in settings.QDRANT_API_KEY
        )

        if qdrant_configured:
            self.qdrant = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
            print("📦 Qdrant: Connected to cloud instance")
        else:
            # Local Qdrant for development
            self.qdrant = QdrantClient(":memory:")
            print("📦 Qdrant: Using in-memory storage (data won't persist)")

        self.collection_name = settings.QDRANT_COLLECTION
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.qdrant.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSIONS,
                    distance=Distance.COSINE,
                ),
            )
            # Create payload index for tenant_id filtering
            self.qdrant.create_payload_index(
                collection_name=self.collection_name,
                field_name="tenant_id",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            print("📦 Created collection with tenant_id index")

    def create_embedding(self, text: str) -> list[float]:
        """
        Convert text into a 1536-dimensional vector.
        This captures the semantic 'meaning' of the text.
        """
        response = self.openai.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding

    def upsert_product(self, product: dict) -> None:
        """
        Store a product in the vector database.
        Uses combined_text for the embedding.
        """
        # Create embedding from combined product text
        embedding = self.create_embedding(product["combined_text"])

        # Create point with payload
        point = PointStruct(
            id=hash(f"{product['tenant_id']}_{product['id']}") % (2**63),
            vector=embedding,
            payload={
                "product_id": product["id"],
                "tenant_id": product["tenant_id"],
                "name": product["name"],
                "price": product["price"],
                "description": product["short_description"],
                "image_url": product["image_url"],
                "permalink": product["permalink"],
                "categories": product["categories"],
                "stock_status": product["stock_status"],
            },
        )

        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[point],
        )

    def upsert_products_batch(self, products: list[dict]) -> int:
        """Batch upsert products for efficiency."""
        points = []
        for product in products:
            embedding = self.create_embedding(product["combined_text"])
            point = PointStruct(
                id=hash(f"{product['tenant_id']}_{product['id']}") % (2**63),
                vector=embedding,
                payload={
                    "product_id": product["id"],
                    "tenant_id": product["tenant_id"],
                    "name": product["name"],
                    "price": product["price"],
                    "description": product["short_description"],
                    "image_url": product["image_url"],
                    "permalink": product["permalink"],
                    "categories": product["categories"],
                    "stock_status": product["stock_status"],
                },
            )
            points.append(point)

        if points:
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points,
            )

        return len(points)

    def search(
        self,
        query: str,
        tenant_id: str,
        top_k: int = 5,
        score_threshold: Optional[float] = 0.3,
    ) -> list[dict]:
        """
        SECURITY-CRITICAL: Search products with HARD tenant filter.
        This ensures complete data isolation between retailers.
        """
        # Convert query to vector
        query_vector = self.create_embedding(query)

        # HARD FILTER: tenant_id must match exactly
        # This happens at the database level - zero risk of data leakage
        tenant_filter = Filter(
            must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]
        )

        # Search with filter using query_points (new Qdrant API)
        results = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=tenant_filter,
            limit=top_k,
            score_threshold=score_threshold,
        )

        # Format results (query_points returns QueryResponse with .points)
        return [
            {
                "score": hit.score,
                "product_id": hit.payload["product_id"],
                "name": hit.payload["name"],
                "price": hit.payload["price"],
                "description": hit.payload["description"],
                "image_url": hit.payload["image_url"],
                "permalink": hit.payload["permalink"],
                "categories": hit.payload["categories"],
                "stock_status": hit.payload["stock_status"],
            }
            for hit in results.points
        ]

    def delete_tenant_products(self, tenant_id: str) -> None:
        """Delete all products for a tenant (for re-sync)."""
        self.qdrant.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))
                ]
            ),
        )


# Singleton instance
vector_service = VectorService()
