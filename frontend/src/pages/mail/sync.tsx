// frontend/src/pages/mail/sync.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Avatar,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  AppBar,
  Toolbar,
  FormControlLabel,
  Switch,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import {
  Sync as SyncIcon,
  Email,
  CheckCircle,
  Error,
  PlayArrow,
  Pause,
  Stop,
  Settings,
  Refresh,
  Schedule,
  Folder,
  ExpandMore,
  Info,
} from "@mui/icons-material";
import { useRouter } from "next/router";
import api from "../../lib/api";
import { useOAuth } from "../../hooks/useOAuth";

interface SyncJob {
  id: string;
  token_id: number;
  email_address: string;
  status: "running" | "completed" | "failed" | "paused" | "queued";
  progress: number;
  total_emails: number;
  processed_emails: number;
  errors: number;
  started_at: string;
  completed_at?: string;
  estimated_completion?: string;
  folders_synced: string[];
  last_error?: string;
}

interface SyncSettings {
  auto_sync_enabled: boolean;
  sync_interval_minutes: number;
  max_concurrent_syncs: number;
  sync_folders: string[];
  sync_attachments: boolean;
  keep_local_copies: boolean;
}

interface SyncStats {
  total_syncs_today: number;
  successful_syncs: number;
  failed_syncs: number;
  emails_synced_today: number;
  last_full_sync: string | null;
  next_scheduled_sync: string | null;
}

