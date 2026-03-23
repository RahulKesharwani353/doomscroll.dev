import type { Source } from '../types';
import { useSourceContext } from '../contexts/SourceContext';

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

interface SourceFilterProps {
  sources?: Source[];
  selectedSource: string | null;
  onSourceSelect: (source: string | null) => void;
  currentCount?: number;
}

export default function SourceFilter({
  sources = [],
  selectedSource,
  onSourceSelect,
  currentCount = 0
}: SourceFilterProps) {
  const { getSourceStyle } = useSourceContext();
  const sourceList = sources.length > 0 ? sources : DEFAULT_SOURCES;

  return (
    <div className="flex flex-wrap items-center gap-2 mb-4 sm:mb-6 animate-fade-in">
      {/* All Sources Chip */}
      <button
        onClick={() => onSourceSelect(null)}
        className={`flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 rounded-[8px] text-[11px] sm:text-[12px] font-medium transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer ${
          selectedSource === null
            ? 'bg-gradient-to-r from-purple-500 to-indigo-500 text-white shadow-[0px_4px_15px_0px_rgba(168,85,247,0.25)]'
            : 'bg-[rgba(255,255,255,0.05)] text-[#a0aec0] border border-[rgba(255,255,255,0.1)] hover:bg-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)]'
        }`}
      >
        <span>All</span>
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
            className={`flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 rounded-[8px] text-[11px] sm:text-[12px] font-medium transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer ${
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
