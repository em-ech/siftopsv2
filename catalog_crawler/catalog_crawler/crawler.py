"""Main async crawler implementation."""

import asyncio
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
import aiofiles
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from rich.progress import Progress, TaskID
from rich.console import Console

from .models import Product, CrawlReport, CrawlState
from .parsers import ProductParser, ListingParser

logger = logging.getLogger(__name__)
console = Console()


class RateLimitError(Exception):
    """Raised when rate limited (429)."""
    pass


class ServerError(Exception):
    """Raised on 5xx errors."""
    pass


class CatalogCrawler:
    """Async catalog crawler with polite defaults."""

    def __init__(
        self,
        base_url: str,
        start_path: str = "/store/",
        output_dir: str = "./out",
        concurrency: int = 5,
        delay: float = 0.5,
        timeout: float = 30.0,
        retries: int = 3,
        max_pages: Optional[int] = None,
        download_images: bool = False,
        force: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.start_path = start_path
        self.output_dir = Path(output_dir)
        self.concurrency = concurrency
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.max_pages = max_pages
        self.download_images = download_images
        self.force = force

        # Parsers
        self.product_parser = ProductParser(base_url)
        self.listing_parser = ListingParser(base_url)

        # State
        self.state = CrawlState()
        self.products: list[Product] = []
        self.semaphore = asyncio.Semaphore(concurrency)

        # Report
        self.report = CrawlReport(
            base_url=base_url,
            start_path=start_path,
            settings={
                "concurrency": concurrency,
                "delay": delay,
                "timeout": timeout,
                "retries": retries,
                "max_pages": max_pages,
            },
        )

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def state_file(self) -> Path:
        return self.output_dir / ".crawl_state.json"

    @property
    def jsonl_file(self) -> Path:
        return self.output_dir / "catalog.jsonl"

    @property
    def csv_file(self) -> Path:
        return self.output_dir / "catalog.csv"

    @property
    def report_file(self) -> Path:
        return self.output_dir / "report.json"

    async def run(self) -> CrawlReport:
        """Run the crawler."""
        self.report.started_at = datetime.utcnow()

        # Load state if resuming
        if not self.force and self.state_file.exists():
            await self._load_state()
            logger.info(f"Resuming crawl with {len(self.state.visited_urls)} visited URLs")
        else:
            # Start fresh
            start_url = urljoin(self.base_url, self.start_path)
            self.state.pending_urls = [start_url]

        # Create HTTP client with polite headers
        headers = {
            "User-Agent": "CatalogCrawler/1.0 (Educational/Research; +https://github.com/example/catalog-crawler)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        async with httpx.AsyncClient(
            timeout=self.timeout,
            headers=headers,
            follow_redirects=True,
        ) as client:
            self.client = client

            with Progress() as progress:
                task = progress.add_task("[cyan]Crawling...", total=None)

                # Phase 1: Discover all product URLs
                await self._discover_products(progress, task)

                # Phase 2: Fetch all product details
                progress.update(task, description="[green]Fetching products...")
                progress.update(task, total=len(self.state.product_urls))
                progress.update(task, completed=0)

                await self._fetch_products(progress, task)

        # Save results
        await self._save_results()

        self.report.completed_at = datetime.utcnow()
        self.report.duration_seconds = (
            self.report.completed_at - self.report.started_at
        ).total_seconds()
        self.report.total_products_found = len(self.products)

        # Save report
        await self._save_report()

        # Clean up state file on success
        if self.state_file.exists():
            self.state_file.unlink()

        return self.report

    async def _discover_products(self, progress: Progress, task: TaskID):
        """Discover all product URLs by crawling listing pages."""
        pages_crawled = 0

        while self.state.pending_urls:
            if self.max_pages and pages_crawled >= self.max_pages:
                logger.info(f"Reached max pages limit: {self.max_pages}")
                break

            url = self.state.pending_urls.pop(0)

            if url in self.state.visited_urls:
                continue

            try:
                html = await self._fetch_page(url)
                self.state.visited_urls.add(url)
                pages_crawled += 1
                self.report.total_pages_crawled = pages_crawled

                progress.update(
                    task,
                    description=f"[cyan]Discovering... ({pages_crawled} pages, {len(self.state.product_urls)} products)",
                )

                # Check if this is a product page
                if self.listing_parser.is_product_page(html):
                    self.state.product_urls.add(url)
                    continue

                # Parse listing page
                result = self.listing_parser.parse(html, url)

                # Add discovered products
                for product_url in result.product_urls:
                    if product_url not in self.state.product_urls:
                        self.state.product_urls.add(product_url)

                # Add new pages to crawl
                for cat_url in result.category_urls:
                    if cat_url not in self.state.visited_urls:
                        if cat_url not in self.state.pending_urls:
                            self.state.pending_urls.append(cat_url)
                            self.report.total_categories_found += 1

                # Add pagination
                for page_url in result.pagination_urls:
                    if page_url not in self.state.visited_urls:
                        if page_url not in self.state.pending_urls:
                            self.state.pending_urls.append(page_url)

                # Save state periodically
                if pages_crawled % 10 == 0:
                    await self._save_state()

            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                self.report.errors.append({"url": url, "error": str(e)})

        logger.info(f"Discovery complete: {len(self.state.product_urls)} products found")

    async def _fetch_products(self, progress: Progress, task: TaskID):
        """Fetch all discovered product pages."""
        product_urls = list(self.state.product_urls)

        # Create tasks with semaphore for concurrency control
        tasks = [
            self._fetch_product_with_semaphore(url, progress, task)
            for url in product_urls
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _fetch_product_with_semaphore(
        self, url: str, progress: Progress, task: TaskID
    ):
        """Fetch a single product with semaphore control."""
        async with self.semaphore:
            try:
                html = await self._fetch_page(url)
                product = self.product_parser.parse(html, url)
                self.products.append(product)
                progress.advance(task)
            except Exception as e:
                logger.error(f"Error fetching product {url}: {e}")
                self.report.errors.append({"url": url, "error": str(e)})
                progress.advance(task)

    @retry(
        retry=retry_if_exception_type((RateLimitError, ServerError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    async def _fetch_page(self, url: str) -> str:
        """Fetch a page with rate limiting and retries."""
        # Polite delay
        await asyncio.sleep(self.delay)

        response = await self.client.get(url)

        if response.status_code == 429:
            logger.warning(f"Rate limited on {url}, backing off...")
            raise RateLimitError(f"Rate limited: {url}")

        if response.status_code >= 500:
            logger.warning(f"Server error {response.status_code} on {url}")
            raise ServerError(f"Server error {response.status_code}: {url}")

        response.raise_for_status()
        return response.text

    async def _save_state(self):
        """Save crawl state for resume capability."""
        state_data = {
            "visited_urls": list(self.state.visited_urls),
            "pending_urls": self.state.pending_urls,
            "product_urls": list(self.state.product_urls),
            "last_updated": datetime.utcnow().isoformat(),
        }
        async with aiofiles.open(self.state_file, "w") as f:
            await f.write(json.dumps(state_data, indent=2))

    async def _load_state(self):
        """Load crawl state for resuming."""
        async with aiofiles.open(self.state_file, "r") as f:
            content = await f.read()
            state_data = json.loads(content)

        self.state.visited_urls = set(state_data.get("visited_urls", []))
        self.state.pending_urls = state_data.get("pending_urls", [])
        self.state.product_urls = set(state_data.get("product_urls", []))

    async def _save_results(self):
        """Save products to JSONL and CSV."""
        # JSONL
        async with aiofiles.open(self.jsonl_file, "w") as f:
            for product in self.products:
                line = product.model_dump_json() + "\n"
                await f.write(line)

        logger.info(f"Saved {len(self.products)} products to {self.jsonl_file}")

        # CSV
        if self.products:
            fieldnames = list(self.products[0].to_flat_dict().keys())
            with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for product in self.products:
                    writer.writerow(product.to_flat_dict())

            logger.info(f"Saved {len(self.products)} products to {self.csv_file}")

    async def _save_report(self):
        """Save crawl report."""
        async with aiofiles.open(self.report_file, "w") as f:
            await f.write(self.report.model_dump_json(indent=2))

        logger.info(f"Saved report to {self.report_file}")
