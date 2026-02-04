"""
Admin Routes
Handles retailer management, product ingestion, and analytics.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import io

from app.services.db_service import db_service
from app.services.vector_service import vector_service
from app.services.woocommerce_service import WooCommerceService

router = APIRouter(prefix="/admin", tags=["admin"])


# ==================== REQUEST/RESPONSE MODELS ====================


class TenantCreate(BaseModel):
    tenant_id: str
    name: str
    woocommerce_url: Optional[str] = None
    woocommerce_key: Optional[str] = None
    woocommerce_secret: Optional[str] = None


class WooCommerceSyncRequest(BaseModel):
    tenant_id: str
    woocommerce_url: str
    consumer_key: str
    consumer_secret: str


class AnalyticsResponse(BaseModel):
    total_searches: int
    unique_queries: int
    zero_result_queries: list
    top_queries: list
    conversion_rate: float


# ==================== TENANT ROUTES ====================


@router.post("/tenants")
async def create_tenant(tenant: TenantCreate):
    """Register a new retailer."""
    try:
        config = {}
        if tenant.woocommerce_url:
            config["woocommerce"] = {
                "url": tenant.woocommerce_url,
                "key": tenant.woocommerce_key,
                "secret": tenant.woocommerce_secret,
            }

        result = db_service.create_tenant(
            tenant_id=tenant.tenant_id,
            name=tenant.name,
            config=config,
        )
        return {"success": True, "tenant": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants")
async def list_tenants():
    """List all registered retailers."""
    try:
        tenants = db_service.list_tenants()
        return {"tenants": tenants}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get a specific retailer."""
    try:
        tenant = db_service.get_tenant(tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return {"tenant": tenant}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PRODUCT INGESTION ROUTES ====================


@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
):
    """
    Upload a CSV file to ingest products.

    Expected CSV columns:
    - name (required)
    - description
    - price
    - image_url
    - category
    - sku
    - stock_status
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        # Validate required columns
        if "name" not in df.columns:
            raise HTTPException(
                status_code=400, detail="CSV must have a 'name' column"
            )

        # Normalize and process products
        products = []
        for _, row in df.iterrows():
            product = {
                "id": str(row.get("id", hash(row["name"]) % (2**31))),
                "tenant_id": tenant_id,
                "name": row["name"],
                "slug": row.get("slug", row["name"].lower().replace(" ", "-")),
                "sku": str(row.get("sku", "")),
                "price": str(row.get("price", "0")),
                "regular_price": str(row.get("regular_price", row.get("price", "0"))),
                "sale_price": str(row.get("sale_price", "")),
                "stock_status": row.get("stock_status", "instock"),
                "stock_quantity": row.get("stock_quantity"),
                "description": str(row.get("description", "")),
                "short_description": str(row.get("short_description", row.get("description", "")[:200])),
                "combined_text": f"{row['name']}. {row.get('description', '')}",
                "categories": [row.get("category", "")] if row.get("category") else [],
                "image_url": row.get("image_url"),
                "permalink": row.get("url", row.get("permalink", "")),
            }
            products.append(product)

        # Store in Supabase
        try:
            db_service.upsert_products_batch(products)
        except Exception:
            pass  # Continue even if DB fails

        # Store in Qdrant (vectors)
        count = vector_service.upsert_products_batch(products)

        return {
            "success": True,
            "products_processed": count,
            "tenant_id": tenant_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/woocommerce")
async def sync_woocommerce(request: WooCommerceSyncRequest):
    """
    Sync products from a WooCommerce store.
    This connects to stores like Van Leeuwen Ice Cream.
    """
    try:
        # Initialize WooCommerce client
        wc = WooCommerceService(
            url=request.woocommerce_url,
            consumer_key=request.consumer_key,
            consumer_secret=request.consumer_secret,
        )

        # Fetch all products
        raw_products = wc.get_all_products()

        # Normalize products
        products = [
            wc.normalize_product(p, request.tenant_id) for p in raw_products
        ]

        # Clear existing products for this tenant (re-sync)
        vector_service.delete_tenant_products(request.tenant_id)
        try:
            db_service.delete_tenant_products(request.tenant_id)
        except Exception:
            pass

        # Store in databases
        try:
            db_service.upsert_products_batch(products)
        except Exception:
            pass

        count = vector_service.upsert_products_batch(products)

        return {
            "success": True,
            "products_synced": count,
            "tenant_id": request.tenant_id,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ANALYTICS ROUTES ====================


@router.get("/analytics/{tenant_id}", response_model=AnalyticsResponse)
async def get_analytics(tenant_id: str, days: int = 30):
    """
    Get ROI analytics for a retailer.

    Returns:
    - Total searches
    - Unique queries
    - Zero-result queries (the "Demand Map" - what users want but can't find)
    - Top queries
    - Conversion rate
    """
    try:
        analytics = db_service.get_search_analytics(tenant_id, days=days)
        return AnalyticsResponse(**analytics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{tenant_id}")
async def get_products(tenant_id: str, limit: int = 100):
    """Get all products for a tenant."""
    try:
        products = db_service.get_products(tenant_id, limit=limit)
        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
