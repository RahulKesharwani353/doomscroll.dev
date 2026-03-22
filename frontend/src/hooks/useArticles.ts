import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import type { Article, PaginationMeta } from '../types';

interface UseArticlesResult {
  articles: Article[];
  pagination: PaginationMeta | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useArticles(
  source: string | null = null,
  page: number = 1,
  limit: number = 20
): UseArticlesResult {
  const [articles, setArticles] = useState<Article[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchArticles = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.getArticles({ page, limit, source });
      setArticles(response.data || []);
      setPagination(response.pagination || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setArticles([]);
    } finally {
      setLoading(false);
    }
  }, [source, page, limit]);

  useEffect(() => {
    fetchArticles();
  }, [fetchArticles]);

  return { articles, pagination, loading, error, refetch: fetchArticles };
}

interface UseSearchArticlesResult {
  articles: Article[];
  pagination: PaginationMeta | null;
  loading: boolean;
  error: string | null;
}

export function useSearchArticles(
  query: string,
  page: number = 1,
  limit: number = 20
): UseSearchArticlesResult {
  const [articles, setArticles] = useState<Article[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async () => {
    if (!query || query.length < 2) {
      setArticles([]);
      setPagination(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.searchArticles({ query, page, limit });
      setArticles(response.data || []);
      setPagination(response.pagination || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setArticles([]);
    } finally {
      setLoading(false);
    }
  }, [query, page, limit]);

  useEffect(() => {
    const debounceTimer = setTimeout(search, 300);
    return () => clearTimeout(debounceTimer);
  }, [search]);

  return { articles, pagination, loading, error };
}
