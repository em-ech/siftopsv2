/**
 * Client-side data loading utilities
 * Fetches catalog via HTTP or uses demo data
 */

import type { Catalog, Product, Category } from "./types";

// Client-side catalog cache
let clientCatalogCache: Catalog | null = null;

/**
 * Get catalog data via fetch (works on client-side)
 */
export async function getCatalog(): Promise<Catalog> {
  if (clientCatalogCache) {
    return clientCatalogCache;
  }

  try {
    const response = await fetch("/catalog.json");
    if (!response.ok) {
      throw new Error("Catalog not found");
    }
    clientCatalogCache = await response.json();
    return clientCatalogCache!;
  } catch {
    return getDemoCatalog();
  }
}

export async function getProducts(): Promise<Product[]> {
  const catalog = await getCatalog();
  return catalog.products;
}

export async function getCategories(): Promise<Category[]> {
  const catalog = await getCatalog();
  return catalog.categories;
}

export async function getProductBySlug(slug: string): Promise<Product | null> {
  const catalog = await getCatalog();
  return catalog.products.find((p) => p.slug === slug) || null;
}

export async function getProductsByCategory(
  categorySlug: string
): Promise<Product[]> {
  const catalog = await getCatalog();
  return catalog.products.filter((p) => p.categories.includes(categorySlug));
}

export async function searchProducts(query: string): Promise<Product[]> {
  const catalog = await getCatalog();
  const lowerQuery = query.toLowerCase();

  return catalog.products.filter(
    (p) =>
      p.name.toLowerCase().includes(lowerQuery) ||
      p.shortDescription?.toLowerCase().includes(lowerQuery) ||
      p.tags.some((t) => t.toLowerCase().includes(lowerQuery))
  );
}

export async function getFeaturedProducts(limit = 8): Promise<Product[]> {
  const catalog = await getCatalog();
  return catalog.products.slice(0, limit);
}

// Demo catalog for development when no crawled data exists
function getDemoCatalog(): Catalog {
  const demoProducts: Product[] = [
    {
      id: "honeycomb",
      slug: "honeycomb",
      name: "Honeycomb",
      price: 12.0,
      priceText: "$12.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Rich and creamy vanilla ice cream studded with crunchy honeycomb toffee pieces.",
      longDescription:
        "Our honeycomb ice cream is made with fresh cream and pure honey from local apiaries. Each pint is packed with crunchy honeycomb toffee pieces.",
      mainImage: "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=600",
      gallery: [],
      categories: ["pints", "classics"],
      tags: ["vanilla", "honeycomb", "sweet"],
      sku: "VL-HC-001",
      url: null,
      ingredients: "Cream, Sugar, Honey, Egg Yolks, Honeycomb Toffee",
      allergens: ["Milk", "Eggs"],
      additionalInfo: [{ key: "Weight", value: "14 oz" }],
    },
    {
      id: "sicilian-pistachio",
      slug: "sicilian-pistachio",
      name: "Sicilian Pistachio",
      price: 14.0,
      priceText: "$14.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Authentic pistachio ice cream made with pistachios imported directly from Sicily.",
      longDescription:
        "Naturally green with an intense nutty flavor that comes from the finest Sicilian pistachios.",
      mainImage: "https://images.unsplash.com/photo-1560008581-09826d1de69e?w=600",
      gallery: [],
      categories: ["pints", "classics"],
      tags: ["pistachio", "nutty", "premium"],
      sku: "VL-SP-002",
      url: null,
      ingredients: "Cream, Sugar, Sicilian Pistachios, Egg Yolks",
      allergens: ["Milk", "Eggs", "Tree Nuts"],
      additionalInfo: [{ key: "Weight", value: "14 oz" }],
    },
    {
      id: "vegan-chocolate",
      slug: "vegan-chocolate",
      name: "Vegan Chocolate",
      price: 12.0,
      priceText: "$12.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Rich, dark chocolate ice cream made entirely plant-based with oat milk.",
      longDescription:
        "Indulgent chocolate flavor without any dairy. Made with premium cocoa and creamy oat milk base.",
      mainImage: "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=600",
      gallery: [],
      categories: ["vegan", "pints"],
      tags: ["vegan", "chocolate", "dairy-free"],
      sku: "VL-VC-003",
      url: null,
      ingredients: "Oat Milk, Sugar, Cocoa, Coconut Oil",
      allergens: ["Oats"],
      additionalInfo: [{ key: "Weight", value: "14 oz" }],
    },
    {
      id: "earl-grey",
      slug: "earl-grey",
      name: "Earl Grey Tea",
      price: 12.0,
      priceText: "$12.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Delicate Earl Grey tea-infused ice cream with hints of bergamot.",
      longDescription:
        "A sophisticated flavor for tea lovers. Infused with real Earl Grey tea leaves.",
      mainImage: "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=600",
      gallery: [],
      categories: ["pints", "classics"],
      tags: ["tea", "bergamot", "sophisticated"],
      sku: "VL-EG-004",
      url: null,
      ingredients: "Cream, Sugar, Earl Grey Tea, Egg Yolks",
      allergens: ["Milk", "Eggs"],
      additionalInfo: [{ key: "Weight", value: "14 oz" }],
    },
    {
      id: "mango-sorbet",
      slug: "mango-sorbet",
      name: "Mango Sorbet",
      price: 10.0,
      priceText: "$10.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Refreshing dairy-free mango sorbet made with ripe Alphonso mangoes.",
      longDescription:
        "Light and tropical. Made with the king of mangoes - the Alphonso variety from India.",
      mainImage: "https://images.unsplash.com/photo-1488900128323-21503983a07e?w=600",
      gallery: [],
      categories: ["sorbet", "vegan"],
      tags: ["mango", "tropical", "dairy-free", "refreshing"],
      sku: "VL-MS-005",
      url: null,
      ingredients: "Mango Puree, Sugar, Water, Lemon Juice",
      allergens: [],
      additionalInfo: [{ key: "Weight", value: "14 oz" }],
    },
    {
      id: "salted-caramel",
      slug: "salted-caramel",
      name: "Salted Caramel",
      price: 12.0,
      priceText: "$12.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Buttery caramel ice cream with swirls of sea salt caramel sauce.",
      longDescription:
        "The perfect balance of sweet and salty. Handmade caramel swirled throughout.",
      mainImage: "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?w=600",
      gallery: [],
      categories: ["pints", "classics"],
      tags: ["caramel", "salty", "sweet"],
      sku: "VL-SC-006",
      url: null,
      ingredients: "Cream, Sugar, Caramel, Sea Salt, Egg Yolks",
      allergens: ["Milk", "Eggs"],
      additionalInfo: [{ key: "Weight", value: "14 oz" }],
    },
  ];

  const demoCategories: Category[] = [
    { name: "Pints", slug: "pints" },
    { name: "Vegan", slug: "vegan" },
    { name: "Sorbet", slug: "sorbet" },
    { name: "Classics", slug: "classics" },
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
