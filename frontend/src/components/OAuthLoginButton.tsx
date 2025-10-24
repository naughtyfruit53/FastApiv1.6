/**
 * OAuth Login Button Component
 * Handles OAuth2 login flow for Google and Microsoft
 */

import React, { useState } from 'react';
import {
  Button,
  Box,
  Alert,
  CircularProgress,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import {
  Google as GoogleIcon,
  Microsoft as MicrosoftIcon,
  Email as EmailIcon,
  Security as SecurityIcon
} from '@mui/icons-material';
import { useOAuth } from '../hooks/useOAuth';

interface OAuthProvider {
  name: string;
  display_name: string;
  icon: string;
  scopes: string[];
}

interface OAuthLoginButtonProps {
  variant?: 'button' | 'list';
  onSuccess?: (result: any) => void;
  onError?: (error: string) => void;
}

const OAuthLoginButton: React.FC<OAuthLoginButtonProps> = ({
  variant = 'button',
  onSuccess, // Used for OAuth callback handling, not direct success
  onError
}) => {
  const [open, setOpen] = useState(false);
  const [providers, setProviders] = useState<OAuthProvider[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { initiateOAuthFlow, getProviders } = useOAuth();

  const handleOpen = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getProviders();
      setProviders(response.providers);
      setOpen(true);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to load OAuth providers';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleProviderSelect = async (provider: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await initiateOAuthFlow(provider);
      // OAuth flow redirects to provider, then back to callback URL
      // onSuccess will be called by the OAuth callback handler
      console.log('Initiating OAuth flow for:', provider);
      window.location.href = result.authorization_url;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || `Failed to initiate ${provider} OAuth flow`;
      setError(errorMsg);
      onError?.(errorMsg);
      setLoading(false);
    }
  };

  const getProviderIcon = (iconName: string) => {
    switch (iconName) {
      case 'google':
        return <GoogleIcon sx={{ color: '#4285f4' }} />;
      case 'microsoft':
        return <MicrosoftIcon sx={{ color: '#00a1f1' }} />;
      default:
        return <EmailIcon />;
    }
  };

  const getProviderColor = (provider: string) => {
    switch (provider) {
      case 'google':
        return '#4285f4';
      case 'microsoft':
        return '#00a1f1';
      default:
        return 'primary';
    }
  };

  if (variant === 'list') {
    return (
      <Box>
        {providers.map((provider) => (
          <Button
            key={provider.name}
            fullWidth
            variant="outlined"
            startIcon={getProviderIcon(provider.icon)}
            onClick={() => handleProviderSelect(provider.name)}
            disabled={loading}
            sx={{
              mb: 1,
              borderColor: getProviderColor(provider.name),
              color: getProviderColor(provider.name),
              '&:hover': {
                borderColor: getProviderColor(provider.name),
                backgroundColor: `${getProviderColor(provider.name)}08`
              }
            }}
          >
            Connect {provider.display_name}
          </Button>
        ))}
      </Box>
    );
  }

  return (
    <>
      <Button
        variant="contained"
        startIcon={loading ? <CircularProgress size={20} /> : <EmailIcon />}
        onClick={handleOpen}
        disabled={loading}
        sx={{ mb: 2 }}
      >
        {loading ? 'Loading...' : 'Connect Email Account'}
      </Button>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SecurityIcon />
            <Typography variant="h6">Connect Email Account</Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Connect your email account to send and receive emails directly from TritIQ.
            Your credentials are encrypted and stored securely.
          </Typography>

          <List>
            {providers.map((provider) => (
              <ListItem key={provider.name} disablePadding>
                <ListItemButton
                  onClick={() => handleProviderSelect(provider.name)}
                  disabled={loading}
                  sx={{
                    border: 1,
                    borderColor: 'grey.300',
                    borderRadius: 1,
                    mb: 1,
                    '&:hover': {
                      borderColor: getProviderColor(provider.name),
                    }
                  }}
                >
                  <ListItemIcon>
                    {getProviderIcon(provider.icon)}
                  </ListItemIcon>
                  <ListItemText
                    primary={`Connect ${provider.display_name}`}
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Permissions: 
                        </Typography>
                        <Box sx={{ mt: 0.5 }}>
                          {provider.scopes.map((scope) => (
                            <Chip
                              key={scope}
                              label={scope.replace('gmail.', '').replace('Mail.', '')}
                              size="small"
                              variant="outlined"
                              sx={{ mr: 0.5, mb: 0.5, fontSize: '0.7rem' }}
                            />
                          ))}
                        </Box>
                      </Box>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>

          {providers.length === 0 && !loading && (
            <Alert severity="info">
              No OAuth providers are configured. Please contact your administrator.
            </Alert>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default OAuthLoginButton;