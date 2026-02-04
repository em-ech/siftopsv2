#!/usr/bin/env python3
"""
Product Ingestion Script
Phase 1: CSV processing and normalization

Usage:
    python scripts/ingest.py <csv_file> <tenant_id>

Example:
    python scripts/ingest.py data/products.csv vanleeuwen
"""

import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_service import vector_service
from app.services.db_service import db_service


def normalize_csv_row(row: pd.Series, tenant_id: str) -> dict:
    """
    Normalize a CSV row into our product format.
    Handles messy data with fallbacks.
    """
    name = str(row.get("name", row.get("title", row.get("product_name", "Unknown"))))

    # Build description from various possible columns
    description = str(
        row.get(
            "description",
            row.get("desc", row.get("product_description", "")),
        )
    )
    short_desc = str(row.get("short_description", description[:200] if description else ""))

    # Combined text for embedding
    combined_text = f"{name}. {short_desc} {description}".strip()

    # Handle categories (could be comma-separated string or list)
    categories_raw = row.get("category", row.get("categories", ""))
    if isinstance(categories_raw, str):
        categories = [c.strip() for c in categories_raw.split(",") if c.strip()]
    else:
        categories = []

    return {
        "id": str(row.get("id", row.get("sku", hash(name) % (2**31)))),
        "tenant_id": tenant_id,
        "name": name,
        "slug": name.lower().replace(" ", "-").replace("'", ""),
        "sku": str(row.get("sku", "")),
        "price": str(row.get("price", "0")),
        "regular_price": str(row.get("regular_price", row.get("price", "0"))),
        "sale_price": str(row.get("sale_price", "")),
        "stock_status": row.get("stock_status", "instock"),
        "stock_quantity": row.get("stock_quantity", row.get("quantity")),
        "description": description,
        "short_description": short_desc,
        "combined_text": combined_text,
        "categories": categories,
        "image_url": row.get("image_url", row.get("image", row.get("img"))),
        "permalink": row.get("url", row.get("permalink", row.get("link", ""))),
    }


def ingest_csv(csv_path: str, tenant_id: str) -> int:
    """
    Ingest a CSV file into the system.

    Returns:
        Number of products processed
    """
    print(f"📂 Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"📊 Found {len(df)} rows")

    # Normalize all rows
    print("🔄 Normalizing data...")
    products = []
    for _, row in df.iterrows():
        try:
            product = normalize_csv_row(row, tenant_id)
            products.append(product)
        except Exception as e:
            print(f"⚠️  Skipping row due to error: {e}")

    print(f"✅ Normalized {len(products)} products")

    # Clear existing products for this tenant
    print(f"🗑️  Clearing existing products for tenant: {tenant_id}")
    vector_service.delete_tenant_products(tenant_id)
    try:
        db_service.delete_tenant_products(tenant_id)
    except Exception:
        print("⚠️  Could not clear Supabase (may not be configured)")

    # Store in Supabase
    print("💾 Storing in Supabase...")
    try:
        db_count = db_service.upsert_products_batch(products)
        print(f"✅ Stored {db_count} products in Supabase")
    except Exception as e:
        print(f"⚠️  Supabase storage failed: {e}")

    # Store in Qdrant (vectors)
    print("🧠 Creating embeddings and storing in Qdrant...")
    print("   (This may take a while for large datasets)")

    vector_count = 0
    batch_size = 10  # Process in batches to show progress

    for i in range(0, len(products), batch_size):
        batch = products[i : i + batch_size]
        vector_count += vector_service.upsert_products_batch(batch)
        print(f"   Processed {min(i + batch_size, len(products))}/{len(products)}")

    print(f"✅ Stored {vector_count} vectors in Qdrant")

    return vector_count


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/ingest.py <csv_file> <tenant_id>")
        print("Example: python scripts/ingest.py data/products.csv vanleeuwen")
        sys.exit(1)

    csv_path = sys.argv[1]
    tenant_id = sys.argv[2]

    if not Path(csv_path).exists():
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)

    print(f"\n🚀 Sift Retail AI - Product Ingestion")
    print(f"=" * 40)
    print(f"CSV File: {csv_path}")
    print(f"Tenant ID: {tenant_id}")
    print(f"=" * 40 + "\n")

    count = ingest_csv(csv_path, tenant_id)

    print(f"\n✨ Done! Ingested {count} products for tenant '{tenant_id}'")
    print("You can now test with: curl -X POST localhost:8000/search -d '{...}'")


if __name__ == "__main__":
    main()
