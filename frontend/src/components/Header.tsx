import type { ChangeEvent } from 'react';
import { LogoIcon, SearchIcon, UserIcon } from '../assets/icons';

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export default function Header({ searchQuery, onSearchChange }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-4 sm:px-6 lg:px-8 h-[60px] sm:h-[69px] bg-[rgba(20,20,30,0.8)] backdrop-blur-md border-b border-white/10">
      {/* Logo */}
      <div className="flex items-center group cursor-pointer">
        <div className="w-8 h-8 mr-4 sm:w-9 sm:h-9 flex items-center justify-center bg-gradient-to-br from-purple-500 to-indigo-500 rounded-[8px] shadow-[0px_4px_15px_0px_rgba(168,85,247,0.15)] transition-all duration-300 group-hover:shadow-[0px_4px_20px_0px_rgba(168,85,247,0.3)] group-hover:scale-105">
          <LogoIcon className="w-4 h-4 sm:w-5 sm:h-5 text-white transition-transform duration-300 group-hover:rotate-12" />
        </div>
        <div className="hidden sm:block text-lg sm:text-xl font-medium text-white">
          Doomscroll
        </div>
        <div className="hidden sm:block text-lg sm:text-xl font-medium text-white transition-colors duration-200 group-hover:text-purple-300">
          .dev
        </div>
      </div>

      {/* Search - Responsive */}
      <div className="flex-1 max-w-[480px] mx-4 sm:mx-6 lg:absolute lg:left-1/2 lg:-translate-x-1/2 lg:w-[480px]">
        <div className="relative group">
          <SearchIcon className="absolute left-3 sm:left-[14px] top-1/2 -translate-y-1/2 w-4 h-4 sm:w-[18px] sm:h-[18px] text-slate-500 transition-colors duration-200 group-focus-within:text-purple-400" />
          <input
            type="text"
            className="w-full h-10 sm:h-11 pl-10 sm:pl-11 pr-4 bg-white/5 border border-white/10 rounded-[8px] text-white text-sm placeholder-slate-500 focus:outline-none focus:border-purple-500/50 focus:bg-white/[0.07] transition-all duration-200"
            placeholder="Search articles..."
            value={searchQuery}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onSearchChange(e.target.value)
            }
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button className="w-9 h-9 sm:w-10 sm:h-10 flex items-center justify-center bg-gradient-to-br from-purple-500 to-indigo-500 rounded-[8px] shadow-[0px_4px_15px_0px_rgba(168,85,247,0.15)] text-white transition-all duration-200 hover:shadow-[0px_4px_20px_0px_rgba(168,85,247,0.35)] hover:scale-105 active:scale-95 cursor-pointer">
          <UserIcon className="w-4 h-4 sm:w-5 sm:h-5" />
        </button>
      </div>
    </header>
  );
}
