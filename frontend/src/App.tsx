import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Layout } from './components/layout/Layout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { HomePage } from './pages/HomePage';
import { RfcDetailPage } from './pages/RfcDetailPage';
import { RfcCreatePage } from './pages/RfcCreatePage';
import { RfcEditPage } from './pages/RfcEditPage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { VerifyEmailPage } from './pages/VerifyEmailPage';
import { ProfilePage } from './pages/ProfilePage';
import { NotFoundPage } from './pages/NotFoundPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route
              path="/rfc/new"
              element={
                <ProtectedRoute>
                  <RfcCreatePage />
                </ProtectedRoute>
              }
            />
            <Route path="/rfc/:id" element={<RfcDetailPage />} />
            <Route
              path="/rfc/:id/edit"
              element={
                <ProtectedRoute>
                  <RfcEditPage />
                </ProtectedRoute>
              }
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
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
