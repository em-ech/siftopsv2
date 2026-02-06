/**
 * API service for connecting to Sift Retail AI
 * Routes through Next.js API routes (Node.js BFF layer)
 * which proxy to the Python FastAPI backend for AI features
 */

const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || "pullbear";
const STORE_NAME = process.env.NEXT_PUBLIC_STORE_NAME || "Pull & Bear";

export interface SiftSearchResult {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url: string | null;
  category: string | null;
  score: number;
}

export interface SiftSearchResponse {
  results: SiftSearchResult[];
  count: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  response: string;
  products: SiftSearchResult[];
  products_count: number;
}

export interface HealthStatus {
  python: boolean;
  supabase: boolean;
}

/**
 * Semantic search using Sift AI (via Next.js API route → Python backend)
 */
export async function siftSearch(
  query: string,
  topK: number = 10
): Promise<SiftSearchResponse> {
  const response = await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      tenant_id: TENANT_ID,
      top_k: topK,
    }),
  });

  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * RAG-powered chat using Sift AI (via Next.js API route → Python backend)
 */
export async function siftChat(
  message: string,
  history: ChatMessage[] = []
): Promise<ChatResponse> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      tenant_id: TENANT_ID,
      store_name: STORE_NAME,
      history,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check backend health (Python + Supabase)
 */
export async function checkBackendHealth(): Promise<HealthStatus> {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) return { python: false, supabase: false };
    return response.json();
  } catch {
    return { python: false, supabase: false };
  }
}
