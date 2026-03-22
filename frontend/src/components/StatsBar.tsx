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
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
      {/* Total Articles */}
      <div className="flex items-center gap-4 p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
        <div className="w-12 h-12 flex items-center justify-center bg-purple-600/20 text-purple-400 rounded-xl">
          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 17l10 5 10-5" />
          </svg>
        </div>
        <div>
          <h4 className="text-2xl font-bold text-white">{totalArticles.toLocaleString()}</h4>
          <p className="text-sm text-slate-400">Total Articles</p>
        </div>
      </div>

      {/* Active Sources */}
      <div className="flex items-center gap-4 p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
        <div className="w-12 h-12 flex items-center justify-center bg-blue-600/20 text-blue-400 rounded-xl">
          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
          </svg>
        </div>
        <div>
          <h4 className="text-2xl font-bold text-white">{activeSources}</h4>
          <p className="text-sm text-slate-400">Active Sources</p>
        </div>
      </div>

      {/* Last Updated */}
      <div className="flex items-center gap-4 p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
        <div className="w-12 h-12 flex items-center justify-center bg-green-600/20 text-green-400 rounded-xl">
          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v6l4 2" />
          </svg>
        </div>
        <div>
          <h4 className="text-2xl font-bold text-white">{lastUpdated ? formatTimeAgo(lastUpdated) : 'N/A'}</h4>
          <p className="text-sm text-slate-400">Last Updated</p>
        </div>
      </div>
    </div>
  );
}
