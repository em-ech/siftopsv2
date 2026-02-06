import { NextRequest, NextResponse } from "next/server";
import { getSupabaseServer } from "@/lib/supabase";
import { mapDbProductToProduct } from "@/lib/mappers";
import fs from "fs";
import path from "path";

const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || "pullbear";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;

  try {
    // Try Supabase first
    const supabase = getSupabaseServer();

    if (supabase) {
      const { data, error } = await supabase
        .from("products")
        .select("*")
        .eq("tenant_id", TENANT_ID)
        .eq("slug", slug)
        .single();

      if (!error && data) {
        return NextResponse.json({ product: mapDbProductToProduct(data) });
      }
    }

    // Fallback to static catalog
    const product = getStaticProduct(slug);
    if (product) {
      return NextResponse.json({ product });
    }

    return NextResponse.json({ error: "Product not found" }, { status: 404 });
  } catch (error) {
    console.error("Product API error:", error);
    const product = getStaticProduct(slug);
    if (product) {
      return NextResponse.json({ product });
    }
    return NextResponse.json(
      { error: "Product not found" },
      { status: 404 }
    );
  }
}

function getStaticProduct(slug: string) {
  try {
    const catalogPath = path.join(process.cwd(), "public", "catalog.json");
    const data = JSON.parse(fs.readFileSync(catalogPath, "utf-8"));
    return (
      (data.products || []).find(
        (p: Record<string, unknown>) => p.slug === slug
      ) || null
    );
  } catch {
    return null;
  }
}
