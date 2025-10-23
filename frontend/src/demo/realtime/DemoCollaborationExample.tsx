/**
 * Demo Collaboration Example Component
 * 
 * Demonstrates integration of real-time collaboration, AI help, and analytics
 * in a demo mode page.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Fab,
  AppBar,
  Toolbar,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  SmartToy as AIIcon,
  Analytics as AnalyticsIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';

// Import our new features
import { useDemoCollaboration } from './useDemoCollaboration';
import { ParticipantIndicator } from './ParticipantIndicator';
import { AIChatbot } from '../../ai/AIChatbot';
import { analyticsTracker } from '../../analytics/components/analyticsTracker';

interface DemoCollaborationExampleProps {
  demoSessionId: string;
  userId?: string;
  userName?: string;
}

export const DemoCollaborationExample: React.FC<DemoCollaborationExampleProps> = ({
  demoSessionId,
  userId = 'anonymous',
  userName = 'Guest',
}) => {
  const [aiChatOpen, setAiChatOpen] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');

  // Initialize real-time collaboration
  const {
    isConnected,
    participants,
    sendNavigation,
    sendInteraction,
    error,
  } = useDemoCollaboration({
    sessionId: demoSessionId,
    userId,
    userName,
    autoConnect: true,
    onNavigation: (data) => {
      console.log('User navigated:', data);
      // Show notification about other user's navigation
    },
    onInteraction: (data) => {
      console.log('User interacted:', data);
      // Show notification about other user's interaction
    },
  });

  // Initialize analytics
  useEffect(() => {
    analyticsTracker.initialize(userId);
    analyticsTracker.trackPageView('/demo/collaboration-example', 'demo', {
      demoSessionId,
      isCollaborative: true,
    });
  }, [userId, demoSessionId]);

  // Handle view changes
  const handleViewChange = (view: string) => {
    setCurrentView(view);
    
    // Track analytics
    analyticsTracker.trackNavigation(currentView, view, {
      demoMode: true,
      collaborative: true,
    });
    
    // Send to other participants
    if (isConnected) {
      sendNavigation(`/demo/${view}`, `Demo: ${view}`);
    }
  };

  // Handle button clicks
  const handleAction = (action: string) => {
    // Track analytics
    analyticsTracker.trackClick(action, `/demo/${currentView}`, {
      demoMode: true,
    });
    
    // Send to other participants
    if (isConnected) {
      sendInteraction('click', action, {
        view: currentView,
        timestamp: new Date().toISOString(),
      });
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header with participant indicators */}
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Demo Mode - Collaborative Session
          </Typography>
          
          {/* Show participants */}
          <ParticipantIndicator
            participants={participants}
            currentUserId={userId}
            variant="compact"
          />
          
          {/* Connection status */}
          <Box sx={{ ml: 2 }}>
            <Typography variant="caption">
              {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main content */}
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, flex: 1 }}>
        {/* Error display */}
        {error && (
          <Paper sx={{ p: 2, mb: 2, bgcolor: 'error.light' }}>
            <Typography color="error">
              Connection Error: {error.message}
            </Typography>
          </Paper>
        )}

        {/* Demo content */}
        <Grid container spacing={3}>
          {/* Navigation buttons */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Navigate Demo
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant={currentView === 'dashboard' ? 'contained' : 'outlined'}
                  onClick={() => handleViewChange('dashboard')}
                  aria-label="View dashboard"
                >
                  Dashboard
                </Button>
                <Button
                  variant={currentView === 'sales' ? 'contained' : 'outlined'}
                  onClick={() => handleViewChange('sales')}
                  aria-label="View sales"
                >
                  Sales
                </Button>
                <Button
                  variant={currentView === 'reports' ? 'contained' : 'outlined'}
                  onClick={() => handleViewChange('reports')}
                  aria-label="View reports"
                >
                  Reports
                </Button>
              </Box>
            </Paper>
          </Grid>

          {/* Sample actions */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sample Actions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleAction('create-order')}
                    aria-label="Create order"
                  >
                    Create Order
                  </Button>
                  <Button
                    variant="contained"
                    color="secondary"
                    onClick={() => handleAction('view-report')}
                    aria-label="View report"
                  >
                    View Report
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => handleAction('export-data')}
                    aria-label="Export data"
                  >
                    Export Data
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Session info */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Session Information
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Typography variant="body2">
                    <strong>Session ID:</strong> {demoSessionId}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Your Name:</strong> {userName}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Participants:</strong> {participants.length}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Status:</strong> {isConnected ? 'Connected' : 'Disconnected'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Current View:</strong> {currentView}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Feature showcase */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, bgcolor: 'background.paper' }}>
              <Typography variant="h5" gutterBottom>
                Features Demonstration
              </Typography>
              <Typography paragraph>
                This demo showcases the integration of multiple features:
              </Typography>
              <Box component="ul" sx={{ pl: 3 }}>
                <Typography component="li">
                  <strong>Real-Time Collaboration:</strong> See other participants and their actions in real-time
                </Typography>
                <Typography component="li">
                  <strong>AI Help:</strong> Click the chatbot icon to get contextual assistance
                </Typography>
                <Typography component="li">
                  <strong>Analytics:</strong> All interactions are tracked for UX optimization
                </Typography>
                <Typography component="li">
                  <strong>Accessibility:</strong> Full keyboard navigation and screen reader support
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Floating AI Help Button */}
      <Fab
        color="secondary"
        aria-label="Open AI help"
        onClick={() => {
          setAiChatOpen(true);
          analyticsTracker.trackClick('ai-help-fab', `/demo/${currentView}`);
        }}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
        }}
      >
        <AIIcon />
      </Fab>

      {/* AI Chatbot */}
      <AIChatbot
        open={aiChatOpen}
        onClose={() => {
          setAiChatOpen(false);
          analyticsTracker.trackCustomEvent('ai_chat_closed', `/demo/${currentView}`, {
            sessionDuration: Date.now(), // Would need actual duration
          });
        }}
        context={{
          page: currentView,
          module: 'demo',
          isDemoMode: true,
          isMobile: window.innerWidth < 768,
          previousActions: [currentView],
        }}
        position="bottom-right"
        variant="compact"
      />
    </Box>
  );
};

export default DemoCollaborationExample;
