import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Grid, CircularProgress, Container, Autocomplete, InputAdornment, Tooltip, Modal, FormControl, InputLabel, Select, MenuItem, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Add, Visibility, Edit } from '@mui/icons-material';
import EntitySelector from '../../../components/EntitySelector';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import VoucherLayout from '../../../components/VoucherLayout';
import SearchableDropdown from '../../../components/SearchableDropdown';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, getVoucherStyles, parseRateField, formatRateField } from '../../../utils/voucherUtils';
import { useReferenceOptions } from '../../../utils/nameRefUtils';

const PaymentVoucher: React.FC = () => {
  const config = getVoucherConfig('payment-voucher');
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
    employeeList,
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

  // Handle voucher click to load details
  const handleVoucherClick = (voucher: any) => {
    // Load the selected voucher into the form
    reset(voucher);
    // Set the form with the voucher data
    Object.keys(voucher).forEach(key => {
      setValue(key, voucher[key]);
    });
  };

  // Payment voucher specific state
  const [selectedModule, setSelectedModule] = useState<'Vendor' | 'Customer' | null>(null);
  
  const totalAmountValue = watch('total_amount');
  const selectedEntity = watch('entity'); // Now using entity instead of name_id/name_type

  // Get reference options including unpaid vouchers for the selected entity
  const referenceOptions = useReferenceOptions(
    selectedEntity?.id || null, 
    selectedEntity?.type || null
  );

  // Payment methods for payment vouchers
  const paymentMethods = [
    'Cash',
    'Bank Transfer',
    'Cheque',
    'Credit Card',
    'Debit Card',
    'Online Payment',
    'UPI',
    'Net Banking'
  ];

  // Handle entity creation success
  const handleEntityCreated = (newEntity: any) => {
    setValue('entity', {
      id: newEntity.id,
      name: newEntity.name,
      type: newEntity.type || 'Customer', // Default type
      value: newEntity.id,
      label: newEntity.name
    });
    refreshMasterData();
  };

  // Combined list of all parties (customers + vendors + employees) for unified dropdown
  const allParties = [
    ...(customerList || []).map((customer: any) => ({
      id: customer.id,
      name: customer.name,
      email: customer.email,
      type: 'Customer',
      value: customer.id,
      label: `${customer.name} (Customer)`
    })),
    ...(vendorList || []).map((vendor: any) => ({
      id: vendor.id,
      name: vendor.name,
      email: vendor.email,
      type: 'Vendor',
      value: vendor.id,
      label: `${vendor.name} (Vendor)`
    })),
    ...(employeeList || []).map((employee: any) => ({
      id: employee.id,
      name: employee.name,
      email: employee.email,
      type: 'Employee',
      value: employee.id,
      label: `${employee.name} (Employee)`
    }))
  ];

  // Index Content - Left Panel (40%)
  const indexContent = (
    <TableContainer sx={{ maxHeight: 400 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Voucher No.</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Date</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Party</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Amount</TableCell>
            <TableCell align="right" sx={{ fontSize: 12, fontWeight: 'bold', p: 0, width: 40 }}></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(sortedVouchers?.length === 0) ? (
            <TableRow>
              <TableCell colSpan={5} align="center">No payment vouchers available</TableCell>
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
                  {voucher.entity?.name || 
                   (voucher.name_type === 'Vendor' 
                    ? vendorList?.find((v: any) => v.id === voucher.name_id)?.name 
                    : customerList?.find((c: any) => c.id === voucher.name_id)?.name) || 'N/A'}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  ₹{voucher.total_amount?.toFixed(2) || '0.00'}
                </TableCell>
                <TableCell align="right" sx={{ fontSize: 11, p: 0 }}>
                  <VoucherContextMenu
                    voucher={voucher}
                    voucherType="Payment Voucher"
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
          Payment Voucher - {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'}
        </Typography>
        <VoucherHeaderActions
          mode={mode}
          voucherType="Payment Voucher"
          voucherRoute="/vouchers/Financial-Vouchers/payment-voucher"
          currentId={selectedEntity?.id}
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

          <Grid size={6}>
            <SearchableDropdown
              label="Party Name"
              options={allParties}
              value={selectedEntity?.id || null}
              onChange={(value) => {
                const party = allParties.find(p => p.id === value);
                if (party) {
                  setValue('entity', {
                    id: party.id,
                    name: party.name,
                    type: party.type,
                    value: party.id,
                    label: party.name
                  });
                }
              }}
              getOptionLabel={(option) => option.label}
              getOptionValue={(option) => option.id}
              placeholder="Select or search party..."
              noOptionsText="No parties found"
              disabled={isViewMode}
              fullWidth
              required
              error={!!errors.entity}
              helperText={errors.entity?.message as string}
            />
          </Grid>

          <Grid size={6}>
            <FormControl fullWidth disabled={isViewMode}>
              <InputLabel>Payment Method</InputLabel>
              <Select
                {...control.register('payment_method')}
                value={watch('payment_method') || ''}
                onChange={(e) => setValue('payment_method', e.target.value)}
                error={!!errors.payment_method}
                sx={{ height: 56 }} // Match height with Party Name field
              >
                {paymentMethods.map((method) => (
                  <MenuItem key={method} value={method}>
                    {method}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid size={6}>
            <Autocomplete
              freeSolo
              options={referenceOptions}
              value={watch('reference') || ''}
              onChange={(_, newValue) => setValue('reference', newValue || '')}
              disabled={isViewMode}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Reference"
                  error={!!errors.reference}
                  helperText={errors.reference?.message as string}
                />
              )}
            />
          </Grid>

          <Grid size={6}>
            <TextField
              {...control.register('total_amount', {
                required: 'Amount is required',
                min: { value: 0.01, message: 'Amount must be greater than 0' },
                setValueAs: (value) => parseRateField(value)
              })}
              label="Amount"
              type="number"
              fullWidth
              disabled={isViewMode}
              error={!!errors.total_amount}
              helperText={errors.total_amount?.message as string}
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
                setValue('total_amount', value);
              }}
            />
          </Grid>

          <Grid size={12}>
            <TextField
              {...control.register('notes')}
              label="Notes"
              multiline
              rows={3}
              fullWidth
              disabled={isViewMode}
              error={!!errors.notes}
              helperText={errors.notes?.message as string}
            />
          </Grid>

          {totalAmountValue > 0 && (
            <Grid size={12}>
              <TextField
                fullWidth
                label="Amount in Words"
                value={getAmountInWords(totalAmountValue)}
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
        voucherType="Payment Vouchers"
        voucherTitle="Payment Voucher"
        indexContent={indexContent}
        formContent={formContent}
        onShowAll={handleModalOpen}
        showAllButton={true}
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showFullModal}
            onClose={handleModalClose}
            voucherType="Payment Vouchers"
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
        voucherType="Payment Voucher"
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

export default PaymentVoucher;
