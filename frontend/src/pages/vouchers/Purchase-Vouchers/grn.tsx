// frontend/src/pages/vouchers/Purchase-Vouchers/grn.tsx
// Goods Receipt Note Page - Refactored using shared DRY logic
import React, { useMemo, useState, useEffect } from 'react';
import {Box, TextField, Typography, Grid, CircularProgress, Container, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Autocomplete} from '@mui/material';
import AddVendorModal from '../../../components/AddVendorModal';
import AddProductModal from '../../../components/AddProductModal';
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherLayout from '../../../components/VoucherLayout';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import {getVoucherConfig, getVoucherStyles} from '../../../utils/voucherUtils';
import { voucherService } from '../../../services/vouchersService';
import api from '../../../lib/api';  // Import api for direct call
import { useAuth } from '../../../context/AuthContext';
import { useQuery } from '@tanstack/react-query';
import { useEntityBalance, getBalanceDisplayText } from '../../../hooks/useEntityBalance'; // Added for vendor balance display
const GoodsReceiptNotePage: React.FC = () => {
  const { isOrgContextReady } = useAuth();
  const config = getVoucherConfig('grn');
  const voucherStyles = getVoucherStyles();
  const {
    // State
    mode,
    setMode,
    isLoading,
    showAddVendorModal,
    setShowAddVendorModal,
    showAddProductModal,
    setShowAddProductModal,
    showShippingModal,
    setShowShippingModal,
    addVendorLoading,
    setAddVendorLoading,
    addProductLoading,
    setAddProductLoading,
    addShippingLoading,
    setAddShippingLoading,
    addingItemIndex,
    setAddingItemIndex,
    showFullModal,
    contextMenu,
    useDifferentShipping,
    setUseDifferentShipping,
    searchTerm,
    setSearchTerm,
    fromDate,
    setFromDate,
    toDate,
    setToDate,
    filteredVouchers,
    // Enhanced pagination
    currentPage,
    pageSize,
    paginationData,
    handlePageChange,
    // Reference document handling
    referenceDocument,
    handleReferenceSelected,
    // Form
    control,
    handleSubmit,
    watch,
    setValue,
    errors,
    fields,
    append,
    remove,
    reset,
    // Data
    voucherList,
    vendorList,
    productList,
    voucherData,
    nextVoucherNumber,
    sortedVouchers,
    latestVouchers,
    // Computed
    computedItems,
    totalAmount,
    totalSubtotal,
    totalGst,
    // Mutations
    createMutation,
    updateMutation,
    // Event handlers
    handleCreate,
    handleEdit,
    handleView,
    handleSubmitForm: _handleSubmitForm, // Rename to avoid conflict
    handleContextMenu,
    handleCloseContextMenu,
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
  // Additional state for voucher list modal
  const [showVoucherListModal, setShowVoucherListModal] = useState(false);
  // Goods Receipt Note specific state
  const selectedVendorId = watch('vendor_id');
  const selectedVendor = vendorList?.find((v: any) => v.id === selectedVendorId);
  const vendorValue = useMemo(() => {
    return selectedVendor || null;
  }, [selectedVendor]);
  
  // Fetch vendor balance
  const { balance: vendorBalance, loading: vendorBalanceLoading } = useEntityBalance('vendor', selectedVendorId);
  // Enhanced vendor options with "Add New"
  const enhancedVendorOptions = [
    ...(vendorList || []),
    { id: null, name: 'Add New Vendor...' }
  ];
  // GRN specific states
  const [selectedVoucherType, setSelectedVoucherType] = useState<'purchase-voucher' | 'purchase-order' | null>(null);
  const [selectedVoucherId, setSelectedVoucherId] = useState<number | null>(null);
  // Fetch purchase orders
  const { data: purchaseOrdersData, refetch: refetchOrders } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: () => api.get('/purchase-orders').then(res => res.data),
    enabled: isOrgContextReady,
  });
  // Fetch purchase vouchers
  const { data: purchaseVouchersData, refetch: refetchVouchers } = useQuery({
    queryKey: ['purchase-vouchers'],
    queryFn: () => api.get('/purchase-vouchers').then(res => res.data),
    enabled: isOrgContextReady,
  });
  // Fetch all GRNs to get used PO/PV IDs
  const { data: grns } = useQuery({
    queryKey: ['goods-receipt-notes'],
    queryFn: () => api.get('/goods-receipt-notes').then(res => res.data),
    enabled: isOrgContextReady,
  });
  // Compute used voucher IDs, excluding current GRN in edit mode
  const currentGrnId = mode === 'edit' ? voucherData?.id : null;
  const usedVoucherIds = useMemo(() => {
    if (!grns) {return new Set();}
    return new Set(grns.filter(grn => grn.id !== currentGrnId).map(grn => grn.purchase_order_id));
  }, [grns, currentGrnId]);
  // Filter voucher options to exclude used ones
  const voucherOptions = useMemo(() => {
    let options = [];
    if (selectedVoucherType === 'purchase-order') {
      options = purchaseOrdersData || [];
    } else if (selectedVoucherType === 'purchase-voucher') {
      options = purchaseVouchersData || [];
    }
    return options.filter(option => !usedVoucherIds.has(option.id));
  }, [selectedVoucherType, purchaseOrdersData, purchaseVouchersData, usedVoucherIds]);
  // Fetch selected voucher details
  const { data: selectedVoucherData } = useQuery({
    queryKey: [selectedVoucherType, selectedVoucherId],
    queryFn: () => {
      if (!selectedVoucherType || !selectedVoucherId) {return null;}
      const endpoint = selectedVoucherType === 'purchase-order' ? '/purchase-orders' : '/purchase-vouchers';
      return api.get(`${endpoint}/${selectedVoucherId}`).then(res => res.data);
    },
    enabled: !!selectedVoucherType && !!selectedVoucherId,
  });
  // Populate form with selected voucher data
  useEffect(() => {
    if (selectedVoucherData) {
      setValue('vendor_id', selectedVoucherData.vendor_id);
      // Clear existing items
      remove();
      // Append items from selected voucher
      selectedVoucherData.items.forEach((item: any) => {
        append({
          product_id: item.product_id,
          product_name: item.product?.product_name || item.product_name || '', 
          ordered_quantity: item.quantity,
          received_quantity: item.pending_quantity || item.quantity,
          accepted_quantity: item.pending_quantity || item.quantity,
          rejected_quantity: 0,
          unit_price: item.unit_price, // Keep hidden
          unit: item.unit,
        });
      });
    }
  }, [selectedVoucherData, setValue, append, remove]);
  // Goods Receipt Note specific handlers
  const handleAddItem = () => {
    // No add item for GRN, as items come from voucher
  };
  const handleCancel = () => {
    setMode('view');
    // Optionally refresh or reset form to original voucherData
    if (voucherData) {
      reset(voucherData);
    }
  };
  // Custom submit handler to prompt for PDF after save
  const onSubmit = async (data: any) => {
    try {
      if (config.hasItems !== false) {
        // Calculate totals if needed, but since no price shown, perhaps adjust
        data.total_amount = fields.reduce((sum: number, field: any) => sum + (field.accepted_quantity * field.unit_price), 0);
        data.items = fields.map((field: any) => ({
          product_id: field.product_id,
          ordered_quantity: field.ordered_quantity,
          received_quantity: field.received_quantity,
          accepted_quantity: field.accepted_quantity,
          rejected_quantity: field.rejected_quantity,
          unit: field.unit,
          unit_price: field.unit_price,
          total_cost: field.accepted_quantity * field.unit_price,
        }));
      }
      data.purchase_order_id = selectedVoucherId;
      data.grn_date = data.date + 'T00:00:00Z';
      let response;
      if (mode === 'create') {
        response = await createMutation.mutateAsync(data);
        if (confirm('Voucher created successfully. Generate PDF?')) {
          handleGeneratePDF(response);
        }
      } else if (mode === 'edit') {
        response = await updateMutation.mutateAsync(data);
        if (confirm('Voucher updated successfully. Generate PDF?')) {
          handleGeneratePDF(response);
        }
      }
    } catch (error: any) {
      console.error("Error saving voucher:", error);
      alert('Failed to save goods receipt note. Please try again.');
    }
  };
  // Validation for quantities
  const validateQuantities = () => {
    let valid = true;
    fields.forEach((field, index) => {
      const received = watch(`items.${index}.received_quantity`) || 0;
      const accepted = watch(`items.${index}.accepted_quantity`) || 0;
      const rejected = watch(`items.${index}.rejected_quantity`) || 0;
      if (accepted + rejected > received) {
        alert(`For item ${index + 1}, accepted + rejected cannot exceed received quantity.`);
        valid = false;
      }
    });
    return valid;
  };
  // Wrap submit to include validation
  const handleFormSubmit = (data: any) => {
    if (validateQuantities()) {
      _handleSubmitForm(data);
    }
  };
  // Manual fetch for voucher number if not loaded
  useEffect(() => {
    if (mode === 'create' && !nextVoucherNumber && !isLoading) {
      voucherService.getNextVoucherNumber(config.nextNumberEndpoint)
        .then(number => setValue('voucher_number', number))
        .catch(err => console.error('Failed to fetch voucher number:', err));
    }
  }, [mode, nextVoucherNumber, isLoading, setValue, config.nextNumberEndpoint]);
  // Handle voucher click for modal
  const handleVoucherClick = async (voucher: any) => {
    handleView(voucher.id);
  };
  // Use hook's handleEdit and handleView, mapping handled in effect below
  useEffect(() => {
    if (voucherData && (mode === 'view' || mode === 'edit')) {
      const mappedData = {
        ...voucherData,
        date: voucherData.grn_date ? voucherData.grn_date.split('T')[0] : '',
        items: voucherData.items.map(item => ({
          ...item,
          ordered_quantity: item.ordered_quantity,
          received_quantity: item.received_quantity,
          accepted_quantity: item.accepted_quantity,
          rejected_quantity: item.rejected_quantity,
          product_name: item.product?.product_name,
        })),
        reference_voucher_type: 'purchase-order',
        reference_voucher_number: voucherData.purchase_order?.voucher_number || voucherData.purchase_order_id
      };
      reset(mappedData);
      setSelectedVoucherType('purchase-order');
      setSelectedVoucherId(voucherData.purchase_order_id);
      if (mode === 'edit') {
        remove();
        mappedData.items.forEach((item) => {
          append({
            product_id: item.product_id,
            product_name: item.product_name,
            ordered_quantity: item.ordered_quantity,
            received_quantity: item.received_quantity,
            accepted_quantity: item.accepted_quantity,
            rejected_quantity: item.rejected_quantity,
            unit_price: item.unit_price,
            unit: item.unit,
          });
        });
      }
    }
  }, [voucherData, mode, reset, setValue, append, remove]);
  const indexContent = (
    <>
      {/* Voucher list table */}
      <TableContainer sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold', p: 1 }}>Voucher No.</TableCell>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold', p: 1 }}>Date</TableCell>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold', p: 1 }}>Vendor</TableCell>
              <TableCell align="right" sx={{ fontSize: 15, fontWeight: 'bold', p: 0, width: 40 }}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {latestVouchers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} align="center">No goods receipt notes available</TableCell>
              </TableRow>
            ) : (
              latestVouchers.slice(0, 7).map((voucher: any) => (
                <TableRow 
                  key={voucher.id} 
                  hover 
                  onContextMenu={(e) => { e.preventDefault(); handleContextMenu(e, voucher); }}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }} onClick={() => handleView(voucher.id)}>
                    {voucher.voucher_number}
                  </TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>
                    {voucher.date ? new Date(voucher.date).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{vendorList?.find((v: any) => v.id === voucher.vendor_id)?.name || 'N/A'}</TableCell>
                  <TableCell align="right" sx={{ fontSize: 12, p: 0 }}>
                    <VoucherContextMenu
                      voucher={voucher}
                      voucherType="Goods Receipt Note"
                      onView={() => handleView(voucher.id)}
                      onEdit={() => handleEdit(voucher.id)}
                      onDelete={() => handleDelete(voucher)}
                      onPrint={handleGeneratePDF}
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
    </>
  );
  const formContent = (
    <Box>
      {/* Header Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ fontSize: 20, fontWeight: 'bold', textAlign: 'left', flex: 1, pl: 1 }}>
          {config.voucherTitle} - {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'}
        </Typography>
        <VoucherHeaderActions
          mode={mode}
          voucherType={config.voucherTitle}
          voucherRoute="/vouchers/Purchase-Vouchers/grn"
          currentId={mode === 'create' ? null : voucherData?.id}
          onEdit={() => handleEdit(voucherData?.id)}
          onCreate={handleCreate}
          onCancel={handleCancel}
        />
      </Box>
      <form id="voucherForm" onSubmit={handleSubmit(onSubmit)} style={voucherStyles.formContainer}>
        <Grid container spacing={0.5}>
          {/* Voucher Number */}
          <Grid size={6}>
            <TextField
              fullWidth
              label="Voucher Number"
              {...control.register('voucher_number')}
              disabled
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14, textAlign: 'center', fontWeight: 'bold' } }}
              size="small"
              sx={{ '& .MuiInputBase-root': { height: 27 } }}
            />
          </Grid>
          {/* Date */}
          <Grid size={6}>
            <TextField
              fullWidth
              label="Date"
              type="date"
              {...control.register('date')}
              disabled={mode === 'view'}
              InputLabelProps={{ shrink: true, style: { fontSize: 12, display: 'block', visibility: 'visible' } }}
              inputProps={{ style: { fontSize: 14, textAlign: 'center' } }}
              size="small"
              sx={{ '& .MuiInputBase-root': { height: 27 } }}
            />
          </Grid>
          {/* Voucher Type */}
          <Grid size={3}>
            {mode === 'view' ? (
              <TextField
                fullWidth
                label="Voucher Type"
                value={selectedVoucherType === 'purchase-order' ? 'Purchase Order' : 'Purchase Voucher'}
                disabled
                InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                inputProps={{ style: { fontSize: 14 } }}
                size="small"
                sx={{ '& .MuiInputBase-root': { height: 27 } }}
              />
            ) : (
              <Autocomplete
                size="small"
                options={[{value: 'purchase-order', label: 'Purchase Order'}, {value: 'purchase-voucher', label: 'Purchase Voucher'}]}
                getOptionLabel={(option: any) => option.label}
                value={selectedVoucherType ? {value: selectedVoucherType, label: selectedVoucherType === 'purchase-order' ? 'Purchase Order' : 'Purchase Voucher'} : null}
                onChange={(_, newValue) => {
                  setSelectedVoucherType(newValue?.value || null);
                  setSelectedVoucherId(null);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Voucher Type"
                    InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                    inputProps={{ ...params.inputProps, style: { fontSize: 14 } }}
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  />
                )}
                disabled={mode === 'view'}
              />
            )}
          </Grid>
          {/* Voucher Number */}
          <Grid size={3}>
            {mode === 'view' ? (
              <TextField
                fullWidth
                label="Reference Voucher Number"
                value={watch('reference_voucher_number') || ''}
                disabled
                InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                inputProps={{ style: { fontSize: 14 } }}
                size="small"
                sx={{ '& .MuiInputBase-root': { height: 27 } }}
              />
            ) : (
              <Autocomplete
                size="small"
                options={voucherOptions}
                getOptionLabel={(option: any) => option.voucher_number}
                value={voucherOptions.find((v: any) => v.id === selectedVoucherId) || null}
                onChange={(_, newValue) => {
                  setSelectedVoucherId(newValue?.id || null);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Reference Voucher Number"
                    InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                    inputProps={{ ...params.inputProps, style: { fontSize: 14 } }}
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  />
                )}
                disabled={mode === 'view' || !selectedVoucherType}
              />
            )}
          </Grid>
          {/* Vendor - Switch to TextField when voucher selected for auto-populate */}
          <Grid size={5}>
            {!!selectedVoucherId ? (
              <TextField
                fullWidth
                label="Vendor"
                value={selectedVoucherData?.vendor?.name || selectedVendor?.name || ''}
                disabled
                InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                inputProps={{ style: { fontSize: 14 } }}
                size="small"
                sx={{ '& .MuiInputBase-root': { height: 27 } }}
              />
            ) : (
              <Autocomplete
                size="small"
                options={enhancedVendorOptions}
                getOptionLabel={(option: any) => option?.name || ''}
                value={vendorValue}
                onChange={(_, newValue) => {
                  if (newValue?.id === null) {
                    setShowAddVendorModal(true);
                  } else {
                    setValue('vendor_id', newValue?.id || null);
                  }
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Vendor"
                    error={!!errors.vendor_id}
                    helperText={errors.vendor_id ? 'Required' : ''}
                    InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                    inputProps={{ ...params.inputProps, style: { fontSize: 14 } }}
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  />
                )}
                disabled={mode === 'view'}
              />
            )}
          </Grid>
          <Grid size={1}>
            {selectedVendorId && (
              <TextField
                fullWidth
                label="Balance"
                value={vendorBalanceLoading ? "..." : getBalanceDisplayText(vendorBalance)}
                disabled
                size="small"
                InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                inputProps={{ style: { fontSize: 14, textAlign: 'right', fontWeight: 'bold' } }}
                sx={{ 
                  '& .MuiInputBase-root': { height: 27 },
                  '& .MuiInputBase-input': { 
                    color: vendorBalance > 0 ? '#d32f2f' : vendorBalance < 0 ? '#2e7d32' : '#666'
                  }
                }}
              />
            )}
          </Grid>
          <Grid size={12}>
            <TextField
              fullWidth
              label="Notes"
              {...control.register('notes')}
              multiline
              rows={2}
              disabled={mode === 'view'}
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14 } }}
              size="small"
            />
          </Grid>
          {/* Items section */}
          <Grid size={12} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 27 }}>
            <Typography variant="h6" sx={{ fontSize: 16, fontWeight: 'bold', textAlign: 'center' }}>Items</Typography>
          </Grid>
          {/* Items Table */}
          <Grid size={12}>
            <TableContainer component={Paper} sx={{ maxHeight: 300, ...voucherStyles.centeredTable, ...voucherStyles.optimizedTableContainer }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={voucherStyles.grnTableColumns.productName}>Product</TableCell>
                    <TableCell sx={voucherStyles.grnTableColumns.orderQty}>Order Qty</TableCell>
                    <TableCell sx={voucherStyles.grnTableColumns.receivedQty}>Received Qty</TableCell>
                    <TableCell sx={voucherStyles.grnTableColumns.acceptedQty}>Accepted Qty</TableCell>
                    <TableCell sx={voucherStyles.grnTableColumns.rejectedQty}>Rejected Qty</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {fields.map((field: any, index: number) => (
                    <React.Fragment key={field.id}>
                      <TableRow>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            fullWidth
                            value={watch(`items.${index}.product_name`) || ''}
                            disabled
                            size="small"
                            inputProps={{ style: { textAlign: 'center' } }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            type="number"
                            value={watch(`items.${index}.ordered_quantity`)}
                            disabled
                            size="small"
                            sx={{ width: 100 }}
                            inputProps={{ style: { textAlign: 'center' } }}
                            InputProps={{
                              endAdornment: watch(`items.${index}.unit`) && (
                                <span style={{ fontSize: '12px', color: '#666' }}>
                                  {watch(`items.${index}.unit`)}
                                </span>
                              )
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.received_quantity`, { valueAsNumber: true })}
                            disabled={mode === 'view'}
                            size="small"
                            sx={{ width: 100 }}
                            inputProps={{ style: { textAlign: 'center' } }}
                            InputProps={{
                              endAdornment: watch(`items.${index}.unit`) && (
                                <span style={{ fontSize: '12px', color: '#666' }}>
                                  {watch(`items.${index}.unit`)}
                                </span>
                              )
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.accepted_quantity`, { valueAsNumber: true })}
                            disabled={mode === 'view'}
                            size="small"
                            sx={{ width: 100 }}
                            inputProps={{ style: { textAlign: 'center' } }}
                            InputProps={{
                              endAdornment: watch(`items.${index}.unit`) && (
                                <span style={{ fontSize: '12px', color: '#666' }}>
                                  {watch(`items.${index}.unit`)}
                                </span>
                              )
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.rejected_quantity`, { valueAsNumber: true })}
                            disabled={mode === 'view'}
                            size="small"
                            sx={{ width: 100 }}
                            inputProps={{ style: { textAlign: 'center' } }}
                            InputProps={{
                              endAdornment: watch(`items.${index}.unit`) && (
                                <span style={{ fontSize: '12px', color: '#666' }}>
                                  {watch(`items.${index}.unit`)}
                                </span>
                              )
                            }}
                          />
                        </TableCell>
                      </TableRow>
                      {/* Hide stock display below the row for GRN */}
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>
          {/* GRN does not have totals section - removed as per requirements */}
        </Grid>
      </form>
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
        voucherType={config.voucherTitle}
        voucherTitle={config.voucherTitle}
        indexContent={indexContent}
        formContent={formContent}
        onShowAll={() => setShowVoucherListModal(true)}
        // pagination={paginationData ? {
        //   currentPage: currentPage,
        //   totalPages: paginationData.totalPages,
        //   onPageChange: handlePageChange,
        //   totalItems: paginationData.totalItems
        // } : undefined)
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showVoucherListModal}
            onClose={() => setShowVoucherListModal(false)}
            voucherType="Goods Receipt Notes"
            vouchers={sortedVouchers || []}
            onVoucherClick={handleVoucherClick}
            onEdit={handleEdit}
            onView={handleView}
            onDelete={handleDelete}
            onGeneratePDF={handleGeneratePDF}
            customerList={vendorList}
          />
        }
      />
      {/* Modals */}
      <AddVendorModal 
        open={showAddVendorModal}
        onClose={() => setShowAddVendorModal(false)}
        onVendorAdded={refreshMasterData}
        loading={addVendorLoading}
        setLoading={setAddVendorLoading}
      />
      <AddProductModal 
        open={showAddProductModal}
        onClose={() => setShowAddProductModal(false)}
        onProductAdded={refreshMasterData}
        loading={addProductLoading}
        setLoading={setAddProductLoading}
      />
      <AddShippingAddressModal 
        open={showShippingModal}
        onClose={() => setShowShippingModal(false)}
        loading={addShippingLoading}
        setLoading={setAddShippingLoading}
      />
      <VoucherContextMenu
        contextMenu={contextMenu}
        onClose={handleCloseContextMenu}
        onEdit={handleEdit}
        onView={handleView}
        onDelete={handleDelete}
        onPrint={handleGeneratePDF}
      />
    </>
  );
};
export default GoodsReceiptNotePage;