#!/usr/bin/env python3
"""
Export catalog data for the UI.

Converts the JSONL output from the crawler to a JSON file
suitable for the Next.js storefront.

Usage:
    python scripts/export_for_ui.py --input out/catalog.jsonl --output ui/public/catalog.json
"""

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load products from JSONL file."""
    products = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                products.append(json.loads(line))
    return products


def transform_for_ui(products: list[dict]) -> dict:
    """Transform products for UI consumption."""
    # Extract unique categories
    categories = {}
    for product in products:
        for cat in product.get("categories", []):
            cat_name = cat.get("name") or cat
            if isinstance(cat, dict):
                slug = cat.get("slug", cat_name.lower().replace(" ", "-"))
                categories[slug] = {
                    "name": cat_name,
                    "slug": slug,
                    "url": cat.get("url"),
                }
            else:
                slug = cat_name.lower().replace(" ", "-")
                categories[slug] = {"name": cat_name, "slug": slug}

    # Transform products for UI
    ui_products = []
    for product in products:
        # Get main image URL
        main_image = None
        if product.get("main_image"):
            if isinstance(product["main_image"], dict):
                main_image = product["main_image"].get("url")
            else:
                main_image = product["main_image"]

        # Get gallery images
        gallery = []
        for img in product.get("gallery_images", []):
            if isinstance(img, dict):
                gallery.append(img.get("url"))
            else:
                gallery.append(img)

        # Extract price as number
        price = None
        price_text = product.get("price_text") or product.get("regular_price") or ""
        if price_text:
            # Extract numeric value
            import re
            match = re.search(r"[\d.]+", str(price_text))
            if match:
                try:
                    price = float(match.group())
                except ValueError:
                    pass

        # Get categories as list of slugs
        cat_slugs = []
        for cat in product.get("categories", []):
            if isinstance(cat, dict):
                cat_slugs.append(cat.get("slug") or cat.get("name", "").lower().replace(" ", "-"))
            else:
                cat_slugs.append(cat.lower().replace(" ", "-"))

        ui_product = {
            "id": product.get("slug") or product.get("sku") or str(hash(product["product_url"])),
            "slug": product.get("slug", ""),
            "name": product.get("name", "Unknown"),
            "price": price,
            "priceText": price_text,
            "currency": product.get("currency_symbol", "$"),
            "inStock": product.get("in_stock", True),
            "stockText": product.get("stock_text"),
            "shortDescription": product.get("short_description"),
            "longDescription": product.get("long_description"),
            "mainImage": main_image,
            "gallery": [g for g in gallery if g],
            "categories": cat_slugs,
            "tags": product.get("tags", []),
            "sku": product.get("sku"),
            "url": product.get("product_url"),
            "ingredients": product.get("ingredients"),
            "allergens": product.get("allergens", []),
            "additionalInfo": [
                {"key": info.get("key"), "value": info.get("value")}
                for info in product.get("additional_information", [])
            ],
        }
        ui_products.append(ui_product)

    return {
        "products": ui_products,
        "categories": list(categories.values()),
        "meta": {
            "totalProducts": len(ui_products),
            "totalCategories": len(categories),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Export catalog for UI")
    parser.add_argument(
        "--input",
        default="out/catalog.jsonl",
        help="Input JSONL file from crawler",
    )
    parser.add_argument(
        "--output",
        default="ui/public/catalog.json",
        help="Output JSON file for UI",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        print("Run the crawler first: python -m catalog_crawler")
        return 1

    print(f"Loading products from {input_path}...")
    products = load_jsonl(input_path)
    print(f"Loaded {len(products)} products")

    print("Transforming for UI...")
    catalog = transform_for_ui(products)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        if args.pretty:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        else:
            json.dump(catalog, f, ensure_ascii=False)

    print(f"Saved {catalog['meta']['totalProducts']} products to {output_path}")
    print(f"Categories: {catalog['meta']['totalCategories']}")

    return 0


if __name__ == "__main__":
    exit(main())
