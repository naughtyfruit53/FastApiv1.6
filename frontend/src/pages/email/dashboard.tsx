/**
 * Email Dashboard Page
 * Displays email accounts and redirects to inbox if account is selected
 */

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { Box, Typography, CircularProgress, Alert, Button, List, ListItem, ListItemText, ListItemButton } from '@mui/material';
import { useOAuth } from '../../hooks/useOAuth';
import { useAuth } from '../../context/AuthContext';

const EmailDashboard: React.FC = () => {
  const router = useRouter();
  const { getUserTokens, loading, error } = useOAuth();
  const { user } = useAuth();

  const [tokens, setTokens] = useState<UserEmailToken[]>([]);
  const [selectedToken, setSelectedToken] = useState<number | null>(null);

  useEffect(() => {
    const loadTokens = async () => {
      try {
        const userTokens = await getUserTokens();
        setTokens(userTokens);

        // Check localStorage for selected token
        const storedToken = localStorage.getItem('selectedEmailToken');
        if (storedToken) {
          const tokenId = parseInt(storedToken, 10);
          if (userTokens.some(token => token.id === tokenId)) {
            setSelectedToken(tokenId);
            // Redirect to inbox with selected token
            router.push(`/email/inbox?token=${tokenId}`);
          }
        }
      } catch (err) {
        console.error('Failed to load email tokens:', err);
      }
    };

    if (user) {
      loadTokens();
    }
  }, [user, getUserTokens, router]);

  const handleSelectAccount = (tokenId: number) => {
    localStorage.setItem('selectedEmailToken', tokenId.toString());
    setSelectedToken(tokenId);
    router.push(`/email/inbox?token=${tokenId}`);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  if (tokens.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h5" gutterBottom>
          No Email Accounts Connected
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Please connect an email account to get started.
        </Typography>
        <Button variant="contained" onClick={() => router.push('/settings/email')}>
          Connect Email Account
        </Button>
      </Box>
    );
  }

  if (!selectedToken) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Select Email Account
        </Typography>
        <List>
          {tokens.map(token => (
            <ListItem key={token.id} disablePadding>
              <ListItemButton onClick={() => handleSelectAccount(token.id)}>
                <ListItemText 
                  primary={token.email_address}
                  secondary={`${token.provider.toUpperCase()} - ${token.display_name || 'No name'}`}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>
    );
  }

  // If selected, should redirect, but show loading as fallback
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <CircularProgress />
      <Typography sx={{ ml: 2 }}>Loading inbox...</Typography>
    </Box>
  );
};

export default EmailDashboard;