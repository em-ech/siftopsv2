/**
 * Supabase client for server-side data access
 * Used by API routes and server components
 */

import { createClient, SupabaseClient } from "@supabase/supabase-js";

let serverClient: SupabaseClient | null = null;

/**
 * Get Supabase client for server-side use (API routes, server components)
 * Returns null if credentials are not configured
 */
export function getSupabaseServer(): SupabaseClient | null {
  if (serverClient) return serverClient;

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;

  if (!url || !key) {
    return null;
  }

  serverClient = createClient(url, key);
  return serverClient;
}
