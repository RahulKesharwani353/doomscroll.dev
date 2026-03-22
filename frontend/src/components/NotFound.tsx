import { NotFoundIcon, HomeIcon, ArrowLeftIcon } from '../assets/icons';

interface NotFoundProps {
  onGoHome?: () => void;
  onGoBack?: () => void;
}

export default function NotFound({ onGoHome, onGoBack }: NotFoundProps) {
  const handleGoHome = () => {
    if (onGoHome) {
      onGoHome();
    } else {
      window.location.href = '/';
    }
  };

  const handleGoBack = () => {
    if (onGoBack) {
      onGoBack();
    } else {
      window.history.back();
    }
  };

  return (
    <div className="min-h-screen bg-[rgb(10,10,15)] flex flex-col items-center justify-center px-4 animate-fade-in">
      {/* 404 Illustration */}
      <div className="relative mb-8">
        <div className="text-[120px] sm:text-[180px] font-bold text-white/5 select-none">
          404
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-20 h-20 sm:w-24 sm:h-24 flex items-center justify-center bg-gradient-to-br from-purple-500/20 to-indigo-500/20 rounded-full">
            <NotFoundIcon className="w-12 h-12 sm:w-16 sm:h-16 text-purple-400" />
          </div>
        </div>
      </div>

      {/* Text Content */}
      <div className="text-center max-w-md">
        <h1 className="text-2xl sm:text-3xl font-bold text-white mb-3">
          Page Not Found
        </h1>
        <p className="text-slate-400 text-sm sm:text-base mb-8">
          Oops! The page you're looking for doesn't exist or has been moved.
          Let's get you back on track.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            onClick={handleGoHome}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-br from-purple-500 to-indigo-500 text-white font-medium rounded-xl shadow-[0px_4px_15px_0px_rgba(168,85,247,0.3)] hover:shadow-[0px_4px_25px_0px_rgba(168,85,247,0.4)] transition-all duration-200 hover:scale-105 active:scale-95"
          >
            <HomeIcon className="w-5 h-5" />
            Go Home
          </button>
          <button
            onClick={handleGoBack}
            className="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 text-slate-300 font-medium rounded-xl hover:bg-white/10 hover:border-white/20 hover:text-white transition-all duration-200 hover:scale-105 active:scale-95"
          >
            <ArrowLeftIcon className="w-5 h-5" />
            Go Back
          </button>
        </div>
      </div>

      {/* Decorative Elements */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />
    </div>
  );
}
