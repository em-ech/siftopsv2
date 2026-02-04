"""Parser for individual product pages."""

import re
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag
from typing import Optional

from ..models import (
    Product,
    ProductImage,
    Category,
    AdditionalInfo,
    NutritionInfo,
)


class ProductParser:
    """Parser for WooCommerce product pages."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def parse(self, html: str, product_url: str) -> Product:
        """Parse a product page and extract all data."""
        soup = BeautifulSoup(html, "lxml")

        # Extract slug from URL
        slug = self._extract_slug(product_url)

        # Extract all product data
        name = self._extract_name(soup)
        price_info = self._extract_price(soup)
        stock_info = self._extract_stock(soup)
        descriptions = self._extract_descriptions(soup)
        additional_info = self._extract_additional_info(soup)
        categories = self._extract_categories(soup, product_url)
        tags = self._extract_tags(soup)
        images = self._extract_images(soup, product_url)
        ingredients_allergens = self._extract_ingredients_allergens(soup)
        nutrition = self._extract_nutrition(soup, product_url)
        sku = self._extract_sku(soup)

        return Product(
            product_url=product_url,
            slug=slug,
            name=name,
            price_text=price_info.get("price_text"),
            currency_symbol=price_info.get("currency"),
            regular_price=price_info.get("regular_price"),
            sale_price=price_info.get("sale_price"),
            stock_text=stock_info.get("text"),
            in_stock=stock_info.get("in_stock", True),
            short_description=descriptions.get("short"),
            long_description=descriptions.get("long"),
            additional_information=additional_info,
            categories=categories,
            tags=tags,
            main_image=images.get("main"),
            gallery_images=images.get("gallery", []),
            ingredients=ingredients_allergens.get("ingredients"),
            allergens=ingredients_allergens.get("allergens", []),
            nutrition_info=nutrition.get("info", []),
            nutrition_pdf_url=nutrition.get("pdf_url"),
            sku=sku,
            timestamp_collected=datetime.utcnow(),
        )

    def _extract_slug(self, url: str) -> str:
        """Extract product slug from URL."""
        path = urlparse(url).path
        # Remove trailing slash and get last segment
        segments = [s for s in path.split("/") if s]
        return segments[-1] if segments else ""

    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract product name."""
        selectors = [
            ".product_title",
            "h1.entry-title",
            ".single-product h1",
            "h1[itemprop='name']",
            ".product-title h1",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        # Fallback to first h1
        h1 = soup.find("h1")
        return h1.get_text(strip=True) if h1 else "Unknown Product"

    def _extract_price(self, soup: BeautifulSoup) -> dict:
        """Extract price information."""
        result = {
            "price_text": None,
            "currency": None,
            "regular_price": None,
            "sale_price": None,
        }

        # Find price container
        price_container = soup.select_one(".price") or soup.select_one(
            "[itemprop='price']"
        )

        if price_container:
            result["price_text"] = price_container.get_text(strip=True)

            # Extract currency symbol
            currency = price_container.select_one(".woocommerce-Price-currencySymbol")
            if currency:
                result["currency"] = currency.get_text(strip=True)

            # Check for sale price
            del_price = price_container.select_one("del .amount")
            ins_price = price_container.select_one("ins .amount")

            if del_price and ins_price:
                result["regular_price"] = del_price.get_text(strip=True)
                result["sale_price"] = ins_price.get_text(strip=True)
            else:
                amount = price_container.select_one(".amount")
                if amount:
                    result["regular_price"] = amount.get_text(strip=True)

        # Try meta tag fallback
        if not result["regular_price"]:
            meta_price = soup.select_one('meta[itemprop="price"]')
            if meta_price:
                result["regular_price"] = meta_price.get("content")

        return result

    def _extract_stock(self, soup: BeautifulSoup) -> dict:
        """Extract stock information."""
        result = {"text": None, "in_stock": True}

        # Check stock status
        stock_elem = soup.select_one(".stock")
        if stock_elem:
            result["text"] = stock_elem.get_text(strip=True)
            classes = stock_elem.get("class", [])
            result["in_stock"] = "out-of-stock" not in classes

        # Check for out of stock badge
        if soup.select_one(".out-of-stock") or soup.select_one(".sold-out"):
            result["in_stock"] = False
            if not result["text"]:
                result["text"] = "Out of Stock"

        return result

    def _extract_descriptions(self, soup: BeautifulSoup) -> dict:
        """Extract short and long descriptions."""
        result = {"short": None, "long": None}

        # Short description
        short_desc = soup.select_one(".woocommerce-product-details__short-description")
        if short_desc:
            result["short"] = self._clean_html_text(short_desc)

        # Long description - check tabs
        desc_tab = soup.select_one("#tab-description")
        if desc_tab:
            result["long"] = self._clean_html_text(desc_tab)
        else:
            # Try product description div
            desc_div = soup.select_one(".product-description")
            if desc_div:
                result["long"] = self._clean_html_text(desc_div)

        return result

    def _extract_additional_info(self, soup: BeautifulSoup) -> list[AdditionalInfo]:
        """Extract additional information tab data."""
        info_list = []

        # Find additional info tab
        info_tab = soup.select_one("#tab-additional_information")
        if info_tab:
            # Look for table rows
            for row in info_tab.select("tr"):
                th = row.select_one("th")
                td = row.select_one("td")
                if th and td:
                    info_list.append(
                        AdditionalInfo(
                            key=th.get_text(strip=True),
                            value=td.get_text(strip=True),
                        )
                    )

        # Also check for attribute list format
        attr_list = soup.select(".woocommerce-product-attributes tr")
        for row in attr_list:
            label = row.select_one(".woocommerce-product-attributes-item__label")
            value = row.select_one(".woocommerce-product-attributes-item__value")
            if label and value:
                info_list.append(
                    AdditionalInfo(
                        key=label.get_text(strip=True),
                        value=value.get_text(strip=True),
                    )
                )

        return info_list

    def _extract_categories(self, soup: BeautifulSoup, current_url: str) -> list[Category]:
        """Extract product categories."""
        categories = []
        seen_names = set()

        # Category links
        selectors = [
            ".posted_in a",
            ".product_meta a[rel='tag']",
            "a[href*='/product-category/']",
        ]

        for selector in selectors:
            for link in soup.select(selector):
                href = link.get("href", "")
                if "/product-category/" in href:
                    name = link.get_text(strip=True)
                    if name and name not in seen_names:
                        seen_names.add(name)
                        full_url = urljoin(current_url, href)
                        slug = href.rstrip("/").split("/")[-1]
                        categories.append(
                            Category(name=name, url=full_url, slug=slug)
                        )

        return categories

    def _extract_tags(self, soup: BeautifulSoup) -> list[str]:
        """Extract product tags."""
        tags = []

        tag_container = soup.select_one(".tagged_as")
        if tag_container:
            for link in tag_container.select("a"):
                tag = link.get_text(strip=True)
                if tag:
                    tags.append(tag)

        return tags

    def _extract_images(self, soup: BeautifulSoup, current_url: str) -> dict:
        """Extract main and gallery images with srcset."""
        result = {"main": None, "gallery": []}
        seen_urls = set()

        # Main image
        main_selectors = [
            ".woocommerce-product-gallery__image img",
            ".wp-post-image",
            ".product-image img",
            ".single-product img.attachment-shop_single",
        ]

        for selector in main_selectors:
            img = soup.select_one(selector)
            if img:
                image = self._parse_image(img, current_url)
                if image and image.url not in seen_urls:
                    result["main"] = image
                    seen_urls.add(image.url)
                    break

        # Gallery images
        gallery_selectors = [
            ".woocommerce-product-gallery__image",
            ".product-gallery-image",
            ".flex-control-thumbs img",
        ]

        for selector in gallery_selectors:
            for elem in soup.select(selector):
                # Check for img directly or nested
                img = elem if elem.name == "img" else elem.select_one("img")
                if img:
                    image = self._parse_image(img, current_url)
                    if image and image.url not in seen_urls:
                        result["gallery"].append(image)
                        seen_urls.add(image.url)

                # Check data-large_image attribute
                large_src = elem.get("data-large_image") or elem.get("data-src")
                if large_src and large_src not in seen_urls:
                    full_url = urljoin(current_url, large_src)
                    result["gallery"].append(
                        ProductImage(
                            url=full_url,
                            width=int(elem.get("data-large_image_width", 0)) or None,
                            height=int(elem.get("data-large_image_height", 0)) or None,
                        )
                    )
                    seen_urls.add(full_url)

        return result

    def _parse_image(self, img: Tag, current_url: str) -> Optional[ProductImage]:
        """Parse an img tag into ProductImage with srcset."""
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        if not src:
            return None

        full_url = urljoin(current_url, src)

        # Parse srcset
        srcset_data = []
        srcset = img.get("srcset") or img.get("data-srcset")
        if srcset:
            for entry in srcset.split(","):
                entry = entry.strip()
                parts = entry.split()
                if len(parts) >= 2:
                    url = urljoin(current_url, parts[0])
                    width_str = parts[1].rstrip("w")
                    try:
                        width = int(width_str)
                        srcset_data.append({"url": url, "width": width})
                    except ValueError:
                        srcset_data.append({"url": url, "descriptor": parts[1]})

        # Prefer largest srcset image
        if srcset_data:
            largest = max(
                (s for s in srcset_data if isinstance(s.get("width"), int)),
                key=lambda x: x.get("width", 0),
                default=None,
            )
            if largest:
                full_url = largest["url"]

        return ProductImage(
            url=full_url,
            alt=img.get("alt"),
            width=int(img.get("width", 0)) or None,
            height=int(img.get("height", 0)) or None,
            srcset=srcset_data,
        )

    def _extract_ingredients_allergens(self, soup: BeautifulSoup) -> dict:
        """Extract ingredients and allergens if visible."""
        result = {"ingredients": None, "allergens": []}

        # Look for ingredients section
        ingredient_keywords = ["ingredient", "ingredients", "contains"]
        allergen_keywords = ["allergen", "allergy", "may contain"]

        for elem in soup.find_all(["div", "section", "p", "span"]):
            text = elem.get_text(strip=True).lower()

            for keyword in ingredient_keywords:
                if keyword in text and len(text) < 2000:
                    # Get the actual content
                    content = elem.get_text(strip=True)
                    if not result["ingredients"] or len(content) > len(
                        result["ingredients"]
                    ):
                        result["ingredients"] = content

            for keyword in allergen_keywords:
                if keyword in text:
                    # Extract allergen list
                    content = elem.get_text(strip=True)
                    # Try to parse comma-separated allergens
                    if ":" in content:
                        allergens_part = content.split(":", 1)[1]
                        allergens = [a.strip() for a in allergens_part.split(",")]
                        result["allergens"].extend(allergens)

        # Dedupe allergens
        result["allergens"] = list(set(result["allergens"]))

        return result

    def _extract_nutrition(self, soup: BeautifulSoup, current_url: str) -> dict:
        """Extract nutrition information and PDF links."""
        result = {"info": [], "pdf_url": None}

        # Look for nutrition table
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if any(
                kw in " ".join(headers)
                for kw in ["nutrition", "calories", "fat", "protein"]
            ):
                for row in table.find_all("tr"):
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 2:
                        result["info"].append(
                            NutritionInfo(
                                label=cells[0].get_text(strip=True),
                                value=cells[1].get_text(strip=True),
                            )
                        )

        # Look for PDF links
        for link in soup.find_all("a", href=True):
            href = link["href"].lower()
            text = link.get_text(strip=True).lower()
            if ".pdf" in href and any(
                kw in text or kw in href for kw in ["nutrition", "ingredient", "spec"]
            ):
                result["pdf_url"] = urljoin(current_url, link["href"])
                break

        return result

    def _extract_sku(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product SKU."""
        sku_elem = soup.select_one(".sku")
        if sku_elem:
            return sku_elem.get_text(strip=True)

        # Check meta
        meta_sku = soup.select_one('meta[itemprop="sku"]')
        if meta_sku:
            return meta_sku.get("content")

        return None

    def _clean_html_text(self, element: Tag) -> str:
        """Extract clean text from HTML element."""
        # Remove script and style elements
        for tag in element.find_all(["script", "style"]):
            tag.decompose()

        # Get text with some structure preservation
        text = element.get_text(separator="\n", strip=True)

        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)
