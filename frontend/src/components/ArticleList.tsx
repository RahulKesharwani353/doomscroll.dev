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
  if (loading && articles.length === 0) {
    return (
      <div className="flex flex-col gap-2">
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            style={{ animationDelay: `${i * 50}ms` }}
            className="flex items-center gap-3.5 px-5 py-4 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] rounded-[14px] animate-pulse"
          >
            <div className="w-[38px] h-[38px] bg-white/10 rounded-[10px]" />
            <div className="flex-1">
              <div className="h-4 bg-white/10 rounded w-3/4 mb-2" />
              <div className="flex gap-3">
                <div className="h-5 w-20 bg-white/5 rounded" />
                <div className="h-4 w-16 bg-white/5 rounded" />
                <div className="h-4 w-14 bg-white/5 rounded" />
              </div>
            </div>
            <div className="flex gap-1.5">
              <div className="w-8 h-8 bg-white/5 rounded-lg" />
              <div className="w-16 h-8 bg-white/5 rounded-lg" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-in">
        <div className="w-16 h-16 mb-4 text-red-500">
          <AlertCircleIcon className="w-full h-full" />
        </div>
        <h3 className="text-lg font-medium text-slate-200 mb-2">Failed to load articles</h3>
        <p className="text-slate-400 text-sm">{error}</p>
      </div>
    );
  }

  if (!articles || articles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-in">
        <div className="w-16 h-16 mb-4 text-slate-600">
          <EmptyIcon className="w-full h-full" />
        </div>
        <h3 className="text-lg font-medium text-slate-200 mb-2">No articles found</h3>
        <p className="text-slate-400 text-sm">Try adjusting your search or filters</p>
      </div>
    );
  }

  return (
    <div>
      {/* Article List */}
      <div className="flex flex-col gap-2">
        {articles.map((article, index) => (
          <ArticleCard key={article.id} article={article} index={index} />
        ))}
      </div>

      {/* Load More Button */}
      {hasMore && onLoadMore && (
        <div className="flex justify-center mt-8 animate-fade-in">
          <button
            onClick={onLoadMore}
            disabled={loadingMore}
            className="px-6 py-2.5 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] hover:bg-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)] text-[#a0aec0] hover:text-white text-[13px] font-medium rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
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
