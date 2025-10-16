// frontend/src/pages/vouchers/Sales-Vouchers/delivery-challan.tsx
import React, { useMemo, useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  Typography,
  Grid,
  CircularProgress,
  Container,
  Autocomplete,
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import AddCustomerModal from '../../../components/AddCustomerModal';
import AddProductModal from '../../../components/AddProductModal';
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import TrackingDetailsDialog from '../../../components/TrackingDetailsDialog';
import VoucherLayout from '../../../components/VoucherLayout';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import VoucherReferenceDropdown from '../../../components/VoucherReferenceDropdown';
import VoucherItemTable from '../../../components/VoucherItemTable';
import VoucherFormTotals from '../../../components/VoucherFormTotals';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, getVoucherStyles } from '../../../utils/voucherUtils';
import { getStock } from '../../../services/masterService';
import { voucherService } from '../../../services/vouchersService';
import api from '../../../lib/api';
import { useCompany } from "../../../context/CompanyContext";
import { useGstValidation } from "../../../hooks/useGstValidation";
import { useVoucherDiscounts } from "../../../hooks/useVoucherDiscounts";
import { handleFinalSubmit, handleDuplicate, getStockColor } from "../../../utils/voucherHandlers";
import voucherFormStyles from "../../../styles/voucherFormStyles";
import { useRouter } from "next/router";
import { useQueryClient } from "@tanstack/react-query";
import { useWatch } from "react-hook-form"; // Added missing import for useWatch
import { useEntityBalance, getBalanceDisplayText } from "../../../hooks/useEntityBalance"; // Added for customer balance display

