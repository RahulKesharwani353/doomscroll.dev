import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import api from '../services/api';

const TOKEN_KEY = 'doomscroll_access_token';

interface BookmarkContextType {
  bookmarkedIds: Set<string>;
  isBookmarked: (articleId: string) => boolean;
  toggleBookmark: (articleId: string) => Promise<void>;
  loadBookmarks: () => Promise<void>;
  isLoading: boolean;
}

const BookmarkContext = createContext<BookmarkContextType | undefined>(undefined);

export function BookmarkProvider({ children }: { children: ReactNode }) {
  const [bookmarkedIds, setBookmarkedIds] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);

  const getToken = () => localStorage.getItem(TOKEN_KEY);

  const isBookmarked = useCallback((articleId: string) => {
    return bookmarkedIds.has(articleId);
  }, [bookmarkedIds]);

  const toggleBookmark = useCallback(async (articleId: string) => {
    const token = getToken();
    if (!token) return;

    setIsLoading(true);
    try {
      if (bookmarkedIds.has(articleId)) {
        await api.removeBookmark(token, articleId);
        setBookmarkedIds(prev => {
          const next = new Set(prev);
          next.delete(articleId);
          return next;
        });
      } else {
        await api.addBookmark(token, articleId);
        setBookmarkedIds(prev => new Set(prev).add(articleId));
      }
    } catch (error) {
      console.error('Failed to toggle bookmark:', error);
    } finally {
      setIsLoading(false);
    }
  }, [bookmarkedIds]);

  const loadBookmarks = useCallback(async () => {
    const token = getToken();
    if (!token) return;

    try {
      // Fetch all bookmarks (use high limit to get all)
      const response = await api.getBookmarks(token, 1, 100);
      const ids = response.data.map(b => b.article.id);
      setBookmarkedIds(new Set(ids));
    } catch (error) {
      console.error('Failed to load bookmarks:', error);
    }
  }, []);

  return (
    <BookmarkContext.Provider value={{
      bookmarkedIds,
      isBookmarked,
      toggleBookmark,
      loadBookmarks,
      isLoading,
    }}>
      {children}
    </BookmarkContext.Provider>
  );
}

export function useBookmarks() {
  const context = useContext(BookmarkContext);
  if (context === undefined) {
    throw new Error('useBookmarks must be used within a BookmarkProvider');
  }
  return context;
}
