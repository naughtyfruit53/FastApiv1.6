// frontend/src/components/PDFSystemStatus.tsx

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Stack,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  PictureAsPdf as PDFIcon,
  Business as CompanyIcon,
  AttachFile as FileIcon,
  Security as SecurityIcon
} from '@mui/icons-material';

interface PDFSystemStatusProps {
  companyLogo?: string | null;
  hasProductFiles?: boolean;
  voucherCount?: number;
  rbacEnabled?: boolean;
  className?: string;
}

const PDFSystemStatus: React.FC<PDFSystemStatusProps> = ({
  companyLogo,
  hasProductFiles = false,
  voucherCount = 0,
  rbacEnabled = true,
  className = ''
}) => {
  const features = [
    {
      name: 'Company Logo',
      status: companyLogo ? 'ready' : 'missing',
      description: companyLogo 
        ? 'Company logo will appear on all PDF vouchers' 
        : 'Upload a company logo to brand your vouchers',
      icon: CompanyIcon
    },
    {
      name: 'Product Files',
      status: hasProductFiles ? 'ready' : 'none',
      description: hasProductFiles 
        ? 'Product files are attached and ready for vouchers'
        : 'No product files attached (optional)',
      icon: FileIcon
    },
    {
      name: 'Voucher PDF Generation',
      status: 'ready',
      description: 'Generate professional PDFs for all voucher types',
      icon: PDFIcon
    },
    {
      name: 'Security & RBAC',
      status: rbacEnabled ? 'enabled' : 'disabled',
      description: rbacEnabled 
        ? 'Role-based access control is enabled for PDF generation'
        : 'Basic security enabled',
      icon: SecurityIcon
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
      case 'enabled':
        return 'success';
      case 'missing':
      case 'disabled':
        return 'error';
      case 'none':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
      case 'enabled':
        return <CheckIcon color="success" />;
      case 'missing':
      case 'disabled':
        return <ErrorIcon color="error" />;
      case 'none':
        return <WarningIcon color="warning" />;
      default:
        return <CheckIcon />;
    }
  };

  const getOverallStatus = () => {
    const criticalMissing = !companyLogo;
    if (criticalMissing) return 'warning';
    return 'success';
  };

  const overallStatus = getOverallStatus();

  return (
    <Card className={className} sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <PDFIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="div">
            PDF Generation System Status
          </Typography>
          <Box sx={{ ml: 'auto' }}>
            <Chip
              label={overallStatus === 'success' ? 'Ready' : 'Setup Needed'}
              color={overallStatus as any}
              variant="filled"
              size="small"
            />
          </Box>
        </Box>

        {overallStatus === 'warning' && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Upload a company logo to create professional-looking voucher PDFs with your branding.
          </Alert>
        )}

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Your voucher PDF generation system supports Purchase, Sales, and Pre-Sales vouchers with 
          Indian formatting, tax calculations, and professional styling.
        </Typography>

        <Divider sx={{ my: 2 }} />

        <List dense>
          {features.map((feature, index) => (
            <ListItem key={index} disablePadding sx={{ mb: 1 }}>
              <ListItemIcon sx={{ minWidth: 36 }}>
                {getStatusIcon(feature.status)}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <Typography variant="body2" fontWeight="medium">
                      {feature.name}
                    </Typography>
                    <Chip
                      label={
                        feature.status === 'ready' ? 'Ready' :
                        feature.status === 'enabled' ? 'Enabled' :
                        feature.status === 'missing' ? 'Missing' :
                        feature.status === 'disabled' ? 'Disabled' :
                        'None'
                      }
                      size="small"
                      color={getStatusColor(feature.status) as any}
                      variant="outlined"
                    />
                  </Stack>
                }
                secondary={
                  <Typography variant="caption" color="text.secondary">
                    {feature.description}
                  </Typography>
                }
              />
            </ListItem>
          ))}
        </List>

        {voucherCount > 0 && (
          <Box sx={{ mt: 2 }}>
            <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
              You have {voucherCount} voucher{voucherCount !== 1 ? 's' : ''} that can be converted to PDF.
            </Alert>
          </Box>
        )}

        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Supported formats: A4 • Indian currency formatting • GST calculations • Multi-page support
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PDFSystemStatus;