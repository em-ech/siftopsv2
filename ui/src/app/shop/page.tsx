"use client";

import { Suspense, useState, useEffect, useMemo, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import {
  ProductGrid,
  SearchModeToggle,
  ChatPanel,
  SiftSearchResults,
  type SearchMode,
} from "@/components";
import { getProducts, getCategories } from "@/lib/data";
import { siftSearch, checkBackendHealth, type SiftSearchResult } from "@/lib/api";
import type { Product, Category, SortOption } from "@/lib/types";

function ShopPageContent() {
  const searchParams = useSearchParams();
  const categoryParam = searchParams.get("category");

  // Data state
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  // Search mode state
  const [searchMode, setSearchMode] = useState<SearchMode>("regular");
  const [backendAvailable, setBackendAvailable] = useState<boolean | null>(null);

  // Filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    categoryParam
  );
  const [sortBy, setSortBy] = useState<SortOption>("name");

  // Sift search state
  const [siftResults, setSiftResults] = useState<SiftSearchResult[]>([]);
  const [siftLoading, setSiftLoading] = useState(false);
  const [lastSiftQuery, setLastSiftQuery] = useState("");

  // Load initial data
  useEffect(() => {
    async function loadData() {
      const [productsData, categoriesData] = await Promise.all([
        getProducts(),
        getCategories(),
      ]);
      setProducts(productsData);
      setCategories(categoriesData);
      setLoading(false);
    }
    loadData();
  }, []);

  // Check backend availability
  useEffect(() => {
    async function checkBackend() {
      const available = await checkBackendHealth();
      setBackendAvailable(available);
    }
    checkBackend();
  }, []);

  // Update selected category from URL
  useEffect(() => {
    setSelectedCategory(categoryParam);
  }, [categoryParam]);

  // Debounced Sift search
  useEffect(() => {
    if (searchMode !== "sift" || !searchQuery.trim()) {
      setSiftResults([]);
      setLastSiftQuery("");
      return;
    }

    const timeoutId = setTimeout(async () => {
      if (searchQuery === lastSiftQuery) return;

      setSiftLoading(true);
      try {
        const response = await siftSearch(searchQuery, 12);
        setSiftResults(response.results);
        setLastSiftQuery(searchQuery);
      } catch (error) {
        console.error("Sift search error:", error);
        setSiftResults([]);
      } finally {
        setSiftLoading(false);
      }
    }, 500); // 500ms debounce

    return () => clearTimeout(timeoutId);
  }, [searchQuery, searchMode, lastSiftQuery]);

  // Regular filter and sort
  const filteredProducts = useMemo(() => {
    if (searchMode !== "regular") return products;

    let result = [...products];

    // Filter by search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(query) ||
          p.shortDescription?.toLowerCase().includes(query) ||
          p.tags.some((t) => t.toLowerCase().includes(query))
      );
    }

    // Filter by category
    if (selectedCategory) {
      result = result.filter((p) => p.categories.includes(selectedCategory));
    }

    // Sort
    switch (sortBy) {
      case "name":
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case "price-asc":
        result.sort((a, b) => (a.price || 0) - (b.price || 0));
        break;
      case "price-desc":
        result.sort((a, b) => (b.price || 0) - (a.price || 0));
        break;
      case "newest":
        break;
    }

    return result;
  }, [products, searchQuery, selectedCategory, sortBy, searchMode]);

  // Handle search mode change
  const handleModeChange = useCallback((mode: SearchMode) => {
    setSearchMode(mode);
    // Clear search when switching to chat
    if (mode === "chat") {
      setSearchQuery("");
    }
  }, []);

  // Handle chat products found
  const handleChatProductsFound = useCallback((foundProducts: SiftSearchResult[]) => {
    // Could potentially show these products alongside chat
    console.log("Products found via chat:", foundProducts);
  }, []);

  if (loading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="text-[var(--color-text-muted)]">Loading...</div>
      </div>
    );
  }

  return (
    <div className="py-8 sm:py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8 sm:mb-12">
          <h1 className="text-3xl sm:text-4xl font-serif mb-4">
            {searchMode === "chat"
              ? "Ask About Our Products"
              : selectedCategory
              ? categories.find((c) => c.slug === selectedCategory)?.name ||
                "Shop"
              : "Shop All"}
          </h1>
          {searchMode !== "chat" && (
            <p className="text-[var(--color-text-muted)]">
              {searchMode === "sift" && siftResults.length > 0
                ? `${siftResults.length} AI-matched products`
                : `${filteredProducts.length} product${
                    filteredProducts.length !== 1 ? "s" : ""
                  }`}
            </p>
          )}
        </div>

        {/* Search Mode Toggle + Backend Status */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8 pb-6 border-b border-[var(--color-border)]">
          <SearchModeToggle
            mode={searchMode}
            onChange={handleModeChange}
            disabled={backendAvailable === false && searchMode === "regular"}
          />

          {/* Backend Status */}
          <div className="flex items-center gap-2 text-sm">
            <span
              className={`w-2 h-2 rounded-full ${
                backendAvailable === true
                  ? "bg-green-500"
                  : backendAvailable === false
                  ? "bg-red-500"
                  : "bg-yellow-500 animate-pulse"
              }`}
            />
            <span className="text-[var(--color-text-muted)]">
              {backendAvailable === true
                ? "Sift AI Connected"
                : backendAvailable === false
                ? "Backend Offline"
                : "Checking connection..."}
            </span>
          </div>
        </div>

        {/* Backend Offline Warning */}
        {backendAvailable === false && searchMode !== "regular" && (
          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-start gap-3">
              <svg
                className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <div>
                <h3 className="font-medium text-amber-800">
                  Backend Server Not Running
                </h3>
                <p className="text-sm text-amber-700 mt-1">
                  Start the Sift AI backend to use {searchMode === "sift" ? "semantic search" : "chat"} features:
                </p>
                <code className="block mt-2 text-xs bg-amber-100 px-3 py-2 rounded font-mono">
                  cd backend && uv run uvicorn app.main:app --reload --port 8000
                </code>
              </div>
            </div>
          </div>
        )}

        {/* Chat Mode */}
        {searchMode === "chat" && (
          <div className="max-w-2xl mx-auto">
            <ChatPanel onProductsFound={handleChatProductsFound} />
          </div>
        )}

        {/* Search Modes (Regular & Sift) */}
        {searchMode !== "chat" && (
          <>
            {/* Filters Bar */}
            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <input
                    type="text"
                    placeholder={
                      searchMode === "sift"
                        ? "Describe what you're looking for... (e.g., 'something refreshing for summer')"
                        : "Search products..."
                    }
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-[var(--color-border)] focus:border-[var(--color-primary)] focus:outline-none transition-colors"
                  />
                  <svg
                    className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--color-text-light)]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    {searchMode === "sift" ? (
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                      />
                    ) : (
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                      />
                    )}
                  </svg>
                  {searchMode === "sift" && siftLoading && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      <div className="w-5 h-5 border-2 border-[var(--color-accent)] border-t-transparent rounded-full animate-spin" />
                    </div>
                  )}
                </div>
              </div>

              {/* Category Filter - Only for regular search */}
              {searchMode === "regular" && (
                <div className="sm:w-48">
                  <select
                    value={selectedCategory || ""}
                    onChange={(e) => setSelectedCategory(e.target.value || null)}
                    className="w-full px-4 py-3 border border-[var(--color-border)] focus:border-[var(--color-primary)] focus:outline-none bg-white transition-colors appearance-none cursor-pointer"
                  >
                    <option value="">All Categories</option>
                    {categories.map((cat) => (
                      <option key={cat.slug} value={cat.slug}>
                        {cat.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Sort - Only for regular search */}
              {searchMode === "regular" && (
                <div className="sm:w-48">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as SortOption)}
                    className="w-full px-4 py-3 border border-[var(--color-border)] focus:border-[var(--color-primary)] focus:outline-none bg-white transition-colors appearance-none cursor-pointer"
                  >
                    <option value="name">Name A-Z</option>
                    <option value="price-asc">Price: Low to High</option>
                    <option value="price-desc">Price: High to Low</option>
                    <option value="newest">Newest</option>
                  </select>
                </div>
              )}
            </div>

            {/* Active Filters - Regular mode only */}
            {searchMode === "regular" && (searchQuery || selectedCategory) && (
              <div className="flex flex-wrap gap-2 mb-8">
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery("")}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-[var(--color-background-alt)] text-sm hover:bg-[var(--color-border)] transition-colors"
                  >
                    Search: {searchQuery}
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                    </svg>
                  </button>
                )}
                {selectedCategory && (
                  <button
                    onClick={() => setSelectedCategory(null)}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-[var(--color-background-alt)] text-sm hover:bg-[var(--color-border)] transition-colors"
                  >
                    {categories.find((c) => c.slug === selectedCategory)?.name}
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                    </svg>
                  </button>
                )}
                <button
                  onClick={() => {
                    setSearchQuery("");
                    setSelectedCategory(null);
                  }}
                  className="text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
                >
                  Clear all
                </button>
              </div>
            )}

            {/* Results */}
            {searchMode === "sift" ? (
              <SiftSearchResults
                results={siftResults}
                query={searchQuery}
                isLoading={siftLoading && searchQuery.length > 0}
              />
            ) : (
              <ProductGrid
                products={filteredProducts}
                emptyMessage={
                  searchQuery || selectedCategory
                    ? "No products match your filters. Try adjusting your search."
                    : "No products available."
                }
              />
            )}
          </>
        )}

        {/* Mode Description */}
        <div className="mt-16 pt-8 border-t border-[var(--color-border)]">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div
              className={`p-6 rounded-lg ${
                searchMode === "regular"
                  ? "bg-[var(--color-background-alt)]"
                  : ""
              }`}
            >
              <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[var(--color-background-alt)] flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-[var(--color-text-muted)]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
              <h3 className="font-serif text-lg mb-2">Regular Search</h3>
              <p className="text-sm text-[var(--color-text-muted)]">
                Traditional keyword matching. Search by product name, description, or
                tags.
              </p>
            </div>
            <div
              className={`p-6 rounded-lg ${
                searchMode === "sift" ? "bg-[var(--color-background-alt)]" : ""
              }`}
            >
              <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[var(--color-accent)]/10 flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-[var(--color-accent)]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
              <h3 className="font-serif text-lg mb-2">Sift AI Search</h3>
              <p className="text-sm text-[var(--color-text-muted)]">
                Semantic search powered by AI. Understands intent like "something
                refreshing" or "best for parties".
              </p>
            </div>
            <div
              className={`p-6 rounded-lg ${
                searchMode === "chat" ? "bg-[var(--color-background-alt)]" : ""
              }`}
            >
              <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[var(--color-accent)]/10 flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-[var(--color-accent)]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
              </div>
              <h3 className="font-serif text-lg mb-2">AI Chat</h3>
              <p className="text-sm text-[var(--color-text-muted)]">
                Conversational assistant with RAG. Ask questions and get
                personalized recommendations.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ShopPageLoading() {
  return (
    <div className="min-h-[50vh] flex items-center justify-center">
      <div className="text-[var(--color-text-muted)]">Loading shop...</div>
    </div>
  );
}

export default function ShopPage() {
  return (
    <Suspense fallback={<ShopPageLoading />}>
      <ShopPageContent />
    </Suspense>
  );
}
