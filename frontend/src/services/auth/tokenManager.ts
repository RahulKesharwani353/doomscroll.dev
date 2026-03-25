/**
 * Centralized Token Manager
 * Handles access/refresh token storage and retrieval with automatic refresh
 */

const TOKEN_KEY = 'doomscroll_access_token';
const REFRESH_TOKEN_KEY = 'doomscroll_refresh_token';

type TokenRefreshCallback = (refreshToken: string) => Promise<{ access_token: string; refresh_token: string }>;

class TokenManager {
  private refreshCallback: TokenRefreshCallback | null = null;
  private refreshPromise: Promise<string | null> | null = null;
  private tokenExpiryTimer: ReturnType<typeof setTimeout> | null = null;

  /**
   * Set the callback function for refreshing tokens
   */
  setRefreshCallback(callback: TokenRefreshCallback): void {
    this.refreshCallback = callback;
  }

  /**
   * Get the current access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  /**
   * Get the current refresh token
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  /**
   * Store tokens after login/register
   */
  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    this.scheduleTokenRefresh(accessToken);
  }

  /**
   * Clear all tokens (logout)
   */
  clearTokens(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    this.clearRefreshTimer();
  }

  /**
   * Check if user has tokens stored
   */
  hasTokens(): boolean {
    return !!this.getAccessToken();
  }

  /**
   * Refresh the access token using the refresh token
   * Returns the new access token or null if refresh failed
   */
  async refreshAccessToken(): Promise<string | null> {
    // If already refreshing, wait for that to complete
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    const refreshToken = this.getRefreshToken();
    if (!refreshToken || !this.refreshCallback) {
      this.clearTokens();
      return null;
    }

    this.refreshPromise = this.performRefresh(refreshToken);
    const result = await this.refreshPromise;
    this.refreshPromise = null;
    return result;
  }

  private async performRefresh(refreshToken: string): Promise<string | null> {
    try {
      const tokens = await this.refreshCallback!(refreshToken);
      this.setTokens(tokens.access_token, tokens.refresh_token);
      return tokens.access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearTokens();
      return null;
    }
  }

  /**
   * Schedule automatic token refresh before expiry
   * Assumes JWT with exp claim
   */
  private scheduleTokenRefresh(accessToken: string): void {
    this.clearRefreshTimer();

    try {
      // Decode JWT to get expiry time
      const payload = JSON.parse(atob(accessToken.split('.')[1]));
      const expiryTime = payload.exp * 1000; // Convert to milliseconds
      const currentTime = Date.now();

      // Refresh 1 minute before expiry
      const refreshTime = expiryTime - currentTime - 60000;

      if (refreshTime > 0) {
        this.tokenExpiryTimer = setTimeout(() => {
          this.refreshAccessToken();
        }, refreshTime);
      }
    } catch {
      // If we can't decode the token, don't schedule refresh
      console.warn('Could not decode token for refresh scheduling');
    }
  }

  private clearRefreshTimer(): void {
    if (this.tokenExpiryTimer) {
      clearTimeout(this.tokenExpiryTimer);
      this.tokenExpiryTimer = null;
    }
  }

  /**
   * Get authorization header value
   */
  getAuthHeader(): string | null {
    const token = this.getAccessToken();
    return token ? `Bearer ${token}` : null;
  }
}

// Export singleton instance
export const tokenManager = new TokenManager();
export default tokenManager;
