import { createContext, useContext, useState, useEffect, useCallback, useMemo, type ReactNode } from 'react';
import type { User, LoginCredentials, RegisterCredentials } from '../types';
import { tokenManager } from '../services/auth';
import { authRepository } from '../services/api';

// Separate state and actions for better performance
interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

interface AuthModalState {
  isAuthModalOpen: boolean;
  openAuthModal: () => void;
  closeAuthModal: () => void;
}

type AuthContextType = AuthState & AuthActions & AuthModalState;

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Setup token refresh callback
tokenManager.setRefreshCallback(async (refreshToken: string) => {
  const response = await authRepository.refreshToken(refreshToken);
  return {
    access_token: response.data.access_token,
    refresh_token: response.data.refresh_token,
  };
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const isAuthenticated = !!user;

  // Modal actions - memoized
  const openAuthModal = useCallback(() => setIsAuthModalOpen(true), []);
  const closeAuthModal = useCallback(() => setIsAuthModalOpen(false), []);
  const clearError = useCallback(() => setError(null), []);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      if (tokenManager.hasTokens()) {
        try {
          const response = await authRepository.getCurrentUser();
          setUser(response.data);
        } catch {
          // Token invalid or expired, try refresh
          const newToken = await tokenManager.refreshAccessToken();
          if (newToken) {
            try {
              const response = await authRepository.getCurrentUser();
              setUser(response.data);
            } catch {
              tokenManager.clearTokens();
            }
          }
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    setError(null);
    setIsLoading(true);
    try {
      const response = await authRepository.login(credentials);
      const { user, tokens } = response.data;

      tokenManager.setTokens(tokens.access_token, tokens.refresh_token);
      setUser(user);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (credentials: RegisterCredentials) => {
    setError(null);
    setIsLoading(true);
    try {
      const response = await authRepository.register(credentials);
      const { user, tokens } = response.data;

      tokenManager.setTokens(tokens.access_token, tokens.refresh_token);
      setUser(user);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    authRepository.logout(); // Fire and forget
    tokenManager.clearTokens();
    setUser(null);
  }, []);

  // Memoize context value to prevent unnecessary re-renders
  const value = useMemo<AuthContextType>(() => ({
    // State
    user,
    isLoading,
    isAuthenticated,
    error,
    // Actions
    login,
    register,
    logout,
    clearError,
    // Modal
    isAuthModalOpen,
    openAuthModal,
    closeAuthModal,
  }), [
    user,
    isLoading,
    isAuthenticated,
    error,
    login,
    register,
    logout,
    clearError,
    isAuthModalOpen,
    openAuthModal,
    closeAuthModal,
  ]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Optimized hooks for specific use cases
export function useAuthState(): AuthState {
  const { user, isLoading, isAuthenticated, error } = useAuth();
  return { user, isLoading, isAuthenticated, error };
}

export function useAuthActions(): AuthActions {
  const { login, register, logout, clearError } = useAuth();
  return { login, register, logout, clearError };
}

export function useAuthModal(): AuthModalState {
  const { isAuthModalOpen, openAuthModal, closeAuthModal } = useAuth();
  return { isAuthModalOpen, openAuthModal, closeAuthModal };
}
