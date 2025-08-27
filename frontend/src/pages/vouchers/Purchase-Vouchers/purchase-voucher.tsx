// frontend/src/pages/vouchers/Purchase-Vouchers/purchase-voucher.tsx
// Purchase Voucher Page - Refactored using shared DRY logic
import React, { useMemo, useState, useEffect } from 'react';
import { Box, Button, TextField, Typography, Grid, IconButton, CircularProgress, Container, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Autocomplete, InputAdornment, Tooltip, Modal, Alert, Chip, Fab } from '@mui/material';
import { Add, Remove, Visibility, Edit, CloudUpload, CheckCircle, Description } from '@mui/icons-material';
import AddVendorModal from '../../../components/AddVendorModal';
import AddProductModal from '../../../components/AddProductModal';
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherLayout from '../../../components/VoucherLayout';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import VoucherReferenceDropdown from '../../../components/VoucherReferenceDropdown';
import BalanceDisplay from '../../../components/BalanceDisplay';
import StockDisplay from '../../../components/StockDisplay';
import ProductAutocomplete from '../../../components/ProductAutocomplete';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords, GST_SLABS, parseRateField, formatRateField, getVoucherStyles } from '../../../utils/voucherUtils';
import { getStock } from '../../../services/masterService';
import { voucherService } from '../../../services/vouchersService';
import api from '../../../lib/api';  // Import api for direct call

