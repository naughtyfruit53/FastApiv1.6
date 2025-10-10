'use client';

import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/router';
import { Box, Typography, CircularProgress, Alert, Paper, Button } from '@mui/material';
import { CheckCircle, Error } from '@mui/icons-material';
import { useOAuth } from '../../../hooks/useOAuth';
import { useQueryClient } from '@tanstack/react-query';
import { useEmail } from '../../../context/EmailContext';

const OAuthCallback: React.FC = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { setSelectedAccountId } = useEmail();
  const { handleOAuthCallback } = useOAuth();
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState<string>('');
  const [result, setResult] = useState<any>(null);
  const processedRef = useRef(false);

  useEffect(() => {
    const processCallback = async () => {
      if (processedRef.current || typeof window === 'undefined') return;
      processedRef.current = true;

      const { provider } = router.query; // Get provider from dynamic path
      const { code, state, error, error_description } = router.query;

      if (!provider || (!code && !error)) return;

      const storedProvider = localStorage.getItem(`oauth_provider_${state as string}`);
      if (!storedProvider || storedProvider !== provider) {
        setStatus('error');
        setMessage('Invalid authentication state or provider mismatch. Please try again.');
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

        // Set the new account as selected
        if (result.account_id) {
          setSelectedAccountId(result.account_id);
          localStorage.setItem('selectedEmailAccount', result.account_id.toString());
        }

        // Invalidate queries to refresh accounts
        queryClient.invalidateQueries({ queryKey: ['oauth-tokens'] });
        queryClient.invalidateQueries({ queryKey: ['mail-accounts'] });

        localStorage.removeItem(`oauth_provider_${state as string}`);

        setTimeout(() => {
          router.push('/email/accounts');
        }, 3000);

      } catch (err: any) {
        console.error('OAuth callback error:', err);
        setStatus('error');
        setMessage(err.message || 'Failed to complete OAuth authentication');
        localStorage.removeItem(`oauth_provider_${state as string}`);
      }
    };

    if (router.isReady) processCallback();
  }, [router.isReady, router.query, handleOAuthCallback, router, queryClient, setSelectedAccountId]);

  const handleRetry = () => {
    router.push('/email/oauth');
  };

  const handleGoBack = () => {
    router.push('/email/accounts');
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