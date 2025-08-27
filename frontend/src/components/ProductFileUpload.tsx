import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
  LinearProgress,
  Alert,
  Tooltip,
  Chip
} from '@mui/material';
import {
  CloudUpload,
  AttachFile,
  Delete,
  Download,
  FilePresent
} from '@mui/icons-material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';

interface ProductFile {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  content_type: string;
  created_at: string;
}

interface ProductFileUploadProps {
  productId?: number;
  disabled?: boolean;
}

const ProductFileUpload: React.FC<ProductFileUploadProps> = ({
  productId,
  disabled = false
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  // Query to get existing files
  const { data: files = [], isLoading } = useQuery({
    queryKey: ['product-files', productId],
    queryFn: async () => {
      if (!productId) return [];
      const response = await api.get(`/api/v1/products/${productId}/files`);
      return response.data;
    },
    enabled: !!productId
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      if (!productId) throw new Error('Product ID is required');
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post(
        `/api/v1/products/${productId}/files`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['product-files', productId] });
      setUploadError(null);
    },
    onError: (error: any) => {
      setUploadError(error.response?.data?.detail || 'Upload failed');
    }
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (fileId: number) => {
      await api.delete(`/api/v1/products/${productId}/files/${fileId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['product-files', productId] });
    }
  });

  const handleFileSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    
    const file = files[0];
    
    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File size must be less than 10MB');
      return;
    }
    
    uploadMutation.mutate(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (disabled || !productId) return;
    
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled && productId) {
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

  const handleDownload = async (fileId: number, filename: string) => {
    try {
      const response = await api.get(
        `/api/v1/products/${productId}/files/${fileId}/download`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (contentType: string) => {
    if (contentType.startsWith('image/')) return '🖼️';
    if (contentType.includes('pdf')) return '📄';
    if (contentType.includes('word')) return '📝';
    if (contentType.includes('excel') || contentType.includes('spreadsheet')) return '📊';
    return '📎';
  };

  if (!productId) {
    return (
      <Alert severity="info">
        Save the product first to upload files
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Product Files
        <Chip
          label={`${files.length}/5`}
          color={files.length >= 5 ? 'error' : 'primary'}
          size="small"
          sx={{ ml: 1 }}
        />
      </Typography>

      {uploadError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {uploadError}
        </Alert>
      )}

      {/* Upload Area */}
      {files.length < 5 && !disabled && (
        <Paper
          sx={{
            p: 3,
            mb: 2,
            border: '2px dashed',
            borderColor: isDragOver ? 'primary.main' : 'grey.300',
            bgcolor: isDragOver ? 'action.hover' : 'background.paper',
            cursor: 'pointer',
            textAlign: 'center',
            transition: 'all 0.2s ease-in-out'
          }}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            hidden
            onChange={handleFileInputChange}
            accept="*/*"
          />
          
          {uploadMutation.isPending ? (
            <Box>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Uploading file...
              </Typography>
              <LinearProgress sx={{ mt: 1 }} />
            </Box>
          ) : (
            <Box>
              <CloudUpload sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Click to upload or drag and drop files here
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Maximum file size: 10MB • Maximum 5 files
              </Typography>
            </Box>
          )}
        </Paper>
      )}

      {/* Files List */}
      {files.length > 0 && (
        <Paper sx={{ mt: 2 }}>
          <List>
            {files.map((file: ProductFile) => (
              <ListItem key={file.id} divider>
                <ListItemIcon>
                  <FilePresent color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <span>{getFileIcon(file.content_type)}</span>
                      <Typography variant="body2">
                        {file.original_filename}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        {formatFileSize(file.file_size)} • {new Date(file.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <Tooltip title="Download">
                    <IconButton
                      edge="end"
                      onClick={() => handleDownload(file.id, file.original_filename)}
                      sx={{ mr: 1 }}
                    >
                      <Download />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton
                      edge="end"
                      onClick={() => deleteMutation.mutate(file.id)}
                      disabled={deleteMutation.isPending || disabled}
                    >
                      <Delete />
                    </IconButton>
                  </Tooltip>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {files.length === 0 && productId && !isLoading && (
        <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
          No files uploaded yet
        </Typography>
      )}
    </Box>
  );
};

export default ProductFileUpload;