import { createContext, useContext, useMemo, type ReactNode } from 'react';
import { useSources } from '../hooks/useSources';
import type { Source } from '../types';

export interface SourceStyle {
  color: string;
  colorLight: string;
  label: string;
  shortLabel: string;
  // Tailwind class names for styling
  gradient: string;
  badgeBg: string;
  badgeText: string;
  activeBg: string;
  bg: string;
}

interface SourceContextValue {
  sources: Source[];
  loading: boolean;
  error: string | null;
  getSourceStyle: (sourceSlug: string) => SourceStyle;
}

const DEFAULT_COLOR = '#64748b';

// Predefined styles for known sources
const SOURCE_STYLES: Record<string, {
  gradient: string;
  badgeBg: string;
  badgeText: string;
  activeBg: string;
  bg: string;
}> = {
  hackernews: {
    gradient: 'bg-gradient-to-br from-orange-500 to-orange-600',
    badgeBg: 'bg-orange-500/15',
    badgeText: 'text-orange-400',
    activeBg: 'bg-gradient-to-r from-orange-500 to-orange-600 text-white',
    bg: 'bg-orange-500/10 text-orange-400',
  },
  devto: {
    gradient: 'bg-gradient-to-br from-blue-500 to-blue-600',
    badgeBg: 'bg-blue-500/15',
    badgeText: 'text-blue-400',
    activeBg: 'bg-gradient-to-r from-blue-500 to-blue-600 text-white',
    bg: 'bg-blue-500/10 text-blue-400',
  },
  reddit: {
    gradient: 'bg-gradient-to-br from-orange-600 to-red-500',
    badgeBg: 'bg-red-500/15',
    badgeText: 'text-red-400',
    activeBg: 'bg-gradient-to-r from-orange-600 to-red-500 text-white',
    bg: 'bg-red-500/10 text-red-400',
  },
  lobsters: {
    gradient: 'bg-gradient-to-br from-red-600 to-red-700',
    badgeBg: 'bg-red-600/15',
    badgeText: 'text-red-400',
    activeBg: 'bg-gradient-to-r from-red-600 to-red-700 text-white',
    bg: 'bg-red-600/10 text-red-400',
  },
};

const DEFAULT_STYLES = {
  gradient: 'bg-gradient-to-br from-slate-500 to-slate-600',
  badgeBg: 'bg-slate-500/15',
  badgeText: 'text-slate-400',
  activeBg: 'bg-gradient-to-r from-slate-500 to-slate-600 text-white',
  bg: 'bg-slate-500/10 text-slate-400',
};

function lightenColor(hex: string, percent: number): string {
  const num = parseInt(hex.slice(1), 16);
  const amt = Math.round(2.55 * percent);
  const R = Math.min(255, (num >> 16) + amt);
  const G = Math.min(255, ((num >> 8) & 0x00ff) + amt);
  const B = Math.min(255, (num & 0x0000ff) + amt);
  return `#${((1 << 24) + (R << 16) + (G << 8) + B).toString(16).slice(1)}`;
}

function createSourceStyle(source: Source): SourceStyle {
  const uiConfig = source.ui_config;
  const color = uiConfig?.color || DEFAULT_COLOR;
  const shortLabel = uiConfig?.short_label || source.slug[0]?.toUpperCase() || '?';
  const styles = SOURCE_STYLES[source.slug] || DEFAULT_STYLES;

  return {
    color,
    colorLight: lightenColor(color, 20),
    label: source.name.toUpperCase(),
    shortLabel,
    ...styles,
  };
}

const SourceContext = createContext<SourceContextValue | null>(null);

export function SourceProvider({ children }: { children: ReactNode }) {
  const { sources, loading, error } = useSources();

  const sourceStyleMap = useMemo(() => {
    const map = new Map<string, SourceStyle>();
    for (const source of sources) {
      map.set(source.slug, createSourceStyle(source));
    }
    return map;
  }, [sources]);

  const getSourceStyle = (sourceSlug: string): SourceStyle => {
    return sourceStyleMap.get(sourceSlug) || {
      color: DEFAULT_COLOR,
      colorLight: lightenColor(DEFAULT_COLOR, 20),
      label: sourceSlug.toUpperCase(),
      shortLabel: sourceSlug[0]?.toUpperCase() || '?',
      ...DEFAULT_STYLES,
    };
  };

  return (
    <SourceContext.Provider value={{ sources, loading, error, getSourceStyle }}>
      {children}
    </SourceContext.Provider>
  );
}

export function useSourceContext(): SourceContextValue {
  const context = useContext(SourceContext);
  if (!context) {
    throw new Error('useSourceContext must be used within a SourceProvider');
  }
  return context;
}
