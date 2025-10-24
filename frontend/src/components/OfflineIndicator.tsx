import React from 'react';
import { Alert, Snackbar, Box, Typography } from '@mui/material';
import { CloudOff as OfflineIcon, CloudDone as OnlineIcon } from '@mui/icons-material';
import { usePWA } from '../hooks/usePWA';

const OfflineIndicator: React.FC = () => {
  const { isOnline } = usePWA();
  const [wasOffline, setWasOffline] = React.useState(false);
  const [showOnlineMessage, setShowOnlineMessage] = React.useState(false);

  React.useEffect(() => {
    if (!isOnline) {
      setWasOffline(true);
    } else if (wasOffline) {
      setShowOnlineMessage(true);
      const timer = setTimeout(() => {
        setShowOnlineMessage(false);
        setWasOffline(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isOnline, wasOffline]);

  return (
    <>
      {/* Persistent offline banner */}
      {!isOnline && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 9999,
            bgcolor: 'warning.main',
            color: 'warning.contrastText',
            py: 1,
            px: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 1,
            boxShadow: 3,
          }}
        >
          <OfflineIcon fontSize="small" />
          <Typography variant="body2" fontWeight="medium">
            You are offline. Some features may be limited.
          </Typography>
        </Box>
      )}

      {/* Back online notification */}
      <Snackbar
        open={showOnlineMessage}
        autoHideDuration={3000}
        onClose={() => setShowOnlineMessage(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          severity="success"
          icon={<OnlineIcon />}
          onClose={() => setShowOnlineMessage(false)}
          sx={{ width: '100%' }}
        >
          You are back online!
        </Alert>
      </Snackbar>
    </>
  );
};

export default OfflineIndicator;
