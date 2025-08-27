// pages/analytics/service/sla-compliance.tsx
// SLA Compliance Analytics

import React from 'react';
import { NextPage } from 'next';
import {
  Box,
  Container,
  Typography,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import { Timeline } from '@mui/icons-material';
import { useAuth } from '../../../hooks/useAuth';
import { useQuery } from '@tanstack/react-query';
import SLAComplianceChart from '../../../components/ServiceAnalytics/SLAComplianceChart';
import { rbacService, SERVICE_PERMISSIONS } from '../../../services/rbacService';

const SLAComplianceAnalyticsPage: NextPage = () => {
  const { user } = useAuth();

  const { data: userPermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
    retry: false,
  });

  const hasPermission = userPermissions.includes(SERVICE_PERMISSIONS.SERVICE_REPORTS_READ);

  if (!user || !hasPermission) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">Access Denied: Service Reports Read permission required.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Timeline color="primary" />
          SLA Compliance Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor SLA compliance rates, track breaches, and analyze service level performance against defined targets.
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <SLAComplianceChart />
        </CardContent>
      </Card>
    </Container>
  );
};

export default SLAComplianceAnalyticsPage;