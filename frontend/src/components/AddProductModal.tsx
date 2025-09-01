import React from 'react';
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
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { getProducts } from '../services/masterService';
interface AddProductModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (_data: any) => Promise<void>;
  loading?: boolean;
  initialName?: string;
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
  unit: string;
  gst_rate: number;
}
const AddProductModal: React.FC<AddProductModalProps> = ({
  open,
  onClose,
  onAdd,
  loading = false,
  initialName = ''
}) => {
  const { register, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm<ProductFormData>({
    defaultValues: {
      product_name: initialName,
      hsn_code: '',
      part_number: '',
      unit: 'PCS',
      unit_price: 0,
      gst_rate: 18,
      is_gst_inclusive: false,
      reorder_level: 0,
      description: '',
      is_manufactured: false,
    }
  });
  // Watch form values for bidirectional updates
  const watchedProductName = watch('product_name');
  const watchedHsnCode = watch('hsn_code');
  // Fetch all products for autocomplete functionality
  const { data: allProducts = [], isLoading: productsLoading } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts,
    enabled: open, // Only fetch when modal is open
    staleTime: 300000, // 5 minutes cache
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
  const getProductsByHsn = React.useCallback((hsnCode: string): Product[] => {
    if (!hsnCode.trim()) {return [];}
    return allProducts.filter((product: Product) => 
      product.hsn_code && product.hsn_code.toLowerCase().includes(hsnCode.toLowerCase())
    );
  }, [allProducts]);
  // Create HSN suggestions based on product name
  const getHsnByProductName = React.useCallback((productName: string) => {
    if (!productName.trim()) {return [];}
    const matchingProducts = allProducts.filter((product: Product) =>
      product.product_name.toLowerCase().includes(productName.toLowerCase())
    );
    const hsnCodes = matchingProducts
      .map((product: Product) => product.hsn_code)
      .filter((hsn: string) => hsn && hsn.trim())
      .filter((hsn: string, index: number, array: string[]) => array.indexOf(hsn) === index); // unique
    return hsnCodes;
  }, [allProducts]);
  React.useEffect(() => {
    if (open && initialName) {
      reset({ 
        product_name: initialName,
        hsn_code: '',
        part_number: '',
        unit: 'PCS',
        unit_price: 0,
        gst_rate: 18,
        is_gst_inclusive: false,
        reorder_level: 0,
        description: '',
        is_manufactured: false,
      });
    }
  }, [open, initialName, reset]);
  // Bidirectional auto-population logic
  React.useEffect(() => {
    // When product name changes, suggest HSN codes
    if (watchedProductName && watchedProductName.length > 2) {
      const suggestedHsns = getHsnByProductName(watchedProductName);
      if (suggestedHsns.length === 1 && !watchedHsnCode) {
        // Auto-populate if there's exactly one matching HSN and HSN field is empty
        setValue('hsn_code', suggestedHsns[0]);
      }
    }
  }, [watchedProductName, watchedHsnCode, getHsnByProductName, setValue]);
  React.useEffect(() => {
    // When HSN code changes, suggest product info
    if (watchedHsnCode && watchedHsnCode.length > 2) {
      const matchingProducts = getProductsByHsn(watchedHsnCode);
      if (matchingProducts.length > 0 && !watchedProductName) {
        // If there's a strong match and product name is empty, suggest the most common unit/gst_rate
        const commonUnit = matchingProducts[0].unit;
        const commonGstRate = matchingProducts[0].gst_rate;
        if (commonUnit && commonUnit !== 'PCS') {
          setValue('unit', commonUnit);
        }
        if (commonGstRate && commonGstRate !== 18) {
          setValue('gst_rate', commonGstRate);
        }
      }
    }
  }, [watchedHsnCode, watchedProductName, getProductsByHsn, setValue]);
  const onSubmit = async (productData: ProductFormData) => {
    try {
      // Remove empty fields to match backend schema to match backend schema
      const allowedFields = ['product_name', 'hsn_code', 'part_number', 'unit', 'unit_price', 'gst_rate', 'is_gst_inclusive', 'reorder_level', 'description', 'is_manufactured'];
      const cleanData = Object.fromEntries(
        Object.entries(productData).filter(([key, value]) => {
          if (key === 'unit_price' || key === 'gst_rate' || key === 'reorder_level') {
            return true;  // Send 0 values for numbers as they are meaningful defaults
          }
          return allowedFields.includes(key) && value !== null && String(value).trim() !== '';
        })
      );
      await onAdd(cleanData);
      reset();
      onClose();  // Close modal on success
    } catch (err) {
      console.error(msg, err);
    }
  };
  const handleClose = () => {
    reset();
    onClose();
  };
  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '500px' }
      }}
    >
      <DialogTitle>
        <Typography variant="h6" component="div">
          Add New Product
        </Typography>
      </DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Product Name"
                {...register('product_name', { required: 'Product name is required' })}
                error={!!errors.product_name}
                helperText={
                  errors.product_name?.message || 
                  (watchedProductName && watchedProductName.length > 2 && getHsnByProductName(watchedProductName).length > 0
                    ? `Suggested HSN: ${getHsnByProductName(watchedProductName).slice(0, 3).join(', ')}`
                    : undefined)
                }
                disabled={loading}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <Autocomplete
                freeSolo
                options={uniqueHsnCodes}
                value={watchedHsnCode || ''}
                onInputChange={(_, newValue) => {
                  setValue('hsn_code', newValue || '');
                }}
                onChange={(_, newValue) => {
                  setValue('hsn_code', newValue || '');
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    fullWidth
                    label="HSN Code"
                    placeholder="Search or enter HSN code..."
                    disabled={loading}
                    helperText={
                      watchedHsnCode && getProductsByHsn(watchedHsnCode).length > 0
                        ? `Found ${getProductsByHsn(watchedHsnCode).length} product(s) with this HSN`
                        : undefined
                    }
                    InputProps={{
                      ...params.InputProps,
                      endAdornment: (
                        <>
                          {productsLoading ? <CircularProgress color="inherit" size={20} /> : null}
                          {params.InputProps.endAdornment}
                        </>
                      ),
                    }}
                  />
                )}
                renderOption={(props, option) => (
                  <Box component="li" {...props}>
                    <Box sx={{ width: '100%' }}>
                      <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                        {option}
                      </Typography>
                      {getProductsByHsn(option).length > 0 && (
                        <Typography variant="caption" color="text.secondary">
                          {getProductsByHsn(option).length} product(s): {getProductsByHsn(option).slice(0, 2).map((p: Product) => p.product_name).join(', ')}
                          {getProductsByHsn(option).length > 2 && '...'}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                )}
                noOptionsText="No HSN codes found"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Part Number"
                {...register('part_number')}
                disabled={loading}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Unit"
                {...register('unit', { required: 'Unit is required' })}
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
                {...register('unit_price', { 
                  required: 'Unit price is required',
                  min: { value: 0.01, message: 'Price must be greater than 0' },
                  valueAsNumber: true 
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
                {...register('gst_rate', { 
                  min: { value: 0, message: 'GST rate must be positive' },
                  max: { value: 100, message: 'GST rate cannot exceed 100%' },
                  valueAsNumber: true 
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
                {...register('reorder_level', { 
                  min: { value: 0, message: 'Reorder level must be positive' },
                  valueAsNumber: true 
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
                {...register('description')}
                disabled={loading}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      {...register('is_gst_inclusive')}
                      disabled={loading}
                    />
                  }
                  label="GST Inclusive"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      {...register('is_manufactured')}
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
          <Button 
            onClick={handleClose}
            disabled={loading}
            color="inherit"
          >
            Cancel
          </Button>
          <Button 
            type="submit"
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Adding...' : 'Add Product'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};
export default AddProductModal;