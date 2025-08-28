// pages/admin/audit-logs.tsx
// Company Audit Logs page

import React from 'react';
import { NextPage } from 'next';
import {
  Box,
  Container,
  Typography,
  Alert,
  Card,
  CardContent,
  Grid,
  Paper,
} from '@mui/material';
import { History, Security, Person, Business } from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { isOrgSuperAdmin, canManageUsers } from '../../types/user.types';

const AuditLogsPage: NextPage = () => {
  const { user } = useAuth();

  const canViewAuditLogs = isOrgSuperAdmin(user) || canManageUsers(user);

  if (!user || !canViewAuditLogs) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          Access Denied: You don&apos;t have permission to view audit logs. Only organization super admins can access audit trails.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <History color="primary" />
          Company Audit Logs
        </Typography>
        <Typography variant="body1" color="text.secondary">
          View and monitor all system activities, user actions, and security events for your organization.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Person color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">User Activities</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Login, logout, and user actions
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Security color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Security Events</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Permission changes and security alerts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Business color="primary" fontSize="large" />
                <Box>
                  <Typography variant="h6">Business Operations</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Data changes and business activities
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Main Content */}
        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Audit Trail
            </Typography>
            <Alert severity="info">
              This is a placeholder for the Company Audit Logs interface. The actual implementation would display:
              <ul style={{ marginTop: '8px', marginBottom: 0 }}>
                <li>Searchable audit trail with timestamps and user information</li>
                <li>Filterable events by type, user, date range, and severity</li>
                <li>Detailed event logs with before/after values for data changes</li>
                <li>Export functionality for compliance and reporting</li>
                <li>Real-time monitoring of critical security events</li>
                <li>Integration with backend audit logging system</li>
              </ul>
            </Alert>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default AuditLogsPage;