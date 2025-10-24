// frontend/src/pages/vouchers/Purchase-Vouchers/purchase-order.tsx

import React, { useMemo, useState, useEffect, useRef } from "react";
import {
  Box,
  TextField,
  Typography,
  Grid,
  CircularProgress,
  Container,
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
  Autocomplete,
} from "@mui/material";
import { toast } from "react-toastify";
import AddVendorModal from "../../../components/AddVendorModal";
import AddProductModal from "../../../components/AddProductModal";
import AddShippingAddressModal from "../../../components/AddShippingAddressModal";
import VoucherContextMenu from "../../../components/VoucherContextMenu";
import TrackingDetailsDialog from "../../../components/DispatchManagement/TrackingDetailsDialog";
import VoucherLayout from "../../../components/VoucherLayout";
import VoucherHeaderActions from "../../../components/VoucherHeaderActions";
import VoucherListModal from "../../../components/VoucherListModal";
import VoucherItemTable from "../../../components/VoucherItemTable";
import VoucherFormTotals from "../../../components/VoucherFormTotals";
import AdditionalCharges, { AdditionalChargesData } from '../../../components/AdditionalCharges';
import { useVoucherPage } from "../../../hooks/useVoucherPage";
import { getVoucherConfig, getVoucherStyles, calculateVoucherTotals } from "../../../utils/voucherUtils";
import { getStock } from "../../../services/masterService";
import { voucherService } from "../../../services/vouchersService";
import api from "../../../lib/api";
import { useCompany } from "../../../context/CompanyContext";
import { useRouter } from "next/router";
import { useGstValidation } from "../../../hooks/useGstValidation";
import { useVoucherDiscounts } from "../../../hooks/useVoucherDiscounts";
import { handleFinalSubmit, handleDuplicate, getStockColor } from "../../../utils/voucherHandlers";
import voucherFormStyles from "../../../styles/voucherFormStyles";
import { useQueryClient } from "@tanstack/react-query";
import { useWatch } from "react-hook-form";
import { useEntityBalance, getBalanceDisplayText } from "../../../hooks/useEntityBalance";
import { formatCurrency } from "../../../utils/currencyUtils";

