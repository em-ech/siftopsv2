import { NextRequest, NextResponse } from "next/server";
import { getSupabaseServer } from "@/lib/supabase";
import { mapDbProductToProduct, extractCategories } from "@/lib/mappers";
import fs from "fs";
import path from "path";

const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || "pullbear";

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const category = searchParams.get("category");
  const sort = searchParams.get("sort") || "name";
  const limit = parseInt(searchParams.get("limit") || "100", 10);
  const q = searchParams.get("q");

  try {
    // Try Supabase first
    const supabase = getSupabaseServer();

    if (supabase) {
      let query = supabase
        .from("products")
        .select("*")
        .eq("tenant_id", TENANT_ID)
        .limit(limit);

      if (category) {
        query = query.contains("categories", [category]);
      }

      if (q) {
        query = query.ilike("name", `%${q}%`);
      }

      // Apply sorting
      switch (sort) {
        case "price-asc":
          query = query.order("price", { ascending: true });
          break;
        case "price-desc":
          query = query.order("price", { ascending: false });
          break;
        case "newest":
          query = query.order("created_at", { ascending: false });
          break;
        default:
          query = query.order("name", { ascending: true });
      }

      const { data, error } = await query;

      if (!error && data && data.length > 0) {
        const products = data.map(mapDbProductToProduct);
        return NextResponse.json({ products });
      }
    }

    // Fallback to static catalog.json
    return NextResponse.json({ products: getStaticProducts(category, q, sort, limit) });
  } catch (error) {
    console.error("Products API error:", error);
    // Fallback to static catalog.json
    return NextResponse.json({ products: getStaticProducts(category, q, sort, limit) });
  }
}

function getStaticProducts(
  category: string | null,
  q: string | null,
  sort: string,
  limit: number
) {
  try {
    const catalogPath = path.join(process.cwd(), "public", "catalog.json");
    const data = JSON.parse(fs.readFileSync(catalogPath, "utf-8"));
    let products = data.products || [];

    if (category) {
      products = products.filter((p: Record<string, unknown>) =>
        ((p.categories as string[]) || []).includes(category)
      );
    }

    if (q) {
      const lowerQ = q.toLowerCase();
      products = products.filter(
        (p: Record<string, unknown>) =>
          ((p.name as string) || "").toLowerCase().includes(lowerQ) ||
          ((p.shortDescription as string) || "").toLowerCase().includes(lowerQ)
      );
    }

    switch (sort) {
      case "price-asc":
        products.sort(
          (a: Record<string, unknown>, b: Record<string, unknown>) =>
            ((a.price as number) || 0) - ((b.price as number) || 0)
        );
        break;
      case "price-desc":
        products.sort(
          (a: Record<string, unknown>, b: Record<string, unknown>) =>
            ((b.price as number) || 0) - ((a.price as number) || 0)
        );
        break;
      case "name":
        products.sort(
          (a: Record<string, unknown>, b: Record<string, unknown>) =>
            ((a.name as string) || "").localeCompare((b.name as string) || "")
        );
        break;
    }

    return products.slice(0, limit);
  } catch {
    return [];
  }
}
