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
      id: "pb-001",
      slug: "black-kikkoman-tshirt",
      name: "Black Kikkoman T-shirt",
      price: 10.0,
      priceText: "$10.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "A stylish black T-shirt featuring the iconic Kikkoman design. Perfect for casual urban streetwear.",
      longDescription:
        "A stylish black T-shirt featuring the iconic Kikkoman design. Perfect for casual urban streetwear. Made from 100% cotton for all-day comfort.",
      mainImage: "https://static.pullandbear.net/2/photos//2021/I/0/2/p/8241/912/800/8241912800_4_1_8.jpg",
      gallery: [],
      categories: ["t-shirts"],
      tags: ["casual", "streetwear", "graphic"],
      sku: "PB-001",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "100% Cotton" }],
    },
    {
      id: "pb-007",
      slug: "money-heist-tshirt-black",
      name: "Black Money Heist x Pull&Bear T-shirt",
      price: 30.0,
      priceText: "$30.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Limited edition collaboration T-shirt from Money Heist x Pull&Bear collection. Iconic design.",
      longDescription:
        "Limited edition collaboration T-shirt from Money Heist x Pull&Bear collection. Iconic design featuring the famous red suit motif. A must-have for fans of the hit Netflix series.",
      mainImage: "https://static.pullandbear.net/2/photos//2021/I/0/2/p/8240/976/305/8240976305_4_1_8.jpg",
      gallery: [],
      categories: ["t-shirts"],
      tags: ["collaboration", "limited", "netflix"],
      sku: "PB-007",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "100% Cotton" }],
    },
    {
      id: "pb-011",
      slug: "metallica-justice-tshirt",
      name: "Metallica And Justice for All T-shirt",
      price: 40.0,
      priceText: "$40.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Official Metallica band T-shirt featuring 'And Justice for All' album artwork. A must for metal fans.",
      longDescription:
        "Official Metallica band T-shirt featuring the iconic 'And Justice for All' album artwork. Premium quality print on soft cotton. A must-have for metal fans and music lovers.",
      mainImage: "https://static.pullandbear.net/2/photos//2021/I/0/2/p/8241/581/800/8241581800_4_1_8.jpg",
      gallery: [],
      categories: ["t-shirts"],
      tags: ["band", "music", "metal"],
      sku: "PB-011",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "100% Cotton" }],
    },
    {
      id: "pb-020",
      slug: "premium-oversize-hoodie",
      name: "Premium fabric oversize hoodie",
      price: 15.0,
      priceText: "$15.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Oversized hoodie crafted from premium fabric. Relaxed fit for maximum comfort and style.",
      longDescription:
        "Oversized hoodie crafted from premium fabric. Features a relaxed fit for maximum comfort and style. Perfect for layering or wearing on its own.",
      mainImage: "https://static.pullandbear.net/2/photos//2021/I/0/2/p/8591/541/711/8591541711_2_6_8.jpg",
      gallery: [],
      categories: ["hoodies"],
      tags: ["oversized", "premium", "comfort"],
      sku: "PB-020",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "Cotton Blend" }],
    },
    {
      id: "pb-027",
      slug: "black-hoodie-classic",
      name: "Black hoodie classic",
      price: 26.0,
      priceText: "$26.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Timeless black hoodie for any occasion. A wardrobe staple that never goes out of style.",
      longDescription:
        "Timeless black hoodie for any occasion. Features a classic cut with ribbed cuffs and hem. A wardrobe staple that never goes out of style.",
      mainImage: "https://static.pullandbear.net/2/photos//2021/I/0/2/p/8591/515/800/8591515800_1_1_8.jpg",
      gallery: [],
      categories: ["hoodies"],
      tags: ["black", "classic", "essential"],
      sku: "PB-027",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "Cotton Blend" }],
    },
    {
      id: "pb-030",
      slug: "parka-nylon-details",
      name: "Parka with nylon details",
      price: 80.0,
      priceText: "$80.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Premium parka with stylish nylon accents. Perfect for cold weather with urban style.",
      longDescription:
        "Premium parka featuring stylish nylon accents and a warm lining. Perfect for cold weather while maintaining urban style. Multiple pockets for practicality.",
      mainImage: "https://static.pullandbear.net/2/photos//2021/I/0/2/p/4751/501/800/4751501800_4_1_8.jpg",
      gallery: [],
      categories: ["jackets"],
      tags: ["parka", "winter", "premium"],
      sku: "PB-030",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "Polyester/Nylon" }],
    },
    {
      id: "pb-032",
      slug: "dark-blue-denim-jacket",
      name: "Dark blue denim jacket",
      price: 30.0,
      priceText: "$30.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Classic dark blue denim jacket. A timeless piece that works with any outfit.",
      longDescription:
        "Classic dark blue denim jacket with a timeless design. Features front button closure and chest pockets. Works perfectly with any casual outfit.",
      mainImage: "https://static.pullandbear.net/2/photos//2021/I/0/2/p/8711/527/407/8711527407_4_1_8.jpg",
      gallery: [],
      categories: ["jackets"],
      tags: ["denim", "classic", "blue"],
      sku: "PB-032",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "100% Cotton Denim" }],
    },
    {
      id: "pb-040",
      slug: "blue-faded-jeans",
      name: "Blue Faded standard fit jeans",
      price: 25.0,
      priceText: "$25.00",
      currency: "$",
      inStock: true,
      stockText: "In stock",
      shortDescription:
        "Classic blue faded jeans in standard fit. The perfect everyday denim.",
      longDescription:
        "Classic blue faded jeans in a comfortable standard fit. Features a traditional five-pocket design. The perfect everyday denim for any occasion.",
      mainImage: "https://static.pullandbear.net/2/photos//2021/I/0/2/p/8676/519/800/8676519800_4_1_8.jpg",
      gallery: [],
      categories: ["trousers"],
      tags: ["denim", "jeans", "blue"],
      sku: "PB-040",
      url: null,
      ingredients: null,
      allergens: [],
      additionalInfo: [{ key: "Material", value: "Cotton Denim" }],
    },
  ];

  const demoCategories: Category[] = [
    { name: "T-Shirts", slug: "t-shirts" },
    { name: "Hoodies", slug: "hoodies" },
    { name: "Jackets", slug: "jackets" },
    { name: "Trousers", slug: "trousers" },
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