const PurchaseOrderPage: React.FC = () => {
  console.count('Render: PurchaseOrderPage');
  const { company, isLoading: companyLoading, error: companyError } = useCompany();
  const router = useRouter();
  const { productId, vendorId } = router.query;
  const config = getVoucherConfig("purchase-order");
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
  } = useVoucherPage(config);

  const [showVoucherListModal, setShowVoucherListModal] = useState(false);
  const [submitData, setSubmitData] = useState<any>(null);
  const [roundOffConfirmOpen, setRoundOffConfirmOpen] = useState(false);
  const [stockLoading, setStockLoading] = useState<{ [key: number]: boolean }>({});
  const selectedVendorId = watch("vendor_id");
  
  const [selectedVendor, setSelectedVendor] = useState(null as any);
  
  useEffect(() => {
    if (selectedVendorId && vendorList) {
      const foundVendor = vendorList.find((v: any) => v.id === selectedVendorId);
      if (foundVendor && foundVendor.id !== selectedVendor?.id) {
        setSelectedVendor(foundVendor);
      }
    } else if (!selectedVendorId) {
      setSelectedVendor(null);
    }
  }, [selectedVendorId, vendorList]);
  
  const { balance: vendorBalance, loading: vendorBalanceLoading } = useEntityBalance('vendor', selectedVendorId);

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

  const enhancedVendorOptions = useMemo(() => {
    const sortedVendors = [...(vendorList || [])].sort((a, b) => 
      (a.name || '').localeCompare(b.name || '')
    );
    return [
      { id: null, name: 'Add New Vendor...' },
      ...sortedVendors
    ];
  }, [vendorList]);

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

  const items = useWatch({ control, name: "items" }) || [];
  const totalDiscountValue = useWatch({ control, name: "total_discount" }) || 0;

  const totalsWithAdditionalCharges = useMemo(() => {
    console.log('Calculating totals with items:', items);
    return calculateVoucherTotals(
      items,
      isIntrastate,
      lineDiscountEnabled ? lineDiscountType : null,
      totalDiscountEnabled ? totalDiscountType : null,
      totalDiscountValue,
      additionalCharges
    );
  }, [items, isIntrastate, lineDiscountEnabled, lineDiscountType, totalDiscountEnabled, totalDiscountType, totalDiscountValue, additionalCharges]);

  const localComputedItems = totalsWithAdditionalCharges.computedItems;
  const finalTotalAmount = totalsWithAdditionalCharges.totalAmount;
  const finalTotalAdditionalCharges = totalsWithAdditionalCharges.totalAdditionalCharges;

  useEffect(() => {
    processedRef.current = new Set();
  }, [fields.length]);

  useEffect(() => {
    productIds.forEach((productId: number, index: number) => {
      if (productId && !processedRef.current.has(index) && !stockLoading[index]) {
        const currentStock = watch(`items.${index}.current_stock`);
        if (currentStock === 0 || currentStock === undefined) {
          setStockLoading(prev => ({ ...prev, [index]: true }));
          getStock({ queryKey: ["", { product_id: productId, organization_id: company?.organization_id }] })
            .then(res => {
              console.log("Stock fetch response for product", productId, ":", res);
              const stockData = res[0] || { quantity: 0 };
              setValue(`items.${index}.current_stock`, parseFloat(stockData.quantity || 0));
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
  }, [productIds, fields.length, setValue, watch, company?.organization_id]);

  useEffect(() => {
    if (mode === "create" && !nextVoucherNumber && !isLoading) {
      voucherService.getNextVoucherNumber(config.nextNumberEndpoint)
        .then((number) => setValue("voucher_number", number))
        .catch((err) => console.error("Failed to fetch voucher number:", err));
    }
  }, [mode, nextVoucherNumber, isLoading, setValue, config.nextNumberEndpoint]);

  useEffect(() => {
    if (mode === "create" && productId && productList) {
      const product = productList.find((p) => p.id === Number(productId));
      if (product) {
        const gst_rate = normalizeGstRate(product.gst_rate ?? 18);
        if (fields.length === 1 && !watch(`items.0.product_id`)) {
          remove(0);
        }
        append({
          product_id: product.id,
          product_name: product.product_name || product.name,
          quantity: 0.0,
          unit_price: parseFloat(product.unit_price || 0),
          original_unit_price: parseFloat(product.unit_price || 0),
          discount_percentage: 0,
          discount_amount: 0,
          gst_rate: gst_rate,
          cgst_rate: isIntrastate ? gst_rate / 2 : 0,
          sgst_rate: isIntrastate ? gst_rate / 2 : 0,
          igst_rate: isIntrastate ? 0 : gst_rate,
          amount: 0,
          unit: product.unit,
          current_stock: 0,
          reorder_level: parseFloat(product.reorder_level || 0),
          description: '',
        });
      }
    }
  }, [mode, productId, productList, append, isIntrastate, fields.length, watch, remove]);

  useEffect(() => {
    if (mode === "create" && vendorId && vendorList && !watch("vendor_id")) {
      const vendor = vendorList.find((v) => v.id === Number(vendorId));
      if (vendor) {
        setValue("vendor_id", vendor.id);
        setSelectedVendor(vendor);
        console.log("Set initial vendor from query:", vendor.id);
      }
    }
  }, [mode, vendorId, vendorList, setValue, watch]);

  useEffect(() => {
    console.log("Vendor list in purchase-order:", vendorList);
  }, [vendorList]);

  const handleVendorAdded = (newVendor: any) => {
    if (newVendor?.id) {
      setValue("vendor_id", newVendor.id);
      setSelectedVendor(newVendor);
      console.log("Vendor added, updating vendor_id:", newVendor.id);
      queryClient.setQueryData(["vendors", "", company?.organization_id], (old: any[]) => {
        const updatedList = old ? [...old, newVendor] : [newVendor];
        console.log("Updated vendor list:", updatedList);
        return updatedList;
      });
      queryClient.invalidateQueries(["vendors"]);
      setShowAddVendorModal(false);
      refreshMasterData();
    } else {
      console.error("New vendor ID is missing:", newVendor);
    }
  };

  const handleVoucherClick = (voucher: any) => {
    setMode("view");
    reset({
      ...voucher,
      date: voucher.date ? voucher.date.split('T')[0] : '',
      items: voucher.items.map((item: any) => ({
        ...item,
        cgst_rate: isIntrastate ? (item.gst_rate || 18) / 2 : 0,
        sgst_rate: isIntrastate ? (item.gst_rate || 18) / 2 : 0,
        igst_rate: isIntrastate ? 0 : (item.gst_rate || 18),
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
      date: voucher.date ? voucher.date.split('T')[0] : '',
      items: voucher.items.map((item: any) => ({
        ...item,
        cgst_rate: isIntrastate ? (item.gst_rate || 18) / 2 : 0,
        sgst_rate: isIntrastate ? (item.gst_rate || 18) / 2 : 0,
        igst_rate: isIntrastate ? 0 : (item.gst_rate || 18),
      })),
    });
    if (voucher.additional_charges) {
      setAdditionalCharges(voucher.additional_charges);
      setAdditionalChargesEnabled(Object.values(voucher.additional_charges).some(v => v > 0));
    } else {
      setAdditionalCharges({ freight: 0, installation: 0, packing: 0, insurance: 0, loading: 0, unloading: 0, miscellaneous: 0 });
      setAdditionalChargesEnabled(false);
    }
    queryClient.setQueryData(['purchase-order', voucher.id], voucher);
  };

  const handleViewWithData = (voucher: any) => {
    if (!voucher || !voucher.id) return;
    handleView(voucher.id);
    reset({
      ...voucher,
      date: voucher.date ? voucher.date.split('T')[0] : '',
      items: voucher.items.map((item: any) => ({
        ...item,
        cgst_rate: isIntrastate ? (item.gst_rate || 18) / 2 : 0,
        sgst_rate: isIntrastate ? (item.gst_rate || 18) / 2 : 0,
        igst_rate: isIntrastate ? 0 : (item.gst_rate || 18),
      })),
    });
    if (voucher.additional_charges) {
      setAdditionalCharges(voucher.additional_charges);
      setAdditionalChargesEnabled(Object.values(voucher.additional_charges).some(v => v > 0));
    } else {
      setAdditionalCharges({ freight: 0, installation: 0, packing: 0, insurance: 0, loading: 0, unloading: 0, miscellaneous: 0 });
      setAdditionalChargesEnabled(false);
    }
    queryClient.setQueryData(['purchase-order', voucher.id], voucher);
  };

  useEffect(() => {
    if (voucherData && (mode === "view" || mode === "edit")) {
      const formattedDate = voucherData.date ? voucherData.date.split('T')[0] : '';
      const formattedData = {
        ...voucherData,
        date: formattedDate,
        items: voucherData.items?.map((item: any) => ({
          ...item,
          product_id: item.product_id,
          product_name: item.product?.product_name || item.product_name || "",
          unit_price: parseFloat(item.unit_price || 0),
          original_unit_price: parseFloat(item.product?.unit_price || item.unit_price || 0),
          discount_percentage: parseFloat(item.discount_percentage || 0),
          discount_amount: parseFloat(item.discount_amount || 0),
          gst_rate: normalizeGstRate(item.gst_rate ?? 18),
          cgst_rate: isIntrastate ? normalizeGstRate(item.gst_rate ?? 18) / 2 : 0,
          sgst_rate: isIntrastate ? normalizeGstRate(item.gst_rate ?? 18) / 2 : 0,
          igst_rate: isIntrastate ? 0 : normalizeGstRate(item.gst_rate ?? 18),
          unit: item.unit || item.product?.unit || "",
          current_stock: parseFloat(item.current_stock || 0),
          reorder_level: parseFloat(item.reorder_level || 0),
          description: item.description || '',
          quantity: parseFloat(item.quantity || 0),
        })) || [],
      };
      console.log("[PurchaseOrderPage] Resetting form with voucherData:", formattedData);
      reset(formattedData);
      if (voucherData.additional_charges) {
        setAdditionalCharges(voucherData.additional_charges);
        setAdditionalChargesEnabled(Object.values(voucherData.additional_charges).some(v => v > 0));
      } else {
        setAdditionalCharges({ freight: 0, installation: 0, packing: 0, insurance: 0, loading: 0, unloading: 0, miscellaneous: 0 });
        setAdditionalChargesEnabled(false);
      }
    }
  }, [voucherData, mode, reset, setValue, isIntrastate]);

  // Fetch voucher number when date changes and check for conflicts
  useEffect(() => {
    const fetchVoucherNumber = async () => {
      const currentDate = watch('date');
      if (currentDate && mode === 'create') {
        try {
          // Fetch new voucher number based on date
          const response = await axios.get(
            `/api/v1/purchase-orders/next-number?voucher_date=${currentDate}`
          );
          setValue('voucher_number', response.data);
          
          // Check for backdated conflicts
          const conflictResponse = await axios.get(
            `/api/v1/purchase-orders/check-backdated-conflict?voucher_date=${currentDate}`
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

  const onSubmit = async (data: any) => {
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

  const [trackingDialogOpen, setTrackingDialogOpen] = useState(false);
  const [selectedVoucherForTracking, setSelectedVoucherForTracking] = useState<any>(null);
  
  // State for voucher date conflict detection
  const [conflictInfo, setConflictInfo] = useState<any>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);
  const [pendingDate, setPendingDate] = useState<string | null>(null);

  const handleEditTracking = (voucher: any) => {
    console.log('[PurchaseOrderPage] Opening tracking for PO:', voucher.id);
    setSelectedVoucherForTracking({ id: voucher.id, voucher_number: voucher.voucher_number });
    setTrackingDialogOpen(true);
  };

  const handleTrackingDialogClose = () => {
    setTrackingDialogOpen(false);
    setSelectedVoucherForTracking(null);
    refreshMasterData();
  };

  const handleCreateGRN = (voucher: any) => {
    router.push({
      pathname: '/vouchers/Purchase-Vouchers/grn',
      query: { po_id: voucher.id }
    });
  };

  const getPOColorStatus = (voucher: any) => {
    const grnStatus = voucher.grn_status || 'pending';
    const totalOrdered = voucher.items.reduce((sum: number, item: any) => sum + (item.quantity || 0), 0);
    const totalReceived = voucher.items.reduce((sum: number, item: any) => sum + ((item.quantity - item.pending_quantity) || 0), 0);
    const remaining = totalOrdered - totalReceived;
    
    console.log(`PO ${voucher.voucher_number} grn_status: ${grnStatus}, `
                + `ordered: ${totalOrdered}, received: ${totalReceived}, remaining: ${remaining}, `
                + `items:`, voucher.items.map((item: any) => ({
                  product_id: item.product_id,
                  quantity: item.quantity,
                  delivered_quantity: item.delivered_quantity,
                  pending_quantity: item.pending_quantity
                })));
    
    if (grnStatus === 'complete') {
      return 'green';
    } else if (grnStatus === 'partial') {
      return 'yellow';
    } else {
      return 'white';
    }
  };

  const getColorCode = (status: string) => {
    switch (status) {
      case 'green':
        return '#4caf50';
      case 'yellow':
        return '#ff9800';
      case 'white':
        return '#ffffff';
      default:
        return '#ffffff';
    }
  };

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
            <TableRow><TableCell colSpan={5} align="center">No purchase orders available</TableCell></TableRow>
          ) : (
            latestVouchers.slice(0, 7).map((voucher: any) => {
              const colorStatus = getPOColorStatus(voucher);
              const colorCode = getColorCode(colorStatus);
              const dateStr = voucher.date ? voucher.date.split('T')[0] : '';
              const displayDate = dateStr ? new Date(dateStr).toLocaleDateString('en-GB') : 'N/A';
              return (
                <TableRow 
                  key={voucher.id} 
                  hover 
                  onContextMenu={(e) => { e.preventDefault(); handleContextMenu(e, voucher); }} 
                  sx={{ 
                    cursor: "pointer",
                    backgroundColor: colorCode
                  }}
                >
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }} onClick={() => handleViewWithData(voucher)}>{voucher.voucher_number}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{displayDate}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{vendorList?.find((v: any) => v.id === voucher.vendor_id)?.name || "N/A"}</TableCell>
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{formatCurrency(Math.round(voucher.total_amount) || 0)}</TableCell>
                  <TableCell align="right" sx={{ fontSize: 12, p: 0 }}>
                    <VoucherContextMenu
                      voucher={voucher}
                      voucherType="Purchase Order"
                      onView={handleViewWithData}
                      onEdit={handleEditWithData}
                      onDelete={handleDelete}
                      onPrint={handleGeneratePDF}
                      onDuplicate={(id) => handleDuplicate(id, voucherList, reset, setMode, "Purchase Order")}
                      onCreateGRN={handleCreateGRN}
                      onEditTracking={handleEditTracking}
                      showKebab={true}
                      onClose={() => {}}
                    />
                  </TableCell>
                </TableRow>
              );
            })
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
        voucherRoute="/vouchers/Purchase-Vouchers/purchase-order"
        currentId={mode !== "create" ? voucherData?.id : null}
        onEdit={() => voucherData && voucherData.id && handleEditWithData(voucherData)}
        onCreate={handleCreate}
        onCancel={handleCancel}
      />
    </Box>
  );

  const formBody = (
    <Box>
      {gstError && <Alert severity="error" sx={{ mb: 2 }}>{gstError}</Alert>}
      <form id="voucherForm" onSubmit={handleSubmit(onSubmit)} style={voucherFormStyles.formContainer}>
        <Grid container spacing={1}>
          <Grid size={4}>
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
          <Grid size={4}>
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
            <TextField 
              fullWidth 
              label="Required by Date" 
              type="date" 
              {...control.register("required_by_date")} 
              disabled={mode === "view"} 
              sx={{ 
                ...voucherFormStyles.field, 
                '& .MuiInputBase-input': { textAlign: 'center' } 
              }} 
              InputLabelProps={{ shrink: true }} 
            />
          </Grid>
          <Grid size={4}>
            <TextField 
              fullWidth 
              label="Reference" 
              {...control.register("reference")} 
              disabled={mode === "view"} 
              sx={voucherFormStyles.field} 
              InputLabelProps={{ shrink: true }} 
            />
          </Grid>
          <Grid size={3}>
            <Autocomplete 
              key={selectedVendorId || 'vendor-autocomplete'} 
              size="small" 
              options={enhancedVendorOptions} 
              getOptionLabel={(option: any) => {
                if (typeof option === 'number') return '';
                return option?.name || "";
              }} 
              value={selectedVendor || (vendorList?.find((v: any) => v.id === selectedVendorId) || null)} 
              onChange={(_, newValue) => { 
                if (newValue?.id === null) setShowAddVendorModal(true); 
                else {
                  setValue("vendor_id", newValue?.id || null); 
                  setSelectedVendor(newValue);
                } 
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
              computedItems={localComputedItems}
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
              showDeliveryStatus={mode === "view" || mode === "edit"}
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
              additionalCharges={additionalCharges}
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
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (companyError) {
    return (
      <Container>
        <Alert severity="error" sx={{ mt: 2 }}>
          Error loading company details: {companyError.message}. Please try refreshing or contact support.
        </Alert>
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
        formContent={formBody}
        onShowAll={() => setShowVoucherListModal(true)}
        centerAligned={true}
        modalContent={
          <VoucherListModal
            open={showVoucherListModal}
            onClose={() => setShowVoucherListModal(false)}
            voucherType="Purchase Orders"
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
      <AddVendorModal 
        open={showAddVendorModal} 
        onClose={() => setShowAddVendorModal(false)} 
        onSave={handleVendorAdded} 
        loading={addVendorLoading} 
        setLoading={setAddVendorLoading} 
        organization_id={company?.organization_id}
      />
      <AddProductModal 
        open={showAddProductModal} 
        onClose={() => setShowAddProductModal(false)} 
        onAdd={(newProduct) => { 
          setValue(`items.${addingItemIndex}.product_id`, newProduct.id); 
          setValue(`items.${addingItemIndex}.product_name`, newProduct.product_name); 
          setValue(`items.${addingItemIndex}.unit_price`, parseFloat(newProduct.unit_price || 0)); 
          setValue(`items.${addingItemIndex}.original_unit_price`, parseFloat(newProduct.unit_price || 0)); 
          setValue(`items.${addingItemIndex}.gst_rate`, normalizeGstRate(newProduct.gst_rate ?? 18)); 
          setValue(`items.${addingItemIndex}.cgst_rate`, isIntrastate ? normalizeGstRate(newProduct.gst_rate ?? 18) / 2 : 0); 
          setValue(`items.${addingItemIndex}.sgst_rate`, isIntrastate ? normalizeGstRate(newProduct.gst_rate ?? 18) / 2 : 0); 
          setValue(`items.${addingItemIndex}.igst_rate`, isIntrastate ? 0 : normalizeGstRate(newProduct.gst_rate ?? 18)); 
          setValue(`items.${addingItemIndex}.unit`, newProduct.unit || ""); 
          setValue(`items.${addingItemIndex}.reorder_level`, parseFloat(newProduct.reorder_level || 0)); 
          refreshMasterData(); 
        }} 
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
        voucher={null} 
        voucherType="Purchase Order" 
        onView={handleViewWithData} 
        onEdit={handleEditWithData} 
        onDelete={handleDelete} 
        onPrint={handleGeneratePDF} 
        onDuplicate={(id) => handleDuplicate(id, voucherList, reset, setMode, "Purchase Order")}
        onCreateGRN={handleCreateGRN}
        onEditTracking={handleEditTracking}
        onClose={() => {}}
      />
      {selectedVoucherForTracking && (
        <TrackingDetailsDialog
          open={trackingDialogOpen}
          onClose={handleTrackingDialogClose}
          voucherId={selectedVoucherForTracking.id}
          voucherNumber={selectedVoucherForTracking.voucher_number}
        />
      )}
    </>
  );
};

const normalizeGstRate = (rate: number): number => {
  return rate > 1 ? rate : rate * 100;
};

export default PurchaseOrderPage;