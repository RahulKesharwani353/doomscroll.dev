import { useRef, useEffect, useCallback } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import ArticleCard from './ArticleCard';
import type { Article } from '../types';
import { AlertCircleIcon, EmptyIcon, SpinnerIcon } from '../assets/icons';

interface ArticleListProps {
  articles: Article[];
  loading: boolean;
  error: string | null;
  hasMore?: boolean;
  onLoadMore?: () => void;
  loadingMore?: boolean;
}

// Estimated row height for virtual scrolling
const ESTIMATED_ROW_HEIGHT = 88;
const OVERSCAN = 5;

export default function ArticleList({
  articles,
  loading,
  error,
  hasMore = false,
  onLoadMore,
  loadingMore = false
}: ArticleListProps) {
  const parentRef = useRef<HTMLDivElement>(null);
  const initialLoadCount = useRef<number>(0);
  const hasInitialized = useRef<boolean>(false);

  useEffect(() => {
    if (!hasInitialized.current && articles.length > 0 && !loading) {
      initialLoadCount.current = articles.length;
      hasInitialized.current = true;
    }
    if (articles.length === 0) {
      initialLoadCount.current = 0;
      hasInitialized.current = false;
    }
  }, [articles.length, loading]);

  // Virtualizer for efficient rendering
  const virtualizer = useVirtualizer({
    count: articles.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => ESTIMATED_ROW_HEIGHT,
    overscan: OVERSCAN,
    measureElement: (el) => el.getBoundingClientRect().height + 8, // Include gap
  });

  // Infinite scroll: load more when near bottom
  const handleScroll = useCallback(() => {
    if (!parentRef.current || loadingMore || !hasMore || !onLoadMore) return;

    const { scrollTop, scrollHeight, clientHeight } = parentRef.current;
    const scrollPercentage = (scrollTop + clientHeight) / scrollHeight;

    // Load more when 80% scrolled
    if (scrollPercentage > 0.8) {
      onLoadMore();
    }
  }, [loadingMore, hasMore, onLoadMore]);

  useEffect(() => {
    const scrollElement = parentRef.current;
    if (scrollElement) {
      scrollElement.addEventListener('scroll', handleScroll, { passive: true });
      return () => scrollElement.removeEventListener('scroll', handleScroll);
    }
  }, [handleScroll]);

  if (loading && articles.length === 0) {
    return (
      <div className="flex flex-col gap-2">
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            style={{ animationDelay: `${i * 50}ms` }}
            className="flex items-center gap-3.5 px-5 py-4 bg-card border border-default rounded-[8px] animate-pulse"
          >
            <div className="w-[38px] h-[38px] bg-overlay-medium rounded-[8px]" />
            <div className="flex-1">
              <div className="h-4 bg-overlay-medium rounded w-3/4 mb-2" />
              <div className="flex gap-3">
                <div className="h-5 w-20 bg-overlay-light rounded" />
                <div className="h-4 w-16 bg-overlay-light rounded" />
                <div className="h-4 w-14 bg-overlay-light rounded" />
              </div>
            </div>
            <div className="flex gap-1.5">
              <div className="w-8 h-8 bg-overlay-light rounded-[8px]" />
              <div className="w-16 h-8 bg-overlay-light rounded-[8px]" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-in">
        <div className="w-16 h-16 mb-4 text-error">
          <AlertCircleIcon className="w-full h-full" />
        </div>
        <h3 className="text-lg font-medium text-secondary mb-2">Failed to load articles</h3>
        <p className="text-muted text-sm">{error}</p>
      </div>
    );
  }

  if (!articles || articles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-in">
        <div className="w-16 h-16 mb-4 text-dim">
          <EmptyIcon className="w-full h-full" />
        </div>
        <h3 className="text-lg font-medium text-secondary mb-2">No articles found</h3>
        <p className="text-muted text-sm">Try adjusting your search or filters</p>
      </div>
    );
  }

  const virtualItems = virtualizer.getVirtualItems();

  return (
    <div>
      {/* Virtualized Article List */}
      <div
        ref={parentRef}
        className="max-h-[calc(100vh-200px)] overflow-auto scrollbar-thin"
        style={{ contain: 'strict' }}
      >
        <div
          style={{
            height: `${virtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }}
        >
          {virtualItems.map((virtualRow) => {
            const article = articles[virtualRow.index];
            const shouldAnimate = virtualRow.index < initialLoadCount.current;

            return (
              <div
                key={article.id}
                data-index={virtualRow.index}
                ref={virtualizer.measureElement}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  transform: `translateY(${virtualRow.start}px)`,
                }}
              >
                <ArticleCard
                  article={article}
                  index={shouldAnimate ? virtualRow.index : -1}
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* Loading More Indicator */}
      {loadingMore && (
        <div className="flex justify-center py-4 animate-fade-in">
          <span className="flex items-center gap-2 text-muted text-sm">
            <SpinnerIcon className="w-4 h-4" />
            Loading more articles...
          </span>
        </div>
      )}

      {/* Manual Load More Button (fallback for when auto-load doesn't trigger) */}
      {hasMore && !loadingMore && (
        <div className="flex justify-center mt-4 animate-fade-in">
          <button
            onClick={onLoadMore}
            className="px-6 py-2.5 btn-secondary text-[13px] font-medium hover:scale-105 active:scale-95 cursor-pointer"
          >
            Load More Articles
          </button>
        </div>
      )}
    </div>
  );
}
