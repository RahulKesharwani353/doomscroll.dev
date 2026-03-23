import type { Source } from '../types';

interface DefaultSource {
  slug: string;
  name: string;
}

const DEFAULT_SOURCES: DefaultSource[] = [
  { slug: 'hackernews', name: 'Hacker News' },
  { slug: 'devto', name: 'Dev.to' },
  { slug: 'reddit', name: 'Reddit' },
  { slug: 'lobsters', name: 'Lobsters' },
];

const SOURCE_STYLES: Record<string, { bg: string; activeBg: string; label: string }> = {
  hackernews: { bg: 'bg-[#ff6600]/10 text-[#ff6600]', activeBg: 'bg-[#ff6600] text-white', label: 'HN' },
  devto: { bg: 'bg-[#3b82f6]/10 text-[#3b82f6]', activeBg: 'bg-[#3b82f6] text-white', label: 'DEV' },
  reddit: { bg: 'bg-[#ff4500]/10 text-[#ff4500]', activeBg: 'bg-[#ff4500] text-white', label: 'R' },
  lobsters: { bg: 'bg-[#dc2626]/10 text-[#dc2626]', activeBg: 'bg-[#dc2626] text-white', label: 'L' },
};

interface SourceFilterProps {
  sources?: Source[];
  selectedSource: string | null;
  onSourceSelect: (source: string | null) => void;
  currentCount?: number; // Count for the currently selected filter
}

export default function SourceFilter({
  sources = [],
  selectedSource,
  onSourceSelect,
  currentCount = 0
}: SourceFilterProps) {
  const sourceList = sources.length > 0 ? sources : DEFAULT_SOURCES;

  const getSourceStyle = (slug: string) => {
    return SOURCE_STYLES[slug] || { bg: 'bg-slate-500/10 text-slate-400', activeBg: 'bg-slate-500 text-white', label: slug[0]?.toUpperCase() || '?' };
  };

  return (
    <div className="flex flex-wrap items-center gap-2 mb-4 sm:mb-6 animate-fade-in">
      {/* All Sources Chip */}
      <button
        onClick={() => onSourceSelect(null)}
        className={`flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 rounded-full text-[11px] sm:text-[12px] font-medium transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer ${
          selectedSource === null
            ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white shadow-[0px_4px_15px_0px_rgba(168,85,247,0.25)]'
            : 'bg-[rgba(255,255,255,0.05)] text-[#a0aec0] border border-[rgba(255,255,255,0.1)] hover:bg-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)]'
        }`}
      >
        <span>All</span>
        {/* Show count only when "All" is selected */}
        {selectedSource === null && currentCount > 0 && (
          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-white/20">
            {currentCount}
          </span>
        )}
      </button>

      {/* Source Chips */}
      {sourceList.map((source) => {
        const style = getSourceStyle(source.slug);
        const isSelected = selectedSource === source.slug;

        return (
          <button
            key={source.slug}
            onClick={() => onSourceSelect(source.slug)}
            className={`flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 rounded-full text-[11px] sm:text-[12px] font-medium transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer ${
              isSelected
                ? style.activeBg + ' shadow-lg'
                : style.bg + ' border border-transparent hover:border-white/10'
            }`}
          >
            <span className="hidden sm:inline">{source.name}</span>
            <span className="sm:hidden">{style.label}</span>
            {/* Show count only when this source is selected */}
            {isSelected && currentCount > 0 && (
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-white/20">
                {currentCount}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
