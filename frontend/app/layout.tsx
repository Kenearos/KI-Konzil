import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { NavTabs } from "@/app/components/NavTabs";

const geist = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CouncilOS — KI-Rat Baukasten",
  description: "Visueller No-Code-Builder für Multi-Agent-KI-Pipelines",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body className={`${geist.variable} antialiased bg-slate-50 h-screen flex flex-col`}>
        <NavTabs />
        <main className="flex-1 overflow-hidden">{children}</main>
      </body>
    </html>
  );
}
