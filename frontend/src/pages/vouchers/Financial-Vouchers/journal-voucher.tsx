// Journal Voucher Page - Refactored using VoucherLayout
import React from 'react';
import { Box, Button, TextField, Typography, Grid, Alert, CircularProgress, Container, Autocomplete, InputAdornment, Tooltip, Modal, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Visibility, Edit } from '@mui/icons-material';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import VoucherLayout from '../../../components/VoucherLayout';
import EntitySelector from '../../../components/EntitySelector';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords, getVoucherStyles, parseRateField, formatRateField } from '../../../utils/voucherUtils';

const JournalVoucher: React.FC = () => {
  const config = getVoucherConfig('journal-voucher');
  const voucherStyles = getVoucherStyles();
  
  const {
    // State
    mode,
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
  const totalAmount = watchedValues?.total_amount || 0;

  // Handle voucher click to load details
  const handleVoucherClick = (voucher: any) => {
    // Load the selected voucher into the form
    reset(voucher);
    // Set the form with the voucher data
    Object.keys(voucher).forEach(key => {
      setValue(key, voucher[key]);
    });
  };

  // Index Content - Left Panel (40%)
  const indexContent = (
    <TableContainer sx={{ maxHeight: 400 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Voucher No.</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Date</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Debit</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Credit</TableCell>
            <TableCell align="right" sx={{ fontSize: 12, fontWeight: 'bold', p: 0, width: 40 }}></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(sortedVouchers?.length === 0) ? (
            <TableRow>
              <TableCell colSpan={5} align="center">No journal vouchers available</TableCell>
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
                  ₹{voucher.debit_amount?.toFixed(2) || '0.00'}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  ₹{voucher.credit_amount?.toFixed(2) || '0.00'}
                </TableCell>
                <TableCell align="right" sx={{ fontSize: 11, p: 0 }}>
                  <VoucherContextMenu
                    voucher={voucher}
                    voucherType="Journal Voucher"
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
          Journal Voucher - {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'}
        </Typography>
        <VoucherHeaderActions
          mode={mode}
          voucherType="Journal Voucher"
          voucherRoute="/vouchers/Financial-Vouchers/journal-voucher"
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
              helperText={errors.date?.message as string}
            />
          </Grid>

          <Grid size={12}>
            <EntitySelector
              name="debit_account"
              control={control}
              label="Debit Account"
              entityTypes={['ExpenseAccount', 'Customer', 'Vendor', 'Employee']}
              allowTypeSelection={true}
              required={true}
              disabled={isViewMode}
            />
          </Grid>

          <Grid size={6}>
            <TextField
              {...control.register('debit_amount', {
                required: 'Debit amount is required',
                min: { value: 0.01, message: 'Amount must be greater than 0' },
                setValueAs: (value) => parseRateField(value)
              })}
              label="Debit Amount"
              type="number"
              fullWidth
              disabled={isViewMode}
              error={!!errors.debit_amount}
              helperText={errors.debit_amount?.message as string}
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
                setValue('debit_amount', value);
                // Auto-set credit amount to match (for balanced entry)
                setValue('credit_amount', value);
              }}
            />
          </Grid>

          <Grid size={6}>
            <TextField
              {...control.register('credit_amount', {
                required: 'Credit amount is required',
                min: { value: 0.01, message: 'Amount must be greater than 0' },
                setValueAs: (value) => parseRateField(value)
              })}
              label="Credit Amount"
              type="number"
              fullWidth
              disabled={isViewMode}
              error={!!errors.credit_amount}
              helperText={errors.credit_amount?.message as string}
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
                setValue('credit_amount', value);
                // Auto-set debit amount to match (for balanced entry)
                setValue('debit_amount', value);
              }}
            />
          </Grid>

          <Grid size={12}>
            <EntitySelector
              name="credit_account"
              control={control}
              label="Credit Account"
              entityTypes={['ExpenseAccount', 'Customer', 'Vendor', 'Employee']}
              allowTypeSelection={true}
              required={true}
              disabled={isViewMode}
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
              helperText={errors.description?.message as string}
              placeholder="Enter transaction description..."
            />
          </Grid>

          {(watch('debit_amount') > 0 || watch('credit_amount') > 0) && (
            <Grid size={12}>
              <TextField
                fullWidth
                label="Amount in Words"
                value={getAmountInWords(Math.max(watch('debit_amount') || 0, watch('credit_amount') || 0))}
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
        voucherType="Journal Vouchers"
        voucherTitle="Journal Voucher"
        indexContent={indexContent}
        formContent={formContent}
        onShowAll={handleModalOpen}
        showAllButton={true}
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showFullModal}
            onClose={handleModalClose}
            voucherType="Journal Vouchers"
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
        voucherType="Journal Voucher"
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

export default JournalVoucher;