import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold">Sift Retail AI</h1>
          <nav className="flex gap-4">
            <Link
              href="/admin"
              className="text-sm hover:underline"
            >
              Admin
            </Link>
            <a
              href="http://localhost:3001"
              className="text-sm hover:underline"
            >
              Ice Cream Demo
            </a>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-bold mb-6 tracking-tight">
            Semantic Discovery Engine for Retail
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Turn customer intent into sales with AI-powered product discovery.
            No more keyword matching - understand what customers really want.
          </p>
          <div className="flex gap-4 justify-center">
            <a
              href="http://localhost:3001"
              className="px-8 py-3 bg-black text-white rounded-full font-medium hover:bg-gray-800 transition"
            >
              Try Ice Cream Demo
            </a>
            <Link
              href="/admin"
              className="px-8 py-3 border border-gray-300 rounded-full font-medium hover:border-gray-500 transition"
            >
              Admin Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-12">Core Features</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 border rounded-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h4 className="text-xl font-semibold mb-2">Vector Search</h4>
              <p className="text-gray-600">
                Understand customer intent, not just keywords. &quot;Something refreshing&quot;
                finds fruit sorbets, not just products with &quot;refreshing&quot; in the name.
              </p>
            </div>
            <div className="p-6 border rounded-lg">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h4 className="text-xl font-semibold mb-2">Zero Hallucination</h4>
              <p className="text-gray-600">
                RAG-powered responses use only your product data. The AI physically
                cannot recommend products that don&apos;t exist in your catalog.
              </p>
            </div>
            <div className="p-6 border rounded-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h4 className="text-xl font-semibold mb-2">Multi-Tenant Security</h4>
              <p className="text-gray-600">
                Hard metadata filtering ensures complete data isolation.
                Retailer A&apos;s customers can never see Retailer B&apos;s products.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-12">How It Works</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                1
              </div>
              <h4 className="font-semibold mb-2">Ingest Products</h4>
              <p className="text-gray-600 text-sm">
                Upload CSV or sync with WooCommerce. Products are embedded into
                1536-dimensional vectors capturing semantic meaning.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                2
              </div>
              <h4 className="font-semibold mb-2">Customer Queries</h4>
              <p className="text-gray-600 text-sm">
                Queries are converted to vectors and matched against products.
                Security filters ensure tenant isolation at the database level.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-black text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                3
              </div>
              <h4 className="font-semibold mb-2">AI Recommendations</h4>
              <p className="text-gray-600 text-sm">
                GPT-4o synthesizes results into natural recommendations,
                constrained to only use retrieved products.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-16 px-4 bg-gray-900 text-white">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-12">Tech Stack</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <p className="font-semibold text-lg">FastAPI</p>
              <p className="text-gray-400 text-sm">Backend Orchestrator</p>
            </div>
            <div>
              <p className="font-semibold text-lg">Next.js</p>
              <p className="text-gray-400 text-sm">Frontend & Admin</p>
            </div>
            <div>
              <p className="font-semibold text-lg">Qdrant</p>
              <p className="text-gray-400 text-sm">Vector Database</p>
            </div>
            <div>
              <p className="font-semibold text-lg">Supabase</p>
              <p className="text-gray-400 text-sm">Relational DB</p>
            </div>
            <div>
              <p className="font-semibold text-lg">OpenAI</p>
              <p className="text-gray-400 text-sm">Embeddings & Chat</p>
            </div>
            <div>
              <p className="font-semibold text-lg">WooCommerce</p>
              <p className="text-gray-400 text-sm">Store Integration</p>
            </div>
            <div>
              <p className="font-semibold text-lg">Tailwind</p>
              <p className="text-gray-400 text-sm">Styling</p>
            </div>
            <div>
              <p className="font-semibold text-lg">shadcn/ui</p>
              <p className="text-gray-400 text-sm">Components</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t">
        <div className="max-w-6xl mx-auto text-center text-gray-500 text-sm">
          <p>Sift Retail AI v2.0 - Semantic Discovery Engine</p>
        </div>
      </footer>
    </div>
  );
}
