'use client';

/**
 * Email Account Settings Page
 * Manage email accounts with multi-account support
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Add as AddIcon,
  Email as EmailIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMailAccounts, deleteMailAccount, MailAccount } from '../../services/emailService';
import userService from '../../services/userService'; // Changed to default import
import { useRouter } from 'next/navigation';
import SyncStatus from './sync';
import EmailTemplates from './templates';

const EmailAccountSettings: React.FC = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [reauthDialogOpen, setReauthDialogOpen] = useState(false);
  const [refreshDialogOpen, setRefreshDialogOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<MailAccount | null>(null);
  const [selectedTokenId, setSelectedTokenId] = useState<number | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);

  // Fetch accounts
  const { data: accounts = [], isLoading: accountsLoading } = useQuery({
    queryKey: ['mailAccounts'],
    queryFn: getMailAccounts,
  });

  // Fetch tokens
  const { data: tokens = [], isLoading: tokensLoading } = useQuery({
    queryKey: ['userTokens'],
    queryFn: userService.getUserTokens, // Changed to userService.method
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteMailAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mailAccounts'] });
      setDeleteDialogOpen(false);
      setSelectedAccount(null);
    },
  });

  // Refresh mutation
  const refreshMutation = useMutation({
    mutationFn: (tokenId: number) => userService.refreshToken(tokenId), // Changed to userService.method
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userTokens'] });
      setRefreshDialogOpen(false);
      setSelectedTokenId(null);
    },
  });

  const handleDeleteClick = (account: MailAccount) => {
    setSelectedAccount(account);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedAccount?.id) {
      deleteMutation.mutate(selectedAccount.id);
    }
  };

  const handleAddAccount = () => {
    // Navigate to OAuth connection page to add a new account
    router.push('/email/oauth');
  };

  const handleReauthClick = (account: MailAccount) => {
    // Find the token for this account
    const token = tokens.find(t => t.id === account.oauth_token_id);
    if (token && token.status === 'REFRESH_FAILED') {
      setSelectedProvider(token.provider);
      setReauthDialogOpen(true);
    }
  };

  const handleRefreshClick = (account: MailAccount) => {
    // Find the token for this account
    const token = tokens.find(t => t.id === account.oauth_token_id);
    if (token) {
      setSelectedTokenId(token.id);
      setRefreshDialogOpen(true);
    }
  };

  const handleReauthConfirm = () => {
    if (selectedProvider) {
      // Navigate to OAuth login for re-authorization
      router.push(`/email/oauth?provider=${selectedProvider}&reauth=true`);
    }
    setReauthDialogOpen(false);
  };

  const handleRefreshConfirm = () => {
    if (selectedTokenId) {
      refreshMutation.mutate(selectedTokenId);
    }
  };

  if (accountsLoading || tokensLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Email Account Settings
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddAccount}
        >
          Add Account
        </Button>
      </Box>

      {accounts.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <EmailIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No Email Accounts
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Add an email account to start managing your emails
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddAccount}
            sx={{ mt: 2 }}
          >
            Add Your First Account
          </Button>
        </Paper>
      ) : (
        <Paper>
          <List>
            {accounts.map((account, index) => {
              const token = tokens.find(t => t.id === account.oauth_token_id);
              const isFailed = token && token.status === 'REFRESH_FAILED';
              return (
                <React.Fragment key={account.id}>
                  {index > 0 && <Divider />}
                  <ListItem>
                    <ListItemText
                      primary={account.display_name || account.email_address}
                      secondary={
                        <>
                          <Typography component="span" variant="body2" color="text.primary">
                            {account.email_address}
                          </Typography>
                          {' — '}
                          {account.account_type?.toUpperCase()}
                          {account.sync_enabled ? ' (Sync Enabled)' : ' (Sync Disabled)'}
                        </>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        aria-label="refresh"
                        onClick={() => handleRefreshClick(account)}
                        color="primary"
                        sx={{ mr: 1 }}
                      >
                        <RefreshIcon />
                      </IconButton>
                      {isFailed && (
                        <IconButton
                          edge="end"
                          aria-label="reauthorize"
                          onClick={() => handleReauthClick(account)}
                          color="warning"
                          sx={{ mr: 1 }}
                        >
                          <RefreshIcon />
                        </IconButton>
                      )}
                      <IconButton
                        edge="end"
                        aria-label="delete"
                        onClick={() => handleDeleteClick(account)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                </React.Fragment>
              );
            })}
          </List>
        </Paper>
      )}

      <Divider sx={{ my: 4 }} />

      <SyncStatus />

      <Divider sx={{ my: 4 }} />

      <EmailTemplates />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Email Account</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the email account{' '}
            <strong>{selectedAccount?.email_address}</strong>?
            This action cannot be undone. All emails and settings associated with this account will be permanently removed.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Re-authorize Confirmation Dialog */}
      <Dialog
        open={reauthDialogOpen}
        onClose={() => setReauthDialogOpen(false)}
      >
        <DialogTitle>Re-authorize Email Account</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Your authentication token has expired or is invalid. Re-authorization is required to continue using this account.
          </Alert>
          <DialogContentText>
            This will redirect you to {selectedProvider?.toUpperCase()} to grant access again. Your existing data will remain intact.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReauthDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleReauthConfirm}
            color="primary"
            variant="contained"
          >
            Re-authorize
          </Button>
        </DialogActions>
      </Dialog>

      {/* Refresh Confirmation Dialog */}
      <Dialog
        open={refreshDialogOpen}
        onClose={() => setRefreshDialogOpen(false)}
      >
        <DialogTitle>Refresh Token</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to refresh this token? This will attempt to get a new access token using the refresh token.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRefreshDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleRefreshConfirm}
            color="primary"
            variant="contained"
            disabled={refreshMutation.isPending}
          >
            {refreshMutation.isPending ? 'Refreshing...' : 'Refresh'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EmailAccountSettings;