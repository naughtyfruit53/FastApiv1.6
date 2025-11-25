// frontend/src/pages/vouchers/Purchase-Vouchers/purchase-return.tsx
import React, { useMemo, useState, useEffect, useRef } from "react";
import {
  Box,
  TextField,
  Typography,
  Grid,
  CircularProgress,
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
} from "@mui/material";
import AddVendorModal from "../../../components/AddVendorModal";
import AddProductModal from "../../../components/AddProductModal";
import AddShippingAddressModal from "../../../components/AddShippingAddressModal";
import VoucherContextMenu from "../../../components/VoucherContextMenu";
import VoucherLayout from "../../../components/VoucherLayout";
import VoucherHeaderActions from "../../../components/VoucherHeaderActions";
import VoucherListModal from "../../../components/VoucherListModal";
import VoucherReferenceDropdown from "../../../components/VoucherReferenceDropdown";
import VoucherItemTable from "../../../components/VoucherItemTable";
import VoucherFormTotals from "../../../components/VoucherFormTotals";
import AdditionalCharges, { AdditionalChargesData } from '../../../components/AdditionalCharges';
import VoucherDateConflictModal from '../../../components/VoucherDateConflictModal';
import api from '../../../lib/api';
import { useVoucherPage } from "../../../hooks/useVoucherPage";
import { getVoucherConfig, getVoucherStyles, calculateVoucherTotals } from "../../../utils/voucherUtils";
import { getStock } from "../../../services/masterService";
import { voucherService } from "../../../services/vouchersService";
import { useCompany } from "../../../context/CompanyContext";
import { useRouter } from "next/router";
import { useGstValidation } from "../../../hooks/useGstValidation";
import { useVoucherDiscounts } from "../../../hooks/useVoucherDiscounts";
import { handleFinalSubmit, handleDuplicate, getStockColor } from "../../../utils/voucherHandlers";
import voucherFormStyles from "../../../styles/voucherFormStyles";
import { useQueryClient, useQuery } from "@tanstack/react-query";
import { useWatch } from "react-hook-form"; // Added missing import for useWatch
import { useEntityBalance, getBalanceDisplayText } from "../../../hooks/useEntityBalance"; // Added for vendor balance display
import { formatCurrency } from "../../../utils/currencyUtils";
import { useAuth } from '../../../context/AuthContext';

