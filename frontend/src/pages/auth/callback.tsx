/**
 * OAuth Callback Page
 * Handles OAuth2 callback from providers and completes the authentication flow
 */

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  Button
} from '@mui/material';
import { CheckCircle, Error } from '@mui/icons-material';
import { useOAuth } from '../../hooks/useOAuth';

const OAuthCallback: React.FC = () => {
  const router = useRouter();
  const { handleOAuthCallback } = useOAuth();
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState<string>('');
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    const processCallback = async () => {
      const { code, state, error, error_description, provider } = router.query;

      if (!code && !error) {
        // Still loading or missing parameters
        return;
      }

      const storedProvider = localStorage.getItem(`oauth_provider_${state as string}`);
      console.log(`Stored provider for state ${state}: ${storedProvider}`);
      if (!storedProvider) {
        setStatus('error');
        setMessage('Invalid authentication state. Please try again.');
        return;
      }

      try {
        if (error) {
          throw new Error((error_description as string) || (error as string));
        }

        const result = await handleOAuthCallback(
          storedProvider,
          code as string,
          state as string,
          error as string,
          error_description as string
        );

        setResult(result);
        setStatus('success');
        setMessage(`Successfully connected ${storedProvider} email account`);

        // Clean up storage
        localStorage.removeItem(`oauth_provider_${state as string}`);

        // Redirect to mail dashboard after a short delay
        setTimeout(() => {
          router.push('/mail/dashboard');
        }, 3000);

      } catch (err: any) {
        console.error('OAuth callback error:', err);
        setStatus('error');
        setMessage(err.message || 'Failed to complete OAuth authentication');
        // Clean up on error as well
        localStorage.removeItem(`oauth_provider_${state as string}`);
      }
    };

    if (router.isReady) {
      processCallback();
    }
  }, [router.isReady, router.query, handleOAuthCallback, router]);

  const handleRetry = () => {
    router.push('/mail/dashboard');
  };

  const handleGoBack = () => {
    router.push('/mail/dashboard');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'grey.50',
        p: 3
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          maxWidth: 500,
          width: '100%',
          textAlign: 'center'
        }}
      >
        {status === 'loading' && (
          <>
            <CircularProgress size={60} sx={{ mb: 3 }} />
            <Typography variant="h5" gutterBottom>
              Completing Authentication
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Please wait while we securely connect your email account...
            </Typography>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle 
              sx={{ 
                fontSize: 60, 
                color: 'success.main', 
                mb: 3 
              }} 
            />
            <Typography variant="h5" gutterBottom color="success.main">
              Authentication Successful!
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              {message}
            </Typography>
            
            {result && (
              <Alert severity="success" sx={{ mb: 3, textAlign: 'left' }}>
                <Typography variant="subtitle2">Account Details:</Typography>
                <Typography variant="body2">
                  Email: {result.email}
                </Typography>
                <Typography variant="body2">
                  Provider: {result.provider}
                </Typography>
              </Alert>
            )}

            <Typography variant="body2" color="text.secondary">
              Redirecting to your mail dashboard in 3 seconds...
            </Typography>
          </>
        )}

        {status === 'error' && (
          <>
            <Error 
              sx={{ 
                fontSize: 60, 
                color: 'error.main', 
                mb: 3 
              }} 
            />
            <Typography variant="h5" gutterBottom color="error.main">
              Authentication Failed
            </Typography>
            <Alert severity="error" sx={{ mb: 3, textAlign: 'left' }}>
              {message}
            </Alert>
            
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button variant="outlined" onClick={handleGoBack}>
                Go to Mail Dashboard
              </Button>
              <Button variant="contained" onClick={handleRetry}>
                Try Again
              </Button>
            </Box>
          </>
        )}
      </Paper>
    </Box>
  );
};

export default OAuthCallback;