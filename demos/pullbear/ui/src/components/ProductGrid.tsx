import { ProductCard } from "./ProductCard";
import type { Product } from "@/lib/types";

interface ProductGridProps {
  products: Product[];
  emptyMessage?: string;
}

export function ProductGrid({
  products,
  emptyMessage = "No products found",
}: ProductGridProps) {
  if (products.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-[var(--color-text-muted)] text-sm">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-4 gap-y-8">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
