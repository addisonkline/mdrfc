import { BrowserRouter, Navigate, Route, Routes, useParams } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Layout } from './components/layout/Layout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { AdminRoute } from './components/layout/AdminRoute';
import { HomePage } from './pages/HomePage';
import { RfcDetailPage } from './pages/RfcDetailPage';
import { RfcCreatePage } from './pages/RfcCreatePage';
import { RfcRevisionCreatePage } from './pages/RfcRevisionCreatePage';
import { RfcRevisionsPage } from './pages/RfcRevisionsPage';
import { RfcRevisionDetailPage } from './pages/RfcRevisionDetailPage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { VerifyEmailPage } from './pages/VerifyEmailPage';
import { ProfilePage } from './pages/ProfilePage';
import { ReadmePage } from './pages/ReadmePage';
import { ReadmeRevisionsPage } from './pages/ReadmeRevisionsPage';
import { ReadmeRevisionDetailPage } from './pages/ReadmeRevisionDetailPage';
import { ReadmeRevisionCreatePage } from './pages/ReadmeRevisionCreatePage';
import { AdminReviewQueuePage } from './pages/AdminReviewQueuePage';
import { QuarantinedRfcsPage } from './pages/QuarantinedRfcsPage';
import { QuarantinedCommentsPage } from './pages/QuarantinedCommentsPage';
import { NotFoundPage } from './pages/NotFoundPage';

function LegacyRfcDetailRedirect() {
  const { id } = useParams<{ id: string }>();
  return <Navigate to={`/rfcs/${id}`} replace />;
}

function LegacyRfcEditRedirect() {
  const { id } = useParams<{ id: string }>();
  return <Navigate to={`/rfcs/${id}/revisions/new`} replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/rfcs" element={<HomePage />} />
            <Route
              path="/rfcs/new"
              element={
                <ProtectedRoute>
                  <RfcCreatePage />
                </ProtectedRoute>
              }
            />
            <Route path="/rfcs/:id" element={<RfcDetailPage />} />
            <Route path="/rfcs/:id/revisions" element={<RfcRevisionsPage />} />
            <Route
              path="/rfcs/:id/revisions/new"
              element={
                <ProtectedRoute>
                  <RfcRevisionCreatePage />
                </ProtectedRoute>
              }
            />
            <Route path="/rfcs/:id/revisions/:revisionId" element={<RfcRevisionDetailPage />} />
            <Route path="/rfc/new" element={<Navigate to="/rfcs/new" replace />} />
            <Route path="/rfc/:id" element={<LegacyRfcDetailRedirect />} />
            <Route path="/rfc/:id/edit" element={<LegacyRfcEditRedirect />} />
            <Route path="/readme" element={<ReadmePage />} />
            <Route path="/readme/revisions" element={<ReadmeRevisionsPage />} />
            <Route
              path="/readme/revisions/:revisionId"
              element={<ReadmeRevisionDetailPage />}
            />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <Navigate to="/admin/review-needed" replace />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/review-needed"
              element={
                <AdminRoute>
                  <AdminReviewQueuePage />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/quarantined/rfcs"
              element={
                <AdminRoute>
                  <QuarantinedRfcsPage />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/rfcs/:id/comments/quarantined"
              element={
                <AdminRoute>
                  <QuarantinedCommentsPage />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/readme/revisions/new"
              element={
                <AdminRoute>
                  <ReadmeRevisionCreatePage />
                </AdminRoute>
              }
            />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