import { ProtectedPage } from '../../../components/ProtectedPage';
const PurchaseReturnPage: React.FC = () => {
  const { company, isLoading: companyLoading } = useCompany();
  const { isOrgContextReady } = useAuth();
  const router = useRouter();
  const { from_grn_id } = router.query;
  const config = getVoucherConfig("purchase-return");
  const voucherStyles = getVoucherStyles();
  const queryClient = useQueryClient();
  const processedRef = useRef<Set<number>>(new Set());

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
    contextMenu,
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
    handleGeneratePDF,
    handleDelete,
    refreshMasterData,
    getAmountInWords,
    totalRoundOff,
  } = useVoucherPage(config);

  const [showVoucherListModal, setShowVoucherListModal] = useState(false);
  const [submitData, setSubmitData] = useState<any>(null);
  const [roundOffConfirmOpen, setRoundOffConfirmOpen] = useState(false);
  const [stockLoading, setStockLoading] = useState<{ [key: number]: boolean }>({});
  const selectedVendorId = watch("vendor_id");
  
  // Fetch vendor balance
  const { balance: vendorBalance, loading: vendorBalanceLoading } = useEntityBalance('vendor', selectedVendorId);

  // Use new hooks
  const { gstError } = useGstValidation(selectedVendorId, vendorList);
  const {
    lineDiscountEnabled,
    lineDiscountType,
    totalDiscountEnabled,
    totalDiscountType,
    discountDialogOpen,
    discountDialogFor,
    handleToggleLineDiscount,
    handleToggleTotalDiscount,
    handleDiscountTypeSelect,
    handleDiscountDialogClose,
  } = useVoucherDiscounts();
  const [descriptionEnabled, setDescriptionEnabled] = useState(false);
  const [additionalChargesEnabled, setAdditionalChargesEnabled] = useState(false);
  const [additionalChargesModalOpen, setAdditionalChargesModalOpen] = useState(false);
  const [additionalCharges, setAdditionalCharges] = useState<AdditionalChargesData>({
    freight: 0,
    installation: 0,
    packing: 0,
    insurance: 0,
    loading: 0,
    unloading: 0,
    miscellaneous: 0,
  });
  const [localAdditionalCharges, setLocalAdditionalCharges] = useState<AdditionalChargesData>(additionalCharges);
  
  // State for voucher date conflict detection
  const [conflictInfo, setConflictInfo] = useState<any>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);
  const [pendingDate, setPendingDate] = useState<string | null>(null);

  const handleToggleDescription = (checked: boolean) => {
    setDescriptionEnabled(checked);
    if (!checked) {
      fields.forEach((_, index) => setValue(`items.${index}.description`, ''));
    }
  };

  const handleToggleAdditionalCharges = (checked: boolean) => {
    setAdditionalChargesEnabled(checked);
    if (checked) {
      setLocalAdditionalCharges(additionalCharges);
      setAdditionalChargesModalOpen(true);
    } else {
      setAdditionalCharges({
        freight: 0,
        installation: 0,
        packing: 0,
        insurance: 0,
        loading: 0,
        unloading: 0,
        miscellaneous: 0,
      });
    }
  };

  const handleAdditionalChargesConfirm = () => {
    setAdditionalCharges(localAdditionalCharges);
    setAdditionalChargesModalOpen(false);
  };

  const handleAdditionalChargesCancel = () => {
    if (Object.values(localAdditionalCharges).every(value => value === 0)) {
      setAdditionalChargesEnabled(false);
    }
    setAdditionalChargesModalOpen(false);
  };

  const productIds = useWatch({
    control,
    name: fields.map((_, i) => `items.${i}.product_id`),
  });

  const productNames = useWatch({
    control,
    name: fields.map((_, i) => `items.${i}.product_name`),
  });

  const selectedProducts = useMemo(() => {
    return fields.map((_, index) => {
      const productId = productIds[index];
      const productName = productNames[index];
      return productList?.find((p: any) => p.id === productId) || { id: productId, product_name: productName || "" };
    });
  }, [fields.length, productList, productIds, productNames]);

  // Use useWatch for items and total_discount to ensure reactivity
  const items = useWatch({ control, name: "items" }) || [];
  const totalDiscountValue = useWatch({ control, name: "total_discount" }) || 0;

  // Override totals with additional charges
  const totalsWithAdditionalCharges = useMemo(() => {
    console.log('Calculating totals with items:', items); // Debug log to check if items are updating correctly
    return calculateVoucherTotals(
      items,
      isIntrastate,
      lineDiscountEnabled ? lineDiscountType : null,
      totalDiscountEnabled ? totalDiscountType : null,
      totalDiscountValue,
      additionalCharges
    );
  }, [items, isIntrastate, lineDiscountEnabled, lineDiscountType, totalDiscountEnabled, totalDiscountType, totalDiscountValue, additionalCharges]);

  const localComputedItems = totalsWithAdditionalCharges.computedItems; // Use the fully calculated items for table display

  const finalTotalAmount = totalsWithAdditionalCharges.totalAmount;
  const finalTotalAdditionalCharges = totalsWithAdditionalCharges.totalAdditionalCharges;

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
        cgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
        sgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
        igst_rate: isIntrastate ? 0 : item.gst_rate,
      })),
    });
    if (voucher.additional_charges) {
      setAdditionalCharges(voucher.additional_charges);
      setAdditionalChargesEnabled(Object.values(voucher.additional_charges).some(v => v > 0));
    } else {
      setAdditionalCharges({ freight: 0, installation: 0, packing: 0, insurance: 0, loading: 0, unloading: 0, miscellaneous: 0 });
      setAdditionalChargesEnabled(false);
    }
  };

  const handleEditWithData = (voucher: any) => {
    if (!voucher || !voucher.id) return;
    handleEdit(voucher.id);
    reset({
      ...voucher,
      date: voucher.date ? new Date(voucher.date).toISOString().split('T')[0] : '',
      items: voucher.items.map((item: any) => ({
        ...item,
        cgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
        sgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
        igst_rate: isIntrastate ? 0 : item.gst_rate,
      })),
    });
    if (voucher.additional_charges) {
      setAdditionalCharges(voucher.additional_charges);
      setAdditionalChargesEnabled(Object.values(voucher.additional_charges).some(v => v > 0));
    } else {
      setAdditionalCharges({ freight: 0, installation: 0, packing: 0, insurance: 0, loading: 0, unloading: 0, miscellaneous: 0 });
      setAdditionalChargesEnabled(false);
    }
    // Prefill cache to avoid duplicate fetch
    queryClient.setQueryData(['purchase-return', voucher.id], voucher);
  };

  const handleViewWithData = (voucher: any) => {
    if (!voucher || !voucher.id) return;
    handleView(voucher.id);
    reset({
      ...voucher,
      date: voucher.date ? new Date(voucher.date).toISOString().split('T')[0] : '',
      items: voucher.items.map((item: any) => ({
        ...item,
        cgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
        sgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
        igst_rate: isIntrastate ? 0 : item.gst_rate,
      })),
    });
    if (voucher.additional_charges) {
      setAdditionalCharges(voucher.additional_charges);
      setAdditionalChargesEnabled(Object.values(voucher.additional_charges).some(v => v > 0));
    } else {
      setAdditionalCharges({ freight: 0, installation: 0, packing: 0, insurance: 0, loading: 0, unloading: 0, miscellaneous: 0 });
      setAdditionalChargesEnabled(false);
    }
    // Prefill cache to avoid duplicate fetch
    queryClient.setQueryData(['purchase-return', voucher.id], voucher);
  };

  useEffect(() => {
    if (voucherData && (mode === "view" || mode === "edit")) {
      const formattedDate = voucherData.date ? new Date(voucherData.date).toISOString().split('T')[0] : '';
      const formattedData = {
        ...voucherData,
        date: formattedDate,
      };
      reset(formattedData);
      if (voucherData.additional_charges) {
        setAdditionalCharges(voucherData.additional_charges);
        setAdditionalChargesEnabled(Object.values(voucherData.additional_charges).some(v => v > 0));
      } else {
        setAdditionalCharges({ freight: 0, installation: 0, packing: 0, insurance: 0, loading: 0, unloading: 0, miscellaneous: 0 });
        setAdditionalChargesEnabled(false);
      }
      if (voucherData.items && voucherData.items.length > 0) {
        remove();
        voucherData.items.forEach((item: any) => {
          append({
            ...item,
            product_id: item.product_id,
            product_name: item.product?.product_name || item.product_name || "",
            quantity: item.quantity,
            unit_price: item.unit_price,
            original_unit_price: item.product?.unit_price || item.unit_price || 0,
            discount_percentage: item.discount_percentage || 0,
            discount_amount: item.discount_amount || 0,
            gst_rate: item.gst_rate ?? 18,
            cgst_rate: isIntrastate ? (item.gst_rate ?? 18) / 2 : 0,
            sgst_rate: isIntrastate ? (item.gst_rate ?? 18) / 2 : 0,
            igst_rate: isIntrastate ? 0 : item.gst_rate ?? 18,
            unit: item.unit,
            current_stock: item.current_stock || 0,
            reorder_level: item.reorder_level || 0,
            description: item.description || '',
          });
        });
      }
    }
  }, [voucherData, mode, reset, append, remove, isIntrastate]);

  // Fetch voucher number when date changes and check for conflicts
  useEffect(() => {
    const fetchVoucherNumber = async () => {
      const currentDate = watch('date');
      if (currentDate && mode === 'create') {
        try {
          // Fetch new voucher number based on date
          const response = await api.get(
            `/purchase-returns/next-number`,
            { params: { voucher_date: currentDate } }
          );
          setValue('voucher_number', response.data);
          
          // Check for backdated conflicts
          const conflictResponse = await api.get(
            `/purchase-returns/check-backdated-conflict`,
            { params: { voucher_date: currentDate } }
          );
          
          if (conflictResponse.data.has_conflict) {
            setConflictInfo(conflictResponse.data);
            setShowConflictModal(true);
            setPendingDate(currentDate);
          }
        } catch (error) {
          console.error('Error fetching voucher number:', error);
        }
      }
    };
    
    fetchVoucherNumber();
  }, [watch('date'), mode, setValue]);

  const onSubmit = (data: any) => {
    if (from_grn_id) {
      data.grn_id = Number(from_grn_id);
    }
    if (totalRoundOff !== 0) {
      setSubmitData(data);
      setRoundOffConfirmOpen(true);
      return;
    }
    handleFinalSubmit(
      data,
      watch,
      localComputedItems,
      isIntrastate,
      finalTotalAmount,
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
      config,
      additionalCharges
    );
  };

  const handleCancel = () => {
    setMode("view");
    if (voucherData) reset(voucherData);
  };

  const enhancedVendorOptions = [...(vendorList || []), { id: null, name: "Add New Vendor..." }];

  // Conflict modal handlers
  const handleChangeDateToSuggested = () => {
    if (conflictInfo?.suggested_date) {
      setValue('date', conflictInfo.suggested_date.split('T')[0]);
      setShowConflictModal(false);
      setPendingDate(null);
    }
  };

  const handleProceedAnyway = () => {
    setShowConflictModal(false);
  };

  const handleCancelConflict = () => {
    setShowConflictModal(false);
    if (pendingDate) {
      setValue('date', '');
    }
    setPendingDate(null);
  };

  // New: Fetch and pre-populate from GRN if from_grn_id is present
  const { data: grnData } = useQuery({
    queryKey: ['grn', from_grn_id],
    queryFn: () => {
      if (!from_grn_id) return null;
      return voucherService.getGrnById(Number(from_grn_id));
    },
    enabled: !!from_grn_id && isOrgContextReady,
  });

  useEffect(() => {
    if (grnData && mode === 'create') {
      setValue('vendor_id', grnData.vendor_id);
      setValue('reference_type', 'goods-receipt-note');
      setValue('reference_id', grnData.id);
      setValue('reference_number', grnData.voucher_number);
      setValue('date', new Date().toISOString().split('T')[0]);

      // Clear existing items
      remove();

      // Append items from GRN with rejected quantities (only if rejected > 0, but add all for flexibility)
      grnData.items.forEach((item: any) => {
        const product = productList?.find((p: any) => p.id === item.product_id) || {};
        append({
          product_id: item.product_id,
          product_name: item.product_name || product.product_name || '',
          quantity: item.rejected_quantity || 0,
          unit_price: item.unit_price || product.unit_price || 0,
          original_unit_price: product.unit_price || 0,
          discount_percentage: 0,
          discount_amount: 0,
          gst_rate: product.gst_rate ?? 18,
          cgst_rate: isIntrastate ? (product.gst_rate ?? 18) / 2 : 0,
          sgst_rate: isIntrastate ? (product.gst_rate ?? 18) / 2 : 0,
          igst_rate: isIntrastate ? 0 : (product.gst_rate ?? 18),
          unit: item.unit || product.unit || '',
          current_stock: 0,
          reorder_level: product.reorder_level || 0,
          description: '',
        });
      });

      toast.success('Pre-populated rejection note from GRN with rejected quantities');
    }
  }, [grnData, mode, setValue, remove, append, isIntrastate, productList]);

  const indexContent = (
    <TableContainer sx={{ maxHeight: 400 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Voucher No.</TableCell>
            <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Date</TableCell>
            <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Vendor</TableCell>
            <TableCell align="center" sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}>Total Amount</TableCell>
            <TableCell align="right" sx={{ fontSize: 15, fontWeight: "bold", p: 0, width: 40 }}></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {latestVouchers.length === 0 ? (
            <TableRow><TableCell colSpan={5} align="center">No purchase returns available</TableCell></TableRow>
          ) : (
            latestVouchers.slice(0, 7).map((voucher: any) => (
              <TableRow key={voucher.id} hover onContextMenu={(e) => { e.preventDefault(); handleContextMenu(e, voucher); }} sx={{ cursor: "pointer" }}>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }} onClick={() => handleViewWithData(voucher)}>{voucher.voucher_number}</TableCell>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{voucher.date ? new Date(voucher.date).toLocaleDateString() : "N/A"}</TableCell>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{vendorList?.find((v: any) => v.id === voucher.vendor_id)?.name || "N/A"}</TableCell>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{formatCurrency(voucher.total_amount || 0)}</TableCell>
                <TableCell align="right" sx={{ fontSize: 12, p: 0 }}>
                  <VoucherContextMenu
                    voucher={voucher}
                    voucherType="Purchase Return"
                    onView={handleViewWithData}
                    onEdit={handleEditWithData}
                    onDelete={handleDelete}
                    onPrint={(voucher) => handleGeneratePDF(voucher)}
                    onDuplicate={(id) => handleDuplicate(id, voucherList, reset, setMode, "Purchase Return")}
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
        voucherRoute="/vouchers/Purchase-Vouchers/purchase-return"
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
      <form id="voucherForm" onSubmit={handleSubmit(onSubmit)} style={voucherFormStyles.formContainer}>
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
              voucherType="purchase-return"
              value={{ referenceType: watch('reference_type'), referenceId: watch('reference_id'), referenceNumber: watch('reference_number') }}
              onChange={(reference) => { setValue('reference_type', reference.referenceType || ''); setValue('reference_id', reference.referenceId || null); setValue('reference_number', reference.referenceNumber || ''); }}
              disabled={mode === 'view'}
              onReferenceSelected={handleReferenceSelected}
            />
          </Grid>
          <Grid size={3}>
            <Autocomplete 
              size="small" 
              options={enhancedVendorOptions} 
              getOptionLabel={(option: any) => {
                if (typeof option === 'number') return '';
                return option?.name || "";
              }} 
              value={vendorList?.find((v: any) => v.id === watch("vendor_id")) || null} 
              onChange={(_, newValue) => { 
                if (newValue?.id === null) setShowAddVendorModal(true); 
                else setValue("vendor_id", newValue?.id || null); 
              }} 
              renderInput={(params) => 
                <TextField 
                  {...params} 
                  label="Vendor" 
                  error={!!errors.vendor_id} 
                  helperText={errors.vendor_id ? "Required" : ""} 
                  sx={voucherFormStyles.field} 
                  InputLabelProps={{ shrink: true }} 
                />
              } 
              disabled={mode === "view"} 
            />
          </Grid>
          <Grid size={1}>
            {selectedVendorId && (
              <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '100%' }}>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    textAlign: 'right',
                    fontWeight: 'bold',
                    fontSize: '0.875rem',
                    color: vendorBalance > 0 ? '#d32f2f' : vendorBalance < 0 ? '#2e7d32' : '#666'
                  }}
                >
                  {vendorBalanceLoading ? "..." : getBalanceDisplayText(vendorBalance)}
                </Typography>
              </Box>
            )}
          </Grid>
          <Grid size={4}>
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
              rows={2} 
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
              computedItems={localComputedItems} // Use fully calculated items for accurate line totals
              lineDiscountEnabled={lineDiscountEnabled}
              lineDiscountType={lineDiscountType}
              totalDiscountEnabled={totalDiscountEnabled}
              descriptionEnabled={descriptionEnabled}
              additionalChargesEnabled={additionalChargesEnabled}
              handleToggleLineDiscount={handleToggleLineDiscount}
              handleToggleTotalDiscount={handleToggleTotalDiscount}
              handleToggleDescription={handleToggleDescription}
              handleToggleAdditionalCharges={handleToggleAdditionalCharges}
              stockLoading={stockLoading}
              getStockColor={getStockColor}
              selectedProducts={selectedProducts}
              showLineDiscountCheckbox={mode !== "view"}
              showTotalDiscountCheckbox={mode !== "view"}
              showDescriptionCheckbox={mode !== "view"}
              showAdditionalChargesCheckbox={mode !== "view"}
            />
          </Grid>
          {additionalChargesEnabled && mode === 'view' && (
            <Grid size={12}>
              <AdditionalCharges
                charges={additionalCharges}
                onChange={setAdditionalCharges}
                mode={mode}
              />
            </Grid>
          )}
          <Grid size={12}>
            <VoucherFormTotals
              totalSubtotal={totalsWithAdditionalCharges.totalSubtotal}
              totalCgst={totalsWithAdditionalCharges.totalCgst}
              totalSgst={totalsWithAdditionalCharges.totalSgst}
              totalIgst={totalsWithAdditionalCharges.totalIgst}
              totalAmount={totalsWithAdditionalCharges.totalAmount}
              totalRoundOff={totalsWithAdditionalCharges.totalRoundOff}
              totalAdditionalCharges={totalsWithAdditionalCharges.totalAdditionalCharges}
              additionalCharges={additionalCharges} // Added passing detailed charges
              isIntrastate={isIntrastate}
              totalDiscountEnabled={totalDiscountEnabled}
              totalDiscountType={totalDiscountType}
              mode={mode}
              watch={watch}
              control={control}
              setValue={setValue}
              handleToggleTotalDiscount={handleToggleTotalDiscount}
              getAmountInWords={getAmountInWords}
            />
          </Grid>
          <Grid size={12}>
            <TextField
              fullWidth
              label="Amount in Words"
              value={getAmountInWords(finalTotalAmount)}
              disabled
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14 } }}
              size="small"
              sx={{ mt: 2 }}
            />
          </Grid>
        </Grid>
      </form>
      <Dialog open={discountDialogOpen} onClose={handleDiscountDialogClose}>
        <DialogTitle>Select Discount Type</DialogTitle>
        <DialogContent><Typography>Please select the discount type for {discountDialogFor} discount.</Typography></DialogContent>
        <DialogActions>
          <Button onClick={() => handleDiscountTypeSelect('percentage')}>Discount %</Button>
          <Button onClick={() => handleDiscountTypeSelect('amount')}>Discount ₹</Button>
          <Button onClick={handleDiscountDialogClose}>Cancel</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={roundOffConfirmOpen} onClose={() => setRoundOffConfirmOpen(false)}>
        <DialogTitle>Confirm Round Off</DialogTitle>
        <DialogContent><Typography>Round off amount is {totalRoundOff.toFixed(2)}. Proceed with save?</Typography></DialogContent>
        <DialogActions>
          <Button onClick={() => setRoundOffConfirmOpen(false)}>Cancel</Button>
          <Button onClick={() => { setRoundOffConfirmOpen(false); if (submitData) handleFinalSubmit(submitData, watch, localComputedItems, isIntrastate, finalTotalAmount, totalRoundOff, lineDiscountEnabled, lineDiscountType, totalDiscountEnabled, totalDiscountType, createMutation, updateMutation, mode, handleGeneratePDF, refreshMasterData, config, additionalCharges); }} variant="contained">Confirm</Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={additionalChargesModalOpen}
        onClose={handleAdditionalChargesCancel}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Additional Charges</DialogTitle>
        <DialogContent>
          <AdditionalCharges
            charges={localAdditionalCharges}
            onChange={setLocalAdditionalCharges}
            mode="edit"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleAdditionalChargesCancel}>Cancel</Button>
          <Button onClick={handleAdditionalChargesConfirm} variant="contained">Confirm</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  if (isLoading || companyLoading) {
    return (
      <ProtectedPage moduleKey="procurement" action="write">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </ProtectedPage>
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
            voucherType="Purchase Returns"
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
      <AddVendorModal open={showAddVendorModal} onClose={() => setShowAddVendorModal(false)} onAdd={(newVendor) => { setValue("vendor_id", newVendor.id); refreshMasterData(); }} loading={addVendorLoading} setLoading={setAddVendorLoading} />
      <AddProductModal open={showAddProductModal} onClose={() => setShowAddProductModal(false)} onAdd={(newProduct) => { setValue(`items.${addingItemIndex}.product_id`, newProduct.id); setValue(`items.${addingItemIndex}.product_name`, newProduct.product_name); setValue(`items.${addingItemIndex}.unit_price`, newProduct.unit_price || 0); setValue(`items.${addingItemIndex}.original_unit_price`, newProduct.unit_price || 0); setValue(`items.${addingItemIndex}.gst_rate`, newProduct.gst_rate ?? 18); setValue(`items.${addingItemIndex}.cgst_rate`, isIntrastate ? (newProduct.gst_rate ?? 18) / 2 : 0); setValue(`items.${addingItemIndex}.sgst_rate`, isIntrastate ? (newProduct.gst_rate ?? 18) / 2 : 0); setValue(`items.${addingItemIndex}.igst_rate`, isIntrastate ? 0 : newProduct.gst_rate ?? 18); setValue(`items.${addingItemIndex}.unit`, newProduct.unit || ""); setValue(`items.${addingItemIndex}.reorder_level`, newProduct.reorder_level || 0); refreshMasterData(); }} loading={addProductLoading} setLoading={setAddProductLoading} />
      <AddShippingAddressModal open={showShippingModal} onClose={() => setShowShippingModal(false)} loading={addShippingLoading} setLoading={setAddShippingLoading} />
      <VoucherContextMenu contextMenu={contextMenu} voucher={null} voucherType="Purchase Return" onClose={handleCloseContextMenu} onView={handleViewWithData} onEdit={handleEditWithData} onDelete={handleDelete} onPrint={handleGeneratePDF} onDuplicate={(id) => handleDuplicate(id, voucherList, reset, setMode, "Purchase Return")} />
      <VoucherDateConflictModal
        open={showConflictModal}
        onClose={handleCancelConflict}
        conflictInfo={conflictInfo}
        onChangeDateToSuggested={handleChangeDateToSuggested}
        onProceedAnyway={handleProceedAnyway}
        voucherType="Purchase Return"
      />
    </>
  );
};
export default PurchaseReturnPage;