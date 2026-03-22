import { useState } from 'react';
import { Header, Sidebar, ArticleList, TabBar } from '../components';
import type { TabType } from '../components';
import { useArticles, useSearchArticles } from '../hooks/useArticles';
import { useSources, useSyncStatus } from '../hooks/useSources';

export default function ArticlesPage() {
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeTab, setActiveTab] = useState<TabType>('trending');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const { sources } = useSources();
  const { status: syncStatus } = useSyncStatus();

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
  } = useSearchArticles(searchQuery, 18);

  const articles = isSearching ? searchArticles : regularArticles;
  const pagination = isSearching ? searchPagination : regularPagination;
  const loading = isSearching ? searchLoading : regularLoading;
  const loadingMore = isSearching ? searchLoadingMore : regularLoadingMore;
  const error = isSearching ? searchError : regularError;
  const loadMore = isSearching ? searchLoadMore : regularLoadMore;
  const hasMore = isSearching ? searchHasMore : regularHasMore;

  // Keep these for potential future use
  void syncStatus;

  const handleSourceSelect = (source: string | null): void => {
    setSelectedSource(source);
    setSearchQuery('');
  };

  const handleSearchChange = (query: string): void => {
    setSearchQuery(query);
  };

  const handleTabChange = (tab: TabType): void => {
    setActiveTab(tab);
    // Tab functionality can be extended to filter/sort articles
  };

  const toggleSidebar = (): void => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = (): void => {
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-[rgb(10,10,15)] text-slate-100">
      <Header
        searchQuery={searchQuery}
        onSearchChange={handleSearchChange}
        onMenuToggle={toggleSidebar}
      />

      <main className="flex max-w-[1400px] mx-auto px-4 sm:px-6 gap-4 md:gap-6">
        <Sidebar
          sources={sources}
          selectedSource={selectedSource}
          onSourceSelect={handleSourceSelect}
          totalCount={pagination?.total_items || 0}
          isOpen={sidebarOpen}
          onClose={closeSidebar}
        />

        <section className="flex-1 py-4 sm:py-6 min-w-0">
          {!isSearching && (
            <TabBar activeTab={activeTab} onTabChange={handleTabChange} />
          )}

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

          <ArticleList
            articles={articles}
            loading={loading}
            error={error}
            hasMore={hasMore}
            onLoadMore={loadMore}
            loadingMore={loadingMore}
          />
        </section>
      </main>
    </div>
  );
}
