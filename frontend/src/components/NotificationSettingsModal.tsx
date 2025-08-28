// src/components/NotificationSettingsModal.tsx
// Modal for managing user notification preferences

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Switch,
  FormControlLabel,
  Card,
  CardContent,
  Grid,
  Divider,
  Alert,
  CircularProgress,
  Chip,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Close,
  Email,
  Sms,
  NotificationImportant,
  Notifications,
  ExpandMore,
  Save,
  RestoreDefaultsNone as Restore
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import {
  getNotificationTemplates,
  createNotificationTemplate,
  updateNotificationTemplate,
  notificationQueryKeys,
  NotificationTemplate,
  NOTIFICATION_CHANNELS,
  TEMPLATE_TYPES,
  getChannelDisplayName,
  getTemplateTypeDisplayName
} from '../services/notificationService';

interface NotificationSettingsModalProps {
  open: boolean;
  onClose: () => void;
  userId: number;
  userType?: 'user' | 'customer';
}

interface PreferenceState {
  [key: string]: {
    [channel: string]: boolean;
  };
}

const NotificationSettingsModal: React.FC<NotificationSettingsModalProps> = ({
  open,
  onClose,
  userId,
  userType = 'user'
}) => {
  const [preferences, setPreferences] = useState<PreferenceState>({});
  const [hasChanges, setHasChanges] = useState(false);
  const queryClient = useQueryClient();

  // Available notification types
  const notificationTypes = [
    { key: 'job_assignment', label: 'Job Assignment', description: 'When a new job is assigned to you' },
    { key: 'job_update', label: 'Job Updates', description: 'When job status or details change' },
    { key: 'job_completion', label: 'Job Completion', description: 'When a job is completed' },
    { key: 'feedback_request', label: 'Feedback Requests', description: 'When feedback is requested' },
    { key: 'sla_breach', label: 'SLA Breach Alerts', description: 'When SLA deadlines are at risk' },
    { key: 'appointment_reminder', label: 'Appointment Reminders', description: 'Reminders for upcoming appointments' },
    { key: 'service_completion', label: 'Service Completion', description: 'When service work is completed' },
    { key: 'follow_up', label: 'Follow-up Messages', description: 'Follow-up communications' },
    { key: 'marketing', label: 'Marketing Messages', description: 'Promotional and marketing content' },
    { key: 'system', label: 'System Notifications', description: 'Important system updates and alerts' }
  ];

  // Fetch current preferences
  const { data: currentPreferences = [], isLoading } = useQuery({
    queryKey: ['notification-preferences', userType, userId],
    queryFn: async () => {
      // TODO: Implement API call to get user preferences
      // For now, return mock data
      return [
        { notification_type: 'job_assignment', channel: 'email', is_enabled: true },
        { notification_type: 'job_assignment', channel: 'in_app', is_enabled: true },
        { notification_type: 'sla_breach', channel: 'email', is_enabled: true },
        { notification_type: 'sla_breach', channel: 'sms', is_enabled: true },
        { notification_type: 'marketing', channel: 'email', is_enabled: false },
      ];
    },
    enabled: open,
  });

  // Initialize preferences state from API data
  useEffect(() => {
    if (currentPreferences.length > 0) {
      const prefState: PreferenceState = {};
      
      notificationTypes.forEach(type => {
        prefState[type.key] = {};
        NOTIFICATION_CHANNELS.forEach(channel => {
          const existing = currentPreferences.find(
            p => p.notification_type === type.key && p.channel === channel
          );
          // Default to enabled for important notifications, disabled for marketing
          const defaultEnabled = !['marketing'].includes(type.key);
          prefState[type.key][channel] = existing ? existing.is_enabled : defaultEnabled;
        });
      });
      
      setPreferences(prefState);
    }
  }, [currentPreferences]);

  // Save preferences mutation
  const savePreferencesMutation = useMutation({
    mutationFn: async (prefs: PreferenceState) => {
      // TODO: Implement API call to save preferences
      console.log('Saving preferences:', prefs);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return { success: true };
    },
    onSuccess: () => {
      toast.success('Notification preferences saved successfully');
      setHasChanges(false);
      queryClient.invalidateQueries({ queryKey: ['notification-preferences'] });
    },
    onError: (error) => {
      toast.error('Failed to save notification preferences');
    }
  });

  const handlePreferenceChange = (notificationType: string, channel: string, enabled: boolean) => {
    setPreferences(prev => ({
      ...prev,
      [notificationType]: {
        ...prev[notificationType],
        [channel]: enabled
      }
    }));
    setHasChanges(true);
  };

  const handleSelectAll = (notificationType: string, enabled: boolean) => {
    setPreferences(prev => ({
      ...prev,
      [notificationType]: NOTIFICATION_CHANNELS.reduce((acc, channel) => ({
        ...acc,
        [channel]: enabled
      }), {})
    }));
    setHasChanges(true);
  };

  const handleSave = () => {
    savePreferencesMutation.mutate(preferences);
  };

  const handleReset = () => {
    // Reset to defaults
    const defaultPrefs: PreferenceState = {};
    notificationTypes.forEach(type => {
      defaultPrefs[type.key] = {};
      NOTIFICATION_CHANNELS.forEach(channel => {
        defaultPrefs[type.key][channel] = !['marketing'].includes(type.key);
      });
    });
    setPreferences(defaultPrefs);
    setHasChanges(true);
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'email':
        return <Email sx={{ fontSize: 16 }} />;
      case 'sms':
        return <Sms sx={{ fontSize: 16 }} />;
      case 'push':
        return <NotificationImportant sx={{ fontSize: 16 }} />;
      case 'in_app':
        return <Notifications sx={{ fontSize: 16 }} />;
      default:
        return null;
    }
  };

  const getEnabledChannelsCount = (notificationType: string) => {
    if (!preferences[notificationType]) return 0;
    return Object.values(preferences[notificationType]).filter(Boolean).length;
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { height: '80vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Notification Settings</Typography>
          <IconButton onClick={onClose} aria-label="close">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Alert severity="info" sx={{ mb: 3 }}>
          Choose how you want to be notified about different types of events. You can enable or disable 
          notifications for each channel (email, SMS, push, in-app).
        </Alert>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            {notificationTypes.map((type) => (
              <Accordion key={type.key} defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', mr: 2 }}>
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                        {type.label}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {type.description}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip
                        label={`${getEnabledChannelsCount(type.key)}/${NOTIFICATION_CHANNELS.length} enabled`}
                        size="small"
                        color={getEnabledChannelsCount(type.key) > 0 ? 'primary' : 'default'}
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ pl: 2 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleSelectAll(type.key, true)}
                          >
                            Enable All
                          </Button>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleSelectAll(type.key, false)}
                          >
                            Disable All
                          </Button>
                        </Box>
                      </Grid>
                      {NOTIFICATION_CHANNELS.map((channel) => (
                        <Grid item xs={6} sm={3} key={channel}>
                          <Card variant="outlined" sx={{ p: 1 }}>
                            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
                              {getChannelIcon(channel)}
                              <Typography variant="body2" align="center">
                                {getChannelDisplayName(channel)}
                              </Typography>
                              <FormControlLabel
                                control={
                                  <Switch
                                    checked={preferences[type.key]?.[channel] || false}
                                    onChange={(e) => handlePreferenceChange(type.key, channel, e.target.checked)}
                                    size="small"
                                  />
                                }
                                label=""
                                sx={{ m: 0 }}
                              />
                            </Box>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3, gap: 1 }}>
        <Button
          onClick={handleReset}
          startIcon={<Restore />}
          variant="outlined"
        >
          Reset to Defaults
        </Button>
        <Box sx={{ flex: 1 }} />
        <Button onClick={onClose} variant="outlined">
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          startIcon={<Save />}
          disabled={!hasChanges || savePreferencesMutation.isPending}
        >
          {savePreferencesMutation.isPending ? 'Saving...' : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default NotificationSettingsModal;