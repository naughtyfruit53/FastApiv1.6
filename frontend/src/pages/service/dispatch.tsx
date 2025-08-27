// pages/service/dispatch.tsx
// Dispatch Management page

import React from 'react';
import { NextPage } from 'next';
import {
  Box,
  Container,
  Typography,
  Alert,
} from '@mui/material';
import { LocalShipping } from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { useQuery } from '@tanstack/react-query';
import DispatchManagement from '../../components/DispatchManagement/DispatchManagement';
import { rbacService, SERVICE_PERMISSIONS } from '../../services/rbacService';

const DispatchManagementPage: NextPage = () => {
  const { user } = useAuth();

  const { data: userPermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
    retry: false,
  });

  const hasWorkOrderPermission = userPermissions.includes(SERVICE_PERMISSIONS.WORK_ORDER_READ);

  if (!user || !hasWorkOrderPermission) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to view dispatch management. Contact your administrator to request work order permissions.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <LocalShipping color="primary" />
          Dispatch Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage service dispatch orders, installation job scheduling, and technician assignments.
        </Typography>
      </Box>

      <DispatchManagement />
    </Container>
  );
};

export default DispatchManagementPage;