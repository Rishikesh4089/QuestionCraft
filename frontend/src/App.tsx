import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { AuthProvider, useAuth } from "./contexts/AuthContext";

import LandingPage from "./pages/Landing/LandingPage";
import LoginPage from "./pages/Auth/LoginPage";
import SignupPage from "./pages/Auth/SignupPage";

import MainLayout from "./pages/MainLayout";

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--qc-bg)] flex items-center justify-center">
        <div className="text-center">
          <div
            className="
              w-14
              h-14
              border-4
              border-[var(--qc-primary)]
              border-t-transparent
              rounded-full
              animate-spin
              mx-auto
              mb-6
            "
          />

          <p className="text-[var(--qc-text-secondary)]">
            Loading...
          </p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Public */}

      <Route
        path="/"
        element={
          user ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <LandingPage />
          )
        }
      />

      <Route
        path="/login"
        element={
          user ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <LoginPage />
          )
        }
      />

      <Route
        path="/signup"
        element={
          user ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <SignupPage />
          )
        }
      />

      {/* Protected */}

      <Route
        path="/dashboard"
        element={
          user ? (
            <MainLayout />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />

      {/* 404 */}

      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}