# Sift Retail AI

A multi-tenant SaaS platform that gives any online retailer AI-powered product discovery in minutes. Retailers upload their catalog (CSV, JSON, or WooCommerce sync) and Sift provides semantic search, an AI shopping assistant, and embeddable widgets -- all with complete data isolation between tenants.

## High-Level Overview

Sift solves the "search relevance" problem for small-to-mid-size retailers. Traditional keyword search fails when a customer searches for "something warm for a winter trip" -- Sift understands intent, extracts constraints (budget, color, style), and returns semantically relevant products ranked by match quality.

**What it does:**
- **Semantic Search** -- Understands natural language queries like "casual outfit under $40" and returns relevant products, not just keyword matches.
- **AI Chat Assistant** -- A zero-hallucination shopping assistant that only recommends products from the retailer's own catalog. Multi-turn conversations with product links.
- **Catalog Ingestion** -- Upload a CSV/JSON or connect WooCommerce. Products are normalized, optionally enriched with LLM-extracted attributes (color, material, style), embedded, and stored.
- **Multi-Tenant Isolation** -- Every query is filtered at the database level by `tenant_id`. No cross-tenant data leakage.
- **Analytics** -- Search metrics, zero-result queries (demand signals), click tracking.
- **Embeddable Widgets** -- Drop-in `<script>` tags for search and chat on any website.

## Architecture

```
                         Retailer's Website
                                |
                    +-----------+-----------+
                    |                       |
              Search Widget           Chat Widget
                    |                       |
                    +------> Next.js UI <---+
                             (Demos / Dashboard)
                                |
                         API Routes (proxy)
                                |
                    +-----------+-----------+
                    |                       |
                    v                       v
            POST /search/            POST /chat/
                    |                       |
                    +---> FastAPI Backend <--+
                          (Railway)
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
          OpenAI        Qdrant        Supabase
        Embeddings    Vector DB     Postgres DB
        + GPT-4o     (Semantic     (Products,
                      Search)      Tenants,
                                   Analytics)
```

### Request Flow

1. **Search**: User query -> Query Understanding (LLM extracts budget/color/category) -> OpenAI Embedding -> Qdrant vector search (filtered by tenant) -> Optional LLM validation -> Results
2. **Chat**: User message -> Vector search for relevant products -> Build constrained prompt (only retrieved products) -> GPT-4o generates response -> Products + response returned
3. **Ingestion**: Raw products -> Normalize (clean HTML, prices, slugs) -> Enrich (optional LLM attribute extraction) -> Build embedding text -> Vectorize (OpenAI) -> Store in Supabase + Qdrant

### Security Model

- **Tenant isolation** enforced at the Qdrant filter level -- queries physically cannot return another tenant's products
- **Prompt injection detection** on all search/chat inputs
- **Product data sanitization** before LLM prompts (prevents injection via malicious product names)
- **Zero-hallucination RAG** -- the LLM system prompt only contains retrieved products, never general knowledge

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend API | FastAPI (Python 3.13, uv) |
| Vector Database | Qdrant Cloud |
| Relational Database | Supabase (Postgres) |
| AI/ML | OpenAI (GPT-4o, text-embedding-3-small) |
| Demo UIs | Next.js 15 + Tailwind CSS |
| Deployment | Railway (backend), Vercel-ready (frontends) |

## Project Structure

```
siftopsv2/
├── backend/                    # FastAPI backend (deployed to Railway)
│   ├── app/
│   │   ├── main.py            # Entry point, CORS, routes
│   │   ├── core/              # Config, security, caching
│   │   ├── routes/            # API endpoints (search, chat, admin)
│   │   ├── services/          # Business logic
│   │   │   ├── ingestion/     # Pipeline: normalize -> enrich -> embed
│   │   │   ├── rag/           # Enhanced retriever, validator, reranker
│   │   │   ├── vector_service.py   # Qdrant operations
│   │   │   ├── chat_service.py     # RAG chat pipeline
│   │   │   └── db_service.py       # Supabase operations
│   │   └── schemas/           # Pydantic models (ProductRaw -> ProductCreate)
│   ├── scripts/               # Seeding scripts (seed_pullbear.py)
│   ├── data/                  # Catalog JSON files
│   └── railway.toml           # Railway deployment config
├── demos/
│   └── pullbear/              # Pull & Bear demo store
│       ├── ui/                # Next.js storefront
│       └── catalog/           # Catalog data + seeding scripts
├── frontend/                  # Admin dashboard (Next.js)
├── catalog_crawler/           # Product scraping tools
├── supabase/
│   └── schema.sql             # Database schema
└── scripts/                   # Utility scripts
```

## Live Demo (Pull & Bear)

The Pull & Bear demo showcases Sift powering a fashion retailer:

- **Backend**: https://backend-production-df02.up.railway.app
- **Health**: https://backend-production-df02.up.railway.app/health
- **Demo UI**: Run locally with `cd demos/pullbear/ui && npm run dev`

### Try it

```bash
# Semantic search
curl -s https://backend-production-df02.up.railway.app/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "warm jacket under $40", "tenant_id": "pullbear", "top_k": 3}'

# AI chat
curl -s https://backend-production-df02.up.railway.app/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "I need something for a night out", "tenant_id": "pullbear", "store_name": "Pull & Bear"}'
```

## Quick Start

### 1. Backend

```bash
cd backend
cp .env.example .env    # Add your API keys
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### 2. Seed a catalog

```bash
cd backend
uv run python scripts/seed_pullbear.py
```

### 3. Demo UI

```bash
cd demos/pullbear/ui
cp .env.example .env.local    # Set PYTHON_API_URL
npm install && npm run dev
```

## Environment Variables

### Backend (.env)

```
OPENAI_API_KEY=sk-...
QDRANT_URL=https://xxx.cloud.qdrant.io
QDRANT_API_KEY=...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=...
CORS_ORIGINS=http://localhost:3000,https://*.vercel.app
```

### Demo UI (.env.local)

```
PYTHON_API_URL=https://backend-production-df02.up.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=...
NEXT_PUBLIC_TENANT_ID=pullbear
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/search/` | Semantic product search with query understanding |
| `POST` | `/chat/` | AI shopping assistant (RAG) |
| `GET` | `/health` | Service health check |
| `POST` | `/admin/upload` | CSV/JSON catalog upload |
| `POST` | `/admin/sync/woocommerce` | WooCommerce catalog sync |
| `GET` | `/admin/analytics/{tenant_id}` | Search analytics |
| `POST` | `/admin/api-keys/{tenant_id}` | Create widget API key |

## Deployment (Railway)

The backend is deployed to Railway with `railway.toml`:

```toml
[build]
buildCommand = "pip install uv && uv sync"

[deploy]
startCommand = "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
healthcheckPath = "/health"
```

Deploy:
```bash
cd backend
railway up
railway domain    # Get public URL
```

---

Built for the IE Venture Lab bootcamp.
