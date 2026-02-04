/**
 * Type definitions for the catalog data
 */

export interface Product {
  id: string;
  slug: string;
  name: string;
  price: number | null;
  priceText: string | null;
  currency: string;
  inStock: boolean;
  stockText: string | null;
  shortDescription: string | null;
  longDescription: string | null;
  mainImage: string | null;
  gallery: string[];
  categories: string[];
  tags: string[];
  sku: string | null;
  url: string | null;
  ingredients: string | null;
  allergens: string[];
  additionalInfo: AdditionalInfo[];
}

export interface AdditionalInfo {
  key: string;
  value: string;
}

export interface Category {
  name: string;
  slug: string;
  url?: string;
}

export interface Catalog {
  products: Product[];
  categories: Category[];
  meta: {
    totalProducts: number;
    totalCategories: number;
  };
}

export type SortOption = "name" | "price-asc" | "price-desc" | "newest";