const SyncPage: React.FC = () => {
  const router = useRouter();
  const { getUserTokens } = useOAuth();
  const [syncJobs, setSyncJobs] = useState<SyncJob[]>([]);
  const [syncSettings, setSyncSettings] = useState<SyncSettings | null>(null);
  const [syncStats, setSyncStats] = useState<SyncStats | null>(null);
  const [emailTokens, setEmailTokens] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const tokens = await getUserTokens();
        setEmailTokens(tokens);
        await fetchSyncData();
      } catch (err) {
        setError('Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchSyncData, 5000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, getUserTokens]);

  const fetchSyncData = async () => {
    try {
      const [jobsRes, settingsRes, statsRes] = await Promise.all([
        api.get('/api/v1/mail/sync/jobs'),
        api.get('/api/v1/mail/sync/settings'),
        api.get('/api/v1/mail/sync/stats')
      ]);
      
      setSyncJobs(jobsRes.data);
      setSyncSettings(settingsRes.data);
      setSyncStats(statsRes.data);
    } catch (err: any) {
      console.error('Error fetching sync data:', err);
      setError('Failed to load sync data. Please try again.');
    }
  };

  const handleStartSync = async (tokenId?: number) => {
    try {
      const response = await api.post('/api/v1/mail/sync', {
        token_id: tokenId
      });
      if (response.data.success) {
        fetchSyncData();
      } else {
        setError(response.data.message);
      }
    } catch (err: any) {
      setError('Failed to start sync. Please try again.');
    }
  };

  const handleStopSync = async (jobId: string) => {
    try {
      await api.post(`/api/v1/mail/sync/jobs/${jobId}/stop`);
      fetchSyncData();
    } catch (err: any) {
      setError('Failed to stop sync. Please try again.');
    }
  };

  const handleUpdateSettings = async (newSettings: Partial<SyncSettings>) => {
    try {
      await api.put('/api/v1/mail/sync/settings', newSettings);
      fetchSyncData();
    } catch (err: any) {
      setError('Failed to update settings. Please try again.');
    }
  };

  const formatTimeAgo = (dateTime: string) => {
    const date = new Date(dateTime);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const formatEstimatedTime = (dateTime: string) => {
    const date = new Date(dateTime);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffMins <= 0) return "Any moment";
    if (diffMins < 60) return `${diffMins}m remaining`;
    const diffHours = Math.floor(diffMins / 60);
    return `${diffHours}h ${diffMins % 60}m remaining`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'info';
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'paused': return 'warning';
      case 'queued': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <CircularProgress size={20} />;
      case 'completed': return <CheckCircle color="success" />;
      case 'failed': return <Error color="error" />;
      case 'paused': return <Pause color="warning" />;
      case 'queued': return <Schedule color="action" />;
      default: return <Info />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <SyncIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Email Sync
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
            }
            label="Auto Refresh"
            sx={{ mr: 2 }}
          />
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchSyncData}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={() => handleStartSync()}
          >
            Sync All
          </Button>
        </Toolbar>
      </AppBar>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ m: 2 }}>
          {error}
        </Alert>
      )}

      {/* Main Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
        {/* Sync Stats */}
        {syncStats && (
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Syncs Today
                  </Typography>
                  <Typography variant="h5">
                    {syncStats.total_syncs_today}
                  </Typography>
                  <Typography variant="body2" color="success.main">
                    {syncStats.successful_syncs} successful
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Failed Syncs
                  </Typography>
                  <Typography variant="h5" color={syncStats.failed_syncs > 0 ? "error.main" : "success.main"}>
                    {syncStats.failed_syncs}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Emails Synced Today
                  </Typography>
                  <Typography variant="h5">
                    {syncStats.emails_synced_today.toLocaleString()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Next Sync
                  </Typography>
                  <Typography variant="h6">
                    {syncStats.next_scheduled_sync 
                      ? formatEstimatedTime(syncStats.next_scheduled_sync)
                      : "Not scheduled"
                    }
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        <Grid container spacing={3}>
          {/* Active Sync Jobs */}
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sync Jobs
                </Typography>
                <List>
                  {syncJobs.map((job) => (
                    <ListItem
                      key={job.id}
                      sx={{
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1,
                        mb: 2,
                      }}
                    >
                      <ListItemIcon>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <Email />
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                            <Typography variant="subtitle1">
                              {job.email_address}
                            </Typography>
                            <Chip
                              icon={getStatusIcon(job.status)}
                              label={job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                              color={getStatusColor(job.status) as any}
                              size="small"
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {job.processed_emails.toLocaleString()} / {job.total_emails.toLocaleString()} emails
                              {job.errors > 0 && (
                                <span style={{ color: 'red' }}> • {job.errors} errors</span>
                              )}
                            </Typography>
                            {job.status === 'running' && job.estimated_completion && (
                              <Typography variant="body2" color="text.secondary">
                                {formatEstimatedTime(job.estimated_completion)}
                              </Typography>
                            )}
                            {job.last_error && (
                              <Typography variant="body2" color="error.main">
                                Error: {job.last_error}
                              </Typography>
                            )}
                            <Box sx={{ mt: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={job.progress}
                                sx={{ height: 6, borderRadius: 3 }}
                              />
                              <Typography variant="caption" color="text.secondary">
                                {job.progress}% complete
                              </Typography>
                            </Box>
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Started {formatTimeAgo(job.started_at)}
                          </Typography>
                          {job.status === 'running' && (
                            <IconButton
                              size="small"
                              onClick={() => handleStopSync(job.id)}
                              color="warning"
                            >
                              <Stop />
                            </IconButton>
                          )}
                          {(job.status === 'paused' || job.status === 'failed') && (
                            <IconButton
                              size="small"
                              onClick={() => handleStartSync(job.token_id)}
                              color="primary"
                            >
                              <PlayArrow />
                            </IconButton>
                          )}
                        </Box>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>

                {syncJobs.length === 0 && (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <SyncIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary">
                      No active sync jobs
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Start a sync to see progress here.
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Sync Settings */}
          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sync Settings
                </Typography>
                
                {syncSettings && (
                  <Box>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={syncSettings.auto_sync_enabled}
                          onChange={(e) => handleUpdateSettings({ auto_sync_enabled: e.target.checked })}
                        />
                      }
                      label="Auto Sync"
                      sx={{ mb: 2 }}
                    />

                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Sync Interval</InputLabel>
                      <Select
                        value={syncSettings.sync_interval_minutes}
                        label="Sync Interval"
                        onChange={(e) => handleUpdateSettings({ sync_interval_minutes: e.target.value as number })}
                      >
                        <MenuItem value={5}>5 minutes</MenuItem>
                        <MenuItem value={15}>15 minutes</MenuItem>
                        <MenuItem value={30}>30 minutes</MenuItem>
                        <MenuItem value={60}>1 hour</MenuItem>
                        <MenuItem value={120}>2 hours</MenuItem>
                      </Select>
                    </FormControl>

                    <TextField
                      fullWidth
                      label="Max Concurrent Syncs"
                      type="number"
                      value={syncSettings.max_concurrent_syncs}
                      onChange={(e) => handleUpdateSettings({ max_concurrent_syncs: parseInt(e.target.value) })}
                      sx={{ mb: 2 }}
                      inputProps={{ min: 1, max: 10 }}
                    />

                    <FormControlLabel
                      control={
                        <Switch
                          checked={syncSettings.sync_attachments}
                          onChange={(e) => handleUpdateSettings({ sync_attachments: e.target.checked })}
                        />
                      }
                      label="Sync Attachments"
                      sx={{ mb: 2 }}
                    />

                    <FormControlLabel
                      control={
                        <Switch
                          checked={syncSettings.keep_local_copies}
                          onChange={(e) => handleUpdateSettings({ keep_local_copies: e.target.checked })}
                        />
                      }
                      label="Keep Local Copies"
                      sx={{ mb: 2 }}
                    />

                    <Divider sx={{ my: 2 }} />

                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="subtitle2">Folder Settings</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          Select which folders to sync:
                        </Typography>
                        {["INBOX", "SENT", "DRAFTS", "SPAM", "TRASH"].map((folder) => (
                          <FormControlLabel
                            key={folder}
                            control={
                              <Switch
                                checked={syncSettings.sync_folders.includes(folder)}
                                onChange={(e) => {
                                  const newFolders = e.target.checked
                                    ? [...syncSettings.sync_folders, folder]
                                    : syncSettings.sync_folders.filter(f => f !== folder);
                                  handleUpdateSettings({ sync_folders: newFolders });
                                }}
                              />
                            }
                            label={folder}
                            sx={{ display: 'block', mb: 1 }}
                          />
                        ))}
                      </AccordionDetails>
                    </Accordion>
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<PlayArrow />}
                    onClick={() => handleStartSync()}
                    fullWidth
                  >
                    Sync All Accounts
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Settings />}
                    onClick={() => router.push('/mail/accounts')}
                    fullWidth
                  >
                    Manage Accounts
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Folder />}
                    onClick={() => router.push('/mail/inbox')}
                    fullWidth
                  >
                    View Inbox
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default SyncPage;