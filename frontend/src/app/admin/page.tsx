"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  uploadCSV,
  syncWooCommerce,
  getAnalytics,
  type Analytics,
} from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function AdminPage() {
  const [tenantId, setTenantId] = useState("vanleeuwen");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<string | null>(null);

  // WooCommerce sync
  const [wcUrl, setWcUrl] = useState("https://vanleeuwenicecream.com");
  const [wcKey, setWcKey] = useState("");
  const [wcSecret, setWcSecret] = useState("");
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<string | null>(null);

  // Analytics
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !tenantId) return;

    setUploading(true);
    setUploadResult(null);

    try {
      const result = await uploadCSV(file, tenantId);
      setUploadResult(
        `Success! Processed ${result.products_processed} products.`
      );
    } catch (error) {
      setUploadResult(`Error: ${error}`);
    } finally {
      setUploading(false);
    }
  };

  const handleWooCommerceSync = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!wcUrl || !wcKey || !wcSecret || !tenantId) return;

    setSyncing(true);
    setSyncResult(null);

    try {
      const result = await syncWooCommerce(tenantId, wcUrl, wcKey, wcSecret);
      setSyncResult(`Success! Synced ${result.products_synced} products.`);
    } catch (error) {
      setSyncResult(`Error: ${error}`);
    } finally {
      setSyncing(false);
    }
  };

  const loadAnalytics = async () => {
    if (!tenantId) return;

    setLoadingAnalytics(true);
    try {
      const data = await getAnalytics(tenantId);
      setAnalytics(data);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  useEffect(() => {
    if (tenantId) {
      loadAnalytics();
    }
  }, [tenantId]);

  // Prepare chart data
  const topQueriesData =
    analytics?.top_queries.map(([query, count]) => ({
      query: query.length > 15 ? query.slice(0, 15) + "..." : query,
      count,
    })) || [];

  const zeroResultsData =
    analytics?.zero_result_queries.map(([query, count]) => ({
      query: query.length > 15 ? query.slice(0, 15) + "..." : query,
      count,
    })) || [];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Sift Retail AI</h1>
        <p className="text-gray-600 mb-8">Admin Dashboard</p>

        {/* Tenant Selection */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Store Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <label className="block text-sm font-medium mb-2">
                  Tenant ID
                </label>
                <Input
                  value={tenantId}
                  onChange={(e) => setTenantId(e.target.value)}
                  placeholder="e.g., vanleeuwen"
                />
              </div>
              <Button onClick={loadAnalytics} disabled={loadingAnalytics}>
                {loadingAnalytics ? "Loading..." : "Refresh Analytics"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* CSV Upload */}
          <Card>
            <CardHeader>
              <CardTitle>Upload Product CSV</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleFileUpload} className="space-y-4">
                <Input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
                <Button type="submit" disabled={uploading || !file}>
                  {uploading ? "Uploading..." : "Upload & Process"}
                </Button>
                {uploadResult && (
                  <p
                    className={`text-sm ${
                      uploadResult.startsWith("Error")
                        ? "text-red-600"
                        : "text-green-600"
                    }`}
                  >
                    {uploadResult}
                  </p>
                )}
              </form>
            </CardContent>
          </Card>

          {/* WooCommerce Sync */}
          <Card>
            <CardHeader>
              <CardTitle>WooCommerce Sync</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleWooCommerceSync} className="space-y-4">
                <Input
                  value={wcUrl}
                  onChange={(e) => setWcUrl(e.target.value)}
                  placeholder="Store URL"
                />
                <Input
                  value={wcKey}
                  onChange={(e) => setWcKey(e.target.value)}
                  placeholder="Consumer Key"
                />
                <Input
                  type="password"
                  value={wcSecret}
                  onChange={(e) => setWcSecret(e.target.value)}
                  placeholder="Consumer Secret"
                />
                <Button
                  type="submit"
                  disabled={syncing || !wcUrl || !wcKey || !wcSecret}
                >
                  {syncing ? "Syncing..." : "Sync Products"}
                </Button>
                {syncResult && (
                  <p
                    className={`text-sm ${
                      syncResult.startsWith("Error")
                        ? "text-red-600"
                        : "text-green-600"
                    }`}
                  >
                    {syncResult}
                  </p>
                )}
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Analytics Section */}
        <h2 className="text-2xl font-bold mb-4">Analytics & ROI</h2>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-500">Total Searches</p>
              <p className="text-3xl font-bold">
                {analytics?.total_searches || 0}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-500">Unique Queries</p>
              <p className="text-3xl font-bold">
                {analytics?.unique_queries || 0}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-500">Zero-Result Searches</p>
              <p className="text-3xl font-bold">
                {analytics?.zero_result_queries.length || 0}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-500">Conversion Rate</p>
              <p className="text-3xl font-bold">
                {((analytics?.conversion_rate || 0) * 100).toFixed(1)}%
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle>Top Search Queries</CardTitle>
            </CardHeader>
            <CardContent>
              {topQueriesData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={topQueriesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="query" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#000" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-gray-500 text-center py-12">
                  No search data yet
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Demand Map (Zero-Result Queries)</CardTitle>
              <p className="text-sm text-gray-500">
                Products customers want but can&apos;t find
              </p>
            </CardHeader>
            <CardContent>
              {zeroResultsData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={zeroResultsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="query" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#ef4444" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-gray-500 text-center py-12">
                  No zero-result queries yet
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
