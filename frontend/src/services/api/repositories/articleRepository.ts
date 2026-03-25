/**
 * Article Repository
 * Handles all article-related API operations
 */

import { apiClient } from '../client';
import type { Article, PaginatedResponse, DataResponse } from '../../../types';

export interface GetArticlesParams {
  page?: number;
  limit?: number;
  source?: string | null;
}

export interface SearchArticlesParams {
  query: string;
  page?: number;
  limit?: number;
  source?: string | null;
}

class ArticleRepository {
  /**
   * Get paginated list of articles
   */
  async getAll(params: GetArticlesParams = {}): Promise<PaginatedResponse<Article>> {
    const { page = 1, limit = 20, source = null } = params;
    const searchParams = new URLSearchParams({
      page: String(page),
      limit: String(limit),
    });
    if (source) searchParams.append('source', source);

    return apiClient.get<PaginatedResponse<Article>>(`/articles?${searchParams}`);
  }

  /**
   * Get a single article by ID
   */
  async getById(articleId: string): Promise<DataResponse<Article>> {
    return apiClient.get<DataResponse<Article>>(`/articles/${articleId}`);
  }

  /**
   * Search articles by query
   */
  async search(params: SearchArticlesParams): Promise<PaginatedResponse<Article>> {
    const { query, page = 1, limit = 20, source = null } = params;
    const searchParams = new URLSearchParams({
      q: query,
      page: String(page),
      limit: String(limit),
    });
    if (source) searchParams.append('source', source);

    return apiClient.get<PaginatedResponse<Article>>(`/articles/search?${searchParams}`);
  }
}

export const articleRepository = new ArticleRepository();
export default articleRepository;
