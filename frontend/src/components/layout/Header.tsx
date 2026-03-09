import Link from "next/link";

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/news", label: "News" },
  { href: "/schedule", label: "Schedule" },
  { href: "/search", label: "Search" },
] as const;

export default function Header() {
  return (
    <header className="sticky top-0 z-50 flex h-14 items-center justify-between border-b border-neutral-800 bg-neutral-950 px-6">
      <Link href="/" className="flex items-center gap-2">
        <span className="text-xl font-bold tracking-tight text-white">
          F1 <span className="text-f1-red">Insight</span> AI
        </span>
      </Link>

      <nav className="hidden items-center gap-6 sm:flex">
        {navLinks.map(({ href, label }) => (
          <Link
            key={href}
            href={href}
            className="text-sm font-medium text-neutral-400 transition-colors hover:text-white"
          >
            {label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
