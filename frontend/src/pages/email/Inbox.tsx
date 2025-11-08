/**
 * Email Inbox Component
 * Displays email list with search, filtering, and pagination
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Avatar,
  Chip,
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
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  AttachFile as AttachmentIcon,
  MoreVert as MoreVertIcon,
  Archive as ArchiveIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getEmails, updateEmailStatus, triggerSync, Email, MailAccount, EmailListResponse } from '../../services/emailService';
import { ProtectedPage } from '../../components/ProtectedPage';

interface InboxProps {
  selectedAccount?: MailAccount;
  onEmailSelect?: (email: Email) => void;
  onThreadSelect?: (threadId: number) => void;
  onCompose?: () => void;
  onAccountSelect?: (accountId: number) => void;
  currentFolder: string;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  statusFilter: string;
  setStatusFilter: (filter: string) => void;
  page: number;
  setPage: (page: number) => void;
}

const Inbox: React.FC<InboxProps> = ({
  selectedAccount,
  onEmailSelect,
  onThreadSelect,
  searchTerm,
  setSearchTerm,
  statusFilter,
  setStatusFilter,
  page,
  setPage,
  currentFolder
}) => {
  const pageSize = 25;
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuEmailId, setMenuEmailId] = useState<number | null>(null);

  const queryClient = useQueryClient();

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
    const date = new Date(dateString);
    // Format as dd/mm/yyyy HH:MM AM/PM in user's timezone
    return new Intl.DateTimeFormat('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }).format(date);
  };

  const getEmailPreview = (email: Email) => {
    const text = email.body_text || email.body_html?.replace(/<[^>]*>/g, '') || '';
    return text.substring(0, 100) + (text.length > 100 ? '...' : '');
  };

  return (
    <ProtectedPage moduleKey="email" action="read">
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
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
                              {email.subject}
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
    </ProtectedPage>
  );
};

export default Inbox;