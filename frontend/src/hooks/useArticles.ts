import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../services/api';
import type { Article, PaginationMeta } from '../types';

interface UseArticlesResult {
  articles: Article[];
  pagination: PaginationMeta | null;
  loading: boolean;
  loadingMore: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  loadMore: () => Promise<void>;
  hasMore: boolean;
}

export function useArticles(
  source: string | null = null,
  limit: number = 20
): UseArticlesResult {
  const [articles, setArticles] = useState<Article[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchArticles = useCallback(async (page: number = 1, append: boolean = false) => {
    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      const response = await api.getArticles({ page, limit, source });
      if (append) {
        setArticles(prev => [...prev, ...(response.data || [])]);
      } else {
        setArticles(response.data || []);
      }
      setPagination(response.pagination || null);
      setCurrentPage(page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      if (!append) {
        setArticles([]);
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [source, limit]);

  const refetch = useCallback(async () => {
    setCurrentPage(1);
    await fetchArticles(1, false);
  }, [fetchArticles]);

  const loadMore = useCallback(async () => {
    if (pagination?.has_next && !loadingMore) {
      await fetchArticles(currentPage + 1, true);
    }
  }, [fetchArticles, currentPage, pagination?.has_next, loadingMore]);

  useEffect(() => {
    setCurrentPage(1);
    setArticles([]);
    fetchArticles(1, false);
  }, [source, limit]);

  const hasMore = pagination?.has_next ?? false;

  return { articles, pagination, loading, loadingMore, error, refetch, loadMore, hasMore };
}

interface UseSearchArticlesResult {
  articles: Article[];
  pagination: PaginationMeta | null;
  loading: boolean;
  loadingMore: boolean;
  error: string | null;
  loadMore: () => Promise<void>;
  hasMore: boolean;
}

export function useSearchArticles(
  query: string,
  limit: number = 20,
  source: string | null = null
): UseSearchArticlesResult {
  const [articles, setArticles] = useState<Article[]>([]);
  const [pagination, setPagination] = useState<PaginationMeta | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [debouncedQuery, setDebouncedQuery] = useState<string>(query);
  const isFirstRender = useRef(true);

  // Debounce the query - set loading immediately when typing starts
  useEffect(() => {
    // Skip on first render
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    // If query is being typed (length >= 2), show loading immediately
    if (query.length >= 2) {
      setLoading(true);
    }

    const debounceTimer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 400);

    return () => clearTimeout(debounceTimer);
  }, [query]);

  const search = useCallback(async (page: number = 1, append: boolean = false) => {
    if (!debouncedQuery || debouncedQuery.length < 2) {
      setArticles([]);
      setPagination(null);
      setLoading(false);
      return;
    }

    if (append) {
      setLoadingMore(true);
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      const response = await api.searchArticles({ query: debouncedQuery, page, limit, source });
      if (append) {
        setArticles(prev => [...prev, ...(response.data || [])]);
      } else {
        setArticles(response.data || []);
      }
      setPagination(response.pagination || null);
      setCurrentPage(page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      if (!append) {
        setArticles([]);
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [debouncedQuery, limit, source]);

  const loadMore = useCallback(async () => {
    if (pagination?.has_next && !loadingMore) {
      await search(currentPage + 1, true);
    }
  }, [search, currentPage, pagination?.has_next, loadingMore]);

  // Fetch when debounced query or source changes
  useEffect(() => {
    setCurrentPage(1);
    search(1, false);
  }, [debouncedQuery, limit, source]);

  const hasMore = pagination?.has_next ?? false;

  return { articles, pagination, loading, loadingMore, error, loadMore, hasMore };
}
