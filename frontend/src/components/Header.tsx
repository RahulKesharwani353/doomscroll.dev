import type { ChangeEvent } from 'react';

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onMenuToggle?: () => void;
}

export default function Header({ searchQuery, onSearchChange, onMenuToggle }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-4 sm:px-6 lg:px-8 h-[60px] sm:h-[69px] bg-[rgba(20,20,30,0.8)] backdrop-blur-md border-b border-white/10">
      {/* Mobile Menu Button */}
      <button
        onClick={onMenuToggle}
        className="md:hidden w-10 h-10 flex items-center justify-center text-slate-400 hover:text-white transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
      >
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      {/* Logo */}
      <div className="flex items-center gap-2 sm:gap-2.5 group cursor-pointer">
        <div className="w-8 h-8 sm:w-9 sm:h-9 flex items-center justify-center bg-gradient-to-br from-purple-500 to-indigo-500 rounded-[8px] sm:rounded-[10px] shadow-[0px_4px_15px_0px_rgba(168,85,247,0.15)] transition-all duration-300 group-hover:shadow-[0px_4px_20px_0px_rgba(168,85,247,0.3)] group-hover:scale-105">
          <svg className="w-4 h-4 sm:w-5 sm:h-5 text-white transition-transform duration-300 group-hover:rotate-12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z" />
            <path d="M2 17l10 5 10-5" />
            <path d="M2 12l10 5 10-5" />
          </svg>
        </div>
        <span className="hidden sm:block text-lg sm:text-xl font-bold text-white transition-colors duration-200 group-hover:text-purple-300">
          Doomscroll.dev
        </span>
      </div>

      {/* Search - Responsive */}
      <div className="flex-1 max-w-[480px] mx-4 sm:mx-6 lg:absolute lg:left-1/2 lg:-translate-x-1/2 lg:w-[480px]">
        <div className="relative group">
          <svg
            className="absolute left-3 sm:left-[14px] top-1/2 -translate-y-1/2 w-4 h-4 sm:w-[18px] sm:h-[18px] text-slate-500 transition-colors duration-200 group-focus-within:text-purple-400"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="M21 21l-4.35-4.35" />
          </svg>
          <input
            type="text"
            className="w-full h-10 sm:h-11 pl-10 sm:pl-11 pr-4 bg-white/5 border border-white/10 rounded-xl text-white text-sm placeholder-slate-500 focus:outline-none focus:border-purple-500/50 focus:bg-white/[0.07] transition-all duration-200"
            placeholder="Search articles..."
            value={searchQuery}
            onChange={(e: ChangeEvent<HTMLInputElement>) => onSearchChange(e.target.value)}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button className="hidden sm:flex w-10 h-10 items-center justify-center bg-white/5 border border-white/10 rounded-[10px] text-slate-400 hover:text-white hover:bg-white/10 hover:border-white/20 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
        </button>
        <button className="w-9 h-9 sm:w-10 sm:h-10 flex items-center justify-center bg-gradient-to-br from-purple-500 to-indigo-500 rounded-[8px] sm:rounded-[10px] shadow-[0px_4px_15px_0px_rgba(168,85,247,0.15)] text-white transition-all duration-200 hover:shadow-[0px_4px_20px_0px_rgba(168,85,247,0.35)] hover:scale-105 active:scale-95 cursor-pointer">
          <svg className="w-4 h-4 sm:w-5 sm:h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="7" r="4" />
            <path d="M5.5 21a7.5 7.5 0 0 1 13 0" />
          </svg>
        </button>
      </div>
    </header>
  );
}
