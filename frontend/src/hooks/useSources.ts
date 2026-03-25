import { useState, useEffect } from 'react';
import { sourceRepository } from '../services/api';
import type { Source, SyncStatus } from '../types';

interface UseSourcesResult {
  sources: Source[];
  loading: boolean;
  error: string | null;
}

export function useSources(): UseSourcesResult {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSources = async () => {
      try {
        const response = await sourceRepository.getAll();
        setSources(response.data || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchSources();
  }, []);

  return { sources, loading, error };
}

interface UseSyncStatusResult {
  status: SyncStatus | null;
  loading: boolean;
  error: string | null;
}

export function useSyncStatus(): UseSyncStatusResult {
  const [status, setStatus] = useState<SyncStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await sourceRepository.getSyncStatus();
        setStatus(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();

    // Refresh every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return { status, loading, error };
}
