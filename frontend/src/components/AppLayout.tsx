// frontend/src/components/AppLayout.tsx
import React from 'react';
import { useRouter } from 'next/router';
import { Box } from '@mui/material';
import MegaMenu from './MegaMenu';
import LogoBadge from './LogoBadge';
import { useAuth } from '../context/AuthContext';
interface AppLayoutProps {
  children: React.ReactNode;
}
/**
 * Global app layout that conditionally renders MegaMenu for authenticated users
 * on all pages except login and other public routes
 */
const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const { user, logout, loading, permissionsLoading } = useAuth();
  const router = useRouter();
  // Public routes that should not show the MegaMenu
  const publicRoutes = ['/login', '/register', '/forgot-password', '/reset-password'];
  const isPublicRoute = publicRoutes.includes(router.pathname);
  // Don't show MegaMenu on public routes or while auth is loading
  const shouldShowMenu = !isPublicRoute && !loading && !permissionsLoading && !!user;
  return (
    <>
      {shouldShowMenu && (
        <MegaMenu
          user={user}
          onLogout={logout}
          isVisible={true}
        />
      )}
      <Box
        sx={{
          minHeight: '100vh',
        }}
      >
        {children}
      </Box>
      {/* Global logo badge - hidden on print/PDF, shown on all authenticated pages */}
      {shouldShowMenu && <LogoBadge />}
    </>
  );
};
export default AppLayout;