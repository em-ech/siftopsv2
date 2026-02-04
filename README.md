# Sift Retail AI v2

A comprehensive retail AI platform featuring:
- **Semantic Discovery Engine**: Vector search to understand customer intent
- **Catalog Crawler**: Polite web scraper for WooCommerce stores
- **Demo Storefront**: Van Leeuwen-inspired UI with extracted design tokens

## Features

### Sift Retail AI (Backend + Frontend)
- **Vector Search**: Semantic product discovery using OpenAI embeddings
- **Zero Hallucination**: RAG-powered responses constrained to your catalog
- **Multi-Tenant Security**: Hard metadata filtering for complete data isolation
- **WooCommerce Integration**: Sync products from WooCommerce stores
- **ROI Analytics**: Track searches and identify demand gaps

### Catalog Crawler
- **Polite Crawling**: Configurable rate limiting, delays, and retries
- **Resume Capability**: Save/restore state for interrupted crawls
- **Rich Extraction**: Products, images, categories, ingredients, allergens
- **Multiple Outputs**: JSONL, CSV, and summary reports

### Demo Storefront (UI)
- **Van Leeuwen-inspired Design**: Extracted color palette and typography
- **Responsive Layout**: Mobile-first, accessible components
- **Product Catalog**: Search, filter, sort, and product detail pages

## Tech Stack

| Component | Technology |
|-----------|------------|
| AI Backend | FastAPI (Python) |
| AI Frontend | Next.js + Tailwind |
| Vector DB | Qdrant |
| Relational DB | Supabase (Postgres) |
| AI Models | OpenAI (GPT-4o, Embeddings) |
| Crawler | Python + httpx + BeautifulSoup |
| Demo UI | Next.js + Tailwind (no UI kits) |

## Project Structure

```
siftopsv2/
├── backend/              # Sift AI FastAPI backend
│   ├── app/
│   │   ├── main.py       # Entry point
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic
│   │   └── core/         # Configuration
│   ├── scripts/          # Ingestion scripts
│   └── data/             # Sample data
├── frontend/             # Sift AI admin/demo frontend
│   └── src/
├── catalog_crawler/      # WooCommerce catalog scraper
│   ├── catalog_crawler/
│   │   ├── crawler.py    # Main crawler
│   │   ├── parsers/      # HTML parsers
│   │   └── models/       # Pydantic models
│   └── tests/
├── ui/                   # Van Leeuwen demo storefront
│   ├── src/
│   │   ├── app/          # Next.js pages
│   │   ├── components/   # React components
│   │   └── lib/          # Data utilities
│   └── theme/            # Extracted design tokens
├── scripts/              # Utility scripts
│   ├── extract_theme_tokens.py
│   └── export_for_ui.py
└── supabase/             # Database schema
```

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
source ~/.local/bin/env  # if uv not in PATH
uv sync

# Run the server
uv run uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Create environment file
cp .env.example .env.local

# Install dependencies
npm install

# Run the dev server
npm run dev
```

### 3. Database Setup

1. Create a [Supabase](https://supabase.com) project
2. Run the SQL in `supabase/schema.sql` in the SQL Editor
3. Copy your URL and anon key to `backend/.env`

### 4. Vector Database Setup

1. Create a [Qdrant Cloud](https://cloud.qdrant.io) cluster
2. Copy your URL and API key to `backend/.env`

## Environment Variables

### Backend (.env)

```
OPENAI_API_KEY=sk-...
QDRANT_URL=https://xxx.cloud.qdrant.io:6333
QDRANT_API_KEY=...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=...
WOOCOMMERCE_URL=https://vanleeuwenicecream.com
WOOCOMMERCE_CONSUMER_KEY=ck_...
WOOCOMMERCE_CONSUMER_SECRET=cs_...
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints

### Search
```bash
POST /search/
{
  "query": "something refreshing for summer",
  "tenant_id": "vanleeuwen",
  "top_k": 5
}
```

