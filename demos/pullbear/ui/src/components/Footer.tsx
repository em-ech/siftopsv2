import Link from "next/link";

export function Footer() {
  return (
    <footer className="bg-[var(--color-background-alt)] border-t border-[var(--color-border)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-2">
            <h3 className="text-2xl font-bold mb-4">PULL&amp;BEAR</h3>
            <p className="text-[var(--color-text-muted)] text-sm max-w-md">
              Discover the latest trends in fashion, streetwear, and casual
              clothing. Graphic tees, hoodies, jackets, and more.
            </p>
          </div>

          {/* Shop */}
          <div>
            <h4 className="text-xs font-medium tracking-widest uppercase mb-4">
              Shop
            </h4>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/shop"
                  className="text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
                >
                  All Products
                </Link>
              </li>
              <li>
                <Link
                  href="/shop?category=t-shirts"
                  className="text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
                >
                  T-Shirts
                </Link>
              </li>
              <li>
                <Link
                  href="/shop?category=hoodies"
                  className="text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
                >
                  Hoodies
                </Link>
              </li>
              <li>
                <Link
                  href="/shop?category=jackets"
                  className="text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
                >
                  Jackets
                </Link>
              </li>
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 className="text-xs font-medium tracking-widest uppercase mb-4">
              Information
            </h4>
            <ul className="space-y-3">
              <li>
                <span className="text-sm text-[var(--color-text-muted)]">
                  Demo Store
                </span>
              </li>
              <li>
                <span className="text-sm text-[var(--color-text-muted)]">
                  Data from Crawler
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-12 pt-8 border-t border-[var(--color-border)]">
          <p className="text-xs text-[var(--color-text-light)] text-center">
            This is a demo storefront. Product data collected via polite web
            crawling for educational purposes.
          </p>
        </div>
      </div>
    </footer>
  );
}
