// frontend/src/pages/mail/accounts.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Avatar,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  TextField,
  FormControlLabel,
  Switch,
  Divider,
  AppBar,
  Toolbar,
  Badge,
  Menu,
  MenuItem,
} from "@mui/material";
import {
  Add,
  Settings,
  Delete,
  Edit,
  Sync,
  Email,
  CheckCircle,
  Error,
  Warning,
  Refresh,
  MoreVert,
  Google as GoogleIcon,
  Microsoft as MicrosoftIcon,
} from "@mui/icons-material";
import { useRouter } from "next/router";
import api from "../../lib/api";
import OAuthLoginButton from "../../components/OAuthLoginButton";

interface EmailAccount {
  id: number;
  name: string;
  email_address: string;
  provider: string;
  display_name: string | null;
  sync_enabled: boolean;
  sync_folders: string[] | null;
  last_sync_at: string | null;
  last_sync_status: string | null;
  last_sync_error: string | null;
  unread_count: number;
  total_emails: number;
  status: "active" | "error" | "syncing" | "inactive";
  created_at: string;
  is_active: boolean;
}

interface SyncStats {
  total_accounts: number;
  active_accounts: number;
  last_sync: string | null;
  sync_errors: number;
}

const AccountsPage: React.FC = () => {
  const router = useRouter();
  const [accounts, setAccounts] = useState<EmailAccount[]>([]);
  const [syncStats, setSyncStats] = useState<SyncStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAccount, setSelectedAccount] = useState<EmailAccount | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuAccountId, setMenuAccountId] = useState<number | null>(null);
  const [syncing, setSyncing] = useState<{ [key: number]: boolean }>({});

  useEffect(() => {
    fetchAccounts();
    fetchSyncStats();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Mock data for email accounts
      const mockAccounts: EmailAccount[] = [
        {
          id: 1,
          name: "Primary Work Email",
          email_address: "john.doe@company.com",
          provider: "google",
          display_name: "John Doe",
          sync_enabled: true,
          sync_folders: ["INBOX", "SENT", "DRAFTS"],
          last_sync_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
          last_sync_status: "success",
          last_sync_error: null,
          unread_count: 15,
          total_emails: 1250,
          status: "active",
          created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          is_active: true,
        },
        {
          id: 2,
          name: "Support Email",
          email_address: "support@company.com",
          provider: "microsoft",
          display_name: "Support Team",
          sync_enabled: true,
          sync_folders: ["inbox", "sentitems"],
          last_sync_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          last_sync_status: "error",
          last_sync_error: "Authentication failed - token expired",
          unread_count: 5,
          total_emails: 892,
          status: "error",
          created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
          is_active: true,
        },
      ];
      
      setAccounts(mockAccounts);
    } catch (err: any) {
      console.error('Error fetching accounts:', err);
      setError('Failed to load email accounts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSyncStats = async () => {
    try {
      const mockStats: SyncStats = {
        total_accounts: 2,
        active_accounts: 1,
        last_sync: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
        sync_errors: 1,
      };
      setSyncStats(mockStats);
    } catch (err: any) {
      console.error('Error fetching sync stats:', err);
    }
  };

  const handleSyncAccount = async (accountId: number) => {
    try {
      setSyncing(prev => ({ ...prev, [accountId]: true }));
      
      // TODO: Implement actual sync API call
      console.log(`Syncing account ${accountId}`);
      
      // Simulate sync process
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Update account status
      setAccounts(prev => prev.map(acc => 
        acc.id === accountId 
          ? { 
              ...acc, 
              last_sync_at: new Date().toISOString(),
              last_sync_status: "success",
              last_sync_error: null,
              status: "active"
            }
          : acc
      ));
      
    } catch (err: any) {
      console.error(`Error syncing account ${accountId}:`, err);
      setError('Failed to sync account. Please try again.');
    } finally {
      setSyncing(prev => ({ ...prev, [accountId]: false }));
    }
  };

  const handleDeleteAccount = async (accountId: number) => {
    try {
      // TODO: Implement actual delete API call
      console.log(`Deleting account ${accountId}`);
      
      setAccounts(prev => prev.filter(acc => acc.id !== accountId));
    } catch (err: any) {
      console.error(`Error deleting account ${accountId}:`, err);
      setError('Failed to delete account. Please try again.');
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, accountId: number) => {
    setAnchorEl(event.currentTarget);
    setMenuAccountId(accountId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuAccountId(null);
  };

  const formatTimeAgo = (dateTime: string | null) => {
    if (!dateTime) return "Never";
    
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

  const getProviderIcon = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'google':
        return <GoogleIcon sx={{ color: '#4285f4' }} />;
      case 'microsoft':
      case 'outlook':
        return <MicrosoftIcon sx={{ color: '#00a1f1' }} />;
      default:
        return <Email />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'error': return 'error';
      case 'syncing': return 'warning';
      case 'inactive': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle color="success" />;
      case 'error': return <Error color="error" />;
      case 'syncing': return <CircularProgress size={20} />;
      case 'inactive': return <Warning color="warning" />;
      default: return <CheckCircle color="success" />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Email sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Email Accounts
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchAccounts}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setShowAddModal(true)}
          >
            Add Account
          </Button>
        </Toolbar>
      </AppBar>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ m: 2 }}>
          {error}
        </Alert>
      )}

      {/* Main Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
        {/* Sync Stats */}
        {syncStats && (
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Accounts
                  </Typography>
                  <Typography variant="h5">
                    {syncStats.total_accounts}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Active Accounts
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {syncStats.active_accounts}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Sync Errors
                  </Typography>
                  <Typography variant="h5" color={syncStats.sync_errors > 0 ? "error.main" : "success.main"}>
                    {syncStats.sync_errors}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Last Sync
                  </Typography>
                  <Typography variant="h6">
                    {formatTimeAgo(syncStats.last_sync)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Accounts List */}
        <Grid container spacing={3}>
          {accounts.map((account) => (
            <Grid item xs={12} md={6} lg={4} key={account.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                }}
              >
                <CardContent sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                      {getProviderIcon(account.provider)}
                    </Avatar>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" component="div">
                        {account.name}
                      </Typography>
                      <Typography color="text.secondary" variant="body2">
                        {account.email_address}
                      </Typography>
                    </Box>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuClick(e, account.id)}
                    >
                      <MoreVert />
                    </IconButton>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Chip
                      icon={getStatusIcon(account.status)}
                      label={account.status.charAt(0).toUpperCase() + account.status.slice(1)}
                      color={getStatusColor(account.status) as any}
                      size="small"
                      sx={{ mb: 1 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Provider: {account.provider.charAt(0).toUpperCase() + account.provider.slice(1)}
                    </Typography>
                  </Box>

                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Unread
                      </Typography>
                      <Typography variant="h6">
                        {account.unread_count}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Total Emails
                      </Typography>
                      <Typography variant="h6">
                        {account.total_emails.toLocaleString()}
                      </Typography>
                    </Grid>
                  </Grid>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Last Sync: {formatTimeAgo(account.last_sync_at)}
                    </Typography>
                    {account.last_sync_error && (
                      <Typography variant="body2" color="error.main" sx={{ mt: 1 }}>
                        Error: {account.last_sync_error}
                      </Typography>
                    )}
                  </Box>

                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={syncing[account.id] ? <CircularProgress size={16} /> : <Sync />}
                      onClick={() => handleSyncAccount(account.id)}
                      disabled={syncing[account.id]}
                    >
                      Sync
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<Settings />}
                      onClick={() => {
                        setSelectedAccount(account);
                        setShowEditModal(true);
                      }}
                    >
                      Settings
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Empty State */}
        {accounts.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Email sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" color="text.secondary" gutterBottom>
              No Email Accounts
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Add your first email account to start managing your emails.
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setShowAddModal(true)}
            >
              Add Email Account
            </Button>
          </Box>
        )}
      </Box>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          handleMenuClose();
          if (menuAccountId) {
            const account = accounts.find(acc => acc.id === menuAccountId);
            if (account) {
              setSelectedAccount(account);
              setShowEditModal(true);
            }
          }
        }}>
          <Edit sx={{ mr: 1 }} />
          Edit Settings
        </MenuItem>
        <MenuItem onClick={() => {
          handleMenuClose();
          if (menuAccountId) {
            handleSyncAccount(menuAccountId);
          }
        }}>
          <Sync sx={{ mr: 1 }} />
          Sync Now
        </MenuItem>
        <MenuItem onClick={() => {
          handleMenuClose();
          if (menuAccountId && window.confirm('Are you sure you want to delete this account?')) {
            handleDeleteAccount(menuAccountId);
          }
        }}>
          <Delete sx={{ mr: 1 }} />
          Delete Account
        </MenuItem>
      </Menu>

      {/* Add Account Dialog */}
      <Dialog
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Add Email Account</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Setup Email Account
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Connect your email account securely with OAuth:
            </Typography>
            <OAuthLoginButton 
              variant="list"
              onSuccess={(result) => {
                console.log('OAuth success:', result);
                setShowAddModal(false);
                fetchAccounts();
              }}
              onError={(error) => {
                console.error('OAuth error:', error);
                setError(`OAuth Setup Failed: ${error}`);
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAddModal(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Account Dialog */}
      <Dialog
        open={showEditModal}
        onClose={() => setShowEditModal(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Account Settings</DialogTitle>
        <DialogContent>
          {selectedAccount && (
            <Box sx={{ pt: 1 }}>
              <TextField
                fullWidth
                label="Account Name"
                defaultValue={selectedAccount.name}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Email Address"
                value={selectedAccount.email_address}
                disabled
                sx={{ mb: 2 }}
              />
              <FormControlLabel
                control={<Switch defaultChecked={selectedAccount.sync_enabled} />}
                label="Enable Email Sync"
                sx={{ mb: 2 }}
              />
              <Typography variant="body2" color="text.secondary">
                Created: {new Date(selectedAccount.created_at).toLocaleDateString()}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEditModal(false)}>
            Cancel
          </Button>
          <Button variant="contained" onClick={() => setShowEditModal(false)}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AccountsPage;