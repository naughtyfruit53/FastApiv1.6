// Contra Voucher Page - Refactored using VoucherLayout
import React from 'react';
import { Box, Button, TextField, Typography, Grid, Alert, CircularProgress, Container, InputAdornment, Tooltip, Modal, Autocomplete, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { Visibility, Edit } from '@mui/icons-material';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import VoucherLayout from '../../../components/VoucherLayout';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, getVoucherStyles, parseRateField, formatRateField } from '../../../utils/voucherUtils';

const ContraVoucher: React.FC = () => {
  const config = getVoucherConfig('contra-voucher');
  const voucherStyles = getVoucherStyles();
  
  const {
    // State
    mode,
    setMode,
    isLoading,
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
    vendorList,
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
  const totalAmount = watchedValues?.amount || 0;

  // Handle voucher click to load details
  const handleVoucherClick = (voucher: any) => {
    // Load the selected voucher into the form
    reset(voucher);
    // Set the form with the voucher data
    Object.keys(voucher).forEach(key => {
      setValue(key, voucher[key]);
    });
  };

  // Bank account options (these would typically come from a master data service)
  const bankAccounts = [
    'Bank Account 1',
    'Bank Account 2', 
    'Cash Account',
    'Petty Cash',
    'Current Account - SBI',
    'Savings Account - HDFC',
    'Fixed Deposit Account'
  ];

  // Transfer types for contra vouchers
  const transferTypes = [
    'Bank to Bank',
    'Bank to Cash',
    'Cash to Bank',
    'Cash to Cash'
  ];

  // Index Content - Left Panel (40%)
  const indexContent = (
    <TableContainer sx={{ maxHeight: 400 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Voucher No.</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Date</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Type</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Amount</TableCell>
            <TableCell align="right" sx={{ fontSize: 12, fontWeight: 'bold', p: 0, width: 40 }}></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(sortedVouchers?.length === 0) ? (
            <TableRow>
              <TableCell colSpan={5} align="center">No contra vouchers available</TableCell>
            </TableRow>
          ) : (
            sortedVouchers?.slice(0, 7).map((voucher: any) => (
              <TableRow 
                key={voucher.id} 
                hover
                onContextMenu={(e) => { e.preventDefault(); handleContextMenu(e, voucher); }}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }} onClick={() => handleVoucherClick(voucher)}>
                  {voucher.voucher_number}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  {new Date(voucher.date).toLocaleDateString()}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  {voucher.transfer_type || 'N/A'}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  ₹{voucher.amount?.toFixed(2) || '0.00'}
                </TableCell>
                <TableCell align="right" sx={{ fontSize: 11, p: 0 }}>
                  <VoucherContextMenu
                    voucher={voucher}
                    voucherType="Contra Voucher"
                    onView={() => handleView(voucher.id)}
                    onEdit={() => handleEdit(voucher.id)}
                    onDelete={() => handleDelete(voucher)}
                    onPrint={() => handleGeneratePDF()}
                    showKebab={true}
                    onClose={() => {}}
                  />
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );

  // Form Content - Right Panel (60%)
  const formContent = (
    <Box>
      {/* Header Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ fontSize: 18, fontWeight: 'bold', textAlign: 'center', flex: 1 }}>
          Contra Voucher - {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'}
        </Typography>
        <VoucherHeaderActions
          mode={mode}
          voucherType="Contra Voucher"
          voucherRoute="/vouchers/Financial-Vouchers/contra-voucher"
          currentId={watch('id')}
        />
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
          mt: 2,
          ...voucherStyles.formContainer
        }}
      >
        <Grid container spacing={2}>
          <Grid size={6}>
            <TextField
              {...control.register('voucher_number')}
              label="Voucher Number"
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
              disabled={isViewMode}
              sx={voucherStyles.centerField}
              InputLabelProps={{
                shrink: true,
              }}
              inputProps={{ style: { textAlign: 'center' } }}
              error={!!errors.date}
              helperText={errors.date?.message?.toString()}
            />
          </Grid>

          <Grid size={6}>
            <FormControl fullWidth disabled={isViewMode}>
              <InputLabel>Transfer Type</InputLabel>
              <Select
                {...control.register('transfer_type')}
                value={watch('transfer_type') || ''}
                onChange={(e) => setValue('transfer_type', e.target.value)}
                error={!!errors.transfer_type}
                required
              >
                {transferTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid size={6}>
            <TextField
              {...control.register('amount', {
                required: 'Amount is required',
                min: { value: 0.01, message: 'Amount must be greater than 0' },
                setValueAs: (value) => parseRateField(value)
              })}
              label="Amount"
              type="number"
              fullWidth
              disabled={isViewMode}
              error={!!errors.amount}
              helperText={errors.amount?.message?.toString()}
              sx={{
                ...voucherStyles.rateField,
                ...voucherStyles.centerField
              }}
              InputProps={{
                inputProps: { 
                  step: "0.01",
                  style: { textAlign: 'center' }
                }
              }}
              onChange={(e) => {
                const value = parseRateField(e.target.value);
                setValue('amount', value);
              }}
            />
          </Grid>

          <Grid size={6}>
            <FormControl fullWidth disabled={isViewMode}>
              <InputLabel>From Account</InputLabel>
              <Select
                {...control.register('from_account')}
                value={watch('from_account') || ''}
                onChange={(e) => setValue('from_account', e.target.value)}
                error={!!errors.from_account}
                required
              >
                {bankAccounts.map((account) => (
                  <MenuItem key={account} value={account}>
                    {account}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid size={6}>
            <FormControl fullWidth disabled={isViewMode}>
              <InputLabel>To Account</InputLabel>
              <Select
                {...control.register('to_account')}
                value={watch('to_account') || ''}
                onChange={(e) => setValue('to_account', e.target.value)}
                error={!!errors.to_account}
                required
              >
                {bankAccounts.map((account) => (
                  <MenuItem key={account} value={account}>
                    {account}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid size={12}>
            <TextField
              {...control.register('reference')}
              label="Reference"
              fullWidth
              disabled={isViewMode}
              error={!!errors.reference}
              helperText={errors.reference?.message?.toString()}
              placeholder="Enter reference number or details..."
            />
          </Grid>

          <Grid size={12}>
            <TextField
              {...control.register('description')}
              label="Description"
              multiline
              rows={3}
              fullWidth
              disabled={isViewMode}
              error={!!errors.description}
              helperText={errors.description?.message?.toString()}
              placeholder="Enter transaction description..."
            />
          </Grid>

          {totalAmount > 0 && (
            <Grid size={12}>
              <TextField
                fullWidth
                label="Amount in Words"
                value={getAmountInWords(totalAmount)}
                disabled
                InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                inputProps={{ style: { fontSize: 14, textAlign: 'center' } }}
                size="small"
              />
            </Grid>
          )}

          {/* Action buttons - removed Generate PDF */}
          <Grid size={12}>
            <Box display="flex" gap={2}>
              {mode !== 'view' && (
                <Button
                  type="submit"
                  variant="contained"
                  color="success"
                  disabled={createMutation.isPending || updateMutation.isPending}
                  sx={{ fontSize: 12 }}
                >
                  Save
                </Button>
              )}
              <Button
                variant="outlined"
                onClick={handleCreate}
                sx={{ fontSize: 12 }}
              >
                Clear
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <>
      <VoucherLayout
        voucherType="Contra Vouchers"
        voucherTitle="Contra Voucher"
        indexContent={indexContent}
        formContent={formContent}
        onShowAll={handleModalOpen}
        showAllButton={true}
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showFullModal}
            onClose={handleModalClose}
            voucherType="Contra Vouchers"
            vouchers={sortedVouchers || []}
            onVoucherClick={handleVoucherClick}
            onEdit={handleEdit}
            onView={handleView}
            onDelete={handleDelete}
            onGeneratePDF={handleGeneratePDF}
            customerList={customerList}
            vendorList={vendorList}
          />
        }
      />
      
      {/* Keep context menu for right-click functionality */}
      <VoucherContextMenu
        voucherType="Contra Voucher"
        contextMenu={contextMenu}
        onClose={handleContextMenuClose}
        onEdit={(id) => {
          handleEdit(id);
          handleContextMenuClose();
        }}
        onView={(id) => {
          handleView(id);
          handleContextMenuClose();
        }}
        onDelete={(id) => {
          handleDelete(id);
          handleContextMenuClose();
        }}
      />
    </>
  );
};

export default ContraVoucher;