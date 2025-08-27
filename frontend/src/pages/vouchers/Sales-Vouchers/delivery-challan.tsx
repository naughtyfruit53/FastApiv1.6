// frontend/src/pages/vouchers/Sales-Vouchers/delivery-challan.tsx
// Delivery Challan Page - Refactored using shared DRY logic
import React, { useMemo, useState, useEffect } from 'react';
import { Box, Button, TextField, Typography, Grid, IconButton, CircularProgress, Container, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Autocomplete, InputAdornment, Tooltip, Modal, Alert, Chip, Fab } from '@mui/material';
import { Add, Remove, Visibility, Edit, CloudUpload, CheckCircle, Description } from '@mui/icons-material';
import AddCustomerModal from '../../../components/AddCustomerModal';
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
import { getVoucherConfig, numberToWords, GST_SLABS, getVoucherStyles } from '../../../utils/voucherUtils';
import { getStock } from '../../../services/masterService';
import { voucherService } from '../../../services/vouchersService';
import api from '../../../lib/api';  // Import api for direct call

const DeliveryChallanPage: React.FC = () => {
  const config = getVoucherConfig('delivery-challan');
  const voucherStyles = getVoucherStyles();
  const {
    // State
    mode,
    setMode,
    isLoading,
    showAddCustomerModal,
    setShowAddCustomerModal,
    showAddProductModal,
    setShowAddProductModal,
    showShippingModal,
    setShowShippingModal,
    addCustomerLoading,
    setAddCustomerLoading,
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
    customerList,
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

    // Utilities
    isViewMode,
  } = useVoucherPage(config);

  // Additional state for voucher list modal
  const [showVoucherListModal, setShowVoucherListModal] = useState(false);

  // Delivery Challan specific state
  const selectedCustomerId = watch('customer_id');
  const selectedCustomer = customerList?.find((c: any) => c.id === selectedCustomerId);

  // Enhanced customer options with "Add New"
  const enhancedCustomerOptions = [
    ...(customerList || []),
    { id: null, name: 'Add New Customer...' }
  ];

  // Stock data state for items
  const [stockLoading, setStockLoading] = useState<{[key: number]: boolean}>({});

  // Delivery Challan specific handlers
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
        response = await api.post('/delivery-challans', data);
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
        response = await api.put('/delivery-challans/' + data.id, data);
        if (confirm('Voucher updated successfully. Generate PDF?')) {
          handleGeneratePDF(response.data);
        }
      }
      
      // Refresh voucher list to show latest at top
      await refreshMasterData();
      
    } catch (error) {
      console.error('Error saving delivery challan:', error);
      alert('Failed to save delivery challan. Please try again.');
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
      const response = await api.get(`/delivery-challans/${voucher.id}`);
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
      const response = await api.get(`/delivery-challans/${voucher.id}`);
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
      const response = await api.get(`/delivery-challans/${voucher.id}`);
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
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold', p: 1 }}>Customer</TableCell>
              <TableCell align="center" sx={{ fontSize: 15, fontWeight: 'bold', p: 1 }}>Amount</TableCell>
              <TableCell align="right" sx={{ fontSize: 15, fontWeight: 'bold', p: 0, width: 40 }}></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {latestVouchers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">No delivery challans available</TableCell>
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
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{customerList?.find((c: any) => c.id === voucher.customer_id)?.name || 'N/A'}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>₹{voucher.total_amount?.toLocaleString() || '0'}</TableCell>
                  <TableCell align="right" sx={{ fontSize: 12, p: 0 }}>
                    <VoucherContextMenu
                      voucher={voucher}
                      voucherType="Delivery Challan"
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
          voucherRoute="/vouchers/Sales-Vouchers/delivery-challan"
          currentId={selectedCustomerId}
        />
      </Box>

      <form onSubmit={handleSubmit(onSubmit)} style={voucherStyles.formContainer}>
        <Grid container spacing={1}>
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

          {/* Customer, Reference, Payment Terms in one row */}
          <Grid size={4}>
            <Autocomplete
              size="small"
              options={enhancedCustomerOptions}
              getOptionLabel={(option: any) => option?.name || ''}
              value={selectedCustomer || null}
              onChange={(_, newValue) => {
                if (newValue?.id === null) {
                  setShowAddCustomerModal(true);
                } else {
                  setValue('customer_id', newValue?.id || null);
                }
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Customer"
                  error={!!errors.customer_id}
                  helperText={errors.customer_id ? 'Required' : ''}
                  InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                  inputProps={{ ...params.inputProps, style: { fontSize: 14 } }}
                  size="small"
                  sx={{ '& .MuiInputBase-root': { height: 27 } }}
                />
              )}
              disabled={mode === 'view'}
            />
          </Grid>

          <Grid size={4}>
            <TextField
              fullWidth
              label="Reference"
              {...control.register('reference')}
              disabled={mode === 'view'}
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14 } }}
              size="small"
              sx={{ '& .MuiInputBase-root': { height: 27 } }}
            />
          </Grid>

          <Grid size={4}>
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
            <TableContainer component={Paper} sx={{ maxHeight: 300, ...voucherStyles.centeredTable }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontSize: 12, fontWeight: 'bold', p: 1, width: '30%', textAlign: 'center' }}>Product</TableCell>
                    <TableCell sx={{ fontSize: 12, fontWeight: 'bold', p: 1, textAlign: 'center' }}>Qty</TableCell>
                    <TableCell sx={{ fontSize: 12, fontWeight: 'bold', p: 1, textAlign: 'center' }}>Rate</TableCell>
                    <TableCell sx={{ fontSize: 12, fontWeight: 'bold', p: 1, textAlign: 'center' }}>Disc%</TableCell>
                    <TableCell sx={{ fontSize: 12, fontWeight: 'bold', p: 1, textAlign: 'center' }}>GST%</TableCell>
                    <TableCell sx={{ fontSize: 12, fontWeight: 'bold', p: 1, textAlign: 'center' }}>Amount</TableCell>
                    {mode !== 'view' && (
                      <TableCell sx={{ fontSize: 12, fontWeight: 'bold', p: 1, textAlign: 'center' }}>Action</TableCell>
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
                        <TableCell sx={{ p: 1, textAlign: 'right' }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.unit_price`, { valueAsNumber: true })}
                            disabled={mode === 'view'}
                            size="small"
                            sx={{ width: 80 }}
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
                      {/* Stock display below the row - only qty and unit */}
                      <TableRow>
                        <TableCell colSpan={mode !== 'view' ? 7 : 6} sx={{ py: 0.5, pl: 2, bgcolor: 'action.hover' }}>
                          {stockLoading[index] ? (
                            <CircularProgress size={12} />
                          ) : watch(`items.${index}.product_id`) ? (
                            <Typography variant="caption" color={getStockColor(watch(`items.${index}.current_stock`), watch(`items.${index}.reorder_level`))}>
                              {watch(`items.${index}.current_stock`)} {watch(`items.${index}.unit`)}
                            </Typography>
                          ) : null}
                        </TableCell>
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
                      {/* Total removed for GRN/Delivery Challan */}
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
        // } : undefined)
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showVoucherListModal}
            onClose={() => setShowVoucherListModal(false)}
            voucherType="Delivery Challans"
            vouchers={sortedVouchers || []}
            onVoucherClick={handleVoucherClick}
            onEdit={handleEditWithData}
            onView={handleViewWithData}
            onDelete={handleDelete}
            onGeneratePDF={handleGeneratePDF}
            customerList={customerList}
          />
        }
      />

      {/* Modals */}
      <AddCustomerModal 
        open={showAddCustomerModal}
        onClose={() => setShowAddCustomerModal(false)}
        onAdd={refreshMasterData}
        loading={addCustomerLoading}
        setLoading={setAddCustomerLoading}
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

export default DeliveryChallanPage;