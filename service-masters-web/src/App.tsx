import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import AppShell from '@/components/AppShell';
import LoginPage from '@/features/auth/LoginPage';
import OrdersPage from '@/features/orders/OrdersPage';
import OrderDetailsPage from '@/features/orders/OrderDetailsPage';
import UploadPhotosPage from '@/features/orders/UploadPhotosPage';
import ReportPage from '@/features/orders/ReportPage';
import SchedulePage from '@/features/schedule/SchedulePage';
import EarningsPage from '@/features/earnings/EarningsPage';
import ProfilePage from '@/features/profile/ProfilePage';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const loading = useAuthStore((s) => s.loading);

  if (loading) {
    return (
      <div className="min-h-full flex items-center justify-center text-on-surface-variant">
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  const fetchMe = useAuthStore((s) => s.fetchMe);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    if (localStorage.getItem('access_token')) {
      fetchMe();
    } else {
      useAuthStore.setState({ loading: false });
    }
  }, [fetchMe]);

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/orders" replace /> : <LoginPage />}
      />

      <Route
        element={
          <PrivateRoute>
            <AppShell />
          </PrivateRoute>
        }
      >
        <Route path="/orders" element={<OrdersPage />} />
        <Route path="/schedule" element={<SchedulePage />} />
        <Route path="/earnings" element={<EarningsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>

      <Route
        path="/orders/:id"
        element={
          <PrivateRoute>
            <OrderDetailsPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/orders/:id/photos"
        element={
          <PrivateRoute>
            <UploadPhotosPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/orders/:id/report"
        element={
          <PrivateRoute>
            <ReportPage />
          </PrivateRoute>
        }
      />

      <Route path="*" element={<Navigate to="/orders" replace />} />
    </Routes>
  );
}
