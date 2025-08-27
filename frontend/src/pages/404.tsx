// frontend/src/pages/404.tsx

'use client';

import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper
} from '@mui/material';
import { Home, ArrowBack } from '@mui/icons-material';
import { useRouter } from 'next/navigation';

const NotFoundPage: React.FC = () => {
  const router = useRouter();

  const handleGoHome = () => {
    router.push('/');
  };

  const handleGoBack = () => {
    router.back();
  };

  return (
    <Container maxWidth="md" sx={{ mt: 8 }}>
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h3" color="error" gutterBottom>
          404 - Page Not Found
        </Typography>
        
        <Typography variant="h6" color="textSecondary" gutterBottom>
          The page you are looking for does not exist or has been moved.
        </Typography>

        <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="contained"
            startIcon={<Home />}
            onClick={handleGoHome}
          >
            Go Home
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<ArrowBack />}
            onClick={handleGoBack}
          >
            Go Back
          </Button>
        </Box>

        <Typography variant="body2" color="textSecondary" sx={{ mt: 3 }}>
          If you believe this is an error, please contact support.
        </Typography>
      </Paper>
    </Container>
  );
};

export default NotFoundPage;