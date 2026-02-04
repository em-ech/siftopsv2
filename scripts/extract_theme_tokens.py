#!/usr/bin/env python3
"""
Theme Token Extractor

Extracts design tokens (colors, fonts, spacing) from a website's HTML and CSS
to create a tokenized theme that mimics the site's aesthetic.

Usage:
    python scripts/extract_theme_tokens.py --url https://vanleeuwenicecream.com --output ui/theme/tokens.json
"""

import argparse
import json
import re
import asyncio
from pathlib import Path
from urllib.parse import urljoin, urlparse
from collections import Counter
from typing import Optional

import httpx
from bs4 import BeautifulSoup


class ThemeExtractor:
    """Extracts design tokens from a website."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.css_content = ""
        self.html_content = ""

    async def extract(self) -> dict:
        """Extract all theme tokens."""
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "ThemeExtractor/1.0 (Educational/Research)",
            },
        ) as client:
            # Fetch homepage
            response = await client.get(self.base_url)
            self.html_content = response.text

            # Parse HTML to find CSS links
            soup = BeautifulSoup(self.html_content, "lxml")

            # Collect CSS from linked stylesheets
            css_links = soup.find_all("link", rel="stylesheet")
            for link in css_links[:10]:  # Limit to first 10 stylesheets
                href = link.get("href")
                if href:
                    css_url = urljoin(self.base_url, href)
                    try:
                        css_response = await client.get(css_url)
                        self.css_content += "\n" + css_response.text
                    except Exception as e:
                        print(f"Warning: Could not fetch {css_url}: {e}")

            # Also extract inline styles
            for style in soup.find_all("style"):
                self.css_content += "\n" + (style.string or "")

        # Extract tokens
        tokens = {
            "colors": self._extract_colors(),
            "typography": self._extract_typography(),
            "spacing": self._extract_spacing(),
            "borders": self._extract_borders(),
            "shadows": self._extract_shadows(),
            "buttons": self._extract_button_styles(),
            "cards": self._extract_card_styles(),
            "meta": {
                "source_url": self.base_url,
                "extracted_at": str(asyncio.get_event_loop().time()),
                "note": "Tokens are approximations extracted from computed styles",
            },
        }

        return tokens

    def _extract_colors(self) -> dict:
        """Extract color palette from CSS."""
        colors = {
            "primary": [],
            "secondary": [],
            "neutral": [],
            "background": [],
            "text": [],
            "accent": [],
        }

        # CSS custom properties (variables)
        var_pattern = r"--[\w-]+:\s*(#[0-9a-fA-F]{3,8}|rgb[a]?\([^)]+\)|[a-z]+)"
        for match in re.finditer(var_pattern, self.css_content, re.IGNORECASE):
            var_name = match.group(0).split(":")[0].strip()
            color_value = match.group(1).strip()

            # Categorize by variable name
            if any(kw in var_name.lower() for kw in ["primary", "brand", "main"]):
                colors["primary"].append(color_value)
            elif any(kw in var_name.lower() for kw in ["secondary", "accent"]):
                colors["secondary"].append(color_value)
            elif any(kw in var_name.lower() for kw in ["bg", "background"]):
                colors["background"].append(color_value)
            elif any(kw in var_name.lower() for kw in ["text", "font", "body"]):
                colors["text"].append(color_value)

        # Extract hex colors from CSS
        hex_pattern = r"#([0-9a-fA-F]{3,8})\b"
        all_colors = re.findall(hex_pattern, self.css_content)
        color_counts = Counter(all_colors)

        # Get most common colors
        most_common = [f"#{c}" for c, _ in color_counts.most_common(20)]

        # Categorize by appearance
        for color in most_common:
            hex_val = color.lstrip("#")
            if len(hex_val) == 3:
                hex_val = "".join([c * 2 for c in hex_val])

            try:
                r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
                brightness = (r * 299 + g * 587 + b * 114) / 1000

                if brightness > 240:  # Very light
                    if color not in colors["background"]:
                        colors["background"].append(color)
                elif brightness < 30:  # Very dark
                    if color not in colors["text"]:
                        colors["text"].append(color)
                elif r > 200 and g < 100 and b < 100:  # Reddish
                    if color not in colors["accent"]:
                        colors["accent"].append(color)
                else:
                    if color not in colors["neutral"]:
                        colors["neutral"].append(color)
            except (ValueError, IndexError):
                pass

        # Dedupe and limit
        for key in colors:
            colors[key] = list(dict.fromkeys(colors[key]))[:5]

        # Set defaults if nothing found
        if not colors["primary"]:
            colors["primary"] = ["#000000"]
        if not colors["background"]:
            colors["background"] = ["#ffffff", "#f5f5f5"]
        if not colors["text"]:
            colors["text"] = ["#1a1a1a", "#333333"]

        return colors

    def _extract_typography(self) -> dict:
        """Extract typography settings from CSS."""
        typography = {
            "fontFamilies": {
                "heading": None,
                "body": None,
                "mono": "monospace",
            },
            "fontSizes": {
                "xs": "0.75rem",
                "sm": "0.875rem",
                "base": "1rem",
                "lg": "1.125rem",
                "xl": "1.25rem",
                "2xl": "1.5rem",
                "3xl": "1.875rem",
                "4xl": "2.25rem",
                "5xl": "3rem",
            },
            "fontWeights": {
                "normal": "400",
                "medium": "500",
                "semibold": "600",
                "bold": "700",
            },
            "lineHeights": {
                "tight": "1.25",
                "normal": "1.5",
                "relaxed": "1.75",
            },
        }

        # Extract font-family declarations
        font_pattern = r"font-family:\s*([^;]+)"
        fonts = re.findall(font_pattern, self.css_content, re.IGNORECASE)

        # Count font usage
        font_counts = Counter()
        for font in fonts:
            # Clean and get first font in stack
            clean_font = font.split(",")[0].strip().strip("'\"")
            if clean_font and clean_font not in ["inherit", "initial", "unset"]:
                font_counts[clean_font] += 1

        # Get most common fonts
        common_fonts = [f for f, _ in font_counts.most_common(5)]

        if common_fonts:
            # Categorize fonts
            for font in common_fonts:
                font_lower = font.lower()
                if any(kw in font_lower for kw in ["serif", "georgia", "times", "garamond"]):
                    if not typography["fontFamilies"]["heading"]:
                        typography["fontFamilies"]["heading"] = f'"{font}", serif'
                elif any(kw in font_lower for kw in ["mono", "courier", "consolas"]):
                    typography["fontFamilies"]["mono"] = f'"{font}", monospace'
                else:
                    if not typography["fontFamilies"]["body"]:
                        typography["fontFamilies"]["body"] = f'"{font}", sans-serif'
                    elif not typography["fontFamilies"]["heading"]:
                        typography["fontFamilies"]["heading"] = f'"{font}", sans-serif'

        # Set defaults
        if not typography["fontFamilies"]["body"]:
            typography["fontFamilies"]["body"] = '"Inter", "Helvetica Neue", sans-serif'
        if not typography["fontFamilies"]["heading"]:
            typography["fontFamilies"]["heading"] = typography["fontFamilies"]["body"]

        return typography

    def _extract_spacing(self) -> dict:
        """Extract spacing scale from CSS."""
        spacing = {
            "0": "0",
            "1": "0.25rem",
            "2": "0.5rem",
            "3": "0.75rem",
            "4": "1rem",
            "5": "1.25rem",
            "6": "1.5rem",
            "8": "2rem",
            "10": "2.5rem",
            "12": "3rem",
            "16": "4rem",
            "20": "5rem",
            "24": "6rem",
        }

        # Try to find custom spacing values
        gap_pattern = r"(?:gap|padding|margin):\s*(\d+(?:\.\d+)?)(px|rem|em)"
        matches = re.findall(gap_pattern, self.css_content)

        if matches:
            # Convert to rem and find common values
            rem_values = []
            for value, unit in matches:
                num = float(value)
                if unit == "px":
                    num = num / 16  # Convert to rem
                rem_values.append(round(num, 3))

            # Get unique common values
            common = Counter(rem_values).most_common(10)
            for i, (val, _) in enumerate(common):
                if val > 0 and val <= 10:
                    spacing[str(i + 1)] = f"{val}rem"

        return spacing

    def _extract_borders(self) -> dict:
        """Extract border styles from CSS."""
        borders = {
            "radius": {
                "none": "0",
                "sm": "0.125rem",
                "md": "0.375rem",
                "lg": "0.5rem",
                "xl": "0.75rem",
                "2xl": "1rem",
                "full": "9999px",
            },
            "widths": {
                "0": "0",
                "1": "1px",
                "2": "2px",
                "4": "4px",
            },
        }

        # Extract border-radius values
        radius_pattern = r"border-radius:\s*(\d+(?:\.\d+)?)(px|rem|em|%)"
        matches = re.findall(radius_pattern, self.css_content)

        if matches:
            radii = []
            for value, unit in matches:
                num = float(value)
                if unit == "px":
                    radii.append(f"{num}px")
                elif unit == "%":
                    radii.append(f"{num}%")
                else:
                    radii.append(f"{num}{unit}")

            common_radii = Counter(radii).most_common(5)
            sizes = ["sm", "md", "lg", "xl", "2xl"]
            for i, (radius, _) in enumerate(common_radii):
                if i < len(sizes):
                    borders["radius"][sizes[i]] = radius

        return borders

    def _extract_shadows(self) -> dict:
        """Extract box-shadow values from CSS."""
        shadows = {
            "sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
            "md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
            "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
            "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
        }

        # Extract box-shadow values
        shadow_pattern = r"box-shadow:\s*([^;]+)"
        matches = re.findall(shadow_pattern, self.css_content)

        if matches:
            # Use most common shadows
            shadow_counts = Counter(matches)
            common = shadow_counts.most_common(4)
            sizes = ["sm", "md", "lg", "xl"]
            for i, (shadow, _) in enumerate(common):
                if i < len(sizes) and shadow.strip() not in ["none", "inherit"]:
                    shadows[sizes[i]] = shadow.strip()

        return shadows

    def _extract_button_styles(self) -> dict:
        """Extract button styling patterns."""
        buttons = {
            "primary": {
                "background": "#000000",
                "color": "#ffffff",
                "hoverBackground": "#333333",
                "borderRadius": "0.375rem",
                "padding": "0.75rem 1.5rem",
                "fontWeight": "500",
            },
            "secondary": {
                "background": "transparent",
                "color": "#000000",
                "border": "1px solid #000000",
                "hoverBackground": "#f5f5f5",
                "borderRadius": "0.375rem",
                "padding": "0.75rem 1.5rem",
                "fontWeight": "500",
            },
        }

        # Try to find button styles in CSS
        # This is approximate - real values would come from computed styles
        return buttons

    def _extract_card_styles(self) -> dict:
        """Extract card styling patterns."""
        cards = {
            "background": "#ffffff",
            "borderRadius": "0.5rem",
            "shadow": "0 1px 3px 0 rgb(0 0 0 / 0.1)",
            "hoverShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
            "padding": "1rem",
            "transition": "box-shadow 0.2s ease-in-out",
        }

        return cards

    def generate_tailwind_config(self, tokens: dict) -> str:
        """Generate Tailwind CSS config extension from tokens."""
        config = {
            "theme": {
                "extend": {
                    "colors": {
                        "brand": {
                            "primary": tokens["colors"]["primary"][0] if tokens["colors"]["primary"] else "#000000",
                            "secondary": tokens["colors"]["secondary"][0] if tokens["colors"]["secondary"] else "#666666",
                        },
                        "surface": {
                            "background": tokens["colors"]["background"][0] if tokens["colors"]["background"] else "#ffffff",
                            "card": tokens["colors"]["background"][1] if len(tokens["colors"]["background"]) > 1 else "#f5f5f5",
                        },
                    },
                    "fontFamily": {
                        "heading": tokens["typography"]["fontFamilies"]["heading"],
                        "body": tokens["typography"]["fontFamilies"]["body"],
                    },
                    "borderRadius": tokens["borders"]["radius"],
                    "boxShadow": tokens["shadows"],
                },
            },
        }

        return f"""// Generated Tailwind config extension from extracted tokens
