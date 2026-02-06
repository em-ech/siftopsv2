/**
 * Client-side data loading utilities
 * Fetches from Next.js API routes (backed by Supabase)
 * Falls back to static catalog.json if API unavailable
 */

import type { Catalog, Product, Category } from "./types";

// Client-side cache
let productsCache: Product[] | null = null;
let categoriesCache: Category[] | null = null;

/**
 * Fetch all products from the API
 */
export async function getProducts(
  options: {
    category?: string | null;
    sort?: string;
    limit?: number;
    q?: string;
  } = {}
): Promise<Product[]> {
  const params = new URLSearchParams();
  if (options.category) params.set("category", options.category);
  if (options.sort) params.set("sort", options.sort);
  if (options.limit) params.set("limit", String(options.limit));
  if (options.q) params.set("q", options.q);

  const qs = params.toString();

  try {
    const response = await fetch(`/api/products${qs ? `?${qs}` : ""}`);
    if (!response.ok) throw new Error("API error");
    const data = await response.json();
    const products = data.products || [];

    // Cache the unfiltered full list
    if (!options.category && !options.q && !options.sort) {
      productsCache = products;
    }
    return products;
  } catch {
    return getStaticProducts();
  }
}

/**
 * Fetch categories from the API
 */
export async function getCategories(): Promise<Category[]> {
  if (categoriesCache) return categoriesCache;

  try {
    const response = await fetch("/api/categories");
    if (!response.ok) throw new Error("API error");
    const data = await response.json();
    categoriesCache = data.categories || [];
    return categoriesCache!;
  } catch {
    return getStaticCategories();
  }
}

/**
 * Fetch a single product by slug
 */
export async function getProductBySlug(
  slug: string
): Promise<Product | null> {
  try {
    const response = await fetch(`/api/products/${slug}`);
    if (!response.ok) return null;
    const data = await response.json();
    return data.product || null;
  } catch {
    return getStaticProductBySlug(slug);
  }
}

/**
 * Search products by keyword
 */
export async function searchProducts(query: string): Promise<Product[]> {
  return getProducts({ q: query });
}

/**
 * Get featured products (first N)
 */
export async function getFeaturedProducts(limit = 8): Promise<Product[]> {
  return getProducts({ limit });
}

// ========== Static fallbacks ==========

let staticCatalogCache: Catalog | null = null;

async function loadStaticCatalog(): Promise<Catalog> {
  if (staticCatalogCache) return staticCatalogCache;

  try {
    const response = await fetch("/catalog.json");
    if (!response.ok) throw new Error("Not found");
    staticCatalogCache = await response.json();
    return staticCatalogCache!;
  } catch {
    return getDemoCatalog();
  }
}

async function getStaticProducts(): Promise<Product[]> {
  const catalog = await loadStaticCatalog();
  return catalog.products;
}

async function getStaticCategories(): Promise<Category[]> {
  const catalog = await loadStaticCatalog();
  return catalog.categories;
}

async function getStaticProductBySlug(slug: string): Promise<Product | null> {
  const catalog = await loadStaticCatalog();
  return catalog.products.find((p) => p.slug === slug) || null;
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
