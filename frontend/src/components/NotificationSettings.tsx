import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import { Notifications as NotificationsIcon } from '@mui/icons-material';
import { usePushNotifications } from '../hooks/usePushNotifications';

const NotificationSettings: React.FC = () => {
  const {
    isSupported,
    permission,
    subscription,
    requestPermission,
    subscribe,
    unsubscribe,
    sendNotification,
  } = usePushNotifications();

  const [loading, setLoading] = React.useState(false);

  const handleEnableNotifications = async () => {
    setLoading(true);
    try {
      if (permission === 'default') {
        await requestPermission();
      }
      await subscribe();
    } finally {
      setLoading(false);
    }
  };

  const handleDisableNotifications = async () => {
    setLoading(true);
    try {
      await unsubscribe();
    } finally {
      setLoading(false);
    }
  };

  const handleTestNotification = () => {
    sendNotification('Test Notification', {
      body: 'This is a test notification from TRITIQ BOS',
      icon: '/icons/icon-192x192.png',
    });
  };

  if (!isSupported) {
    return (
      <Card>
        <CardContent>
          <Alert severity="info">
            Push notifications are not supported on this browser or device.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <NotificationsIcon sx={{ mr: 1 }} />
          <Typography variant="h6">Push Notifications</Typography>
        </Box>

        {permission === 'denied' && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Notifications are blocked. Please enable them in your browser settings.
          </Alert>
        )}

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Stay updated with real-time notifications for important events, updates, and reminders.
        </Typography>

        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={Boolean(subscription)}
                onChange={(e) => {
                  if (e.target.checked) {
                    handleEnableNotifications();
                  } else {
                    handleDisableNotifications();
                  }
                }}
                disabled={loading || permission === 'denied'}
              />
            }
            label={subscription ? 'Notifications Enabled' : 'Enable Notifications'}
          />
        </Box>

        {subscription && (
          <>
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle2" gutterBottom>
              Notification Preferences
            </Typography>

            <List dense>
              <ListItem>
                <ListItemText
                  primary="Order Updates"
                  secondary="Get notified about new orders and status changes"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>

              <ListItem>
                <ListItemText
                  primary="Inventory Alerts"
                  secondary="Low stock and reorder notifications"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>

              <ListItem>
                <ListItemText
                  primary="Task Reminders"
                  secondary="Upcoming tasks and deadlines"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>

              <ListItem>
                <ListItemText
                  primary="System Updates"
                  secondary="App updates and maintenance notifications"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>
            </List>

            <Divider sx={{ my: 2 }} />

            <Button
              variant="outlined"
              onClick={handleTestNotification}
              fullWidth
            >
              Send Test Notification
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default NotificationSettings;
