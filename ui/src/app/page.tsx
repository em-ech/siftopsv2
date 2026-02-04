import Link from "next/link";
import { ProductGrid } from "@/components";
import { getFeaturedProducts, getCategories } from "@/lib/data.server";

export default function HomePage() {
  const featuredProducts = getFeaturedProducts(8);
  const categories = getCategories();

  return (
    <div>
      {/* Hero Section */}
      <section className="relative h-[70vh] min-h-[500px] max-h-[800px] flex items-center justify-center overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 bg-[var(--color-secondary)]">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-white/20" />
        </div>

        {/* Content */}
        <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-serif mb-6 tracking-tight">
            Artisan Ice Cream
          </h1>
          <p className="text-lg sm:text-xl text-[var(--color-text-muted)] mb-8 max-w-2xl mx-auto">
            Handcrafted in small batches using the finest ingredients from around
            the world. Every scoop tells a story.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/shop" className="btn btn-primary">
              Shop Now
            </Link>
            <Link href="/shop?category=vegan" className="btn btn-secondary">
              Explore Vegan
            </Link>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-16 sm:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-serif text-center mb-12">
            Shop by Category
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
            {categories.slice(0, 4).map((category) => (
              <Link
                key={category.slug}
                href={`/shop?category=${category.slug}`}
                className="group relative aspect-square bg-[var(--color-background-alt)] overflow-hidden"
              >
                <div className="absolute inset-0 bg-[var(--color-secondary)] group-hover:bg-[var(--color-accent)] transition-colors duration-300" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-lg sm:text-xl font-serif tracking-wide group-hover:scale-105 transition-transform">
                    {category.name}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-16 sm:py-24 bg-[var(--color-background-alt)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-serif mb-4 sm:mb-0">
              Featured Flavors
            </h2>
            <Link
              href="/shop"
              className="text-sm tracking-wider uppercase hover:text-[var(--color-text-muted)] transition-colors"
            >
              View All →
            </Link>
          </div>
          <ProductGrid products={featuredProducts} />
        </div>
      </section>

      {/* AI Search Feature */}
      <section className="py-16 sm:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <span className="inline-block px-3 py-1 text-xs font-medium tracking-wider uppercase bg-[var(--color-accent)]/10 text-[var(--color-accent)] rounded-full mb-4">
              Powered by Sift AI
            </span>
            <h2 className="text-3xl sm:text-4xl font-serif mb-4">
              Find Your Perfect Flavor
            </h2>
            <p className="text-lg text-[var(--color-text-muted)] max-w-2xl mx-auto">
              Use our AI-powered search to discover ice cream based on how you
              feel, not just what you know. Try "something refreshing" or "best
              for a date night".
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Regular Search */}
            <div className="text-center p-6">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--color-background-alt)] flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-[var(--color-text-muted)]"
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
              <h3 className="font-serif text-xl mb-2">Regular Search</h3>
              <p className="text-sm text-[var(--color-text-muted)]">
                Classic keyword search by name, description, or tags
              </p>
            </div>

            {/* Sift AI */}
            <div className="text-center p-6 bg-[var(--color-background-alt)] rounded-lg">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--color-accent)]/20 flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-[var(--color-accent)]"
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
              <h3 className="font-serif text-xl mb-2">Sift AI Search</h3>
              <p className="text-sm text-[var(--color-text-muted)]">
                Semantic search that understands your intent and mood
              </p>
            </div>

            {/* Chat */}
            <div className="text-center p-6">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--color-background-alt)] flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-[var(--color-text-muted)]"
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
              <h3 className="font-serif text-xl mb-2">AI Chat</h3>
              <p className="text-sm text-[var(--color-text-muted)]">
                Conversational recommendations powered by RAG
              </p>
            </div>
          </div>

          <div className="text-center mt-10">
            <Link
              href="/shop"
              className="btn btn-primary inline-flex items-center gap-2"
            >
              Try AI Search
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* About Banner */}
      <section className="py-16 sm:py-24 bg-[var(--color-primary)] text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-serif mb-6">
            Crafted with Care
          </h2>
          <p className="text-lg text-white/80 mb-8 max-w-2xl mx-auto">
            Every pint of Van Leeuwen ice cream is made with the same care and
            attention to detail as the very first batch we made. We source the
            finest ingredients and craft each flavor by hand.
          </p>
          <Link
            href="/shop"
            className="inline-block btn bg-white text-[var(--color-primary)] hover:bg-white/90"
          >
            Discover More
          </Link>
        </div>
      </section>
    </div>
  );
}
