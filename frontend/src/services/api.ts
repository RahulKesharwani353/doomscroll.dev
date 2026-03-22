import type {
  Article,
  Source,
  SyncJob,
  SyncStatus,
  HealthStatus,
  PaginatedResponse,
  ListResponse,
  DataResponse,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE_URL = `${BASE_URL}/api`;

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
}

interface GetArticlesParams {
  page?: number;
  limit?: number;
  source?: string | null;
}

interface SearchArticlesParams {
  query: string;
  page?: number;
  limit?: number;
}

interface GetSyncJobsParams {
  page?: number;
  limit?: number;
}

class ApiService {
  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'API request failed');
    }

    return data as T;
  }

  // Articles
  async getArticles({ page = 1, limit = 20, source = null }: GetArticlesParams = {}): Promise<PaginatedResponse<Article>> {
    const params = new URLSearchParams({ page: String(page), limit: String(limit) });
    if (source) params.append('source', source);
    return this.request<PaginatedResponse<Article>>(`/articles?${params}`);
  }

  async getArticle(articleId: string): Promise<DataResponse<Article>> {
    return this.request<DataResponse<Article>>(`/articles/${articleId}`);
  }

  async searchArticles({ query, page = 1, limit = 20 }: SearchArticlesParams): Promise<PaginatedResponse<Article>> {
    const params = new URLSearchParams({ q: query, page: String(page), limit: String(limit) });
    return this.request<PaginatedResponse<Article>>(`/articles/search?${params}`);
  }

  // Sources
  async getSources(): Promise<ListResponse<Source>> {
    return this.request<ListResponse<Source>>('/sources');
  }

  // Sync
  async getSyncStatus(): Promise<DataResponse<SyncStatus>> {
    return this.request<DataResponse<SyncStatus>>('/sync/status');
  }

  async getSyncJobs({ page = 1, limit = 10 }: GetSyncJobsParams = {}): Promise<PaginatedResponse<SyncJob>> {
    const params = new URLSearchParams({ page: String(page), limit: String(limit) });
    return this.request<PaginatedResponse<SyncJob>>(`/sync/jobs?${params}`);
  }

  // Health
  async getHealth(): Promise<DataResponse<HealthStatus>> {
    return this.request<DataResponse<HealthStatus>>('/health');
  }
}

const api = new ApiService();
export default api;
