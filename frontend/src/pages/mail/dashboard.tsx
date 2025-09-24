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
  Sync,
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
      main: '#1a73e8',
    },
    secondary: {
      main: '#ea4335',
    },
    background: {
      default: '#f1f3f4',
      paper: '#ffffff',
    },
    text: {
      primary: '#202124',
      secondary: '#5f6368',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiListItem: {
      styleOverrides: {
        root: {
          '&:hover': {
            backgroundColor: '#f2f2f2',
          },
          '&.Mui-selected': {
            backgroundColor: '#d2e3fc',
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
  is_unread: boolean;
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

  const handleEmailSelect = (emailId: number) => {
    setSelectedEmailId(emailId);
  };

  const handleSync = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.post('/mail/sync', { force_sync: true });
      const statsResponse = await api.get('/mail/dashboard');
      setStats(statsResponse.data);
      fetchEmails(page); // Refresh current page
    } catch (err: any) {
      setError(err.message || 'Failed to sync emails');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const syncInterval = setInterval(async () => {
      try {
        const prevUnread = stats?.unread_emails ?? 0;
        const statsResponse = await api.get('/mail/dashboard');
        setStats(statsResponse.data);
        if (statsResponse.data.unread_emails > prevUnread) {
          const newCount = statsResponse.data.unread_emails - prevUnread;
          setNewEmailCount(newCount);
          setToastOpen(true);
          fetchEmails(page); // Refresh list
        }
      } catch (err) {
        console.error('Auto-sync error:', err);
      }
    }, 60000); // Sync every minute

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

  const handleThreadSelect = (thread: Thread) => {
    // Select the latest email in the thread
    const latestEmail = thread.emails.sort((a, b) => new Date(b.received_at).getTime() - new Date(a.received_at).getTime())[0];
    setSelectedEmailId(latestEmail.id);
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
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* Stats Row (Tiles) */}
        <Box p={2} bgcolor="white" borderBottom="1px solid #dadce0" boxShadow={1}>
          <Grid container spacing={2} alignItems="center">
            {stats && ['total_emails', 'flagged_emails', 'today_emails', 'this_week_emails'].map((key) => (
              <Grid item xs={3} key={key}>
                <MetricCard
                  title={formatStatTitle(key)}
                  value={stats[key as keyof MailStats]}
                  icon={getStatIcon(key as keyof MailStats)}
                  color="info"
                  onClick={() => handleStatClick(key)}
                />
              </Grid>
            ))}
            <Grid item xs={12} container justifyContent="center" spacing={2}>
              <Grid item>
                <Button variant="outlined" color="primary" startIcon={<Sync />} onClick={handleSync} disabled={loading}>
                  Sync
                </Button>
              </Grid>
              <Grid item>
                <Button variant="contained" color="primary" startIcon={<Add />} onClick={() => setComposeOpen(true)}>
                  Compose
                </Button>
              </Grid>
              <Grid item>
                <Button 
                  variant="outlined" 
                  color="primary" 
                  startIcon={<EmailIcon />} 
                  onClick={handleSetupOrManage}
                >
                  {emailTokens.length > 0 ? 'Manage Accounts' : 'Setup Email Account'}
                </Button>
              </Grid>
            </Grid>
          </Grid>
        </Box>

        {/* Main Content Flex Row */}
        <Box display="flex" flexGrow={1}>
          {/* Left Sidebar */}
          <Box
            width="15%"
            height="100%"
            overflowY="auto"
            borderRight="1px solid #dadce0"
            bgcolor="#f1f3f4"
          >
            <List component="nav">
              <ListItem button selected={currentFolder === 'INBOX'} onClick={() => handleFolderChange('INBOX')} sx={{ cursor: 'pointer' }}>
                <ListItemIcon><Inbox sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Inbox" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'STARRED'} onClick={() => handleFolderChange('STARRED')} sx={{ cursor: 'pointer' }}>
                <ListItemIcon><StarIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Starred" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'SNOOZED'} onClick={() => handleFolderChange('SNOOZED')} sx={{ cursor: 'pointer' }}>
                <ListItemIcon><SnoozeIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Snoozed" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'IMPORTANT'} onClick={() => handleFolderChange('IMPORTANT')} sx={{ cursor: 'pointer' }}>
                <ListItemIcon><ImportantIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Important" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'SENT'} onClick={() => handleFolderChange('SENT')} sx={{ cursor: 'pointer' }}>
                <ListItemIcon><Send sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Sent" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'DRAFTS'} onClick={() => handleFolderChange('DRAFTS')} sx={{ cursor: 'pointer' }}>
                <ListItemIcon><Drafts sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Drafts" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'SPAM'} onClick={() => handleFolderChange('SPAM')} sx={{ cursor: 'pointer' }}>
                <ListItemIcon><ReportIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Spam" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'TRASH'} onClick={() => handleFolderChange('TRASH')} sx={{ cursor: 'pointer' }}>
                <ListItemIcon><TrashIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Trash" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'ARCHIVED'} onClick={() => handleFolderChange('ARCHIVED')} sx={{ cursor: 'pointer' }}>
                <ListItemIcon><ArchiveIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Archived" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'CATEGORIES'} onClick={() => handleFolderChange('CATEGORIES')} sx={{ cursor: 'pointer' }}>
                <ListItemIcon><CategoryIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Categories" sx={{ color: '#202124' }} />
              </ListItem>
            </List>
            <Divider />
            {/* Add more custom labels or sections if needed */}
          </Box>

          {/* Email List */}
          <Box width="25%" height="100%" overflowY="auto" pr={2} borderRight="1px solid #dadce0" bgcolor="white">
            <Box sx={{ display: 'flex', alignItems: 'center', p: 2, color: '#202124' }}>
              <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                {currentFolder} ({threads.length})
              </Typography>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
                size="small"
              />
            </Box>
            <List disablePadding>
              {threads.map((thread, index) => (
                <ListItem
                  key={thread.thread_id}
                  button
                  onClick={() => handleThreadSelect(thread)}
                  sx={{
                    py: 1.5,
                    borderBottom: '1px solid #f1f3f4',
                    '&:hover': { bgcolor: '#f2f2f2' },
                    '&.Mui-selected': { bgcolor: '#d2e3fc' },
                    bgcolor: thread.emails.some(e => e.is_unread) ? '#f5f5f5' : 'transparent', // 10% grey for unread
                  }}
                >
                  <ListItemIcon>
                    <Avatar sx={{ width: 40, height: 40, bgcolor: '#e8f0fe', color: '#1967d2' }}>
                      {thread.emails[0].from_name ? thread.emails[0].from_name[0] : <Person />}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={thread.emails[0].subject}
                    secondary={`${thread.emails[0].from_name || thread.emails[0].from_address} • ${formatTimeAgo(thread.emails[0].received_at)} (${thread.emails.length} messages)`}
                    primaryTypographyProps={{
                      noWrap: true,
                      fontWeight: thread.emails.some(e => e.is_unread) ? "bold" : "normal",
                      color: '#202124',
                    }}
                    secondaryTypographyProps={{ noWrap: true, color: '#5f6368' }}
                  />
                </ListItem>
              ))}
            </List>
            {listLoading && <Box display="flex" justifyContent="center" p={2}><CircularProgress size={24} /></Box>}
            {threads.length === 0 && <Typography sx={{ p: 2, color: '#5f6368' }}>No emails</Typography>}
          </Box>

          {/* Email Viewer */}
          <Box flexGrow={1} height="100%" p={3} overflowY="auto" bgcolor="white">
            {selectedEmailId ? (
              <EmailReader messageId={selectedEmailId} />
            ) : (
              <Box sx={{ textAlign: "center", mt: 10 }}>
                <Typography variant="h6" color="textSecondary">
                  Select an email to view
                </Typography>
              </Box>
            )}
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