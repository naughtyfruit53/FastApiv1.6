'use client';

/**
 * OAuth Connections Page
 * Manage OAuth connections for email accounts
 */

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Alert,
} from '@mui/material';
import OAuthLoginButton from '../../components/OAuthLoginButton';

const OAuthConnections: React.FC = () => {
  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        OAuth Connections
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Connect your email accounts using OAuth2 authentication for secure access to Gmail, Outlook, and other providers.
      </Alert>

      <Paper sx={{ p: 4 }}>
        <Typography variant="h6" gutterBottom>
          Connect Email Account
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 3 }}>
          Click the button below to authenticate with your email provider using OAuth2.
          This will allow the application to access your emails securely.
        </Typography>
        
        <OAuthLoginButton />
      </Paper>

      <Paper sx={{ p: 4, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          About OAuth Authentication
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          OAuth2 is a secure authentication protocol that allows you to grant access to your email account
          without sharing your password. The application receives a token that can be used to access your
          emails on your behalf.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          <strong>Supported Providers:</strong>
        </Typography>
        <ul>
          <li>
            <Typography variant="body2" color="text.secondary">
              Google Gmail - Full IMAP/SMTP access
            </Typography>
          </li>
          <li>
            <Typography variant="body2" color="text.secondary">
              Microsoft Outlook/Office 365 - Full IMAP/SMTP access
            </Typography>
          </li>
        </ul>
      </Paper>
    </Box>
  );
};

export default OAuthConnections;
