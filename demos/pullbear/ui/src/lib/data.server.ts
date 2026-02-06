/**
 * Server-side data loading utilities
 * Direct Supabase queries for server components (no HTTP round-trip)
 * Falls back to static catalog.json if Supabase unavailable
 */

import type { Catalog, Product, Category } from "./types";
import { getSupabaseServer } from "./supabase";
import { mapDbProductToProduct, extractCategories } from "./mappers";
import fs from "fs";
import path from "path";

const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || "pullbear";

// Server-side catalog cache for static fallback
let staticCatalogCache: Catalog | null = null;

/**
 * Get all products from Supabase
 */
export async function getProducts(): Promise<Product[]> {
  const supabase = getSupabaseServer();

  if (supabase) {
    try {
      const { data, error } = await supabase
        .from("products")
        .select("*")
        .eq("tenant_id", TENANT_ID)
        .order("name", { ascending: true })
        .limit(100);

      if (!error && data && data.length > 0) {
        return data.map(mapDbProductToProduct);
      }
    } catch (err) {
      console.warn("Supabase query failed, using static fallback:", err);
    }
  }

  return getStaticCatalog().products;
}

/**
 * Get categories derived from products
 */
export async function getCategories(): Promise<Category[]> {
  const supabase = getSupabaseServer();

  if (supabase) {
    try {
      const { data, error } = await supabase
        .from("products")
        .select("categories")
        .eq("tenant_id", TENANT_ID);

      if (!error && data && data.length > 0) {
        return extractCategories(data);
      }
    } catch (err) {
      console.warn("Supabase categories query failed:", err);
    }
  }

  return getStaticCatalog().categories;
}

/**
 * Get a single product by slug
 */
export async function getProductBySlug(slug: string): Promise<Product | null> {
  const supabase = getSupabaseServer();

  if (supabase) {
    try {
      const { data, error } = await supabase
        .from("products")
        .select("*")
        .eq("tenant_id", TENANT_ID)
        .eq("slug", slug)
        .single();

      if (!error && data) {
        return mapDbProductToProduct(data);
      }
    } catch (err) {
      console.warn("Supabase product query failed:", err);
    }
  }

  const catalog = getStaticCatalog();
  return catalog.products.find((p) => p.slug === slug) || null;
}

/**
 * Get products by category
 */
export async function getProductsByCategory(
  categorySlug: string
): Promise<Product[]> {
  const supabase = getSupabaseServer();

  if (supabase) {
    try {
      const { data, error } = await supabase
        .from("products")
        .select("*")
        .eq("tenant_id", TENANT_ID)
        .contains("categories", [categorySlug])
        .order("name", { ascending: true });

      if (!error && data && data.length > 0) {
        return data.map(mapDbProductToProduct);
      }
    } catch (err) {
      console.warn("Supabase category query failed:", err);
    }
  }

  const catalog = getStaticCatalog();
  return catalog.products.filter((p) => p.categories.includes(categorySlug));
}

/**
 * Get featured products (first N)
 */
export async function getFeaturedProducts(limit = 8): Promise<Product[]> {
  const supabase = getSupabaseServer();

  if (supabase) {
    try {
      const { data, error } = await supabase
        .from("products")
        .select("*")
        .eq("tenant_id", TENANT_ID)
        .limit(limit);

      if (!error && data && data.length > 0) {
        return data.map(mapDbProductToProduct);
      }
    } catch (err) {
      console.warn("Supabase featured query failed:", err);
    }
  }

  return getStaticCatalog().products.slice(0, limit);
}

// ========== Static fallback ==========

function getStaticCatalog(): Catalog {
  if (staticCatalogCache) return staticCatalogCache;

  try {
    const catalogPath = path.join(process.cwd(), "public", "catalog.json");
    if (fs.existsSync(catalogPath)) {
      const data = fs.readFileSync(catalogPath, "utf-8");
      staticCatalogCache = JSON.parse(data);
      return staticCatalogCache!;
    }
  } catch (error) {
    console.warn("Could not load catalog.json:", error);
  }

  return getDemoCatalog();
}

function getDemoCatalog(): Catalog {
  const demoProducts: Product[] = [
    {
      id: "pb-016",
      slug: "cowboy-bebop-sweatshirt",
      name: "Cowboy Bebop Sweatshirt",
      price: 49.99,
      priceText: "$49.99",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Cowboy Bebop graphic sweatshirt. A Pull & Bear essential.",
      longDescription: null,
      mainImage:
        "https://static.pullandbear.net/2/photos//2022/V/0/2/p/4590/517/600/4590517600_4_1_8.jpg",
      gallery: [],
      categories: ["t-shirts"],
      tags: ["casual", "streetwear", "graphic"],
      sku: "PB-016",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "100% Cotton" }],
    },
    {
      id: "pb-005",
      slug: "premium-oversize-hoodie",
      name: "Premium fabric oversize hoodie",
      price: 39.99,
      priceText: "$39.99",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Premium fabric oversize hoodie. Relaxed fit for maximum comfort.",
      longDescription: null,
      mainImage:
        "https://static.pullandbear.net/2/photos//2021/I/0/2/p/8591/541/711/8591541711_2_6_8.jpg",
      gallery: [],
      categories: ["hoodies"],
      tags: ["comfort", "layering", "oversized"],
      sku: "PB-005",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "Cotton Blend" }],
    },
    {
      id: "pb-021",
      slug: "quilted-bomber-jacket",
      name: "Quilted Bomber Jacket",
      price: 29.99,
      priceText: "$29.99",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Quilted bomber jacket. Essential outerwear from Pull & Bear.",
      longDescription: null,
      mainImage:
        "https://static.pullandbear.net/2/photos//2022/V/0/2/p/8711/507/737/8711507737_4_1_8.jpg",
      gallery: [],
      categories: ["jackets"],
      tags: ["outerwear", "bomber"],
      sku: "PB-021",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "Polyester/Nylon" }],
    },
    {
      id: "pb-080",
      slug: "blue-faded-standard-fit-jeans",
      name: "Blue Faded Standard Fit Jeans",
      price: 25.0,
      priceText: "$25.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Blue faded standard fit jeans. The perfect everyday denim.",
      longDescription: null,
      mainImage:
        "https://static.pullandbear.net/2/photos//2021/I/0/2/p/8676/519/800/8676519800_4_1_8.jpg",
      gallery: [],
      categories: ["trousers"],
      tags: ["bottoms", "denim"],
      sku: "PB-080",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "Cotton Denim" }],
    },
  ];

  const demoCategories: Category[] = [
    { name: "T-Shirts", slug: "t-shirts" },
    { name: "Hoodies & Sweatshirts", slug: "hoodies" },
    { name: "Jackets & Coats", slug: "jackets" },
    { name: "Trousers & Jeans", slug: "trousers" },
  ];

  return {
    products: demoProducts,
    categories: demoCategories,
    meta: {
      totalProducts: demoProducts.length,
      totalCategories: demoCategories.length,
    },
  };
}
