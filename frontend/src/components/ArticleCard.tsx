import { useState, useMemo, type MouseEvent } from 'react';
import { formatTimeAgo } from '../utils/helpers';
import type { Article } from '../types';
import { ClockIcon, CopyIcon, CheckIcon, UserIcon } from '../assets/icons';
import { useSourceContext } from '../contexts/SourceContext';

interface ArticleCardProps {
  article: Article;
  index?: number;
}

export default function ArticleCard({ article, index = 0 }: ArticleCardProps) {
  const [copied, setCopied] = useState(false);
  const { getSourceStyle } = useSourceContext();

  const style = useMemo(() => getSourceStyle(article.source), [article.source, getSourceStyle]);

  const handleClick = (): void => {
    window.open(article.url, '_blank', 'noopener,noreferrer');
  };

  const handleCopy = async (e: MouseEvent<HTMLButtonElement>): Promise<void> => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(article.url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Only apply staggered animation for initial load (index >= 0)
  // For load more items (index = -1), show immediately without delay
  const shouldAnimate = index >= 0;

  return (
    <article
      onClick={handleClick}
      style={shouldAnimate ? { animationDelay: `${index * 50}ms` } : undefined}
      className={`flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-3.5 p-4 sm:px-5 sm:py-4 bg-[rgba(255,255,255,0.05)] hover:bg-[rgba(255,255,255,0.08)] border border-[rgba(255,255,255,0.1)] hover:border-[rgba(255,255,255,0.2)] rounded-[8px] cursor-pointer transition-all duration-200 hover:translate-x-1 hover:shadow-[0_4px_20px_rgba(0,0,0,0.3)] group ${shouldAnimate ? 'animate-slide-up' : ''}`}
    >
      {/* Mobile: Top row with source icon and actions */}
      <div className="flex items-start sm:items-center gap-3 sm:gap-3.5 sm:flex-1 sm:min-w-0">
        {/* Source Icon */}
        <div className={`w-9 h-9 sm:w-[38px] sm:h-[38px] shrink-0 flex items-center justify-center rounded-[8px] ${style.gradient} transition-transform duration-200 group-hover:scale-110`}>
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
                <UserIcon className="w-3 h-3" />
                <span className="truncate max-w-[80px]">{article.author}</span>
              </span>
            )}

            {/* Time */}
            <span className="flex items-center gap-1 text-[11px] sm:text-[12px] text-[#64748b]">
              <ClockIcon className="w-3 h-3" />
              {formatTimeAgo(article.published_at)}
            </span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end sm:justify-start gap-1.5 shrink-0 mt-2 sm:mt-0">
        <button
          onClick={handleCopy}
          className={`w-8 h-8 flex items-center justify-center rounded-[8px] transition-all duration-200 active:scale-95 cursor-pointer ${
            copied
              ? 'text-emerald-400 bg-emerald-500/10'
              : 'text-white/30 hover:text-white/70 hover:bg-white/[0.06]'
          }`}
          title={copied ? 'Copied!' : 'Copy link'}
        >
          {copied ? <CheckIcon className="w-4 h-4" /> : <CopyIcon className="w-4 h-4" />}
        </button>
        <button
          onClick={handleClick}
          className="px-3 sm:px-4 py-1.5 sm:py-2 bg-[rgba(255,255,255,0.08)] border border-[rgba(255,255,255,0.1)] rounded-[8px] text-[11px] sm:text-[12px] font-medium text-[#a0aec0] hover:text-white hover:bg-purple-500/20 hover:border-purple-500/30 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
        >
          Read
        </button>
      </div>
    </article>
  );
}
