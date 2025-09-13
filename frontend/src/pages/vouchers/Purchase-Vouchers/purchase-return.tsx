// frontend/src/pages/vouchers/Purchase-Vouchers/purchase-return.tsx
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
  Fab,
  Alert,
  Button,
  Checkbox,
  FormControlLabel,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { Add, Remove, Clear } from "@mui/icons-material";
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
import { useGstValidation } from "../../../hooks/useGstValidation";
import { useVoucherDiscounts } from "../../../hooks/useVoucherDiscounts";
import { handleFinalSubmit, handleDuplicate, getStockColor } from "../../../utils/voucherHandlers";
import voucherFormStyles from "../../../styles/voucherFormStyles";

const PurchaseReturnPage: React.FC = () => {
  const { company, isLoading: companyLoading } = useCompany();
  const router = useRouter();
  const { productId, vendorId } = router.query;
  const config = getVoucherConfig("purchase-return");
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
    nextVoucherNumber,
    sortedVouchers,
    latestVouchers,
    computedItems,
    totalAmount,
    totalSubtotal,
    totalCgst,
    totalSgst,
    totalIgst,
    totalRoundOff,
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
  } = useVoucherPage(config);

  const [showVoucherListModal, setShowVoucherListModal] = useState(false);
  const [submitData, setSubmitData] = useState<any>(null);
  const [roundOffConfirmOpen, setRoundOffConfirmOpen] = useState(false);
  const [stockLoading, setStockLoading] = useState<{ [key: number]: boolean }>({});
  const selectedVendorId = watch("vendor_id");

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
  }, [fields.length, productList, ...fields.map((_, index) => watch(`items.${index}.product_id`))]);

  const companyState = useMemo(() => {
    if (company?.state_code) {
      return company.state_code;
    }
    if (company?.gst_number && company.gst_number.length >= 2) {
      return company.gst_number.slice(0, 2);
    }
    return null;
  }, [company]);

  const selectedVendor = vendorList?.find((v: any) => v.id === selectedVendorId);

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
      return true;
    }
    return companyState === vendorState;
  }, [companyState, vendorState]);

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

  const handleVoucherClick = async (voucher: any) => {
    try {
      const response = await api.get(`/purchase-returns/${voucher.id}`);
      const fullVoucherData = response.data;
      setMode("view");
      reset(fullVoucherData);
    } catch (err) {
      console.error("Failed to load voucher data for view:", err);
      setMode("view");
      reset(voucher);
    }
  };

  const handleEditWithData = async (voucher: any) => {
    if (!voucher || !voucher.id) return;
    try {
      const response = await api.get(`/purchase-returns/${voucher.id}`);
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
    if (!voucher || !voucher.id) return;
    try {
      const response = await api.get(`/purchase-returns/${voucher.id}`);
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

  const enhancedVendorOptions = [...(vendorList || []), { id: null, name: "Add New Vendor..." }];

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
                <TableCell align="center" sx={{ fontSize: 12, p: 1 }}>₹{voucher.total_amount?.toLocaleString() || "0"}</TableCell>
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
        currentId={mode !== "create" ? voucherList?.find((v: any) => v.id === watch('id'))?.id : null}
        onEdit={() => handleEditWithData(voucherList?.find((v: any) => v.id === watch('id')))}
        onCreate={handleCreate}
      />
    </Box>
  );

  const formBody = (
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
            <Autocomplete 
              size="small" 
              options={enhancedVendorOptions} 
              getOptionLabel={(option: any) => option?.name || ""} 
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
          <Grid size={4}>
            <VoucherReferenceDropdown
              voucherType="purchase-return"
              value={{ referenceType: watch('reference_type'), referenceId: watch('reference_id'), referenceNumber: watch('reference_number') }}
              onChange={(reference) => { setValue('reference_type', reference.referenceType || ''); setValue('reference_id', reference.referenceId || null); setValue('reference_number', reference.referenceNumber || ''); }}
              disabled={mode === 'view'}
              onReferenceSelected={handleReferenceSelected}
            />
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
              lineDiscountEnabled={lineDiscountEnabled}
              lineDiscountType={lineDiscountType}
              totalDiscountEnabled={totalDiscountEnabled}
              descriptionEnabled={descriptionEnabled}
              handleToggleLineDiscount={handleToggleLineDiscount}
              handleToggleTotalDiscount={handleToggleTotalDiscount}
              handleToggleDescription={handleToggleDescription}
              stockLoading={stockLoading}
              getStockColor={getStockColor}
              selectedProducts={selectedProducts}
              showLineDiscountCheckbox={mode !== "view"}
              showTotalDiscountCheckbox={mode !== "view"}
              showDescriptionCheckbox={mode !== "view"}
            />
          </Grid>
          <Grid size={12}>
            <VoucherFormTotals
              totalSubtotal={totalSubtotal}
              totalCgst={totalCgst}
              totalSgst={totalSgst}
              totalIgst={totalIgst}
              totalAmount={totalAmount}
              totalRoundOff={totalRoundOff}
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
              value={getAmountInWords(totalAmount)}
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
        formContent={formBody}
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
    </>
  );
};

export default PurchaseReturnPage;