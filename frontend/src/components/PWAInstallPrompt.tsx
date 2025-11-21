import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
} from '@mui/material';
import {
  Close as CloseIcon,
  GetApp as InstallIcon,
  PhoneIphone as MobileIcon,
} from '@mui/icons-material';
import { usePWA } from '../hooks/usePWA';

const PWAInstallPrompt: React.FC = () => {
  const { isInstallable, promptInstall } = usePWA();
  const [showPrompt, setShowPrompt] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Check if user has previously dismissed the prompt
    const isDismissed = localStorage.getItem('pwa-install-dismissed') === 'true';
    setDismissed(isDismissed);

    // Show prompt after 30 seconds if installable and not dismissed
    if (isInstallable && !isDismissed) {
      const timer = setTimeout(() => {
        setShowPrompt(true);
      }, 30000);

      return () => clearTimeout(timer);
    }
  }, [isInstallable]);

  const handleInstall = async () => {
    await promptInstall();
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    setDismissed(true);
    localStorage.setItem('pwa-install-dismissed', 'true');
  };

  const handleClose = () => {
    setShowPrompt(false);
  };

  if (!isInstallable || dismissed) {
    return null;
  }

  return (
    <Dialog
      open={showPrompt}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        },
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <MobileIcon />
          <Typography variant="h6">Install TritIQ App</Typography>
        </Box>
        <IconButton onClick={handleClose} sx={{ color: 'white' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Get the best experience with our mobile app. Install TRITIQ BOS for:
        </Typography>
        
        <Box sx={{ pl: 2 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            ✓ Faster loading and better performance
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            ✓ Work offline with cached data
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            ✓ Quick access from your home screen
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            ✓ Push notifications for updates
          </Typography>
          <Typography variant="body2">
            ✓ Native app-like experience
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button
          onClick={handleDismiss}
          sx={{
            color: 'white',
            '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' },
          }}
        >
          Not Now
        </Button>
        <Button
          onClick={handleInstall}
          variant="contained"
          startIcon={<InstallIcon />}
          sx={{
            bgcolor: 'white',
            color: '#667eea',
            '&:hover': {
              bgcolor: 'rgba(255,255,255,0.9)',
            },
          }}
        >
          Install
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PWAInstallPrompt;
