import type { PaginationMeta } from '../types';

interface PaginationProps {
  pagination: PaginationMeta | null;
  onPageChange: (page: number) => void;
}

export default function Pagination({ pagination, onPageChange }: PaginationProps) {
  if (!pagination || pagination.total_pages <= 1) {
    return null;
  }

  const { page, total_pages, has_prev, has_next } = pagination;

  const getPageNumbers = (): number[] => {
    const pages: number[] = [];
    const maxVisible = 5;

    let start = Math.max(1, page - Math.floor(maxVisible / 2));
    let end = Math.min(total_pages, start + maxVisible - 1);

    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    return pages;
  };

  return (
    <div className="flex items-center justify-center gap-2 mt-8">
      {/* Previous Button */}
      <button
        disabled={!has_prev}
        onClick={() => onPageChange(page - 1)}
        className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
          has_prev
            ? 'bg-slate-800 text-slate-200 hover:bg-slate-700 hover:text-white'
            : 'bg-slate-900 text-slate-600 cursor-not-allowed'
        }`}
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        Prev
      </button>

      {/* Page Numbers */}
      <div className="flex items-center gap-1">
        {getPageNumbers().map((pageNum) => (
          <button
            key={pageNum}
            onClick={() => onPageChange(pageNum)}
            className={`w-10 h-10 flex items-center justify-center rounded-lg text-sm font-medium transition-colors cursor-pointer ${
              pageNum === page
                ? 'bg-purple-600 text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
            }`}
          >
            {pageNum}
          </button>
        ))}
      </div>

      {/* Next Button */}
      <button
        disabled={!has_next}
        onClick={() => onPageChange(page + 1)}
        className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
          has_next
            ? 'bg-slate-800 text-slate-200 hover:bg-slate-700 hover:text-white'
            : 'bg-slate-900 text-slate-600 cursor-not-allowed'
        }`}
      >
        Next
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>
    </div>
  );
}
