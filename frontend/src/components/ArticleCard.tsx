import type { MouseEvent } from 'react';
import { formatTimeAgo } from '../utils/helpers';
import type { Article } from '../types';

const SOURCE_STYLES: Record<string, { bg: string; label: string }> = {
  hackernews: { bg: 'bg-orange-500', label: 'HN' },
  devto: { bg: 'bg-blue-500', label: 'DEV' },
  reddit: { bg: 'bg-orange-600', label: 'R' },
  lobsters: { bg: 'bg-red-600', label: 'L' },
};

interface ArticleCardProps {
  article: Article;
}

export default function ArticleCard({ article }: ArticleCardProps) {
  const style = SOURCE_STYLES[article.source] || { bg: 'bg-slate-600', label: article.source[0]?.toUpperCase() || '?' };

  const handleClick = (): void => {
    window.open(article.url, '_blank', 'noopener,noreferrer');
  };

  const handleBookmark = (e: MouseEvent<HTMLButtonElement>): void => {
    e.stopPropagation();
    // Bookmark functionality - to be implemented
  };

  return (
    <article
      onClick={handleClick}
      className="group flex items-start gap-4 p-4 bg-slate-900/50 hover:bg-slate-800/70 border border-slate-800 hover:border-slate-700 rounded-xl cursor-pointer transition-all duration-200"
    >
      {/* Source Badge */}
      <div className={`w-10 h-10 shrink-0 flex items-center justify-center rounded-lg text-sm font-bold text-white ${style.bg}`}>
        {style.label}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <h3 className="text-slate-100 font-medium leading-snug mb-2 group-hover:text-white transition-colors line-clamp-2">
          {article.title}
        </h3>
        <div className="flex flex-wrap items-center gap-3 text-sm text-slate-400">
          <span className={`px-2 py-0.5 rounded text-xs font-medium text-white ${style.bg}`}>
            {article.source}
          </span>
          {article.author && (
            <span className="flex items-center gap-1.5">
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="7" r="4" />
                <path d="M5.5 21a7.5 7.5 0 0 1 13 0" />
              </svg>
              <span className="truncate max-w-[120px]">{article.author}</span>
            </span>
          )}
          <span className="flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 6v6l4 2" />
            </svg>
            {formatTimeAgo(article.published_at)}
          </span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={handleBookmark}
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
        </button>
        <button
          onClick={handleClick}
          className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-lg transition-colors cursor-pointer"
        >
          Read
        </button>
      </div>
    </article>
  );
}
