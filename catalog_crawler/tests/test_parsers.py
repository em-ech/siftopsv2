"""Tests for HTML parsers."""

import pytest
from pathlib import Path

from catalog_crawler.parsers import ProductParser, ListingParser


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def product_html():
    """Load product page HTML fixture."""
    return (FIXTURES_DIR / "product_page.html").read_text()


@pytest.fixture
def listing_html():
    """Load listing page HTML fixture."""
    return (FIXTURES_DIR / "listing_page.html").read_text()


class TestProductParser:
    """Tests for ProductParser."""

    @pytest.fixture
    def parser(self):
        return ProductParser("https://vanleeuwenicecream.com")

    def test_parse_name(self, parser, product_html):
        """Test product name extraction."""
        product = parser.parse(product_html, "https://vanleeuwenicecream.com/product/honeycomb/")
        assert product.name == "Honeycomb Ice Cream"

    def test_parse_slug(self, parser, product_html):
        """Test slug extraction from URL."""
        product = parser.parse(product_html, "https://vanleeuwenicecream.com/product/honeycomb/")
        assert product.slug == "honeycomb"

    def test_parse_price(self, parser, product_html):
        """Test price extraction."""
        product = parser.parse(product_html, "https://vanleeuwenicecream.com/product/honeycomb/")
        assert product.currency_symbol == "$"
        assert product.regular_price == "$12.00"

    def test_parse_stock(self, parser, product_html):
        """Test stock status extraction."""
        product = parser.parse(product_html, "https://vanleeuwenicecream.com/product/honeycomb/")
        assert product.in_stock is True
        assert "In stock" in product.stock_text

    def test_parse_descriptions(self, parser, product_html):
        """Test description extraction."""
        product = parser.parse(product_html, "https://vanleeuwenicecream.com/product/honeycomb/")
        assert "honeycomb toffee pieces" in product.short_description
        assert "local apiaries" in product.long_description

    def test_parse_additional_info(self, parser, product_html):
        """Test additional information extraction."""
        product = parser.parse(product_html, "https://vanleeuwenicecream.com/product/honeycomb/")
        assert len(product.additional_information) == 2
        weights = [info for info in product.additional_information if info.key == "Weight"]
        assert len(weights) == 1
        assert weights[0].value == "14 oz"

    def test_parse_categories(self, parser, product_html):
        """Test category extraction."""
        product = parser.parse(product_html, "https://vanleeuwenicecream.com/product/honeycomb/")
        category_names = [c.name for c in product.categories]
        assert "Pints" in category_names
        assert "Classics" in category_names

    def test_parse_tags(self, parser, product_html):
        """Test tag extraction."""
        product = parser.parse(product_html, "https://vanleeuwenicecream.com/product/honeycomb/")
        assert "vanilla" in product.tags
        assert "honeycomb" in product.tags

    def test_parse_images(self, parser, product_html):
        """Test image extraction."""
        product = parser.parse(product_html, "https://vanleeuwenicecream.com/product/honeycomb/")
        assert product.main_image is not None
        # Should pick largest from srcset
        assert "1200" in product.main_image.url
        assert len(product.main_image.srcset) == 3

    def test_parse_sku(self, parser, product_html):
        """Test SKU extraction."""
        product = parser.parse(product_html, "https://vanleeuwenicecream.com/product/honeycomb/")
        assert product.sku == "VL-HC-001"


class TestListingParser:
    """Tests for ListingParser."""

    @pytest.fixture
    def parser(self):
        return ListingParser("https://vanleeuwenicecream.com")

    def test_extract_product_urls(self, parser, listing_html):
        """Test product URL extraction."""
        result = parser.parse(listing_html, "https://vanleeuwenicecream.com/store/")
        assert len(result.product_urls) == 3
        assert "https://vanleeuwenicecream.com/product/honeycomb/" in result.product_urls
        assert "https://vanleeuwenicecream.com/product/sicilian-pistachio/" in result.product_urls

    def test_extract_category_urls(self, parser, listing_html):
        """Test category URL extraction."""
        result = parser.parse(listing_html, "https://vanleeuwenicecream.com/store/")
        assert len(result.category_urls) == 3
        assert "https://vanleeuwenicecream.com/product-category/pints/" in result.category_urls
        assert "https://vanleeuwenicecream.com/product-category/vegan/" in result.category_urls

    def test_extract_pagination(self, parser, listing_html):
        """Test pagination extraction."""
        result = parser.parse(listing_html, "https://vanleeuwenicecream.com/store/page/2/")
        assert len(result.pagination_urls) > 0
        assert result.next_page_url == "https://vanleeuwenicecream.com/store/page/3/"

    def test_is_product_page_false(self, parser, listing_html):
        """Test that listing page is not detected as product page."""
        assert parser.is_product_page(listing_html) is False

    def test_is_product_page_true(self, parser, product_html):
        """Test that product page is detected correctly."""
        product_html = (FIXTURES_DIR / "product_page.html").read_text()
        assert parser.is_product_page(product_html) is True
