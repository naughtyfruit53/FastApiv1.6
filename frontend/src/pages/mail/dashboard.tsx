// frontend/src/pages/mail/dashboard.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Button,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Avatar,
  Badge,
  Modal,
  TextField,
  FormControlLabel,
  Switch,
} from "@mui/material";
import {
  Email,
  Dashboard,
  Inbox,
  Send,
  Drafts,
  Flag,
  Today,
  AttachFile,
  Person,
  Add,
  Sync,
  MarkEmailRead,
  MarkEmailUnread,
  Archive,
  Settings,
  Close,
} from "@mui/icons-material";
import { useRouter } from "next/router";
import api from "../../lib/api";
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
}
interface EmailAccount {
  id: number;
  name: string;
  email_address: string;
  unread_count: number;
  sync_status: "success" | "error" | "syncing";
  last_sync: string;
}
const MailDashboard: React.FC = () => {
  const router = useRouter();
  const [stats, setStats] = useState<MailStats | null>(null);
  const [recentEmails, setRecentEmails] = useState<RecentEmail[]>([]);
  const [emailAccounts, setEmailAccounts] = useState<EmailAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEmailConfigModal, setShowEmailConfigModal] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch mail dashboard stats
        const statsResponse = await api.get('/mail/dashboard');
        setStats(statsResponse.data);

        // Fetch recent emails
        const emailsResponse = await api.get('/emails', {
          params: { page: 1, per_page: 5, sort_by: 'received_at', sort_order: 'desc' },
        });
        setRecentEmails(emailsResponse.data.emails);

        // Fetch email accounts
        const accountsResponse = await api.get('/accounts');
        setEmailAccounts(accountsResponse.data.map((account: any) => ({
          id: account.id,
          name: account.name,
          email_address: account.email_address,
          unread_count: account.unread_count,
          sync_status: account.last_sync_status || 'success',
          last_sync: account.last_sync_at || new Date().toISOString(),
        })));
      } catch (error: any) {
        console.error('Error fetching mail dashboard data:', error);
        const errorMessage = error.response?.status === 401
          ? 'Authentication failed. Please log in again.'
          : error.response?.status === 500
          ? 'Server error. Please try again later.'
          : error.response?.status === 404
          ? 'Endpoint not found. Check API URL configuration.'
          : `Failed to load mail dashboard data: ${error.message || 'Unknown error'}`;
        setError(errorMessage);

        if (retryCount < maxRetries) {
          setTimeout(() => {
            setRetryCount(retryCount + 1);
          }, 2000);
        } else {
          // Fallback to empty data
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
          setRecentEmails([]);
          setEmailAccounts([]);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [retryCount]);

  const handleNavigate = (path: string) => {
    router.push(path);
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "urgent": return "error";
      case "high": return "warning";
      case "normal": return "default";
      case "low": return "info";
      default: return "default";
    }
  };

  const getSyncStatusColor = (status: string) => {
    switch (status) {
      case "success": return "success";
      case "error": return "error";
      case "syncing": return "warning";
      default: return "default";
    }
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

  if (!stats) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">No mail data available</Alert>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        p: 3,
        opacity: 0,
        animation: "fadeInUp 0.6s ease-out forwards",
        "@keyframes fadeInUp": {
          from: { opacity: 0, transform: "translateY(30px)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 4,
          pb: 2,
          borderBottom: "1px solid",
          borderColor: "divider",
          position: "relative",
          "&::after": {
            content: '""',
            position: "absolute",
            bottom: "-1px",
            left: 0,
            width: "60px",
            height: "3px",
            background: "linear-gradient(90deg, primary.main, primary.light)",
            borderRadius: "2px",
          },
        }}
      >
        <Typography
          variant="h4"
          component="h1"
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            fontWeight: "bold",
            color: "text.primary",
          }}
        >
          <Dashboard color="primary" />
          Mail Dashboard
        </Typography>
        <Box sx={{ display: "flex", gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Sync />}
            onClick={() => handleNavigate("/mail/sync")}
            sx={{
              borderRadius: 2,
              transition: "all 0.2s ease-in-out",
              "&:hover": {
                transform: "translateY(-2px)",
                boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
              },
            }}
          >
            Sync Mail
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleNavigate("/mail/compose")}
          >
            Compose
          </Button>
        </Box>
      </Box>
      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Emails
                  </Typography>
                  <Typography variant="h5">{stats.total_emails.toLocaleString()}</Typography>
                </Box>
                <Email color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Unread
                  </Typography>
                  <Typography variant="h5" color="warning.main">{stats.unread_emails}</Typography>
                </Box>
                <Badge badgeContent={stats.unread_emails} color="warning">
                  <MarkEmailUnread color="warning" sx={{ fontSize: 40 }} />
                </Badge>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Flagged
                  </Typography>
                  <Typography variant="h5">{stats.flagged_emails}</Typography>
                </Box>
                <Flag color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Today's Emails
                  </Typography>
                  <Typography variant="h5">{stats.today_emails}</Typography>
                </Box>
                <Today color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Main Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography
                variant="h6"
                gutterBottom
                sx={{ display: "flex", alignItems: "center", gap: 1 }}
              >
                <Inbox color="primary" />
                Recent Emails
              </Typography>
              <List>
                {recentEmails.map((email, index) => (
                  <React.Fragment key={email.id}>
                    <ListItem
                      sx={{
                        cursor: "pointer",
                        borderRadius: 1,
                        backgroundColor: email.is_unread ? "action.hover" : "transparent",
                        "&:hover": { backgroundColor: "action.selected" },
                      }}
                      onClick={() => handleNavigate(`/mail/emails/${email.id}`)}
                    >
                      <ListItemIcon>
                        <Avatar sx={{ bgcolor: "primary.main", width: 32, height: 32 }}>
                          {email.from_name ? email.from_name.charAt(0).toUpperCase() : <Person />}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
                            <Typography
                              variant="subtitle2"
                              sx={{ fontWeight: email.is_unread ? "bold" : "normal" }}
                            >
                              {email.subject}
                            </Typography>
                            {email.priority !== "normal" && (
                              <Chip
                                label={email.priority}
                                size="small"
                                color={getPriorityColor(email.priority) as any}
                              />
                            )}
                            {email.is_flagged && <Flag color="error" sx={{ fontSize: 16 }} />}
                            {email.has_attachments && <AttachFile sx={{ fontSize: 16 }} />}
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              From: {email.from_name || email.from_address}
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              {formatTimeAgo(email.received_at)}
                            </Typography>
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        {email.is_unread ? (
                          <MarkEmailUnread color="warning" />
                        ) : (
                          <MarkEmailRead color="disabled" />
                        )}
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < recentEmails.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
              {recentEmails.length === 0 && (
                <Box sx={{ textAlign: "center", py: 4 }}>
                  <Typography color="textSecondary">No recent emails</Typography>
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={() => handleNavigate("/mail/accounts")}
                    sx={{ mt: 2 }}
                  >
                    Setup Email Account
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Quick Actions
                  </Typography>
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 2 }}>
                    <Button
                      variant="outlined"
                      startIcon={<Inbox />}
                      onClick={() => handleNavigate("/mail/inbox")}
                      fullWidth
                    >
                      View Inbox
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Send />}
                      onClick={() => handleNavigate("/mail/sent")}
                      fullWidth
                    >
                      Sent Items
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Drafts />}
                      onClick={() => handleNavigate("/mail/drafts")}
                      fullWidth
                    >
                      Drafts ({stats.draft_emails})
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Archive />}
                      onClick={() => handleNavigate("/mail/archived")}
                      fullWidth
                    >
                      Archived
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">Email Accounts</Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<Settings />}
                        onClick={() => setShowEmailConfigModal(true)}
                      >
                        Manual Setup
                      </Button>
                    </Box>
                  </Box>
                  <List dense>
                    {emailAccounts.map((account) => (
                      <ListItem
                        key={account.id}
                        sx={{ borderRadius: 1, mb: 1, border: "1px solid", borderColor: "divider" }}
                      >
                        <ListItemIcon>
                          <Avatar sx={{ bgcolor: getSyncStatusColor(account.sync_status) + ".main", width: 32, height: 32 }}>
                            <Email />
                          </Avatar>
                        </ListItemIcon>
                        <ListItemText
                          primary={account.name}
                          secondary={
                            <Box>
                              <Typography variant="caption" display="block">{account.email_address}</Typography>
                              <Typography variant="caption" color="textSecondary">
                                Last sync: {formatTimeAgo(account.last_sync)}
                              </Typography>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Badge badgeContent={account.unread_count} color="warning">
                            <Inbox />
                          </Badge>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={() => handleNavigate("/mail/accounts/create")}
                    fullWidth
                    sx={{ mt: 1 }}
                  >
                    Add Account
                  </Button>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Mail Stats</Typography>
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                      <Typography variant="body2">Sent Emails</Typography>
                      <Typography variant="body2">{stats.sent_emails}</Typography>
                    </Box>
                    <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                      <Typography variant="body2">This Week</Typography>
                      <Typography variant="body2">{stats.this_week_emails}</Typography>
                    </Box>
                    <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                      <Typography variant="body2">Drafts</Typography>
                      <Typography variant="body2">{stats.draft_emails}</Typography>
                    </Box>
                    {stats.spam_emails > 0 && (
                      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                        <Typography variant="body2" color="error">Spam</Typography>
                        <Typography variant="body2" color="error">{stats.spam_emails}</Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      {/* Email Configuration Modal */}
      <Modal
        open={showEmailConfigModal}
        onClose={() => setShowEmailConfigModal(false)}
        aria-labelledby="email-config-modal"
      >
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 600,
            bgcolor: 'background.paper',
            boxShadow: 24,
            p: 4,
            borderRadius: 2,
            maxHeight: '90vh',
            overflow: 'auto',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">Add Email Account</Typography>
            <Button onClick={() => setShowEmailConfigModal(false)} sx={{ minWidth: 'auto', p: 1 }}>
              <Close />
            </Button>
          </Box>
          <Typography variant="h6" sx={{ mb: 2 }}>Manual Configuration</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Configure your email account manually using IMAP/SMTP settings:
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField fullWidth label="Account Name" placeholder="e.g., Work Email" helperText="A display name for this email account" />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Email Address" type="email" placeholder="user@example.com" />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Incoming Mail (IMAP) Settings</Typography>
            </Grid>
            <Grid item xs={8}>
              <TextField fullWidth label="IMAP Server" placeholder="imap.gmail.com" />
            </Grid>
            <Grid item xs={4}>
              <TextField fullWidth label="Port" type="number" defaultValue="993" />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel control={<Switch defaultChecked />} label="Use SSL/TLS" />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Outgoing Mail (SMTP) Settings</Typography>
            </Grid>
            <Grid item xs={8}>
              <TextField fullWidth label="SMTP Server" placeholder="smtp.gmail.com" />
            </Grid>
            <Grid item xs={4}>
              <TextField fullWidth label="Port" type="number" defaultValue="587" />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel control={<Switch defaultChecked />} label="Use SSL/TLS" />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Authentication</Typography>
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Username" placeholder="Usually your email address" />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Password" type="password" placeholder="Your email password or app password" />
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info" sx={{ mt: 2 }}>
                For Gmail and other modern email providers, you may need to use an "App Password" instead of your regular password.
                Check your email provider's documentation for details.
              </Alert>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
                <Button variant="outlined" onClick={() => setShowEmailConfigModal(false)}>
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  onClick={async () => {
                    try {
                      // TODO: Implement actual save logic by calling /api/v1/accounts endpoint
                      await api.post('/accounts', {
                        name: 'Work Email', // Replace with actual form data
                        email_address: 'user@example.com', // Replace with actual form data
                        imap_server: 'imap.gmail.com', // Replace with actual form data
                        imap_port: 993, // Replace with actual form data
                        smtp_server: 'smtp.gmail.com', // Replace with actual form data
                        smtp_port: 587, // Replace with actual form data
                        username: 'user@example.com', // Replace with actual form data
                        password: 'password', // Replace with actual form data
                      });
                      setShowEmailConfigModal(false);
                      fetchData();
                    } catch (error) {
                      console.error('Error saving email account:', error);
                      setError('Failed to save email account. Please try again.');
                    }
                  }}
                >
                  Save Account
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Modal>
    </Box>
  );
};
export default MailDashboard;