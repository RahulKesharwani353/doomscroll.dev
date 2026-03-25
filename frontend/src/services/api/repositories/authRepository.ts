/**
 * Auth Repository
 * Handles all authentication-related API operations
 */

import { apiClient } from '../client';
import type {
  DataResponse,
  AuthResponse,
  TokenResponse,
  User,
  LoginCredentials,
  RegisterCredentials,
} from '../../../types';

class AuthRepository {
  /**
   * Register a new user
   */
  async register(credentials: RegisterCredentials): Promise<DataResponse<AuthResponse>> {
    return apiClient.post<DataResponse<AuthResponse>>('/auth/register', credentials, {
      requiresAuth: false,
    });
  }

  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<DataResponse<AuthResponse>> {
    return apiClient.post<DataResponse<AuthResponse>>('/auth/login', credentials, {
      requiresAuth: false,
    });
  }

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<DataResponse<TokenResponse>> {
    return apiClient.post<DataResponse<TokenResponse>>(
      '/auth/refresh',
      { refresh_token: refreshToken },
      { requiresAuth: false, skipRetry: true }
    );
  }

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<DataResponse<User>> {
    return apiClient.get<DataResponse<User>>('/auth/me');
  }

  /**
   * Logout user (invalidate token on server)
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout', undefined, { skipRetry: true });
    } catch {
      // Ignore logout errors - we'll clear tokens locally anyway
    }
  }
}

export const authRepository = new AuthRepository();
export default authRepository;