const PurchaseVoucherPage: React.FC = () => {
  const config = getVoucherConfig('purchase-voucher');
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

    // Enhanced utilities
    isViewMode,
    enhancedRateUtils,
  } = useVoucherPage(config);

  // Additional state for voucher list modal
  const [showVoucherListModal, setShowVoucherListModal] = useState(false);

  // Purchase Voucher specific state
  const selectedVendorId = watch('vendor_id');
  const selectedVendor = vendorList?.find((v: any) => v.id === selectedVendorId);

  // Enhanced vendor options with "Add New"
  const enhancedVendorOptions = [
    ...(vendorList || []),
    { id: null, name: 'Add New Vendor...' }
  ];

  // Stock data state for items
  const [stockLoading, setStockLoading] = useState<{[key: number]: boolean}>({});

  // Purchase Voucher specific handlers
  const handleAddItem = () => {
    append({
      product_id: null,
      product_name: '',
      quantity: 1,
      unit_price: 0,
      discount_percentage: 0,
      gst_rate: 18,
      amount: 0,
      unit: '',
      current_stock: 0,
      reorder_level: 0
    });
  };

  // Custom submit handler to prompt for PDF after save
  const onSubmit = async (data: any) => {
    try {
      if (config.hasItems !== false) {
        data.items = computedItems;
        data.total_amount = totalAmount;
      }

      let response;
      if (mode === 'create') {
        response = await api.post('/purchase-vouchers', data);
        if (confirm('Voucher created successfully. Generate PDF?')) {
          handleGeneratePDF(response.data);
        }
        // Reset form and prepare for next entry
        reset();
        setMode('create');
        // Fetch next voucher number
        try {
          const nextNumber = await voucherService.getNextVoucherNumber(config.nextNumberEndpoint);
          setValue('voucher_number', nextNumber);
          setValue('date', new Date().toISOString().split('T')[0]);
        } catch (err) {
          console.error('Failed to fetch next voucher number:', err);
        }
      } else if (mode === 'edit') {
        response = await api.put('/purchase-vouchers/' + data.id, data);
        if (confirm('Voucher updated successfully. Generate PDF?')) {
          handleGeneratePDF(response.data);
        }
      }
      
      // Refresh voucher list to show latest at top
      await refreshMasterData();
      
    } catch (error) {
      console.error('Error saving purchase voucher:', error);
      alert('Failed to save purchase voucher. Please try again.');
    }
  };

  // Function to get stock color
  const getStockColor = (stock: number, reorder: number) => {
    if (stock === 0) return 'error.main';
    if (stock <= reorder) return 'warning.main';
    return 'success.main';
  };

  // Memoize all selected products
  const selectedProducts = useMemo(() => {
    return fields.map((_, index) => {
      const productId = watch(`items.${index}.product_id`);
      return productList?.find((p: any) => p.id === productId) || null;
    });
  }, [fields.length, productList, ...fields.map((_, index) => watch(`items.${index}.product_id`))]);

  // Effect to fetch stock when product changes
  useEffect(() => {
    fields.forEach((_, index) => {
      const productId = watch(`items.${index}.product_id`);
      if (productId) {
        setStockLoading(prev => ({ ...prev, [index]: true }));
        getStock({ queryKey: ['', { product_id: productId }] }).then(res => {
          console.log('Stock Response for product ' + productId + ':', res);
          const stockData = res[0] || { quantity: 0 };
          setValue(`items.${index}.current_stock`, stockData.quantity);
          setStockLoading(prev => ({ ...prev, [index]: false }));
        }).catch(err => {
          console.error('Failed to fetch stock:', err);
          setStockLoading(prev => ({ ...prev, [index]: false }));
        });
      } else {
        setValue(`items.${index}.current_stock`, 0);
        setStockLoading(prev => ({ ...prev, [index]: false }));
      }
    });
  }, [fields.map(f => watch(`items.${fields.indexOf(f)}.product_id`)).join(','), setValue, fields.length]);

  // Manual fetch for voucher number if not loaded
  useEffect(() => {
    if (mode === 'create' && !nextVoucherNumber && !isLoading) {
      voucherService.getNextVoucherNumber(config.nextNumberEndpoint)
        .then(number => setValue('voucher_number', number))
        .catch(err => console.error('Failed to fetch voucher number:', err));
    }
  }, [mode, nextVoucherNumber, isLoading, setValue, config.nextNumberEndpoint]);

  const handleVoucherClick = async (voucher: any) => {
    try {
      // Fetch complete voucher data including items
      const response = await api.get(`/purchase-vouchers/${voucher.id}`);
      const fullVoucherData = response.data;
      
      // Load the complete voucher data into the form
      setMode('view');
      reset(fullVoucherData);
    } catch (error) {
      console.error('Error fetching voucher details:', error);
      // Fallback to available data
      setMode('view');
      reset(voucher);
    }
  };
  
  // Enhanced handleEdit to fetch complete data
  const handleEditWithData = async (voucher: any) => {
    try {
      const response = await api.get(`/purchase-vouchers/${voucher.id}`);
      const fullVoucherData = response.data;
      setMode('edit');
      reset(fullVoucherData);
    } catch (error) {
      console.error('Error fetching voucher details:', error);
      handleEdit(voucher);
    }
  };
  
  // Enhanced handleView to fetch complete data
  const handleViewWithData = async (voucher: any) => {
    try {
      const response = await api.get(`/purchase-vouchers/${voucher.id}`);
      const fullVoucherData = response.data;
      setMode('view');
      reset(fullVoucherData);
    } catch (error) {
      console.error('Error fetching voucher details:', error);
      handleView(voucher);
    }
  };

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
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold', p: 1 }}>Amount</TableCell>
              <TableCell align="right" sx={{ fontSize: 15, fontWeight: 'bold', p: 0, width: 40 }}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {latestVouchers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">No purchase vouchers available</TableCell>
              </TableRow>
            ) : (
              latestVouchers.slice(0, 7).map((voucher: any) => (
                <TableRow 
                  key={voucher.id} 
                  hover 
                  onContextMenu={(e) => { e.preventDefault(); handleContextMenu(e, voucher); }}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }} onClick={() => handleViewWithData(voucher)}>
                    {voucher.voucher_number}
                  </TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>
                    {voucher.date ? new Date(voucher.date).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{vendorList?.find((v: any) => v.id === voucher.vendor_id)?.name || 'N/A'}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>₹{voucher.total_amount?.toLocaleString() || '0'}</TableCell>
                  <TableCell align="right" sx={{ fontSize: 12, p: 0 }}>
                    <VoucherContextMenu
                      voucher={voucher}
                      voucherType="Purchase Voucher"
                      onView={() => handleViewWithData(voucher)}
                      onEdit={() => handleEditWithData(voucher)}
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
    </>
  );

  const formContent = (
    <Box>
      {/* Header Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ fontSize: 20, fontWeight: 'bold', textAlign: 'center', flex: 1 }}>
          {config.voucherTitle} - {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'}
        </Typography>
        <VoucherHeaderActions
          mode={mode}
          voucherType={config.voucherTitle}
          voucherRoute="/vouchers/Purchase-Vouchers/purchase-voucher"
          currentId={selectedVendorId}
        />
      </Box>

      <form onSubmit={handleSubmit(onSubmit)} style={voucherStyles.formContainer}>
        <Grid container spacing={1} sx={voucherStyles.centerText}>
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
              sx={{ 
                '& .MuiInputBase-root': { height: 27 },
                ...voucherStyles.dateField
              }}
            />
          </Grid>

          {/* Vendor, Reference, Payment Terms in one row */}
          <Grid size={6}>
            <Autocomplete
              size="small"
              options={enhancedVendorOptions}
              getOptionLabel={(option: any) => option?.name || ''}
              value={selectedVendor || null}
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
          </Grid>

          <Grid size={3}>
            <VoucherReferenceDropdown
              voucherType="purchase-voucher"
              value={{
                referenceType: watch('reference_type'),
                referenceId: watch('reference_id'),
                referenceNumber: watch('reference_number')
              }}
              onChange={(reference) => {
                setValue('reference_type', reference.referenceType || '');
                setValue('reference_id', reference.referenceId || null);
                setValue('reference_number', reference.referenceNumber || '');
              }}
              disabled={mode === 'view'}
              onReferenceSelected={handleReferenceSelected}
            />
          </Grid>

          <Grid size={3}>
            <TextField
              fullWidth
              label="Payment Terms"
              {...control.register('payment_terms')}
              disabled={mode === 'view'}
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14 } }}
              size="small"
              sx={{ '& .MuiInputBase-root': { height: 27 } }}
            />
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
                    <TableCell sx={voucherStyles.productTableColumns.productName}>Product</TableCell>
                    <TableCell sx={{ width: 80, textAlign: 'center', fontSize: '0.8rem' }}>Stock</TableCell>
                    <TableCell sx={voucherStyles.productTableColumns.quantity}>Qty</TableCell>
                    <TableCell sx={voucherStyles.productTableColumns.rate}>Rate</TableCell>
                    <TableCell sx={voucherStyles.productTableColumns.discount}>Disc%</TableCell>
                    <TableCell sx={voucherStyles.productTableColumns.gst}>GST%</TableCell>
                    <TableCell sx={voucherStyles.productTableColumns.amount}>Amount</TableCell>
                    {mode !== 'view' && (
                      <TableCell sx={voucherStyles.productTableColumns.action}>Action</TableCell>
                    )}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {fields.map((field: any, index: number) => (
                    <React.Fragment key={field.id}>
                      <TableRow>
                        <TableCell sx={{ p: 1 }}>
                          <ProductAutocomplete
                            value={selectedProducts[index]}
                            onChange={(product) => {
                              setValue(`items.${index}.product_id`, product?.id || null);
                              setValue(`items.${index}.product_name`, product?.product_name || '');
                              setValue(`items.${index}.unit_price`, product?.unit_price || 0);
                              setValue(`items.${index}.gst_rate`, product?.gst_rate || 18);
                              setValue(`items.${index}.unit`, product?.unit || '');
                              setValue(`items.${index}.reorder_level`, product?.reorder_level || 0);
                              // Stock fetch handled in useEffect
                            }}
                            disabled={mode === 'view'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          {watch(`items.${index}.product_id`) ? (
                            <StockDisplay 
                              productId={watch(`items.${index}.product_id`)}
                              disabled={false}
                              showLabel={false}
                            />
                          ) : (
                            <Typography variant="caption" sx={{ color: 'text.disabled', fontSize: '0.7rem' }}>
                              -
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'right' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                            <TextField
                              type="number"
                              {...control.register(`items.${index}.quantity`, { valueAsNumber: true })}
                              disabled={mode === 'view'}
                              size="small"
                              sx={{ width: 60 }}
                            />
                            <Typography sx={{ ml: 1, fontSize: 12 }}>{watch(`items.${index}.unit`)}</Typography>
                          </Box>
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: 'center' }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.unit_price`, { 
                              valueAsNumber: true,
                              setValueAs: (value) => enhancedRateUtils.parseRate(value)
                            })}
                            disabled={mode === 'view'}
                            size="small"
                            sx={{
                              width: 80,
                              ...voucherStyles.rateField
                            }}
                            inputProps={{ 
                              min: 0, 
                              step: 0.01,
                              style: { textAlign: 'center' }
                            }}
                            onChange={(e) => {
                              const value = parseRateField(e.target.value);
                              setValue(`items.${index}.unit_price`, value);
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1 }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.discount_percentage`, { valueAsNumber: true })}
                            disabled={mode === 'view'}
                            size="small"
                            sx={{ width: 60 }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1 }}>
                          <Autocomplete
                            size="small"
                            options={GST_SLABS}
                            value={watch(`items.${index}.gst_rate`) || 18}
                            onChange={(_, value) => setValue(`items.${index}.gst_rate`, value || 18)}
                            renderInput={(params) => (
                              <TextField {...params} size="small" sx={{ width: 60 }} />
                            )}
                            disabled={mode === 'view'}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, fontSize: 14 }}>
                          ₹{computedItems[index]?.amount?.toLocaleString() || '0'}
                        </TableCell>
                        {mode !== 'view' && (
                          <TableCell sx={{ p: 1 }}>
                            <IconButton
                              size="small"
                              onClick={() => remove(index)}
                              color="error"
                            >
                              <Remove />
                            </IconButton>
                          </TableCell>
                        )}
                      </TableRow>
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {mode !== 'view' && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
                <Fab color="primary" size="small" onClick={handleAddItem}>
                  <Add />
                </Fab>
              </Box>
            )}
          </Grid>

          {/* Totals */}
          <Grid size={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
              <Box sx={{ minWidth: 300 }}>
                <Grid container spacing={1}>
                  <Grid size={6}>
                    <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>
                      Subtotal:
                    </Typography>
                  </Grid>
                  <Grid size={6}>
                    <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>
                      ₹{totalSubtotal.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid size={6}>
                    <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14 }}>
                      GST:
                    </Typography>
                  </Grid>
                  <Grid size={6}>
                    <Typography variant="body2" sx={{ textAlign: 'right', fontSize: 14, fontWeight: 'bold' }}>
                      ₹{totalGst.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid size={6}>
                    <Typography variant="h6" sx={{ textAlign: 'right', fontSize: 16, fontWeight: 'bold' }}>
                      Total:
                    </Typography>
                  </Grid>
                  <Grid size={6}>
                    <Typography variant="h6" sx={{ textAlign: 'right', fontSize: 16, fontWeight: 'bold' }}>
                      ₹{totalAmount.toLocaleString()}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Box>
          </Grid>

          {/* Amount in Words */}
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

          {/* Action buttons - removed Generate PDF */}
          <Grid size={12}>
            <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
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
            </Box>
          </Grid>
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
        // } : undefined}
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showVoucherListModal}
            onClose={() => setShowVoucherListModal(false)}
            voucherType="Purchase Vouchers"
            vouchers={sortedVouchers || []}
            onVoucherClick={handleVoucherClick}
            onEdit={handleEditWithData}
            onView={handleViewWithData}
            onDelete={handleDelete}
            onGeneratePDF={handleGeneratePDF}
            vendorList={vendorList}
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
        onEdit={handleEditWithData}
        onView={handleViewWithData}
        onDelete={handleDelete}
        onPrint={handleGeneratePDF}
      />
    </>
  );
};

export default PurchaseVoucherPage;