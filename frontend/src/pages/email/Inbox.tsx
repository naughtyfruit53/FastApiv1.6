/**
 * Email Inbox Component
 * Displays email list with search, filtering, and pagination
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Avatar,
  Chip,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  CircularProgress,
  Alert,
  Divider,
  IconButton,
  Menu,
  MenuList,
  ListItemAvatar,
  Skeleton
} from '@mui/material';
import {
  Email as EmailIcon,
  Inbox as InboxIcon,
  Send as SentIcon,
  Archive as ArchiveIcon,
  Delete as DeleteIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  AttachFile as AttachmentIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMailAccounts, getEmails, updateEmailStatus, triggerSync, Email, MailAccount, EmailListResponse } from '../../services/emailService';
import OAuthLoginButton from '../../components/OAuthLoginButton';
import EmailSelector from '../../components/email/EmailSelector'; // Assuming this component exists

interface InboxProps {
  selectedAccount?: MailAccount;
  onEmailSelect?: (email: Email) => void;
  onThreadSelect?: (threadId: number) => void;
  onCompose?: () => void;
  onAccountSelect?: (accountId: number) => void;
}

const Inbox: React.FC<InboxProps> = ({
  selectedAccount,
  onEmailSelect,
  onThreadSelect,
  onCompose,
  onAccountSelect
}) => {
  const [currentFolder, setCurrentFolder] = useState('INBOX');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(25);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuEmailId, setMenuEmailId] = useState<number | null>(null);

  const queryClient = useQueryClient();

  // Fetch mail accounts
  const { data: accounts = [], isLoading: accountsLoading } = useQuery({
    queryKey: ['mail-accounts'],
    queryFn: getMailAccounts
  });

  // Fetch emails for selected account
  const { 
    data: emailsData,
    isLoading: emailsLoading,
    error: emailsError
  } = useQuery({
    queryKey: ['emails', selectedAccount?.id, currentFolder, page, statusFilter],
    queryFn: () => selectedAccount 
      ? getEmails(
          selectedAccount.id,
          currentFolder,
          pageSize,
          (page - 1) * pageSize,
          statusFilter || undefined
        )
      : Promise.resolve({
          emails: [],
          total_count: 0,
          offset: 0,
          limit: pageSize,
          has_more: false,
          folder: currentFolder
        } as EmailListResponse),
    enabled: !!selectedAccount
  });

  // Update email status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ emailId, new_status }: { emailId: number; new_status: Email['status'] }) =>
      updateEmailStatus(emailId, new_status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] });
    }
  });

  // Trigger sync mutation
  const syncMutation = useMutation({
    mutationFn: (accountId: number) => triggerSync(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] });
    }
  });

  const handleEmailClick = (email: Email) => {
    // Mark as read if unread
    if (email.status === 'unread') {
      updateStatusMutation.mutate({ emailId: email.id, new_status: 'read' });
    }
    
    // Navigate to thread view if part of thread, otherwise email detail
    if (email.thread_id && onThreadSelect) {
      onThreadSelect(email.thread_id);
    } else if (onEmailSelect) {
      onEmailSelect(email);
    }
  };

  const handleToggleStar = (emailId: number, isFlagged: boolean) => {
    updateStatusMutation.mutate({
      emailId,
      new_status: isFlagged ? 'read' : 'flagged'
    });
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, emailId: number) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setMenuEmailId(emailId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuEmailId(null);
  };

  const handleArchive = (emailId: number) => {
    updateStatusMutation.mutate({ emailId, new_status: 'archived' });
    handleMenuClose();
  };

  const handleDelete = (emailId: number) => {
    updateStatusMutation.mutate({ emailId, new_status: 'deleted' });
    handleMenuClose();
  };

  const handleSync = () => {
    if (selectedAccount) {
      syncMutation.mutate(selectedAccount.id);
    }
  };

  const formatEmailDate = (dateString: string) => {
    const localDate = new Date(dateString);
  
    // Format as 'MM/DD/YYYY hh:mm A' (e.g., '02/24/2025 3:29 PM')
    const formatted = localDate.toLocaleString('en-US', {
      month: '2-digit',
      day: '2-digit',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  
    return formatted;
  };

  const getEmailPreview = (email: Email) => {
    const text = email.body_text || email.body_html?.replace(/<[^>]*>/g, '') || '';
    return text.substring(0, 100) + (text.length > 100 ? '...' : '');
  };

  const folders = [
    { key: 'INBOX', label: 'Inbox', icon: <InboxIcon /> },
    { key: 'SENT', label: 'Sent', icon: <SentIcon /> },
    { key: 'ARCHIVED', label: 'Archived', icon: <ArchiveIcon /> },
    { key: 'DELETED', label: 'Trash', icon: <DeleteIcon /> },
  ];

  // Show OAuth login if no accounts
  if (!accountsLoading && accounts.length === 0) {
    return (
      <Card sx={{ m: 2, p: 3, textAlign: 'center' }}>
        <CardContent>
          <EmailIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Connect Your Email Account
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Get started by connecting your email account to send and receive messages directly from TritIQ.
          </Typography>
          <OAuthLoginButton onError={(error) => console.error('OAuth Error:', error)} />
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ display: 'flex', height: '100%' }}>
      {/* Sidebar with folders */}
      <Box sx={{ width: 240, borderRight: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Box sx={{ p: 2 }}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<AddIcon />}
            onClick={onCompose}
            sx={{ mb: 2 }}
          >
            Compose
          </Button>
        </Box>

        <List dense>
          {folders.map((folder) => (
            <ListItem key={folder.key} disablePadding>
              <ListItemButton
                selected={currentFolder === folder.key}
                onClick={() => setCurrentFolder(folder.key)}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {folder.icon}
                </ListItemIcon>
                <ListItemText primary={folder.label} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        <Divider sx={{ my: 1 }} />

        {/* Account selector */}
        <Box sx={{ p: 2 }}>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
            Email Accounts
          </Typography>
          {accountsLoading ? (
            <Skeleton variant="rectangular" height={40} />
          ) : (
            <EmailSelector 
              accounts={accounts}
              onSelect={onAccountSelect!}
            />
          )}
        </Box>
      </Box>

      {/* Main email list */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Toolbar */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
            <TextField
              size="small"
              placeholder="Search emails..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />
              }}
              sx={{ flexGrow: 1 }}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Filter</InputLabel>
              <Select
                value={statusFilter}
                label="Filter"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="unread">Unread</MenuItem>
                <MenuItem value="flagged">Flagged</MenuItem>
                <MenuItem value="has_attachments">With Attachments</MenuItem>
              </Select>
            </FormControl>
            <IconButton 
              onClick={handleSync}
              disabled={syncMutation.isPending || !selectedAccount}
              title="Sync emails"
            >
              {syncMutation.isPending ? <CircularProgress size={20} /> : <RefreshIcon />}
            </IconButton>
          </Box>
        </Box>

        {/* Email list */}
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {emailsLoading ? (
            <Box sx={{ p: 2 }}>
              {Array.from({ length: 10 }).map((_, index) => (
                <Box key={index} sx={{ mb: 1 }}>
                  <Skeleton variant="rectangular" height={80} />
                </Box>
              ))}
            </Box>
          ) : emailsError ? (
            <Alert severity="error" sx={{ m: 2 }}>
              Failed to load emails: {(emailsError as Error).message}
            </Alert>
          ) : !selectedAccount ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">
                Select an email account to view messages
              </Typography>
            </Box>
          ) : (
            <>
              <List dense>
                {emailsData?.emails.map((email) => (
                  <React.Fragment key={email.id}>
                    <ListItem disablePadding>
                      <ListItemButton
                        onClick={() => handleEmailClick(email)}
                        sx={{
                          bgcolor: email.status === 'unread' ? 'action.hover' : 'transparent',
                          '&:hover': { bgcolor: 'action.selected' }
                        }}
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: 'primary.main' }}>
                            {(email.from_name || email.from_address).charAt(0).toUpperCase()}
                          </Avatar>
                        </ListItemAvatar>
                        
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <Typography
                                variant="body2"
                                fontWeight={email.status === 'unread' ? 'bold' : 'normal'}
                                noWrap
                                sx={{ flex: 1, mr: 1 }}
                              >
                                {email.from_name || email.from_address}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {formatEmailDate(email.received_at)}
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography
                                variant="body2"
                                fontWeight={email.status === 'unread' ? 'bold' : 'normal'}
                                noWrap
                                sx={{ mb: 0.5 }}
                              >
                                {email.subject || '(No subject)'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary" noWrap>
                                {getEmailPreview(email)}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                                {email.has_attachments && (
                                  <AttachmentIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                                )}
                                {email.is_important && (
                                  <StarIcon sx={{ fontSize: 16, color: 'warning.main' }} />
                                )}
                                {email.labels?.map((label) => (
                                  <Chip key={label} label={label} size="small" variant="outlined" />
                                ))}
                              </Box>
                            </Box>
                          }
                        />

                        <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleStar(email.id, email.is_flagged);
                            }}
                          >
                            {email.is_flagged ? (
                              <StarIcon sx={{ color: 'warning.main' }} />
                            ) : (
                              <StarBorderIcon />
                            )}
                          </IconButton>
                          
                          <IconButton
                            size="small"
                            onClick={(e) => handleMenuClick(e, email.id)}
                          >
                            <MoreVertIcon />
                          </IconButton>
                        </Box>
                      </ListItemButton>
                    </ListItem>
                    <Divider component="li" />
                  </React.Fragment>
                ))}
              </List>

              {emailsData && emailsData.emails.length === 0 && (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <EmailIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Typography color="text.secondary">
                    No emails found in {currentFolder.toLowerCase()}
                  </Typography>
                </Box>
              )}

              {/* Pagination */}
              {emailsData && emailsData.total_count > pageSize && (
                <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
                  <Pagination
                    count={Math.ceil(emailsData.total_count / pageSize)}
                    page={page}
                    onChange={(_, newPage) => setPage(newPage)}
                    color="primary"
                  />
                </Box>
              )}
            </>
          )}
        </Box>
      </Box>

      {/* Context menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuList dense>
          <MenuItem onClick={() => menuEmailId && handleArchive(menuEmailId)}>
            <ArchiveIcon sx={{ mr: 1 }} /> Archive
          </MenuItem>
          <MenuItem onClick={() => menuEmailId && handleDelete(menuEmailId)}>
            <DeleteIcon sx={{ mr: 1 }} /> Delete
          </MenuItem>
        </MenuList>
      </Menu>
    </Box>
  );
};

export default Inbox;