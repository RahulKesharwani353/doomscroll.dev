import { useContext } from 'react';
import { SourceContext, type SourceContextValue } from '../contexts/types';

export function useSourceContext(): SourceContextValue {
  const context = useContext(SourceContext);
  if (!context) {
    throw new Error('useSourceContext must be used within a SourceProvider');
  }
  return context;
}
