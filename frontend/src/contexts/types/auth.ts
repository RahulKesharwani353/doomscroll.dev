import { createContext } from 'react';
import type { User, LoginCredentials, RegisterCredentials } from '../../types';

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

export interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export interface AuthModalState {
  isAuthModalOpen: boolean;
  openAuthModal: () => void;
  closeAuthModal: () => void;
}

export type AuthContextType = AuthState & AuthActions & AuthModalState;

export const AuthContext = createContext<AuthContextType | undefined>(undefined);
