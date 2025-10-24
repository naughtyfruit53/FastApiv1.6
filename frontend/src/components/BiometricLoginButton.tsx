import React from 'react';
import { Button, CircularProgress, Alert } from '@mui/material';
import { Fingerprint as FingerprintIcon } from '@mui/icons-material';
import { useBiometric } from '../hooks/useBiometric';

interface BiometricLoginButtonProps {
  onSuccess: () => void;
  onError?: (error: string) => void;
  disabled?: boolean;
}

const BiometricLoginButton: React.FC<BiometricLoginButtonProps> = ({
  onSuccess,
  onError,
  disabled = false,
}) => {
  const { isAvailable, isSupported, authenticate, error } = useBiometric();
  const [loading, setLoading] = React.useState(false);

  const handleAuthenticate = async () => {
    setLoading(true);
    try {
      const success = await authenticate();
      if (success) {
        onSuccess();
      } else if (error && onError) {
        onError(error);
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isSupported) {
    return null;
  }

  return (
    <>
      <Button
        fullWidth
        variant="outlined"
        startIcon={loading ? <CircularProgress size={20} /> : <FingerprintIcon />}
        onClick={handleAuthenticate}
        disabled={!isAvailable || disabled || loading}
        sx={{
          mt: 2,
          borderColor: 'primary.main',
          color: 'primary.main',
          '&:hover': {
            borderColor: 'primary.dark',
            bgcolor: 'primary.50',
          },
        }}
      >
        {loading ? 'Authenticating...' : 'Login with Biometrics'}
      </Button>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {!isAvailable && isSupported && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Biometric authentication is not set up on this device. Please use password login.
        </Alert>
      )}
    </>
  );
};

export default BiometricLoginButton;
