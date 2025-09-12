// frontend/src/pages/mail/inbox.tsx
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
  Inbox as InboxIcon,
  Star,
  StarBorder,
  AttachFile,
  Search,
  MoreVert,
  Delete,
  Archive,
  MarkEmailRead,
  MarkEmailUnread,
  Reply,
  Forward,
  Refresh,
  FilterList,
} from "@mui/icons-material";
import { useRouter } from "next/router";
import api from "../../lib/api";

interface Email {
  id: string;
  subject: string;
  from_address: string;
  from_name?: string;
  received_at: string;
  is_read: boolean;
  is_flagged: boolean;
  has_attachments: boolean;
  priority: "low" | "normal" | "high" | "urgent";
  snippet: string;
}

interface EmailFolder {
  id: string;
  name: string;
  type: string;
}

const InboxPage: React.FC = () => {
  const router = useRouter();
  const [emails, setEmails] = useState<Email[]>([]);
  const [folders, setFolders] = useState<EmailFolder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEmails, setSelectedEmails] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState("");
  const [currentFolder, setCurrentFolder] = useState("INBOX");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);

  useEffect(() => {
    fetchEmails();
    fetchFolders();
  }, [currentFolder, page, searchTerm]);

  const fetchEmails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // For now, use mock data since backend endpoints might not be fully implemented
      const mockEmails: Email[] = [
        {
          id: "1",
          subject: "Quarterly Financial Report Q4 2024",
          from_address: "finance@company.com",
          from_name: "Finance Team",
          received_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          is_read: false,
          is_flagged: true,
          has_attachments: true,
          priority: "high",
          snippet: "Please find attached the quarterly financial report for Q4 2024. The results show strong performance across all divisions...",
        },
        {
          id: "2",
          subject: "Team Meeting - Project Status Update",
          from_address: "manager@company.com",
          from_name: "Project Manager",
          received_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          is_read: true,
          is_flagged: false,
          has_attachments: false,
          priority: "normal",
          snippet: "Hi team, we're scheduling a meeting to discuss the current project status and upcoming milestones...",
        },
        {
          id: "3",
          subject: "System Maintenance Notification",
          from_address: "noreply@company.com",
          from_name: "IT Department",
          received_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          is_read: true,
          is_flagged: false,
          has_attachments: false,
          priority: "normal",
          snippet: "This is to inform you that scheduled system maintenance will be performed this weekend...",
        },
      ];
      
      setEmails(mockEmails);
      setTotalPages(1);
    } catch (err: any) {
      console.error('Error fetching emails:', err);
      setError('Failed to load emails. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchFolders = async () => {
    try {
      // Mock folder data for now
      const mockFolders: EmailFolder[] = [
        { id: "INBOX", name: "Inbox", type: "inbox" },
        { id: "SENT", name: "Sent", type: "sent" },
        { id: "DRAFTS", name: "Drafts", type: "drafts" },
        { id: "SPAM", name: "Spam", type: "spam" },
        { id: "TRASH", name: "Trash", type: "trash" },
      ];
      setFolders(mockFolders);
    } catch (err: any) {
      console.error('Error fetching folders:', err);
    }
  };

  const handleEmailSelect = (emailId: string) => {
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

  const handleEmailClick = (email: Email) => {
    // Mark as read and navigate to email detail
    router.push(`/mail/emails/${email.id}`);
  };

  const handleStarToggle = async (emailId: string, starred: boolean) => {
    try {
      // TODO: Implement API call to toggle star
      console.log(`Toggling star for email ${emailId}: ${starred}`);
    } catch (err: any) {
      console.error('Error toggling star:', err);
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, emailId: string) => {
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
      console.log(`Performing bulk action ${action} on emails:`, emailIds);
      
      switch (action) {
        case 'delete':
          // TODO: Implement bulk delete API call
          break;
        case 'archive':
          // TODO: Implement bulk archive API call
          break;
        case 'markRead':
          // TODO: Implement bulk mark read API call
          break;
        case 'markUnread':
          // TODO: Implement bulk mark unread API call
          break;
      }
      
      setSelectedEmails(new Set());
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
          <InboxIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Inbox
          </Typography>
          <TextField
            size="small"
            placeholder="Search emails..."
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
          <IconButton onClick={fetchEmails}>
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
              startIcon={<MarkEmailRead />}
              onClick={() => handleBulkAction('markRead')}
            >
              Mark Read
            </Button>
            <Button
              color="inherit"
              startIcon={<MarkEmailUnread />}
              onClick={() => handleBulkAction('markUnread')}
            >
              Mark Unread
            </Button>
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
                    backgroundColor: email.is_read ? 'transparent' : 'action.hover',
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
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStarToggle(email.id, !email.is_flagged);
                      }}
                    >
                      {email.is_flagged ? <Star color="warning" /> : <StarBorder />}
                    </IconButton>
                  </ListItemIcon>

                  <ListItemIcon>
                    <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                      {email.from_name ? email.from_name.charAt(0).toUpperCase() : 'U'}
                    </Avatar>
                  </ListItemIcon>

                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <Typography
                          variant="subtitle2"
                          sx={{
                            fontWeight: email.is_read ? 'normal' : 'bold',
                            maxWidth: 200,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {email.from_name || email.from_address}
                        </Typography>
                        {email.priority !== "normal" && (
                          <Chip
                            label={email.priority}
                            size="small"
                            color={getPriorityColor(email.priority) as any}
                          />
                        )}
                        {email.has_attachments && (
                          <AttachFile sx={{ fontSize: 16, color: 'text.secondary' }} />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: email.is_read ? 'normal' : 'bold',
                            mb: 0.5,
                          }}
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
                        {formatTimeAgo(email.received_at)}
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
                <InboxIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  No emails in inbox
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  When you receive emails, they'll appear here.
                </Typography>
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
        <MenuItem onClick={() => { handleMenuClose(); /* TODO: Mark as read */ }}>
          <MarkEmailRead sx={{ mr: 1 }} />
          Mark as Read
        </MenuItem>
        <MenuItem onClick={() => { handleMenuClose(); /* TODO: Mark as unread */ }}>
          <MarkEmailUnread sx={{ mr: 1 }} />
          Mark as Unread
        </MenuItem>
        <MenuItem onClick={() => { handleMenuClose(); /* TODO: Reply */ }}>
          <Reply sx={{ mr: 1 }} />
          Reply
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

export default InboxPage;