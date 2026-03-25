import { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Header } from '../components';
import ArticleCard from '../components/ArticleCard';
import { useAuth, useBookmarks } from '../hooks';
import { bookmarkRepository } from '../services/api';
import { tokenManager } from '../services/auth';
import type { Bookmark, PaginationMeta } from '../types';
import { SpinnerIcon, BookmarkIcon, AlertCircleIcon, ChevronRightIcon, HomeIcon } from '../assets/icons';

export default function BookmarksPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { loadBookmarks } = useBookmarks();

  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBookmarks = useCallback(async (page = 1, append = false) => {
    if (!tokenManager.hasTokens()) return;

    try {
      if (page === 1) setLoading(true);
      else setLoadingMore(true);

      const response = await bookmarkRepository.getAll(page, 20);

      if (append) {
        setBookmarks(prev => [...prev, ...response.data]);
      } else {
        setBookmarks(response.data);
        // Sync bookmark IDs to context
        loadBookmarks();
      }
      setPagination(response.pagination);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load bookmarks');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [loadBookmarks]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/');
      return;
    }
    if (isAuthenticated) {
      fetchBookmarks();
    }
  }, [isAuthenticated, authLoading, navigate, fetchBookmarks]);

  // Handler to remove bookmark from local list
  const handleRemoveBookmark = useCallback((articleId: string) => {
    setBookmarks(prev => prev.filter(b => b.article.id !== articleId));
    // Also update the count in pagination
    setPagination(prev => prev ? { ...prev, total_items: prev.total_items - 1 } : null);
  }, []);

  const handleLoadMore = () => {
    if (pagination?.has_next && !loadingMore) {
      fetchBookmarks(pagination.page + 1, true);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-primary flex items-center justify-center">
        <SpinnerIcon className="w-8 h-8 text-accent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-primary text-secondary">
      <Header searchQuery="" onSearchChange={() => {}} />

      <main className="max-w-[900px] mx-auto px-4 sm:px-6 py-4 sm:py-6">
        {/* Breadcrumbs */}
        <nav className="flex items-center gap-2 text-sm mb-4">
          <Link
            to="/articles"
            className="flex items-center gap-1 text-secondary hover:text-primary transition-colors"
          >
            <HomeIcon className="w-4 h-4" />
            <span>Home</span>
          </Link>
          <ChevronRightIcon className="w-4 h-4 text-dim" />
          <span className="text-primary font-medium flex items-center gap-1">
            <BookmarkIcon className="w-4 h-4" />
            Bookmarks
          </span>
        </nav>

        {/* Page Header */}
        <div className="mb-6">
          <h1 className="text-xl sm:text-2xl font-semibold text-primary flex items-center gap-2">
            <BookmarkIcon className="w-6 h-6" />
            Bookmarks
          </h1>
          {!loading && pagination && (
            <p className="text-xs sm:text-sm text-muted mt-1">
              {pagination.total_items} saved article{pagination.total_items !== 1 ? 's' : ''}
            </p>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col gap-2">
            {[...Array(5)].map((_, i) => (
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
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-in">
            <div className="w-16 h-16 mb-4 text-error">
              <AlertCircleIcon className="w-full h-full" />
            </div>
            <h3 className="text-lg font-medium text-secondary mb-2">Failed to load bookmarks</h3>
            <p className="text-muted text-sm">{error}</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && bookmarks.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-in">
            <div className="w-16 h-16 mb-4 text-dim">
              <BookmarkIcon className="w-full h-full" />
            </div>
            <h3 className="text-lg font-medium text-secondary mb-2">No bookmarks yet</h3>
            <p className="text-muted text-sm">Save articles to read later by clicking the bookmark icon</p>
          </div>
        )}

        {/* Bookmark List */}
        {!loading && !error && bookmarks.length > 0 && (
          <div>
            <div className="flex flex-col gap-2">
              {bookmarks.map((bookmark, index) => (
                <ArticleCard
                  key={bookmark.id}
                  article={bookmark.article}
                  index={index < 20 ? index : -1}
                  onBookmarkRemove={handleRemoveBookmark}
                />
              ))}
            </div>

            {/* Load More Button */}
            {(pagination?.has_next || loadingMore) && (
              <div className="flex justify-center mt-8 animate-fade-in">
                <button
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                  className="px-6 py-2.5 btn-secondary text-[13px] font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 active:scale-95 cursor-pointer"
                >
                  {loadingMore ? (
                    <span className="flex items-center gap-2">
                      <SpinnerIcon className="w-4 h-4" />
                      Loading...
                    </span>
                  ) : (
                    'Load More'
                  )}
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
