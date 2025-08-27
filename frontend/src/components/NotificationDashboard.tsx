// src/components/NotificationDashboard.tsx
// Main dashboard component for notification management

import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Tabs,
  Tab,
  Typography,
  AppBar
} from '@mui/material';
import {
  Dashboard,
  Create,
  Send,
  History,
  BarChart
} from '@mui/icons-material';
import NotificationTemplates from './NotificationTemplates';
import SendNotification from './SendNotification';
import NotificationLogs from './NotificationLogs';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`notification-tabpanel-${index}`}
      aria-labelledby={`notification-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const NotificationDashboard: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Notification Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage notification templates, send messages, and view delivery logs
        </Typography>
      </Box>

      <Paper sx={{ width: '100%' }}>
        <AppBar position="static" color="default" elevation={0}>
          <Tabs
            value={selectedTab}
            onChange={handleTabChange}
            variant="fullWidth"
            indicatorColor="primary"
            textColor="primary"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab
              label="Templates"
              icon={<Create />}
              iconPosition="start"
              sx={{ textTransform: 'none' }}
            />
            <Tab
              label="Send Notifications"
              icon={<Send />}
              iconPosition="start"
              sx={{ textTransform: 'none' }}
            />
            <Tab
              label="Logs & History"
              icon={<History />}
              iconPosition="start"
              sx={{ textTransform: 'none' }}
            />
          </Tabs>
        </AppBar>

        <TabPanel value={selectedTab} index={0}>
          <NotificationTemplates />
        </TabPanel>

        <TabPanel value={selectedTab} index={1}>
          <SendNotification />
        </TabPanel>

        <TabPanel value={selectedTab} index={2}>
          <NotificationLogs />
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default NotificationDashboard;