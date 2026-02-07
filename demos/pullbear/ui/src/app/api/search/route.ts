import { NextRequest, NextResponse } from "next/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || "pullbear";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${PYTHON_API_URL}/search/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: body.query,
        tenant_id: body.tenant_id || TENANT_ID,
        top_k: body.top_k || 10,
      }),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Search service unavailable" },
        { status: response.status }
      );
    }

    const data = await response.json();

    // Map backend product_id to frontend id
    if (data.results) {
      data.results = data.results.map(
        (p: Record<string, unknown>) => ({
          ...p,
          id: p.product_id || p.id,
        })
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Search proxy error:", error);
    return NextResponse.json(
      { error: "Search service unavailable" },
      { status: 503 }
    );
  }
}
