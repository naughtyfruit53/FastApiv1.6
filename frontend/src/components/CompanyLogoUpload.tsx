import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  IconButton,
  Paper,
  CircularProgress,
  Alert,
  Avatar,
  Tooltip,
  Stack
} from '@mui/material';
import {
  CloudUpload,
  Delete,
  PhotoCamera,
  Business
} from '@mui/icons-material';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { companyService } from '../services/authService';

interface CompanyLogoUploadProps {
  companyId: number;
  currentLogoPath?: string | null;
  disabled?: boolean;
  onLogoChange?: (logoPath: string | null) => void;
}

const CompanyLogoUpload: React.FC<CompanyLogoUploadProps> = ({
  companyId,
  currentLogoPath,
  disabled = false,
  onLogoChange
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(currentLogoPath || null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => companyService.uploadLogo(companyId, file),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['company'] });
      setPreviewUrl(companyService.getLogoUrl(companyId));
      setUploadError(null);
      if (onLogoChange) {
        onLogoChange(data.logo_path);
      }
    },
    onError: (error: any) => {
      setUploadError(error.message || 'Failed to upload logo');
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: () => companyService.deleteLogo(companyId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['company'] });
      setPreviewUrl(null);
      setUploadError(null);
      if (onLogoChange) {
        onLogoChange(null);
      }
    },
    onError: (error: any) => {
      setUploadError(error.message || 'Failed to delete logo');
    },
  });

  const validateFile = (file: File): string | null => {
    // Check file type
    if (!file.type.startsWith('image/')) {
      return 'Please select an image file (PNG, JPG, JPEG, GIF, etc.)';
    }

    // Check file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      return 'Logo file size must be less than 5MB';
    }

    return null;
  };

  const handleFileSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    const validationError = validateFile(file);

    if (validationError) {
      setUploadError(validationError);
      return;
    }

    // Create preview URL
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    // Upload file
    uploadMutation.mutate(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (!disabled) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragOver(true);
    }
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(e.target.files);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleDeleteLogo = () => {
    deleteMutation.mutate();
  };

  const isLoading = uploadMutation.isPending || deleteMutation.isPending;

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Company Logo
      </Typography>

      {uploadError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {uploadError}
        </Alert>
      )}

      <Stack direction="row" spacing={2} alignItems="center">
        {/* Logo Preview */}
        <Avatar
          src={previewUrl || undefined}
          sx={{
            width: 80,
            height: 80,
            bgcolor: 'grey.200',
            border: '2px solid',
            borderColor: 'grey.300'
          }}
        >
          {!previewUrl && <Business sx={{ fontSize: 40, color: 'grey.500' }} />}
        </Avatar>

        {/* Upload Area */}
        <Box sx={{ flex: 1 }}>
          {!previewUrl ? (
            <Paper
              sx={{
                p: 2,
                border: '2px dashed',
                borderColor: isDragOver ? 'primary.main' : 'grey.300',
                bgcolor: isDragOver ? 'action.hover' : 'background.paper',
                cursor: disabled ? 'default' : 'pointer',
                textAlign: 'center',
                transition: 'all 0.2s ease-in-out',
                minHeight: 80,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={disabled ? undefined : handleUploadClick}
            >
              {isLoading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2">
                    {uploadMutation.isPending ? 'Uploading...' : 'Processing...'}
                  </Typography>
                </Box>
              ) : (
                <Box>
                  <CloudUpload sx={{ fontSize: 32, color: 'grey.500', mb: 1 }} />
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Drag & drop logo here or click to upload
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    PNG, JPG, JPEG, GIF up to 5MB
                  </Typography>
                </Box>
              )}
            </Paper>
          ) : (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Change Logo">
                <Button
                  variant="outlined"
                  startIcon={<PhotoCamera />}
                  onClick={handleUploadClick}
                  disabled={disabled || isLoading}
                  size="small"
                >
                  Change
                </Button>
              </Tooltip>
              <Tooltip title="Remove Logo">
                <IconButton
                  color="error"
                  onClick={handleDeleteLogo}
                  disabled={disabled || isLoading}
                  size="small"
                >
                  <Delete />
                </IconButton>
              </Tooltip>
            </Box>
          )}
        </Box>
      </Stack>

      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInputChange}
        accept="image/*"
        style={{ display: 'none' }}
        disabled={disabled}
      />
    </Box>
  );
};

export default CompanyLogoUpload;