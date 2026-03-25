/**
 * Source Repository
 * Handles all source-related API operations
 */

import { apiClient } from '../client';
import type { Source, SyncStatus, ListResponse, DataResponse } from '../../../types';

class SourceRepository {
  /**
   * Get all available sources
   */
  async getAll(): Promise<ListResponse<Source>> {
    return apiClient.get<ListResponse<Source>>('/sources', {
      requiresAuth: false,
    });
  }

  /**
   * Get current sync status
   */
  async getSyncStatus(): Promise<DataResponse<SyncStatus>> {
    return apiClient.get<DataResponse<SyncStatus>>('/sync/status', {
      requiresAuth: false,
    });
  }
}

export const sourceRepository = new SourceRepository();
export default sourceRepository;
