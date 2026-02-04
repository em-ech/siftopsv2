"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { ProductCard } from "@/components/ProductCard";
import { ChatWidget } from "@/components/ChatWidget";
import { searchProducts, type Product } from "@/lib/api";

const TENANT_ID = "vanleeuwen";
const STORE_NAME = "Van Leeuwen Ice Cream";

export default function ShopDemoPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Demo products when no search
  const [demoProducts] = useState<Product[]>([
    {
      product_id: "1",
      name: "Honeycomb Ice Cream",
      price: "12.00",
      description: "Creamy vanilla ice cream with honeycomb pieces",
      image_url: null,
      permalink: "#",
      categories: ["Ice Cream", "Pints"],
      stock_status: "instock",
    },
    {
      product_id: "2",
      name: "Sicilian Pistachio",
      price: "14.00",
      description: "Made with authentic Sicilian pistachios",
      image_url: null,
      permalink: "#",
      categories: ["Ice Cream", "Pints"],
      stock_status: "instock",
    },
    {
      product_id: "3",
      name: "Vegan Chocolate Chip Cookie Dough",
      price: "12.00",
      description: "Dairy-free chocolate chip cookie dough ice cream",
      image_url: null,
      permalink: "#",
      categories: ["Vegan", "Ice Cream"],
      stock_status: "instock",
    },
  ]);

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setProducts([]);
      return;
    }

    setIsSearching(true);
    try {
      const result = await searchProducts(query, TENANT_ID, 10);
      setProducts(result.results);
    } catch (error) {
      console.error("Search failed:", error);
      setProducts([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      handleSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const displayProducts = products.length > 0 ? products : demoProducts;

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">{STORE_NAME}</h1>
          <nav className="flex gap-6 text-sm">
            <a href="#" className="hover:underline">Shop</a>
            <a href="#" className="hover:underline">About</a>
            <a href="#" className="hover:underline">Locations</a>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="bg-yellow-50 py-16">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">Artisan Ice Cream</h2>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Handcrafted in small batches using the finest ingredients from around the world.
          </p>

          {/* Semantic Search Bar */}
          <div className="max-w-xl mx-auto">
            <Input
              type="search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Try: 'something refreshing for summer' or 'vegan chocolate'"
              className="text-lg py-6"
            />
            <p className="text-sm text-gray-500 mt-2">
              Powered by Sift AI - Search by meaning, not just keywords
            </p>
          </div>
        </div>
      </section>

      {/* Products */}
      <section className="py-12">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center mb-8">
            <h3 className="text-2xl font-bold">
              {searchQuery ? `Results for "${searchQuery}"` : "Featured Products"}
            </h3>
            {isSearching && (
              <span className="text-gray-500">Searching...</span>
            )}
          </div>

          {displayProducts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {displayProducts.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>No products found for your search.</p>
              <p className="text-sm mt-2">Try asking our AI assistant for help!</p>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <p className="text-sm text-gray-400">
            Demo store powered by Sift Retail AI
          </p>
        </div>
      </footer>

      {/* Chat Widget */}
      <ChatWidget
        tenantId={TENANT_ID}
        storeName={STORE_NAME}
        primaryColor="#1a1a1a"
      />
    </div>
  );
}
