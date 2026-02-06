"use client";

import Link from "next/link";
import { useState } from "react";

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-[var(--color-border)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center">
            <span className="text-xl sm:text-2xl font-bold tracking-tight">
              PULL&amp;BEAR
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link
              href="/shop"
              className="text-sm tracking-wider uppercase hover:text-[var(--color-text-muted)] transition-colors"
            >
              Shop
            </Link>
            <Link
              href="/shop?category=t-shirts"
              className="text-sm tracking-wider uppercase hover:text-[var(--color-text-muted)] transition-colors"
            >
              T-Shirts
            </Link>
            <Link
              href="/shop?category=hoodies"
              className="text-sm tracking-wider uppercase hover:text-[var(--color-text-muted)] transition-colors"
            >
              Hoodies
            </Link>
            <Link
              href="/shop?category=jackets"
              className="text-sm tracking-wider uppercase hover:text-[var(--color-text-muted)] transition-colors"
            >
              Jackets
            </Link>
          </nav>

          {/* Search & Cart (Desktop) */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              href="/shop"
              className="p-2 hover:bg-[var(--color-background-alt)] rounded-full transition-colors"
              aria-label="Search"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle menu"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-[var(--color-border)]">
            <nav className="flex flex-col space-y-4">
              <Link
                href="/shop"
                className="text-sm tracking-wider uppercase"
                onClick={() => setIsMenuOpen(false)}
              >
                Shop All
              </Link>
              <Link
                href="/shop?category=t-shirts"
                className="text-sm tracking-wider uppercase"
                onClick={() => setIsMenuOpen(false)}
              >
                T-Shirts
              </Link>
              <Link
                href="/shop?category=hoodies"
                className="text-sm tracking-wider uppercase"
                onClick={() => setIsMenuOpen(false)}
              >
                Hoodies
              </Link>
              <Link
                href="/shop?category=jackets"
                className="text-sm tracking-wider uppercase"
                onClick={() => setIsMenuOpen(false)}
              >
                Jackets
              </Link>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
