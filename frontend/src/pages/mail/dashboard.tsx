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
  CssBaseline,
  Divider,
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

const MailDashboard: React.FC = () => {
  const router = useRouter();
  const { logout } = useAuth();
  const { getUserTokens } = useOAuth();
  const [stats, setStats] = useState<MailStats | null>(null);
  const [emails, setEmails] = useState<RecentEmail[]>([]);
  const [emailTokens, setEmailTokens] = useState<UserEmailToken[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<RecentEmail | null>(null);
  const [loading, setLoading] = useState(true);
  const [listLoading, setListLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [composeOpen, setComposeOpen] = useState(false);
  const [currentFolder, setCurrentFolder] = useState('INBOX');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const observer = useRef<IntersectionObserver | null>(null);
  const maxRetries = 3;
  const perPage = 20; // Smaller batches for infinite scroll

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
      const newEmails = emailsResponse.data.emails;
      setEmails(prev => pageNum === 1 ? newEmails : [...prev, ...newEmails]);
      setHasMore(newEmails.length === perPage);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch emails');
    } finally {
      setListLoading(false);
    }
  }, [currentFolder]);

  useEffect(() => {
    setPage(1);
    setEmails([]);
    setHasMore(true);
    fetchEmails(1);
  }, [currentFolder, fetchEmails]);

  const lastEmailRef = useCallback((node: HTMLLIElement | null) => {
    if (listLoading) return;
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prev => prev + 1);
        fetchEmails(page + 1);
      }
    });
    if (node) observer.current.observe(node);
  }, [listLoading, hasMore, fetchEmails, page]);

  const handleEmailSelect = (email: RecentEmail) => {
    setSelectedEmail(email);
  };

  const handleSync = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.post('/mail/sync', { force_sync: false });
      const statsResponse = await api.get('/mail/dashboard');
      setStats(statsResponse.data);
      fetchEmails(1); // Refresh email list after sync
    } catch (err: any) {
      setError(err.message || 'Failed to sync emails');
    } finally {
      setLoading(false);
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
        <OAuthLoginButton variant="list" />
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
            </Grid>
          </Grid>
        </Box>

        {/* Main Content Flex Row */}
        <Box display="flex" flexGrow={1} overflow="hidden">
          {/* Left Sidebar */}
          <Box
            width="15%"
            overflowY="auto"
            borderRight="1px solid #dadce0"
            bgcolor="#f1f3f4"
          >
            <List component="nav">
              <ListItem button selected={currentFolder === 'INBOX'} onClick={() => handleFolderChange('INBOX')}>
                <ListItemIcon><Inbox sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Inbox" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'STARRED'} onClick={() => handleFolderChange('STARRED')}>
                <ListItemIcon><StarIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Starred" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'SNOOZED'} onClick={() => handleFolderChange('SNOOZED')}>
                <ListItemIcon><SnoozeIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Snoozed" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'IMPORTANT'} onClick={() => handleFolderChange('IMPORTANT')}>
                <ListItemIcon><ImportantIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Important" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'SENT'} onClick={() => handleFolderChange('SENT')}>
                <ListItemIcon><Send sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Sent" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'DRAFTS'} onClick={() => handleFolderChange('DRAFTS')}>
                <ListItemIcon><Drafts sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Drafts" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'SPAM'} onClick={() => handleFolderChange('SPAM')}>
                <ListItemIcon><ReportIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Spam" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'TRASH'} onClick={() => handleFolderChange('TRASH')}>
                <ListItemIcon><TrashIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Trash" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'ARCHIVED'} onClick={() => handleFolderChange('ARCHIVED')}>
                <ListItemIcon><ArchiveIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Archived" sx={{ color: '#202124' }} />
              </ListItem>
              <ListItem button selected={currentFolder === 'CATEGORIES'} onClick={() => handleFolderChange('CATEGORIES')}>
                <ListItemIcon><CategoryIcon sx={{ color: '#5f6368' }} /></ListItemIcon>
                <ListItemText primary="Categories" sx={{ color: '#202124' }} />
              </ListItem>
            </List>
            <Divider />
            {/* Add more custom labels or sections if needed */}
          </Box>

          {/* Email List */}
          <Box width="35%" overflowY="auto" pr={2} borderRight="1px solid #dadce0" bgcolor="white">
            <Typography variant="subtitle1" sx={{ p: 2, color: '#202124', textAlign: 'center' }}>
              {currentFolder} ({emails.length})
            </Typography>
            <List disablePadding>
              {emails.map((email, index) => (
                <ListItem
                  ref={emails.length === index + 1 ? lastEmailRef : null}
                  key={email.id}
                  button
                  selected={selectedEmail?.id === email.id}
                  onClick={() => handleEmailSelect(email)}
                  sx={{
                    py: 1.5,
                    borderBottom: '1px solid #f1f3f4',
                    '&:hover': { bgcolor: '#f2f2f2' },
                    '&.Mui-selected': { bgcolor: '#d2e3fc' },
                  }}
                >
                  <ListItemIcon>
                    <Avatar sx={{ width: 40, height: 40, bgcolor: '#e8f0fe', color: '#1967d2' }}>
                      {email.from_name ? email.from_name[0] : <Person />}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={email.subject}
                    secondary={`${email.from_name || email.from_address} • ${formatTimeAgo(email.received_at)}`}
                    primaryTypographyProps={{
                      noWrap: true,
                      fontWeight: email.is_unread ? "bold" : "normal",
                      color: '#202124',
                    }}
                    secondaryTypographyProps={{ noWrap: true, color: '#5f6368' }}
                  />
                </ListItem>
              ))}
            </List>
            {listLoading && <Box display="flex" justifyContent="center" p={2}><CircularProgress size={24} /></Box>}
            {emails.length === 0 && <Typography sx={{ p: 2, color: '#5f6368' }}>No emails</Typography>}
          </Box>

          {/* Email Viewer */}
          <Box flexGrow={1} p={3} overflowY="auto" bgcolor="white">
            {selectedEmail ? (
              <EmailReader email={selectedEmail} />
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
    </ThemeProvider>
  );
};

export default MailDashboard;