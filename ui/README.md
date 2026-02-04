# Van Leeuwen Demo Storefront

A lightweight storefront that displays crawled catalog data with a design inspired by Van Leeuwen Ice Cream's aesthetic.

## Features

- **Home Page**: Hero banner, category tiles, featured products
- **Shop Page**: Search, filter by category, sort by price/name
- **Product Detail**: Image gallery, descriptions, ingredients, allergens
- **Responsive**: Mobile-first design
- **Accessible**: Semantic HTML, ARIA labels, keyboard navigation

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the storefront.

## Loading Catalog Data

The UI loads product data from `public/catalog.json`. To use crawled data:

```bash
# From the project root
python scripts/export_for_ui.py \
  --input out/catalog.jsonl \
  --output ui/public/catalog.json
```

If `catalog.json` doesn't exist, the UI displays demo products.

## Design System

### Color Palette

| Name | Value | Usage |
|------|-------|-------|
| Primary | `#1a1a1a` | Text, buttons, emphasis |
| Secondary | `#f5e6d3` | Warm cream backgrounds |
| Accent | `#c9a87c` | Gold highlights, hover states |
| Background | `#ffffff` | Main background |
| Background Alt | `#faf9f7` | Section backgrounds |
| Text Muted | `#666666` | Secondary text |

### Typography

| Family | Usage |
|--------|-------|
| Playfair Display | Headings, titles |
| Inter | Body text, UI elements |

Font sizes follow a modular scale from `0.75rem` to `3.75rem`.

### Spacing

Uses a consistent spacing scale:
- `4px`, `8px`, `12px`, `16px`, `24px`, `32px`, `48px`, `64px`, `96px`

### Components

#### Buttons

```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary">Secondary Button</button>
```

#### Product Cards

Cards use subtle hover effects with shadow and lift:

```jsx
<div className="product-card">
  <div className="aspect-product">
    <Image ... />
  </div>
  <h3>Product Name</h3>
  <p>$12.00</p>
</div>
```

## Project Structure

```
ui/
├── src/
│   ├── app/
│   │   ├── layout.tsx        # Root layout with Header/Footer
│   │   ├── page.tsx          # Home page
│   │   ├── shop/
│   │   │   └── page.tsx      # Shop listing
│   │   └── product/
│   │       └── [slug]/
│   │           └── page.tsx  # Product detail
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── ProductCard.tsx
│   │   ├── ProductGrid.tsx
│   │   └── ImageGallery.tsx
│   └── lib/
│       ├── types.ts          # TypeScript types
│       └── data.ts           # Data loading utilities
├── theme/
│   └── tokens.json           # Extracted design tokens
└── public/
    └── catalog.json          # Product catalog (generated)
```

## Customization

### Changing Colors

Edit CSS variables in `src/app/globals.css`:

```css
:root {
  --color-primary: #1a1a1a;
  --color-secondary: #f5e6d3;
  --color-accent: #c9a87c;
  /* ... */
}
```

### Changing Fonts

Update the Google Fonts imports in `src/app/layout.tsx`:

```tsx
import { Inter, Playfair_Display } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });
const playfair = Playfair_Display({ subsets: ["latin"] });
```

## Build for Production

```bash
npm run build
npm start
```

## Notes

- This is a demo storefront for educational purposes
- Product data is collected via polite web crawling
- The design mimics Van Leeuwen's aesthetic without copying exact assets
- No real checkout functionality is implemented
