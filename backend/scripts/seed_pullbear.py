#!/usr/bin/env python3
"""
Seed script for loading Pull & Bear catalog into Sift Retail AI.

Usage:
    cd backend
    uv run python scripts/seed_pullbear.py

This script:
1. Creates the 'pullbear' tenant if it doesn't exist
2. Loads products from data/pullbear_catalog.json
3. Runs them through the ingestion pipeline (normalize, enrich, embed)
4. Stores them in Supabase and Qdrant
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the backend app to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.db_service import DBService
from app.services.vector_service import VectorService
from app.services.ingestion import IngestionPipeline, create_fast_pipeline


async def main():
    """Load Pull & Bear catalog into the system."""

    # Load catalog
    catalog_path = Path(__file__).parent.parent / "data" / "pullbear_catalog.json"
    if not catalog_path.exists():
        print(f"Error: Catalog not found at {catalog_path}")
        sys.exit(1)

    with open(catalog_path) as f:
        products = json.load(f)

    print(f"Loaded {len(products)} products from {catalog_path.name}")

    # Initialize services
    db = DBService()
    vector = VectorService()

    # Create tenant if needed
    tenant_id = "pullbear"
    try:
        # Check if tenant exists by trying to get products
        existing = await db.get_products(tenant_id, limit=1)
        print(f"Tenant '{tenant_id}' exists with existing products")
    except Exception:
        # Create tenant
        print(f"Creating tenant '{tenant_id}'...")
        await db.supabase.table("tenants").insert({
            "id": tenant_id,
            "name": "Pull & Bear",
            "config": {"description": "Pull & Bear fashion demo store"},
            "plan": "free"
        }).execute()
        print(f"Tenant '{tenant_id}' created")

    # Create ingestion pipeline (fast mode - no LLM enrichment)
    pipeline = create_fast_pipeline(db, vector)

    # Transform products to expected format
    raw_products = []
    for p in products:
        raw_products.append({
            "id": p["id"],
            "name": p["name"],
            "description": p.get("description", ""),
            "price": p.get("price", 0),
            "category": p.get("category", ""),
            "image_url": p.get("image_url"),
            "brand": p.get("brand", "Pull & Bear"),
            "tags": p.get("tags", "").split(",") if isinstance(p.get("tags"), str) else [],
        })

    print(f"\nProcessing {len(raw_products)} products through ingestion pipeline...")
    print("(This may take a few minutes for embedding generation)\n")

    # Process in batches
    batch_size = 10
    total_success = 0
    total_failed = 0

    for i in range(0, len(raw_products), batch_size):
        batch = raw_products[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(raw_products) + batch_size - 1) // batch_size

        print(f"Processing batch {batch_num}/{total_batches}...")

        result = await pipeline.process_batch(batch, tenant_id)

        total_success += result.successful
        total_failed += result.failed

        print(f"  - Success: {result.successful}, Failed: {result.failed}")
        if result.errors:
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"  - Error: {error}")

    print(f"\n{'='*50}")
    print(f"Seeding complete!")
    print(f"  Total processed: {len(raw_products)}")
    print(f"  Successful: {total_success}")
    print(f"  Failed: {total_failed}")
    print(f"{'='*50}")

    # Verify products in database
    products_in_db = await db.get_products(tenant_id, limit=100)
    print(f"\nVerification: {len(products_in_db)} products now in database for tenant '{tenant_id}'")


if __name__ == "__main__":
    asyncio.run(main())
