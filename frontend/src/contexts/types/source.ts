import { createContext } from 'react';
import type { Source } from '../../types';

export interface SourceStyle {
  color: string;
  colorLight: string;
  label: string;
  shortLabel: string;
  gradient: string;
  badgeBg: string;
  badgeText: string;
  activeBg: string;
  bg: string;
}

export interface SourceContextValue {
  sources: Source[];
  loading: boolean;
  error: string | null;
  getSourceStyle: (sourceSlug: string) => SourceStyle;
}

export const SourceContext = createContext<SourceContextValue | null>(null);
