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
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  TextField
} from '@mui/material';
import {
  PictureAsPdf as PdfIcon,
  Download as DownloadIcon,
  Preview as PreviewIcon,
  MoreVert as MoreIcon,
  Email as EmailIcon,
  Send as SendIcon
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
  // New props for email functionality
  vendorEmail?: string;
  customerEmail?: string;
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
  className = '',
  vendorEmail,
  customerEmail
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [error, setError] = useState<PDFError | null>(null);
  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  const [isEmailSetup, setIsEmailSetup] = useState(false);
  const [emailSending, setEmailSending] = useState(false);
  const [emailSubject, setEmailSubject] = useState('');
  const [emailBody, setEmailBody] = useState('');
  
  // Check if email is configured on component mount
  React.useEffect(() => {
    const checkEmailSetup = async () => {
      try {
        const response = await api.get('/mail/tokens');
        setIsEmailSetup(response.data && response.data.length > 0);
      } catch (err) {
        setIsEmailSetup(false);
      }
    };
    checkEmailSetup();
  }, []);

  const getRecipientEmail = () => {
    // For purchase vouchers, send to vendor
    // For sales vouchers, send to customer
    if (['purchase'].includes(voucherType)) {
      return vendorEmail;
    } else if (['sales', 'quotation', 'sales_order', 'proforma'].includes(voucherType)) {
      return customerEmail;
    }
    return null;
  };

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

  const showEmailPrompt = async () => {
    if (!isEmailSetup) {
      setError({ 
        message: 'Email not configured. Please setup your email account first.', 
        type: 'warning' 
      });
      return;
    }

    const recipientEmail = getRecipientEmail();
    if (!recipientEmail) {
      setError({ 
        message: 'Email ID not available for this contact.', 
        type: 'warning' 
      });
      return;
    }

    // Try to get email template from API
    try {
      const entityType = ['purchase'].includes(voucherType) ? 'vendor' : 'customer';
      const voucherTypeNormalized = voucherType.replace('-', '_');
      
      const response = await api.get(
        `/api/v1/voucher-email-templates/default/${voucherTypeNormalized}/${entityType}`
      );
      
      if (response.data) {
        // Use template with variable substitution
        const subject = response.data.subject_template
          .replace('{voucher_number}', voucherNumber || `#${voucherId}`)
          .replace('{organization_name}', 'Your Company'); // TODO: Get actual org name
        
        const body = response.data.body_template
          .replace('{vendor_name}', 'Vendor Name') // TODO: Get actual name
          .replace('{customer_name}', 'Customer Name') // TODO: Get actual name
          .replace('{voucher_number}', voucherNumber || `#${voucherId}`)
          .replace('{voucher_date}', new Date().toLocaleDateString())
          .replace('{total_amount}', 'Amount') // TODO: Get actual amount
          .replace('{organization_name}', 'Your Company'); // TODO: Get actual org name
        
        setEmailSubject(subject);
        setEmailBody(body);
      }
    } catch (err) {
      // Fallback to default if API call fails
      const voucherTypeLabel = voucherType.charAt(0).toUpperCase() + voucherType.slice(1).replace('_', ' ');
      setEmailSubject(`${voucherTypeLabel} - ${voucherNumber || `#${voucherId}`}`);
      setEmailBody(`Dear Customer/Vendor,\n\nPlease find attached the ${voucherTypeLabel.toLowerCase()} document.\n\nThank you for your business.\n\nBest regards,\nYour Company Team`);
    }
    
    setEmailDialogOpen(true);
  };

  const sendEmailWithPDF = async () => {
    setEmailSending(true);
    try {
      const recipientEmail = getRecipientEmail();
      if (!recipientEmail) {
        throw new Error('Recipient email not available');
      }

      // For now, send email without PDF attachment
      // In a production system, you'd want to implement proper attachment support
      const emailData = {
        to_addresses: [recipientEmail],
        subject: emailSubject,
        body_html: `<p>${emailBody.replace(/\n/g, '<br>')}</p>`,
        body_text: emailBody
      };

      // Get user's first email token
      const tokensResponse = await api.get('/mail/tokens');
      if (!tokensResponse.data || tokensResponse.data.length === 0) {
        throw new Error('No email account configured');
      }

      const tokenId = tokensResponse.data[0].id;
      
      // Send email using existing endpoint
      const formData = new FormData();
      formData.append('to_addresses', JSON.stringify(emailData.to_addresses));
      formData.append('cc_addresses', JSON.stringify([]));
      formData.append('bcc_addresses', JSON.stringify([]));
      formData.append('subject', emailData.subject);
      formData.append('body_html', emailData.body_html);
      formData.append('body_text', emailData.body_text);

      await api.post(`/mail/tokens/${tokenId}/emails/send`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setEmailDialogOpen(false);
      setError({ message: 'Email sent successfully! (PDF attachment will be added in future update)', type: 'info' });
      
    } catch (err: any) {
      console.error('Email sending error:', err);
      setError({ 
        message: err.response?.data?.detail || err.message || 'Failed to send email', 
        type: 'error' 
      });
    } finally {
      setEmailSending(false);
    }
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

        // Extract filename from Content-Disposition header
        let filename = `voucher_${voucherId}.pdf`; // Fallback filename
        const contentDisposition = response.headers['content-disposition'];
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="?([^"]+)"?/);
          if (match && match[1]) {
            filename = match[1];
          }
        }

        if (download) {
          // Force download with extracted filename
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          
          // Show email prompt after successful PDF generation
          setTimeout(() => showEmailPrompt(), 500);
        } else {
          // Open in new tab for preview
          window.open(url, '_blank');
          
          // Show email prompt after successful PDF generation
          setTimeout(() => showEmailPrompt(), 500);
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

      {/* Email Dialog */}
      <Dialog 
        open={emailDialogOpen} 
        onClose={() => setEmailDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <EmailIcon />
          Send Voucher via Email
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Send this voucher to: <strong>{getRecipientEmail()}</strong>
            </Typography>
            
            <TextField
              fullWidth
              label="Subject"
              value={emailSubject}
              onChange={(e) => setEmailSubject(e.target.value)}
              sx={{ mb: 2 }}
              variant="outlined"
            />
            
            <TextField
              fullWidth
              multiline
              rows={6}
              label="Message"
              value={emailBody}
              onChange={(e) => setEmailBody(e.target.value)}
              variant="outlined"
              placeholder="Enter your message here..."
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button 
            onClick={() => setEmailDialogOpen(false)}
            disabled={emailSending}
          >
            Cancel
          </Button>
          <Button 
            variant="contained"
            onClick={sendEmailWithPDF}
            disabled={emailSending || !emailSubject.trim()}
            startIcon={emailSending ? <CircularProgress size={16} /> : <SendIcon />}
          >
            {emailSending ? 'Sending...' : 'Send Email'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default VoucherPDFButton;