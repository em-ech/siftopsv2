"""
Database Service
Handles Supabase operations for relational data:
- Products (hard data: price, stock, images)
- Tenants (retailers)
- Search Logs (for ROI analytics)
"""

from supabase import create_client, Client
from datetime import datetime
from typing import Optional
from app.core.config import settings


class DatabaseService:
    def __init__(self):
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            self.client: Client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY,
            )
        else:
            self.client = None

    def _ensure_client(self):
        if not self.client:
            raise Exception("Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY.")

    # ==================== TENANT OPERATIONS ====================

    def create_tenant(self, tenant_id: str, name: str, config: dict = None) -> dict:
        """Register a new retailer/tenant."""
        self._ensure_client()
        data = {
            "id": tenant_id,
            "name": name,
            "config": config or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        result = self.client.table("tenants").insert(data).execute()
        return result.data[0] if result.data else None

    def get_tenant(self, tenant_id: str) -> Optional[dict]:
        """Get tenant by ID."""
        self._ensure_client()
        result = (
            self.client.table("tenants")
            .select("*")
            .eq("id", tenant_id)
            .single()
            .execute()
        )
        return result.data

    def list_tenants(self) -> list[dict]:
        """List all tenants."""
        self._ensure_client()
        result = self.client.table("tenants").select("*").execute()
        return result.data or []

    # ==================== PRODUCT OPERATIONS ====================

    def upsert_product(self, product: dict) -> dict:
        """Insert or update a product in Supabase."""
        self._ensure_client()
        data = {
            "id": f"{product['tenant_id']}_{product['id']}",
            "tenant_id": product["tenant_id"],
            "external_id": product["id"],
            "name": product["name"],
            "slug": product["slug"],
            "sku": product.get("sku", ""),
            "price": float(product["price"]) if product["price"] else 0,
            "regular_price": float(product["regular_price"]) if product["regular_price"] else 0,
            "sale_price": float(product["sale_price"]) if product["sale_price"] else None,
            "stock_status": product["stock_status"],
            "stock_quantity": product.get("stock_quantity"),
            "description": product["description"],
            "short_description": product["short_description"],
            "categories": product["categories"],
            "image_url": product["image_url"],
            "permalink": product["permalink"],
            "updated_at": datetime.utcnow().isoformat(),
        }
        result = self.client.table("products").upsert(data).execute()
        return result.data[0] if result.data else None

    def upsert_products_batch(self, products: list[dict]) -> int:
        """Batch upsert products."""
        self._ensure_client()
        data = [
            {
                "id": f"{p['tenant_id']}_{p['id']}",
                "tenant_id": p["tenant_id"],
                "external_id": p["id"],
                "name": p["name"],
                "slug": p["slug"],
                "sku": p.get("sku", ""),
                "price": float(p["price"]) if p["price"] else 0,
                "regular_price": float(p["regular_price"]) if p["regular_price"] else 0,
                "sale_price": float(p["sale_price"]) if p["sale_price"] else None,
                "stock_status": p["stock_status"],
                "stock_quantity": p.get("stock_quantity"),
                "description": p["description"],
                "short_description": p["short_description"],
                "categories": p["categories"],
                "image_url": p["image_url"],
                "permalink": p["permalink"],
                "updated_at": datetime.utcnow().isoformat(),
            }
            for p in products
        ]
        result = self.client.table("products").upsert(data).execute()
        return len(result.data) if result.data else 0

    def get_products(self, tenant_id: str, limit: int = 100) -> list[dict]:
        """Get products for a tenant."""
        self._ensure_client()
        result = (
            self.client.table("products")
            .select("*")
            .eq("tenant_id", tenant_id)
            .limit(limit)
            .execute()
        )
        return result.data or []

    def get_product(self, tenant_id: str, product_id: str) -> Optional[dict]:
        """Get a specific product."""
        self._ensure_client()
        result = (
            self.client.table("products")
            .select("*")
            .eq("id", f"{tenant_id}_{product_id}")
            .single()
            .execute()
        )
        return result.data

    def delete_tenant_products(self, tenant_id: str) -> None:
        """Delete all products for a tenant."""
        self._ensure_client()
        self.client.table("products").delete().eq("tenant_id", tenant_id).execute()

    # ==================== SEARCH LOG OPERATIONS (ROI Analytics) ====================

    def log_search(
        self,
        tenant_id: str,
        query: str,
        results_count: int,
        session_id: Optional[str] = None,
        converted: bool = False,
    ) -> dict:
        """
        Log a search query for analytics.
        This powers the "Demand Map" feature - showing what users want but can't find.
        """
        self._ensure_client()
        data = {
            "tenant_id": tenant_id,
            "query": query,
            "results_count": results_count,
            "session_id": session_id,
            "converted": converted,
            "created_at": datetime.utcnow().isoformat(),
        }
        result = self.client.table("search_logs").insert(data).execute()
        return result.data[0] if result.data else None

    def get_search_analytics(
        self, tenant_id: str, days: int = 30
    ) -> dict:
        """
        Get search analytics for a tenant.
        Returns: top queries, zero-result queries, conversion rate.
        """
        self._ensure_client()
        from datetime import timedelta

        since = (datetime.utcnow() - timedelta(days=days)).isoformat()

        # Get all searches in time period
        result = (
            self.client.table("search_logs")
            .select("*")
            .eq("tenant_id", tenant_id)
            .gte("created_at", since)
            .execute()
        )

        logs = result.data or []

        if not logs:
            return {
                "total_searches": 0,
                "unique_queries": 0,
                "zero_result_queries": [],
                "top_queries": [],
                "conversion_rate": 0,
            }

        # Analyze
        from collections import Counter

        queries = [log["query"].lower() for log in logs]
        zero_results = [log["query"] for log in logs if log["results_count"] == 0]
        conversions = sum(1 for log in logs if log["converted"])

        query_counts = Counter(queries)
        zero_result_counts = Counter(zero_results)

        return {
            "total_searches": len(logs),
            "unique_queries": len(set(queries)),
            "zero_result_queries": zero_result_counts.most_common(10),
            "top_queries": query_counts.most_common(10),
            "conversion_rate": conversions / len(logs) if logs else 0,
        }


# Singleton instance
db_service = DatabaseService()
