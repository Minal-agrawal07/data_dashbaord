import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "AI Dashboard Builder",
  description: "Describe charts in plain English. AI builds them.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <nav className="border-b border-gray-800 bg-gray-900 px-6 py-3 flex items-center gap-6">
          <span className="font-bold text-indigo-400 text-lg">AI Dashboard</span>
          <Link href="/" className="text-sm text-gray-300 hover:text-white transition-colors">Home</Link>
          <Link href="/builder" className="text-sm text-gray-300 hover:text-white transition-colors">Builder</Link>
          <Link href="/setup" className="text-sm text-gray-300 hover:text-white transition-colors">Data Sources</Link>
        </nav>
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
