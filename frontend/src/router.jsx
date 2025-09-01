import { createBrowserRouter, Navigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { useAuth } from '@/contexts/AuthContext';

// Auth Pages
import Login from '@/pages/auth/Login';
import Register from '@/pages/auth/Register';
import ForgotPassword from '@/pages/auth/ForgotPassword';
import ResetPassword from '@/pages/auth/ResetPassword';

// App Pages
import Dashboard from '@/pages/Dashboard';
import Documents from '@/pages/Documents';
import DocumentDetail from '@/pages/DocumentDetail';
import Team from '@/pages/Team';
import Billing from '@/pages/Billing';
import Settings from '@/pages/Settings';
import Profile from '@/pages/Profile';
import Help from '@/pages/Help';
import NotFound from '@/pages/NotFound';
import NewOrganization from '@/pages/NewOrganization';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Public Route Component (redirects to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Router Configuration
export const createRouter = () => {
  return createBrowserRouter([
    {
      path: '/',
      element: <MainLayout />,
      children: [
        {
          index: true,
          element: <Navigate to="/dashboard" replace />,
        },
        {
          path: 'dashboard',
          element: <ProtectedRoute><Dashboard /></ProtectedRoute>,
        },
        {
          path: 'documents',
          element: <ProtectedRoute><Documents /></ProtectedRoute>,
        },
        {
          path: 'documents/:id',
          element: <ProtectedRoute><DocumentDetail /></ProtectedRoute>,
        },
        {
          path: 'team',
          element: <ProtectedRoute><Team /></ProtectedRoute>,
        },
        {
          path: 'billing',
          element: <ProtectedRoute><Billing /></ProtectedRoute>,
        },
        {
          path: 'settings',
          element: <ProtectedRoute><Settings /></ProtectedRoute>,
        },
        {
          path: 'profile',
          element: <ProtectedRoute><Profile /></ProtectedRoute>,
        },
        {
          path: 'help',
          element: <ProtectedRoute><Help /></ProtectedRoute>,
        },
        {
          path: 'organizations/new',
          element: <ProtectedRoute><NewOrganization /></ProtectedRoute>,
        },
        {
          path: 'login',
          element: <PublicRoute><AuthLayout><Login /></AuthLayout></PublicRoute>,
        },
        {
          path: 'register',
          element: <PublicRoute><AuthLayout><Register /></AuthLayout></PublicRoute>,
        },
        {
          path: 'forgot-password',
          element: <PublicRoute><AuthLayout><ForgotPassword /></AuthLayout></PublicRoute>,
        },
        {
          path: 'reset-password',
          element: <PublicRoute><AuthLayout><ResetPassword /></AuthLayout></PublicRoute>,
        },
        {
          path: '*',
          element: <NotFound />,
        },
      ],
    },
  ]);
};

