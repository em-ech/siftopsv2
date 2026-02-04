"""Parser for product listing/category pages."""

import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import NamedTuple


class ListingParseResult(NamedTuple):
    """Result of parsing a listing page."""

    product_urls: list[str]
    category_urls: list[str]
    pagination_urls: list[str]
    next_page_url: str | None


class ListingParser:
    """Parser for WooCommerce product listing pages."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def parse(self, html: str, current_url: str) -> ListingParseResult:
        """Parse a listing page and extract URLs."""
        soup = BeautifulSoup(html, "lxml")

        product_urls = self._extract_product_urls(soup, current_url)
        category_urls = self._extract_category_urls(soup, current_url)
        pagination_urls, next_page = self._extract_pagination(soup, current_url)

        return ListingParseResult(
            product_urls=product_urls,
            category_urls=category_urls,
            pagination_urls=pagination_urls,
            next_page_url=next_page,
        )

    def _extract_product_urls(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Extract product URLs from listing page."""
        product_urls = set()

        # WooCommerce product links - multiple selectors for different themes
        selectors = [
            "a.woocommerce-LoopProduct-link",
            ".product a.woocommerce-loop-product__link",
            ".products .product a[href*='/product/']",
            ".product-item a[href*='/product/']",
            "li.product a[href]",
            ".wc-block-grid__product a[href]",
            "a[href*='/product/']",
        ]

        for selector in selectors:
            for link in soup.select(selector):
                href = link.get("href")
                if href and "/product/" in href:
                    full_url = urljoin(current_url, href)
                    # Only include URLs from same domain
                    if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                        product_urls.add(full_url.split("?")[0].split("#")[0])

        return list(product_urls)

    def _extract_category_urls(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Extract category URLs from the page."""
        category_urls = set()

        # Category links
        selectors = [
            ".product-categories a",
            ".widget_product_categories a",
            "a[href*='/product-category/']",
            ".wc-block-product-categories a",
            "nav.woocommerce-breadcrumb a",
            ".cat-item a",
        ]

        for selector in selectors:
            for link in soup.select(selector):
                href = link.get("href")
                if href and "/product-category/" in href:
                    full_url = urljoin(current_url, href)
                    if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                        category_urls.add(full_url.split("?")[0].split("#")[0])

        return list(category_urls)

    def _extract_pagination(
        self, soup: BeautifulSoup, current_url: str
    ) -> tuple[list[str], str | None]:
        """Extract pagination URLs and next page."""
        pagination_urls = set()
        next_page = None

        # Pagination links
        selectors = [
            ".woocommerce-pagination a",
            ".page-numbers a",
            "nav.pagination a",
            ".pagination a",
        ]

        for selector in selectors:
            for link in soup.select(selector):
                href = link.get("href")
                if href:
                    full_url = urljoin(current_url, href)
                    if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                        pagination_urls.add(full_url)

                    # Check if this is the "next" link
                    classes = link.get("class", [])
                    if "next" in classes or link.get("rel") == ["next"]:
                        next_page = full_url

        # Also look for next in rel links
        next_link = soup.find("a", rel="next")
        if next_link and next_link.get("href"):
            next_page = urljoin(current_url, next_link["href"])

        return list(pagination_urls), next_page

    def is_product_page(self, html: str) -> bool:
        """Check if the page is a single product page."""
        soup = BeautifulSoup(html, "lxml")

        # Check for product page indicators
        indicators = [
            soup.select_one(".single-product"),
            soup.select_one(".product_title"),
            soup.select_one(".woocommerce-product-gallery"),
            soup.select_one("form.cart"),
            soup.select_one(".single_add_to_cart_button"),
        ]

        return any(indicators)
