import { useState } from 'react';
import { Header, Sidebar, ArticleList, Pagination, StatsBar } from './components';
import { useArticles, useSearchArticles } from './hooks/useArticles';
import { useSources, useSyncStatus } from './hooks/useSources';

export default function App() {
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const { sources } = useSources();
  const { status: syncStatus } = useSyncStatus();

  // Use search results if searching, otherwise use regular articles
  const isSearching = searchQuery.length >= 2;

  const {
    articles: regularArticles,
    pagination: regularPagination,
    loading: regularLoading,
    error: regularError,
  } = useArticles(selectedSource, currentPage, 20);

  const {
    articles: searchArticles,
    pagination: searchPagination,
    loading: searchLoading,
    error: searchError,
  } = useSearchArticles(searchQuery, currentPage, 20);

  const articles = isSearching ? searchArticles : regularArticles;
  const pagination = isSearching ? searchPagination : regularPagination;
  const loading = isSearching ? searchLoading : regularLoading;
  const error = isSearching ? searchError : regularError;

  const handleSourceSelect = (source: string | null): void => {
    setSelectedSource(source);
    setCurrentPage(1);
    setSearchQuery('');
  };

  const handleSearchChange = (query: string): void => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handlePageChange = (page: number): void => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      <Header searchQuery={searchQuery} onSearchChange={handleSearchChange} />

      <main className="flex max-w-7xl mx-auto">
        <Sidebar
          sources={sources}
          selectedSource={selectedSource}
          onSourceSelect={handleSourceSelect}
          totalCount={pagination?.total_items || 0}
        />

        <section className="flex-1 p-6">
          <StatsBar
            totalArticles={pagination?.total_items || 0}
            activeSources={syncStatus?.enabled_sources || 4}
            lastUpdated={syncStatus?.last_sync?.completed_at}
          />

          <div className="mb-6">
            <h2 className="text-xl font-semibold text-white">
              {isSearching
                ? `Search results for "${searchQuery}"`
                : selectedSource
                ? `${selectedSource.charAt(0).toUpperCase() + selectedSource.slice(1)} Articles`
                : 'All Articles'}
            </h2>
          </div>

          <ArticleList articles={articles} loading={loading} error={error} />

          <Pagination pagination={pagination} onPageChange={handlePageChange} />
        </section>
      </main>
    </div>
  );
}
