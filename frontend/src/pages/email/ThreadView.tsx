/**
 * Email Thread View Component
 * Displays email conversations with reply functionality
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Divider,
  Avatar,
  Chip,
  Button,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Alert,
  Skeleton,
  Snackbar
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Reply as ReplyIcon,
  ReplyAll as ReplyAllIcon,
  Forward as ForwardIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  AttachFile as AttachmentIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as emailService from '../../services/emailService';
import { apiClient as api } from '../../services/api/client';

interface ThreadViewProps {
  threadId?: number;
  initialEmail?: emailService.Email;
  onBack?: () => void;
  onReply?: (email: emailService.Email) => void;
  onReplyAll?: (email: emailService.Email) => void;
  onForward?: (email: emailService.Email) => void;
}

const ThreadView: React.FC<ThreadViewProps> = ({
  threadId,
  initialEmail,
  onBack,
  onReply,
  onReplyAll,
  onForward
}) => {
  const [expandedEmails, setExpandedEmails] = useState<Set<number>>(new Set());
  const [showImagesToast, setShowImagesToast] = useState(true);
  const [loadImages, setLoadImages] = useState(false);
  const queryClient = useQueryClient();

  // Fetch thread details if threadId provided
  const { 
    data: thread,
    isLoading: threadLoading,
    error: threadError
  } = useQuery({
    queryKey: ['email-thread', threadId],
    queryFn: () => threadId ? emailService.getEmailThread(threadId) : Promise.resolve(null),
    enabled: !!threadId
  });

  // Fetch thread emails if threadId provided
  const { 
    data: fetchedEmails = [],
    isLoading: emailsLoading,
    error: emailsError
  } = useQuery({
    queryKey: ['thread-emails', threadId],
    queryFn: async () => {
      if (!threadId) return [];
      const response = await api.get(`/email/threads/${threadId}/emails`);
      return response.data;
    },
    enabled: !!threadId
  });

  // Use initialEmail if no threadId
  const emails = threadId ? fetchedEmails : (initialEmail ? [initialEmail] : []);

  // Use thread data or derive from single email
  const effectiveThread = thread || (initialEmail ? {
    id: initialEmail.id,
    subject: initialEmail.subject,
    participants: [initialEmail.from_address, ...initialEmail.to_addresses.map(a => a.email)],
    message_count: 1,
    unread_count: initialEmail.status === 'unread' ? 1 : 0,
    has_attachments: initialEmail.has_attachments,
    status: initialEmail.status,
    priority: initialEmail.priority,
  } : null);

  // Update email status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ emailId, status }: { emailId: number; status: emailService.Email['status'] }) =>
      emailService.updateEmailStatus(emailId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['email-thread'] });
      queryClient.invalidateQueries({ queryKey: ['thread-emails'] });
      queryClient.invalidateQueries({ queryKey: ['emails'] });
    }
  });

  React.useEffect(() => {
    if (emails.length > 0) {
      // Expand all emails by default
      const allIds = new Set(emails.map(e => e.id));
      setExpandedEmails(allIds);
      
      // Mark all unread as read
      emails.forEach(email => {
        if (email.status === 'unread') {
          updateStatusMutation.mutate({ emailId: email.id, status: 'read' });
        }
      });
    }
  }, [emails.map(e => e.id).join(',')]);  // Depend on email IDs

  const handleToggleExpand = (emailId: number) => {
    const newExpanded = new Set(expandedEmails);
    if (newExpanded.has(emailId)) {
      newExpanded.delete(emailId);
    } else {
      newExpanded.add(emailId);
      // Mark as read when expanded
      const email = emails.find(e => e.id === emailId);
      if (email && email.status === 'unread') {
        updateStatusMutation.mutate({ emailId, status: 'read' });
      }
    }
    setExpandedEmails(newExpanded);
  };

  const handleToggleStar = (emailId: number, isFlagged: boolean) => {
    updateStatusMutation.mutate({
      emailId,
      status: isFlagged ? 'read' : 'flagged'
    });
  };

  const handleDownloadAttachment = async (attachment: emailService.EmailAttachment) => {
    try {
      await emailService.downloadAttachment(attachment.id);
      console.log('Download triggered for:', attachment.filename);
    } catch (error) {
      console.error('Failed to download attachment:', error);
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

  const handleLoadImages = () => {
    setLoadImages(true);
    setShowImagesToast(false);
  };

  const renderEmailContent = (email: emailService.Email) => {
    const isExpanded = expandedEmails.has(email.id);
    
    // Process HTML for images: if not loading, remove src; else load
    const processedHtml = loadImages 
      ? email.body_html 
      : email.body_html?.replace(/<img[^>]*src=["']([^"']+)["'][^>]*>/gi, '<img alt="Image blocked for security" style="opacity:0.5">');

    return (
      <Card key={email.id} sx={{ mb: 1, border: 1, borderColor: 'divider' }}>
        <CardContent sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
              <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                {(email.from_name || email.from_address).charAt(0).toUpperCase()}
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" fontWeight={email.status === 'unread' ? 'bold' : 'normal'}>
                  {email.from_name || email.from_address}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatEmailDate(email.received_at)}
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <IconButton
                size="small"
                onClick={() => handleToggleStar(email.id, email.is_flagged)}
              >
                {email.is_flagged ? (
                  <StarIcon sx={{ color: 'warning.main' }} />
                ) : (
                  <StarBorderIcon />
                )}
              </IconButton>
              
              <IconButton
                size="small"
                onClick={() => handleToggleExpand(email.id)}
              >
                {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
          </Box>

          <Collapse in={isExpanded}>
            <Divider sx={{ my: 1 }} />
            
            {/* Email metadata */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" fontWeight="bold" gutterBottom>
                {email.subject}
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, mb: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  <strong>From:</strong> {email.from_name ? `${email.from_name} <${email.from_address}>` : email.from_address}
                </Typography>
                
                <Typography variant="caption" color="text.secondary">
                  <strong>To:</strong> {email.to_addresses.map(addr => 
                    addr.name ? `${addr.name} <${addr.email}>` : addr.email
                  ).join(', ')}
                </Typography>
                
                {email.cc_addresses?.length > 0 && (
                  <Typography variant="caption" color="text.secondary">
                    <strong>CC:</strong> {email.cc_addresses.map(addr => 
                      addr.name ? `${addr.name} <${addr.email}>` : addr.email
                    ).join(', ')}
                  </Typography>
                )}
                
                <Typography variant="caption" color="text.secondary">
                  <strong>Date:</strong> {formatEmailDate(email.received_at)}
                </Typography>
              </Box>

              {/* Priority and flags */}
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                {email.priority !== 'normal' && (
                  <Chip 
                    label={email.priority} 
                    size="small" 
                    color={email.priority === 'high' || email.priority === 'urgent' ? 'error' : 'default'}
                  />
                )}
                {email.is_important && (
                  <Chip label="Important" size="small" color="warning" />
                )}
                {email.labels?.map((label) => (
                  <Chip key={label} label={label} size="small" variant="outlined" />
                ))}
              </Box>
            </Box>

            {/* Attachments */}
            {email.attachments?.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" fontWeight="bold" gutterBottom>
                  <AttachmentIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
                  Attachments ({email.attachments.length})
                </Typography>
                
                <List dense>
                  {email.attachments.map((attachment) => (
                    <ListItem 
                      key={attachment.id}
                      sx={{ 
                        border: 1, 
                        borderColor: 'divider', 
                        borderRadius: 1, 
                        mb: 0.5,
                        bgcolor: attachment.is_quarantined ? 'error.light' : 'background.paper'
                      }}
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'primary.main', width: 24, height: 24 }}>
                          <AttachmentIcon sx={{ fontSize: 14 }} />
                        </Avatar>
                      </ListItemAvatar>
                      
                      <ListItemText
                        primary={attachment.filename}
                        secondary={
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              {attachment.size_bytes ? `${Math.round(attachment.size_bytes / 1024)} KB` : ''} • 
                              {attachment.content_type || 'Unknown type'}
                            </Typography>
                            {attachment.is_quarantined && (
                              <Chip label="Quarantined" size="small" color="error" sx={{ ml: 1 }} />
                            )}
                          </Box>
                        }
                      />
                      
                      {!attachment.is_quarantined && (
                        <IconButton 
                          size="small" 
                          onClick={() => handleDownloadAttachment(attachment)}
                          title="Download attachment"
                        >
                          <DownloadIcon />
                        </IconButton>
                      )}
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* Email content */}
            <Box sx={{ mb: 2 }}>
              {email.body_html ? (
                <div 
                  dangerouslySetInnerHTML={{ __html: processedHtml }}
                  style={{
                    maxWidth: '100%',
                    overflow: 'hidden',
                    wordWrap: 'break-word'
                  }}
                />
              ) : (
                <Typography 
                  variant="body2" 
                  component="pre"
                  sx={{ 
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'inherit',
                    wordWrap: 'break-word'
                  }}
                >
                  {email.body_text || '(No content)'}
                </Typography>
              )}
            </Box>

            {/* Action buttons */}
            <Box sx={{ display: 'flex', gap: 1, pt: 1, borderTop: 1, borderColor: 'divider' }}>
              <Button
                size="small"
                startIcon={<ReplyIcon />}
                onClick={() => onReply?.(email)}
                variant="outlined"
              >
                Reply
              </Button>
              
              <Button
                size="small"
                startIcon={<ReplyAllIcon />}
                onClick={() => onReplyAll?.(email)}
                variant="outlined"
                disabled={!email.to_addresses || email.to_addresses.length <= 1}
              >
                Reply All
              </Button>
              
              <Button
                size="small"
                startIcon={<ForwardIcon />}
                onClick={() => onForward?.(email)}
                variant="outlined"
              >
                Forward
              </Button>
            </Box>
          </Collapse>
        </CardContent>
      </Card>
    );
  };

  if (threadLoading || emailsLoading) {
    return (
      <Box sx={{ p: 2 }}>
        <Skeleton variant="rectangular" height={60} sx={{ mb: 2 }} />
        {Array.from({ length: 3 }).map((_, index) => (
          <Skeleton key={index} variant="rectangular" height={200} sx={{ mb: 2 }} />
        ))}
      </Box>
    );
  }

  if (threadError || emailsError) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">
          Failed to load email thread: {(threadError as Error)?.message || (emailsError as Error)?.message}
        </Alert>
      </Box>
    );
  }

  if (emails.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">
          No emails to display
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton onClick={onBack} sx={{ mr: 1 }}>
              <BackIcon />
            </IconButton>
            
            <Box>
              <Typography variant="h6" noWrap>
                {effectiveThread?.subject || 'Email Thread'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {effectiveThread?.message_count || emails.length} messages • {effectiveThread?.participants.join(', ')}
              </Typography>
            </Box>
          </Box>

          {effectiveThread && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              {effectiveThread.unread_count > 0 && (
                <Chip 
                  label={`${effectiveThread.unread_count} unread`} 
                  size="small" 
                  color="primary" 
                />
              )}
              {effectiveThread.has_attachments && (
                <Chip 
                  label="Has attachments" 
                  size="small" 
                  variant="outlined"
                  icon={<AttachmentIcon />}
                />
              )}
            </Box>
          )}
        </Box>
      </Box>

      {/* Email list */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {emails.map(email => renderEmailContent(email))}
      </Box>

      {/* Images Toast */}
      <Snackbar
        open={showImagesToast}
        autoHideDuration={null}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          severity="info"
          action={
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button color="inherit" size="small" onClick={handleLoadImages}>
                Display images
              </Button>
              <Button color="inherit" size="small" onClick={() => setShowImagesToast(false)}>
                Dismiss
              </Button>
            </Box>
          }
          sx={{ width: '100%' }}
        >
          This email contains remote images. Display images from this sender?
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ThreadView;