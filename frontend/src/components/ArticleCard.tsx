import type { MouseEvent } from 'react';
import { formatTimeAgo } from '../utils/helpers';
import type { Article } from '../types';

const SOURCE_STYLES: Record<string, { gradient: string; badgeBg: string; badgeText: string; label: string; shortLabel: string }> = {
  hackernews: {
    gradient: 'bg-gradient-to-br from-[#ff6600] to-[#ff8533]',
    badgeBg: 'bg-[rgba(255,102,0,0.15)]',
    badgeText: 'text-[#ff6600]',
    label: 'HACKER NEWS',
    shortLabel: 'HN'
  },
  devto: {
    gradient: 'bg-gradient-to-br from-[#3b82f6] to-[#60a5fa]',
    badgeBg: 'bg-[rgba(59,130,246,0.15)]',
    badgeText: 'text-[#3b82f6]',
    label: 'DEV.TO',
    shortLabel: 'DEV'
  },
  reddit: {
    gradient: 'bg-gradient-to-br from-[#ff4500] to-[#ff6633]',
    badgeBg: 'bg-[rgba(255,69,0,0.15)]',
    badgeText: 'text-[#ff4500]',
    label: 'REDDIT',
    shortLabel: 'R'
  },
  lobsters: {
    gradient: 'bg-gradient-to-br from-[#dc2626] to-[#ef4444]',
    badgeBg: 'bg-[rgba(220,38,38,0.15)]',
    badgeText: 'text-[#dc2626]',
    label: 'LOBSTERS',
    shortLabel: 'L'
  },
};

interface ArticleCardProps {
  article: Article;
  index?: number;
}

export default function ArticleCard({ article, index = 0 }: ArticleCardProps) {
  const style = SOURCE_STYLES[article.source] || {
    gradient: 'bg-gradient-to-br from-slate-500 to-slate-600',
    badgeBg: 'bg-slate-500/15',
    badgeText: 'text-slate-400',
    label: article.source.toUpperCase(),
    shortLabel: article.source[0]?.toUpperCase() || '?'
  };

  const handleClick = (): void => {
    window.open(article.url, '_blank', 'noopener,noreferrer');
  };

  const handleShare = (e: MouseEvent<HTMLButtonElement>): void => {
    e.stopPropagation();
    // Share functionality - to be implemented
  };

  return (
    <article
      onClick={handleClick}
      style={{ animationDelay: `${index * 50}ms` }}
      className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-3.5 p-4 sm:px-5 sm:py-4 bg-[rgba(255,255,255,0.05)] hover:bg-[rgba(255,255,255,0.08)] border border-[rgba(255,255,255,0.1)] hover:border-[rgba(255,255,255,0.2)] rounded-[14px] cursor-pointer transition-all duration-200 hover:translate-x-1 hover:shadow-[0_4px_20px_rgba(0,0,0,0.3)] animate-slide-up group"
    >
      {/* Mobile: Top row with source icon and actions */}
      <div className="flex items-start sm:items-center gap-3 sm:gap-3.5 sm:flex-1 sm:min-w-0">
        {/* Source Icon */}
        <div className={`w-9 h-9 sm:w-[38px] sm:h-[38px] shrink-0 flex items-center justify-center rounded-[8px] sm:rounded-[10px] ${style.gradient} transition-transform duration-200 group-hover:scale-110`}>
          <span className="text-[10px] sm:text-[11px] font-bold text-white">{style.shortLabel}</span>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="text-[13px] sm:text-[14px] font-medium text-white leading-[1.4] mb-1 sm:mb-1.5 line-clamp-2 sm:truncate group-hover:text-purple-200 transition-colors duration-200">
            {article.title}
          </h3>

          {/* Meta Row */}
          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
            {/* Source Badge */}
            <span className={`px-2 py-0.5 rounded text-[9px] sm:text-[10px] font-medium tracking-[0.3px] uppercase ${style.badgeBg} ${style.badgeText} transition-all duration-200 group-hover:scale-105`}>
              {style.label}
            </span>

            {/* Author - hidden on mobile */}
            {article.author && (
              <span className="hidden sm:flex items-center gap-1 text-[12px] text-[#64748b]">
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="7" r="4" />
                  <path d="M5.5 21a7.5 7.5 0 0 1 13 0" />
                </svg>
                <span className="truncate max-w-[80px]">{article.author}</span>
              </span>
            )}

            {/* Time */}
            <span className="flex items-center gap-1 text-[11px] sm:text-[12px] text-[#64748b]">
              <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              {formatTimeAgo(article.published_at)}
            </span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end sm:justify-start gap-1.5 shrink-0 mt-2 sm:mt-0">
        <button
          onClick={handleShare}
          className="w-8 h-8 flex items-center justify-center rounded-lg text-[#64748b] hover:text-white hover:bg-white/10 transition-all duration-200 hover:scale-110 active:scale-95 cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
            <polyline points="16 6 12 2 8 6" />
            <line x1="12" y1="2" x2="12" y2="15" />
          </svg>
        </button>
        <button
          onClick={handleClick}
          className="px-3 sm:px-4 py-1.5 sm:py-2 bg-[rgba(255,255,255,0.08)] border border-[rgba(255,255,255,0.1)] rounded-lg text-[11px] sm:text-[12px] font-medium text-[#a0aec0] hover:text-white hover:bg-purple-500/20 hover:border-purple-500/30 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
        >
          Read
        </button>
      </div>
    </article>
  );
}
