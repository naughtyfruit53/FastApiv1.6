// frontend/src/components/VoucherItemTable.tsx
import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  Autocomplete,
  IconButton,
  Typography,
  CircularProgress,
  Fab,
  InputAdornment,
  Box,
  Checkbox,
  FormControlLabel,
} from "@mui/material";
import { Add, Remove } from "@mui/icons-material";
import ProductAutocomplete from "./ProductAutocomplete";
import { GST_SLABS, normalizeGstRate } from "../utils/voucherUtils";
import { getStock } from "../services/masterService";

interface VoucherItemTableProps {
  fields: any[];
  control: any;
  watch: any;
  setValue: any;
  remove: (index: number) => void;
  append: (item: any) => void;
  mode: string;
  isIntrastate: boolean;
  computedItems: any[];
  lineDiscountEnabled: boolean;
  lineDiscountType: string;
  totalDiscountEnabled: boolean;
  descriptionEnabled: boolean;
  additionalChargesEnabled: boolean;
  handleToggleLineDiscount: (checked: boolean) => void;
  handleToggleTotalDiscount: (checked: boolean) => void;
  handleToggleDescription: (checked: boolean) => void;
  handleToggleAdditionalCharges: (checked: boolean) => void;
  stockLoading: { [key: number]: boolean };
  getStockColor: (stock: number, reorder: number) => string;
  selectedProducts: any[];
  showLineDiscountCheckbox?: boolean;
  showTotalDiscountCheckbox?: boolean;
  showDescriptionCheckbox?: boolean;
  showAdditionalChargesCheckbox?: boolean;
  showDeliveryStatus?: boolean; // For PO: show delivered/pending quantities
  voucherType?: string; // Added to identify GRN-specific rendering
}

