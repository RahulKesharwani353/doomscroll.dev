import { formatTimeAgo } from '../utils/helpers';

interface StatsBarProps {
  totalArticles?: number;
  activeSources?: number;
  lastUpdated?: string | null;
}

export default function StatsBar({
  totalArticles = 0,
  activeSources = 0,
  lastUpdated = null
}: StatsBarProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6">
      {/* Total Articles */}
      <div className="flex items-center gap-3 px-4 sm:px-5 py-3 sm:py-4 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] rounded-xl">
        <div className="w-9 h-9 sm:w-10 sm:h-10 flex items-center justify-center rounded-[10px]" style={{ background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%)' }}>
          <svg className="w-4 h-4 sm:w-5 sm:h-5 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
          </svg>
        </div>
        <div>
          <h4 className="text-base sm:text-[18px] font-semibold text-white leading-tight">{totalArticles}</h4>
          <p className="text-[10px] sm:text-[11px] text-[#64748b]">Total Articles</p>
        </div>
      </div>

      {/* Active Sources */}
      <div className="flex items-center gap-3 px-4 sm:px-5 py-3 sm:py-4 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] rounded-xl">
        <div className="w-9 h-9 sm:w-10 sm:h-10 flex items-center justify-center rounded-[10px]" style={{ background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(96, 165, 250, 0.2) 100%)' }}>
          <svg className="w-4 h-4 sm:w-5 sm:h-5 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
            <polyline points="17 6 23 6 23 12" />
          </svg>
        </div>
        <div>
          <h4 className="text-base sm:text-[18px] font-semibold text-white leading-tight">{activeSources}</h4>
          <p className="text-[10px] sm:text-[11px] text-[#64748b]">Active Sources</p>
        </div>
      </div>

      {/* Last Updated */}
      <div className="flex items-center gap-3 px-4 sm:px-5 py-3 sm:py-4 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] rounded-xl">
        <div className="w-9 h-9 sm:w-10 sm:h-10 flex items-center justify-center rounded-[10px]" style={{ background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(74, 222, 128, 0.2) 100%)' }}>
          <svg className="w-4 h-4 sm:w-5 sm:h-5 text-green-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
        </div>
        <div>
          <h4 className="text-base sm:text-[18px] font-semibold text-white leading-tight">{lastUpdated ? formatTimeAgo(lastUpdated) : '2m ago'}</h4>
          <p className="text-[10px] sm:text-[11px] text-[#64748b]">Last Updated</p>
        </div>
      </div>
    </div>
  );
}
