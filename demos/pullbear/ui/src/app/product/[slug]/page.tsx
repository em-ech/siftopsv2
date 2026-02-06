import { notFound } from "next/navigation";
import Link from "next/link";
import { ImageGallery } from "@/components";
import { getProductBySlug, getProducts } from "@/lib/data.server";

interface ProductPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const products = await getProducts();
  return products.map((product) => ({
    slug: product.slug,
  }));
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { slug } = await params;
  const product = await getProductBySlug(slug);

  if (!product) {
    notFound();
  }

  const allImages = [
    product.mainImage,
    ...product.gallery,
  ].filter(Boolean) as string[];

  return (
    <div className="py-6 sm:py-10">
      <div className="w-[90%] mx-auto">
        {/* Breadcrumb */}
        <nav className="mb-6">
          <ol className="flex items-center gap-2 text-[10px] tracking-[0.1em] uppercase">
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
            {product.categories.length > 0 && (
              <>
                <li className="text-[var(--color-text-light)]">/</li>
                <li>
                  <Link
                    href={`/shop?category=${product.categories[0]}`}
                    className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
                  >
                    {product.categories[0]}
                  </Link>
                </li>
              </>
            )}
            <li className="text-[var(--color-text-light)]">/</li>
            <li className="text-[var(--color-text)] normal-case">
              {product.name}
            </li>
          </ol>
        </nav>

        {/* Product Content - Two column */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
          {/* Images */}
          <div>
            <ImageGallery images={allImages} alt={product.name} />
          </div>

          {/* Details */}
          <div className="lg:py-4">
            {/* Category */}
            {product.categories.length > 0 && (
              <p className="text-[10px] tracking-[0.15em] uppercase text-[var(--color-text-muted)] mb-3">
                {product.categories.join(" / ")}
              </p>
            )}

            {/* Name */}
            <h1 className="text-xl sm:text-2xl font-bold tracking-[0.05em] uppercase mb-4">
              {product.name}
            </h1>

            {/* Price */}
            <p className="text-lg font-bold mb-6">
              {product.priceText ||
                (product.price ? `$${product.price.toFixed(2)}` : "")}
            </p>

            {/* Stock Status */}
            <div className="mb-6">
              {product.inStock ? (
                <span className="inline-flex items-center gap-2 text-xs text-green-700">
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                  {product.stockText || "In Stock"}
                </span>
              ) : (
                <span className="inline-flex items-center gap-2 text-xs text-red-700">
                  <span className="w-1.5 h-1.5 bg-red-500 rounded-full"></span>
                  {product.stockText || "Out of Stock"}
                </span>
              )}
            </div>

            {/* Short Description */}
            {product.shortDescription && (
              <p className="text-xs text-[var(--color-text-muted)] mb-8 leading-relaxed">
                {product.shortDescription}
              </p>
            )}

            {/* Size Selector */}
            <div className="mb-6">
              <p className="text-[10px] font-bold tracking-[0.15em] uppercase mb-3">
                Size
              </p>
              <div className="flex gap-2">
                {["S", "M", "L", "XL"].map((size) => (
                  <button
                    key={size}
                    className="w-12 h-12 border border-[var(--color-border)] text-xs font-bold tracking-wide hover:border-black transition-colors flex items-center justify-center"
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>

            {/* Add to Bag Button */}
            <button
              disabled={!product.inStock}
              className="btn btn-primary w-full mb-6 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {product.inStock ? "ADD TO SHOPPING BAG" : "SOLD OUT"}
            </button>

            {/* Wishlist */}
            <button className="flex items-center gap-2 text-xs tracking-[0.08em] uppercase text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors mb-8">
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
                />
              </svg>
              Add to wishlist
            </button>

            {/* Tags */}
            {product.tags.length > 0 && (
              <div className="mb-8">
                <div className="flex flex-wrap gap-2">
                  {product.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 border border-[var(--color-border)] text-[10px] tracking-[0.08em] uppercase"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Reference / SKU */}
            {product.sku && (
              <p className="text-[10px] text-[var(--color-text-light)] tracking-wider uppercase">
                REF: {product.sku}
              </p>
            )}
          </div>
        </div>

        {/* Product Details Section */}
        <div className="mt-16 border-t border-[var(--color-border)] pt-12">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            {/* Description */}
            {product.longDescription && (
              <div className="lg:col-span-2">
                <h2 className="text-sm font-bold tracking-[0.1em] uppercase mb-4">
                  Description
                </h2>
                <p className="text-xs text-[var(--color-text-muted)] leading-relaxed whitespace-pre-line">
                  {product.longDescription}
                </p>
              </div>
            )}

            {/* Additional Info */}
            <div>
              {product.additionalInfo.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold tracking-[0.1em] uppercase mb-4">
                    Product Details
                  </h3>
                  <dl className="space-y-3">
                    {product.additionalInfo.map((info, index) => (
                      <div
                        key={index}
                        className="flex justify-between text-xs border-b border-[var(--color-border)] pb-2"
                      >
                        <dt className="text-[var(--color-text-muted)] uppercase tracking-wider text-[10px]">
                          {info.key}
                        </dt>
                        <dd className="font-medium">{info.value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Back Link */}
        <div className="mt-12 pt-8 border-t border-[var(--color-border)]">
          <Link
            href="/shop"
            className="inline-flex items-center gap-2 text-xs tracking-[0.08em] uppercase hover:opacity-60 transition-opacity"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
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
