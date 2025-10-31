// frontend/src/components/AppLayout.tsx
'use client';
import React from 'react';
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
