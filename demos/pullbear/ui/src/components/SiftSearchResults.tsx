"use client";

import Image from "next/image";
import Link from "next/link";
import type { SiftSearchResult } from "@/lib/api";

interface SiftSearchResultsProps {
  results: SiftSearchResult[];
  query: string;
  isLoading?: boolean;
}

export function SiftSearchResults({
  results,
  query,
  isLoading = false,
}: SiftSearchResultsProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="relative w-16 h-16 mb-4">
          <div className="absolute inset-0 border-4 border-[var(--color-border)] rounded-full" />
          <div className="absolute inset-0 border-4 border-[var(--color-accent)] rounded-full border-t-transparent animate-spin" />
        </div>
        <p className="text-[var(--color-text-muted)]">
          Searching with AI for "{query}"...
        </p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="w-16 h-16 mx-auto mb-4 text-[var(--color-text-light)]">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1}
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-serif mb-2">No matches found</h3>
        <p className="text-[var(--color-text-muted)]">
          Try a different search term or browse all products
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="flex items-center justify-between pb-4 border-b border-[var(--color-border)]">
        <div>
          <h2 className="text-lg font-serif">AI Search Results</h2>
          <p className="text-sm text-[var(--color-text-muted)]">
            Found {results.length} semantically matching products for "{query}"
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-[var(--color-accent)]">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
          </svg>
          Powered by Sift AI
        </div>
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {results.map((result, index) => (
          <Link
            key={`${result.id}-${index}`}
            href={`/product/${result.id}`}
            className="group flex gap-4 p-4 bg-white border border-[var(--color-border)] rounded-lg hover:border-[var(--color-accent)] hover:shadow-md transition-all"
          >
            {/* Rank Badge */}
            <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-[var(--color-background-alt)] rounded-full text-sm font-medium">
              {index + 1}
            </div>

            {/* Image */}
            <div className="relative w-20 h-20 flex-shrink-0 overflow-hidden rounded-lg bg-[var(--color-background-alt)]">
              {result.image_url ? (
                <Image
                  src={result.image_url}
                  alt={result.name}
                  fill
                  className="object-cover group-hover:scale-105 transition-transform duration-300"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-[var(--color-text-light)]">
                  <svg
                    className="w-8 h-8"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1}
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </div>
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2 mb-1">
                <h3 className="font-serif text-lg group-hover:text-[var(--color-accent)] transition-colors truncate">
                  {result.name}
                </h3>
                {result.price != null && (
                  <span className="flex-shrink-0 text-sm font-medium">
                    ${typeof result.price === 'number' ? result.price.toFixed(2) : parseFloat(String(result.price)).toFixed(2)}
                  </span>
                )}
              </div>

              <p className="text-sm text-[var(--color-text-muted)] line-clamp-2 mb-2">
                {result.description}
              </p>

              {/* Match Score */}
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1.5 bg-[var(--color-background-alt)] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[var(--color-accent)] rounded-full transition-all duration-500"
                    style={{ width: `${Math.round(result.score * 100)}%` }}
                  />
                </div>
                <span className="text-xs text-[var(--color-accent)] font-medium">
                  {Math.round(result.score * 100)}% match
                </span>
              </div>

              {result.category && (
                <span className="inline-block mt-2 text-xs px-2 py-0.5 bg-[var(--color-background-alt)] rounded">
                  {result.category}
                </span>
              )}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
