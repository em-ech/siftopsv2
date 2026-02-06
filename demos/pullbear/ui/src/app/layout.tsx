import type { Metadata } from "next";
import { Archivo_Narrow } from "next/font/google";
import "./globals.css";
import { Header, Footer } from "@/components";

const archivo = Archivo_Narrow({
  variable: "--font-archivo",
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "PULL&BEAR | New Collection Online",
  description:
    "Discover the latest trends in men's and women's fashion at PULL&BEAR. T-shirts, hoodies, jackets, trousers and more.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${archivo.variable} antialiased min-h-screen flex flex-col`}
        style={{
          fontFamily: "var(--font-archivo), 'Archivo Narrow', sans-serif",
        }}
      >
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
