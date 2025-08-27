// Credit Note Page - Refactored using shared DRY logic with 40:60 split layout
import React from 'react';
import { Box, Button, TextField, Typography, Grid, Alert, CircularProgress, Container, Autocomplete, createFilterOptions, InputAdornment, Tooltip, Modal, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Add, Visibility, Edit } from '@mui/icons-material';
import AddCustomerModal from '../../../components/AddCustomerModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords, getVoucherStyles, parseRateField, formatRateField } from '../../../utils/voucherUtils';

const CreditNotePage: React.FC = () => {
  const config = getVoucherConfig('credit-note');
  const voucherStyles = getVoucherStyles();
  
  const {
    // State
    mode,
    isLoading,
    showAddCustomerModal,
    setShowAddCustomerModal,
    addCustomerLoading,
    setAddCustomerLoading,
    showFullModal,
    contextMenu,
    searchTerm,
    setSearchTerm,
    fromDate,
    setFromDate,
    toDate,
    setToDate,
    filteredVouchers,

    // Form
    control,
    handleSubmit,
    watch,
    setValue,
    reset,
    errors,

    // Data
    voucherList,
    customerList,
    sortedVouchers,

    // Mutations
    createMutation,
    updateMutation,

    // Event handlers
    handleCreate,
    handleEdit,
    handleView,
    handleSubmitForm,
    handleContextMenu,
    handleCloseContextMenu: handleContextMenuClose,
    handleSearch,
    handleModalOpen,
    handleModalClose,
    handleGeneratePDF,
    handleDelete,
    refreshMasterData,
    getAmountInWords,

    // Utilities
    isViewMode,
  } = useVoucherPage(config);

  // Watch form values
  const watchedValues = watch();
  const totalAmount = watchedValues?.total_amount || 0;

  // Combined customer options for autocomplete
  const customerFilter = createFilterOptions();

  // Handle voucher click to load details
  const handleVoucherClick = (voucher: any) => {
    // Load the selected voucher into the form
    reset(voucher);
    // Set the form with the voucher data
    Object.keys(voucher).forEach(key => {
      setValue(key, voucher[key]);
    });
  };

  // Handle customer creation success
  const handleCustomerCreated = async (newCustomer: any): Promise<void> => {
    setValue('customer_id', newCustomer.id);
    refreshMasterData();
  };

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Grid container spacing={3}>
        {/* Left side - Voucher List (40%) */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Paper sx={{ p: 2, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Credit Notes</Typography>
              <VoucherHeaderActions
                mode="create"
                voucherType="Credit Note"
                voucherRoute="/vouchers/financial-vouchers/credit-note"
                onModalOpen={handleModalOpen}
              />
            </Box>

            {isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Sr.</TableCell>
                      <TableCell>Voucher #</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Customer</TableCell>
                      <TableCell>Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sortedVouchers.slice(0, 7).map((voucher: any, index: number) => (
                      <TableRow 
                        key={voucher.id}
                        onClick={() => handleVoucherClick(voucher)}
                        onContextMenu={(e) => handleContextMenu(e, voucher)}
                        sx={{ 
                          cursor: 'pointer',
                          '&:hover': { bgcolor: 'action.hover' }
                        }}
                      >
                        <TableCell>{index + 1}</TableCell>
                        <TableCell>{voucher.voucher_number}</TableCell>
                        <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          {customerList?.find((c: any) => c.id === voucher.customer_id)?.name || 'N/A'}
                        </TableCell>
                        <TableCell>₹{voucher.total_amount?.toFixed(2) || '0.00'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Right side - Voucher Form (60%) */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Paper sx={{ p: 3, height: 'calc(100vh - 120px)', overflow: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'} Credit Note
              </Typography>
              {mode !== 'create' && (
                <Box>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    onClick={() => handleGeneratePDF()}
                    sx={{ mr: 1 }}
                  >
                    Generate PDF
                  </Button>
                </Box>
              )}
            </Box>

            {(createMutation.isPending || updateMutation.isPending) && (
              <Box display="flex" justifyContent="center" my={2}>
                <CircularProgress />
              </Box>
            )}

            <Box 
              component="form" 
              onSubmit={handleSubmit(handleSubmitForm)} 
              sx={{ 
                mt: 3,
                ...voucherStyles.formContainer
              }}
            >
              <Grid container spacing={3}>
                <Grid size={6}>
                  <TextField
                    {...control.register('voucher_number')}
                    label="Credit Note Number"
                    fullWidth
                    disabled={true}
                    sx={voucherStyles.centerField}
                    InputProps={{
                      readOnly: true,
                      style: { textAlign: 'center', fontWeight: 'bold' }
                    }}
                  />
                </Grid>
                <Grid size={6}>
                  <TextField
                    {...control.register('date')}
                    label="Date"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    sx={voucherStyles.centerField}
                    disabled={isViewMode}
                  />
                </Grid>

                <Grid size={12}>
                  <Autocomplete
                    options={customerList || []}
                    getOptionLabel={(option) => option.name || ''}
                    value={customerList?.find((c: any) => c.id === watch('customer_id')) || null}
                    onChange={(_, newValue) => {
                      setValue('customer_id', newValue?.id || null);
                    }}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Customer"
                        required
                        disabled={isViewMode}
                        error={!!errors.customer_id}
                        helperText={errors.customer_id?.message?.toString()}
                        InputProps={{
                          ...params.InputProps,
                          endAdornment: (
                            <>
                              {!isViewMode && (
                                <Tooltip title="Add New Customer">
                                  <Button
                                    size="small"
                                    onClick={() => setShowAddCustomerModal(true)}
                                    sx={{ minWidth: 'auto', p: 0.5 }}
                                  >
                                    <Add fontSize="small" />
                                  </Button>
                                </Tooltip>
                              )}
                              {params.InputProps.endAdornment}
                            </>
                          ),
                        }}
                      />
                    )}
                    disabled={isViewMode}
                  />
                </Grid>

                <Grid size={6}>
                  <TextField
                    {...control.register('total_amount')}
                    label="Total Amount"
                    type="number"
                    fullWidth
                    required
                    disabled={isViewMode}
                    sx={voucherStyles.centerField}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                    }}
                  />
                </Grid>

                <Grid size={6}>
                  <TextField
                    {...control.register('reference')}
                    label="Reference"
                    fullWidth
                    disabled={isViewMode}
                    sx={voucherStyles.centerField}
                  />
                </Grid>

                <Grid size={12}>
                  <TextField
                    {...control.register('notes')}
                    label="Notes"
                    fullWidth
                    multiline
                    rows={3}
                    disabled={isViewMode}
                  />
                </Grid>

                {totalAmount > 0 && (
                  <Grid size={12}>
                    <Alert severity="info">
                      <Typography variant="body2">
                        Amount in words: {getAmountInWords(totalAmount)}
                      </Typography>
                    </Alert>
                  </Grid>
                )}

                {!isViewMode && (
                  <Grid size={12}>
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                      <Button
                        type="submit"
                        variant="contained"
                        disabled={createMutation.isPending || updateMutation.isPending}
                      >
                        {mode === 'create' ? 'Create' : 'Update'} Credit Note
                      </Button>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Add Customer Modal */}
      <AddCustomerModal
        open={showAddCustomerModal}
        onClose={() => setShowAddCustomerModal(false)}
        onAdd={handleCustomerCreated}
        loading={addCustomerLoading}
      />

      {/* Context Menu */}
      <VoucherContextMenu
        voucherType="credit-note"
        contextMenu={contextMenu}
        onClose={handleContextMenuClose}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onPrint={() => handleGeneratePDF()}
      />

      {/* Voucher List Modal */}
      <VoucherListModal
        open={showFullModal}
        onClose={handleModalClose}
        vouchers={filteredVouchers}
        voucherType="Credit Note"
        onVoucherClick={handleView}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onGeneratePDF={handleGeneratePDF}
      />
    </Container>
  );
};

export default CreditNotePage;