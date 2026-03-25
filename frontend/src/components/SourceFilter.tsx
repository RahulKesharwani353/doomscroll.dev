import type { Source } from '../types';
import { useSourceContext } from '../hooks';

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
            ? 'gradient-primary-r text-primary shadow-purple'
            : 'bg-card text-secondary border border-default hover:bg-card-hover hover:border-hover'
        }`}
      >
        <span>All</span>
        {selectedSource === null && currentCount > 0 && (
          <span className="chip-count">
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
                : style.bg + ' border border-transparent hover:border-default'
            }`}
          >
            <span className="hidden sm:inline">{source.name}</span>
            <span className="sm:hidden">{style.label}</span>
            {/* Show count only when this source is selected */}
            {isSelected && currentCount > 0 && (
              <span className="chip-count">
                {currentCount}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
