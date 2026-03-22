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
  hackernews: { bg: 'bg-[#ff6600]', label: 'HN' },
  devto: { bg: 'bg-[#3b82f6]', label: 'DEV' },
  reddit: { bg: 'bg-[#ff4500]', label: 'R' },
  lobsters: { bg: 'bg-[#dc2626]', label: 'L' },
};

interface SidebarProps {
  sources?: Source[];
  selectedSource: string | null;
  onSourceSelect: (source: string | null) => void;
  totalCount?: number;
  isOpen?: boolean;
  onClose?: () => void;
}

export default function Sidebar({
  sources = [],
  selectedSource,
  onSourceSelect,
  totalCount = 0,
  isOpen = false,
  onClose
}: SidebarProps) {
  const sourceList = sources.length > 0 ? sources : DEFAULT_SOURCES;

  const getSourceStyle = (slug: string) => {
    return SOURCE_STYLES[slug] || { bg: 'bg-slate-600', label: slug[0]?.toUpperCase() || '?' };
  };

  const getArticleCount = (source: Source | DefaultSource): number => {
    if ('article_count' in source && source.article_count !== undefined) {
      return source.article_count;
    }
    return 0;
  };

  const handleSourceClick = (source: string | null) => {
    onSourceSelect(source);
    onClose?.();
  };

  const sidebarContent = (
    <div className="bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] rounded-2xl p-4">
      <h3 className="text-[11px] font-semibold text-[#64748b] uppercase tracking-[0.8px] mb-3 px-2">
        Sources
      </h3>
      <ul className="space-y-0.5">
        {/* All Sources */}
        <li>
          <button
            onClick={() => handleSourceClick(null)}
            className={`w-full h-[42px] flex items-center gap-2.5 px-2.5 rounded-[10px] transition-all duration-200 cursor-pointer hover:scale-[1.02] active:scale-[0.98] ${
              selectedSource === null
                ? 'bg-gradient-to-r from-purple-500 to-indigo-500 shadow-[0px_4px_15px_0px_rgba(168,85,247,0.15)]'
                : 'hover:bg-white/5'
            }`}
          >
            <span className={`w-[26px] h-[26px] flex items-center justify-center rounded-md text-[9px] font-semibold text-white transition-transform duration-200 ${
              selectedSource === null
                ? 'bg-white/20'
                : 'bg-gradient-to-br from-purple-500 to-indigo-500'
            }`}>
              ALL
            </span>
            <span className={`flex-1 text-left text-[12px] font-medium transition-colors duration-200 ${
              selectedSource === null ? 'text-white' : 'text-[#a0aec0]'
            }`}>
              All Sources
            </span>
            <span className={`text-[10px] transition-colors duration-200 ${
              selectedSource === null ? 'text-white/70' : 'text-[#64748b]'
            }`}>
              {totalCount || 128}
            </span>
          </button>
        </li>

        {/* Individual Sources */}
        {sourceList.map((source, index) => {
          const style = getSourceStyle(source.slug);
          const isSelected = selectedSource === source.slug;
          const count = getArticleCount(source);

          return (
            <li key={source.slug} style={{ animationDelay: `${(index + 1) * 50}ms` }} className="animate-fade-in">
              <button
                onClick={() => handleSourceClick(source.slug)}
                className={`w-full h-[42px] flex items-center gap-2.5 px-2.5 rounded-[10px] transition-all duration-200 cursor-pointer hover:scale-[1.02] active:scale-[0.98] ${
                  isSelected ? 'bg-white/5' : 'hover:bg-white/5'
                }`}
              >
                <span className={`w-[26px] h-[26px] flex items-center justify-center rounded-md text-[9px] font-semibold text-white transition-transform duration-200 hover:scale-110 ${style.bg}`}>
                  {style.label}
                </span>
                <span className={`flex-1 text-left text-[12px] font-medium transition-colors duration-200 ${
                  isSelected ? 'text-white' : 'text-[#a0aec0]'
                }`}>
                  {source.name}
                </span>
                {count > 0 && (
                  <span className="text-[10px] text-[#64748b]">
                    {count}
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden animate-fade-in backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      {/* Mobile Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full w-[260px] bg-[rgb(10,10,15)] z-50 transform transition-transform duration-300 ease-out md:hidden ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-4 pt-6">
          {/* Mobile Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2 group">
              <div className="w-8 h-8 flex items-center justify-center bg-gradient-to-br from-purple-500 to-indigo-500 rounded-lg transition-all duration-300 group-hover:scale-105">
                <svg className="w-4 h-4 text-white transition-transform duration-300 group-hover:rotate-12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z" />
                  <path d="M2 17l10 5 10-5" />
                  <path d="M2 12l10 5 10-5" />
                </svg>
              </div>
              <span className="text-lg font-bold text-white">Doomscroll</span>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-white transition-all duration-200 hover:scale-110 active:scale-95 hover:bg-white/10 rounded-lg"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          {sidebarContent}
        </div>
      </aside>

      {/* Desktop Sidebar */}
      <aside className="hidden md:block w-[200px] shrink-0 animate-slide-in-left">
        <div className="sticky top-[93px]">
          {sidebarContent}
        </div>
      </aside>
    </>
  );
}