const DeliveryChallanPage: React.FC = () => {
  const { company, isLoading: companyLoading } = useCompany();
  const router = useRouter();
  const config = getVoucherConfig('delivery-challan');
  const voucherStyles = getVoucherStyles();
  const queryClient = useQueryClient();
  const processedRef = useRef<Set<number>>(new Set());

  const {
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
    contextMenu,
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
    customerList,
    productList,
    voucherData,
    nextVoucherNumber,
    sortedVouchers,
    latestVouchers,
    computedItems,
    totalAmount,
    totalSubtotal,
    totalCgst,
    totalSgst,
    totalIgst,
    totalDiscount,
    totalTaxable,
    gstBreakdown,
    isIntrastate,
    createMutation,
    updateMutation,
    handleCreate,
    handleEdit,
    handleView,
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
    totalRoundOff,
    handleRevise,
  } = useVoucherPage(config);

  const [showVoucherListModal, setShowVoucherListModal] = useState(false);
  const [submitData, setSubmitData] = useState<any>(null);
  const [roundOffConfirmOpen, setRoundOffConfirmOpen] = useState(false);
  const [stockLoading, setStockLoading] = useState<{ [key: number]: boolean }>({});
  const selectedCustomerId = watch("customer_id");
  
  // Fetch customer balance
  const { balance: customerBalance, loading: customerBalanceLoading } = useEntityBalance('customer', selectedCustomerId);

  // Use new hooks
  const { gstError } = useGstValidation(selectedCustomerId, customerList);
  const [descriptionEnabled, setDescriptionEnabled] = useState(false);

  const handleToggleDescription = (checked: boolean) => {
    setDescriptionEnabled(checked);
    if (!checked) {
      fields.forEach((_, index) => setValue(`items.${index}.description`, ''));
    }
  };

  const selectedProducts = useMemo(() => {
    return fields.map((_, index) => {
      const productId = watch(`items.${index}.product_id`);
      return productList?.find((p: any) => p.id === productId) || null;
    });
  }, [fields, productList, watch]); // Removed fields.length and spread map as deps - use fields ref

  const productIds = useWatch({
    control,
    name: fields.map((_, i) => `items.${i}.product_id`),
  });

  // Reset processed when fields length changes
  useEffect(() => {
    processedRef.current = new Set();
  }, [fields.length]);

  // Fetch stock when productIds change or on load
  useEffect(() => {
    productIds.forEach((productId: number, index: number) => {
      if (productId && !processedRef.current.has(index) && !stockLoading[index]) {
        const currentStock = watch(`items.${index}.current_stock`);
        if (currentStock === 0 || currentStock === undefined) {
          setStockLoading(prev => ({ ...prev, [index]: true }));
          getStock({ queryKey: ["", { product_id: productId }] })
            .then(res => {
              const stockData = res[0] || { quantity: 0 };
              setValue(`items.${index}.current_stock`, stockData.quantity);
            })
            .catch(err => console.error("Failed to fetch stock:", err))
            .finally(() => {
              setStockLoading(prev => ({ ...prev, [index]: false }));
              processedRef.current.add(index);
            });
        } else {
          processedRef.current.add(index);
        }
      }
    });
  }, [productIds, fields, stockLoading, setValue, watch]);

  useEffect(() => {
    if (mode === "create" && !nextVoucherNumber && !isLoading) {
      voucherService.getNextVoucherNumber(config.nextNumberEndpoint)
        .then((number) => setValue("voucher_number", number))
        .catch((err) => console.error("Failed to fetch voucher number:", err));
    }
  }, [mode, nextVoucherNumber, isLoading, setValue, config.nextNumberEndpoint]);

  const handleVoucherClick = (voucher: any) => {
    // Use the voucher from list (assumes full data from backend joins)
    setMode("view");
    reset({
      ...voucher,
      date: voucher.date ? new Date(voucher.date).toISOString().split('T')[0] : '',
      items: voucher.items.map((item: any) => ({
        ...item,
      })),
    });
  };

  const handleEditWithData = (voucher: any) => {
    if (!voucher || !voucher.id) return;
    handleEdit(voucher.id);
    reset({
      ...voucher,
      date: voucher.date ? new Date(voucher.date).toISOString().split('T')[0] : '',
      items: voucher.items.map((item: any) => ({
        ...item,
      })),
    });
    // Prefill cache to avoid duplicate fetch
    queryClient.setQueryData(['delivery-challan', voucher.id], voucher);
  };

  const handleViewWithData = (voucher: any) => {
    if (!voucher || !voucher.id) return;
    handleView(voucher.id);
    reset({
      ...voucher,
      date: voucher.date ? new Date(voucher.date).toISOString().split('T')[0] : '',
      items: voucher.items.map((item: any) => ({
        ...item,
      })),
    });
    // Prefill cache to avoid duplicate fetch
    queryClient.setQueryData(['delivery-challan', voucher.id], voucher);
  };

  useEffect(() => {
    if (voucherData && (mode === "view" || mode === "edit")) {
      const formattedDate = voucherData.date ? new Date(voucherData.date).toISOString().split('T')[0] : '';
      const formattedData = {
        ...voucherData,
        date: formattedDate,
      };
      reset(formattedData);
      if (voucherData.items && voucherData.items.length > 0) {
        remove();
        voucherData.items.forEach((item: any) => {
          append({
            ...item,
            product_id: item.product_id,
            product_name: item.product?.product_name || item.product_name || "",
            quantity: item.quantity,
            unit: item.unit,
            current_stock: item.current_stock || 0,
            reorder_level: item.reorder_level || 0,
            description: item.description || '',
          });
        });
      }
    }
  }, [voucherData, mode, reset, append, remove]);

  const onSubmit = (data: any) => {
    if (totalRoundOff !== 0) {
      setSubmitData(data);
      setRoundOffConfirmOpen(true);
      return;
    }
    handleFinalSubmit(
      data,
      watch,
      computedItems,
      isIntrastate,
      totalAmount,
      totalRoundOff,
      lineDiscountEnabled,
      lineDiscountType,
      totalDiscountEnabled,
      totalDiscountType,
      createMutation,
      updateMutation,
      mode,
      handleGeneratePDF,
      refreshMasterData,
      config
    );
  };

  const handleCancel = () => {
    setMode("view");
    if (voucherData) reset(voucherData);
  };

  // State for tracking dialog
  const [trackingDialogOpen, setTrackingDialogOpen] = useState(false);
  const [selectedVoucherForTracking, setSelectedVoucherForTracking] = useState<any>(null);

  const handleEditTracking = (voucher: any) => {
    setSelectedVoucherForTracking(voucher);
    setTrackingDialogOpen(true);
  };

  const handleTrackingDialogClose = () => {
    setTrackingDialogOpen(false);
    setSelectedVoucherForTracking(null);
    // Refresh the voucher list to show updated tracking
    refreshMasterData();
  };

  const enhancedCustomerOptions = [...(customerList || []), { id: null, name: "Add New Customer..." }];

  const indexContent = (
    <TableContainer sx={{ maxHeight: 400 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Voucher No.</TableCell>
            <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Date</TableCell>
            <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Customer</TableCell>
            <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Total Quantity</TableCell>
            <TableCell align="right" sx={{ fontSize: 15, fontWeight: "bold", p: 0, width: 40 }}></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {latestVouchers.length === 0 ? (
            <TableRow><TableCell colSpan={5} align="center">No delivery challans available</TableCell></TableRow>
          ) : (
            latestVouchers.slice(0, 7).map((voucher: any) => (
              <TableRow key={voucher.id} hover onContextMenu={(e) => { e.preventDefault(); handleContextMenu(e, voucher); }} sx={{ cursor: "pointer" }}>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }} onClick={() => handleViewWithData(voucher)}>{voucher.voucher_number}</TableCell>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{voucher.date ? new Date(voucher.date).toLocaleDateString() : "N/A"}</TableCell>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{customerList?.find((c: any) => c.id === voucher.customer_id)?.name || "N/A"}</TableCell>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{voucher.items?.reduce((sum: number, item: any) => sum + item.quantity, 0) || 0}</TableCell>
                <TableCell align="right" sx={{ fontSize: 12, p: 0 }}>
                  <VoucherContextMenu
                    voucher={voucher}
                    voucherType="Delivery Challan"
                    onView={handleViewWithData}
                    onEdit={handleEditWithData}
                    onDelete={handleDelete}
                    onPrint={handleGeneratePDF}
                    onDuplicate={(id) => handleDuplicate(id, voucherList, reset, setMode, "Delivery Challan")}
                    onEditTracking={handleEditTracking}
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

  const formHeader = (
    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <Typography variant="h5" sx={{ fontSize: 20, fontWeight: "bold" }}>
        {config.voucherTitle} - {mode === "create" ? "Create" : mode === "edit" ? "Edit" : "View"}
      </Typography>
      <VoucherHeaderActions
        mode={mode}
        voucherType={config.voucherTitle}
        voucherRoute="/vouchers/Sales-Vouchers/delivery-challan"
        currentId={mode !== "create" ? voucherData?.id : null}
        onEdit={() => voucherData && voucherData.id && handleEditWithData(voucherData)}
        onCreate={handleCreate}
        onCancel={handleCancel}
      />
    </Box>
  );

  const formContent = (
    <Box>
      {gstError && <Alert severity="error" sx={{ mb: 2 }}>{gstError}</Alert>}
      <form id="voucherForm" onSubmit={handleSubmit(onSubmit)} style={voucherStyles.formContainer}>
        <Grid container spacing={1}>
          <Grid size={6}>
            <TextField 
              fullWidth 
              label="Voucher Number" 
              {...control.register("voucher_number")} 
              disabled 
              sx={{ 
                ...voucherFormStyles.field, 
                '& .MuiInputBase-input': { textAlign: 'center', fontWeight: 'bold' } 
              }} 
              InputLabelProps={{ shrink: true }} 
            />
          </Grid>
          <Grid size={6}>
            <TextField 
              fullWidth 
              label="Date" 
              type="date" 
              {...control.register("date")} 
              disabled={mode === "view"} 
              sx={{ 
                ...voucherFormStyles.field, 
                '& .MuiInputBase-input': { textAlign: 'center' } 
              }} 
              InputLabelProps={{ shrink: true }} 
            />
          </Grid>
          <Grid size={4}>
            <VoucherReferenceDropdown
              voucherType="delivery-challan"
              value={{ referenceType: watch('reference_type'), referenceId: watch('reference_id'), referenceNumber: watch('reference_number') }}
              onChange={(reference) => { setValue('reference_type', reference.referenceType || ''); setValue('reference_id', reference.referenceId || null); setValue('reference_number', reference.referenceNumber || ''); }}
              disabled={mode === 'view'}
              onReferenceSelected={handleReferenceSelected}
            />
          </Grid>
          <Grid size={3}>
            <Autocomplete 
              size="small" 
              options={enhancedCustomerOptions} 
              getOptionLabel={(option: any) => option?.name || ""} 
              value={customerList?.find((c: any) => c.id === watch("customer_id")) || null} 
              onChange={(_, newValue) => { 
                if (newValue?.id === null) setShowAddCustomerModal(true); 
                else setValue("customer_id", newValue?.id || null); 
              }} 
              renderInput={(params) => 
                <TextField 
                  {...params} 
                  label="Customer" 
                  error={!!errors.customer_id} 
                  helperText={errors.customer_id ? "Required" : ""} 
                  sx={voucherFormStyles.field} 
                  InputLabelProps={{ shrink: true }} 
                />
              } 
              disabled={mode === "view"} 
            />
          </Grid>
          <Grid size={1}>
            {selectedCustomerId && (
              <TextField
                fullWidth
                label="Balance"
                value={customerBalanceLoading ? "..." : getBalanceDisplayText(customerBalance)}
                disabled
                size="small"
                sx={{ 
                  ...voucherFormStyles.field,
                  '& .MuiInputBase-input': { 
                    textAlign: 'right',
                    fontWeight: 'bold',
                    color: customerBalance > 0 ? '#d32f2f' : customerBalance < 0 ? '#2e7d32' : '#666'
                  }
                }}
                InputLabelProps={{ shrink: true }}
              />
            )}
          </Grid>
          <Grid size={8}>
            <TextField 
              fullWidth 
              label="Payment Terms" 
              {...control.register("payment_terms")} 
              disabled={mode === "view"} 
              sx={voucherFormStyles.field} 
              InputLabelProps={{ shrink: true }} 
            />
          </Grid>
          <Grid size={12}>
            <TextField 
              fullWidth 
              label="Notes" 
              {...control.register("notes")} 
              multiline 
              rows={1} 
              disabled={mode === "view"} 
              sx={voucherFormStyles.notesField} 
              InputLabelProps={{ shrink: true }} 
            />
          </Grid>
          <Grid size={12} sx={voucherFormStyles.itemsHeader}>
            <Typography variant="h6" sx={{ fontSize: 16, fontWeight: "bold" }}>Items</Typography>
          </Grid>
          <Grid size={12}>
            <VoucherItemTable
              fields={fields}
              control={control}
              watch={watch}
              setValue={setValue}
              remove={remove}
              append={append}
              mode={mode}
              isIntrastate={isIntrastate}
              computedItems={computedItems}
              descriptionEnabled={descriptionEnabled}
              handleToggleDescription={handleToggleDescription}
              stockLoading={stockLoading}
              getStockColor={getStockColor}
              selectedProducts={selectedProducts}
              showDescriptionCheckbox={mode !== "view"}
            />
          </Grid>
          <Grid size={12}>
            <Typography>Total Quantity: {fields.reduce((sum, _, index) => sum + (watch(`items.${index}.quantity`) || 0), 0)}</Typography>
          </Grid>
        </Grid>
      </form>
      <Dialog open={roundOffConfirmOpen} onClose={() => setRoundOffConfirmOpen(false)}>
        <DialogTitle>Confirm Round Off</DialogTitle>
        <DialogContent><Typography>Round off amount is {totalRoundOff.toFixed(2)}. Proceed with save?</Typography></DialogContent>
        <DialogActions>
          <Button onClick={() => setRoundOffConfirmOpen(false)}>Cancel</Button>
          <Button onClick={() => { setRoundOffConfirmOpen(false); if (submitData) handleFinalSubmit(submitData, watch, computedItems, isIntrastate, totalAmount, totalRoundOff, lineDiscountEnabled, lineDiscountType, totalDiscountEnabled, totalDiscountType, createMutation, updateMutation, mode, handleGeneratePDF, refreshMasterData, config); }} variant="contained">Confirm</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  if (isLoading || companyLoading) {
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
        formHeader={formHeader}
        formContent={formContent}
        onShowAll={() => setShowVoucherListModal(true)}
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
      <AddCustomerModal open={showAddCustomerModal} onClose={() => setShowAddCustomerModal(false)} onAdd={(newCustomer) => { setValue("customer_id", newCustomer.id); refreshMasterData(); }} loading={addCustomerLoading} setLoading={setAddCustomerLoading} />
      <AddProductModal open={showAddProductModal} onClose={() => setShowAddProductModal(false)} onAdd={(newProduct) => { setValue(`items.${addingItemIndex}.product_id`, newProduct.id); setValue(`items.${addingItemIndex}.product_name`, newProduct.product_name); setValue(`items.${addingItemIndex}.unit_price`, newProduct.unit_price || 0); setValue(`items.${addingItemIndex}.original_unit_price`, newProduct.unit_price || 0); setValue(`items.${addingItemIndex}.gst_rate`, newProduct.gst_rate ?? 18); setValue(`items.${addingItemIndex}.cgst_rate`, isIntrastate ? (newProduct.gst_rate ?? 18) / 2 : 0); setValue(`items.${addingItemIndex}.sgst_rate`, isIntrastate ? (newProduct.gst_rate ?? 18) / 2 : 0); setValue(`items.${addingItemIndex}.igst_rate`, isIntrastate ? 0 : newProduct.gst_rate ?? 18); setValue(`items.${addingItemIndex}.unit`, newProduct.unit || ""); setValue(`items.${addingItemIndex}.reorder_level`, newProduct.reorder_level || 0); refreshMasterData(); }} loading={addProductLoading} setLoading={setAddProductLoading} />
      <AddShippingAddressModal open={showShippingModal} onClose={() => setShowShippingModal(false)} loading={addShippingLoading} setLoading={setAddShippingLoading} />
      <VoucherContextMenu 
        contextMenu={contextMenu} 
        voucher={null} 
        voucherType="Delivery Challan" 
        onClose={handleCloseContextMenu} 
        onView={handleViewWithData} 
        onEdit={handleEditWithData} 
        onDelete={handleDelete} 
        onPrint={handleGeneratePDF} 
        onDuplicate={(id) => handleDuplicate(id, voucherList, reset, setMode, "Delivery Challan")}
        onEditTracking={handleEditTracking}
      />
      {selectedVoucherForTracking && (
        <TrackingDetailsDialog
          open={trackingDialogOpen}
          onClose={handleTrackingDialogClose}
          voucherType="delivery_challan"
          voucherId={selectedVoucherForTracking.id}
          voucherNumber={selectedVoucherForTracking.voucher_number}
        />
      )}
    </>
  );
};

export default DeliveryChallanPage;