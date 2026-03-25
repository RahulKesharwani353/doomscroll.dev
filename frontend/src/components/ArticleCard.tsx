import { useState, useMemo, type MouseEvent } from 'react';
import { formatTimeAgo } from '../utils/helpers';
import type { Article } from '../types';
import { ClockIcon, CopyIcon, CheckIcon, UserIcon, BookmarkIcon, BookmarkFilledIcon } from '../assets/icons';
import { useSourceContext, useAuth, useBookmarks } from '../hooks';

interface ArticleCardProps {
  article: Article;
  index?: number;
  onBookmarkRemove?: (articleId: string) => void;
}

export default function ArticleCard({ article, index = 0, onBookmarkRemove }: ArticleCardProps) {
  const [copied, setCopied] = useState(false);
  const { getSourceStyle } = useSourceContext();
  const { isAuthenticated } = useAuth();
  const { isBookmarked, toggleBookmark } = useBookmarks();

  const style = useMemo(() => getSourceStyle(article.source), [article.source, getSourceStyle]);
  const bookmarked = isBookmarked(article.id);

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

  const handleBookmark = async (e: MouseEvent<HTMLButtonElement>): Promise<void> => {
    e.stopPropagation();
    const wasBookmarked = bookmarked;
    await toggleBookmark(article.id);
    // If it was bookmarked and now removed, call the callback
    if (wasBookmarked && onBookmarkRemove) {
      onBookmarkRemove(article.id);
    }
  };

  // Only apply staggered animation for initial load (index >= 0)
  // For load more items (index = -1), show immediately without delay
  const shouldAnimate = index >= 0;

  return (
    <article
      onClick={handleClick}
      style={shouldAnimate ? { animationDelay: `${index * 50}ms` } : undefined}
      className={`flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-3.5 p-4 sm:px-5 sm:py-4 bg-card hover:bg-card-hover border border-default hover:border-hover rounded-[8px] cursor-pointer transition-all duration-200 hover:translate-x-1 hover:shadow-card group ${shouldAnimate ? 'animate-slide-up' : ''}`}
    >
      {/* Mobile: Top row with source icon and actions */}
      <div className="flex items-start sm:items-center gap-3 sm:gap-3.5 sm:flex-1 sm:min-w-0">
        {/* Source Icon */}
        <div className={`w-9 h-9 sm:w-[38px] sm:h-[38px] shrink-0 flex items-center justify-center rounded-[8px] ${style.gradient} transition-transform duration-200 group-hover:scale-110`}>
          <span className="text-[10px] sm:text-[11px] font-bold text-primary">{style.shortLabel}</span>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="text-[13px] sm:text-[14px] font-medium text-primary leading-[1.4] mb-1 sm:mb-1.5 line-clamp-2 sm:truncate group-hover:text-accent-light transition-colors duration-200">
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
              <span className="hidden sm:flex items-center gap-1 text-[12px] text-muted">
                <UserIcon className="w-3 h-3" />
                <span className="truncate max-w-[80px]">{article.author}</span>
              </span>
            )}

            {/* Time */}
            <span className="flex items-center gap-1 text-[11px] sm:text-[12px] text-muted">
              <ClockIcon className="w-3 h-3" />
              {formatTimeAgo(article.published_at)}
            </span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end sm:justify-start gap-1.5 shrink-0 mt-2 sm:mt-0">
        {isAuthenticated && (
          <button
            onClick={handleBookmark}
            className={`group/bookmark w-8 h-8 flex items-center justify-center rounded-[8px] transition-all duration-200 active:scale-95 cursor-pointer ${
              bookmarked
                ? 'btn-ghost-active'
                : 'btn-ghost'
            }`}
            title={bookmarked ? 'Remove bookmark' : 'Add bookmark'}
          >
            {bookmarked ? (
              <BookmarkFilledIcon className="w-4 h-4" />
            ) : (
              <>
                <BookmarkIcon className="w-4 h-4 group-hover/bookmark:hidden" />
                <BookmarkFilledIcon className="w-4 h-4 hidden group-hover/bookmark:block" />
              </>
            )}
          </button>
        )}
        <button
          onClick={handleCopy}
          className={`w-8 h-8 flex items-center justify-center rounded-[8px] transition-all duration-200 active:scale-95 cursor-pointer ${
            copied
              ? 'text-success bg-success'
              : 'btn-icon'
          }`}
          title={copied ? 'Copied!' : 'Copy link'}
        >
          {copied ? <CheckIcon className="w-4 h-4" /> : <CopyIcon className="w-4 h-4" />}
        </button>
        <button
          onClick={handleClick}
          className="btn-read px-3 sm:px-4 py-1.5 sm:py-2 text-[11px] sm:text-[12px] font-medium transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
        >
          Read
        </button>
      </div>
    </article>
  );
}
