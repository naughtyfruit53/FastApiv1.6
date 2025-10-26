import React from 'react';
import {
  Box,
  LinearProgress,
  Typography,
  Paper,
  Alert,
} from '@mui/material';
import { CheckCircle, Error, HourglassEmpty } from '@mui/icons-material';

interface BulkImportExportProgressBarProps {
  isProcessing: boolean;
  progress: number;
  type: 'import' | 'export';
  status?: 'idle' | 'processing' | 'success' | 'error';
  message?: string;
  error?: string;
  fileName?: string;
}

const BulkImportExportProgressBar: React.FC<BulkImportExportProgressBarProps> = ({
  isProcessing,
  progress,
  type,
  status = 'idle',
  message,
  error,
  fileName,
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'processing':
        return 'primary';
      default:
        return 'inherit';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircle color="success" />;
      case 'error':
        return <Error color="error" />;
      case 'processing':
        return <HourglassEmpty color="primary" />;
      default:
        return null;
    }
  };

  if (!isProcessing && status === 'idle') {
    return null;
  }

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          {getStatusIcon()}
          <Typography variant="body1" fontWeight="medium">
            {type === 'import' ? 'Importing' : 'Exporting'} {fileName ? `"${fileName}"` : 'data'}
          </Typography>
        </Box>

        {isProcessing && status === 'processing' && (
          <>
            <LinearProgress
              variant={progress > 0 ? 'determinate' : 'indeterminate'}
              value={progress}
              sx={{ mb: 1, height: 8, borderRadius: 4 }}
              color={getStatusColor() as any}
            />
            <Typography variant="body2" color="text.secondary" align="center">
              {progress > 0 ? `${Math.round(progress)}% complete` : 'Processing...'}
            </Typography>
          </>
        )}

        {message && status === 'success' && (
          <Alert severity="success" sx={{ mt: 1 }}>
            {message}
          </Alert>
        )}

        {error && status === 'error' && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {error}
          </Alert>
        )}

        {status === 'processing' && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Please wait while we process your {type === 'import' ? 'import' : 'export'}. 
            Do not close this window.
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default BulkImportExportProgressBar;
