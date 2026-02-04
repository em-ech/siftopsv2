# Catalog Crawler

A polite, scalable catalog collector for WooCommerce storefronts. Designed for ethical data collection with configurable rate limiting, retry logic, and resume capability.

## Features

- **Polite Crawling**: Configurable delays, concurrency limits, and exponential backoff
- **Resume Capability**: Saves state to disk, can resume interrupted crawls
- **Rich Data Extraction**: Extracts comprehensive product information including:
  - Product name, slug, SKU
  - Prices (regular and sale)
  - Stock status
  - Short and long descriptions
  - Additional information (from tabs)
  - Categories and tags
  - Images with srcset variants
  - Ingredients and allergens (if visible)
  - Nutrition information (if available)
- **Multiple Output Formats**: JSONL, CSV, and summary report
- **Async Architecture**: Built with httpx and asyncio for efficient crawling

## Installation

```bash
cd catalog_crawler
pip install -e .
```

Or with uv:

```bash
cd catalog_crawler
uv pip install -e .
```

## Usage

### Basic Usage

```bash
python -m catalog_crawler --base-url https://vanleeuwenicecream.com --start /store/
```

### All Options

```bash
python -m catalog_crawler \
  --base-url https://vanleeuwenicecream.com \
  --start /store/ \
  --out ./out \
  --concurrency 5 \
  --delay 0.5 \
  --timeout 30 \
  --retries 3 \
  --max-pages 100 \
  --log-level INFO
```

### CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--base-url` | `https://vanleeuwenicecream.com` | Base URL of the store |
| `--start` | `/store/` | Starting path for crawl |
| `--out` | `./out` | Output directory |
| `--concurrency` | `5` | Maximum concurrent requests |
| `--delay` | `0.5` | Delay between requests (seconds) |
| `--timeout` | `30` | Request timeout (seconds) |
| `--retries` | `3` | Number of retries for failed requests |
| `--max-pages` | None | Maximum pages to crawl (unlimited if not set) |
| `--download-images` | `false` | Download product images locally |
| `--force` | `false` | Force fresh crawl, ignore saved state |
| `--log-level` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Output Files

After a successful crawl, the output directory contains:

```
out/
├── catalog.jsonl      # Products in JSON Lines format (one per line)
├── catalog.csv        # Products in CSV format
└── report.json        # Crawl summary and statistics
```

### JSONL Format

Each line in `catalog.jsonl` is a complete product record:

```json
{
  "product_url": "https://example.com/product/honeycomb/",
  "slug": "honeycomb",
  "name": "Honeycomb Ice Cream",
  "price_text": "$12.00",
  "currency_symbol": "$",
  "regular_price": "$12.00",
  "sale_price": null,
  "stock_text": "In stock",
  "in_stock": true,
  "short_description": "Rich and creamy...",
  "long_description": "Full description...",
  "additional_information": [
    {"key": "Weight", "value": "14 oz"}
  ],
  "categories": [
    {"name": "Pints", "url": "/product-category/pints/", "slug": "pints"}
  ],
  "tags": ["vanilla", "honeycomb"],
  "main_image": {
    "url": "https://example.com/honeycomb.jpg",
    "alt": "Honeycomb Ice Cream",
    "srcset": [...]
  },
  "gallery_images": [...],
  "ingredients": "Cream, Sugar, Honey...",
  "allergens": ["Milk", "Eggs"],
  "sku": "VL-HC-001",
  "timestamp_collected": "2024-01-15T10:30:00Z"
}
```

## Resume Capability

The crawler automatically saves its state to `.crawl_state.json` in the output directory. If a crawl is interrupted:

```bash
# Simply run the same command again - it will resume from where it left off
python -m catalog_crawler --base-url https://vanleeuwenicecream.com

# To start fresh, use --force
python -m catalog_crawler --base-url https://vanleeuwenicecream.com --force
```

## Rate Limiting & Politeness

The crawler implements several politeness features:

1. **Configurable Delay**: Default 0.5s between requests
2. **Concurrency Limit**: Default 5 concurrent requests
3. **Exponential Backoff**: On 429 (rate limit) or 5xx errors
4. **Respectful User-Agent**: Identifies itself clearly
5. **Robots.txt**: Manual review recommended before crawling

## Project Structure

```
catalog_crawler/
├── catalog_crawler/
│   ├── __init__.py
│   ├── __main__.py          # CLI entry point
│   ├── cli.py               # Click CLI implementation
│   ├── crawler.py           # Main crawler logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── product.py       # Pydantic models
│   └── parsers/
│       ├── __init__.py
│       ├── listing_parser.py  # Category/listing page parser
│       └── product_parser.py  # Product detail page parser
├── tests/
│   ├── fixtures/            # HTML test fixtures
│   ├── test_models.py
│   └── test_parsers.py
└── pyproject.toml
```

## Running Tests

```bash
cd catalog_crawler
pip install -e ".[dev]"
pytest
```

## Ethical Considerations

This tool is designed for:
- Educational purposes
- Research and analysis
- Building demos and prototypes

Please ensure you:
- Respect robots.txt directives
- Don't overload servers (use conservative settings)
- Don't use collected data for commercial purposes without permission
- Comply with the website's terms of service

## License

MIT
