// frontend/src/components/VoucherPageWithPDF.tsx

/**
 * Example integration of PDF generation into voucher pages
 * This shows how to integrate the PDF button with existing voucher components
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  Grid,
  Chip
} from '@mui/material';
import VoucherHeaderActions from './VoucherHeaderActions';
import VoucherPDFButton from './VoucherPDFButton';
import PDFSystemStatus from './PDFSystemStatus';
import usePDFGeneration from '../hooks/usePDFGeneration';

interface VoucherPageWithPDFProps {
  voucherType: 'purchase' | 'sales' | 'quotation' | 'sales_order' | 'proforma';
  voucherId?: number;
  voucherNumber?: string;
  voucherData?: any;
  mode: 'create' | 'edit' | 'view';
  onEdit?: () => void;
  onCreate?: () => void;
  onCancel?: () => void;
  companyLogo?: string | null;
  hasProductFiles?: boolean;
}

const VoucherPageWithPDF: React.FC<VoucherPageWithPDFProps> = ({
  voucherType,
  voucherId,
  voucherNumber,
  voucherData,
  mode,
  onEdit,
  onCreate,
  onCancel,
  companyLogo,
  hasProductFiles = false
}) => {
  const { isGenerating, error, previewPDF, downloadPDF, clearError } = usePDFGeneration();

  const handleQuickPreview = async () => {
    if (voucherId) {
      await previewPDF(voucherType, voucherId);
    }
  };

  const handleQuickDownload = async () => {
    if (voucherId) {
      await downloadPDF(voucherType, voucherId, voucherNumber);
    }
  };

  const getVoucherTypeLabel = (type: string) => {
    switch (type) {
      case 'purchase': return 'Purchase Voucher';
      case 'sales': return 'Sales Invoice';
      case 'quotation': return 'Quotation';
      case 'sales_order': return 'Sales Order';
      case 'proforma': return 'Proforma Invoice';
      default: return 'Voucher';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header with PDF Actions */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography variant="h5" component="h1" gutterBottom>
              {getVoucherTypeLabel(voucherType)}
              {voucherNumber && (
                <Chip 
                  label={voucherNumber} 
                  size="small" 
                  sx={{ ml: 2 }}
                  variant="outlined"
                />
              )}
            </Typography>
            {mode === 'view' && (
              <Typography variant="body2" color="text.secondary">
                View and manage your {getVoucherTypeLabel(voucherType).toLowerCase()}
              </Typography>
            )}
          </Box>
          
          {/* PDF Generation Buttons */}
          {mode === 'view' && voucherId && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <VoucherPDFButton
                voucherType={voucherType}
                voucherId={voucherId}
                voucherNumber={voucherNumber}
                variant="button"
                size="small"
                disabled={isGenerating}
              />
              <VoucherPDFButton
                voucherType={voucherType}
                voucherId={voucherId}
                voucherNumber={voucherNumber}
                variant="menu"
                size="small"
                disabled={isGenerating}
              />
            </Box>
          )}
        </Box>

        <VoucherHeaderActions
          mode={mode}
          voucherType={getVoucherTypeLabel(voucherType)}
          voucherRoute={`/vouchers/${voucherType}`}
          currentId={voucherId}
          onEdit={onEdit}
          onCreate={onCreate}
          onCancel={onCancel}
          voucherNumber={voucherNumber}
          showPDFButton={true}
        />
      </Paper>

      <Grid container spacing={3}>
        {/* Main Content Area */}
        <Grid item xs={12} md={8}>
          <Paper elevation={1} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Voucher Details
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {/* Your existing voucher form/display content goes here */}
            <Box sx={{ minHeight: 400 }}>
              <Typography variant="body2" color="text.secondary">
                Voucher form fields and data display would go here...
              </Typography>
              
              {voucherData && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Voucher Information:
                  </Typography>
                  <Typography variant="body2">
                    ID: {voucherData.id}<br/>
                    Status: {voucherData.status}<br/>
                    Date: {voucherData.date}<br/>
                    Total Items: {voucherData.items?.length || 0}
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Sidebar with PDF Status */}
        <Grid item xs={12} md={4}>
          <PDFSystemStatus
            companyLogo={companyLogo}
            hasProductFiles={hasProductFiles}
            voucherCount={1}
            rbacEnabled={true}
          />

          {/* Quick PDF Actions */}
          {mode === 'view' && voucherId && (
            <Paper elevation={1} sx={{ p: 2, mt: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Quick PDF Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <VoucherPDFButton
                  voucherType={voucherType}
                  voucherId={voucherId}
                  voucherNumber={voucherNumber}
                  variant="button"
                  disabled={isGenerating}
                />
              </Box>
              
              {error && (
                <Typography 
                  variant="caption" 
                  color="error" 
                  sx={{ mt: 1, display: 'block' }}
                >
                  {error}
                </Typography>
              )}
            </Paper>
          )}

          {/* Integration Tips */}
          <Paper elevation={1} sx={{ p: 2, mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              PDF Features
            </Typography>
            <Typography variant="caption" display="block" sx={{ mb: 1 }}>
              ✓ Professional A4 layout
            </Typography>
            <Typography variant="caption" display="block" sx={{ mb: 1 }}>
              ✓ Indian currency formatting
            </Typography>
            <Typography variant="caption" display="block" sx={{ mb: 1 }}>
              ✓ GST tax calculations
            </Typography>
            <Typography variant="caption" display="block" sx={{ mb: 1 }}>
              ✓ Company logo integration
            </Typography>
            <Typography variant="caption" display="block">
              ✓ Multi-page support
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default VoucherPageWithPDF;