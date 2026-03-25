import { useRef, useEffect } from 'react';
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

export default function ArticleList({
  articles,
  loading,
  error,
  hasMore = false,
  onLoadMore,
  loadingMore = false
}: ArticleListProps) {
  // Track initial load count to only animate first batch
  const initialLoadCount = useRef<number>(0);
  const hasInitialized = useRef<boolean>(false);

  useEffect(() => {
    // Only set initial count on first successful load
    if (!hasInitialized.current && articles.length > 0 && !loading) {
      initialLoadCount.current = articles.length;
      hasInitialized.current = true;
    }
    // Reset when articles are cleared (source change, new search)
    if (articles.length === 0) {
      initialLoadCount.current = 0;
      hasInitialized.current = false;
    }
  }, [articles.length, loading]);

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

  return (
    <div>
      {/* Article List */}
      <div className="flex flex-col gap-2">
        {articles.map((article, index) => (
          <ArticleCard
            key={article.id}
            article={article}
            // Only stagger animation for initial batch (first 18 items)
            // After that, show items immediately (index = -1 means no delay)
            index={index < initialLoadCount.current ? index : -1}
          />
        ))}
      </div>

      {/* Load More Button - show while loading OR when there's more */}
      {(hasMore || loadingMore) && onLoadMore && (
        <div className="flex justify-center mt-8 animate-fade-in">
          <button
            onClick={onLoadMore}
            disabled={loadingMore}
            className="px-6 py-2.5 btn-secondary text-[13px] font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 active:scale-95 cursor-pointer"
          >
            {loadingMore ? (
              <span className="flex items-center gap-2">
                <SpinnerIcon className="w-4 h-4" />
                Loading...
              </span>
            ) : (
              'Load More Articles'
            )}
          </button>
        </div>
      )}
    </div>
  );
}