const VoucherItemTable: React.FC<VoucherItemTableProps> = ({
  fields,
  control,
  watch,
  setValue,
  remove,
  append,
  mode,
  isIntrastate,
  computedItems,
  lineDiscountEnabled,
  lineDiscountType,
  totalDiscountEnabled,
  descriptionEnabled,
  additionalChargesEnabled,
  handleToggleLineDiscount,
  handleToggleTotalDiscount,
  handleToggleDescription,
  handleToggleAdditionalCharges,
  stockLoading,
  getStockColor,
  selectedProducts,
  showLineDiscountCheckbox = false,
  showTotalDiscountCheckbox = false,
  showDescriptionCheckbox = false,
  showAdditionalChargesCheckbox = false,
  showDeliveryStatus = false,
  voucherType = '',
}) => {
  const handleAddItem = () => {
    append({
      product_id: null,
      product_name: "",
      quantity: 0.0,
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
      description: "",
      ordered_quantity: 0, // Added for GRN
      received_quantity: 0, // Added for GRN
      accepted_quantity: 0, // Added for GRN
      rejected_quantity: 0, // Added for GRN
    });
  };

  const handleProductChange = async (index: number, product: any) => {
    console.log("[VoucherItemTable] handleProductChange called:", { index, product });
    setValue(`items.${index}.product_id`, product?.id || null);
    setValue(`items.${index}.product_name`, product?.product_name || "");
    setValue(`items.${index}.unit_price`, product?.unit_price || 0);
    setValue(`items.${index}.original_unit_price`, product?.unit_price || 0);
    const normalizedGst = normalizeGstRate(product?.gst_rate ?? 18);
    setValue(`items.${index}.gst_rate`, normalizedGst);
    setValue(`items.${index}.cgst_rate`, isIntrastate ? normalizedGst / 2 : 0);
    setValue(`items.${index}.sgst_rate`, isIntrastate ? normalizedGst / 2 : 0);
    setValue(`items.${index}.igst_rate`, isIntrastate ? 0 : normalizedGst);
    setValue(`items.${index}.unit`, product?.unit || "");
    setValue(`items.${index}.reorder_level`, product?.reorder_level || 0);
    setValue(`items.${index}.current_stock`, 0);

    if (product?.id) {
      stockLoading[index] = true;
      try {
        const res = await getStock({
          queryKey: ["", { product_id: product.id }],
        });
        console.log(`[VoucherItemTable] Stock fetch for product ${product.id}:`, {
          response: res,
          responseType: typeof res,
          isArray: Array.isArray(res),
          productId: product.id,
          stockData: res[0],
        });
        if (!Array.isArray(res) || res.length === 0) {
          console.warn(`[VoucherItemTable] Invalid stock response for product ${product.id}:`, res);
          setValue(`items.${index}.current_stock`, 0);
          return;
        }
        const stockData = res[0] || { quantity: 0 };
        const stockQuantity = parseFloat(stockData.quantity || 0);
        console.log(`[VoucherItemTable] Setting current_stock for index ${index}:`, {
          stockQuantity,
          productId: product.id,
        });
        setValue(`items.${index}.current_stock`, stockQuantity);
      } catch (err) {
        console.error(`[VoucherItemTable] Failed to fetch stock for product ${product.id}:`, err);
        setValue(`items.${index}.current_stock`, 0);
      } finally {
        stockLoading[index] = false;
      }
    }
  };

  return (
    <>
      {mode !== "view" &&
        (showLineDiscountCheckbox ||
          showTotalDiscountCheckbox ||
          showDescriptionCheckbox ||
          showAdditionalChargesCheckbox) && (
          <Box sx={{ display: "flex", gap: 2, mb: 2, justifyContent: "flex-start" }}>
            {showLineDiscountCheckbox && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={lineDiscountEnabled}
                    onChange={(e) => handleToggleLineDiscount(e.target.checked)}
                  />
                }
                label="Enable Line Discount"
              />
            )}
            {showTotalDiscountCheckbox && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={totalDiscountEnabled}
                    onChange={(e) => handleToggleTotalDiscount(e.target.checked)}
                  />
                }
                label="Enable Total Discount"
              />
            )}
            {showDescriptionCheckbox && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={descriptionEnabled}
                    onChange={(e) => handleToggleDescription(e.target.checked)}
                  />
                }
                label="Enable Description"
              />
            )}
            {showAdditionalChargesCheckbox && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={additionalChargesEnabled}
                    onChange={(e) => handleToggleAdditionalCharges(e.target.checked)}
                  />
                }
                label="Enable Additional Charges"
              />
            )}
          </Box>
        )}
      <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell
                align="center"
                sx={{ fontSize: 12, fontWeight: "bold", p: 1, width: "30%" }}
              >
                Product
              </TableCell>
              <TableCell
                align="center"
                sx={{ fontSize: 12, fontWeight: "bold", p: 1, width: "100px" }}
              >
                {/* Stock header removed as per requirements, stock values still shown in cells */}
              </TableCell>
              {voucherType === 'goods-receipt-notes' ? (
                <>
                  <TableCell
                    align="center"
                    sx={{ fontSize: 12, fontWeight: "bold", p: 1, textAlign: "center" }}
                  >
                    Ordered Qty
                  </TableCell>
                  <TableCell
                    align="center"
                    sx={{ fontSize: 12, fontWeight: "bold", p: 1, textAlign: "center" }}
                  >
                    Received Qty
                  </TableCell>
                  <TableCell
                    align="center"
                    sx={{ fontSize: 12, fontWeight: "bold", p: 1, textAlign: "center" }}
                  >
                    Accepted Qty
                  </TableCell>
                  <TableCell
                    align="center"
                    sx={{ fontSize: 12, fontWeight: "bold", p: 1, textAlign: "center" }}
                  >
                    Rejected Qty
                  </TableCell>
                </>
              ) : (
                <TableCell
                  align="center"
                  sx={{ fontSize: 12, fontWeight: "bold", p: 1, textAlign: "center" }}
                >
                  Qty
                </TableCell>
              )}
              {showDeliveryStatus && (
                <>
                  <TableCell
                    align="center"
                    sx={{ fontSize: 12, fontWeight: "bold", p: 1, textAlign: "center" }}
                  >
                    Delivered
                  </TableCell>
                  <TableCell
                    align="center"
                    sx={{ fontSize: 12, fontWeight: "bold", p: 1, textAlign: "center" }}
                  >
                    Pending
                  </TableCell>
                </>
              )}
              <TableCell
                align="center"
                sx={{ fontSize: 12, fontWeight: "bold", p: 1, textAlign: "center" }}
              >
                Rate
              </TableCell>
              {lineDiscountEnabled && (
                <TableCell
                  align="center"
                  sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}
                >
                  {lineDiscountType === "percentage" ? "Disc%" : "Disc ₹"}
                </TableCell>
              )}
              <TableCell
                align="center"
                sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}
              >
                GST%
              </TableCell>
              <TableCell
                align="center"
                sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}
              >
                Line Total
              </TableCell>
              {mode !== "view" && (
                <TableCell
                  align="center"
                  sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}
                >
                  Action
                </TableCell>
              )}
            </TableRow>
          </TableHead>
          <TableBody>
            {fields.map((field, index) => (
              <React.Fragment key={field.id}>
                <TableRow>
                  <TableCell sx={{ p: 1 }}>
                    <ProductAutocomplete
                      value={
                        selectedProducts[index] || {
                          id: watch(`items.${index}.product_id`),
                          product_name: watch(`items.${index}.product_name`) || "",
                        }
                      }
                      onChange={(product) => handleProductChange(index, product)}
                      disabled={mode === "view" || voucherType === 'goods-receipt-notes'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                    {stockLoading[index] ? (
                      <CircularProgress size={12} />
                    ) : watch(`items.${index}.product_id`) ? (
                      <Typography
                        variant="caption"
                        color={getStockColor(
                          watch(`items.${index}.current_stock`) || 0,
                          watch(`items.${index}.reorder_level`) || 0,
                        )}
                      >
                        {(watch(`items.${index}.current_stock`) || 0).toFixed(2)}{" "}
                        {watch(`items.${index}.unit`) || ""}
                      </Typography>
                    ) : null}
                  </TableCell>
                  {voucherType === 'goods-receipt-notes' ? (
                    <>
                      <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                        <TextField
                          type="number"
                          value={watch(`items.${index}.ordered_quantity`) || 0}
                          disabled
                          size="small"
                          sx={{ width: 120 }}
                          InputProps={{
                            inputProps: { min: 0, step: 0.01 },
                            endAdornment: (
                              <InputAdornment position="end">
                                {watch(`items.${index}.unit`) || ""}
                              </InputAdornment>
                            ),
                          }}
                        />
                      </TableCell>
                      <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                        <TextField
                          type="number"
                          {...control.register(`items.${index}.received_quantity`, {
                            valueAsNumber: true,
                          })}
                          disabled={mode === "view"}
                          size="small"
                          sx={{ width: 120 }}
                          InputProps={{
                            inputProps: { min: 0, step: 0.01 },
                            endAdornment: (
                              <InputAdornment position="end">
                                {watch(`items.${index}.unit`) || ""}
                              </InputAdornment>
                            ),
                          }}
                        />
                      </TableCell>
                      <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                        <TextField
                          type="number"
                          {...control.register(`items.${index}.accepted_quantity`, {
                            valueAsNumber: true,
                          })}
                          disabled={mode === "view"}
                          size="small"
                          sx={{ width: 120 }}
                          InputProps={{
                            inputProps: { min: 0, step: 0.01 },
                            endAdornment: (
                              <InputAdornment position="end">
                                {watch(`items.${index}.unit`) || ""}
                              </InputAdornment>
                            ),
                          }}
                        />
                      </TableCell>
                      <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                        <TextField
                          type="number"
                          {...control.register(`items.${index}.rejected_quantity`, {
                            valueAsNumber: true,
                          })}
                          disabled={mode === "view"}
                          size="small"
                          sx={{ width: 120 }}
                          InputProps={{
                            inputProps: { min: 0, step: 0.01 },
                            endAdornment: (
                              <InputAdornment position="end">
                                {watch(`items.${index}.unit`) || ""}
                              </InputAdornment>
                            ),
                          }}
                        />
                      </TableCell>
                    </>
                  ) : (
                    <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                      <TextField
                        type="number"
                        {...control.register(`items.${index}.quantity`, {
                          valueAsNumber: true,
                        })}
                        disabled={mode === "view"}
                        size="small"
                        sx={{ width: 120 }}
                        InputProps={{
                          inputProps: { min: 0, step: 0.01 },
                          endAdornment: (
                            <InputAdornment position="end">
                              {watch(`items.${index}.unit`) || ""}
                            </InputAdornment>
                          ),
                        }}
                      />
                    </TableCell>
                  )}
                  {showDeliveryStatus && (
                    <>
                      <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                        <Typography variant="caption" sx={{ fontSize: 12 }}>
                          {(watch(`items.${index}.delivered_quantity`) || 0).toFixed(2)}{" "}
                          {watch(`items.${index}.unit`) || ""}
                        </Typography>
                      </TableCell>
                      <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                        <Typography variant="caption" sx={{ fontSize: 12 }}>
                          {(watch(`items.${index}.pending_quantity`) || 0).toFixed(2)}{" "}
                          {watch(`items.${index}.unit`) || ""}
                        </Typography>
                      </TableCell>
                    </>
                  )}
                  <TableCell align="center" sx={{ p: 1, textAlign: "center" }}>
                    <TextField
                      type="number"
                      {...control.register(`items.${index}.unit_price`, {
                        valueAsNumber: true,
                      })}
                      disabled={mode === "view"}
                      size="small"
                      sx={{ width: 80 }}
                      InputProps={{ inputProps: { min: 0, step: 0.01 } }}
                    />
                  </TableCell>
                  {lineDiscountEnabled && (
                    <TableCell align="center" sx={{ p: 1 }}>
                      <TextField
                        type="number"
                        {...control.register(
                          `items.${index}.${
                            lineDiscountType === "percentage"
                              ? "discount_percentage"
                              : "discount_amount"
                          }`,
                          { valueAsNumber: true },
                        )}
                        disabled={mode === "view"}
                        size="small"
                        sx={{ width: 60 }}
                        InputProps={{
                          inputProps: {
                            min: 0,
                            step: lineDiscountType === "percentage" ? 0.01 : 1,
                          },
                        }}
                      />
                    </TableCell>
                  )}
                  <TableCell align="center" sx={{ p: 1 }}>
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
                        <TextField {...params} size="small" sx={{ width: 60 }} />
                      )}
                      disabled={mode === "view"}
                    />
                  </TableCell>
                  <TableCell align="center" sx={{ p: 1, fontSize: 14 }}>
                    ₹{computedItems[index]?.amount?.toLocaleString() || "0"}
                  </TableCell>
                  {mode !== "view" && (
                    <TableCell align="center" sx={{ p: 1 }}>
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
                    <TableCell
                      colSpan={mode !== "view" ? 8 : 7}
                      sx={{ p: 1 }}
                    >
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
      {mode !== "view" && voucherType !== 'goods-receipt-notes' && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 1 }}>
          <Fab color="primary" size="small" onClick={handleAddItem}>
            <Add />
          </Fab>
        </Box>
      )}
    </>
  );
};

export default VoucherItemTable;