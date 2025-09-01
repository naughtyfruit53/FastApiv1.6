// frontend/src/components/VoucherLayout.tsx
// Enhanced VoucherLayout component with comprehensive UI improvements
import React from 'react';
import { Container, Grid, Paper, Box, Typography, Button, Pagination } from '@mui/material';
import { getVoucherStyles } from '../utils/voucherUtils';
interface VoucherLayoutProps {
  voucherType: string;
  voucherTitle?: string;
  indexContent: React.ReactNode;
  formContent: React.ReactNode;
  onShowAll?: () => void;
  showAllButton?: boolean;
  // Enhanced pagination props
  pagination?: {
    currentPage: number;
    totalPages: number;
    onPageChange: (_page: number) => void;
    totalItems: number;
  };
  // Additional props for modal functionality
  showModal?: boolean;
  onCloseModal?: () => void;
  modalContent?: React.ReactNode;
  // Center alignment control
  centerAligned?: boolean;
}
const VoucherLayout: React.FC<VoucherLayoutProps> = ({
  voucherType,
  voucherTitle: _voucherTitle,
  indexContent,
  formContent,
  onShowAll,
  showAllButton = true,
  pagination,
  showModal: _showModal = false,
  onCloseModal: _onCloseModal,
  modalContent,
  centerAligned: _centerAligned = true
}) => {
  const voucherStyles = getVoucherStyles();
  return (
    <>
      <Box sx={{ 
        ...voucherStyles.edgeToEdgeContainer, 
        width: '100%',
        maxWidth: '100%', 
        overflowX: 'hidden',
        boxSizing: 'border-box'
      }}>
        <Container 
          maxWidth={false} 
          sx={{ 
            padding: 0, 
            margin: 0, 
            width: '100%',
            maxWidth: '100%', 
            overflowX: 'hidden',
            boxSizing: 'border-box'
          }}
        >
          {/* Remove redundant top-level title per requirements */}
          <Grid container spacing={0} sx={{ 
            minHeight: '100vh',
            width: '100%',
            margin: 0,
            '& .MuiGrid-item': {
              paddingLeft: 0,
              paddingTop: 0
            }
          }}>
            {/* Index Panel - approximately 40% */}
            <Grid size={{ xs: 12, md: 5, lg: 4 }} sx={{ 
              borderRight: '1px solid #e0e0e0',
              maxWidth: { xs: '100%', md: '40%', lg: '33.333%' }
            }}>
              <Paper sx={{ 
                p: 1,
                height: '100vh',
                borderRadius: 0,
                boxShadow: 'none',
                overflow: 'auto',
                width: '100%',
                ...voucherStyles.indexContainer
              }}>
                <Box 
                  display="flex" 
                  justifyContent="space-between" 
                  alignItems="center" 
                  mb={1}
                  sx={{ width: '100%' }}
                >
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontSize: 18, 
                      fontWeight: 'bold', 
                      flex: 1,
                      ...voucherStyles.centerText
                    }}
                  >
                    {voucherType}
                  </Typography>
                  {showAllButton && (
                    <Button 
                      variant="outlined" 
                      size="small" 
                      onClick={onShowAll}
                      sx={{ ml: 1 }}
                    >
                      Show All
                    </Button>
                  )}
                </Box>
                {/* Index Content */}
                <Box sx={{ width: '100%' }}>
                  {indexContent}
                </Box>
                {/* Pagination for index if provided */}
                {pagination && (
                  <Box sx={voucherStyles.paginationContainer}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
                      <Typography variant="caption" sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                        Page {pagination.currentPage} of {pagination.totalPages} 
                        ({pagination.totalItems} total items)
                      </Typography>
                      <Pagination
                        count={pagination.totalPages}
                        page={pagination.currentPage}
                        onChange={(_, page) => pagination.onPageChange(page)}
                        size="small"
                        color="primary"
                        showFirstButton
                        showLastButton
                      />
                    </Box>
                  </Box>
                )}
              </Paper>
            </Grid>
            {/* Form Panel - approximately 60% */}
            <Grid size={{ xs: 12, md: 7, lg: 8 }} sx={{
              maxWidth: { xs: '100%', md: '60%', lg: '66.667%' }
            }}>
              <Paper sx={{ 
                p: 1,
                height: '100vh',
                borderRadius: 0,
                boxShadow: 'none',
                overflow: 'auto',
                width: '100%',
                ...voucherStyles.formContainer
              }}>
                {formContent}
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
      {/* Modal Content */}
      {modalContent}
    </>
  );
};
export default VoucherLayout;