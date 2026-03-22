// API Response Types
export interface PaginationMeta {
  page: number;
  limit: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface DataResponse<T> {
  success: boolean;
  message?: string;
  data: T;
}

export interface ListResponse<T> {
  success: boolean;
  message?: string;
  data: T[];
  count: number;
}

export interface PaginatedResponse<T> {
  success: boolean;
  message?: string;
  data: T[];
  pagination: PaginationMeta;
}

// Domain Types
export interface Article {
  id: string;
  title: string;
  url: string;
  author?: string;
  source: string;
  published_at: string;
  fetched_at: string;
  created_at?: string;
  updated_at?: string;
}

export interface Source {
  id: number;
  name: string;
  slug: string;
  base_url: string;
  is_enabled: boolean;
  article_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface SyncJob {
  id: number;
  source_id?: number;
  source_slug?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  articles_fetched: number;
  articles_created: number;
  articles_updated: number;
  articles_failed: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface SyncStatus {
  total_sources: number;
  enabled_sources: number;
  total_articles: number;
  last_sync?: SyncJob;
}

export interface HealthStatus {
  status: string;
  database: string;
  version: string;
}
