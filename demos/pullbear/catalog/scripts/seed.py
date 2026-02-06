#!/usr/bin/env python3
"""
Pull & Bear Demo Catalog Seeder

Seeds the Pull & Bear demo catalog into Sift Retail AI.

Usage:
    cd demos/pullbear/catalog/scripts
    python seed.py

    Or from project root:
    cd siftopsv2
    python -m demos.pullbear.catalog.scripts.seed

Prerequisites:
    - Backend server configured with .env file
    - Supabase and Qdrant credentials set
    - Run from a Python environment with backend dependencies installed

This script:
1. Creates the 'pullbear' tenant if it doesn't exist
2. Loads products from ../data/pullbear_catalog.json
3. Runs them through the ingestion pipeline (normalize, embed)
4. Stores them in Supabase and Qdrant
"""

import json
import sys
from pathlib import Path

# Determine paths
SCRIPT_DIR = Path(__file__).parent.resolve()
CATALOG_DIR = SCRIPT_DIR.parent
DEMO_DIR = CATALOG_DIR.parent
PROJECT_ROOT = DEMO_DIR.parent.parent  # siftopsv2/

# Add backend to path
BACKEND_PATH = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_PATH))

# Catalog data path
CATALOG_FILE = CATALOG_DIR / "data" / "pullbear_catalog.json"


def main():
    """Load Pull & Bear catalog into the system."""

    print("=" * 60)
    print("Pull & Bear Demo Catalog Seeder")
    print("=" * 60)

    # Verify catalog exists
    if not CATALOG_FILE.exists():
        print(f"\nError: Catalog not found at {CATALOG_FILE}")
        print(f"Expected location: demos/pullbear/catalog/data/pullbear_catalog.json")
        sys.exit(1)

    # Import backend services (after path setup)
    try:
        from app.services.db_service import DatabaseService
        from app.services.vector_service import VectorService
        from app.schemas.product import ProductRaw
        from app.services.ingestion import create_fast_pipeline
    except ImportError as e:
        print(f"\nError: Could not import backend services: {e}")
        print("Make sure you're running from an environment with backend dependencies installed.")
        print(f"Backend path: {BACKEND_PATH}")
        sys.exit(1)

    # Load catalog
    with open(CATALOG_FILE) as f:
        products = json.load(f)

    print(f"\nLoaded {len(products)} products from catalog")
    print(f"Source: {CATALOG_FILE.relative_to(PROJECT_ROOT)}")

    # Initialize services
    db = DatabaseService()
    vector = VectorService()

    tenant_id = "pullbear"

    # Check/create tenant
    print(f"\nChecking tenant '{tenant_id}'...")
    try:
        result = db.client.table("tenants").select("id").eq("id", tenant_id).execute()
        if not result.data:
            print(f"Creating tenant '{tenant_id}'...")
            db.client.table("tenants").insert({
                "id": tenant_id,
                "name": "Pull & Bear",
                "config": {
                    "description": "Pull & Bear fashion demo store",
                    "demo": True,
                },
            }).execute()
            print(f"Tenant '{tenant_id}' created")
        else:
            print(f"Tenant '{tenant_id}' exists")
    except Exception as e:
        print(f"Warning: Could not verify tenant: {e}")

    # Create ingestion pipeline (fast mode - no LLM enrichment)
    pipeline = create_fast_pipeline()

    # Transform products to ProductRaw objects
    raw_products = []
    for p in products:
        tags = p.get("tags", "")
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        raw = ProductRaw(
            id=p["id"],
            name=p["name"],
            description=p.get("description", ""),
            price=float(p.get("price", 0)),
            categories=[p.get("category", "")] if p.get("category") else [],
            image_url=p.get("image_url"),
            brand=p.get("brand", "Pull & Bear"),
            tags=tags,
            stock_status="instock",
        )
        raw_products.append(raw)

    print(f"\nProcessing {len(raw_products)} products through ingestion pipeline...")
    print("(This may take a few minutes for embedding generation)\n")

    # Process through pipeline
    def progress_callback(processed, total):
        print(f"  Progress: {processed}/{total}")

    result = pipeline.process(raw_products, tenant_id, progress_callback=progress_callback)

    print(f"\nPipeline complete:")
    print(f"  - Total: {result.total}")
    print(f"  - Successful: {result.successful}")
    print(f"  - Failed: {result.failed}")

    if result.errors:
        print(f"\nErrors:")
        for error in result.errors[:5]:
            print(f"  - {error}")

    if not result.products:
        print("\nNo products to store!")
        sys.exit(1)

    # Store in database
    print(f"\nStoring {len(result.products)} products in Supabase...")
    products_data = []
    for p in result.products:
        products_data.append({
            "tenant_id": p.tenant_id,
            "id": p.external_id,
            "name": p.name,
            "slug": p.slug,
            "sku": p.sku or "",
            "price": p.price,
            "regular_price": p.regular_price or p.price,
            "sale_price": p.sale_price,
            "stock_status": p.stock_status,
            "stock_quantity": p.stock_quantity,
            "description": p.description or "",
            "short_description": p.short_description or "",
            "categories": p.categories,
            "image_url": p.image_url,
            "permalink": p.permalink or "",
        })
    db_count = db.upsert_products_batch(products_data)
    print(f"  - Stored {db_count} products in database")

    # Store in vector database
    print(f"\nGenerating embeddings and storing in Qdrant...")

    vector_products = []
    for p in result.products:
        vector_products.append({
            "id": p.external_id,
            "tenant_id": p.tenant_id,
            "name": p.name,
            "short_description": p.short_description or p.description[:200] if p.description else "",
            "price": p.price,
            "image_url": p.image_url,
            "permalink": p.permalink or "",
            "categories": p.categories,
            "stock_status": p.stock_status,
            "combined_text": p.embedding_text,
        })

    try:
        vector_count = vector.upsert_products_batch(vector_products)
        print(f"  - Stored {vector_count} products in vector database")
    except Exception as e:
        print(f"  - Warning: Vector storage failed: {e}")
        print("    (Products are in Supabase, but vector search won't work)")

    print(f"\n{'='*60}")
    print(f"Seeding complete!")
    print(f"{'='*60}")
    print(f"  Tenant: {tenant_id}")
    print(f"  Products in DB: {db_count}")
    print(f"\nNext steps:")
    print(f"  1. Start the backend: cd backend && uv run uvicorn app.main:app --reload")
    print(f"  2. Start the UI: cd demos/pullbear/ui && npm run dev")
    print(f"  3. Open http://localhost:3000")

    # Verify
    print(f"\nSample products:")
    products_in_db = db.get_products(tenant_id, limit=5)
    for p in products_in_db:
        print(f"  - {p['name']} (${p['price']})")


if __name__ == "__main__":
    main()