// Source: {tokens['meta']['source_url']}

module.exports = {json.dumps(config, indent=2)}
"""


async def main():
    parser = argparse.ArgumentParser(description="Extract design tokens from a website")
    parser.add_argument(
        "--url",
        default="https://vanleeuwenicecream.com",
        help="URL to extract tokens from",
    )
    parser.add_argument(
        "--output",
        default="ui/theme/tokens.json",
        help="Output path for tokens JSON",
    )
    parser.add_argument(
        "--tailwind-config",
        default="ui/theme/tailwind.extend.js",
        help="Output path for Tailwind config",
    )

    args = parser.parse_args()

    print(f"Extracting theme tokens from {args.url}...")

    extractor = ThemeExtractor(args.url)
    tokens = await extractor.extract()

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save tokens
    with open(output_path, "w") as f:
        json.dump(tokens, f, indent=2)
    print(f"Saved tokens to {output_path}")

    # Generate Tailwind config
    tailwind_config = extractor.generate_tailwind_config(tokens)
    tailwind_path = Path(args.tailwind_config)
    tailwind_path.parent.mkdir(parents=True, exist_ok=True)

    with open(tailwind_path, "w") as f:
        f.write(tailwind_config)
    print(f"Saved Tailwind config to {tailwind_path}")

    # Print summary
    print("\nExtracted tokens summary:")
    print(f"  Colors: {sum(len(v) for v in tokens['colors'].values())} values")
    print(f"  Fonts: {tokens['typography']['fontFamilies']['body']}")
    print(f"  Border radii: {len(tokens['borders']['radius'])} values")


if __name__ == "__main__":
    asyncio.run(main())
