// frontend/src/pages/vouchers/Purchase-Vouchers/purchase-order.tsx
import React, { useMemo, useState, useEffect } from "react";
import {
  Box,
  TextField,
  Typography,
  Grid,
  IconButton,
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
  InputAdornment,
  Fab,
  Alert,
  Button,
  Checkbox,
  FormControlLabel,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TableFooter,
} from "@mui/material";
import { Add, Remove, Clear } from "@mui/icons-material";
import AddVendorModal from "../../../components/AddVendorModal";
import AddProductModal from "../../../components/AddProductModal";
import AddShippingAddressModal from "../../../components/AddShippingAddressModal";
import VoucherContextMenu from "../../../components/VoucherContextMenu";
import VoucherLayout from "../../../components/VoucherLayout";
import VoucherHeaderActions from "../../../components/VoucherHeaderActions";
import VoucherListModal from "../../../components/VoucherListModal";
import ProductAutocomplete from "../../../components/ProductAutocomplete";
import { useVoucherPage } from "../../../hooks/useVoucherPage";
import {
  getVoucherConfig,
  GST_SLABS,
  getVoucherStyles,
} from "../../../utils/voucherUtils";
import { getStock } from "../../../services/masterService";
import { voucherService } from "../../../services/vouchersService";
import api from "../../../lib/api";
import { useCompany } from "../../../context/CompanyContext";
import { useRouter } from "next/router";
import { toast } from "react-toastify";

