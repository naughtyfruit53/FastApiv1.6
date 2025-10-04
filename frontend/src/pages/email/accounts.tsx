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
  Edit as EditIcon,
  Email as EmailIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMailAccounts, deleteMailAccount, MailAccount } from '../../services/emailService';
import { useRouter } from 'next/navigation';
import SyncStatus from './sync';
import EmailTemplates from './templates';

const EmailAccountSettings: React.FC = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<MailAccount | null>(null);

  // Fetch accounts
  const { data: accounts = [], isLoading: accountsLoading } = useQuery({
    queryKey: ['mailAccounts'],
    queryFn: getMailAccounts,
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

  if (accountsLoading) {
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
            {accounts.map((account, index) => (
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
                      aria-label="delete"
                      onClick={() => handleDeleteClick(account)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              </React.Fragment>
            ))}
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
    </Box>
  );
};

export default EmailAccountSettings;