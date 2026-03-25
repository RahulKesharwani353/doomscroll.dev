import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogoIcon } from '../assets/icons';

type AuthMode = 'login' | 'register';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login, register, error, clearError } = useAuth();

  // Reset form when modal opens/closes
  useEffect(() => {
    if (!isOpen) {
      setEmail('');
      setPassword('');
      setMode('login');
      clearError();
    }
  }, [isOpen, clearError]);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setIsSubmitting(true);

    try {
      if (mode === 'login') {
        await login({ email, password });
      } else {
        await register({ email, password });
      }
      onClose();
    } catch {
      // Error handled by context
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    clearError();
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-overlay-dark backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Background gradient orbs */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-overlay-accent rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-overlay-accent rounded-full blur-[128px] pointer-events-none" />

      {/* Modal */}
      <div className="relative w-full max-w-[400px] animate-in fade-in zoom-in-95 duration-200">
        {/* Card */}
        <div className="relative bg-modal backdrop-blur-xl border border-subtle rounded-2xl p-8 shadow-2xl">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center text-muted hover:text-primary hover:bg-overlay-medium rounded-lg transition-all"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 flex items-center justify-center gradient-primary rounded-xl">
                <LogoIcon className="w-5 h-5 text-primary" />
              </div>
              <span className="text-xl font-semibold text-primary">Doomscroll</span>
            </div>
          </div>

          {/* Title */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-semibold text-primary mb-2">
              {mode === 'login' ? 'Welcome back' : 'Create account'}
            </h1>
            <p className="text-secondary text-sm">
              {mode === 'login'
                ? 'Sign in to continue to your feed'
                : 'Join to personalize your experience'}
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-error border border-error rounded-xl px-4 py-3 text-error text-sm">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm text-secondary">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
                className="input-field w-full h-12 px-4 rounded-xl transition-all"
                placeholder="name@example.com"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm text-secondary">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="input-field w-full h-12 px-4 rounded-xl transition-all"
                placeholder={mode === 'register' ? 'Min 6 characters' : 'Enter password'}
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full h-12 gradient-primary-dark text-primary font-medium rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed mt-6"
            >
              {isSubmitting
                ? (mode === 'login' ? 'Signing in...' : 'Creating account...')
                : (mode === 'login' ? 'Sign in' : 'Create account')}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-subtle" />
            <span className="text-muted text-sm">or</span>
            <div className="flex-1 h-px bg-subtle" />
          </div>

          {/* Toggle mode */}
          <button
            onClick={toggleMode}
            className="btn-alt w-full h-12 font-medium rounded-xl transition-all duration-200"
          >
            {mode === 'login' ? 'Create new account' : 'Sign in instead'}
          </button>
        </div>
      </div>
    </div>
  );
}
