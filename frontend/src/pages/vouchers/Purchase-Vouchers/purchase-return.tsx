// frontend/src/pages/vouchers/Purchase-Vouchers/purchase-return.tsx
// Purchase Return Page - Refactored using shared DRY logic
import React, { useMemo, useState, useEffect } from "react";
import {
  Box,
  Button,
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
  Fab,
} from "@mui/material";
import { Add, Remove } from "@mui/icons-material";
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
const PurchaseReturnPage: React.FC = () => {
  const { company, isLoading: companyLoading, error: companyError } = useCompany();
  const router = useRouter();
  const { productId, vendorId } = router.query;
  const config = getVoucherConfig("purchase-return");
  const voucherStyles = getVoucherStyles();
  const [gstError, setGstError] = useState<string | null>(null);

  // Derive company state code with fallback to gst_number prefix
  const companyState = useMemo(() => {
    if (company?.state_code) {
      console.log("[PurchaseReturnPage] Company state_code:", company.state_code);
      return company.state_code;
    }
    if (company?.gst_number && company.gst_number.length >= 2) {
      const stateCodeFromGst = company.gst_number.slice(0, 2);
      console.log("[PurchaseReturnPage] Derived state from GST:", stateCodeFromGst);
      return stateCodeFromGst;
    }
    console.log("[PurchaseReturnPage] No state code available");
    return null;
  }, [company]);
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
  // Purchase Return specific state
  const selectedVendorId = watch("vendor_id");
  const selectedVendor = vendorList?.find(
    (v: any) => v.id === selectedVendorId,
  );

  // Validate state codes for GST calculation after company data is loaded
  useEffect(() => {
    if (companyLoading) {
      console.log("[PurchaseReturnPage] Company data still loading, skipping GST validation");
      return;
    }
    if (selectedVendorId && !selectedVendor?.state_code && !selectedVendor?.gst_number) {
      setGstError("Vendor state code or GST number is missing. Please update vendor details.");
    } else if (!companyState) {
      setGstError("Company state code or GST number is missing. Please update company details in settings.");
    } else {
      setGstError(null);
    }
    console.log("[PurchaseReturnPage] GST Validation:", {
      selectedVendor,
      companyState,
      selectedVendorId,
      vendorStateCode: selectedVendor?.state_code || selectedVendor?.gst_number?.slice(0, 2),
      timestamp: new Date().toISOString(),
    });
  }, [selectedVendorId, selectedVendor, companyState, companyLoading]);

  // Determine if transaction is intrastate
  const vendorState = useMemo(() => {
    if (selectedVendor?.state_code) {
      return selectedVendor.state_code;
    }
    if (selectedVendor?.gst_number && selectedVendor.gst_number.length >= 2) {
      return selectedVendor.gst_number.slice(0, 2);
    }
    return null;
  }, [selectedVendor]);

  const isIntrastate = useMemo(() => {
    if (!companyState || !vendorState) {
      return true; // Default to intrastate if state codes are not available
    }
    return companyState === vendorState;
  }, [companyState, vendorState]);
  // Enhanced vendor options with "Add New"
  const enhancedVendorOptions = [
    ...(vendorList || []),
    { id: null, name: "Add New Vendor..." },
  ];
  // Stock data state for items
  const [stockLoading, setStockLoading] = useState<{ [key: number]: boolean }>(
    {},
  );
  // Purchase Return specific handlers
  const handleAddItem = () => {
    append({
      product_id: null,
      product_name: "",
      quantity: 1,
      unit_price: 0,
      original_unit_price: 0,
      discount_percentage: 0,
      gst_rate: 18,
      cgst_rate: isIntrastate ? 9 : 0,
      sgst_rate: isIntrastate ? 9 : 0,
      igst_rate: isIntrastate ? 0 : 18,
      amount: 0,
      unit: "",
      current_stock: 0,
      reorder_level: 0,
    });
  };
  // Custom submit handler to prompt for PDF after save
  const onSubmit = async (data: any) => {
    try {
      if (config.hasItems !== false) {
        data.items = computedItems.map((item: any) => ({
          ...item,
          cgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
          sgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
          igst_rate: isIntrastate ? 0 : item.gst_rate,
        }));
        data.total_amount = totalAmount;
        data.is_intrastate = isIntrastate;
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
        }
      }

      let response;
      if (mode === "create") {
        response = await createMutation.mutateAsync(data);
        if (confirm("Purchase return created successfully. Generate PDF?")) {
          handleGeneratePDF(response);
        }
      } else if (mode === "edit") {
        response = await updateMutation.mutateAsync(data);
        if (confirm("Purchase return updated successfully. Generate PDF?")) {
          handleGeneratePDF(response);
        }
      }
    } catch (err) {
      console.error("Failed to save purchase return:", err);
      alert("Failed to save purchase return. Please try again.");
    }
  };
  // Function to get stock color
  const getStockColor = (stock: number, reorder: number) => {
    if (stock === 0) {
      return "error.main";
    }
    if (stock <= reorder) {
      return "warning.main";
    }
    return "success.main";
  };
  // Memoize all selected products
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
  // Effect to fetch stock when product changes
  useEffect(() => {
    fields.forEach((_, index) => {
      const productId = watch(`items.${index}.product_id`);
      if (productId) {
        setStockLoading((prev) => ({ ...prev, [index]: true }));
        getStock({ queryKey: ["", { product_id: productId }] })
          .then((res) => {
            console.log("Stock Response for product " + productId + ":", res);
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
  // Manual fetch for voucher number if not loaded
  useEffect(() => {
    if (mode === "create" && !nextVoucherNumber && !isLoading) {
      voucherService
        .getNextVoucherNumber(config.nextNumberEndpoint)
        .then((number) => setValue("voucher_number", number))
        .catch((err) => console.error("Failed to fetch voucher number:", err));
    }
  }, [mode, nextVoucherNumber, isLoading, setValue, config.nextNumberEndpoint]);
  const handleVoucherClick = async (voucher: any) => {
    try {
      // Fetch complete voucher data including items
      const response = await api.get(`/purchase-returns/${voucher.id}`);
      const fullVoucherData = response.data;
      // Load the complete voucher data into the form
      setMode("view");
      reset(fullVoucherData);
    } catch (err) {
      console.error("Failed to load voucher data for view:", err);
      // Fallback to available data
      setMode("view");
      reset(voucher);
    }
  };
  // Enhanced handleEdit to fetch complete data
  const handleEditWithData = async (voucher: any) => {
    try {
      const response = await api.get(`/purchase-returns/${voucher.id}`);
      const fullVoucherData = response.data;
      setMode("edit");
      reset(fullVoucherData);
    } catch (err) {
      console.error("Failed to load voucher data for edit:", err);
      handleEdit(voucher);
    }
  };
  // Enhanced handleView to fetch complete data
  const handleViewWithData = async (voucher: any) => {
    try {
      const response = await api.get(`/purchase-returns/${voucher.id}`);
      const fullVoucherData = response.data;
      setMode("view");
      reset(fullVoucherData);
    } catch (err) {
      console.error("Failed to load voucher data for view:", err);
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
                  No purchase returns available
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
                      voucherType="Purchase Return"
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
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 2,
        }}
      >
        <Typography variant="h5" sx={{ fontSize: 20, fontWeight: "bold" }}>
          {config.voucherTitle} -{" "}
          {mode === "create" ? "Create" : mode === "edit" ? "Edit" : "View"}
        </Typography>
        <VoucherHeaderActions
          mode={mode}
          voucherType={config.voucherTitle}
          voucherRoute="/vouchers/Purchase-Vouchers/purchase-return"
          currentId={selectedVendorId}
        />
      </Box>
      <form
        id="voucherForm"
        onSubmit={handleSubmit(onSubmit)}
        style={voucherStyles.formContainer}
      >
        <Grid container spacing={1}>
          {/* Voucher Number */}
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
          {/* Date */}
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
          {/* Vendor, Reference, Payment Terms in one row */}
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
          {/* Items section */}
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
          {/* Items Table */}
          <Grid size={12}>
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
                    <TableCell sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}>
                      Disc%
                    </TableCell>
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
                                `items.${index}.gst_rate`,
                                product?.gst_rate || 18,
                              );
                              setValue(
                                `items.${index}.unit`,
                                product?.unit || "",
                              );
                              setValue(
                                `items.${index}.reorder_level`,
                                product?.reorder_level || 0,
                              );
                              // Stock fetch handled in useEffect
                            }}
                            disabled={mode === "view"}
                            size="small"
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1, textAlign: "right" }}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "flex-end",
                            }}
                          >
                            <TextField
                              type="number"
                              {...control.register(`items.${index}.quantity`, {
                                valueAsNumber: true,
                              })}
                              disabled={mode === "view"}
                              size="small"
                              sx={{ width: 60 }}
                            />
                            <Typography sx={{ ml: 1, fontSize: 12 }}>
                              {watch(`items.${index}.unit`)}
                            </Typography>
                          </Box>
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
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1 }}>
                          <TextField
                            type="number"
                            {...control.register(
                              `items.${index}.discount_percentage`,
                              { valueAsNumber: true },
                            )}
                            disabled={mode === "view"}
                            size="small"
                            sx={{ width: 60 }}
                          />
                        </TableCell>
                        <TableCell sx={{ p: 1 }}>
                          <Autocomplete
                            size="small"
                            options={GST_SLABS}
                            value={watch(`items.${index}.gst_rate`) || 18}
                            onChange={(_, value) =>
                              setValue(`items.${index}.gst_rate`, value || 18)
                            }
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
                          ₹
                          {computedItems[index]?.amount?.toLocaleString() ||
                            "0"}
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
                      {/* Stock display below the row - only qty and unit */}
                      <TableRow>
                        <TableCell
                          colSpan={mode !== "view" ? 7 : 6}
                          sx={{ py: 0.5, pl: 2, bgcolor: "action.hover" }}
                        >
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
                      </TableRow>
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
          {/* Totals */}
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
                  <Grid size={6}>
                    <Typography
                      variant="body2"
                      sx={{ textAlign: "right", fontSize: 14 }}
                    >
                      GST:
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
                      ₹{totalGst.toLocaleString()}
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
              inputProps={{ style: { fontSize: 14 } }}
              size="small"
            />
          </Grid>
        </Grid>
      </form>
    </Box>
  );
  if (isLoading) {
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
export default PurchaseReturnPage;
