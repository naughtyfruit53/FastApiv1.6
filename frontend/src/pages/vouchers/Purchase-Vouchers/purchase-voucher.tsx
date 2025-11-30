// frontend/src/pages/vouchers/Purchase-Vouchers/purchase-voucher.tsx  

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
import AddVendorModal from "../../../components/AddVendorModal";  
import AddProductModal from "../../../components/AddProductModal";  
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';  
import VoucherContextMenu from "../../../components/VoucherContextMenu";  
import VoucherLayout from "../../../components/VoucherLayout";  
import VoucherHeaderActions from "../../../components/VoucherHeaderActions";  
import VoucherListModal from "../../../components/VoucherListModal";  
import VoucherItemTable from "../../../components/VoucherItemTable";  
import VoucherFormTotals from "../../../components/VoucherFormTotals";  
import AdditionalCharges, { AdditionalChargesData } from '../../../components/AdditionalCharges';  
import VoucherDateConflictModal from '../../../components/VoucherDateConflictModal';  
import api from "../../../lib/api";  
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
import { useWatch } from "react-hook-form";  
import { useEntityBalance, getBalanceDisplayText } from "../../../hooks/useEntityBalance";  
import Link from 'next/link';  
import { toast } from "react-toastify"; // Added for toast notifications  
import { useAuth } from '../../../context/AuthContext';  
  
