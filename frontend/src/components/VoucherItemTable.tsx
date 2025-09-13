// frontend/src/components/VoucherItemTable.tsx
// Reusable component for voucher items table, handling append/remove, toggles, stock, and rows.
import React from 'react';
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
  Checkbox, // Added import for Checkbox
  FormControlLabel, // Added import for FormControlLabel
} from '@mui/material';
import { Add, Remove } from '@mui/icons-material';
import ProductAutocomplete from './ProductAutocomplete'; // Assuming this exists; adjust if needed
import { GST_SLABS } from '../utils/voucherUtils'; // Adjust path if needed

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
  handleToggleLineDiscount: (checked: boolean) => void;
  handleToggleTotalDiscount: (checked: boolean) => void;
  handleToggleDescription: (checked: boolean) => void;
  stockLoading: { [key: number]: boolean };
  getStockColor: (stock: number, reorder: number) => string;
  selectedProducts: any[];
  showLineDiscountCheckbox?: boolean; // New prop
  showTotalDiscountCheckbox?: boolean; // New prop
  showDescriptionCheckbox?: boolean; // New prop
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
  handleToggleLineDiscount,
  handleToggleTotalDiscount,
  handleToggleDescription,
  stockLoading,
  getStockColor,
  selectedProducts,
  showLineDiscountCheckbox = false,
  showTotalDiscountCheckbox = false,
  showDescriptionCheckbox = false,
}) => {
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

  return (
    <>
      {mode !== "view" && (showLineDiscountCheckbox || showTotalDiscountCheckbox || showDescriptionCheckbox) && (
        <Box sx={{ display: 'flex', gap: 2, mb: 2, justifyContent: 'flex-start' }}>
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
              {lineDiscountEnabled && (
                <TableCell align="center" sx={{ fontSize: 12, fontWeight: "bold", p: 1 }}>
                  {lineDiscountType === 'percentage' ? 'Disc%' : 'Disc ₹'}
                </TableCell>
              )}
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
                    <ProductAutocomplete
                      value={selectedProducts[index]}
                      onChange={(product) => {
                        setValue(`items.${index}.product_id`, product?.id || null);
                        setValue(`items.${index}.product_name`, product?.product_name || "");
                        setValue(`items.${index}.unit_price`, product?.unit_price || 0);
                        setValue(`items.${index}.original_unit_price`, product?.unit_price || 0);
                        setValue(`items.${index}.gst_rate`, product?.gst_rate ?? 18);
                        setValue(`items.${index}.cgst_rate`, isIntrastate ? (product?.gst_rate ?? 18) / 2 : 0);
                        setValue(`items.${index}.sgst_rate`, isIntrastate ? (product?.gst_rate ?? 18) / 2 : 0);
                        setValue(`items.${index}.igst_rate`, isIntrastate ? 0 : product?.gst_rate ?? 18);
                        setValue(`items.${index}.unit`, product?.unit || "");
                        setValue(`items.${index}.reorder_level`, product?.reorder_level || 0);
                      }}
                      disabled={mode === "view"}
                      size="small"
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
                  {lineDiscountEnabled && (
                    <TableCell align="center" sx={{ p: 1 }}>
                      <TextField
                        type="number"
                        {...control.register(`items.${index}.${lineDiscountType === 'percentage' ? 'discount_percentage' : 'discount_amount'}`, { valueAsNumber: true })}
                        disabled={mode === "view"}
                        size="small"
                        sx={{ width: 60 }}
                        InputProps={{ inputProps: { min: 0, step: lineDiscountType === 'percentage' ? 0.01 : 1 } }}
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
    </>
  );
};

export default VoucherItemTable;