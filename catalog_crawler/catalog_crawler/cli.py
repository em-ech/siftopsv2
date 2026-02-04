"""Command-line interface for the catalog crawler."""

import asyncio
import logging
import sys

import click
from rich.console import Console
from rich.logging import RichHandler

from .crawler import CatalogCrawler

console = Console()


def setup_logging(log_level: str):
    """Configure logging with rich handler."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@click.command()
@click.option(
    "--base-url",
    default="https://vanleeuwenicecream.com",
    help="Base URL of the WooCommerce store",
)
@click.option(
    "--start",
    default="/store/",
    help="Starting path for crawl",
)
@click.option(
    "--out",
    default="./out",
    help="Output directory for results",
)
@click.option(
    "--concurrency",
    default=5,
    type=int,
    help="Maximum concurrent requests",
)
@click.option(
    "--delay",
    default=0.5,
    type=float,
    help="Delay between requests in seconds",
)
@click.option(
    "--timeout",
    default=30.0,
    type=float,
    help="Request timeout in seconds",
)
@click.option(
    "--retries",
    default=3,
    type=int,
    help="Number of retries for failed requests",
)
@click.option(
    "--max-pages",
    default=None,
    type=int,
    help="Maximum number of pages to crawl (None for unlimited)",
)
@click.option(
    "--download-images",
    is_flag=True,
    help="Download product images locally",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force fresh crawl, ignore saved state",
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Logging level",
)
def main(
    base_url: str,
    start: str,
    out: str,
    concurrency: int,
    delay: float,
    timeout: float,
    retries: int,
    max_pages: int | None,
    download_images: bool,
    force: bool,
    log_level: str,
):
    """
    Catalog Crawler - A polite WooCommerce catalog collector.

    Crawls a WooCommerce storefront and extracts product catalog data
    with respectful rate limiting and resume capability.

    Example:
        python -m catalog_crawler --base-url https://vanleeuwenicecream.com --start /store/
    """
    setup_logging(log_level)

    console.print(f"[bold cyan]Catalog Crawler[/bold cyan]")
    console.print(f"Base URL: {base_url}")
    console.print(f"Start path: {start}")
    console.print(f"Output: {out}")
    console.print(f"Concurrency: {concurrency}, Delay: {delay}s")
    console.print()

    crawler = CatalogCrawler(
        base_url=base_url,
        start_path=start,
        output_dir=out,
        concurrency=concurrency,
        delay=delay,
        timeout=timeout,
        retries=retries,
        max_pages=max_pages,
        download_images=download_images,
        force=force,
    )

    try:
        report = asyncio.run(crawler.run())

        console.print()
        console.print("[bold green]Crawl Complete![/bold green]")
        console.print(f"Pages crawled: {report.total_pages_crawled}")
        console.print(f"Products found: {report.total_products_found}")
        console.print(f"Categories found: {report.total_categories_found}")
        console.print(f"Duration: {report.duration_seconds:.1f}s")

        if report.errors:
            console.print(f"[yellow]Errors: {len(report.errors)}[/yellow]")

        console.print()
        console.print(f"Results saved to: {out}/")

    except KeyboardInterrupt:
        console.print("\n[yellow]Crawl interrupted. State saved for resume.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
