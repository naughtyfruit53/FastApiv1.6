// src/components/NotificationLogs.tsx
// Component for viewing notification history and logs

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Grid,
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Visibility,
  Email,
  Sms,
  NotificationImportant,
  Notifications,
  Person,
  Group,
  Refresh,
  FilterList,
  TrendingUp,
  Schedule,
  CheckCircle,
  Error as ErrorIcon,
  Warning
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import {
  getNotificationLogs,
  getNotificationLog,
  getNotificationAnalytics,
  NotificationLog,
  NOTIFICATION_CHANNELS,
  NOTIFICATION_STATUSES,
  getChannelDisplayName,
  getStatusDisplayName,
  getStatusColor,
  notificationQueryKeys
} from '../services/notificationService';
import { format } from 'date-fns';

const NotificationLogs: React.FC = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [selectedLog, setSelectedLog] = useState<NotificationLog | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  
  // Filter state
  const [filters, setFilters] = useState({
    recipient_type: '',
    status: '',
    channel: '',
    search: ''
  });

  // Analytics state
  const [analyticsDays, setAnalyticsDays] = useState(30);

  // Get notification logs
  const { 
    data: logs = [], 
    isLoading: logsLoading,
    error: logsError,
    refetch: refetchLogs
  } = useQuery({
    queryKey: notificationQueryKeys.logsFiltered({
      ...filters,
      limit: rowsPerPage,
      offset: page * rowsPerPage
    }),
    queryFn: () => getNotificationLogs({
      recipient_type: filters.recipient_type || undefined,
      status: filters.status as any || undefined,
      channel: filters.channel as any || undefined,
      limit: rowsPerPage,
      offset: page * rowsPerPage
    }),
  });

  // Get analytics
  const { 
    data: analytics,
    isLoading: analyticsLoading 
  } = useQuery({
    queryKey: notificationQueryKeys.analytics(analyticsDays),
    queryFn: () => getNotificationAnalytics(analyticsDays),
  });

  // Get detailed log when modal opens
  const { 
    data: logDetail,
    isLoading: logDetailLoading 
  } = useQuery({
    queryKey: notificationQueryKeys.log(selectedLog?.id || 0),
    queryFn: () => getNotificationLog(selectedLog!.id),
    enabled: !!selectedLog
  });

  const handleViewDetails = (log: NotificationLog) => {
    setSelectedLog(log);
    setIsDetailModalOpen(true);
  };

  const handleFilterChange = (field: string, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPage(0); // Reset to first page when filtering
  };

  const resetFilters = () => {
    setFilters({
      recipient_type: '',
      status: '',
      channel: '',
      search: ''
    });
    setPage(0);
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'email': return <Email fontSize="small" />;
      case 'sms': return <Sms fontSize="small" />;
      case 'push': return <NotificationImportant fontSize="small" />;
      case 'in_app': return <Notifications fontSize="small" />;
      default: return <Notifications fontSize="small" />;
    }
  };

  const getRecipientTypeIcon = (type: string) => {
    return type === 'customer' ? <Person fontSize="small" /> : <Group fontSize="small" />;
  };

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'sent':
      case 'delivered':
        return <CheckCircle fontSize="small" color="success" />;
      case 'failed':
      case 'bounced':
        return <ErrorIcon fontSize="small" color="error" />;
      case 'pending':
        return <Schedule fontSize="small" color="warning" />;
      default:
        return <Warning fontSize="small" />;
    }
  };

  if (logsError) {
    return (
      <Alert severity="error">
        Failed to load notification logs. Please try again.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Analytics Cards */}
      {analytics && (
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      Total Notifications
                    </Typography>
                    <Typography variant="h5">
                      {analytics.total_notifications.toLocaleString()}
                    </Typography>
                  </Box>
                  <TrendingUp color="primary" />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      Success Rate
                    </Typography>
                    <Typography variant="h5">
                      {analytics.total_notifications > 0 
                        ? Math.round(((analytics.status_breakdown?.delivered || 0) + (analytics.status_breakdown?.sent || 0)) / analytics.total_notifications * 100)
                        : 0}%
                    </Typography>
                  </Box>
                  <CheckCircle color="success" />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      Email Notifications
                    </Typography>
                    <Typography variant="h5">
                      {analytics.channel_breakdown?.email || 0}
                    </Typography>
                  </Box>
                  <Email color="primary" />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      Failed Notifications
                    </Typography>
                    <Typography variant="h5">
                      {(analytics.status_breakdown?.failed || 0) + (analytics.status_breakdown?.bounced || 0)}
                    </Typography>
                  </Box>
                  <ErrorIcon color="error" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Main Content */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" component="h2">
              Notification Logs
            </Typography>
            <Box display="flex" gap={1}>
              <Tooltip title="Refresh">
                <IconButton onClick={() => refetchLogs()}>
                  <Refresh />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {/* Filters */}
          <Grid container spacing={2} mb={3}>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Channel</InputLabel>
                <Select
                  value={filters.channel}
                  label="Channel"
                  onChange={(e) => handleFilterChange('channel', e.target.value)}
                >
                  <MenuItem value="">All Channels</MenuItem>
                  {NOTIFICATION_CHANNELS.map(channel => (
                    <MenuItem key={channel} value={channel}>
                      {getChannelDisplayName(channel)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  label="Status"
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  {NOTIFICATION_STATUSES.map(status => (
                    <MenuItem key={status} value={status}>
                      {getStatusDisplayName(status)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Recipient Type</InputLabel>
                <Select
                  value={filters.recipient_type}
                  label="Recipient Type"
                  onChange={(e) => handleFilterChange('recipient_type', e.target.value)}
                >
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="customer">Customer</MenuItem>
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="segment">Segment</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Search recipient"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                placeholder="Search by email, name..."
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box display="flex" gap={1}>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<FilterList />}
                  onClick={resetFilters}
                >
                  Clear Filters
                </Button>
              </Box>
            </Grid>
          </Grid>

          {/* Table */}
          {logsLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Recipient</TableCell>
                      <TableCell>Channel</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Subject/Content</TableCell>
                      <TableCell>Sent At</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {logs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            {getRecipientTypeIcon(log.recipient_type)}
                            <Box>
                              <Typography variant="body2">
                                {log.recipient_identifier}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {log.recipient_type}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            {getChannelIcon(log.channel)}
                            {getChannelDisplayName(log.channel as any)}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            {getStatusIcon(log.status)}
                            <Chip
                              label={getStatusDisplayName(log.status as any)}
                              size="small"
                              className={getStatusColor(log.status as any)}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box>
                            {log.subject && (
                              <Typography variant="body2" fontWeight="medium">
                                {log.subject.length > 50 ? `${log.subject.substring(0, 50)}...` : log.subject}
                              </Typography>
                            )}
                            <Typography variant="caption" color="text.secondary">
                              {log.content.length > 80 ? `${log.content.substring(0, 80)}...` : log.content}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          {log.sent_at ? (
                            <Box>
                              <Typography variant="body2">
                                {formatDate(log.sent_at)}
                              </Typography>
                              {log.delivered_at && (
                                <Typography variant="caption" color="text.secondary">
                                  Delivered: {formatDate(log.delivered_at)}
                                </Typography>
                              )}
                            </Box>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              {formatDate(log.created_at)}
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View Details">
                            <IconButton 
                              size="small" 
                              onClick={() => handleViewDetails(log)}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                    {logs.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                          <Typography color="text.secondary">
                            No notification logs found
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>

              <TablePagination
                component="div"
                count={-1} // Unknown total count
                page={page}
                onPageChange={(_, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => {
                  setRowsPerPage(parseInt(e.target.value, 10));
                  setPage(0);
                }}
                rowsPerPageOptions={[10, 25, 50, 100]}
              />
            </>
          )}
        </CardContent>
      </Card>

      {/* Detail Modal */}
      <Dialog 
        open={isDetailModalOpen} 
        onClose={() => setIsDetailModalOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Notification Details</DialogTitle>
        <DialogContent>
          {logDetailLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : logDetail ? (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Recipient
                  </Typography>
                  <Typography gutterBottom>
                    {logDetail.recipient_identifier} ({logDetail.recipient_type})
                  </Typography>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Channel
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1} gutterBottom>
                    {getChannelIcon(logDetail.channel)}
                    {getChannelDisplayName(logDetail.channel as any)}
                  </Box>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Status
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1} gutterBottom>
                    {getStatusIcon(logDetail.status)}
                    <Chip
                      label={getStatusDisplayName(logDetail.status as any)}
                      size="small"
                      className={getStatusColor(logDetail.status as any)}
                    />
                  </Box>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Created At
                  </Typography>
                  <Typography gutterBottom>
                    {formatDate(logDetail.created_at)}
                  </Typography>
                </Grid>

                {logDetail.subject && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Subject
                    </Typography>
                    <Typography gutterBottom>
                      {logDetail.subject}
                    </Typography>
                  </Grid>
                )}

                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Content
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50', mt: 1 }}>
                    <Typography style={{ whiteSpace: 'pre-wrap' }}>
                      {logDetail.content}
                    </Typography>
                  </Paper>
                </Grid>

                {logDetail.error_message && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="error">
                      Error Message
                    </Typography>
                    <Alert severity="error" sx={{ mt: 1 }}>
                      {logDetail.error_message}
                    </Alert>
                  </Grid>
                )}

                {logDetail.context_data && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Context Data
                    </Typography>
                    <Paper sx={{ p: 2, bgcolor: 'grey.50', mt: 1 }}>
                      <pre>{JSON.stringify(logDetail.context_data, null, 2)}</pre>
                    </Paper>
                  </Grid>
                )}

                {/* Timeline */}
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Timeline
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemIcon>
                        <Schedule fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Created"
                        secondary={formatDate(logDetail.created_at)}
                      />
                    </ListItem>
                    {logDetail.sent_at && (
                      <ListItem>
                        <ListItemIcon>
                          <CheckCircle fontSize="small" color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Sent"
                          secondary={formatDate(logDetail.sent_at)}
                        />
                      </ListItem>
                    )}
                    {logDetail.delivered_at && (
                      <ListItem>
                        <ListItemIcon>
                          <CheckCircle fontSize="small" color="success" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Delivered"
                          secondary={formatDate(logDetail.delivered_at)}
                        />
                      </ListItem>
                    )}
                    {logDetail.opened_at && (
                      <ListItem>
                        <ListItemIcon>
                          <Visibility fontSize="small" color="info" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Opened"
                          secondary={formatDate(logDetail.opened_at)}
                        />
                      </ListItem>
                    )}
                    {logDetail.clicked_at && (
                      <ListItem>
                        <ListItemIcon>
                          <TrendingUp fontSize="small" color="success" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Clicked"
                          secondary={formatDate(logDetail.clicked_at)}
                        />
                      </ListItem>
                    )}
                  </List>
                </Grid>
              </Grid>
            </Box>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDetailModalOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NotificationLogs;