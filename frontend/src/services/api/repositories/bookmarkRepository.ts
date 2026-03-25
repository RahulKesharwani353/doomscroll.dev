/**
 * Bookmark Repository
 * Handles all bookmark-related API operations
 */

import { apiClient } from '../client';
import type { Bookmark, PaginatedResponse, DataResponse, BookmarkCheckResponse } from '../../../types';

class BookmarkRepository {
  /**
   * Get paginated list of user's bookmarks
   */
  async getAll(page = 1, limit = 20): Promise<PaginatedResponse<Bookmark>> {
    return apiClient.get<PaginatedResponse<Bookmark>>(
      `/bookmarks?page=${page}&limit=${limit}`
    );
  }

  /**
   * Add a bookmark for an article
   */
  async add(articleId: string): Promise<DataResponse<Bookmark>> {
    return apiClient.post<DataResponse<Bookmark>>('/bookmarks', {
      article_id: articleId,
    });
  }

  /**
   * Remove a bookmark
   */
  async remove(articleId: string): Promise<void> {
    await apiClient.delete<void>(`/bookmarks/${articleId}`);
  }

  /**
   * Check if an article is bookmarked
   */
  async check(articleId: string): Promise<DataResponse<BookmarkCheckResponse>> {
    return apiClient.get<DataResponse<BookmarkCheckResponse>>(
      `/bookmarks/check/${articleId}`
    );
  }

  /**
   * Get all bookmark IDs for quick lookup
   */
  async getAllIds(): Promise<Set<string>> {
    const bookmarkIds = new Set<string>();
    let page = 1;
    let hasMore = true;

    while (hasMore) {
      const response = await this.getAll(page, 100);
      for (const bookmark of response.data) {
        bookmarkIds.add(bookmark.article.id);
      }
      hasMore = response.pagination.has_next;
      page++;
    }

    return bookmarkIds;
  }
}

export const bookmarkRepository = new BookmarkRepository();
export default bookmarkRepository;
