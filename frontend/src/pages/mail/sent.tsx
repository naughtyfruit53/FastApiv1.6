// frontend/src/pages/mail/sent.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  Chip,
  Checkbox,
  IconButton,
  Card,
  CardContent,
  Toolbar,
  AppBar,
  Button,
  Menu,
  MenuItem,
  CircularProgress,
  Alert,
  Pagination,
  TextField,
  InputAdornment,
} from "@mui/material";
import {
  Send as SendIcon,
  AttachFile,
  Search,
  MoreVert,
  Delete,
  Archive,
  Forward,
  Refresh,
  FilterList,
  Edit,
} from "@mui/icons-material";
import { useRouter } from "next/router";
import api from "../../lib/api";

interface SentEmail {
  id: number;
  subject: string;
  to_addresses: string[];
  cc_addresses?: string[];
  bcc_addresses?: string[];
  sent_at: string;
  has_attachments: boolean;
  priority: "low" | "normal" | "high" | "urgent";
  snippet: string;
  status: "SENT" | "PENDING" | "FAILED";
}

const SentPage: React.FC = () => {
  const router = useRouter();
  const [emails, setEmails] = useState<SentEmail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEmails, setSelectedEmails] = useState<Set<number>>(new Set());
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedEmailId, setSelectedEmailId] = useState<number | null>(null);

  useEffect(() => {
    fetchSentEmails();
  }, [page, searchTerm]);

  const fetchSentEmails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/api/v1/mail/sent-emails', {
        params: { 
          page, 
          per_page: 20, 
          search: searchTerm || undefined,
          sort_by: 'sent_at', 
          sort_order: 'desc' 
        }
      });
      
      setEmails(response.data.emails);
      setTotalPages(response.data.total_pages);
    } catch (err: any) {
      console.error('Error fetching sent emails:', err);
      setError('Failed to load sent emails. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEmailSelect = (emailId: number) => {
    const newSelected = new Set(selectedEmails);
    if (newSelected.has(emailId)) {
      newSelected.delete(emailId);
    } else {
      newSelected.add(emailId);
    }
    setSelectedEmails(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedEmails.size === emails.length) {
      setSelectedEmails(new Set());
    } else {
      setSelectedEmails(new Set(emails.map(email => email.id)));
    }
  };

  const handleEmailClick = (email: SentEmail) => {
    router.push(`/mail/emails/${email.id}`);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, emailId: number) => {
    setAnchorEl(event.currentTarget);
    setSelectedEmailId(emailId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedEmailId(null);
  };

  const handleBulkAction = async (action: string) => {
    try {
      const emailIds = Array.from(selectedEmails);
      for (const id of emailIds) {
        if (action === 'delete') {
          await api.delete(`/api/v1/mail/sent-emails/${id}`);
        } else if (action === 'archive') {
          await api.put(`/api/v1/mail/sent-emails/${id}`, { status: 'ARCHIVED' });
        }
      }
      setSelectedEmails(new Set());
      fetchSentEmails();
    } catch (err: any) {
      console.error(`Error performing bulk action ${action}:`, err);
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "urgent": return "error";
      case "high": return "warning";
      case "normal": return "default";
      case "low": return "info";
      default: return "default";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "SENT": return "default";
      case "PENDING": return "warning";
      case "FAILED": return "error";
      default: return "default";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "SENT": return "Sent";
      case "PENDING": return "Pending";
      case "FAILED": return "Failed";
      default: return "Unknown";
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
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <SendIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Sent
          </Typography>
          <TextField
            size="small"
            placeholder="Search sent emails..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ mr: 2, width: 300 }}
          />
          <IconButton onClick={fetchSentEmails}>
            <Refresh />
          </IconButton>
          <IconButton>
            <FilterList />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Bulk Actions Toolbar */}
      {selectedEmails.size > 0 && (
        <AppBar position="static" color="secondary" elevation={0}>
          <Toolbar variant="dense">
            <Typography variant="body2" sx={{ mr: 2 }}>
              {selectedEmails.size} selected
            </Typography>
            <Button
              color="inherit"
              startIcon={<Archive />}
              onClick={() => handleBulkAction('archive')}
            >
              Archive
            </Button>
            <Button
              color="inherit"
              startIcon={<Delete />}
              onClick={() => handleBulkAction('delete')}
            >
              Delete
            </Button>
          </Toolbar>
        </AppBar>
      )}

      {/* Email List */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <Card>
          <CardContent sx={{ p: 0 }}>
            {/* Select All Header */}
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Checkbox
                checked={selectedEmails.size === emails.length && emails.length > 0}
                indeterminate={selectedEmails.size > 0 && selectedEmails.size < emails.length}
                onChange={handleSelectAll}
              />
              <Typography variant="body2" component="span" sx={{ ml: 1 }}>
                Select all
              </Typography>
            </Box>

            <List>
              {emails.map((email) => (
                <ListItem
                  key={email.id}
                  sx={{
                    borderBottom: 1,
                    borderColor: 'divider',
                    '&:hover': {
                      backgroundColor: 'action.selected',
                    },
                    cursor: 'pointer',
                  }}
                  onClick={() => handleEmailClick(email)}
                >
                  <ListItemIcon>
                    <Checkbox
                      checked={selectedEmails.has(email.id)}
                      onChange={(e) => {
                        e.stopPropagation();
                        handleEmailSelect(email.id);
                      }}
                    />
                  </ListItemIcon>

                  <ListItemIcon>
                    <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
                      <SendIcon />
                    </Avatar>
                  </ListItemIcon>

                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <Typography
                          variant="subtitle2"
                          sx={{
                            fontWeight: 'normal',
                            maxWidth: 300,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          To: {email.to_addresses.join(', ')}
                          {email.cc_addresses && email.cc_addresses.length > 0 && (
                            <span style={{ color: 'gray' }}> (CC: {email.cc_addresses.join(', ')})</span>
                          )}
                        </Typography>
                        {email.priority !== "normal" && (
                          <Chip
                            label={email.priority}
                            size="small"
                            color={getPriorityColor(email.priority) as any}
                          />
                        )}
                        <Chip
                          label={getStatusLabel(email.status)}
                          size="small"
                          color={getStatusColor(email.status) as any}
                          variant="outlined"
                        />
                        {email.has_attachments && (
                          <AttachFile sx={{ fontSize: 16, color: 'text.secondary' }} />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography
                          variant="body2"
                          sx={{ fontWeight: 'bold', mb: 0.5 }}
                        >
                          {email.subject}
                        </Typography>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            maxWidth: 500,
                          }}
                        >
                          {email.snippet}
                        </Typography>
                      </Box>
                    }
                  />

                  <ListItemSecondaryAction>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        {formatTimeAgo(email.sent_at)}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuClick(e, email.id)}
                      >
                        <MoreVert />
                      </IconButton>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>

            {emails.length === 0 && (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <SendIcon sx={{ fontSize: 48, color: 'text.secondary' }} />
                <Typography variant="h6" color="text.secondary">
                  No sent emails
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Emails you send will appear here.
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<Edit />}
                  onClick={() => router.push('/mail/compose')}
                  sx={{ mt: 2 }}
                >
                  Compose Email
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, newPage) => setPage(newPage)}
            color="primary"
          />
        </Box>
      )}

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => { handleMenuClose(); /* TODO: Resend */ }}>
          <SendIcon sx={{ mr: 1 }} />
          Resend
        </MenuItem>
        <MenuItem onClick={() => { handleMenuClose(); /* TODO: Forward */ }}>
          <Forward sx={{ mr: 1 }} />
          Forward
        </MenuItem>
        <MenuItem onClick={() => { handleMenuClose(); /* TODO: Archive */ }}>
          <Archive sx={{ mr: 1 }} />
          Archive
        </MenuItem>
        <MenuItem onClick={() => { handleMenuClose(); /* TODO: Delete */ }}>
          <Delete sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default SentPage;