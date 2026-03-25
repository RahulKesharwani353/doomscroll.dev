import { Component, type ReactNode, type ErrorInfo } from 'react';
import { AlertCircleIcon, HomeIcon, RefreshIcon } from '../assets/icons';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console in development
    console.error('Error caught by boundary:', error, errorInfo);

    // Call optional error handler
    this.props.onError?.(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  handleGoHome = (): void => {
    window.location.href = '/articles';
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-primary flex flex-col items-center justify-center px-4">
          <div className="text-center max-w-md">
            {/* Error Icon */}
            <div className="w-20 h-20 mx-auto mb-6 flex items-center justify-center bg-error rounded-full">
              <AlertCircleIcon className="w-10 h-10 text-error" />
            </div>

            {/* Error Message */}
            <h1 className="text-2xl font-bold text-primary mb-3">
              Something went wrong
            </h1>
            <p className="text-secondary text-sm mb-2">
              An unexpected error occurred. Don't worry, your data is safe.
            </p>

            {/* Error Details (Development Only) */}
            {import.meta.env.DEV && this.state.error && (
              <details className="mb-6 text-left">
                <summary className="text-muted text-xs cursor-pointer hover:text-secondary">
                  View error details
                </summary>
                <pre className="mt-2 p-3 bg-overlay-light rounded-lg text-xs text-error overflow-auto max-h-32">
                  {this.state.error.message}
                </pre>
              </details>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-6">
              <button
                onClick={this.handleReset}
                className="flex items-center gap-2 px-6 py-3 gradient-primary text-primary font-medium rounded-xl shadow-purple-md hover:shadow-purple-xl transition-all duration-200 hover:scale-105 active:scale-95"
              >
                <RefreshIcon className="w-5 h-5" />
                Try Again
              </button>
              <button
                onClick={this.handleGoHome}
                className="btn-outline flex items-center gap-2 px-6 py-3 font-medium rounded-xl transition-all duration-200 hover:scale-105 active:scale-95"
              >
                <HomeIcon className="w-5 h-5" />
                Go Home
              </button>
            </div>
          </div>

          {/* Decorative Elements */}
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-overlay-accent rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-overlay-accent rounded-full blur-3xl pointer-events-none" />
        </div>
      );
    }

    return this.props.children;
  }
}

// Hook for functional components to trigger error boundary
export function useErrorBoundary(): { showBoundary: (error: Error) => void } {
  return {
    showBoundary: (error: Error) => {
      throw error;
    },
  };
}

export default ErrorBoundary;
