const filterSections = [
  {
    title: "Teams",
    items: ["All Teams"],
  },
  {
    title: "Drivers",
    items: ["All Drivers"],
  },
  {
    title: "Categories",
    items: ["News", "Interviews", "Race Reports"],
  },
] as const;

export default function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 border-r border-neutral-800 bg-neutral-950 p-4 lg:block">
      <div className="space-y-6">
        {filterSections.map((section) => (
          <div key={section.title}>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-neutral-500">
              {section.title}
            </h3>
            <ul className="space-y-1">
              {section.items.map((item) => (
                <li key={item}>
                  <span className="block rounded-md px-2 py-1.5 text-sm text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-white">
                    {item}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-lg border border-neutral-800 bg-neutral-900 p-3">
        <p className="text-xs text-neutral-500">
          Filters will be available once data ingestion is active.
        </p>
      </div>
    </aside>
  );
}
