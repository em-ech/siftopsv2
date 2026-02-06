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
        {/* Image Container - 3:4 fashion aspect ratio */}
        <div className="aspect-product relative overflow-hidden bg-[var(--color-background-alt)]">
          {product.mainImage ? (
            <Image
              src={product.mainImage}
              alt={product.name}
              fill
              sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
              className="object-cover"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-[var(--color-text-light)] text-xs uppercase tracking-wider">
                No image
              </span>
            </div>
          )}

          {/* Out of Stock Badge */}
          {!product.inStock && (
            <div className="absolute top-0 left-0 bg-black text-white px-3 py-1">
              <span className="text-[10px] tracking-[0.1em] uppercase font-bold">
                Sold Out
              </span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="pt-3 pb-1">
          {/* Name */}
          <h3 className="text-xs font-normal tracking-wide normal-case leading-snug">
            {product.name}
          </h3>

          {/* Price */}
          <p className="mt-1 text-xs font-bold">
            {product.priceText ||
              (product.price ? `$${product.price.toFixed(2)}` : "")}
          </p>
        </div>
      </article>
    </Link>
  );
}
