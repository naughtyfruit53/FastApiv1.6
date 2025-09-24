// frontend/src/pages/mail/dashboard.tsx
import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  Box,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CssBaseline,
  Divider,
  Pagination,
  Snackbar,
  IconButton,
} from "@mui/material";
import {
  Inbox,
  Send,
  Drafts,
  Flag,
  Today,
  DateRange as DateRangeIcon,
  Report as ReportIcon,
  MarkEmailUnread,
  Person,
  Add,
  Sync as SyncIcon,
  Star as StarIcon,
  AccessTime as SnoozeIcon,
  LabelImportant as ImportantIcon,
  Archive as ArchiveIcon,
  Delete as TrashIcon,
  Category as CategoryIcon,
  Email as EmailIcon,
} from "@mui/icons-material";
import { useRouter } from "next/router";
import api from "../../lib/api";
import { useAuth } from "../../context/AuthContext";
import { useOAuth } from "../../hooks/useOAuth";
import OAuthLoginButton from "../../components/OAuthLoginButton";
import EmailReader from "../../components/EmailReader";  // Assume this component exists for displaying email body
import MetricCard from "../../components/MetricCard";
import EmailCompose from "../../components/EmailCompose";
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#1a1a1a',
      secondary: '#6c757d',
    },
    grey: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#eeeeee',
      300: '#e0e0e0',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
      fontSize: '1.75rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1.125rem',
    },
    subtitle1: {
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
          border: '1px solid #f0f0f0',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 24px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          },
        },
        contained: {
          background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '2px 8px',
          '&:hover': {
            backgroundColor: '#f8fafc',
            transform: 'translateX(4px)',
            transition: 'all 0.2s ease-in-out',
          },
          '&.Mui-selected': {
            backgroundColor: '#e3f2fd',
            borderLeft: '3px solid #1976d2',
          },
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '2px 8px',
          '&:hover': {
            backgroundColor: '#f8fafc',
            transform: 'translateX(4px)',
            transition: 'all 0.2s ease-in-out',
          },
          '&.Mui-selected': {
            backgroundColor: '#e3f2fd',
            borderLeft: '3px solid #1976d2',
          },
        },
      },
    },
  },
});

interface MailStats {
  total_emails: number;
  unread_emails: number;
  flagged_emails: number;
  today_emails: number;
  this_week_emails: number;
  sent_emails: number;
  draft_emails: number;
  spam_emails: number;
}

interface RecentEmail {
  id: number;
  subject: string;
  from_address: string;
  from_name?: string;
  received_at: string;
  status: string;  // Changed from is_unread to status
  is_flagged: boolean;
  has_attachments: boolean;
  priority: "low" | "normal" | "high" | "urgent";
  body_text: string;  // Added for body display
  body_html?: string;  // Added for body display
  thread_id: string;  // Added for threading
}

interface UserEmailToken {
  id: number;
  email_address: string;
  display_name: string | null;
  provider: string;
  status: string;
  last_sync_at: string | null;
  last_sync_status: string | null;
  unread_count: number;
}

interface Thread {
  thread_id: string;
  emails: RecentEmail[];
}

