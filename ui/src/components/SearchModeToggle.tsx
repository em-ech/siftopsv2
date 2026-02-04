"use client";

export type SearchMode = "regular" | "sift" | "chat";

interface SearchModeToggleProps {
  mode: SearchMode;
  onChange: (mode: SearchMode) => void;
  disabled?: boolean;
}

const modes: { id: SearchMode; label: string; description: string }[] = [
  {
    id: "regular",
    label: "Regular",
    description: "Basic keyword search",
  },
  {
    id: "sift",
    label: "Sift AI",
    description: "Semantic search",
  },
  {
    id: "chat",
    label: "Chat",
    description: "Ask questions",
  },
];

export function SearchModeToggle({
  mode,
  onChange,
  disabled = false,
}: SearchModeToggleProps) {
  return (
    <div className="flex flex-col gap-2">
      <span className="text-xs font-medium tracking-wide uppercase text-[var(--color-text-muted)]">
        Search Mode
      </span>
      <div className="inline-flex rounded-lg bg-[var(--color-background-alt)] p-1">
        {modes.map((m) => (
          <button
            key={m.id}
            onClick={() => onChange(m.id)}
            disabled={disabled}
            className={`
              relative px-4 py-2 text-sm font-medium transition-all duration-200
              ${
                mode === m.id
                  ? "bg-white text-[var(--color-primary)] shadow-sm"
                  : "text-[var(--color-text-muted)] hover:text-[var(--color-text)]"
              }
              ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
              first:rounded-l-md last:rounded-r-md
            `}
            title={m.description}
          >
            {m.label}
            {m.id === "sift" && (
              <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 text-[10px] bg-[var(--color-accent)] text-white rounded-full">
                AI
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
