// pages/service/dashboard.tsx
// Service CRM Dashboard

import React from 'react';
import { NextPage } from 'next';
import {
  Box,
  Container,
  Typography,
  Alert,
  Grid,
  Card,
  CardContent,
  Paper,
} from '@mui/material';
import { Dashboard, SupportAgent, Assignment, Schedule, People } from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { useQuery } from '@tanstack/react-query';
import { rbacService, SERVICE_PERMISSIONS } from '../../services/rbacService';

const ServiceDashboardPage: NextPage = () => {
  const { user } = useAuth();

  const { data: userPermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
    retry: false,
  });

  const hasServiceReadPermission = userPermissions.includes(SERVICE_PERMISSIONS.SERVICE_READ);

  if (!user || !hasServiceReadPermission) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to view the service dashboard. Contact your administrator to request service access permissions.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Dashboard color="primary" />
          Service CRM Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Overview of your service operations, performance metrics, and key indicators.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Quick Stats */}
        <Grid size={{ xs: 12, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Assignment color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Active Jobs</Typography>
                  <Typography variant="h4" color="primary">-</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Currently in progress
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Schedule color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Today&apos;s Schedule</Typography>
                  <Typography variant="h4" color="primary">-</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Appointments scheduled
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <People color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Available Technicians</Typography>
                  <Typography variant="h4" color="primary">-</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Ready for assignment
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <SupportAgent color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">SLA Compliance</Typography>
                  <Typography variant="h4" color="primary">-</Typography>
                  <Typography variant="body2" color="text.secondary">
                    This month
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Dashboard Content */}
        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Service Dashboard
            </Typography>
            <Alert severity="info">
              This is a placeholder for the Service CRM Dashboard. The actual dashboard would display:
              <ul style={{ marginTop: '8px', marginBottom: 0 }}>
                <li>Real-time service metrics and KPIs</li>
                <li>Job status overview and recent activity</li>
                <li>Technician availability and performance</li>
                <li>SLA compliance tracking</li>
                <li>Customer satisfaction trends</li>
                <li>Upcoming appointments and schedules</li>
              </ul>
            </Alert>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ServiceDashboardPage;