### Chat
```bash
POST /chat/
{
  "message": "What's your best vegan option?",
  "tenant_id": "vanleeuwen",
  "store_name": "Van Leeuwen"
}
```

### Admin - WooCommerce Sync
```bash
POST /admin/sync/woocommerce
{
  "tenant_id": "vanleeuwen",
  "woocommerce_url": "https://vanleeuwenicecream.com",
  "consumer_key": "ck_...",
  "consumer_secret": "cs_..."
}
```

### Admin - CSV Upload
```bash
POST /admin/upload
Content-Type: multipart/form-data
file: products.csv
tenant_id: vanleeuwen
```

## Deployment

### Backend (Render)
1. Connect GitHub repo
2. Set base directory to `backend`
3. Build command: `pip install uv && uv sync`
4. Start command: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Frontend (Vercel)
1. Connect GitHub repo
2. Set root directory to `frontend`
3. Set `NEXT_PUBLIC_API_URL` to your Render URL

## WooCommerce Setup

To get WooCommerce API keys:
1. Go to WooCommerce > Settings > Advanced > REST API
2. Add key with Read permissions
3. Copy Consumer Key and Secret

## Security

- **Tenant Isolation**: All queries include a hard `tenant_id` filter at the database level
- **RAG Guardrails**: LLM can only reference retrieved products
- **No Data Leakage**: Cross-tenant access is impossible by design

---

## Catalog Crawler

A polite web scraper for WooCommerce storefronts.

### Usage

```bash
cd catalog_crawler
pip install -e .

# Crawl Van Leeuwen store
python -m catalog_crawler \
  --base-url https://vanleeuwenicecream.com \
  --start /store/ \
  --out ./out \
  --concurrency 5 \
  --delay 0.5
```

### Output

```
out/
├── catalog.jsonl    # Products (one JSON per line)
├── catalog.csv      # Products in CSV format
└── report.json      # Crawl statistics
```

See [catalog_crawler/README.md](catalog_crawler/README.md) for full documentation.

---

## Demo Storefront (UI)

A Van Leeuwen-inspired storefront that displays crawled catalog data.

### Setup

```bash
# Extract theme tokens from the source site
python scripts/extract_theme_tokens.py \
  --url https://vanleeuwenicecream.com \
  --output ui/theme/tokens.json

# Convert crawler output for UI
python scripts/export_for_ui.py \
  --input out/catalog.jsonl \
  --output ui/public/catalog.json

# Run the UI
cd ui
npm install
npm run dev
```

### Design System

The UI uses a tokenized theme that mimics Van Leeuwen's aesthetic:

| Token | Value | Description |
|-------|-------|-------------|
| Primary | `#1a1a1a` | Main text, buttons |
| Secondary | `#f5e6d3` | Warm cream background |
| Accent | `#c9a87c` | Gold highlights |
| Font Heading | Playfair Display | Elegant serif |
| Font Body | Inter | Clean sans-serif |

Tokens are stored in `ui/theme/tokens.json` and can be manually adjusted.

### Pages

- `/` - Home with hero and featured products
- `/shop` - Product listing with search, filter, sort
- `/product/[slug]` - Product detail with gallery

### How Tokens Are Extracted

The `extract_theme_tokens.py` script:

1. Fetches the homepage HTML
2. Downloads linked CSS files
3. Parses CSS variables and computed styles
4. Extracts colors, fonts, spacing, shadows
5. Categorizes values (primary, background, text, etc.)
6. Outputs `tokens.json` and Tailwind config extension

**Note**: Extracted tokens are approximations. Some values are manually refined to better capture the brand feel.

### Adjusting Tokens

Edit `ui/theme/tokens.json` to customize:

```json
{
  "colors": {
    "primary": ["#1a1a1a"],
    "secondary": ["#f5e6d3"]
  },
  "typography": {
    "fontFamilies": {
      "heading": "'Playfair Display', serif",
      "body": "'Inter', sans-serif"
    }
  }
}
```

Then update `ui/src/app/globals.css` CSS variables to match.
