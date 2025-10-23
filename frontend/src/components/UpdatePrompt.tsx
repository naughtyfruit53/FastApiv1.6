import React from 'react';
import { Snackbar, Alert, Button } from '@mui/material';
import { usePWA } from '../hooks/usePWA';

const UpdatePrompt: React.FC = () => {
  const { updateAvailable, updateServiceWorker } = usePWA();

  const handleUpdate = () => {
    updateServiceWorker();
  };

  return (
    <Snackbar
      open={updateAvailable}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      <Alert
        severity="info"
        action={
          <Button color="inherit" size="small" onClick={handleUpdate}>
            Update
          </Button>
        }
      >
        A new version is available! Click Update to refresh.
      </Alert>
    </Snackbar>
  );
};

export default UpdatePrompt;
