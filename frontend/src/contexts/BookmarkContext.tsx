import { useState, useCallback, useMemo, type ReactNode } from 'react';
import { bookmarkRepository } from '../services/api';
import { tokenManager } from '../services/auth';
import { BookmarkContext } from './types';

export function BookmarkProvider({ children }: { children: ReactNode }) {
  const [bookmarkedIds, setBookmarkedIds] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);

  const isBookmarked = useCallback((articleId: string) => {
    return bookmarkedIds.has(articleId);
  }, [bookmarkedIds]);

  const toggleBookmark = useCallback(async (articleId: string) => {
    if (!tokenManager.hasTokens()) return;

    // Optimistic update
    const wasBookmarked = bookmarkedIds.has(articleId);
    setBookmarkedIds(prev => {
      const next = new Set(prev);
      if (wasBookmarked) {
        next.delete(articleId);
      } else {
        next.add(articleId);
      }
      return next;
    });

    try {
      if (wasBookmarked) {
        await bookmarkRepository.remove(articleId);
      } else {
        await bookmarkRepository.add(articleId);
      }
    } catch (error) {
      // Revert optimistic update on error
      setBookmarkedIds(prev => {
        const next = new Set(prev);
        if (wasBookmarked) {
          next.add(articleId);
        } else {
          next.delete(articleId);
        }
        return next;
      });
      console.error('Failed to toggle bookmark:', error);
    }
  }, [bookmarkedIds]);

  const loadBookmarks = useCallback(async () => {
    if (!tokenManager.hasTokens()) return;

    setIsLoading(true);
    try {
      const ids = await bookmarkRepository.getAllIds();
      setBookmarkedIds(ids);
    } catch (error) {
      console.error('Failed to load bookmarks:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value = useMemo(() => ({
    bookmarkedIds,
    isBookmarked,
    toggleBookmark,
    loadBookmarks,
    isLoading,
  }), [bookmarkedIds, isBookmarked, toggleBookmark, loadBookmarks, isLoading]);

  return (
    <BookmarkContext.Provider value={value}>
      {children}
    </BookmarkContext.Provider>
  );
}
