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
} from "@mui/icons-material";
import { useRouter } from "next/router";
import api from "../../lib/api";
import { useAuth } from "../../context/AuthContext";
import { useOAuth } from "../../hooks/useOAuth";
import OAuthLoginButton from "../../components/OAuthLoginButton";
import EmailReader from "../../components/EmailReader";  // Assume this component exists for displaying email body

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
  const [recentEmails, setRecentEmails] = useState<RecentEmail[]>([]);
  const [emailTokens, setEmailTokens] = useState<UserEmailToken[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<RecentEmail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;

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

        // Fetch recent emails (assume API returns full details including body)
        const emailsResponse = await api.get('/mail/emails', {
          params: { page: 1, per_page: 20, sort_by: 'received_at', sort_order: 'desc' },  // Increased per_page for full inbox list
        });
        setRecentEmails(emailsResponse.data.emails);
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
          setRecentEmails([]);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [retryCount, logout, router, getUserTokens]);

  const handleNavigate = (path: string) => {
    router.push(path);
  };

  const handleEmailSelect = (email: RecentEmail) => {
    setSelectedEmail(email);
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
      case "SUCCESS": return "success";
      case "ERROR": return "error";
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
    <Box
      sx={{
        display: "flex",
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
      }}
    >
      {/* Left Sidebar: 10% width - Stacked tiles (stats) and quick actions */}
      <Box
        sx={{
          width: "10%",
          borderRight: 1,
          borderColor: "divider",
          overflowY: "auto",
          p: 2,
          bgcolor: "background.paper",
        }}
      >
        <Typography variant="h6" gutterBottom sx={{ textAlign: "center" }}>
          Quick View
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {/* Stacked Stats Tiles */}
          <Card>
            <CardContent sx={{ p: 1 }}>
              <Typography variant="body2" color="textSecondary">
                Total
              </Typography>
              <Typography variant="h6">{stats.total_emails}</Typography>
            </CardContent>
          </Card>
          <Card>
            <CardContent sx={{ p: 1 }}>
              <Typography variant="body2" color="textSecondary">
                Unread
              </Typography>
              <Typography variant="h6" color="warning.main">{stats.unread_emails}</Typography>
            </CardContent>
          </Card>
          <Card>
            <CardContent sx={{ p: 1 }}>
              <Typography variant="body2" color="textSecondary">
                Flagged
              </Typography>
              <Typography variant="h6">{stats.flagged_emails}</Typography>
            </CardContent>
          </Card>
          <Card>
            <CardContent sx={{ p: 1 }}>
              <Typography variant="body2" color="textSecondary">
                Today
              </Typography>
              <Typography variant="h6">{stats.today_emails}</Typography>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6" gutterBottom sx={{ textAlign: "center" }}>
            Actions
          </Typography>
          <Button variant="text" startIcon={<Inbox />} onClick={() => handleNavigate("/mail/inbox")} fullWidth>
            Inbox
          </Button>
          <Button variant="text" startIcon={<Send />} onClick={() => handleNavigate("/mail/sent")} fullWidth>
            Sent
          </Button>
          <Button variant="text" startIcon={<Drafts />} onClick={() => handleNavigate("/mail/drafts")} fullWidth>
            Drafts
          </Button>
          <Button variant="text" startIcon={<Archive />} onClick={() => handleNavigate("/mail/archived")} fullWidth>
            Archived
          </Button>
          <Button variant="text" startIcon={<Add />} onClick={() => handleNavigate("/mail/compose")} fullWidth>
            Compose
          </Button>
          <Button variant="text" startIcon={<Sync />} onClick={() => handleNavigate("/mail/sync")} fullWidth>
            Sync
          </Button>
        </Box>
      </Box>

      {/* Middle: 25% width - List of emails (inbox) */}
      <Box
        sx={{
          width: "25%",
          borderRight: 1,
          borderColor: "divider",
          overflowY: "auto",
          p: 2,
        }}
      >
        <Typography variant="h6" gutterBottom>
          Inbox
        </Typography>
        <List>
          {recentEmails.map((email) => (
            <ListItem
              key={email.id}
              button
              selected={selectedEmail?.id === email.id}
              onClick={() => handleEmailSelect(email)}
              sx={{
                mb: 1,
                borderRadius: 1,
                bgcolor: email.is_unread ? "action.hover" : "transparent",
              }}
            >
              <ListItemIcon>
                <Avatar sx={{ width: 32, height: 32 }}>
                  {email.from_name ? email.from_name[0] : <Person />}
                </Avatar>
              </ListItemIcon>
              <ListItemText
                primary={email.subject}
                secondary={`${email.from_name || email.from_address} • ${formatTimeAgo(email.received_at)}`}
                primaryTypographyProps={{
                  noWrap: true,
                  fontWeight: email.is_unread ? "bold" : "normal",
                }}
                secondaryTypographyProps={{ noWrap: true }}
              />
              {email.has_attachments && <AttachFile sx={{ fontSize: 16, mr: 1 }} />}
            </ListItem>
          ))}
        </List>
        {recentEmails.length === 0 && <Typography color="textSecondary">No emails</Typography>}
      </Box>

      {/* Right: Remaining screen - Email body */}
      <Box
        sx={{
          flexGrow: 1,
          p: 3,
          overflowY: "auto",
        }}
      >
        {selectedEmail ? (
          <EmailReader email={selectedEmail} />  // Use EmailReader component to show body
        ) : (
          <Box sx={{ textAlign: "center", mt: 10 }}>
            <Typography variant="h6" color="textSecondary">
              Select an email to view
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default MailDashboard;