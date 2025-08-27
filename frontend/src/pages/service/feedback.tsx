// pages/service/feedback.tsx
// Feedback Workflow page

import React from 'react';
import { NextPage } from 'next';
import {
  Box,
  Container,
  Typography,
  Alert,
} from '@mui/material';
import { Feedback } from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { useQuery } from '@tanstack/react-query';
import FeedbackWorkflowIntegration from '../../components/FeedbackWorkflow/FeedbackWorkflowIntegration';
import { rbacService, SERVICE_PERMISSIONS } from '../../services/rbacService';

const FeedbackWorkflowPage: NextPage = () => {
  const { user } = useAuth();

  const { data: userPermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
    retry: false,
  });

  const hasCustomerServicePermission = userPermissions.includes(SERVICE_PERMISSIONS.CUSTOMER_SERVICE_READ);

  if (!user || !hasCustomerServicePermission) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to view feedback workflows. Contact your administrator to request customer service permissions.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Feedback color="primary" />
          Feedback Workflow
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage customer feedback collection, service closure workflows, and customer satisfaction tracking.
        </Typography>
      </Box>

      <FeedbackWorkflowIntegration />
    </Container>
  );
};

export default FeedbackWorkflowPage;