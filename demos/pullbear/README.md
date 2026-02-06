# Pull & Bear Demo Store

A demo storefront showcasing Sift Retail AI's semantic search and RAG-powered chat capabilities.

## Overview

This demo includes:
- **UI**: Next.js storefront with integrated Sift AI search and chat
- **Catalog**: Sample Pull & Bear product catalog (~50 products)

## Directory Structure

```
pullbear/
├── ui/                     # Next.js storefront application
│   ├── src/
│   │   ├── app/           # Next.js app routes
│   │   ├── components/    # React components
│   │   └── lib/           # API client and utilities
│   └── public/            # Static assets and widgets
├── catalog/
│   ├── data/
│   │   └── pullbear_catalog.json    # Product catalog
│   └── scripts/
│       └── seed.py        # Database seeder script
└── README.md              # This file
```

## Quick Start

### Prerequisites

1. Backend server configured with `.env` file (see `/backend/.env.example`)
2. Supabase and Qdrant credentials set
3. Node.js 18+ and Python 3.11+

### Step 1: Seed the Catalog

From the project root (`siftopsv2/`):

```bash
# Install backend dependencies (if not done)
cd backend
uv sync

# Seed the catalog
cd ../demos/pullbear/catalog/scripts
python seed.py
```

Or using the backend's built-in seed script:

```bash
cd backend
uv run python scripts/seed_pullbear.py
```

### Step 2: Start the Backend

```bash
cd backend
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Step 3: Start the UI

```bash
cd demos/pullbear/ui
npm install
npm run dev
```

The demo store will be available at `http://localhost:3000`

## Features

### Semantic Search
- Natural language queries like "blue hoodie under $30"
- Budget extraction and filtering
- Category, color, and style understanding

### AI Chat
- RAG-powered shopping assistant
- Zero hallucination (only references actual products)
- Multi-turn conversations

### Image Search (v2)
- Upload product images to find similar items
- GPT-4V powered visual analysis
- Extracts color, style, category from images

## API Endpoints

The UI connects to these backend endpoints:

| Endpoint | Description |
|----------|-------------|
| `POST /search/` | Semantic search with query understanding |
| `POST /search/v2/search` | Enhanced search with validation |
| `POST /chat/` | RAG-powered chat |
| `POST /chat/image` | Image-based search |
| `GET /search/quick` | Fast autocomplete search |

## Customization

### Changing the Tenant

Update the tenant ID in `ui/src/lib/api.ts`:

```typescript
const TENANT_ID = "pullbear";  // Change to your tenant ID
const STORE_NAME = "Pull & Bear";  // Change to your store name
```

### Adding Products

1. Add products to `catalog/data/pullbear_catalog.json`
2. Re-run the seed script
3. Products will be updated in the database

### Catalog Format

```json
[
  {
    "id": "unique-id",
    "name": "Product Name",
    "description": "Product description...",
    "price": 29.99,
    "category": "T-shirts",
    "image_url": "https://...",
    "brand": "Pull & Bear",
    "tags": "casual,streetwear,graphic"
  }
]
```

## Testing

### Test Search

```bash
# Semantic search
curl -X POST http://localhost:8000/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "blue hoodie under $30", "tenant_id": "pullbear"}'

# Enhanced search with validation
curl -X POST http://localhost:8000/search/v2/search \
  -H "Content-Type: application/json" \
  -d '{"query": "casual t-shirt", "tenant_id": "pullbear", "strategy": "validated"}'
```

### Test Chat

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What do you have for a summer party?", "tenant_id": "pullbear", "store_name": "Pull & Bear"}'
```

### Test Image Search

```bash
curl -X POST http://localhost:8000/chat/image \
  -F "image=@test_image.jpg" \
  -F "tenant_id=pullbear"
```

## Troubleshooting

### "No products found"

1. Make sure you ran the seed script
2. Check the backend logs for errors
3. Verify Qdrant connection in `.env`

### "Connection refused"

1. Make sure the backend is running on port 8000
2. Check CORS settings in `backend/app/main.py`

### Slow search

1. Enable caching: `CACHE_ENABLED=true`
2. Use "fast" strategy for lower latency: `"strategy": "fast"`

## License

Part of Sift Retail AI - see project root for license details.
