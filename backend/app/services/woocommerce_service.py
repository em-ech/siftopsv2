"""
WooCommerce API Service
Handles product synchronization from WooCommerce stores.
"""

from woocommerce import API
from typing import Optional
from app.core.config import settings


class WooCommerceService:
    def __init__(
        self,
        url: str = None,
        consumer_key: str = None,
        consumer_secret: str = None,
    ):
        self.wcapi = API(
            url=url or settings.WOOCOMMERCE_URL,
            consumer_key=consumer_key or settings.WOOCOMMERCE_CONSUMER_KEY,
            consumer_secret=consumer_secret or settings.WOOCOMMERCE_CONSUMER_SECRET,
            version="wc/v3",
            timeout=30,
        )

    def get_products(
        self, page: int = 1, per_page: int = 100, category: Optional[int] = None
    ) -> list[dict]:
        """Fetch products from WooCommerce store."""
        params = {"page": page, "per_page": per_page, "status": "publish"}
        if category:
            params["category"] = category

        response = self.wcapi.get("products", params=params)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"WooCommerce API error: {response.text}")

    def get_all_products(self) -> list[dict]:
        """Fetch all products with pagination."""
        all_products = []
        page = 1

        while True:
            products = self.get_products(page=page, per_page=100)
            if not products:
                break
            all_products.extend(products)
            page += 1

        return all_products

    def get_product(self, product_id: int) -> dict:
        """Fetch a single product by ID."""
        response = self.wcapi.get(f"products/{product_id}")
        if response.status_code == 200:
            return response.json()
        raise Exception(f"WooCommerce API error: {response.text}")

    def get_categories(self) -> list[dict]:
        """Fetch all product categories."""
        response = self.wcapi.get("products/categories", params={"per_page": 100})
        if response.status_code == 200:
            return response.json()
        raise Exception(f"WooCommerce API error: {response.text}")

    def normalize_product(self, product: dict, tenant_id: str) -> dict:
        """
        Normalize WooCommerce product data for ingestion.
        Handles messy data and extracts relevant fields.
        """
        # Extract primary image
        images = product.get("images", [])
        primary_image = images[0]["src"] if images else None

        # Extract categories
        categories = [cat["name"] for cat in product.get("categories", [])]

        # Build description for embedding
        name = product.get("name", "")
        short_desc = product.get("short_description", "")
        description = product.get("description", "")

        # Clean HTML from descriptions
        import re

        def clean_html(text: str) -> str:
            return re.sub(r"<[^>]+>", "", text).strip()

        clean_short = clean_html(short_desc)
        clean_desc = clean_html(description)

        # Combine for semantic search
        combined_text = f"{name}. {clean_short} {clean_desc}".strip()

        return {
            "id": str(product["id"]),
            "tenant_id": tenant_id,
            "name": name,
            "slug": product.get("slug", ""),
            "sku": product.get("sku", ""),
            "price": product.get("price", "0"),
            "regular_price": product.get("regular_price", "0"),
            "sale_price": product.get("sale_price", ""),
            "stock_status": product.get("stock_status", "instock"),
            "stock_quantity": product.get("stock_quantity"),
            "description": clean_desc,
            "short_description": clean_short,
            "combined_text": combined_text,
            "categories": categories,
            "image_url": primary_image,
            "permalink": product.get("permalink", ""),
            "attributes": product.get("attributes", []),
        }


# Singleton instance
woocommerce_service = WooCommerceService()
