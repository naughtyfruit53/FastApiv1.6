// frontend/src/components/VoucherPDFButton.tsx

import React, { useState } from 'react';
import {
  Button,
  Menu,
  MenuItem,
  IconButton,
  CircularProgress,
  Tooltip,
  Box,
  Alert,
  Snackbar
} from '@mui/material';
import {
  PictureAsPdf as PdfIcon,
  Download as DownloadIcon,
  Preview as PreviewIcon,
  MoreVert as MoreIcon
} from '@mui/icons-material';
import api from '../lib/api'; // Changed to default import since it's exported as default in api.ts

interface VoucherPDFButtonProps {
  voucherType: 'purchase' | 'sales' | 'quotation' | 'sales_order' | 'proforma';
  voucherId: number;
  voucherNumber?: string;
  variant?: 'button' | 'icon' | 'menu';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  className?: string;
}

interface PDFError {
  message: string;
  type: 'error' | 'warning' | 'info';
}

const VoucherPDFButton: React.FC<VoucherPDFButtonProps> = ({
  voucherType,
  voucherId,
  voucherNumber,
  variant = 'button',
  size = 'medium',
  disabled = false,
  className = ''
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [error, setError] = useState<PDFError | null>(null);

  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    if (variant === 'menu') {
      setAnchorEl(event.currentTarget);
    } else {
      handlePreviewPDF();
    }
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handlePreviewPDF = async () => {
    await generatePDF(false);
    handleClose();
  };

  const handleDownloadPDF = async () => {
    await generatePDF(true);
    handleClose();
  };

  const generatePDF = async (download: boolean = false) => {
    if (!voucherId || disabled) return;

    setIsGenerating(true);
    setError(null);

    try {
      const endpoint = download 
        ? `/api/v1/pdf-generation/voucher/${voucherType}/${voucherId}/download`
        : `/api/v1/pdf-generation/voucher/${voucherType}/${voucherId}`;

      const response = await api.post(endpoint, {}, {
        responseType: 'blob',
        headers: {
          'Accept': 'application/pdf'
        }
      });

      if (response.status === 200) {
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);

        if (download) {
          // Force download
          const a = document.createElement('a');
          a.href = url;
          a.download = `${voucherType}_${voucherNumber || voucherId}.pdf`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        } else {
          // Open in new tab for preview
          window.open(url, '_blank');
        }

        window.URL.revokeObjectURL(url);
      } else {
        throw new Error('Failed to generate PDF');
      }
    } catch (err: any) {
      console.error('PDF generation error:', err);
      
      let errorMessage = 'Failed to generate PDF';
      let errorType: 'error' | 'warning' | 'info' = 'error';

      if (err.response?.status === 403) {
        errorMessage = 'You do not have permission to generate PDFs for this voucher';
        errorType = 'warning';
      } else if (err.response?.status === 404) {
        errorMessage = 'Voucher not found';
        errorType = 'warning';
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError({ message: errorMessage, type: errorType });
    } finally {
      setIsGenerating(false);
    }
  };

  const renderButton = () => {
    const buttonProps = {
      onClick: handleClick,
      disabled: disabled || isGenerating,
      size,
      className,
      ...(variant === 'icon' && { 
        'aria-label': `Generate ${voucherType} PDF` 
      })
    };

    const icon = isGenerating ? (
      <CircularProgress size={size === 'small' ? 16 : 20} />
    ) : (
      <PdfIcon />
    );

    if (variant === 'icon') {
      return (
        <Tooltip title={`Generate PDF for ${voucherType} ${voucherNumber || voucherId}`}>
          <IconButton {...buttonProps}>
            {icon}
          </IconButton>
        </Tooltip>
      );
    }

    return (
      <Button
        {...buttonProps}
        variant="outlined"
        startIcon={icon}
      >
        {isGenerating ? 'Generating...' : 'Generate PDF'}
      </Button>
    );
  };

  const renderMenu = () => (
    <Menu
      anchorEl={anchorEl}
      open={open}
      onClose={handleClose}
      PaperProps={{
        elevation: 3,
        sx: {
          minWidth: 180,
          '& .MuiMenuItem-root': {
            fontSize: '0.875rem',
          },
        },
      }}
    >
      <MenuItem onClick={handlePreviewPDF} disabled={isGenerating}>
        <PreviewIcon sx={{ mr: 1 }} />
        Preview PDF
      </MenuItem>
      <MenuItem onClick={handleDownloadPDF} disabled={isGenerating}>
        <DownloadIcon sx={{ mr: 1 }} />
        Download PDF
      </MenuItem>
    </Menu>
  );

  const renderMenuButton = () => (
    <Tooltip title="PDF Options">
      <IconButton
        onClick={handleClick}
        disabled={disabled || isGenerating}
        size={size}
        className={className}
      >
        {isGenerating ? (
          <CircularProgress size={size === 'small' ? 16 : 20} />
        ) : (
          <MoreIcon />
        )}
      </IconButton>
    </Tooltip>
  );

  return (
    <Box component="span" className="voucher-pdf-button">
      {variant === 'menu' ? renderMenuButton() : renderButton()}
      {variant === 'menu' && renderMenu()}
      
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setError(null)} 
          severity={error?.type || 'error'}
          variant="filled"
        >
          {error?.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default VoucherPDFButton;