import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ArticlesPage, NotFoundPage } from './pages';
import { SourceProvider } from './contexts/SourceContext';

export default function App() {
  return (
    <SourceProvider>
      <BrowserRouter>
        <Routes>
          {/* Redirect root to /articles */}
          <Route path="/" element={<Navigate to="/articles" replace />} />

          {/* Main articles page */}
          <Route path="/articles" element={<ArticlesPage />} />

          {/* 404 for any other route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </SourceProvider>
  );
}
