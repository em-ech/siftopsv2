"""Product and related models for the catalog crawler."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class ProductImage(BaseModel):
    """Image with srcset variants."""

    url: str
    alt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    srcset: list[dict[str, str | int]] = Field(default_factory=list)


class Category(BaseModel):
    """Product category."""

    name: str
    url: Optional[str] = None
    slug: Optional[str] = None


class AdditionalInfo(BaseModel):
    """Key-value pair from additional information tab."""

    key: str
    value: str


class NutritionInfo(BaseModel):
    """Nutrition information if available."""

    label: str
    value: str


class Product(BaseModel):
    """Complete product record."""

    # Core identifiers
    product_url: str
    slug: str
    name: str

    # Pricing
    price_text: Optional[str] = None
    currency_symbol: Optional[str] = None
    regular_price: Optional[str] = None
    sale_price: Optional[str] = None

    # Availability
    stock_text: Optional[str] = None
    in_stock: bool = True

    # Descriptions
    short_description: Optional[str] = None
    long_description: Optional[str] = None

    # Additional info tab
    additional_information: list[AdditionalInfo] = Field(default_factory=list)

    # Categorization
    categories: list[Category] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    # Images
    main_image: Optional[ProductImage] = None
    gallery_images: list[ProductImage] = Field(default_factory=list)

    # Ingredients/Allergens
    ingredients: Optional[str] = None
    allergens: list[str] = Field(default_factory=list)

    # Nutrition
    nutrition_info: list[NutritionInfo] = Field(default_factory=list)
    nutrition_pdf_url: Optional[str] = None

    # Metadata
    sku: Optional[str] = None
    timestamp_collected: datetime = Field(default_factory=datetime.utcnow)

    def to_flat_dict(self) -> dict:
        """Convert to flat dictionary for CSV export."""
        return {
            "product_url": self.product_url,
            "slug": self.slug,
            "name": self.name,
            "price_text": self.price_text,
            "currency_symbol": self.currency_symbol,
            "regular_price": self.regular_price,
            "sale_price": self.sale_price,
            "stock_text": self.stock_text,
            "in_stock": self.in_stock,
            "short_description": self.short_description,
            "long_description": self.long_description,
            "categories": ", ".join(c.name for c in self.categories),
            "tags": ", ".join(self.tags),
            "main_image_url": self.main_image.url if self.main_image else None,
            "gallery_image_count": len(self.gallery_images),
            "ingredients": self.ingredients,
            "allergens": ", ".join(self.allergens),
            "sku": self.sku,
            "timestamp_collected": self.timestamp_collected.isoformat(),
        }


class CrawlState(BaseModel):
    """State for resume capability."""

    visited_urls: set[str] = Field(default_factory=set)
    pending_urls: list[str] = Field(default_factory=list)
    product_urls: set[str] = Field(default_factory=set)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True


class CrawlReport(BaseModel):
    """Summary report of the crawl."""

    base_url: str
    start_path: str
    total_pages_crawled: int = 0
    total_products_found: int = 0
    total_categories_found: int = 0
    errors: list[dict] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    duration_seconds: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    settings: dict = Field(default_factory=dict)
