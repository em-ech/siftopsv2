import { NextResponse } from "next/server";
import { getSupabaseServer } from "@/lib/supabase";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";

export async function GET() {
  const [python, supabase] = await Promise.all([
    checkPython(),
    checkSupabase(),
  ]);

  return NextResponse.json({ python, supabase });
}

async function checkPython(): Promise<boolean> {
  try {
    const response = await fetch(`${PYTHON_API_URL}/`, {
      method: "GET",
      signal: AbortSignal.timeout(3000),
    });
    return response.ok;
  } catch {
    return false;
  }
}

async function checkSupabase(): Promise<boolean> {
  try {
    const client = getSupabaseServer();
    if (!client) return false;

    const { error } = await client
      .from("tenants")
      .select("id")
      .limit(1);

    return !error;
  } catch {
    return false;
  }
}