const PurchaseOrderPage: React.FC = () => {
  const { company, isLoading: companyLoading, error: companyError } = useCompany();
  const router = useRouter();
  const { productId, vendorId } = router.query;
  const config = getVoucherConfig("purchase-order");
  const voucherStyles = getVoucherStyles();
  const [gstError, setGstError] = useState<string | null>(null);
  const [roundOffConfirmOpen, setRoundOffConfirmOpen] = useState(false);
  const [submitData, setSubmitData] = useState<any>(null);
  const [descriptionEnabled, setDescriptionEnabled] = useState(false);

  // Derive company state code with fallback to gst_number prefix
  const companyState = useMemo(() => {
    if (company?.state_code) {
      console.log("[PurchaseOrderPage] Company state_code:", company.state_code);
      return company.state_code;
    }
    if (company?.gst_number) {
      const gstPrefix = company.gst_number.slice(0, 2);
      console.log("[PurchaseOrderPage] Using GST prefix as state_code:", gstPrefix);
      return gstPrefix;
    }
    console.warn("[PurchaseOrderPage] No state_code or gst_number found in company:", company);
    return null;
  }, [company]);

  // Log company object and query state for debugging
  useEffect(() => {
    console.log("[PurchaseOrderPage] Company context:", {
      company,
      companyLoading,
      companyError,
      companyState,
      timestamp: new Date().toISOString(),
    });
  }, [company, companyLoading, companyError, companyState]);

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
    handleSubmitForm,
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
    lineDiscountEnabled,
    lineDiscountType,
    totalDiscountEnabled,
    totalDiscountType,
    handleToggleLineDiscount,
    handleToggleTotalDiscount,
    discountDialogOpen,
    handleDiscountDialogClose,
    handleDiscountTypeSelect,
    discountDialogFor,
    totalRoundOff,
  } = useVoucherPage(config);

  const [showVoucherListModal, setShowVoucherListModal] = useState(false);
  const selectedVendorId = watch("vendor_id");
  const selectedVendor = vendorList?.find((v: any) => v.id === selectedVendorId);

  // Validate state codes for GST calculation after company data is loaded
  useEffect(() => {
    if (companyLoading) {
      console.log("[PurchaseOrderPage] Company data still loading, skipping GST validation");
      return;
    }
    if (selectedVendorId && !selectedVendor?.state_code && !selectedVendor?.gst_number) {
      setGstError("Vendor state code or GST number is missing. Please update vendor details.");
    } else if (!companyState) {
      setGstError("Company state code or GST number is missing. Please update company details in settings.");
    } else {
      setGstError(null);
    }
    console.log("[PurchaseOrderPage] GST Validation:", {
      selectedVendor,
      companyState,
      selectedVendorId,
      vendorStateCode: selectedVendor?.state_code || selectedVendor?.gst_number?.slice(0, 2),
      timestamp: new Date().toISOString(),
    });
  }, [selectedVendorId, selectedVendor, companyState, companyLoading]);

  const enhancedVendorOptions = [
    ...(vendorList || []),
    { id: null, name: "Add New Vendor..." },
  ];

  const [stockLoading, setStockLoading] = useState<{ [key: number]: boolean }>({});

  const handleToggleDescription = (checked: boolean) => {
    setDescriptionEnabled(checked);
    if (!checked) {
      fields.forEach((_, index) => {
        setValue(`items.${index}.description`, '');
      });
    }
  };

  const handleAddItem = () => {
    append({
      product_id: null,
      product_name: "",
      quantity: 1,
      unit_price: 0,
      original_unit_price: 0,
      discount_percentage: 0,
      discount_amount: 0,
      gst_rate: 18,
      cgst_rate: isIntrastate ? 9 : 0,
      sgst_rate: isIntrastate ? 9 : 0,
      igst_rate: isIntrastate ? 0 : 18,
      amount: 0,
      unit: "",
      current_stock: 0,
      reorder_level: 0,
      description: '',
    });
  };

  const handleCancel = () => {
    setMode("view");
    if (voucherData) {
      reset(voucherData);
    }
  };

  const onSubmit = (data: any) => {
    if (totalRoundOff !== 0) {
      setSubmitData(data);
      setRoundOffConfirmOpen(true);
      return;
    }
    handleFinalSubmit(data);
  };

  const handleFinalSubmit = async (data: any) => {
    if (!data.vendor_id) {
      toast.error("Please select a vendor");
      return;
    }

    const validItems = data.items.filter(
      (item: any) => item.product_id && item.quantity > 0
    );

    if (validItems.length === 0) {
      toast.error("Please add at least one valid product with quantity");
      return;
    }

    data.items = validItems;

    try {
      if (config.hasItems !== false) {
        data.line_discount_type = lineDiscountEnabled ? lineDiscountType : null;
        data.total_discount_type = totalDiscountEnabled ? totalDiscountType : null;
        data.total_discount = watch('total_discount') || 0;
        data.items = computedItems.map((item: any) => ({
          ...item,
          cgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
          sgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
          igst_rate: isIntrastate ? 0 : item.gst_rate,
        }));
        data.total_amount = totalAmount;
        data.is_intrastate = isIntrastate;
        data.round_off = totalRoundOff;
      }
      const itemsToUpdate = data.items.filter(
        (item: any) =>
          item.unit_price !== item.original_unit_price && item.product_id,
      );
      if (itemsToUpdate.length > 0) {
        if (
          confirm(
            `Some items have updated prices. Update master product prices for ${itemsToUpdate.length} items?`,
          )
        ) {
          await Promise.all(
            itemsToUpdate.map((item: any) =>
              api.put(`/products/${item.product_id}`, {
                unit_price: item.unit_price,
              }),
            ),
          );
          refreshMasterData();
        }
      }
      data.items = data.items.map(
        ({ original_unit_price, ...item }: any) => item,
      );
      let response;
      if (mode === "create") {
        response = await createMutation.mutateAsync(data);
        if (confirm("Voucher created successfully. Generate PDF?")) {
          handleGeneratePDF(response);
        }
      } else if (mode === "edit") {
        response = await updateMutation.mutateAsync(data);
        if (confirm("Voucher updated successfully. Generate PDF?")) {
          handleGeneratePDF(response);
        }
      }
    } catch (err) {
      console.error("Error saving purchase order:", err);
      toast.error("Failed to save purchase order. Please try again.");
    }
  };

  const handleDuplicate = async (id: number) => {
    try {
      const voucher = voucherList?.find((v) => v.id === id);
      if (!voucher) {
        return;
      }
      reset({
        ...voucher,
        voucher_number: "",
        date: new Date().toISOString().split("T")[0],
        created_at: undefined,
        updated_at: undefined,
        id: undefined,
      });
      setMode("create");
      toast.success("Purchase order duplicated successfully");
    } catch (err) {
      console.error("Error duplicating purchase order:", err);
      toast.error("Failed to duplicate purchase order");
    }
  };

  const getStockColor = (stock: number, reorder: number) => {
    if (stock === 0) {
      return "error.main";
    }
    if (stock <= reorder) {
      return "warning.main";
    }
    return "success.main";
  };

  const selectedProducts = useMemo(() => {
    return fields.map((_, index) => {
      const productId = watch(`items.${index}.product_id`);
      return productList?.find((p: any) => p.id === productId) || null;
    });
  }, [
    fields.length,
    productList,
    ...fields.map((_, index) => watch(`items.${index}.product_id`)),
  ]);

  useEffect(() => {
    fields.forEach((_, index) => {
      const productId = watch(`items.${index}.product_id`);
      if (productId) {
        setStockLoading((prev) => ({ ...prev, [index]: true }));
        getStock({ queryKey: ["", { product_id: productId }] })
          .then((res) => {
            const stockData = res[0] || { quantity: 0 };
            setValue(`items.${index}.current_stock`, stockData.quantity);
            setStockLoading((prev) => ({ ...prev, [index]: false }));
          })
          .catch((err) => {
            console.error("Failed to fetch stock:", err);
            setStockLoading((prev) => ({ ...prev, [index]: false }));
          });
      } else {
        setValue(`items.${index}.current_stock`, 0);
        setStockLoading((prev) => ({ ...prev, [index]: false }));
      }
    });
  }, [
    fields.map((f) => watch(`items.${fields.indexOf(f)}.product_id`)).join(","),
    setValue,
    fields.length,
  ]);

  useEffect(() => {
    if (mode === "create" && !nextVoucherNumber && !isLoading) {
      voucherService
        .getNextVoucherNumber(config.nextNumberEndpoint)
        .then((number) => setValue("voucher_number", number))
        .catch((err) => console.error("Failed to fetch voucher number:", err));
    }
  }, [mode, nextVoucherNumber, isLoading, setValue, config.nextNumberEndpoint]);

  useEffect(() => {
    if (mode === "create" && productId && productList) {
      const product = productList.find((p) => p.id === Number(productId));
      if (product) {
        append({
          product_id: product.id,
          product_name: product.product_name || product.name,
          quantity: 1,
          unit_price: product.unit_price || 0,
          original_unit_price: product.unit_price || 0,
          discount_percentage: 0,
          discount_amount: 0,
          gst_rate: product.gst_rate ?? 18,
          cgst_rate: isIntrastate ? (product.gst_rate ?? 18) / 2 : 0,
          sgst_rate: isIntrastate ? (product.gst_rate ?? 18) / 2 : 0,
          igst_rate: isIntrastate ? 0 : product.gst_rate ?? 18,
          amount: 0,
          unit: product.unit,
          current_stock: 0,
          reorder_level: product.reorder_level || 0,
          description: '',
        });
      }
    }
  }, [mode, productId, productList, append, isIntrastate]);

  useEffect(() => {
    if (mode === "create" && vendorId && vendorList) {
      const vendor = vendorList.find((v) => v.id === Number(vendorId));
      if (vendor) {
        setValue("vendor_id", vendor.id);
      }
    }
  }, [mode, vendorId, vendorList, setValue]);

  const handleVoucherClick = async (voucher: any) => {
    try {
      const response = await api.get(`/purchase-orders/${voucher.id}`);
      const fullVoucherData = response.data;
      setMode("view");
      reset(fullVoucherData);
    } catch (err) {
      console.error("Error fetching voucher:", err);
      setMode("view");
      reset(voucher);
    }
  };

  const handleEditWithData = async (voucher: any) => {
    if (!voucher || !voucher.id) {
      return;
    }
    try {
      const response = await api.get(`/purchase-orders/${voucher.id}`);
      let fullVoucherData = response.data;
      fullVoucherData.date = fullVoucherData.date ? new Date(fullVoucherData.date).toISOString().split('T')[0] : '';
      setMode("edit");
      reset({
        ...fullVoucherData,
        items: fullVoucherData.items.map((item: any) => ({
          ...item,
          cgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
          sgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
          igst_rate: isIntrastate ? 0 : item.gst_rate,
        })),
      });
    } catch (err) {
      console.error("Error fetching voucher for edit:", err);
      handleEdit(voucher);
    }
  };

  const handleViewWithData = async (voucher: any) => {
    if (!voucher || !voucher.id) {
      return;
    }
    try {
      const response = await api.get(`/purchase-orders/${voucher.id}`);
      let fullVoucherData = response.data;
      fullVoucherData.date = fullVoucherData.date ? new Date(fullVoucherData.date).toISOString().split('T')[0] : '';
      setMode("view");
      reset({
        ...fullVoucherData,
        items: fullVoucherData.items.map((item: any) => ({
          ...item,
          cgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
          sgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
          igst_rate: isIntrastate ? 0 : item.gst_rate,
        })),
      });
    } catch (err) {
      console.error("Error fetching voucher for view:", err);
      handleView(voucher);
    }
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
            unit_price: item.unit_price,
            original_unit_price: item.product?.unit_price || item.unit_price || 0,
            discount_percentage: item.discount_percentage || 0,
            discount_amount: item.discount_amount || 0,
            gst_rate: item.gst_rate ?? 18,
            cgst_rate: isIntrastate ? (item.gst_rate ?? 18) / 2 : 0,
            sgst_rate: isIntrastate ? (item.gst_rate ?? 18) / 2 : 0,
            igst_rate: isIntrastate ? 0 : item.gst_rate ?? 18,
            amount: item.total_amount,
            unit: item.unit,
            current_stock: item.current_stock || 0,
            reorder_level: item.reorder_level || 0,
            description: item.description || '',
          });
        });
      }
    }
  }, [voucherData, mode, reset, append, remove, isIntrastate]);

  const indexContent = (
    <TableContainer sx={{ maxHeight: 400 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell
              align="center"
              sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}
            >
              Voucher No.
            </TableCell>
            <TableCell
              align="center"
              sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}
            >
              Date
            </TableCell>
            <TableCell
              align="center"
              sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}
            >
              Vendor
            </TableCell>
            <TableCell
              align="center"
              sx={{ fontSize: 15, fontWeight: "bold", p: 1 }}
            >
              Total Amount
            </TableCell>
            <TableCell
              align="right"
              sx={{ fontSize: 15, fontWeight: "bold", p: 0, width: 40 }}
            ></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {latestVouchers.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} align="center">
                No purchase orders available
              </TableCell>
            </TableRow>
          ) : (
            latestVouchers.slice(0, 7).map((voucher: any) => (
              <TableRow
                key={voucher.id}
                hover
                onContextMenu={(e) => {
                  e.preventDefault();
                  handleContextMenu(e, voucher);
                }}
                sx={{ cursor: "pointer" }}
              >
                <TableCell
                  align="center"
                  sx={{ fontSize: 12, p: 1 }}
                  onClick={() => handleViewWithData(voucher)}
                >
                  {voucher.voucher_number}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>
                  {voucher.date
                    ? new Date(voucher.date).toLocaleDateString()
                    : "N/A"}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>
                  {vendorList?.find((v: any) => v.id === voucher.vendor_id)
                    ?.name || "N/A"}
                </TableCell>
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>
                  ₹{voucher.total_amount?.toLocaleString() || "0"}
                </TableCell>
                <TableCell align="right" sx={{ fontSize: 12, p: 0 }}>
                  <VoucherContextMenu
                    voucher={voucher}
                    voucherType="Purchase Order"
                    onView={() => handleViewWithData(voucher)}
                    onEdit={() => handleEditWithData(voucher)}
                    onDelete={() => handleDelete(voucher)}
                    onPrint={() => handleGeneratePDF(voucher)}
                    onDuplicate={() => handleDuplicate(voucher.id)}
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

  const gstRatesVary = Object.keys(gstBreakdown).length > 1;

  const formHeader = (
    <Box
      sx={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <Typography variant="h5" sx={{ fontSize: 20, fontWeight: "bold" }}>
        {config.voucherTitle} -{" "}
        {mode === "create" ? "Create" : mode === "edit" ? "Edit" : "View"}
      </Typography>
      <VoucherHeaderActions
        mode={mode}
        voucherType={config.voucherTitle}
        voucherRoute="/vouchers/Purchase-Vouchers/purchase-order"
        currentId={mode !== "create" ? voucherData?.id : null}
        onEdit={() =>
          voucherData && voucherData.id && handleEditWithData(voucherData)
        }
        onCreate={handleCreate}
        onCancel={handleCancel}
      />
    </Box>
  );

  const formBody = (
    <Box>
      {gstError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {gstError}
        </Alert>
      )}
      <form
        id="voucherForm"
        onSubmit={handleSubmit(onSubmit)}
        style={voucherStyles.formContainer}
      >
        <Grid container spacing={1}>
          <Grid size={6}>
            <TextField
              fullWidth
              label="Voucher Number"
              {...control.register("voucher_number")}
              disabled
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{
                style: {
                  fontSize: 14,
                  textAlign: "center",
                  fontWeight: "bold",
                },
              }}
              size="small"
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
            />
          </Grid>
          <Grid size={6}>
            <TextField
              fullWidth
              label="Date"
              type="date"
              {...control.register("date")}
              disabled={mode === "view"}
              InputLabelProps={{
                shrink: true,
                style: {
                  fontSize: 12,
                  display: "block",
                  visibility: "visible",
                },
              }}
              inputProps={{ style: { fontSize: 14, textAlign: "center" } }}
              size="small"
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
            />
          </Grid>
          <Grid size={4}>
            <Autocomplete
              size="small"
              options={enhancedVendorOptions}
              getOptionLabel={(option: any) => option?.name || ""}
              value={selectedVendor || null}
              onChange={(_, newValue) => {
                if (newValue?.id === null) {
                  setShowAddVendorModal(true);
                } else {
                  setValue("vendor_id", newValue?.id || null);
                }
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Vendor"
                  error={!!errors.vendor_id}
                  helperText={errors.vendor_id ? "Required" : ""}
                  InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
                  inputProps={{ ...params.inputProps, style: { fontSize: 14 } }}
                  size="small"
                  sx={{ "& .MuiInputBase-root": { height: 27 } }}
                />
              )}
              disabled={mode === "view"}
            />
          </Grid>
          <Grid size={4}>
            <TextField
              fullWidth
              label="Reference"
              {...control.register("reference")}
              disabled={mode === "view"}
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14 } }}
              size="small"
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
            />
          </Grid>
          <Grid size={4}>
            <TextField
              fullWidth
              label="Payment Terms"
              {...control.register("payment_terms")}
              disabled={mode === "view"}
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14 } }}
              size="small"
              sx={{ "& .MuiInputBase-root": { height: 27 } }}
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
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14 } }}
              size="small"
            />
          </Grid>
          <Grid
            size={12}
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              height: 27,
            }}
          >
            <Typography variant="h6" sx={{ fontSize: 16, fontWeight: "bold" }}>
              Items
            </Typography>
          </Grid>
          <Grid size={12}>
            <Box sx={{display: 'flex', gap: 2, mb: 1}}>
              <FormControlLabel
                control={
                  <Checkbox 
                    checked={lineDiscountEnabled} 
                    onChange={(e) => handleToggleLineDiscount(e.target.checked)}
                    disabled={mode === "view"}
                  />
                }
                label="Add Line Discount"
              />
              <FormControlLabel
                control={
                  <Checkbox 
                    checked={totalDiscountEnabled} 
                    onChange={(e) => handleToggleTotalDiscount(e.target.checked)}
                    disabled={mode === "view"}
                  />
                }
                label="Add Total Discount"
              />
              <FormControlLabel
                control={
                  <Checkbox 
                    checked={descriptionEnabled} 
                    onChange={(e) => handleToggleDescription(e.target.checked)}
                    disabled={mode === "view"}
                  />
                }
                label="Add Description"
              />
            </Box>
            <TableContainer
              component={Paper}
              sx={{ maxHeight: 300, ...voucherStyles.centeredTable }}
            >
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell
                      sx={{
                        fontSize: 12,
                        fontWeight: "bold",
                        p: 1,
                        width: "30%",
                      }}
                    >
                      Product
                    </TableCell>
                    <TableCell
                      sx={{
                        fontSize: 12,
                        fontWeight: "bold",
                        p: 1,
                        width: "100px",
                      }}
                    ></TableCell>
                    <TableCell
                      sx={{
                        fontSize: 12,
                        fontWeight: "bold",
                        p: 1,
                        textAlign: "right",
                      }}
                    >
                      Qty
                    </TableCell>
                    <TableCell
                      sx={{
                        fontSize: 12,
                        fontWeight: "bold",
                        p: 1,
                        textAlign: "right",
                      }}
                    >
                      Rate
                    </TableCell>
                    {lineDiscountEnabled && (
                      <TableCell sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}>
                        {lineDiscountType === 'percentage' ? 'Disc%' : 'Disc ₹'}
                      </TableCell>
                    )}
                    <TableCell sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}>
                      GST%
                    </TableCell>
                    <TableCell sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}>
                      Line Total
                    </TableCell>
                    {mode !== "view" && (
                      <TableCell
                        sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}
                      >
                        Action
                      </TableCell>
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
                              setValue(
                                `items.${index}.product_id`,
                                product?.id || null,
                              );
                              setValue(
                                `items.${index}.product_name`,
                                product?.product_name || "",
                              );
                              setValue(
                                `items.${index}.unit_price`,
                                product?.unit_price || 0,
                              );
                              setValue(
                                `items.${index}.original_unit_price`,
                                product?.unit_price || 0,
                              );
                              setValue(
                                `items.${index}.gst_rate`,
                                product?.gst_rate ?? 18,
                              );
                              setValue(
                                `items.${index}.cgst_rate`,
                                isIntrastate ? (product?.gst_rate ?? 18) / 2 : 0,
                              );
                              setValue(
                                `items.${index}.sgst_rate`,
                                isIntrastate ? (product?.gst_rate ?? 18) / 2 : 0,
                              );
                              setValue(
                                `items.${index}.igst_rate`,
                                isIntrastate ? 0 : product?.gst_rate ?? 18,
                              );
                              setValue(
                                `items.${index}.unit`,
                                product?.unit || "",
                              );
                              setValue(
                                `items.${index}.reorder_level`,
                                product?.reorder_level || 0,
                              );
                            }}
                            disabled={mode === "view"}
                            size="small"
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: "center" }}>
                          {stockLoading[index] ? (
                            <CircularProgress size={12} />
                          ) : watch(`items.${index}.product_id`) ? (
                            <Typography
                              variant="caption"
                              color={getStockColor(
                                watch(`items.${index}.current_stock`),
                                watch(`items.${index}.reorder_level`),
                              )}
                            >
                              {watch(`items.${index}.current_stock`)}{" "}
                              {watch(`items.${index}.unit`)}
                            </Typography>
                          ) : null}
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: "right" }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.quantity`, {
                              valueAsNumber: true,
                            })}
                            disabled={mode === "view"}
                            size="small"
                            sx={{ width: 120 }}
                            InputProps={{
                              inputProps: { min: 0, step: 1 },
                              endAdornment: <InputAdornment position="end">{watch(`items.${index}.unit`) || ''}</InputAdornment>,
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: "right" }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.unit_price`, {
                              valueAsNumber: true,
                            })}
                            disabled={mode === "view"}
                            size="small"
                            sx={{ width: 80 }}
                            InputProps={{
                              inputProps: { min: 0, step: 0.01 },
                            }}
                          />
                        </TableCell>
                        {lineDiscountEnabled && (
                          <TableCell sx={{ p: 1 }}>
                            <TextField
                              type="number"
                              {...control.register(
                                `items.${index}.${lineDiscountType === 'percentage' ? 'discount_percentage' : 'discount_amount'}`,
                                { valueAsNumber: true },
                              )}
                              disabled={mode === "view"}
                              size="small"
                              sx={{ width: 60 }}
                              InputProps={{
                                inputProps: { min: 0, step: lineDiscountType === 'percentage' ? 0.01 : 1 },
                              }}
                            />
                          </TableCell>
                        )}
                        <TableCell sx={{ p: 1 }}>
                          <Autocomplete
                            size="small"
                            options={GST_SLABS}
                            value={watch(`items.${index}.gst_rate`) ?? 18}
                            onChange={(_, value) => {
                              setValue(`items.${index}.gst_rate`, value ?? 18);
                              setValue(
                                `items.${index}.cgst_rate`,
                                isIntrastate ? (value ?? 18) / 2 : 0,
                              );
                              setValue(
                                `items.${index}.sgst_rate`,
                                isIntrastate ? (value ?? 18) / 2 : 0,
                              );
                              setValue(
                                `items.${index}.igst_rate`,
                                isIntrastate ? 0 : value ?? 18,
                              );
                            }}
                            renderInput={(params) => (
                              <TextField
                                {...params}
                                size="small"
                                sx={{ width: 60 }}
                              />
                            )}
                            disabled={mode === "view"}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, fontSize: 14 }}>
                          ₹{computedItems[index]?.amount?.toLocaleString() || "0"}
                        </TableCell>
                        {mode !== "view" && (
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
                      {descriptionEnabled && (
                        <TableRow>
                          <TableCell colSpan={mode !== "view" ? 8 : 7} sx={{ p: 1 }}>
                            <TextField
                              multiline
                              rows={1}
                              placeholder="Description"
                              {...control.register(`items.${index}.description`)}
                              disabled={mode === "view"}
                              size="small"
                              fullWidth
                            />
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {mode !== "view" && (
              <Box sx={{ display: "flex", justifyContent: "center", mt: 1 }}>
                <Fab color="primary" size="small" onClick={handleAddItem}>
                  <Add />
                </Fab>
              </Box>
            )}
          </Grid>
          <Grid size={12}>
            <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 2 }}>
              <Box sx={{ minWidth: 300 }}>
                <Grid container spacing={1}>
                  <Grid size={6}>
                    <Typography
                      variant="body2"
                      sx={{ textAlign: "right", fontSize: 14 }}
                    >
                      Subtotal:
                    </Typography>
                  </Grid>
                  <Grid size={6}>
                    <Typography
                      variant="body2"
                      sx={{
                        textAlign: "right",
                        fontSize: 14,
                        fontWeight: "bold",
                      }}
                    >
                      ₹{totalSubtotal.toLocaleString()}
                    </Typography>
                  </Grid>

                  {totalDiscountEnabled && (
                    <>
                      <Grid size={6}>
                        <Typography
                          variant="body2"
                          sx={{ textAlign: "right", fontSize: 14 }}
                        >
                          Disc {totalDiscountType === 'percentage' ? '%' : '₹'}:
                        </Typography>
                      </Grid>
                      <Grid size={6} sx={{ textAlign: "right" }}>
                        {mode === "view" ? (
                          <Typography
                            variant="body2"
                            sx={{
                              fontSize: 14,
                              fontWeight: "bold",
                            }}
                          >
                            {totalDiscountType === 'percentage'
                              ? `${watch("total_discount") || 0}%`
                              : `₹${(watch("total_discount") || 0).toLocaleString()}`}
                          </Typography>
                        ) : (
                          <TextField
                            type="number"
                            {...control.register("total_discount", { valueAsNumber: true })}
                            size="small"
                            sx={{ width: 120 }}
                            InputProps={{
                              inputProps: { min: 0, step: totalDiscountType === 'percentage' ? 0.01 : 0.01 },
                              endAdornment: (
                                <InputAdornment position="end" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                  <Typography sx={{ mr: 0.5 }}>{totalDiscountType === 'percentage' ? '%' : '₹'}</Typography>
                                  <IconButton
                                    size="small"
                                    onClick={() => {
                                      // clear the discount value and disable total discount
                                      setValue("total_discount", 0);
                                      handleToggleTotalDiscount(false);
                                    }}
                                    aria-label="clear discount"
                                  >
                                    <Clear fontSize="small" />
                                  </IconButton>
                                </InputAdornment>
                              ),
                            }}
                          />
                        )}
                      </Grid>
                    </>
                  )}

                  {isIntrastate ? (
                    <>
                      <Grid size={6}>
                        <Typography
                          variant="body2"
                          sx={{ textAlign: "right", fontSize: 14 }}
                        >
                          CGST:
                        </Typography>
                      </Grid>
                      <Grid size={6}>
                        <Typography
                          variant="body2"
                          sx={{
                            textAlign: "right",
                            fontSize: 14,
                            fontWeight: "bold",
                          }}
                        >
                          ₹{totalCgst.toLocaleString()}
                        </Typography>
                      </Grid>
                      <Grid size={6}>
                        <Typography
                          variant="body2"
                          sx={{ textAlign: "right", fontSize: 14 }}
                        >
                          SGST:
                        </Typography>
                      </Grid>
                      <Grid size={6}>
                        <Typography
                          variant="body2"
                          sx={{
                            textAlign: "right",
                            fontSize: 14,
                            fontWeight: "bold",
                          }}
                        >
                          ₹{totalSgst.toLocaleString()}
                        </Typography>
                      </Grid>
                    </>
                  ) : (
                    <>
                      <Grid size={6}>
                        <Typography
                          variant="body2"
                          sx={{ textAlign: "right", fontSize: 14 }}
                        >
                          IGST:
                        </Typography>
                      </Grid>
                      <Grid size={6}>
                        <Typography
                          variant="body2"
                          sx={{
                            textAlign: "right",
                            fontSize: 14,
                            fontWeight: "bold",
                          }}
                        >
                          ₹{totalIgst.toLocaleString()}
                        </Typography>
                      </Grid>
                    </>
                  )}
                  <Grid size={6}>
                    <Typography
                      variant="body2"
                      sx={{ textAlign: "right", fontSize: 14 }}
                    >
                      Round Off:
                    </Typography>
                  </Grid>
                  <Grid size={6}>
                    <Typography
                      variant="body2"
                      sx={{
                        textAlign: "right",
                        fontSize: 14,
                        fontWeight: "bold",
                      }}
                    >
                      ₹{totalRoundOff > 0 ? '+' : ''}{totalRoundOff.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid size={6}>
                    <Typography
                      variant="h6"
                      sx={{
                        textAlign: "right",
                        fontSize: 16,
                        fontWeight: "bold",
                      }}
                    >
                      Total:
                    </Typography>
                  </Grid>
                  <Grid size={6}>
                    <Typography
                      variant="h6"
                      sx={{
                        textAlign: "right",
                        fontSize: 16,
                        fontWeight: "bold",
                      }}
                    >
                      ₹{Math.round(totalAmount).toLocaleString()}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Box>
          </Grid>
          <Grid size={12}>
            <TextField
              fullWidth
              label="Amount in Words"
              value={getAmountInWords(totalAmount)}
              disabled
              InputLabelProps={{ shrink: true, style: { fontSize: 12 } }}
              inputProps={{ style: { fontSize: 14 } }}
              size="small"
            />
          </Grid>
        </Grid>
      </form>
      <Dialog open={discountDialogOpen} onClose={handleDiscountDialogClose}>
        <DialogTitle>Select Discount Type</DialogTitle>
        <DialogContent>
          <Typography>Please select the discount type for {discountDialogFor} discount.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleDiscountTypeSelect('percentage')}>Discount %</Button>
          <Button onClick={() => handleDiscountTypeSelect('amount')}>Discount ₹</Button>
          <Button onClick={handleDiscountDialogClose}>Cancel</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={roundOffConfirmOpen} onClose={() => setRoundOffConfirmOpen(false)}>
        <DialogTitle>Confirm Round Off</DialogTitle>
        <DialogContent>
          <Typography>Round off amount is {totalRoundOff.toFixed(2)}. Proceed with save?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRoundOffConfirmOpen(false)}>Cancel</Button>
          <Button onClick={() => {
            setRoundOffConfirmOpen(false);
            if (submitData) {
              handleFinalSubmit(submitData);
            }
          }} variant="contained">Confirm</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  if (isLoading || companyLoading) {
    return (
      <Container>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="400px"
        >
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
        formBody={formBody}
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
        onAdd={(newVendor) => {
          setValue("vendor_id", newVendor.id);
          refreshMasterData();
        }}
        loading={addVendorLoading}
        setLoading={setAddVendorLoading}
      />
      <AddProductModal
        open={showAddProductModal}
        onClose={() => setShowAddProductModal(false)}
        onAdd={(newProduct) => {
          setValue(`items.${addingItemIndex}.product_id`, newProduct.id);
          setValue(
            `items.${addingItemIndex}.product_name`,
            newProduct.product_name,
          );
          setValue(
            `items.${addingItemIndex}.unit_price`,
            newProduct.unit_price || 0,
          );
          setValue(
            `items.${addingItemIndex}.original_unit_price`,
            newProduct.unit_price || 0,
          );
          setValue(
            `items.${addingItemIndex}.gst_rate`,
            newProduct.gst_rate ?? 18,
          );
          setValue(
            `items.${addingItemIndex}.cgst_rate`,
            isIntrastate ? (newProduct.gst_rate ?? 18) / 2 : 0,
          );
          setValue(
            `items.${addingItemIndex}.sgst_rate`,
            isIntrastate ? (newProduct.gst_rate ?? 18) / 2 : 0,
          );
          setValue(
            `items.${addingItemIndex}.igst_rate`,
            isIntrastate ? 0 : newProduct.gst_rate ?? 18,
          );
          setValue(`items.${addingItemIndex}.unit`, newProduct.unit || "");
          setValue(
            `items.${addingItemIndex}.reorder_level`,
            newProduct.reorder_level || 0,
          );
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
        voucherType="Purchase Order"
        onClose={handleCloseContextMenu}
        onEdit={handleEditWithData}
        onView={handleViewWithData}
        onDelete={handleDelete}
        onPrint={handleGeneratePDF}
        onDuplicate={(id: number) => handleDuplicate(id)}
      />
    </>
  );
};

export default PurchaseOrderPage;