import { ProtectedPage } from '../../../components/ProtectedPage';  
const PurchaseVoucherPage: React.FC = () => {  
  console.count('Render: PurchaseVoucherPage');  
  const { company, isLoading: companyLoading, error: companyError, refetch: refetchCompany } = useCompany();  
  const { isOrgContextReady } = useAuth();  
  const router = useRouter();  
  console.log('router.query:', router.query);  // Debug log for query params  
  const { productId, vendorId, from_grn_id } = router.query;  
  const config = getVoucherConfig("purchase-voucher");  
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
    
  const [selectedVendor, setSelectedVendor] = useState(null as any);  
  const [refetchLoading, setRefetchLoading] = useState(true);  // Local loading for refetch  
    
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
  
  // Force invalidate and refetch company data on mount to ensure fresh state_code  
  useEffect(() => {  
    const fetchFreshData = async () => {  
      setRefetchLoading(true);  
      try {  
        await refetchCompany();  
      } catch (error) {  
        console.error('Failed to refetch company data:', error);  
      } finally {  
        setRefetchLoading(false);  
      }  
    };  
    fetchFreshData();  
  }, [refetchCompany]);  
  
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
        .then(number => setValue("voucher_number", number))  
        .catch(err => console.error("Failed to fetch voucher number:", err));  
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
          unit: product.unit || " ",  
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
    console.log("Vendor list in purchase-voucher:", vendorList);  
  }, [vendorList]);  
  
  const handleVendorAdded = (newVendor: any) => {  
    if (!newVendor?.id) {  
      console.error("New vendor ID is missing:", newVendor);  
      return;  
    }  
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
  };  
  
  const handleVoucherClick = (voucher: any) => {  
    setMode("view");  
    reset({  
      ...voucher,  
      date: voucher.date ? voucher.date.split('T')[0] : '',  
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
      date: voucher.date ? voucher.date.split('T')[0] : '',  
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
    queryClient.setQueryData(['purchase-voucher', voucher.id], voucher);  
  };  
  
  const handleViewWithData = (voucher: any) => {  
    if (!voucher || !voucher.id) return;  
    handleView(voucher.id);  
    reset({  
      ...voucher,  
      date: voucher.date ? voucher.date.split('T')[0] : '',  
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
    queryClient.setQueryData(['purchase-voucher', voucher.id], voucher);  
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
      console.log("[PurchaseVoucherPage] Resetting form with voucherData:", formattedData);  
      reset(formattedData);  
      if (voucherData.additional_charges) {  
        setAdditionalCharges(voucherData.additional_charges);  
        setAdditionalChargesEnabled(Object.values(voucherData.additional_charges).some(v => v > 0));  
      } else {  
        setAdditionalCharges({ freight: 0, installation: 0, packing: 0, insurance: 0, loading: 0, unloading: 0, miscellaneous: 0 });  
        setAdditionalChargesEnabled(false);  
      }  
      // NEW: Set selectedVendor from voucherData.vendor if available  
      if (voucherData.vendor) {  
        setSelectedVendor(voucherData.vendor);  
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
          const response = await api.get(  
            `/purchase-vouchers/next-number`,  
            { params: { voucher_date: currentDate } }  
          );  
          setValue('voucher_number', response.data);  
            
          // Check for backdated conflicts  
          const conflictResponse = await api.get(  
            `/purchase-vouchers/check-backdated-conflict`,  
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
  
  const onSubmit = async (data: any) => {  
    console.log('data.grn_id:', data.grn_id);  // Specific log for grn_id  
    console.log('Submitting data:', JSON.stringify(data, null, 2));  // Debug log for submit data  
    data.grn_id = watch('grn_id') || Number(from_grn_id) || null;  // Ensure grn_id is set  
    console.log('Final data.grn_id:', data.grn_id);  // Verify  
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
    if (data.grn_id) {  
      queryClient.invalidateQueries(['goods-receipt-notes']);  
    }  
  };  
  
  const handleCancel = () => {  
    setMode("view");  
    if (voucherData) reset(voucherData);  
  };  
  
  // State for voucher date conflict detection  
  const [conflictInfo, setConflictInfo] = useState<any>(null);  
  const [showConflictModal, setShowConflictModal] = useState(false);  
  const [pendingDate, setPendingDate] = useState<string | null>(null);  
  
  // New state for PDF upload  
  const [pdfUploadLoading, setPdfUploadLoading] = useState(false);  
  const [pdfUploadError, setPdfUploadError] = useState<string | null>(null);  
  const [extractedData, setExtractedData] = useState<any>(null);  
  const [showCreateVendorConfirm, setShowCreateVendorConfirm] = useState(false);  
  
  const handleCreateGRN = (voucher: any) => {  
    router.push({  
      pathname: '/vouchers/Purchase-Vouchers/grn',  
      query: { po_id: voucher.id }  
    });  
  };  
  
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
  
  // New PDF upload handler  
  const handlePdfUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {  
    const file = event.target.files?.[0];  
    if (!file) return;  
  
    if (!file.name.toLowerCase().endsWith('.pdf')) {  
      setPdfUploadError('Only PDF files are allowed');  
      return;  
    }  
  
    setPdfUploadLoading(true);  
    setPdfUploadError(null);  
  
    try {  
      const formData = new FormData();  
      formData.append('file', file);  
  
      const response = await api.post('/pdf-extraction/extract/purchase_voucher', formData, {  
        headers: { 'Content-Type': 'multipart/form-data' }  
      });  
  
      const extracted = response.data.extracted_data;  
      setExtractedData(extracted);  
  
      // Check if vendor exists  
      const matchedVendor = vendorList?.find((v: any) =>   
        v.name.toLowerCase() === (extracted.vendor_name || '').toLowerCase()  
      );  
  
      if (matchedVendor) {  
        setValue('vendor_id', matchedVendor.id);  
        setSelectedVendor(matchedVendor);  
        toast.success('Extracted from PDF invoice', { position: "top-right" });  
      } else {  
        // Show confirmation to create new vendor  
        setShowCreateVendorConfirm(true);  
      }  
  
      // Map other extracted data to form fields  
      if (extracted.invoice_number) {  
        setValue('reference', extracted.invoice_number);  
      }  
  
      if (extracted.invoice_date) {  
        setValue('date', extracted.invoice_date);  
      }  
  
      if (extracted.payment_terms) {  
        setValue('payment_terms', extracted.payment_terms);  
      }  
  
      if (extracted.notes) {  
        setValue('notes', extracted.notes);  
      }  
  
      // Clear existing items  
      remove(fields.map((_, index) => index));  
  
      // Add extracted items - append even if no match, with product_name set  
      extracted.items?.forEach((item: any) => {  
        const matchedProduct = productList?.find((p: any) =>   
          p.product_name.toLowerCase() === (item.description || '').toLowerCase()  
        );  
  
        append({  
          product_id: matchedProduct?.id || null,  
          product_name: matchedProduct?.product_name || item.description || '',  
          quantity: item.quantity || 1,  
          unit_price: item.unit_price || matchedProduct?.unit_price || 0,  
          original_unit_price: matchedProduct?.unit_price || 0,  
          discount_percentage: 0,  
          discount_amount: 0,  
          gst_rate: matchedProduct?.gst_rate ?? 18,  
          cgst_rate: isIntrastate ? (matchedProduct?.gst_rate ?? 18) / 2 : 0,  
          sgst_rate: isIntrastate ? (matchedProduct?.gst_rate ?? 18) / 2 : 0,  
          igst_rate: isIntrastate ? 0 : (matchedProduct?.gst_rate ?? 18),  
          unit: matchedProduct?.unit || "",  
          current_stock: 0,  
          reorder_level: matchedProduct?.reorder_level || 0,  
          description: item.description || '',  
        });  
      });  
  
    } catch (error) {  
      console.error('PDF extraction failed:', error);  
      setPdfUploadError('Failed to extract data from PDF. Please try again.');  
    } finally {  
      setPdfUploadLoading(false);  
      event.target.value = ''; // Reset file input  
    }  
  };  
  
  // Handle confirmation for creating new vendor  
  const handleCreateVendorConfirm = () => {  
    setShowCreateVendorConfirm(false);  
    setShowAddVendorModal(true);  
  };  
  
  const handleCreateVendorCancel = () => {  
    setShowCreateVendorConfirm(false);  
    setPdfUploadError('Vendor not found. Please add manually.');  
  };  
  
  // New: Fetch voucher and pre-populate from GRN if from_grn_id is present  
  const { data: grnData } = useQuery({  
    queryKey: ['grn', from_grn_id],  
    queryFn: () => {  
      if (!from_grn_id) return null;  
      return voucherService.getGrnById(Number(from_grn_id));  
    },  
    enabled: !!from_grn_id && isOrgContextReady,  
  });  
  
  useEffect(() => {  
    console.log('from_grn_id:', from_grn_id);  // Debug log  
    if (grnData && mode === 'create') {  
      console.log('Pre-populating from GRN:', grnData);  
      setValue('vendor_id', grnData.vendor_id);  
      setValue('grn_id', Number(from_grn_id));  // Ensure grn_id is set  
      setValue('reference', `GRN {grnData.voucher_number}`);  
      setValue('date', new Date().toISOString().split('T')[0]);  
  
      // Clear existing items  
      remove(fields.map((_, index) => index));  
  
      // Append items from GRN with accepted quantities  
      grnData.items.forEach((item: any) => {  
        const product = productList?.find((p: any) => p.id === item.product_id) || {};  
        append({  
          product_id: item.product_id,  
          product_name: item.product_name || product.product_name || '',  
          quantity: item.accepted_quantity || 0,  
          unit_price: item.unit_price || product.unit_price || 0,  
          original_unit_price: product.unit_price || 0,  
          discount_percentage: 0,  
          discount_amount: 0,  
          gst_rate: normalizeGstRate(product.gst_rate ?? 18),  
          cgst_rate: isIntrastate ? normalizeGstRate(product.gst_rate ?? 18) / 2 : 0,  
          sgst_rate: isIntrastate ? normalizeGstRate(product.gst_rate ?? 18) / 2 : 0,  
          igst_rate: isIntrastate ? 0 : normalizeGstRate(product.gst_rate ?? 18),  
          unit: item.unit || product.unit || '',  
          current_stock: 0,  
          reorder_level: product.reorder_level || 0,  
          description: '',  
        });  
      });  
  
      toast.success('Pre-populated from GRN with accepted quantities');  
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
            <TableRow><TableCell colSpan={5} align="center">No purchase vouchers available</TableCell></TableRow>  
          ) : (  
            latestVouchers.slice(0, 7).map((voucher: any) => {  
              const dateStr = voucher.date ? voucher.date.split('T')[0] : '';  
              const displayDate = dateStr ? new Date(dateStr).toLocaleDateString('en-GB') : 'N/A';  
              return (  
                <TableRow   
                  key={voucher.id}   
                  hover   
                  onContextMenu={(e) => { e.preventDefault(); handleContextMenu(e, voucher); }}   
                  sx={{ cursor: "pointer" }}  
                >  
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }} onClick={() => handleViewWithData(voucher)}>{voucher.voucher_number}</TableCell>  
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{displayDate}</TableCell>  
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>{voucher.vendor?.name || vendorList?.find((v: any) => v.id === voucher.vendor_id)?.name || "N/A"}</TableCell>  
                  <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>₹{voucher.total_amount.toLocaleString()}</TableCell>  
                  <TableCell align="right" sx={{ fontSize: 12, p: 0 }}>  
                    <VoucherContextMenu  
                      voucher={voucher}  
                      voucherType="Purchase Voucher"  
                      onView={handleViewWithData}  
                      onEdit={handleEditWithData}  
                      onDelete={handleDelete}  
                      onPrint={handleGeneratePDF}  
                      onDuplicate={(id) => handleDuplicate(id, voucherList, reset, setMode, "Purchase Voucher")}  
                      onCreateGRN={handleCreateGRN}  
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
        voucherRoute="/vouchers/Purchase-Vouchers/purchase-voucher"  
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
      {!companyLoading && !company?.state_code && (  
        <Alert severity="warning" sx={{ mb: 2 }}>  
          Organization state code not set. Please set it in <Link href="/settings/company">Company Profile</Link> for accurate GST calculation.  
        </Alert>  
      )}  
      <form id="voucherForm" onSubmit={handleSubmit(onSubmit)} style={voucherFormStyles.formContainer}>  
        {/* Hidden field for grn_id */}  
        <input type="hidden" {...control.register("grn_id")} />  
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
          <Grid size={6}>  
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
                  helperText={errors.vendor_id ? "Required" : "" }   
                  sx={voucherFormStyles.field}   
                  InputLabelProps={{ shrink: true }}   
                />  
              }   
              disabled={mode === "view"}   
            />  
          </Grid>  
          <Grid size={2}>  
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
          <Grid size={8}>  
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
      <Dialog open={showCreateVendorConfirm} onClose={handleCreateVendorCancel}>  
        <DialogTitle>Vendor Not Found</DialogTitle>  
        <DialogContent>  
          <Typography>Vendor "{extractedData?.vendor_name}" not found. Would you like to create it?</Typography>  
        </DialogContent>  
        <DialogActions>  
          <Button onClick={handleCreateVendorCancel}>No</Button>  
          <Button onClick={handleCreateVendorConfirm} variant="contained">Yes</Button>  
        </DialogActions>  
      </Dialog>  
    </Box>  
  );  
  
  if (isLoading || companyLoading || refetchLoading) {  
    return (  
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">  
        <CircularProgress />  
      </Box>  
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
    <ProtectedPage moduleKey="vouchers" action="create">  
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
          voucherType="Purchase Voucher"   
          onView={handleViewWithData}   
          onEdit={handleEditWithData}   
          onDelete={handleDelete}   
          onPrint={handleGeneratePDF}   
          onDuplicate={(id) => handleDuplicate(id, voucherList, reset, setMode, "Purchase Voucher")}  
          onCreateGRN={handleCreateGRN}  
          onClose={() => {}}  
        />  
        <VoucherDateConflictModal  
          open={showConflictModal}  
          onClose={handleCancelConflict}  
          conflictInfo={conflictInfo}  
          onChangeDateToSuggested={handleChangeDateToSuggested}  
          onProceedAnyway={handleProceedAnyway}  
          voucherType="Purchase Voucher"  
        />  
      </>  
    </ProtectedPage>  
  );  
};  
  
const normalizeGstRate = (rate: number): number => {  
  return rate > 1 ? rate : rate * 100;  
};  
  
export default PurchaseVoucherPage;  
