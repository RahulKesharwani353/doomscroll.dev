import { SpinnerIcon, LogoIcon } from '../assets/icons';

interface LoadingProps {
  fullScreen?: boolean;
  message?: string;
}

export default function Loading({ fullScreen = false, message = 'Loading...' }: LoadingProps) {
  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-primary flex flex-col items-center justify-center z-50">
        <div className="flex flex-col items-center gap-6 animate-fade-in">
          {/* Animated Logo */}
          <div className="relative">
            <div className="w-16 h-16 flex items-center justify-center gradient-primary rounded-2xl shadow-purple-md animate-pulse">
              <LogoIcon className="w-8 h-8 text-primary" />
            </div>
            {/* Rotating ring */}
            <div className="absolute -inset-2 border-2 border-overlay-accent-medium rounded-3xl animate-spin" style={{ animationDuration: '3s' }} />
          </div>

          {/* Loading text */}
          <div className="flex flex-col items-center gap-2">
            <div className="flex items-center gap-2">
              <SpinnerIcon className="w-5 h-5 text-accent" />
              <span className="text-lg font-medium text-primary">{message}</span>
            </div>
            <span className="text-sm text-muted">Please wait a moment</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-16 animate-fade-in">
      <div className="flex items-center gap-3">
        <SpinnerIcon className="w-6 h-6 text-accent" />
        <span className="text-base font-medium text-secondary">{message}</span>
      </div>
    </div>
  );
}
