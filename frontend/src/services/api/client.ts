/**
 * Base API Client with interceptor support
 * Handles request/response interceptors, retry logic, and error handling
 */

import { tokenManager } from '../auth';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE_URL = `${BASE_URL}/api`;

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;
const RETRYABLE_STATUS_CODES = [408, 429, 500, 502, 503, 504];

export interface RequestConfig extends RequestInit {
  headers?: Record<string, string>;
  requiresAuth?: boolean;
  skipRetry?: boolean;
}

export class ApiError extends Error {
  status: number;
  data?: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

type RequestInterceptor = (config: RequestConfig) => RequestConfig | Promise<RequestConfig>;
type ResponseInterceptor = (response: Response) => Response | Promise<Response>;
type ErrorInterceptor = (error: ApiError) => Promise<never>;

class ApiClient {
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];
  private errorInterceptors: ErrorInterceptor[] = [];

  constructor() {
    this.setupDefaultInterceptors();
  }

  /**
   * Add a request interceptor
   */
  addRequestInterceptor(interceptor: RequestInterceptor): () => void {
    this.requestInterceptors.push(interceptor);
    return () => {
      const index = this.requestInterceptors.indexOf(interceptor);
      if (index > -1) this.requestInterceptors.splice(index, 1);
    };
  }

  /**
   * Add a response interceptor
   */
  addResponseInterceptor(interceptor: ResponseInterceptor): () => void {
    this.responseInterceptors.push(interceptor);
    return () => {
      const index = this.responseInterceptors.indexOf(interceptor);
      if (index > -1) this.responseInterceptors.splice(index, 1);
    };
  }

  /**
   * Add an error interceptor
   */
  addErrorInterceptor(interceptor: ErrorInterceptor): () => void {
    this.errorInterceptors.push(interceptor);
    return () => {
      const index = this.errorInterceptors.indexOf(interceptor);
      if (index > -1) this.errorInterceptors.splice(index, 1);
    };
  }

  private setupDefaultInterceptors(): void {
    // Add auth header interceptor
    this.addRequestInterceptor((config) => {
      if (config.requiresAuth !== false) {
        const authHeader = tokenManager.getAuthHeader();
        if (authHeader) {
          config.headers = {
            ...config.headers,
            'Authorization': authHeader,
          };
        }
      }
      return config;
    });

    // Add 401 error interceptor for token refresh
    this.addErrorInterceptor(async (error) => {
      if (error.status === 401 && tokenManager.hasTokens()) {
        const newToken = await tokenManager.refreshAccessToken();
        if (newToken) {
          // Token refreshed, but we can't retry automatically here
          // The calling code should handle retry
          throw new ApiError('Token refreshed, please retry', 401, { tokenRefreshed: true });
        }
      }
      throw error;
    });
  }

  /**
   * Make an API request with interceptors and retry logic
   */
  async request<T>(endpoint: string, options: RequestConfig = {}): Promise<T> {
    let config: RequestConfig = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    // Run request interceptors
    for (const interceptor of this.requestInterceptors) {
      config = await interceptor(config);
    }

    const url = `${API_BASE_URL}${endpoint}`;
    let lastError: ApiError | null = null;
    const maxAttempts = config.skipRetry ? 1 : MAX_RETRIES;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        let response = await fetch(url, config);

        // Run response interceptors
        for (const interceptor of this.responseInterceptors) {
          response = await interceptor(response);
        }

        // Handle 204 No Content
        if (response.status === 204) {
          return undefined as T;
        }

        const data = await response.json();

        if (!response.ok) {
          const error = new ApiError(
            data.detail || data.message || 'API request failed',
            response.status,
            data
          );

          // Run error interceptors
          for (const interceptor of this.errorInterceptors) {
            await interceptor(error);
          }

          throw error;
        }

        return data as T;
      } catch (error) {
        if (error instanceof ApiError) {
          lastError = error;

          // Check if we should retry
          if (
            attempt < maxAttempts &&
            RETRYABLE_STATUS_CODES.includes(error.status)
          ) {
            await this.delay(RETRY_DELAY * attempt);
            continue;
          }

          throw error;
        }

        // Network error or other fetch error
        lastError = new ApiError(
          error instanceof Error ? error.message : 'Network error',
          0
        );

        if (attempt < maxAttempts) {
          await this.delay(RETRY_DELAY * attempt);
          continue;
        }

        throw lastError;
      }
    }

    throw lastError || new ApiError('Request failed', 0);
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // Convenience methods
  async get<T>(endpoint: string, options?: Omit<RequestConfig, 'method'>): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(endpoint: string, body?: unknown, options?: Omit<RequestConfig, 'method' | 'body'>): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(endpoint: string, body?: unknown, options?: Omit<RequestConfig, 'method' | 'body'>): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(endpoint: string, options?: Omit<RequestConfig, 'method'>): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;
