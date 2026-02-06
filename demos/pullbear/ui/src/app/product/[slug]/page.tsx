import { notFound } from "next/navigation";
import Link from "next/link";
import { ImageGallery } from "@/components";
import { getProductBySlug, getProducts } from "@/lib/data.server";

interface ProductPageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  const products = getProducts();
  return products.map((product) => ({
    slug: product.slug,
  }));
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { slug } = await params;
  const product = getProductBySlug(slug);

  if (!product) {
    notFound();
  }

  // Combine main image and gallery
  const allImages = [
    product.mainImage,
    ...product.gallery,
  ].filter(Boolean) as string[];

  return (
    <div className="py-8 sm:py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <nav className="mb-8">
          <ol className="flex items-center gap-2 text-sm">
            <li>
              <Link
                href="/"
                className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
              >
                Home
              </Link>
            </li>
            <li className="text-[var(--color-text-light)]">/</li>
            <li>
              <Link
                href="/shop"
                className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
              >
                Shop
              </Link>
            </li>
            <li className="text-[var(--color-text-light)]">/</li>
            <li className="text-[var(--color-text)]">{product.name}</li>
          </ol>
        </nav>

        {/* Product Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16">
          {/* Images */}
          <div>
            <ImageGallery images={allImages} alt={product.name} />
          </div>

          {/* Details */}
          <div className="lg:py-4">
            {/* Category */}
            {product.categories.length > 0 && (
              <p className="text-xs tracking-widest uppercase text-[var(--color-text-muted)] mb-2">
                {product.categories.join(" / ")}
              </p>
            )}

            {/* Name */}
            <h1 className="text-3xl sm:text-4xl font-serif mb-4">
              {product.name}
            </h1>

            {/* Price */}
            <p className="text-2xl mb-6">
              {product.priceText ||
                (product.price ? `$${product.price.toFixed(2)}` : "")}
            </p>

            {/* Stock Status */}
            <div className="mb-6">
              {product.inStock ? (
                <span className="inline-flex items-center gap-2 text-sm text-green-700">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  {product.stockText || "In Stock"}
                </span>
              ) : (
                <span className="inline-flex items-center gap-2 text-sm text-red-700">
                  <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                  {product.stockText || "Out of Stock"}
                </span>
              )}
            </div>

            {/* Short Description */}
            {product.shortDescription && (
              <p className="text-[var(--color-text-muted)] mb-8 leading-relaxed">
                {product.shortDescription}
              </p>
            )}

            {/* CTA Button */}
            {product.url ? (
              <a
                href={product.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary w-full sm:w-auto mb-8"
              >
                View on Store
              </a>
            ) : (
              <button
                disabled={!product.inStock}
                className="btn btn-primary w-full sm:w-auto mb-8 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {product.inStock ? "Add to Cart" : "Sold Out"}
              </button>
            )}

            {/* Tags */}
            {product.tags.length > 0 && (
              <div className="mb-8">
                <div className="flex flex-wrap gap-2">
                  {product.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-[var(--color-background-alt)] text-xs tracking-wide"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* SKU */}
            {product.sku && (
              <p className="text-xs text-[var(--color-text-light)] mb-8">
                SKU: {product.sku}
              </p>
            )}
          </div>
        </div>

        {/* Product Details Tabs */}
        <div className="mt-16 border-t border-[var(--color-border)] pt-16">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            {/* Description */}
            {product.longDescription && (
              <div className="lg:col-span-2">
                <h2 className="text-xl font-serif mb-4">Description</h2>
                <div className="prose prose-sm max-w-none text-[var(--color-text-muted)]">
                  <p className="whitespace-pre-line">{product.longDescription}</p>
                </div>
              </div>
            )}

            {/* Additional Info */}
            <div>
              {/* Ingredients */}
              {product.ingredients && (
                <div className="mb-8">
                  <h3 className="text-sm font-medium tracking-wide uppercase mb-3">
                    Ingredients
                  </h3>
                  <p className="text-sm text-[var(--color-text-muted)] leading-relaxed">
                    {product.ingredients}
                  </p>
                </div>
              )}

              {/* Allergens */}
              {product.allergens.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-sm font-medium tracking-wide uppercase mb-3">
                    Allergens
                  </h3>
                  <p className="text-sm text-[var(--color-text-muted)]">
                    Contains: {product.allergens.join(", ")}
                  </p>
                </div>
              )}

              {/* Additional Info Table */}
              {product.additionalInfo.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium tracking-wide uppercase mb-3">
                    Additional Information
                  </h3>
                  <dl className="space-y-2">
                    {product.additionalInfo.map((info, index) => (
                      <div key={index} className="flex justify-between text-sm">
                        <dt className="text-[var(--color-text-muted)]">
                          {info.key}
                        </dt>
                        <dd>{info.value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Back Link */}
        <div className="mt-16 pt-8 border-t border-[var(--color-border)]">
          <Link
            href="/shop"
            className="inline-flex items-center gap-2 text-sm hover:text-[var(--color-text-muted)] transition-colors"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Shop
          </Link>
        </div>
      </div>
    </div>
  );
}
