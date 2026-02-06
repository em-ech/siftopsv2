import { NextRequest, NextResponse } from "next/server";

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000";
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || "pullbear";
const STORE_NAME = process.env.NEXT_PUBLIC_STORE_NAME || "Pull & Bear";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${PYTHON_API_URL}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: body.message,
        tenant_id: body.tenant_id || TENANT_ID,
        store_name: body.store_name || STORE_NAME,
        history: body.history || [],
        session_id: body.session_id,
      }),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Chat service unavailable" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Chat proxy error:", error);
    return NextResponse.json(
      { error: "Chat service unavailable" },
      { status: 503 }
    );
  }
}
