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

const SOURCE_STYLES: Record<string, { bg: string; label: string }> = {
  hackernews: { bg: 'bg-orange-500', label: 'HN' },
  devto: { bg: 'bg-blue-500', label: 'DEV' },
  reddit: { bg: 'bg-orange-600', label: 'R' },
  lobsters: { bg: 'bg-red-600', label: 'L' },
};

interface SidebarProps {
  sources?: Source[];
  selectedSource: string | null;
  onSourceSelect: (source: string | null) => void;
  totalCount?: number;
}

export default function Sidebar({
  sources = [],
  selectedSource,
  onSourceSelect,
  totalCount = 0
}: SidebarProps) {
  const sourceList = sources.length > 0 ? sources : DEFAULT_SOURCES;

  const getSourceStyle = (slug: string) => {
    return SOURCE_STYLES[slug] || { bg: 'bg-slate-600', label: slug[0]?.toUpperCase() || '?' };
  };

  return (
    <aside className="w-64 shrink-0 p-4 hidden md:block">
      <div className="sticky top-24">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 px-3">
          Sources
        </h3>
        <ul className="space-y-1">
          {/* All Sources */}
          <li>
            <button
              onClick={() => onSourceSelect(null)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all cursor-pointer ${
                selectedSource === null
                  ? 'bg-purple-600/20 text-purple-400'
                  : 'text-slate-300 hover:bg-slate-800/50 hover:text-white'
              }`}
            >
              <span className={`w-8 h-8 flex items-center justify-center rounded-lg text-xs font-bold ${
                selectedSource === null ? 'bg-purple-600 text-white' : 'bg-slate-700 text-slate-300'
              }`}>
                ALL
              </span>
              <span className="flex-1 text-left text-sm font-medium">All Sources</span>
              {totalCount > 0 && (
                <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full">
                  {totalCount.toLocaleString()}
                </span>
              )}
            </button>
          </li>

          {/* Individual Sources */}
          {sourceList.map((source) => {
            const style = getSourceStyle(source.slug);
            const isSelected = selectedSource === source.slug;

            return (
              <li key={source.slug}>
                <button
                  onClick={() => onSourceSelect(source.slug)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-slate-800 text-white'
                      : 'text-slate-300 hover:bg-slate-800/50 hover:text-white'
                  }`}
                >
                  <span className={`w-8 h-8 flex items-center justify-center rounded-lg text-xs font-bold text-white ${style.bg}`}>
                    {style.label}
                  </span>
                  <span className="flex-1 text-left text-sm font-medium">{source.name}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </aside>
  );
}
