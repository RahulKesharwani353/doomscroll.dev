import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ArticlesPage, NotFoundPage, BookmarksPage } from './pages';
import { SourceProvider } from './contexts/SourceContext';
import { AuthProvider } from './contexts/AuthContext';
import { BookmarkProvider } from './contexts/BookmarkContext';
import { ErrorBoundary } from './components';
import AuthModal from './components/AuthModal';
import { useAuth } from './hooks';

function AppContent() {
  const { isAuthModalOpen, closeAuthModal } = useAuth();

  return (
    <>
      <Routes>
        {/* Redirect root to /articles */}
        <Route path="/" element={<Navigate to="/articles" replace />} />

        {/* Main articles page */}
        <Route path="/articles" element={<ArticlesPage />} />

        {/* Bookmarks page (requires auth) */}
        <Route path="/bookmarks" element={<BookmarksPage />} />

        {/* 404 for any other route */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>

      <AuthModal isOpen={isAuthModalOpen} onClose={closeAuthModal} />
    </>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BookmarkProvider>
          <SourceProvider>
            <BrowserRouter>
              <AppContent />
            </BrowserRouter>
          </SourceProvider>
        </BookmarkProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
