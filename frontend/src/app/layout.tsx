import type { Metadata } from "next";
import { Newsreader, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const fontSerif = Newsreader({
  variable: "--font-serif",
  subsets: ["latin"],
});

const fontSans = Plus_Jakarta_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
});

const faviconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32"><rect width="32" height="32" rx="7" fill="#0F1F38"/><polygon points="16,6 4,12 16,18 28,12" fill="#F59E0B"/><path d="M8,14.5 V19 C8,21.5 11.5,23.5 16,23.5 C20.5,23.5 24,21.5 24,19 V14.5" fill="none" stroke="#D97706" stroke-width="2" stroke-linecap="round"/><path d="M25,13.5 V21" stroke="#FBBF24" stroke-width="1.8" stroke-linecap="round"/><circle cx="25" cy="21.5" r="1.5" fill="#FBBF24"/><path d="M12,26.5 H20" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/></svg>`;
const faviconDataUri = `data:image/svg+xml,${encodeURIComponent(faviconSvg)}`;

export const metadata: Metadata = {
  title: "Amypo Q&A | Multi-Route Institutional Intelligence & Verification",
  description:
    "Next.js + Tailwind modern chat interface for institutional Q&A with live confidence badges, source citations, routing traces (Cache/SQL/Vector/LLM), Web Speech input, and role toggling.",
  icons: {
    icon: faviconDataUri,
    shortcut: faviconDataUri,
    apple: faviconDataUri,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${fontSerif.variable} ${fontSans.variable} dark h-full antialiased`}
    >
      <body className="min-h-full bg-[#080c14] text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
