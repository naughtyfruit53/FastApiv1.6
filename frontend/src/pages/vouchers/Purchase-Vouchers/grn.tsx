import React, { useMemo, useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Typography,
  Grid,
  CircularProgress,
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Autocomplete,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  IconButton,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import AddVendorModal from '../../../components/AddVendorModal';
import AddProductModal from '../../../components/AddProductModal';
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherLayout from '../../../components/VoucherLayout';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, getVoucherStyles } from '../../../utils/voucherUtils';
import { voucherService } from '../../../services/vouchersService';
import api from '../../../lib/api';
import { useAuth } from '../../../context/AuthContext';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import Link from 'next/link';

const GoodsReceiptNotePage: React.FC = () => {
  const { isOrgContextReady } = useAuth();
  const router = useRouter();
  const { po_id } = router.query;
  const config = getVoucherConfig('grn');
  const voucherStyles = getVoucherStyles();
  const {
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
    currentPage,
    pageSize,
    paginationData,
    handlePageChange,
    referenceDocument,
    handleReferenceSelected,
    control,
    handleSubmit,
    watch,
    setValue,
    errors,
    fields,
    append,
    remove,
    reset,
    voucherList,
    vendorList,
    productList,
    voucherData,
    nextVoucherNumber,
    sortedVouchers,
    latestVouchers,
    computedItems,
    totalAmount,
    totalSubtotal,
    totalGst,
    createMutation,
    updateMutation,
    handleCreate,
    handleEdit,
    handleView,
    handleSubmitForm: _handleSubmitForm,
    handleContextMenu,
    handleCloseContextMenu,
    handleSearch,
    handleModalOpen,
    handleModalClose,
    handleGeneratePDF,
    handleDelete,
    refreshMasterData,
    getAmountInWords,
    isViewMode,
  } = useVoucherPage(config);
  const [showVoucherListModal, setShowVoucherListModal] = useState(false);
  const [isItemsLoading, setIsItemsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [editProductId, setEditProductId] = useState<number | null>(null);
  const selectedVendorId = watch('vendor_id');
  const selectedVendor = vendorList?.find((v: any) => v.id === selectedVendorId);
  const vendorValue = useMemo(() => {
    return selectedVendor || null;
  }, [selectedVendor]);
  
  const enhancedVendorOptions = [
    ...(vendorList || []),
    { id: null, name: 'Add New Vendor...' }
  ];
  const [selectedVoucherType, setSelectedVoucherType] = useState<'purchase-voucher' | 'purchase-order' | null>(null);
  const [selectedVoucherId, setSelectedVoucherId] = useState<number | null>(null);
  const [grnCompleteDialogOpen, setGrnCompleteDialogOpen] = useState(false);
  const [existingGrnId, setExistingGrnId] = useState<number | null>(null);

  const { data: poData } = useQuery({
    queryKey: ['purchase-order', po_id],
    queryFn: () => {
      if (!po_id) return null;
      return api.get(`/purchase-orders/${po_id}`).then(res => res.data);
    },
    enabled: !!po_id && isOrgContextReady,
  });

  const { data: existingGrnData } = useQuery({
    queryKey: ['grn-for-po', po_id],
    queryFn: () => {
      if (!po_id) return null;
      return api.get(`/goods-receipt-notes/for-po/${po_id}`).then(res => res.data);
    },
    enabled: !!po_id && isOrgContextReady,
  });

  // Validate product IDs before processing
  const { data: productValidationData } = useQuery({
    queryKey: ['validate-products', selectedVoucherId],
    queryFn: () => {
      if (!selectedVoucherId || !selectedVoucherType) return { invalid_products: [] };
      return api.post('/products/validate-product-ids', selectedVoucherData?.items?.map((item: any) => item.product_id || item.id_2) || []).then(res => res.data);
    },
    enabled: !!selectedVoucherId && !!selectedVoucherType && isOrgContextReady,
  });

  useEffect(() => {
    if (po_id && !selectedVoucherId) {
      setSelectedVoucherType('purchase-order');
      setSelectedVoucherId(Number(po_id));
      setMode('create');
    }
  }, [po_id, setSelectedVoucherType, setSelectedVoucherId, setMode]);

  useEffect(() => {
    if (poData && poData.grn_status === 'complete' && existingGrnData) {
      setGrnCompleteDialogOpen(true);
      setExistingGrnId(existingGrnData.id);
    }
  }, [poData, existingGrnData]);

  const { data: purchaseOrdersData, refetch: refetchOrders } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: () => api.get('/purchase-orders').then(res => res.data),
    enabled: isOrgContextReady,
  });
  const { data: purchaseVouchersData, refetch: refetchVouchers } = useQuery({
    queryKey: ['purchase-vouchers'],
    queryFn: () => api.get('/purchase-vouchers').then(res => res.data),
    enabled: isOrgContextReady,
  });
  const { data: grns } = useQuery({
    queryKey: ['goods-receipt-notes'],
    queryFn: () => api.get('/goods-receipt-notes').then(res => res.data),
    enabled: isOrgContextReady,
  });
  const currentGrnId = mode === 'edit' ? voucherData?.id : null;
  const usedVoucherIds = useMemo(() => {
    if (!grns) {return new Set();}
    return new Set(grns.filter(grn => grn.id !== currentGrnId).map(grn => grn.purchase_order_id));
  }, [grns, currentGrnId]);
  const voucherOptions = useMemo(() => {
    let options = [];
    if (selectedVoucherType === 'purchase-order') {
      options = purchaseOrdersData || [];
    } else if (selectedVoucherType === 'purchase-voucher') {
      options = purchaseVouchersData || [];
    }
    return options.filter(option => !usedVoucherIds.has(option.id));
  }, [selectedVoucherType, purchaseOrdersData, purchaseVouchersData, usedVoucherIds]);
  const { data: selectedVoucherData, isLoading: isVoucherDataLoading } = useQuery({
    queryKey: [selectedVoucherType, selectedVoucherId],
    queryFn: () => {
      if (!selectedVoucherType || !selectedVoucherId) {return null;}
      const endpoint = selectedVoucherType === 'purchase-order' ? '/purchase-orders' : '/purchase-vouchers';
      return api.get(`${endpoint}/${selectedVoucherId}`).then(res => res.data);
    },
    enabled: !!selectedVoucherType && !!selectedVoucherId && !grnCompleteDialogOpen,
    cacheTime: 0, // Disable caching to avoid stale data
  });

  useEffect(() => {
    if (isVoucherDataLoading) {
      setIsItemsLoading(true);
    } else {
      setIsItemsLoading(false);
    }
  }, [isVoucherDataLoading]);

  useEffect(() => {
    if (selectedVoucherData && !grnCompleteDialogOpen) {
      console.log('[GoodsReceiptNotePage] selectedVoucherData:', JSON.stringify(selectedVoucherData, null, 2));
      setValue('vendor_id', selectedVoucherData.vendor_id || selectedVoucherData.vendor_id_1 || null);
      setValue('reference_voucher_number', selectedVoucherData.voucher_number || selectedVoucherData.voucher_number_1 || '');
      setValue('purchase_order_id', selectedVoucherId);
      remove();
      if (selectedVoucherData.items && Array.isArray(selectedVoucherData.items) && selectedVoucherData.items.length > 0) {
        console.log('[GoodsReceiptNotePage] Processing items:', JSON.stringify(selectedVoucherData.items, null, 2));
        let missingNameItems: string[] = [];
        selectedVoucherData.items.forEach((item: any, index: number) => {
          const productFromList = productList?.find((p: any) => p.id === (item.product_id || item.id_2));
          // Prioritize name_1 from SQL query, then fallback to other sources
          const productName = item.name_1 || item.product?.product_name || item.product_name || productFromList?.name || null;
          console.log(`[GoodsReceiptNotePage] Item ${index}:`, JSON.stringify({
            product_id: item.product_id || item.id_2,
            name_1: item.name_1,
            product_name: item.product_name,
            product: item.product,
            productFromList: productFromList,
            productNameUsed: productName,
            quantity: item.quantity,
            unit_1: item.unit_1,
            unit_price_1: item.unit_price_1,
            po_item_id: item.id_3
          }, null, 2));
          if (!productName) {
            console.error(`[GoodsReceiptNotePage] Item ${index} missing product name (product_id: ${item.product_id || item.id_2})`);
            missingNameItems.push(`Item ${index + 1} (Product ID: ${item.product_id || item.id_2})`);
          } else {
            append({
              product_id: item.product_id || item.id_2 || null,
              product_name: productName,
              ordered_quantity: item.quantity || item.ordered_quantity || 0,
              received_quantity: 0,
              accepted_quantity: 0,
              rejected_quantity: 0,
              unit_price: item.unit_price_1 || item.unit_price || 0,
              unit: item.unit_1 || item.unit || item.product?.unit || productFromList?.unit || '',
              po_item_id: item.id_3 || item.id || null,
            });
          }
        });
        if (missingNameItems.length > 0) {
          const invalidProducts = productValidationData?.invalid_products || [];
          const validationErrors = invalidProducts.map((p: any) => `Product ID ${p.id}: ${p.error}`).join(', ');
          setErrorMessage(
            `Some items are missing product names: ${missingNameItems.join(', ')}. ` +
            (validationErrors ? `Validation errors: ${validationErrors}. ` : '') +
            `Please edit the product records to add valid names.`
          );
        } else {
          setErrorMessage(null);
        }
      } else {
        console.warn('[GoodsReceiptNotePage] No valid items found in selectedVoucherData:', JSON.stringify(selectedVoucherData, null, 2));
        setErrorMessage('No valid items found in the selected purchase order. Please select a valid purchase order.');
      }
    }
  }, [selectedVoucherData, productValidationData, setValue, append, remove, grnCompleteDialogOpen, productList]);

  const handleAddItem = () => {
    // No add item for GRN, as items come from voucher
  };

  const handleCancel = () => {
    setMode('view');
    if (voucherData) {
      reset(voucherData);
    }
    setErrorMessage(null);
  };

  const handleEditProduct = (productId: number) => {
    setEditProductId(productId);
    setShowAddProductModal(true);
  };

  const handleProductModalClose = () => {
    setShowAddProductModal(false);
    setEditProductId(null);
    refreshMasterData(); // Refresh product list after editing
  };

  const onSubmit = async (data: any) => {
    if (errorMessage) {
      alert('Cannot submit GRN due to missing product names. Please resolve the errors by editing the product records.');
      return;
    }
    try {
      console.log('Submitting GRN with data:', {
        vendor_id: data.vendor_id,
        items: data.items.map((item: any) => ({
          product_id: item.product_id,
          ordered_quantity: item.ordered_quantity,
          received_quantity: item.received_quantity,
          accepted_quantity: item.accepted_quantity,
          rejected_quantity: item.rejected_quantity,
          unit: item.unit,
          unit_price: item.unit_price,
          po_item_id: item.po_item_id,
        })),
        purchase_order_id: data.purchase_order_id,
        voucher_number: data.voucher_number,
      });
      if (config.hasItems !== false) {
        if (data.items.some((item: any) => !item.product_name || item.product_name === 'Product Not Found')) {
          alert('Cannot submit GRN with missing or invalid product names.');
          return;
        }
        data.total_amount = fields.reduce((sum: number, field: any) => sum + (field.accepted_quantity * field.unit_price), 0);
        data.items = fields.map((field: any) => ({
          product_id: field.product_id,
          po_item_id: field.po_item_id,
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

  const handleFormSubmit = (data: any) => {
    if (errorMessage) {
      alert('Cannot submit GRN due to missing product names. Please resolve the errors by editing the product records.');
      return;
    }
    if (validateQuantities()) {
      _handleSubmitForm(data);
    }
  };

  useEffect(() => {
    if (mode === 'create' && !nextVoucherNumber && !isLoading) {
      voucherService.getNextVoucherNumber(config.nextNumberEndpoint)
        .then(number => setValue('voucher_number', number))
        .catch(err => console.error('Failed to fetch voucher number:', err));
    }
  }, [mode, nextVoucherNumber, isLoading, setValue, config.nextNumberEndpoint]);

  const handleVoucherClick = async (voucher: any) => {
    handleView(voucher.id);
  };

  useEffect(() => {
    if (voucherData && (mode === 'view' || mode === 'edit')) {
      console.log('[GoodsReceiptNotePage] voucherData for view/edit:', JSON.stringify(voucherData, null, 2));
      const mappedData = {
        ...voucherData,
        date: voucherData.grn_date ? voucherData.grn_date.split('T')[0] : '',
        items: voucherData.items.map(item => ({
          ...item,
          ordered_quantity: item.ordered_quantity,
          received_quantity: item.received_quantity,
          accepted_quantity: item.accepted_quantity,
          rejected_quantity: item.rejected_quantity,
          product_name: item.name_1 || item.product?.product_name || item.product_name || 'Product Not Found',
          po_item_id: item.po_item_id,
        })),
        reference_voucher_type: 'purchase-order',
        reference_voucher_number: voucherData.voucher_number_1 || voucherData.purchase_order?.voucher_number || voucherData.purchase_order_id
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
            po_item_id: item.po_item_id,
          });
        });
      }
    }
  }, [voucherData, mode, reset, setValue, append, remove]);

  const indexContent = (
    <>
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
                <TableCell colSpan="4" align="center">No goods receipt notes available</TableCell>
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
      {errorMessage && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {errorMessage}
        </Alert>
      )}
      <form id="voucherForm" onSubmit={handleSubmit(onSubmit)} style={voucherStyles.formContainer}>
        <Grid container spacing={0.5}>
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
                disabled={mode === 'view' || !!po_id}
              />
            )}
          </Grid>
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
                disabled={mode === 'view' || !selectedVoucherType || !!po_id}
              />
            )}
          </Grid>
          <Grid size={6}>
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
          <Grid size={12} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 27 }}>
            <Typography variant="h6" sx={{ fontSize: 16, fontWeight: 'bold', textAlign: 'center' }}>Items</Typography>
          </Grid>
          <Grid size={12}>
            {isItemsLoading ? (
              <Box display="flex" justifyContent="center" alignItems="center" minHeight="100px">
                <CircularProgress size={24} />
              </Box>
            ) : (
              <TableContainer component={Paper} sx={{ maxHeight: 300, ...voucherStyles.centeredTable, ...voucherStyles.optimizedTableContainer }}>
                <Table stickyHeader size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={voucherStyles.grnTableColumns.productName}>Product</TableCell>
                      <TableCell sx={voucherStyles.grnTableColumns.orderQty}>Order Qty</TableCell>
                      <TableCell sx={voucherStyles.grnTableColumns.receivedQty}>Received Qty</TableCell>
                      <TableCell sx={voucherStyles.grnTableColumns.acceptedQty}>Accepted Qty</TableCell>
                      <TableCell sx={voucherStyles.grnTableColumns.rejectedQty}>Rejected Qty</TableCell>
                      <TableCell sx={{ width: 50 }}>Edit</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {fields.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan="6" align="center">
                          No items available
                        </TableCell>
                      </TableRow>
                    ) : (
                      fields.map((field: any, index: number) => (
                        <TableRow key={field.id}>
                          <TableCell sx={{ p: 1, textAlign: 'center' }}>
                            <TextField
                              fullWidth
                              value={watch(`items.${index}.product_name`) || 'Product Not Found'}
                              disabled
                              size="small"
                              inputProps={{ style: { textAlign: 'center' } }}
                              error={!watch(`items.${index}.product_name`)}
                            />
                          </TableCell>
                          <TableCell sx={{ p: 1, textAlign: 'center' }}>
                            <TextField
                              type="number"
                              value={watch(`items.${index}.ordered_quantity`) || 0}
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
                          <TableCell sx={{ p: 1, textAlign: 'center' }}>
                            <IconButton
                              size="small"
                              onClick={() => handleEditProduct(field.product_id)}
                              disabled={mode === 'view'}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Grid>
        </Grid>
      </form>
      <Dialog open={grnCompleteDialogOpen} onClose={() => {
        setGrnCompleteDialogOpen(false);
        router.push('/vouchers/Purchase-Vouchers/grn');
      }}>
        <DialogTitle>GRN Already Complete</DialogTitle>
        <DialogContent>
          <Typography>
            The GRN for this Purchase Order is already complete.{' '}
            <Link href={`/vouchers/Purchase-Vouchers/grn?grn_id=${existingGrnId}`} passHref>
              View the existing GRN
            </Link>
            .
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setGrnCompleteDialogOpen(false);
            router.push('/vouchers/Purchase-Vouchers/grn');
          }}>Close</Button>
        </DialogActions>
      </Dialog>
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
      <AddVendorModal 
        open={showAddVendorModal}
        onClose={() => setShowAddVendorModal(false)}
        onVendorAdded={refreshMasterData}
        loading={addVendorLoading}
        setLoading={setAddVendorLoading}
      />
      <AddProductModal 
        open={showAddProductModal}
        onClose={handleProductModalClose}
        onProductAdded={refreshMasterData}
        loading={addProductLoading}
        setLoading={setAddProductLoading}
        productId={editProductId}
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