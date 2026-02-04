"""Tests for Pydantic models."""

import pytest
from datetime import datetime

from catalog_crawler.models import (
    Product,
    ProductImage,
    Category,
    AdditionalInfo,
    CrawlReport,
)


class TestProduct:
    """Tests for Product model."""

    def test_create_minimal_product(self):
        """Test creating product with minimal fields."""
        product = Product(
            product_url="https://example.com/product/test/",
            slug="test",
            name="Test Product",
        )
        assert product.name == "Test Product"
        assert product.slug == "test"
        assert product.in_stock is True
        assert product.categories == []

    def test_create_full_product(self):
        """Test creating product with all fields."""
        product = Product(
            product_url="https://example.com/product/honeycomb/",
            slug="honeycomb",
            name="Honeycomb Ice Cream",
            price_text="$12.00",
            currency_symbol="$",
            regular_price="$12.00",
            stock_text="In stock",
            in_stock=True,
            short_description="Delicious honeycomb ice cream",
            long_description="Full description here...",
            additional_information=[
                AdditionalInfo(key="Weight", value="14 oz"),
            ],
            categories=[
                Category(name="Pints", url="/product-category/pints/", slug="pints"),
            ],
            tags=["vanilla", "honeycomb"],
            main_image=ProductImage(url="https://example.com/image.jpg"),
            gallery_images=[
                ProductImage(url="https://example.com/gallery1.jpg"),
            ],
            ingredients="Cream, Sugar, Honey",
            allergens=["Milk", "Eggs"],
            sku="VL-HC-001",
        )

        assert product.name == "Honeycomb Ice Cream"
        assert len(product.categories) == 1
        assert len(product.additional_information) == 1
        assert product.sku == "VL-HC-001"

    def test_to_flat_dict(self):
        """Test flat dict conversion for CSV export."""
        product = Product(
            product_url="https://example.com/product/test/",
            slug="test",
            name="Test Product",
            categories=[
                Category(name="Pints"),
                Category(name="Classics"),
            ],
            tags=["vanilla", "honeycomb"],
        )

        flat = product.to_flat_dict()
        assert flat["name"] == "Test Product"
        assert flat["categories"] == "Pints, Classics"
        assert flat["tags"] == "vanilla, honeycomb"
        assert "timestamp_collected" in flat


class TestProductImage:
    """Tests for ProductImage model."""

    def test_create_image(self):
        """Test creating image with srcset."""
        image = ProductImage(
            url="https://example.com/image.jpg",
            alt="Test image",
            width=600,
            height=600,
            srcset=[
                {"url": "https://example.com/image-300.jpg", "width": 300},
                {"url": "https://example.com/image-600.jpg", "width": 600},
            ],
        )

        assert image.url == "https://example.com/image.jpg"
        assert len(image.srcset) == 2


class TestCrawlReport:
    """Tests for CrawlReport model."""

    def test_create_report(self):
        """Test creating crawl report."""
        report = CrawlReport(
            base_url="https://example.com",
            start_path="/store/",
            total_pages_crawled=50,
            total_products_found=120,
            started_at=datetime.utcnow(),
        )

        assert report.base_url == "https://example.com"
        assert report.total_products_found == 120
        assert report.errors == []
