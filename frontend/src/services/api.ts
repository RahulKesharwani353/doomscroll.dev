import type {
  Article,
  Source,
  SyncJob,
  SyncStatus,
  HealthStatus,
  PaginatedResponse,
  ListResponse,
  DataResponse,
  AuthResponse,
  LoginCredentials,
  RegisterCredentials,
  User,
  TokenResponse,
  Bookmark,
  BookmarkCheckResponse,
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
  source?: string | null;
}

interface GetSyncJobsParams {
  page?: number;
  limit?: number;
}

class ApiService {
  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const { headers, ...restOptions } = options;
    const config: RequestInit = {
      ...restOptions,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    };

    const response = await fetch(url, config);

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

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

  async searchArticles({ query, page = 1, limit = 20, source = null }: SearchArticlesParams): Promise<PaginatedResponse<Article>> {
    const params = new URLSearchParams({ q: query, page: String(page), limit: String(limit) });
    if (source) params.append('source', source);
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

  // Auth
  async register(credentials: RegisterCredentials): Promise<DataResponse<AuthResponse>> {
    return this.request<DataResponse<AuthResponse>>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async login(credentials: LoginCredentials): Promise<DataResponse<AuthResponse>> {
    return this.request<DataResponse<AuthResponse>>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async refreshToken(refreshToken: string): Promise<DataResponse<TokenResponse>> {
    return this.request<DataResponse<TokenResponse>>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  async getCurrentUser(accessToken: string): Promise<DataResponse<User>> {
    return this.request<DataResponse<User>>('/auth/me', {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
  }

  // Bookmarks
  async getBookmarks(accessToken: string, page = 1, limit = 20): Promise<PaginatedResponse<Bookmark>> {
    return this.request<PaginatedResponse<Bookmark>>(`/bookmarks?page=${page}&limit=${limit}`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
  }

  async addBookmark(accessToken: string, articleId: string): Promise<DataResponse<Bookmark>> {
    return this.request<DataResponse<Bookmark>>('/bookmarks', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ article_id: articleId }),
    });
  }

  async removeBookmark(accessToken: string, articleId: string): Promise<void> {
    await this.request<void>(`/bookmarks/${articleId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
  }

  async checkBookmark(accessToken: string, articleId: string): Promise<DataResponse<BookmarkCheckResponse>> {
    return this.request<DataResponse<BookmarkCheckResponse>>(`/bookmarks/check/${articleId}`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
  }
}

const api = new ApiService();
export default api;
