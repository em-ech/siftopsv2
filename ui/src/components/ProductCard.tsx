import Link from "next/link";
import Image from "next/image";
import type { Product } from "@/lib/types";

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <Link href={`/product/${product.slug}`} className="group block">
      <article className="product-card">
        {/* Image Container */}
        <div className="aspect-product relative overflow-hidden bg-[var(--color-background-alt)]">
          {product.mainImage ? (
            <Image
              src={product.mainImage}
              alt={product.name}
              fill
              sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
              className="object-cover group-hover:scale-105 transition-transform duration-500"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-[var(--color-text-light)]">No image</span>
            </div>
          )}

          {/* Out of Stock Badge */}
          {!product.inStock && (
            <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm px-3 py-1">
              <span className="text-xs tracking-wider uppercase">
                Sold Out
              </span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="pt-4 pb-2">
          {/* Categories */}
          {product.categories.length > 0 && (
            <p className="text-xs text-[var(--color-text-light)] tracking-wider uppercase mb-1">
              {product.categories[0]}
            </p>
          )}

          {/* Name */}
          <h3 className="font-serif text-lg group-hover:text-[var(--color-text-muted)] transition-colors">
            {product.name}
          </h3>

          {/* Price */}
          <p className="mt-1 text-sm">
            {product.priceText || (product.price ? `$${product.price.toFixed(2)}` : "")}
          </p>
        </div>
      </article>
    </Link>
  );
}
