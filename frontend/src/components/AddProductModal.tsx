// frontend/src/components/AddProductModal.tsx

import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControlLabel,
  Checkbox,
  Typography,
  CircularProgress,
  Box,
  Grid,
  Autocomplete,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  InputAdornment,
  IconButton,
} from "@mui/material";
import SearchIcon from '@mui/icons-material/Search';
import { useForm } from "react-hook-form";
import { useQuery } from "@tanstack/react-query";
import { getProducts, hsnSearch } from "../services/masterService";
import { toast } from "react-toastify";
interface AddProductModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (_data: any) => Promise<void>;
  onUpdate?: (_data: any) => Promise<void>;
  loading?: boolean;
  initialName?: string;
  productData?: any;
  mode?: 'add' | 'edit';
}
interface ProductFormData {
  product_name: string;
  hsn_code: string;
  part_number: string;
  unit: string;
  unit_price: number;
  gst_rate: number;
  is_gst_inclusive: boolean;
  reorder_level: number;
  description: string;
  is_manufactured: boolean;
}
interface Product {
  product_name: string;
  hsn_code: string;
  part_number: string;
  unit: string;
  gst_rate: number;
}
interface HsnResult {
  hsn_code: string;
  description: string;
  gst_rate: number;
}
const AddProductModal: React.FC<AddProductModalProps> = ({
  open,
  onClose,
  onAdd,
  onUpdate,
  loading = false,
  initialName = "",
  productData,
  mode = 'add',
}) => {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ProductFormData>({
    defaultValues: {
      product_name: initialName,
      hsn_code: "",
      part_number: "",
      unit: "PCS",
      unit_price: 0,
      gst_rate: 18,
      is_gst_inclusive: false,
      reorder_level: 0,
      description: "",
      is_manufactured: false,
    },
  });
  // Watch form values
  const watchedProductName = watch("product_name");
  const watchedHsnCode = watch("hsn_code");
  const watchedDescription = watch("description");
  // Fetch all products
  const { data: allProducts = [], isLoading: productsLoading } = useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
    enabled: open,
    staleTime: 300000,
  });
  // Create unique HSN codes list from existing products
  const uniqueHsnCodes = React.useMemo(() => {
    const hsnSet = new Set<string>();
    allProducts.forEach((product: Product) => {
      if (product.hsn_code && product.hsn_code.trim()) {
        hsnSet.add(product.hsn_code.trim());
      }
    });
    return Array.from(hsnSet).sort();
  }, [allProducts]);
  // Create product suggestions based on HSN code
  const getProductsByHsn = React.useCallback(
    (hsnCode: string): Product[] => {
      if (!hsnCode.trim()) {
        return [];
      }
      return allProducts.filter(
        (product: Product) =>
          product.hsn_code &&
          product.hsn_code.toLowerCase().includes(hsnCode.toLowerCase()),
      );
    },
    [allProducts],
  );
  // Create HSN suggestions based on product name
  const getHsnByProductName = React.useCallback(
    (productName: string) => {
      if (!productName.trim()) {
        return [];
      }
      const matchingProducts = allProducts.filter((product: Product) =>
        product.product_name.toLowerCase().includes(productName.toLowerCase()),
      );
      const hsnCodes = matchingProducts
        .map((product: Product) => product.hsn_code)
        .filter((hsn: string) => hsn && hsn.trim())
        .filter(
          (hsn: string, index: number, array: string[]) =>
            array.indexOf(hsn) === index,
        ); // unique
      return hsnCodes;
    },
    [allProducts],
  );
  // State for HSN suggestion popup
  const [hsnPopupOpen, setHsnPopupOpen] = React.useState(false);
  const [suggestedHsns, setSuggestedHsns] = React.useState<string[]>([]);
  const [hsnSearchLoading, setHsnSearchLoading] = React.useState(false);
  const [hsnApiSuggestions, setHsnApiSuggestions] = React.useState<HsnResult[]>([]);
  React.useEffect(() => {
    if (open) {
      if (mode === 'edit' && productData) {
        reset({
          product_name: productData.product_name,
          hsn_code: productData.product_hsn_code || "",
          part_number: productData.product_part_number || "",
          unit: productData.unit,
          unit_price: productData.unit_price,
          gst_rate: productData.gst_rate,
          is_gst_inclusive: productData.is_gst_inclusive || false,
          reorder_level: productData.reorder_level || 0,
          description: productData.description || "",
          is_manufactured: productData.is_manufactured || false,
        });
      } else {
        reset({
          product_name: initialName,
          hsn_code: "",
          part_number: "",
          unit: "PCS",
          unit_price: 0,
          gst_rate: 18,
          is_gst_inclusive: false,
          reorder_level: 0,
          description: "",
          is_manufactured: false,
        });
      }
    }
  }, [open, initialName, reset, mode, productData]);
  const onSubmit = async (productData: ProductFormData) => {
    try {
      // Remove empty fields to match backend schema
      const allowedFields = [
        "product_name",
        "hsn_code",
        "part_number",
        "unit",
        "unit_price",
        "gst_rate",
        "is_gst_inclusive",
        "reorder_level",
        "description",
        "is_manufactured",
      ];
      const cleanData = Object.fromEntries(
        Object.entries(productData).filter(([key, value]) => {
          if (
            key === "unit_price" ||
            key === "gst_rate" ||
            key === "reorder_level"
          ) {
            return true; // Send 0 values for numbers as they are meaningful defaults
          }
          return (
            allowedFields.includes(key) &&
            value !== null &&
            String(value).trim() !== ""
          );
        }),
      );
      if (mode === 'edit') {
        await onUpdate!({ ...cleanData, id: productData.id });
      } else {
        await onAdd(cleanData);
      }
      reset();
      onClose(); // Close modal on success
    } catch (err: any) {
      let errorMsg = "Error adding product";
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          errorMsg = detail.map((e: any) => `${e.loc.join('.')} - ${e.msg}`).join('\n');
        } else if (typeof detail === "string") {
          errorMsg = detail;
        }
      } else if (err.message) {
        errorMsg = err.message;
      }
      toast.error(errorMsg);
      console.error("Error adding product:", err);
    }
  };
  const handleClose = () => {
    reset();
    onClose();
  };
  // Handler for searching HSN via icon click
  const handleHsnSearchClick = async () => {
    if (!watchedHsnCode || watchedHsnCode.length < 2) {
      toast.info("Enter at least 2 characters in HSN Code to search");
      return;
    }
    setHsnSearchLoading(true);
    try {
      const results = await hsnSearch({ queryKey: ["hsn-search", watchedHsnCode, 10] });
      if (results.length === 0) {
        toast.info("No HSN codes found - enter manually");
      } else if (results.length === 1) {
        // Auto-fill if single result
        const selected = results[0];
        setValue("hsn_code", selected.hsn_code);
        setValue("gst_rate", normalizeGstRate(selected.gst_rate));
        if (selected.description && !watchedDescription && !watchedProductName) {
          setValue("description", selected.description);
        }
        toast.success("HSN details auto-filled");
      } else {
        // Show popup if multiple
        setHsnApiSuggestions(results);
        setHsnPopupOpen(true);
      }
    } catch (err: any) {
      toast.error("Failed to search HSN: " + (err.message || "Unknown error"));
    } finally {
      setHsnSearchLoading(false);
    }
  };
  // Handler for searching product name via icon click (for HSN suggestions)
  const handleProductSearchClick = () => {
    if (!watchedProductName || watchedProductName.length < 3) {
      toast.info("Enter at least 3 characters in Product Name to search");
      return;
    }
    const suggested = getHsnByProductName(watchedProductName);
    if (suggested.length === 0) {
      toast.info("No matching HSN found in existing products");
    } else if (suggested.length === 1 && !watchedHsnCode) {
      // Auto-populate if exactly one
      setValue("hsn_code", suggested[0]);
      toast.success("HSN auto-suggested from similar products");
    } else if (suggested.length > 1 && !watchedHsnCode) {
      // Show popup if multiple
      setSuggestedHsns(suggested);
      setHsnPopupOpen(true);
    } else {
      toast.info("HSN already entered - clear to suggest");
    }
  };
  // Handler for selecting HSN from API popup
  const handleApiHsnSelect = (selected: HsnResult) => {
    setValue("hsn_code", selected.hsn_code);
    setValue("gst_rate", normalizeGstRate(selected.gst_rate));
    if (selected.description && !watchedDescription && !watchedProductName) {
      setValue("description", selected.description);
    }
    setHsnPopupOpen(false);
  };
  // Handler for selecting HSN from local popup
  const handleLocalHsnSelect = (hsn: string) => {
    setValue("hsn_code", hsn);
    // Fetch GST rate via API for selected HSN
    hsnSearch({ queryKey: ["hsn-search", hsn, 1] }).then((results) => {
      if (results.length > 0) {
        setValue("gst_rate", normalizeGstRate(results[0].gst_rate));
      }
    }).catch((err) => {
      console.error("Failed to fetch GST for selected HSN:", err);
      toast.error("Failed to fetch GST rate - enter manually");
    });
    setHsnPopupOpen(false);
  };
  // Normalize GST rate (handle both fraction and percentage)
  const normalizeGstRate = (rate: number): number => {
    return rate > 1 ? rate : rate * 100;
  };
  return (
    <>
      <Dialog
        open={open}
        onClose={handleClose}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { minHeight: "500px" },
        }}
      >
        <DialogTitle>
          <Typography variant="h6" component="div">
            {mode === 'edit' ? 'Edit Product' : 'Add New Product'}
          </Typography>
        </DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Product Name"
                  {...register("product_name", {
                    required: "Product name is required",
                  })}
                  error={!!errors.product_name}
                  helperText={errors.product_name?.message}
                  disabled={loading}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={handleProductSearchClick}
                          disabled={loading || productsLoading}
                          aria-label="Search for HSN suggestions"
                        >
                          <SearchIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="HSN Code"
                  {...register("hsn_code")}
                  disabled={loading}
                  helperText={
                    watchedHsnCode &&
                    getProductsByHsn(watchedHsnCode).length > 0
                      ? `Found ${getProductsByHsn(watchedHsnCode).length} product(s) with this HSN`
                      : undefined
                  }
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={handleHsnSearchClick}
                          disabled={loading || hsnSearchLoading}
                          aria-label="Search HSN code"
                        >
                          {hsnSearchLoading ? (
                            <CircularProgress size={20} />
                          ) : (
                            <SearchIcon />
                          )}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Part Number"
                  {...register("part_number")}
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Unit"
                  {...register("unit", { required: "Unit is required" })}
                  error={!!errors.unit}
                  helperText={errors.unit?.message}
                  disabled={loading}
                  placeholder="e.g., PCS, KG, METER"
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Unit Price"
                  type="number"
                  inputProps={{ step: 0.01 }}
                  {...register("unit_price", {
                    required: "Unit price is required",
                    min: { value: 0.01, message: "Price must be greater than 0" },
                    valueAsNumber: true,
                  })}
                  error={!!errors.unit_price}
                  helperText={errors.unit_price?.message}
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="GST Rate (%)"
                  type="number"
                  inputProps={{ step: 0.01 }}
                  {...register("gst_rate", {
                    min: { value: 0, message: "GST rate must be positive" },
                    max: { value: 100, message: "GST rate cannot exceed 100%" },
                    valueAsNumber: true,
                  })}
                  error={!!errors.gst_rate}
                  helperText={errors.gst_rate?.message}
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Reorder Level"
                  type="number"
                  {...register("reorder_level", {
                    min: { value: 0, message: "Reorder level must be positive" },
                    valueAsNumber: true,
                  })}
                  error={!!errors.reorder_level}
                  helperText={errors.reorder_level?.message}
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  {...register("description")}
                  disabled={loading}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Box sx={{ display: "flex", gap: 2 }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        {...register("is_gst_inclusive")}
                        disabled={loading}
                      />
                    }
                    label="GST Inclusive"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        {...register("is_manufactured")}
                        disabled={loading}
                      />
                    }
                    label="Manufactured Item"
                  />
                </Box>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 2 }}>
            <Button onClick={handleClose} disabled={loading} color="inherit">
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? (mode === 'edit' ? "Updating..." : "Adding...") : (mode === 'edit' ? "Update Product" : "Add Product")}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
      {/* HSN Suggestion Popup (for both local and API) */}
      <Dialog
        open={hsnPopupOpen}
        onClose={() => setHsnPopupOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Select HSN Code</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {hsnApiSuggestions.length > 0 
              ? "Multiple HSN codes found from search. Select one:" 
              : "Multiple HSN codes found for similar products. Select one:"}
          </Typography>
          <List>
            {hsnApiSuggestions.length > 0 
              ? hsnApiSuggestions.map((option) => (
                  <ListItem key={option.hsn_code} disablePadding>
                    <ListItemButton onClick={() => handleApiHsnSelect(option)}>
                      <ListItemText 
                        primary={`${option.hsn_code} (${normalizeGstRate(option.gst_rate)}%)`}
                        secondary={option.description} 
                      />
                    </ListItemButton>
                  </ListItem>
                ))
              : suggestedHsns.map((hsn) => (
                  <ListItem key={hsn} disablePadding>
                    <ListItemButton onClick={() => handleLocalHsnSelect(hsn)}>
                      <ListItemText 
                        primary={hsn}
                        secondary={`Used in ${getProductsByHsn(hsn).length} similar products`} 
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHsnPopupOpen(false)} color="inherit">
            Cancel (Enter Manually)
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};
export default AddProductModal;