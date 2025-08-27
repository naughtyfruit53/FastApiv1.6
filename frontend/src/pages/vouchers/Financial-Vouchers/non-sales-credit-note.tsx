// Non-Sales Credit Note Page - Refactored using VoucherLayout
import React from 'react';
import { Box, Button, TextField, Typography, Grid, Alert, CircularProgress, Container, Autocomplete, InputAdornment, Tooltip, Modal, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { Visibility, Edit, Add } from '@mui/icons-material';
import AddCustomerModal from '../../../components/AddCustomerModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import VoucherLayout from '../../../components/VoucherLayout';
import SearchableDropdown from '../../../components/SearchableDropdown';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords, getVoucherStyles, parseRateField, formatRateField } from '../../../utils/voucherUtils';

const NonSalesCreditNote: React.FC = () => {
  const config = getVoucherConfig('non-sales-credit-note');
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
    handleAddCustomer,
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

  // Credit note reasons
  const creditNoteReasons = [
    'Product Return',
    'Defective Product',
    'Wrong Product Shipped',
    'Pricing Error',
    'Customer Dissatisfaction',
    'Promotional Adjustment',
    'Volume Discount',
    'Settlement Discount',
    'Other'
  ];

  // Get selected entity from form
  const selectedEntity = watch('entity');

  // Index Content - Left Panel (40%)
  const indexContent = (
    <TableContainer sx={{ maxHeight: 400 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Credit Note No.</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Date</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Party</TableCell>
            <TableCell align="center" sx={{ fontSize: 12, fontWeight: 'bold', p: 1 }}>Amount</TableCell>
            <TableCell align="right" sx={{ fontSize: 12, fontWeight: 'bold', p: 0, width: 40 }}></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {(sortedVouchers?.length === 0) ? (
            <TableRow>
              <TableCell colSpan={5} align="center">No credit notes available</TableCell>
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
                  {voucher.credit_note_number || voucher.voucher_number}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  {new Date(voucher.date).toLocaleDateString()}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  {voucher.entity?.name || voucher.customer?.name || 'N/A'}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 11, p: 1 }}>
                  ₹{voucher.total_amount?.toFixed(2) || '0.00'}
                </TableCell>
                <TableCell align="right" sx={{ fontSize: 11, p: 0 }}>
                  <VoucherContextMenu
                    voucher={voucher}
                    voucherType="Non Sales Credit Note"
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
          Non Sales Credit Note - {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'}
        </Typography>
        <VoucherHeaderActions
          mode={mode}
          voucherType="Non Sales Credit Note"
          voucherRoute="/vouchers/Financial-Vouchers/non-sales-credit-note"
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
              {...control.register('credit_note_number')}
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
              <InputLabel>Reason</InputLabel>
              <Select
                {...control.register('reason')}
                value={watch('reason') || ''}
                onChange={(e) => setValue('reason', e.target.value)}
                error={!!errors.reason}
                sx={{ height: 56 }} // Match height with Party Name field
              >
                {creditNoteReasons.map((reason) => (
                  <MenuItem key={reason} value={reason}>
                    {reason}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid size={6}>
            <TextField
              {...control.register('reference_number')}
              label="Reference Number"
              fullWidth
              disabled={isViewMode}
              error={!!errors.reference_number}
              helperText={errors.reference_number?.message as string}
              placeholder="Enter reference invoice/bill number..."
            />
          </Grid>

          <Grid size={6}>
            <TextField
              {...control.register('total_amount', {
                required: 'Amount is required',
                min: { value: 0.01, message: 'Amount must be greater than 0' },
                setValueAs: (value) => parseRateField(value)
              })}
              label="Credit Amount"
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
              {...control.register('description')}
              label="Description"
              multiline
              rows={4}
              fullWidth
              disabled={isViewMode}
              error={!!errors.description}
              helperText={errors.description?.message as string}
              placeholder="Enter detailed description of the credit note..."
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
        voucherType="Non Sales Credit Notes"
        voucherTitle="Non Sales Credit Note"
        indexContent={indexContent}
        formContent={formContent}
        onShowAll={handleModalOpen}
        showAllButton={true}
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showFullModal}
            onClose={handleModalClose}
            voucherType="Non Sales Credit Notes"
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
      
      {/* Keep context menu for right-click functionality */}
      <VoucherContextMenu
        voucherType="Non Sales Credit Note"
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

export default NonSalesCreditNote;