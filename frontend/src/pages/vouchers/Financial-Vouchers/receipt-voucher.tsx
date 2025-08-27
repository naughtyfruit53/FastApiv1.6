// Receipt Voucher Page - Refactored using VoucherLayout
import React from 'react';
import { Box, Button, TextField, Typography, Grid, Alert, CircularProgress, Container, Autocomplete, createFilterOptions, InputAdornment, Tooltip, Modal, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { Add, Visibility, Edit } from '@mui/icons-material';
import { Controller } from 'react-hook-form';
import AddVendorModal from '../../../components/AddVendorModal';
import AddCustomerModal from '../../../components/AddCustomerModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import VoucherLayout from '../../../components/VoucherLayout';
import SearchableDropdown from '../../../components/SearchableDropdown';
import EntitySelector from '../../../components/EntitySelector';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords, getVoucherStyles, parseRateField, formatRateField } from '../../../utils/voucherUtils';

const ReceiptVoucher: React.FC = () => {
  const config = getVoucherConfig('receipt-voucher');
  const voucherStyles = getVoucherStyles();
  
  const {
    // State
    mode,
    isLoading,
    showAddVendorModal,
    setShowAddVendorModal,
    showAddCustomerModal,
    setShowAddCustomerModal,
    addVendorLoading,
    setAddVendorLoading,
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
    handleAddVendor,
    handleAddCustomer,
  } = useVoucherPage(config);

  // Watch form values
  const watchedValues = watch();
  const totalAmount = watchedValues?.total_amount || 0;

  // Combined name options for autocomplete
  const allNameOptions = [
    ...(vendorList || []).map((v: any) => ({ ...v, type: 'Vendor' })),
    ...(customerList || []).map((c: any) => ({ ...c, type: 'Customer' }))
  ];

  const nameFilter = createFilterOptions();

  // Handle voucher click to load details
  const handleVoucherClick = (voucher: any) => {
    // Load the selected voucher into the form
    reset(voucher);
    // Set the form with the voucher data
    Object.keys(voucher).forEach(key => {
      setValue(key, voucher[key]);
    });
  };

  // Combined list of all parties (customers + vendors) for unified dropdown
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
    }))
  ];

  // Payment methods for receipt vouchers
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

  // Get selected entity from form
  const selectedEntity = watch('entity');
  const isViewMode = mode === 'view';

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
              <TableCell colSpan={5} align="center">No receipt vouchers available</TableCell>
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
                  {voucher.vendor?.name || voucher.customer?.name || 'N/A'}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  ₹{voucher.total_amount?.toFixed(2) || '0.00'}
                </TableCell>
                <TableCell align="right" sx={{ fontSize: 11, p: 0 }}>
                  <VoucherContextMenu
                    voucher={voucher}
                    voucherType="Receipt Voucher"
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
          Receipt Voucher - {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'}
        </Typography>
        <VoucherHeaderActions
          mode={mode}
          voucherType="Receipt Voucher"
          voucherRoute="/vouchers/Financial-Vouchers/receipt-voucher"
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
            <TextField
              {...control.register('reference')}
              label="Reference"
              fullWidth
              disabled={isViewMode}
              error={!!errors.reference}
              helperText={errors.reference?.message as string}
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

          {totalAmount > 0 && (
            <Grid size={12}>
              <TextField
                fullWidth
                label="Amount in Words"
                value={numberToWords(totalAmount)}
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
        voucherType="Receipt Vouchers"
        voucherTitle="Receipt Voucher"
        indexContent={indexContent}
        formContent={formContent}
        onShowAll={handleModalOpen}
        showAllButton={true}
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showFullModal}
            onClose={handleModalClose}
            voucherType="Receipt Vouchers"
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
      
      {/* Add Customer Modal */}
      <AddCustomerModal
        open={showAddCustomerModal}
        onClose={() => setShowAddCustomerModal(false)}
        onAdd={handleAddCustomer}
        loading={addCustomerLoading}
      />

      {/* Add Vendor Modal */}
      <AddVendorModal
        open={showAddVendorModal}
        onClose={() => setShowAddVendorModal(false)}
        onAdd={handleAddVendor}
        loading={addVendorLoading}
      />
      
      {/* Keep context menu for right-click functionality */}
      {contextMenu && (
        <VoucherContextMenu
          voucherType="Receipt Voucher"
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
          showKebab={false}
          open={true}
          anchorReference="anchorPosition"
          anchorPosition={{ top: contextMenu.mouseY, left: contextMenu.mouseX }}
        />
      )}
    </>
  );
};

export default ReceiptVoucher;