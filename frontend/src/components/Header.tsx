import { useState, useRef, useEffect } from 'react';
import type { ChangeEvent } from 'react';
import { Link } from 'react-router-dom';
import { LogoIcon, SearchIcon, UserIcon, BookmarkIcon } from '../assets/icons';
import { useAuth } from '../hooks';

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export default function Header({ searchQuery, onSearchChange }: HeaderProps) {
  const { user, isAuthenticated, logout, openAuthModal } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-4 sm:px-6 lg:px-8 h-[60px] sm:h-[69px] bg-header backdrop-blur-md border-b border-default">
      {/* Logo */}
      <Link to="/articles" className="flex items-center group cursor-pointer">
        <div className="w-8 h-8 mr-4 sm:w-9 sm:h-9 flex items-center justify-center gradient-primary rounded-[8px] shadow-purple-sm transition-all duration-300 group-hover:shadow-purple-md group-hover:scale-105">
          <LogoIcon className="w-4 h-4 sm:w-5 sm:h-5 text-primary transition-transform duration-300 group-hover:rotate-12" />
        </div>
        <div className="hidden sm:block text-lg sm:text-xl font-medium text-primary">
          Doomscroll
        </div>
        <div className="hidden sm:block text-lg sm:text-xl font-medium text-primary transition-colors duration-200 group-hover:text-accent-light">
          .dev
        </div>
      </Link>

      {/* Search - Responsive */}
      <div className="flex-1 max-w-[480px] mx-4 sm:mx-6 lg:absolute lg:left-1/2 lg:-translate-x-1/2 lg:w-[480px]">
        <div className="relative group">
          <SearchIcon className="absolute left-3 sm:left-[14px] top-1/2 -translate-y-1/2 w-4 h-4 sm:w-[18px] sm:h-[18px] text-muted transition-colors duration-200 focus-within:text-accent group-focus-within:text-accent" />
          <input
            type="text"
            className="input-search w-full h-10 sm:h-11 pl-10 sm:pl-11 pr-4 text-sm transition-all duration-200"
            placeholder="Search articles..."
            value={searchQuery}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              onSearchChange(e.target.value)
            }
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 relative" ref={dropdownRef}>
        {isAuthenticated ? (
          <>
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="w-9 h-9 sm:w-10 sm:h-10 flex items-center justify-center gradient-primary rounded-[8px] shadow-purple-sm text-primary transition-all duration-200 hover:shadow-purple-lg hover:scale-105 active:scale-95 cursor-pointer"
            >
              <UserIcon className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>

            {showDropdown && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-dropdown border border-default rounded-[8px] shadow-xl overflow-hidden">
                <div className="px-4 py-3 border-b border-default">
                  <p className="text-sm text-primary font-medium truncate">{user?.email}</p>
                </div>
                <Link
                  to="/bookmarks"
                  onClick={() => setShowDropdown(false)}
                  className="w-full px-4 py-2 text-left text-sm text-secondary hover:bg-overlay-light transition-colors flex items-center gap-2"
                >
                  <BookmarkIcon className="w-4 h-4" />
                  Bookmarks
                </Link>
                <button
                  onClick={() => {
                    logout();
                    setShowDropdown(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-secondary hover:bg-overlay-light transition-colors"
                >
                  Sign out
                </button>
              </div>
            )}
          </>
        ) : (
          <button
            onClick={openAuthModal}
            className="px-4 py-2 text-sm font-medium text-primary gradient-primary-dark rounded-[8px] transition-all duration-200"
          >
            Sign In
          </button>
        )}
      </div>
    </header>
  );
}
