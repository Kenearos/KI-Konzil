"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Network, MessagesSquare } from "lucide-react";

const TABS = [
  { href: "/rat-architekt", label: "Rat-Architekt", icon: Network },
  { href: "/konferenzzimmer", label: "Konferenzzimmer", icon: MessagesSquare },
];

export function NavTabs() {
  const pathname = usePathname();

  return (
    <nav className="flex items-center gap-1 px-4 py-2 bg-white border-b border-slate-200 flex-shrink-0">
      <span className="font-bold text-indigo-700 text-sm mr-4">CouncilOS</span>
      {TABS.map(({ href, label, icon: Icon }) => {
        const active = pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            className={[
              "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
              active
                ? "bg-indigo-50 text-indigo-700"
                : "text-slate-500 hover:text-slate-700 hover:bg-slate-50",
            ].join(" ")}
          >
            <Icon size={14} />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
