/**
 * Maps Supabase database rows to frontend types
 */

import type { Product, Category } from "./types";

/**
 * Map a Supabase products table row to the frontend Product type
 */
export function mapDbProductToProduct(row: Record<string, unknown>): Product {
  const price = row.price != null ? Number(row.price) : null;
  const currency = (row.currency as string) || "$";

  return {
    id: (row.external_id as string) || (row.id as string),
    slug: (row.slug as string) || "",
    name: (row.name as string) || "",
    price,
    priceText: price != null ? `${currency}${price.toFixed(2)}` : null,
    currency,
    inStock: (row.stock_status as string) === "instock",
    stockText:
      (row.stock_status as string) === "instock" ? "In stock" : "Out of stock",
    shortDescription: (row.short_description as string) || null,
    longDescription: (row.description as string) || null,
    mainImage: (row.image_url as string) || null,
    gallery: (row.gallery_urls as string[]) || [],
    categories: (row.categories as string[]) || [],
    tags: (row.tags as string[]) || [],
    sku: (row.sku as string) || null,
    url: (row.permalink as string) || null,
    ingredients: null,
    allergens: [],
    additionalInfo: buildAdditionalInfo(row),
  };
}

function buildAdditionalInfo(
  row: Record<string, unknown>
): { key: string; value: string }[] {
  const info: { key: string; value: string }[] = [];

  if (row.brand) {
    info.push({ key: "Brand", value: row.brand as string });
  }
  if (row.sku) {
    info.push({ key: "SKU", value: row.sku as string });
  }

  return info;
}

/**
 * Extract unique categories from a list of products
 */
export function extractCategories(
  products: Record<string, unknown>[]
): Category[] {
  const categorySet = new Set<string>();

  for (const product of products) {
    const categories = (product.categories as string[]) || [];
    for (const cat of categories) {
      categorySet.add(cat);
    }
  }

  return Array.from(categorySet)
    .sort()
    .map((slug) => ({
      name: formatCategoryName(slug),
      slug,
    }));
}

const CATEGORY_NAMES: Record<string, string> = {
  "t-shirts": "T-Shirts",
  hoodies: "Hoodies & Sweatshirts",
  jackets: "Jackets & Coats",
  trousers: "Trousers & Jeans",
};

function formatCategoryName(slug: string): string {
  return (
    CATEGORY_NAMES[slug] ||
    slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
  );
}
