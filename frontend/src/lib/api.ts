/**
 * API Client for Sift Retail AI Backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface Product {
  product_id: string;
  name: string;
  price: string;
  description: string;
  image_url: string | null;
  permalink: string;
  categories: string[];
  stock_status: string;
  score?: number;
}

export interface ChatResponse {
  response: string;
  products: Product[];
  products_count: number;
}

export interface SearchResponse {
  results: Product[];
  count: number;
}

export interface Analytics {
  total_searches: number;
  unique_queries: number;
  zero_result_queries: [string, number][];
  top_queries: [string, number][];
  conversion_rate: number;
}

// Chat endpoint
export async function sendChatMessage(
  message: string,
  tenantId: string,
  storeName: string = "our store",
  history: ChatMessage[] = [],
  sessionId?: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      tenant_id: tenantId,
      store_name: storeName,
      history,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat error: ${response.statusText}`);
  }

  return response.json();
}

// Search endpoint
export async function searchProducts(
  query: string,
  tenantId: string,
  topK: number = 5
): Promise<SearchResponse> {
  const response = await fetch(`${API_URL}/search/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      tenant_id: tenantId,
      top_k: topK,
    }),
  });

  if (!response.ok) {
    throw new Error(`Search error: ${response.statusText}`);
  }

  return response.json();
}

// Admin: Upload CSV
export async function uploadCSV(
  file: File,
  tenantId: string
): Promise<{ success: boolean; products_processed: number }> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("tenant_id", tenantId);

  const response = await fetch(`${API_URL}/admin/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload error: ${response.statusText}`);
  }

  return response.json();
}

// Admin: Sync WooCommerce
export async function syncWooCommerce(
  tenantId: string,
  woocommerceUrl: string,
  consumerKey: string,
  consumerSecret: string
): Promise<{ success: boolean; products_synced: number }> {
  const response = await fetch(`${API_URL}/admin/sync/woocommerce`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tenant_id: tenantId,
      woocommerce_url: woocommerceUrl,
      consumer_key: consumerKey,
      consumer_secret: consumerSecret,
    }),
  });

  if (!response.ok) {
    throw new Error(`Sync error: ${response.statusText}`);
  }

  return response.json();
}

// Admin: Get Analytics
export async function getAnalytics(
  tenantId: string,
  days: number = 30
): Promise<Analytics> {
  const response = await fetch(
    `${API_URL}/admin/analytics/${tenantId}?days=${days}`
  );

  if (!response.ok) {
    throw new Error(`Analytics error: ${response.statusText}`);
  }

  return response.json();
}

// Admin: Get Products
export async function getProducts(
  tenantId: string,
  limit: number = 100
): Promise<{ products: Product[]; count: number }> {
  const response = await fetch(
    `${API_URL}/admin/products/${tenantId}?limit=${limit}`
  );

  if (!response.ok) {
    throw new Error(`Products error: ${response.statusText}`);
  }

  return response.json();
}

// Health check
export async function checkHealth(): Promise<{
  status: string;
  services: Record<string, boolean>;
}> {
  const response = await fetch(`${API_URL}/health`);
  return response.json();
}
