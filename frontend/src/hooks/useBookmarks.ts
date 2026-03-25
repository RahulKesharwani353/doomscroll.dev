import { useContext } from 'react';
import { BookmarkContext, type BookmarkContextType } from '../contexts/types';

export function useBookmarks(): BookmarkContextType {
  const context = useContext(BookmarkContext);
  if (context === undefined) {
    throw new Error('useBookmarks must be used within a BookmarkProvider');
  }
  return context;
}
