"use client";

import { useState } from "react";
import Image from "next/image";

interface ImageGalleryProps {
  images: string[];
  alt: string;
}

export function ImageGallery({ images, alt }: ImageGalleryProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const validImages = [...new Set(images.filter(Boolean))];

  if (validImages.length === 0) {
    return (
      <div className="aspect-[3/4] bg-[var(--color-background-alt)] flex items-center justify-center">
        <span className="text-[var(--color-text-light)] text-xs uppercase tracking-wider">
          No image available
        </span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Main Image - 3:4 portrait ratio */}
      <div className="aspect-[3/4] relative overflow-hidden bg-[var(--color-background-alt)]">
        <Image
          src={validImages[selectedIndex]}
          alt={`${alt} - Image ${selectedIndex + 1}`}
          fill
          sizes="(max-width: 768px) 100vw, 50vw"
          className="object-cover"
          priority
        />

        {/* Navigation Arrows */}
        {validImages.length > 1 && (
          <>
            <button
              onClick={() =>
                setSelectedIndex((prev) =>
                  prev === 0 ? validImages.length - 1 : prev - 1
                )
              }
              className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 flex items-center justify-center hover:bg-white transition-colors"
              aria-label="Previous image"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>
            <button
              onClick={() =>
                setSelectedIndex((prev) =>
                  prev === validImages.length - 1 ? 0 : prev + 1
                )
              }
              className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 flex items-center justify-center hover:bg-white transition-colors"
              aria-label="Next image"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          </>
        )}
      </div>

      {/* Thumbnails */}
      {validImages.length > 1 && (
        <div className="flex gap-2 overflow-x-auto">
          {validImages.map((image, index) => (
            <button
              key={image}
              onClick={() => setSelectedIndex(index)}
              className={`relative w-16 h-20 flex-shrink-0 overflow-hidden ${
                index === selectedIndex
                  ? "border-2 border-black"
                  : "border border-[var(--color-border)] opacity-60 hover:opacity-100"
              } transition-all`}
              aria-label={`View image ${index + 1}`}
            >
              <Image
                src={image}
                alt={`${alt} thumbnail ${index + 1}`}
                fill
                sizes="64px"
                className="object-cover"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
