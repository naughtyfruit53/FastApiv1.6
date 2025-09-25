// frontend/src/pages/mail/dashboard.tsx
import React, { useState, useEffect } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import { EmailService, getSnappyMailUrl } from '../../services'; // Adjust path if needed

const MailDashboard: React.FC<{ userId: number }> = ({ userId }) => { // Expect userId from props/context
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [snappymailUrl, setSnappymailUrl] = useState<string>('');

  useEffect(() => {
    const fetchUrl = async () => {
      try {
        setLoading(true);
        setError(null);
        const url = await getSnappymailUrl(userId);
        setSnappymailUrl(url);
      } catch (err) {
        setError('Failed to fetch email config. Using default.');
        setSnappymailUrl((typeof window !== 'undefined' ? process.env.NEXT_PUBLIC_SNAPPYMAIL_URL : '') || 'http://localhost:8888');
      } finally {
        setLoading(false);
      }
    };
    fetchUrl();

    // Timeout fallback: if still loading after 10s, show error
    const timeout = setTimeout(() => {
      if (loading) {
        setLoading(false);
        setError('Timeout loading SnappyMail. Check service status.');
      }
    }, 10000);

    return () => clearTimeout(timeout);
  }, [userId]);

  const handleLoad = () => {
    setLoading(false);
    setError(null);
  };

  const handleError = () => {
    setLoading(false);
    setError('Failed to load SnappyMail. Ensure service is running and CORS allowed.');
  };

  if (loading && !snappymailUrl) {
    return (
      <Box sx={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading SnappyMail...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
        Email Dashboard
      </Typography>
      <Box sx={{ flex: 1, position: 'relative' }}>
        {error && (
          <Typography color="error" sx={{ p: 2, textAlign: 'center' }}>
            {error}
          </Typography>
        )}
        <iframe
          src={snappymailUrl}
          style={{ width: '100%', height: '100%', border: 'none', display: error ? 'none' : 'block' }}
          title="SnappyMail Webmail"
          sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-top-navigation"
          loading="lazy"
          onLoad={handleLoad}
          onError={handleError}
        />
      </Box>
    </Box>
  );
};

export default MailDashboard;