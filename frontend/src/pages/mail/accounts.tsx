// frontend/src/pages/mail/accounts.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { Add as AddIcon, Delete, Refresh } from '@mui/icons-material';
import { useOAuth } from "../../hooks/useOAuth";
import OAuthLoginButton from "../../components/OAuthLoginButton";
import { useRouter } from "next/router";

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

const AccountsPage: React.FC = () => {
  const { getUserTokens, revokeToken, refreshToken } = useOAuth();
  const [tokens, setTokens] = useState<UserEmailToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [setupOpen, setSetupOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedTokenId, setSelectedTokenId] = useState<number | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchTokens();
  }, []);

  const fetchTokens = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getUserTokens();
      setTokens(response);
    } catch (err: any) {
      setError(err.message || 'Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleRevoke = (tokenId: number) => {
    setSelectedTokenId(tokenId);
    setDeleteDialogOpen(true);
  };

  const confirmRevoke = async () => {
    if (selectedTokenId) {
      try {
        await revokeToken(selectedTokenId);
        fetchTokens();
      } catch (err) {
        setError('Failed to revoke account');
      }
    }
    setDeleteDialogOpen(false);
    setSelectedTokenId(null);
  };

  const handleRefresh = async (tokenId: number) => {
    try {
      await refreshToken(tokenId);
      fetchTokens();
    } catch (err) {
      setError('Failed to refresh token');
    }
  };

  const handleAddAccount = () => {
    setSetupOpen(true);
  };

  const handleBack = () => {
    router.back();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ flexGrow: 1 }}>
          Manage Email Accounts
        </Typography>
        <Button variant="outlined" onClick={handleBack} sx={{ mr: 2 }}>
          Back
        </Button>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddAccount}>
          Add Account
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {tokens.length === 0 ? (
        <Alert severity="info">
          No email accounts connected. Add an account to start.
        </Alert>
      ) : (
        <List>
          {tokens.map((token) => (
            <ListItem key={token.id} divider>
              <ListItemText
                primary={token.email_address}
                secondary={
                  <>
                    {token.provider.toUpperCase()} • {token.display_name} <br />
                    Status: {token.status} • Last sync: {token.last_sync_at || 'Never'}
                  </>
                }
              />
              <ListItemSecondaryAction>
                <IconButton onClick={() => handleRefresh(token.id)} title="Refresh Token">
                  <Refresh />
                </IconButton>
                <IconButton onClick={() => handleRevoke(token.id)} title="Revoke">
                  <Delete color="error" />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}

      <Dialog open={setupOpen} onClose={() => setSetupOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Add Email Account</DialogTitle>
        <DialogContent>
          <OAuthLoginButton variant="list" />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSetupOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Revoke</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to revoke this email account? This action cannot be undone.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button color="error" onClick={confirmRevoke}>Revoke</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AccountsPage;