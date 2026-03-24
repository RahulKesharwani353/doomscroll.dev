import { useState, useEffect } from 'react';
import { Header, ArticleList, SourceFilter } from '../components';
import { useArticles, useSearchArticles } from '../hooks/useArticles';
import { useSourceContext } from '../contexts/SourceContext';
import { useAuth } from '../contexts/AuthContext';
import { useBookmarks } from '../contexts/BookmarkContext';

export default function ArticlesPage() {
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const { sources } = useSourceContext();
  const { isAuthenticated } = useAuth();
  const { loadBookmarks } = useBookmarks();

  // Use search results if searching, otherwise use regular articles
  const isSearching = searchQuery.length >= 2;

  const {
    articles: regularArticles,
    pagination: regularPagination,
    loading: regularLoading,
    loadingMore: regularLoadingMore,
    error: regularError,
    loadMore: regularLoadMore,
    hasMore: regularHasMore,
  } = useArticles(selectedSource, 18);

  const {
    articles: searchArticles,
    pagination: searchPagination,
    loading: searchLoading,
    loadingMore: searchLoadingMore,
    error: searchError,
    loadMore: searchLoadMore,
    hasMore: searchHasMore,
  } = useSearchArticles(searchQuery, 18, selectedSource);

  const articles = isSearching ? searchArticles : regularArticles;
  const pagination = isSearching ? searchPagination : regularPagination;
  const loading = isSearching ? searchLoading : regularLoading;
  const loadingMore = isSearching ? searchLoadingMore : regularLoadingMore;
  const error = isSearching ? searchError : regularError;
  const loadMore = isSearching ? searchLoadMore : regularLoadMore;
  const hasMore = isSearching ? searchHasMore : regularHasMore;

  // Load all bookmarks once when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadBookmarks();
    }
  }, [isAuthenticated, loadBookmarks]);

  const handleSourceSelect = (source: string | null): void => {
    setSelectedSource(source);
    // Don't clear search query - allow filtering search results by source
  };

  const handleSearchChange = (query: string): void => {
    setSearchQuery(query);
  };

  return (
    <div className="min-h-screen bg-[rgb(10,10,15)] text-slate-100">
      <Header
        searchQuery={searchQuery}
        onSearchChange={handleSearchChange}
      />

      <main className="max-w-[900px] mx-auto px-4 sm:px-6 py-4 sm:py-6">
        {/* Source Filter - Always visible */}
        <SourceFilter
          sources={sources}
          selectedSource={selectedSource}
          onSourceSelect={handleSourceSelect}
          currentCount={pagination?.total_items || 0}
        />

        {/* Search Results Header */}
        {isSearching && (
          <div className="mb-4 sm:mb-6 animate-fade-in">
            <h2 className="text-lg sm:text-xl font-semibold text-white">
              Search results for "{searchQuery}"
            </h2>
            {!loading && (
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                {pagination?.total_items || 0} articles found
              </p>
            )}
          </div>
        )}

        {/* Article List */}
        <ArticleList
          articles={articles}
          loading={loading}
          error={error}
          hasMore={hasMore}
          onLoadMore={loadMore}
          loadingMore={loadingMore}
        />
      </main>
    </div>
  );
}
