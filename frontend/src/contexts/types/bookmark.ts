import { createContext } from 'react';

export interface BookmarkContextType {
  bookmarkedIds: Set<string>;
  isBookmarked: (articleId: string) => boolean;
  toggleBookmark: (articleId: string) => Promise<void>;
  loadBookmarks: () => Promise<void>;
  isLoading: boolean;
}

export const BookmarkContext = createContext<BookmarkContextType | undefined>(undefined);
