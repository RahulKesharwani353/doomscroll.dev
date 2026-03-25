import { useContext } from 'react';
import { AuthContext, type AuthContextType, type AuthState, type AuthActions, type AuthModalState } from '../contexts/types';

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

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
