// src/pages/notification-demo.tsx
// Demo page to showcase notification components

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  Divider,
  Alert
} from '@mui/material';
import {
  Notifications,
  Settings,
  Send,
  Dashboard
} from '@mui/icons-material';
import NotificationBell from '../components/NotificationBell';
import NotificationSettingsModal from '../components/NotificationSettingsModal';
import AlertsFeed from '../components/AlertsFeed';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastContainer } from 'react-toastify';

// Create a query client for the demo
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: false,
    },
  },
});

const NotificationDemo: React.FC = () => {
  const [settingsOpen, setSettingsOpen] = useState(false);

  const handleOpenSettings = () => {
    setSettingsOpen(true);
  };

  const handleCloseSettings = () => {
    setSettingsOpen(false);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            🔔 Notification & Alerts System Demo
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Service CRM Vertical Slice Implementation
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            This demo showcases the complete notification system including real-time alerts, 
            user preferences, and workflow integration for the Service CRM platform.
          </Alert>
        </Box>

        <Grid container spacing={4}>
          {/* Notification Bell Demo */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Notifications sx={{ mr: 1 }} />
                  <Typography variant="h5" component="h2">
                    Notification Bell
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Real-time notification dropdown with unread count badge and quick actions.
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <NotificationBell onSettingsClick={handleOpenSettings} />
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Click the bell icon to view notifications. Badge shows unread count.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Settings Modal Demo */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Settings sx={{ mr: 1 }} />
                  <Typography variant="h5" component="h2">
                    Notification Settings
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Comprehensive user preference management for all notification types and channels.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Settings />}
                  onClick={handleOpenSettings}
                  fullWidth
                >
                  Open Settings Modal
                </Button>
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Configure notification preferences for email, SMS, push, and in-app alerts.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Alerts Feed Demo */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Dashboard sx={{ mr: 1 }} />
                  <Typography variant="h5" component="h2">
                    Alerts Feed
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Real-time alerts and notifications feed with filtering, bulk actions, and priority indicators.
                </Typography>
                <AlertsFeed 
                  showFilters={true}
                  maxHeight={400}
                  autoRefresh={true}
                  refreshInterval={30000}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Feature Overview */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🚀 Implemented Features
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Notifications color="primary" sx={{ fontSize: 40, mb: 1 }} />
                    <Typography variant="subtitle2" gutterBottom>
                      Multi-Channel Notifications
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Email, SMS, Push, In-App
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Settings color="primary" sx={{ fontSize: 40, mb: 1 }} />
                    <Typography variant="subtitle2" gutterBottom>
                      User Preferences
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Granular opt-in/out controls
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Send color="primary" sx={{ fontSize: 40, mb: 1 }} />
                    <Typography variant="subtitle2" gutterBottom>
                      Workflow Integration
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Automated triggers for CRM events
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <Dashboard color="primary" sx={{ fontSize: 40, mb: 1 }} />
                    <Typography variant="subtitle2" gutterBottom>
                      Real-Time Updates
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Live feed with auto-refresh
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Implementation Status */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                📋 Implementation Status
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="success.main" gutterBottom>
                    ✅ Completed Backend Features
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    <li>SQLAlchemy models (NotificationTemplate, NotificationLog, NotificationPreference)</li>
                    <li>FastAPI endpoints for CRUD operations</li>
                    <li>User preference management API</li>
                    <li>Multi-channel notification service</li>
                    <li>Email/SMS/Push gateway integration (mockable)</li>
                    <li>Automated trigger system</li>
                    <li>Unit tests and service validation</li>
                  </ul>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="success.main" gutterBottom>
                    ✅ Completed Frontend Features
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    <li>NotificationBell component with unread count</li>
                    <li>NotificationSettingsModal for preferences</li>
                    <li>AlertsFeed with filtering and bulk actions</li>
                    <li>Real-time updates via polling</li>
                    <li>Workflow integration utilities</li>
                    <li>TypeScript interfaces and services</li>
                    <li>Material-UI responsive design</li>
                  </ul>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>

        {/* Settings Modal */}
        <NotificationSettingsModal
          open={settingsOpen}
          onClose={handleCloseSettings}
          userId={1}
          userType="user"
        />

        {/* Toast Container for notifications */}
        <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </Container>
    </QueryClientProvider>
  );
};

export default NotificationDemo;