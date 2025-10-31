// frontend/src/components/AppLayout.tsx
'use client';
import React, { ReactElement, ReactNode } from 'react';
import { Box } from '@mui/material';
import MegaMenu from './MegaMenu';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/router';

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Skip layout for login and public pages
  const publicPaths = ['/login', '/register', '/forgot-password', '/reset-password'];
  const isPublicPath = publicPaths.some(path => router.pathname.startsWith(path));

  if (isPublicPath) {
    return <>{children}</>;
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <MegaMenu user={user} onLogout={handleLogout} isVisible={true} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          minHeight: 'calc(100vh - 64px)', // Account for AppBar height
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default AppLayout;

// HOC for pages that need the app layout
export function withAppLayout(page: ReactElement): ReactNode {
  return <AppLayout>{page}</AppLayout>;
}
