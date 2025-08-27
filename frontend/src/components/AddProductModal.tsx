// frontend/src/components/AddProductModal.tsx

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
  Grid as Grid,
} from '@mui/material';
import { useForm } from 'react-hook-form';

interface AddProductModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (productData: any) => Promise<void>;
  loading?: boolean;
  initialName?: string;
}

interface ProductFormData {
  name: string;
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

const AddProductModal: React.FC<AddProductModalProps> = ({
  open,
  onClose,
  onAdd,
  loading = false,
  initialName = ''
}) => {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<ProductFormData>({
    defaultValues: {
      name: initialName,
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

  React.useEffect(() => {
    if (open && initialName) {
      reset({ 
        name: initialName,
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

  const onSubmit = async (data: ProductFormData) => {
    try {
      // Remove empty fields to match backend schema (consistent with customer modal)
      const allowedFields = ['name', 'hsn_code', 'part_number', 'unit', 'unit_price', 'gst_rate', 'is_gst_inclusive', 'reorder_level', 'description', 'is_manufactured'];
      const cleanData = Object.fromEntries(
        Object.entries(data).filter(([key, value]) => {
          if (key === 'unit_price' || key === 'gst_rate' || key === 'reorder_level') {
            return true;  // Send 0 values for numbers as they are meaningful defaults
          }
          return allowedFields.includes(key) && value != null && String(value).trim() !== '';
        })
      );
      await onAdd(cleanData);
      reset();
      onClose();  // Close modal on success (consistent with other modals)
    } catch (error) {
      console.error('Error adding product:', error);
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
                {...register('name', { required: 'Product name is required' })}
                error={!!errors.name}
                helperText={errors.name?.message}
                disabled={loading}
              />
            </Grid>
            
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="HSN Code"
                {...register('hsn_code')}
                disabled={loading}
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
                  min: { value: 0, message: 'Price must be positive' },
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
            
            <Grid size={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                {...register('description')}
                disabled={loading}
              />
            </Grid>
            
            <Grid size={12}>
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