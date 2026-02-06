import { NextResponse } from "next/server";
import { getSupabaseServer } from "@/lib/supabase";
import { extractCategories } from "@/lib/mappers";
import fs from "fs";
import path from "path";
import type { Category } from "@/lib/types";

const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || "pullbear";

export async function GET() {
  try {
    // Try Supabase first
    const supabase = getSupabaseServer();

    if (supabase) {
      const { data, error } = await supabase
        .from("products")
        .select("categories")
        .eq("tenant_id", TENANT_ID);

      if (!error && data && data.length > 0) {
        const categories = extractCategories(data);
        return NextResponse.json({ categories });
      }
    }

    // Fallback to static catalog
    return NextResponse.json({ categories: getStaticCategories() });
  } catch (error) {
    console.error("Categories API error:", error);
    return NextResponse.json({ categories: getStaticCategories() });
  }
}

function getStaticCategories(): Category[] {
  try {
    const catalogPath = path.join(process.cwd(), "public", "catalog.json");
    const data = JSON.parse(fs.readFileSync(catalogPath, "utf-8"));
    if (data.categories) return data.categories;
    if (data.products) return extractCategories(data.products);
    return [];
  } catch {
    return [];
  }
}
