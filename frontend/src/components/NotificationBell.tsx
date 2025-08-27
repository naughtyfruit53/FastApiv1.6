// src/components/NotificationBell.tsx
// Notification bell icon component with unread count badge

import React, { useState, useEffect } from 'react';
import {
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Typography,
  Box,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Chip,
  Button,
  CircularProgress
} from '@mui/material';
import {
  Notifications,
  NotificationsNone,
  Email,
  Sms,
  NotificationImportant,
  Settings,
  MarkEmailRead,
  Clear
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import {
  getNotificationLogs,
  notificationQueryKeys,
  NotificationLog,
  getChannelDisplayName,
  getStatusDisplayName,
  getStatusColor
} from '../services/notificationService';

interface NotificationBellProps {
  onSettingsClick?: () => void;
}

const NotificationBell: React.FC<NotificationBellProps> = ({ onSettingsClick }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const queryClient = useQueryClient();

  // Fetch recent notifications
  const { data: notifications = [], isLoading, error } = useQuery({
    queryKey: notificationQueryKeys.logsFiltered({ 
      limit: 20, 
      status: undefined,
      recipient_type: 'user'  // For current user notifications
    }),
    queryFn: () => getNotificationLogs({ 
      limit: 20, 
      recipient_type: 'user'
    }),
    refetchInterval: 30000, // Poll every 30 seconds for real-time updates
  });

  // Calculate unread count (notifications that haven't been opened)
  useEffect(() => {
    if (notifications) {
      const unread = notifications.filter(notif => 
        !notif.opened_at && notif.status === 'delivered'
      ).length;
      setUnreadCount(unread);
    }
  }, [notifications]);

  // Mark notification as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      // TODO: Implement mark as read API endpoint
      console.log('Marking notification as read:', notificationId);
      return Promise.resolve();
    },
    onSuccess: () => {
      // Refresh notifications
      queryClient.invalidateQueries({ queryKey: notificationQueryKeys.logs() });
    },
    onError: (error) => {
      toast.error('Failed to mark notification as read');
    }
  });

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = (notification: NotificationLog) => {
    // Mark as read if not already read
    if (!notification.opened_at) {
      markAsReadMutation.mutate(notification.id);
    }
    
    // TODO: Navigate to relevant page based on notification type
    console.log('Clicked notification:', notification);
    handleClose();
  };

  const handleMarkAllRead = () => {
    // TODO: Implement mark all as read
    console.log('Mark all as read');
    handleClose();
  };

  const getNotificationIcon = (channel: string) => {
    switch (channel) {
      case 'email':
        return <Email fontSize="small" />;
      case 'sms':
        return <Sms fontSize="small" />;
      case 'push':
      case 'in_app':
        return <NotificationImportant fontSize="small" />;
      default:
        return <Notifications fontSize="small" />;
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

  const isOpen = Boolean(anchorEl);

  return (
    <>
      <IconButton
        color="inherit"
        onClick={handleClick}
        aria-label="notifications"
        aria-describedby={isOpen ? 'notification-menu' : undefined}
        aria-haspopup="true"
        aria-expanded={isOpen ? 'true' : undefined}
      >
        <Badge badgeContent={unreadCount} color="error" max={99}>
          {unreadCount > 0 ? <Notifications /> : <NotificationsNone />}
        </Badge>
      </IconButton>

      <Menu
        id="notification-menu"
        anchorEl={anchorEl}
        open={isOpen}
        onClose={handleClose}
        PaperProps={{
          style: {
            maxHeight: 400,
            width: 360,
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" component="div">
              Notifications
            </Typography>
            <Box>
              {onSettingsClick && (
                <IconButton size="small" onClick={onSettingsClick} aria-label="notification settings">
                  <Settings />
                </IconButton>
              )}
              {unreadCount > 0 && (
                <IconButton size="small" onClick={handleMarkAllRead} aria-label="mark all as read">
                  <MarkEmailRead />
                </IconButton>
              )}
            </Box>
          </Box>
          {unreadCount > 0 && (
            <Typography variant="body2" color="text.secondary">
              {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
            </Typography>
          )}
        </Box>

        <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress size={24} />
            </Box>
          ) : error ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="error">
                Failed to load notifications
              </Typography>
            </Box>
          ) : notifications.length === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No notifications
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {notifications.map((notification, index) => (
                <React.Fragment key={notification.id}>
                  <ListItem
                    button
                    onClick={() => handleNotificationClick(notification)}
                    sx={{
                      backgroundColor: notification.opened_at ? 'transparent' : 'action.hover',
                      '&:hover': {
                        backgroundColor: 'action.selected',
                      },
                    }}
                  >
                    <ListItemIcon>
                      <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                        {getNotificationIcon(notification.channel)}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <Typography
                            variant="body2"
                            sx={{
                              fontWeight: notification.opened_at ? 'normal' : 'bold',
                              flex: 1,
                              mr: 1
                            }}
                          >
                            {notification.subject || 'Notification'}
                          </Typography>
                          <Chip
                            label={getChannelDisplayName(notification.channel as any)}
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: '0.7rem', height: 20 }}
                          />
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
                            {notification.content}
                          </Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="caption" color="text.secondary">
                              {formatTimeAgo(notification.created_at)}
                            </Typography>
                            <Chip
                              label={getStatusDisplayName(notification.status as any)}
                              size="small"
                              sx={{
                                fontSize: '0.6rem',
                                height: 16,
                                ...getStatusColor(notification.status as any).split(' ').reduce((acc, cls) => {
                                  if (cls.startsWith('text-')) {
                                    acc.color = cls.replace('text-', '');
                                  } else if (cls.startsWith('bg-')) {
                                    acc.backgroundColor = cls.replace('bg-', '');
                                  }
                                  return acc;
                                }, {} as any)
                              }}
                            />
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < notifications.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Box>

        <Divider />
        <Box sx={{ p: 1 }}>
          <Button
            fullWidth
            variant="text"
            onClick={() => {
              // TODO: Navigate to notifications page
              console.log('View all notifications');
              handleClose();
            }}
          >
            View All Notifications
          </Button>
        </Box>
      </Menu>
    </>
  );
};

export default NotificationBell;