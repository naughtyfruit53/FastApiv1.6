import React, { useEffect, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  IconButton,
  Alert,
} from '@mui/material';
import {
  PhotoCamera as CameraIcon,
  FlipCameraIos as FlipIcon,
  Close as CloseIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { useCamera } from '../hooks/useCamera';

interface CameraCaptureProps {
  open: boolean;
  onClose: () => void;
  onCapture: (photo: Blob) => void;
  title?: string;
}

const CameraCapture: React.FC<CameraCaptureProps> = ({
  open,
  onClose,
  onCapture,
  title = 'Capture Photo',
}) => {
  const {
    isSupported,
    isActive,
    stream,
    error,
    startCamera,
    stopCamera,
    capturePhoto,
    switchCamera,
  } = useCamera();

  const videoRef = useRef<HTMLVideoElement>(null);
  const [capturedImage, setCapturedImage] = React.useState<string | null>(null);

  useEffect(() => {
    if (open && isSupported) {
      startCamera();
    }

    return () => {
      stopCamera();
    };
  }, [open, isSupported, startCamera, stopCamera]);

  useEffect(() => {
    if (stream && videoRef.current) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  const handleCapture = async () => {
    const photo = await capturePhoto();
    if (photo) {
      const url = URL.createObjectURL(photo);
      setCapturedImage(url);
    }
  };

  const handleRetake = () => {
    if (capturedImage) {
      URL.revokeObjectURL(capturedImage);
    }
    setCapturedImage(null);
  };

  const handleConfirm = () => {
    if (capturedImage) {
      fetch(capturedImage)
        .then((res) => res.blob())
        .then((blob) => {
          onCapture(blob);
          handleClose();
        });
    }
  };

  const handleClose = () => {
    stopCamera();
    if (capturedImage) {
      URL.revokeObjectURL(capturedImage);
      setCapturedImage(null);
    }
    onClose();
  };

  if (!isSupported) {
    return (
      <Dialog open={open} onClose={onClose}>
        <DialogContent>
          <Alert severity="error">
            Camera is not supported on this device.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  }

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      fullScreen
      PaperProps={{
        sx: {
          bgcolor: 'black',
          color: 'white',
        },
      }}
    >
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {title}
        <IconButton onClick={handleClose} sx={{ color: 'white' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 0, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {error && (
          <Alert severity="error" sx={{ m: 2 }}>
            {error}
          </Alert>
        )}

        <Box
          sx={{
            position: 'relative',
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {capturedImage ? (
            <img
              src={capturedImage}
              alt="Captured"
              style={{
                maxWidth: '100%',
                maxHeight: '100%',
                objectFit: 'contain',
              }}
            />
          ) : (
            <video
              ref={videoRef}
              autoPlay
              playsInline
              style={{
                maxWidth: '100%',
                maxHeight: '100%',
                objectFit: 'contain',
              }}
            />
          )}
        </Box>
      </DialogContent>

      <DialogActions
        sx={{
          justifyContent: 'center',
          gap: 2,
          py: 3,
          bgcolor: 'rgba(0,0,0,0.8)',
        }}
      >
        {capturedImage ? (
          <>
            <Button
              variant="outlined"
              onClick={handleRetake}
              sx={{
                color: 'white',
                borderColor: 'white',
                '&:hover': {
                  borderColor: 'white',
                  bgcolor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              Retake
            </Button>
            <Button
              variant="contained"
              startIcon={<CheckIcon />}
              onClick={handleConfirm}
              sx={{
                bgcolor: 'success.main',
                '&:hover': {
                  bgcolor: 'success.dark',
                },
              }}
            >
              Use Photo
            </Button>
          </>
        ) : (
          <>
            <IconButton
              onClick={switchCamera}
              disabled={!isActive}
              sx={{
                color: 'white',
                bgcolor: 'rgba(255,255,255,0.2)',
                '&:hover': {
                  bgcolor: 'rgba(255,255,255,0.3)',
                },
              }}
            >
              <FlipIcon />
            </IconButton>
            <IconButton
              onClick={handleCapture}
              disabled={!isActive}
              sx={{
                width: 80,
                height: 80,
                color: 'white',
                bgcolor: 'primary.main',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
              }}
            >
              <CameraIcon fontSize="large" />
            </IconButton>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CameraCapture;
