// frontend/src/pages/vouchers/Sales-Vouchers/delivery-challan.tsx
import React, { useMemo, useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Typography,
  Grid,
  IconButton,
  CircularProgress,
  Container,
  Paper,
  Autocomplete,
  Fab,
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
  FormControlLabel,
  Checkbox,
  InputAdornment,
} from '@mui/material';
import { Add, Remove } from '@mui/icons-material';
import AddCustomerModal from '../../../components/AddCustomerModal';
import AddProductModal from '../../../components/AddProductModal';
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherLayout from '../../../components/VoucherLayout';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import VoucherReferenceDropdown from '../../../components/VoucherReferenceDropdown';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, getVoucherStyles, GST_SLABS } from '../../../utils/voucherUtils';
import { getStock } from '../../../services/masterService';
import { voucherService } from '../../../services/vouchersService';
import api from '../../../lib/api';
import { useCompany } from "../../../context/CompanyContext";
import { useGstValidation } from "../../../hooks/useGstValidation";
import { handleDuplicate, getStockColor } from "../../../utils/voucherHandlers";
import voucherFormStyles from "../../../styles/voucherFormStyles";

const DeliveryChallanPage: React.FC = () => {
  const { company, isLoading: companyLoading } = useCompany();
  const config = getVoucherConfig('delivery-challan');
  const voucherStyles = getVoucherStyles();

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
    nextVoucherNumber,
    sortedVouchers,
    latestVouchers,
    voucherData,
    computedItems,
    totalAmount,
    totalSubtotal,
    totalCgst,
    totalSgst,
    totalIgst,
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
  const [stockLoading, setStockLoading] = useState<{[key: number]: boolean}>({});
  const selectedCustomerId = watch('customer_id');
  const [useDifferentShipping, setUseDifferentShipping] = useState(false);

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
  }, [fields.length, productList, ...fields.map((_, index) => watch(`items.${index}.product_id`))]);

  useEffect(() => {
    fields.forEach((_, index) => {
      const productId = watch(`items.${index}.product_id`);
      if (productId) {
        setStockLoading(prev => ({ ...prev, [index]: true }));
        getStock({ queryKey: ['', { product_id: productId }] })
          .then(res => {
            const stockData = res[0] || { quantity: 0 };
            setValue(`items.${index}.current_stock`, stockData.quantity);
            setStockLoading(prev => ({ ...prev, [index]: false }));
          })
          .catch(err => {
            console.error('Failed to fetch stock:', err);
            setStockLoading(prev => ({ ...prev, [index]: false }));
          });
      } else {
        setValue(`items.${index}.current_stock`, 0);
        setStockLoading(prev => ({ ...prev, [index]: false }));
      }
    });
  }, [fields.map(f => watch(`items.${fields.indexOf(f)}.product_id`)).join(','), setValue, fields.length]);

  useEffect(() => {
    if (mode === 'create' && !nextVoucherNumber && !isLoading) {
      voucherService.getNextVoucherNumber(config.nextNumberEndpoint)
        .then(number => setValue('voucher_number', number))
        .catch(err => console.error('Failed to fetch voucher number:', err));
    }
  }, [mode, nextVoucherNumber, isLoading, setValue, config.nextNumberEndpoint]);

  const handleVoucherClick = async (voucher: any) => {
    try {
      const response = await api.get(`/delivery-challans/${voucher.id}`);
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
    if (!voucher || !voucher.id) return;
    try {
      const response = await api.get(`/delivery-challans/${voucher.id}`);
      let fullVoucherData = response.data;
      fullVoucherData.date = fullVoucherData.date ? new Date(fullVoucherData.date).toISOString().split('T')[0] : '';
      setMode("edit");
      reset({
        ...fullVoucherData,
        items: fullVoucherData.items.map((item: any) => ({
          ...item,
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
      const response = await api.get(`/delivery-challans/${voucher.id}`);
      let fullVoucherData = response.data;
      fullVoucherData.date = fullVoucherData.date ? new Date(fullVoucherData.date).toISOString().split('T')[0] : '';
      setMode("view");
      reset({
        ...fullVoucherData,
        items: fullVoucherData.items.map((item: any) => ({
          ...item,
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
    // Simplified submit without discounts/GST/round off
    if (mode === 'create') {
      createMutation.mutate(data, {
        onSuccess: (response) => {
          if (confirm("Challan created successfully. Generate PDF?")) {
            handleGeneratePDF(response);
          }
          refreshMasterData();
        },
        onError: (err) => console.error(err),
      });
    } else if (mode === 'edit') {
      updateMutation.mutate(data, {
        onSuccess: (response) => {
          if (confirm("Challan updated successfully. Generate PDF?")) {
            handleGeneratePDF(response);
          }
          refreshMasterData();
        },
        onError: (err) => console.error(err),
      });
    }
  };

  const handleCancel = () => {
    setMode("view");
    if (voucherData) reset(voucherData);
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
          <Grid size={4}>
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
            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControlLabel
                control={<Checkbox checked={useDifferentShipping} onChange={(e) => setUseDifferentShipping(e.target.checked)} disabled={mode === "view"} />}
                label="Use Different Shipping Address"
              />
            </Box>
          </Grid>
          {useDifferentShipping && (
            <Grid size={12}>
              <TextField
                fullWidth
                label="Shipping Address"
                {...control.register("shipping_address")}
                multiline
                rows={2}
                disabled={mode === "view"}
                sx={voucherFormStyles.field}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          )}
          <Grid size={12}>
            {mode !== "view" && (
              <Box sx={{ display: 'flex', gap: 2, mb: 2, justifyContent: 'flex-start' }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={descriptionEnabled}
                      onChange={(e) => handleToggleDescription(e.target.checked)}
                    />
                  }
                  label="Enable Description"
                />
              </Box>
            )}
            <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell align="center" sx={{ fontSize: 12, fontWeight: "bold", p: 1, width: "30%" }}>Product</TableCell>
                    <TableCell align="center" sx={{ fontSize: 12, fontWeight: "bold", p: 1, width: "100px" }}></TableCell>
                    <TableCell align="center" sx={{ fontSize: 12, fontWeight: "bold", p: 1, textAlign: "center" }}>Qty</TableCell>
                    <TableCell align="center" sx={{ fontSize: 12, fontWeight: "bold", p: 1, textAlign: "center" }}>Rate</TableCell>
                    <TableCell align="center" sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}>GST%</TableCell>
                    <TableCell align="center" sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}>Line Total</TableCell>
                    {mode !== "view" && <TableCell align="center" sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}>Action</TableCell>}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {fields.map((field, index) => (
                    <React.Fragment key={field.id}>
                      <TableRow>
                        <TableCell sx={{ p: 1 }}>
                          <Autocomplete
                            options={productList || []}
                            getOptionLabel={(option: any) => option.product_name || ''}
                            value={selectedProducts[index]}
                            onChange={(_, value) => {
                              setValue(`items.${index}.product_id`, value?.id || null);
                              setValue(`items.${index}.product_name`, value?.product_name || '');
                              setValue(`items.${index}.unit`, value?.unit || '');
                              setValue(`items.${index}.reorder_level`, value?.reorder_level || 0);
                            }}
                            renderInput={(params) => <TextField {...params} label="Product" />}
                            disabled={mode === 'view'}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                          {stockLoading[index] ? (
                            <CircularProgress size={12} />
                          ) : watch(`items.${index}.product_id`) ? (
                            <Typography variant="caption" color={getStockColor(watch(`items.${index}.current_stock`), watch(`items.${index}.reorder_level`))}>
                              {watch(`items.${index}.current_stock`)} {watch(`items.${index}.unit`)}
                            </Typography>
                          ) : null}
                        </TableCell>
                        <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.quantity`, { valueAsNumber: true })}
                            disabled={mode === "view"}
                            size="small"
                            sx={{ width: 120 }}
                            InputProps={{
                              inputProps: { min: 0, step: 1 },
                              endAdornment: <InputAdornment position="end">{watch(`items.${index}.unit`) || ''}</InputAdornment>,
                            }}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                          <TextField
                            type="number"
                            {...control.register(`items.${index}.unit_price`, { valueAsNumber: true })}
                            disabled={mode === "view"}
                            size="small"
                            sx={{ width: 80 }}
                            InputProps={{ inputProps: { min: 0, step: 0.01 } }}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ p: 1 }}>
                          <Autocomplete
                            size="small"
                            options={GST_SLABS}
                            value={watch(`items.${index}.gst_rate`) ?? 18}
                            onChange={(_, value) => {
                              setValue(`items.${index}.gst_rate`, value ?? 18);
                              setValue(`items.${index}.cgst_rate`, isIntrastate ? (value ?? 18) / 2 : 0);
                              setValue(`items.${index}.sgst_rate`, isIntrastate ? (value ?? 18) / 2 : 0);
                              setValue(`items.${index}.igst_rate`, isIntrastate ? 0 : value ?? 18);
                            }}
                            renderInput={(params) => <TextField {...params} size="small" sx={{ width: 60 }} />}
                            disabled={mode === "view"}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ p: 1, fontSize: 14 }}>
                          ₹{computedItems[index]?.amount?.toLocaleString() || "0"}
                        </TableCell>
                        {mode !== "view" && (
                          <TableCell align="center" sx={{ p: 1 }}>
                            <IconButton size="small" onClick={() => remove(index)} color="error">
                              <Remove />
                            </IconButton>
                          </TableCell>
                        )}
                      </TableRow>
                      {descriptionEnabled && (
                        <TableRow>
                          <TableCell colSpan={mode !== "view" ? 7 : 6} sx={{ p: 1 }}>
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
            {mode !== 'view' && (
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                <Fab color="primary" size="small" onClick={() => append({ product_id: null, product_name: '', quantity: 1, unit: '', description: '' })}>
                  <Add />
                </Fab>
              </Box>
            )}
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
          <Button onClick={() => { setRoundOffConfirmOpen(false); if (submitData) onSubmit(submitData); }} variant="contained">Confirm</Button>
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
      <AddProductModal open={showAddProductModal} onClose={() => setShowAddProductModal(false)} onAdd={(newProduct) => { setValue(`items.${addingItemIndex}.product_id`, newProduct.id); setValue(`items.${addingItemIndex}.product_name`, newProduct.product_name); setValue(`items.${addingItemIndex}.unit`, newProduct.unit || ""); setValue(`items.${addingItemIndex}.reorder_level`, newProduct.reorder_level || 0); refreshMasterData(); }} loading={addProductLoading} setLoading={setAddProductLoading} />
      <AddShippingAddressModal open={showShippingModal} onClose={() => setShowShippingModal(false)} loading={addShippingLoading} setLoading={setAddShippingLoading} />
      <VoucherContextMenu contextMenu={contextMenu} voucher={null} voucherType="Delivery Challan" onClose={handleCloseContextMenu} onView={handleViewWithData} onEdit={handleEditWithData} onDelete={handleDelete} onPrint={handleGeneratePDF} onDuplicate={(id) => handleDuplicate(id, voucherList, reset, setMode, "Delivery Challan")} />
    </>
  );
};

export default DeliveryChallanPage;