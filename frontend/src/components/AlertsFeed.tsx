// src/components/AlertsFeed.tsx
// Real-time alerts and notifications feed component

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Chip,
  IconButton,
  Button,
  Divider,
  Alert,
  CircularProgress,
  TextField,
  MenuItem,
  Grid,
  Badge,
  Tooltip,
  Collapse
} from '@mui/material';
import {
  Notifications,
  Warning,
  Error,
  Info,
  CheckCircle,
  AccessTime,
  Person,
  Work,
  Feedback,
  Assignment,
  Update,
  FilterList,
  Refresh,
  ExpandMore,
  ExpandLess,
  MarkEmailRead,
  Delete,
  Visibility
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import {
  getNotificationLogs,
  notificationQueryKeys,
  NotificationLog,
  getChannelDisplayName,
  getStatusDisplayName,
  getStatusColor,
  NOTIFICATION_STATUSES
} from '../services/notificationService';

interface AlertsFeedProps {
  userId?: number;
  showFilters?: boolean;
  maxHeight?: string | number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface AlertFilters {
  status: string;
  channel: string;
  type: string;
  timeRange: string;
}

const AlertsFeed: React.FC<AlertsFeedProps> = ({
  userId,
  showFilters = true,
  maxHeight = 600,
  autoRefresh = true,
  refreshInterval = 30000
}) => {
  const [filters, setFilters] = useState<AlertFilters>({
    status: 'all',
    channel: 'all',
    type: 'all',
    timeRange: 'all'
  });
  const [showFiltersPanel, setShowFiltersPanel] = useState(false);
  const [selectedAlerts, setSelectedAlerts] = useState<Set<number>>(new Set());
  const queryClient = useQueryClient();

  // Build query parameters from filters
  const getQueryParams = () => {
    const params: any = {
      limit: 50,
      recipient_type: 'user'
    };

    if (filters.status !== 'all') {
      params.status = filters.status;
    }
    if (filters.channel !== 'all') {
      params.channel = filters.channel;
    }

    return params;
  };

  // Fetch alerts/notifications
  const { data: alerts = [], isLoading, error, refetch } = useQuery({
    queryKey: notificationQueryKeys.logsFiltered(getQueryParams()),
    queryFn: () => getNotificationLogs(getQueryParams()),
    refetchInterval: autoRefresh ? refreshInterval : false,
  });

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: async (alertIds: number[]) => {
      // TODO: Implement mark as read API
      console.log('Marking alerts as read:', alertIds);
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationQueryKeys.logs() });
      setSelectedAlerts(new Set());
      toast.success('Alerts marked as read');
    },
    onError: () => {
      toast.error('Failed to mark alerts as read');
    }
  });

  // Delete alerts mutation
  const deleteAlertsMutation = useMutation({
    mutationFn: async (alertIds: number[]) => {
      // TODO: Implement delete alerts API
      console.log('Deleting alerts:', alertIds);
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationQueryKeys.logs() });
      setSelectedAlerts(new Set());
      toast.success('Alerts deleted');
    },
    onError: () => {
      toast.error('Failed to delete alerts');
    }
  });

  const handleFilterChange = (filterType: keyof AlertFilters, value: string) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleSelectAlert = (alertId: number) => {
    setSelectedAlerts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(alertId)) {
        newSet.delete(alertId);
      } else {
        newSet.add(alertId);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedAlerts.size === alerts.length) {
      setSelectedAlerts(new Set());
    } else {
      setSelectedAlerts(new Set(alerts.map(alert => alert.id)));
    }
  };

  const handleMarkSelectedAsRead = () => {
    if (selectedAlerts.size > 0) {
      markAsReadMutation.mutate(Array.from(selectedAlerts));
    }
  };

  const handleDeleteSelected = () => {
    if (selectedAlerts.size > 0) {
      deleteAlertsMutation.mutate(Array.from(selectedAlerts));
    }
  };

  const getAlertIcon = (alert: NotificationLog) => {
    const triggerEvent = alert.trigger_event;
    
    switch (triggerEvent) {
      case 'sla_breach':
        return <Warning color="error" />;
      case 'job_assignment':
        return <Assignment color="primary" />;
      case 'job_update':
        return <Update color="info" />;
      case 'job_completion':
        return <CheckCircle color="success" />;
      case 'feedback_request':
        return <Feedback color="primary" />;
      default:
        switch (alert.status) {
          case 'failed':
            return <Error color="error" />;
          case 'delivered':
            return <CheckCircle color="success" />;
          default:
            return <Info color="primary" />;
        }
    }
  };

  const getAlertPriority = (alert: NotificationLog) => {
    const triggerEvent = alert.trigger_event;
    
    switch (triggerEvent) {
      case 'sla_breach':
        return 'high';
      case 'job_assignment':
      case 'feedback_request':
        return 'medium';
      default:
        return 'low';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return date.toLocaleDateString();
  };

  const unreadCount = alerts.filter(alert => !alert.opened_at).length;

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h6" component="div">
              Alerts & Notifications
            </Typography>
            {unreadCount > 0 && (
              <Badge badgeContent={unreadCount} color="error">
                <Notifications />
              </Badge>
            )}
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {showFilters && (
              <IconButton
                onClick={() => setShowFiltersPanel(!showFiltersPanel)}
                color={showFiltersPanel ? 'primary' : 'default'}
              >
                <FilterList />
              </IconButton>
            )}
            <IconButton onClick={() => refetch()} disabled={isLoading}>
              <Refresh />
            </IconButton>
          </Box>
        </Box>

        {selectedAlerts.size > 0 && (
          <Box sx={{ mb: 2, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2">
                {selectedAlerts.size} alert{selectedAlerts.size !== 1 ? 's' : ''} selected
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  size="small"
                  startIcon={<MarkEmailRead />}
                  onClick={handleMarkSelectedAsRead}
                  disabled={markAsReadMutation.isPending}
                >
                  Mark as Read
                </Button>
                <Button
                  size="small"
                  startIcon={<Delete />}
                  onClick={handleDeleteSelected}
                  disabled={deleteAlertsMutation.isPending}
                  color="error"
                >
                  Delete
                </Button>
              </Box>
            </Box>
          </Box>
        )}

        <Collapse in={showFiltersPanel}>
          <Box sx={{ mb: 2, p: 2, bgcolor: 'background.paper', border: 1, borderColor: 'divider', borderRadius: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={3}>
                <TextField
                  select
                  fullWidth
                  label="Status"
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  size="small"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  {NOTIFICATION_STATUSES.map(status => (
                    <MenuItem key={status} value={status}>
                      {getStatusDisplayName(status)}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  select
                  fullWidth
                  label="Channel"
                  value={filters.channel}
                  onChange={(e) => handleFilterChange('channel', e.target.value)}
                  size="small"
                >
                  <MenuItem value="all">All Channels</MenuItem>
                  <MenuItem value="email">Email</MenuItem>
                  <MenuItem value="sms">SMS</MenuItem>
                  <MenuItem value="push">Push</MenuItem>
                  <MenuItem value="in_app">In-App</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  select
                  fullWidth
                  label="Type"
                  value={filters.type}
                  onChange={(e) => handleFilterChange('type', e.target.value)}
                  size="small"
                >
                  <MenuItem value="all">All Types</MenuItem>
                  <MenuItem value="job_assignment">Job Assignment</MenuItem>
                  <MenuItem value="job_update">Job Update</MenuItem>
                  <MenuItem value="sla_breach">SLA Breach</MenuItem>
                  <MenuItem value="feedback_request">Feedback Request</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  select
                  fullWidth
                  label="Time Range"
                  value={filters.timeRange}
                  onChange={(e) => handleFilterChange('timeRange', e.target.value)}
                  size="small"
                >
                  <MenuItem value="all">All Time</MenuItem>
                  <MenuItem value="today">Today</MenuItem>
                  <MenuItem value="week">This Week</MenuItem>
                  <MenuItem value="month">This Month</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </Box>
        </Collapse>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">
            Failed to load alerts. Please try again.
          </Alert>
        ) : alerts.length === 0 ? (
          <Box sx={{ textAlign: 'center', p: 4 }}>
            <Notifications sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No alerts found
            </Typography>
            <Typography variant="body2" color="text.disabled">
              You're all caught up! No new notifications.
            </Typography>
          </Box>
        ) : (
          <Box sx={{ maxHeight, overflow: 'auto' }}>
            <List sx={{ p: 0 }}>
              {alerts.map((alert, index) => {
                const priority = getAlertPriority(alert);
                const isSelected = selectedAlerts.has(alert.id);
                const isUnread = !alert.opened_at;

                return (
                  <React.Fragment key={alert.id}>
                    <ListItem
                      sx={{
                        backgroundColor: isSelected ? 'action.selected' : isUnread ? 'action.hover' : 'transparent',
                        cursor: 'pointer',
                        '&:hover': {
                          backgroundColor: 'action.focus',
                        },
                        borderLeft: 4,
                        borderLeftColor: priority === 'high' ? 'error.main' : priority === 'medium' ? 'warning.main' : 'transparent'
                      }}
                      onClick={() => handleSelectAlert(alert.id)}
                    >
                      <ListItemIcon>
                        <Avatar
                          sx={{
                            width: 40,
                            height: 40,
                            bgcolor: getPriorityColor(priority) === 'error' ? 'error.main' : 
                                   getPriorityColor(priority) === 'warning' ? 'warning.main' : 'primary.main'
                          }}
                        >
                          {getAlertIcon(alert)}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <Typography
                              variant="subtitle2"
                              sx={{
                                fontWeight: isUnread ? 'bold' : 'normal',
                                flex: 1,
                                mr: 1
                              }}
                            >
                              {alert.subject || `${alert.trigger_event?.replace('_', ' ').toUpperCase()} Notification`}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                              <Chip
                                label={getChannelDisplayName(alert.channel as any)}
                                size="small"
                                variant="outlined"
                                sx={{ fontSize: '0.7rem', height: 20 }}
                              />
                              <Chip
                                label={priority.toUpperCase()}
                                size="small"
                                color={getPriorityColor(priority) as any}
                                sx={{ fontSize: '0.7rem', height: 20 }}
                              />
                            </Box>
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                                mb: 0.5
                              }}
                            >
                              {alert.content}
                            </Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <AccessTime sx={{ fontSize: 14 }} />
                                <Typography variant="caption" color="text.secondary">
                                  {formatTimeAgo(alert.created_at)}
                                </Typography>
                              </Box>
                              <Chip
                                label={getStatusDisplayName(alert.status as any)}
                                size="small"
                                sx={{
                                  fontSize: '0.6rem',
                                  height: 16,
                                }}
                                color={alert.status === 'delivered' ? 'success' : alert.status === 'failed' ? 'error' : 'default'}
                              />
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < alerts.length - 1 && <Divider />}
                  </React.Fragment>
                );
              })}
            </List>
          </Box>
        )}

        {alerts.length > 0 && (
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Button
              variant="outlined"
              size="small"
              onClick={handleSelectAll}
            >
              {selectedAlerts.size === alerts.length ? 'Deselect All' : 'Select All'}
            </Button>
            <Typography variant="caption" color="text.secondary">
              Showing {alerts.length} alerts
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default AlertsFeed;