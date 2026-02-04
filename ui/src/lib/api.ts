/**
 * API service for connecting to Sift Retail AI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || "vanleeuwen";
const STORE_NAME = process.env.NEXT_PUBLIC_STORE_NAME || "Van Leeuwen";

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

/**
 * Semantic search using Sift AI backend
 */
export async function siftSearch(
  query: string,
  topK: number = 10
): Promise<SiftSearchResponse> {
  const response = await fetch(`${API_BASE_URL}/search/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
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
 * RAG-powered chat using Sift AI backend
 */
export async function siftChat(
  message: string,
  history: ChatMessage[] = []
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
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
 * Check if the backend is available
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      method: "GET",
    });
    return response.ok;
  } catch {
    return false;
  }
}