const MailDashboard: React.FC = () => {
  const router = useRouter();
  const { logout } = useAuth();
  const { getUserTokens } = useOAuth();
  const [stats, setStats] = useState<MailStats | null>(null);
  const [emails, setEmails] = useState<RecentEmail[]>([]);
  const [threads, setThreads] = useState<Thread[]>([]);
  const [emailTokens, setEmailTokens] = useState<UserEmailToken[]>([]);
  const [selectedEmailId, setSelectedEmailId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [listLoading, setListLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [composeOpen, setComposeOpen] = useState(false);
  const [setupOpen, setSetupOpen] = useState(false);
  const [currentFolder, setCurrentFolder] = useState('INBOX');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [toastOpen, setToastOpen] = useState(false);
  const [newEmailCount, setNewEmailCount] = useState(0);
  const maxRetries = 3;
  const perPage = 50;

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch OAuth tokens (email accounts)
        const tokensResponse = await getUserTokens();
        setEmailTokens(tokensResponse);

        if (tokensResponse.length === 0) {
          setLoading(false);
          return;
        }

        // Fetch mail dashboard stats
        const statsResponse = await api.get('/mail/dashboard');
        setStats(statsResponse.data);
      } catch (error: any) {
        console.error('Error fetching mail dashboard data:', error);
        let errorMessage = 'Failed to load mail dashboard data';
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.userMessage) {
          errorMessage = error.userMessage;
        } else if (error.message) {
          errorMessage = error.message;
        }

        const status = error.status || error.response?.status;
        if (status === 401) {
          errorMessage = 'Authentication failed. Please log in again.';
          logout();
          router.push('/login');
        } else if (status === 403) {
          errorMessage = 'You do not have permission to access the mail dashboard. Contact your administrator.';
        } else if (status === 500) {
          errorMessage = 'Server error. Please try again later.';
        }

        setError(errorMessage);

        if (retryCount < maxRetries) {
          setTimeout(() => {
            setRetryCount(retryCount + 1);
          }, 2000);
        } else {
          setStats({
            total_emails: 0,
            unread_emails: 0,
            flagged_emails: 0,
            today_emails: 0,
            this_week_emails: 0,
            sent_emails: 0,
            draft_emails: 0,
            spam_emails: 0,
          });
          setEmails([]);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [retryCount, logout, router, getUserTokens]);

  const fetchEmails = useCallback(async (pageNum: number) => {
    setListLoading(true);
    try {
      const emailsResponse = await api.get('/mail/emails', {
        params: { folder: currentFolder, page: pageNum, per_page: perPage, sort_by: 'received_at', sort_order: 'desc' },
      });
      setEmails(emailsResponse.data.emails);
      setTotalPages(emailsResponse.data.total_pages);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch emails');
    } finally {
      setListLoading(false);
    }
  }, [currentFolder]);

  useEffect(() => {
    setPage(1);
    fetchEmails(1);
  }, [currentFolder, fetchEmails]);

  useEffect(() => {
    // Group emails into threads
    const grouped = emails.reduce((acc: {[key: string]: Thread}, email) => {
      if (!acc[email.thread_id]) {
        acc[email.thread_id] = { thread_id: email.thread_id, emails: [] };
      }
      acc[email.thread_id].emails.push(email);
      return acc;
    }, {});
    setThreads(Object.values(grouped));
  }, [emails]);

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
    fetchEmails(value);
  };

  const handleEmailSelect = async (emailId: number) => {
    setSelectedEmailId(emailId);
    try {
      await api.put(`/emails/${emailId}`, { status: 'READ' });
      fetchEmails(page);  // Refresh the list to remove highlight
    } catch (err) {
      console.error('Failed to mark email as read:', err);
    }
  };

  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'success' | 'error'>('idle');

  const handleSync = async (background = false) => {
    if (!background) setLoading(true);
    setSyncStatus('syncing');
    setError(null);
    try {
      // Start background sync without blocking UI
      api.post('/mail/sync', { force_sync: true })
        .then(() => {
          setSyncStatus('success');
          // Refresh data after sync completes
          return api.get('/mail/dashboard');
        })
        .then((statsResponse) => {
          setStats(statsResponse.data);
          fetchEmails(page);
          setTimeout(() => setSyncStatus('idle'), 3000); // Reset status after 3 seconds
        })
        .catch((err) => {
          setSyncStatus('error');
          console.error('Background sync error:', err);
          setTimeout(() => setSyncStatus('idle'), 5000);
        });
      
      if (!background) {
        // For manual sync, update UI immediately
        const statsResponse = await api.get('/mail/dashboard');
        setStats(statsResponse.data);
        fetchEmails(page);
      }
    } catch (err: any) {
      setSyncStatus('error');
      if (!background) {
        setError(err.message || 'Failed to sync emails');
      }
      setTimeout(() => setSyncStatus('idle'), 5000);
    } finally {
      if (!background) setLoading(false);
    }
  };

  useEffect(() => {
    const syncInterval = setInterval(async () => {
      try {
        const prevUnread = stats?.unread_emails ?? 0;
        // Background sync without blocking UI
        handleSync(true);
        
        // Check for new emails
        const statsResponse = await api.get('/mail/dashboard');
        if (statsResponse.data.unread_emails > prevUnread) {
          const newCount = statsResponse.data.unread_emails - prevUnread;
          setNewEmailCount(newCount);
          setToastOpen(true);
        }
      } catch (err) {
        console.error('Auto-sync error:', err);
      }
    }, 600000); // Sync every 10 minutes

    return () => clearInterval(syncInterval);
  }, [stats, page, fetchEmails]);

  const handleToastClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setToastOpen(false);
  };

  const handleToastClick = () => {
    setToastOpen(false);
    setCurrentFolder('INBOX');
    fetchEmails(1);
  };

  const handleSetupOrManage = () => {
    if (emailTokens.length === 0) {
      setSetupOpen(true);
    } else {
      router.push('/mail/accounts');
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

  const getStatIcon = (key: keyof MailStats) => {
    switch (key) {
      case 'total_emails': return <Inbox />;
      case 'flagged_emails': return <Flag />;
      case 'today_emails': return <Today />;
      case 'this_week_emails': return <DateRangeIcon />;
      default: return <Inbox />;
    }
  };

  const formatStatTitle = (key: string) => {
    return key.replace(/_/g, ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  const handleStatClick = (key: string) => {
    switch (key) {
      case 'total_emails':
        setCurrentFolder('INBOX');
        break;
      case 'flagged_emails':
        setCurrentFolder('FLAGGED');
        break;
      case 'today_emails':
        setCurrentFolder('TODAY');
        break;
      case 'this_week_emails':
        setCurrentFolder('THIS_WEEK');
        break;
      default:
        setCurrentFolder('INBOX');
    }
  };

  const handleFolderChange = (folder: string) => {
    setCurrentFolder(folder);
  };

  const handleThreadSelect = async (thread: Thread) => {
    // Select the latest email in the thread
    const latestEmail = thread.emails.sort((a, b) => new Date(b.received_at).getTime() - new Date(a.received_at).getTime())[0];
    await handleEmailSelect(latestEmail.id);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
        <Button
          variant="outlined"
          onClick={() => setRetryCount(retryCount + 1)}
          sx={{ mt: 2 }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (emailTokens.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h5" gutterBottom>
          No Email Accounts Connected
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Connect your email account to start sending and receiving emails.
        </Typography>
        <Button
          variant="contained"
          startIcon={<EmailIcon />}
          onClick={() => setSetupOpen(true)}
        >
          Setup Email Account
        </Button>
        <Dialog open={setupOpen} onClose={() => setSetupOpen(false)} fullWidth maxWidth="sm">
          <DialogTitle>Setup Email Account</DialogTitle>
          <DialogContent>
            <OAuthLoginButton variant="list" />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSetupOpen(false)}>Cancel</Button>
          </DialogActions>
        </Dialog>
      </Box>
    );
  }

  if (!stats) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">No mail data available</Alert>
      </Box>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        minHeight: '100vh',
        bgcolor: 'background.default'
      }}>
        {/* Enhanced Header with Stats */}
        <Box 
          sx={{ 
            p: 3, 
            bgcolor: 'background.paper', 
            borderBottom: '1px solid #e0e0e0',
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box>
              <Typography variant="h4" component="h1" sx={{ 
                color: 'text.primary',
                background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}>
                Mail Dashboard
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Manage your email communications efficiently
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button 
                variant="contained" 
                startIcon={<Add />} 
                onClick={() => setComposeOpen(true)}
                sx={{ 
                  px: 3,
                  py: 1.5,
                  fontSize: '0.95rem'
                }}
              >
                Compose
              </Button>
              <Button 
                variant="outlined" 
                startIcon={syncStatus === 'syncing' ? <CircularProgress size={16} /> : <SyncIcon />}
                onClick={() => handleSync(false)}
                disabled={syncStatus === 'syncing'}
                sx={{ 
                  px: 3, 
                  py: 1.5,
                  color: syncStatus === 'success' ? 'success.main' : 
                         syncStatus === 'error' ? 'error.main' : 'primary.main',
                  borderColor: syncStatus === 'success' ? 'success.main' : 
                               syncStatus === 'error' ? 'error.main' : 'primary.main',
                }}
              >
                {syncStatus === 'syncing' ? 'Syncing...' : 
                 syncStatus === 'success' ? 'Synced' : 
                 syncStatus === 'error' ? 'Retry' : 'Sync'}
              </Button>
              <Button 
                variant="outlined" 
                startIcon={<EmailIcon />} 
                onClick={handleSetupOrManage}
                sx={{ px: 3, py: 1.5 }}
              >
                {emailTokens.length > 0 ? 'Accounts' : 'Setup'}
              </Button>
            </Box>
          </Box>

          {/* Enhanced Stats Grid */}
          <Grid container spacing={3}>
            {stats && [
              { key: 'total_emails', label: 'Total Emails', color: '#1976d2' },
              { key: 'unread_emails', label: 'Unread', color: '#dc004e' },
              { key: 'today_emails', label: 'Today', color: '#388e3c' },
              { key: 'this_week_emails', label: 'This Week', color: '#f57c00' },
            ].map((item) => (
              <Grid item xs={12} sm={6} md={3} key={item.key}>
                <Box
                  onClick={() => handleStatClick(item.key)}
                  sx={{
                    p: 2.5,
                    bgcolor: 'background.paper',
                    borderRadius: 2,
                    border: '1px solid #e0e0e0',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
                      borderColor: item.color,
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 2,
                        bgcolor: `${item.color}20`,
                        color: item.color,
                        mr: 2,
                      }}
                    >
                      {getStatIcon(item.key as keyof MailStats)}
                    </Box>
                    <Typography variant="subtitle2" color="text.secondary">
                      {item.label}
                    </Typography>
                  </Box>
                  <Typography variant="h4" sx={{ 
                    fontWeight: 700, 
                    color: item.color,
                    lineHeight: 1
                  }}>
                    {stats[item.key as keyof MailStats].toLocaleString()}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Main Content with improved layout */}
        <Box display="flex" flexGrow={1} sx={{ height: 'calc(100vh - 280px)' }}>
          {/* Enhanced Left Sidebar */}
          <Box
            sx={{
              width: '280px',
              bgcolor: 'background.paper',
              borderRight: '1px solid #e0e0e0',
              overflowY: 'auto',
              p: 2,
            }}
          >
            <Typography variant="subtitle1" sx={{ mb: 2, px: 1, color: 'text.primary' }}>
              Folders
            </Typography>
            <List component="nav" sx={{ px: 0 }}>
              {[
                { key: 'INBOX', label: 'Inbox', icon: <Inbox />, badge: stats?.unread_emails },
                { key: 'STARRED', label: 'Starred', icon: <StarIcon /> },
                { key: 'SNOOZED', label: 'Snoozed', icon: <SnoozeIcon /> },
                { key: 'IMPORTANT', label: 'Important', icon: <ImportantIcon /> },
                { key: 'SENT', label: 'Sent', icon: <Send /> },
                { key: 'DRAFTS', label: 'Drafts', icon: <Drafts /> },
                { key: 'SPAM', label: 'Spam', icon: <ReportIcon /> },
                { key: 'TRASH', label: 'Trash', icon: <TrashIcon /> },
                { key: 'ARCHIVED', label: 'Archived', icon: <ArchiveIcon /> },
              ].map((folder) => (
                <ListItem
                  key={folder.key}
                  button
                  selected={currentFolder === folder.key}
                  onClick={() => handleFolderChange(folder.key)}
                  sx={{ py: 1, mb: 0.5 }}
                >
                  <ListItemIcon sx={{ minWidth: 36, color: 'primary.main' }}>
                    {folder.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={folder.label} 
                    sx={{ 
                      '& .MuiListItemText-primary': { 
                        fontSize: '0.9rem',
                        fontWeight: currentFolder === folder.key ? 600 : 400
                      }
                    }} 
                  />
                  {folder.badge && folder.badge > 0 && (
                    <Box
                      sx={{
                        bgcolor: 'error.main',
                        color: 'white',
                        borderRadius: '12px',
                        px: 1,
                        py: 0.2,
                        fontSize: '0.75rem',
                        minWidth: '20px',
                        textAlign: 'center',
                      }}
                    >
                      {folder.badge}
                    </Box>
                  )}
                </ListItem>
              ))}
            </List>
          </Box>

          {/* Enhanced Email List */}
          <Box 
            sx={{ 
              width: '420px', 
              bgcolor: 'background.paper',
              borderRight: '1px solid #e0e0e0',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0', bgcolor: 'grey.50' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {currentFolder.charAt(0) + currentFolder.slice(1).toLowerCase()} ({threads.length})
                </Typography>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={handlePageChange}
                  color="primary"
                  size="small"
                  sx={{
                    '& .MuiPaginationItem-root': {
                      fontSize: '0.75rem',
                    }
                  }}
                />
              </Box>
            </Box>
            
            <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
              {listLoading && (
                <Box display="flex" justifyContent="center" p={3}>
                  <CircularProgress size={32} />
                </Box>
              )}
              
              <List disablePadding>
                {threads.map((thread, index) => (
                  <ListItem
                    key={thread.thread_id}
                    button
                    onClick={() => handleThreadSelect(thread)}
                    sx={{
                      py: 2,
                      px: 3,
                      borderBottom: '1px solid #f0f0f0',
                      bgcolor: thread.emails.some(e => e.status === "UNREAD") 
                        ? '#fff3cd' 
                        : 'transparent',
                      '&:hover': { 
                        bgcolor: thread.emails.some(e => e.status === "UNREAD")
                          ? '#ffeaa7'
                          : '#f8fafc'
                      },
                      '&.Mui-selected': { 
                        bgcolor: '#e3f2fd',
                        borderLeft: '4px solid #1976d2'
                      },
                    }}
                  >
                    <ListItemIcon sx={{ mr: 2 }}>
                      <Avatar 
                        sx={{ 
                          width: 48, 
                          height: 48, 
                          bgcolor: 'primary.main',
                          fontSize: '1.1rem',
                          fontWeight: 600
                        }}
                      >
                        {thread.emails[0].from_name 
                          ? thread.emails[0].from_name[0].toUpperCase() 
                          : <Person />
                        }
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography
                          variant="subtitle2"
                          sx={{
                            fontWeight: thread.emails.some(e => e.status === "UNREAD") ? 700 : 500,
                            color: 'text.primary',
                            fontSize: '0.95rem',
                            lineHeight: 1.3,
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                          }}
                        >
                          {thread.emails[0].subject || '(No Subject)'}
                        </Typography>
                      }
                      secondary={
                        <Box>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              color: 'text.secondary',
                              fontSize: '0.85rem',
                              mb: 0.5
                            }}
                          >
                            {thread.emails[0].from_name || thread.emails[0].from_address}
                          </Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography 
                              variant="caption" 
                              sx={{ color: 'text.secondary' }}
                            >
                              {formatTimeAgo(thread.emails[0].received_at)}
                            </Typography>
                            {thread.emails.length > 1 && (
                              <Box
                                sx={{
                                  bgcolor: 'primary.main',
                                  color: 'white',
                                  borderRadius: '10px',
                                  px: 1,
                                  py: 0.2,
                                  fontSize: '0.7rem',
                                }}
                              >
                                {thread.emails.length}
                              </Box>
                            )}
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
              
              {threads.length === 0 && !listLoading && (
                <Box sx={{ 
                  textAlign: 'center', 
                  py: 8,
                  color: 'text.secondary' 
                }}>
                  <Inbox sx={{ fontSize: 48, opacity: 0.5, mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    No emails in {currentFolder.toLowerCase()}
                  </Typography>
                  <Typography variant="body2">
                    Your emails will appear here when available.
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>

          {/* Enhanced Email Viewer */}
          <Box 
            sx={{ 
              flexGrow: 1, 
              bgcolor: 'background.paper',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {selectedEmailId ? (
              <Box sx={{ height: '100%', overflow: 'hidden' }}>
                <EmailReader messageId={selectedEmailId} />
              </Box>
            ) : (
              <Box sx={{ 
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                color: 'text.secondary',
                bgcolor: 'grey.50'
              }}>
                <EmailIcon sx={{ fontSize: 64, opacity: 0.3, mb: 2 }} />
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 300 }}>
                  Select an email to view
                </Typography>
                <Typography variant="body2">
                  Choose an email from the list to read its contents
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
      </Box>
          </Box>
        </Box>
      </Box>

      <Dialog open={composeOpen} onClose={() => setComposeOpen(false)} fullWidth maxWidth="md">
        <EmailCompose open={composeOpen} onClose={() => setComposeOpen(false)} />
      </Dialog>

      <Dialog open={setupOpen} onClose={() => setSetupOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Setup Email Account</DialogTitle>
        <DialogContent>
          <OAuthLoginButton variant="list" />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSetupOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={toastOpen}
        autoHideDuration={6000}
        onClose={handleToastClose}
        message={`${newEmailCount} new email${newEmailCount > 1 ? 's' : ''} arrived`}
        action={
          <Button color="inherit" size="small" onClick={handleToastClick}>
            View
          </Button>
        }
      />
    </ThemeProvider>
  );
};

export default MailDashboard;