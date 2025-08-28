// frontend/src/components/AddBOMModal.tsx

import React, { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { 
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Grid,
  IconButton,
  CircularProgress,
  Switch,
  FormControlLabel,
  Paper,
  Autocomplete,
  Box
} from '@mui/material';
import { Add, Remove } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';
import { getProducts } from '../services/masterService';

interface BOMComponent {
  component_item_id: number;
  quantity_required: number;
  unit: string;
  unit_cost: number;
  wastage_percentage: number;
  is_optional: boolean;
  sequence: number;
  notes?: string;
}

interface BOM {
  id?: number;
  bom_name: string;
  output_item_id: number;
  output_quantity: number;
  version: string;
  validity_start?: string;
  validity_end?: string;
  description?: string;
  notes?: string;
  material_cost: number;
  labor_cost: number;
  overhead_cost: number;
  is_active: boolean;
  components: BOMComponent[];
}

const defaultBOM: BOM = {
  bom_name: '',
  output_item_id: 0,
  output_quantity: 1.0,
  version: '1.0',
  description: '',
  notes: '',
  material_cost: 0.0,
  labor_cost: 0.0,
  overhead_cost: 0.0,
  is_active: true,
  components: [
    {
      component_item_id: 0,
      quantity_required: 1.0,
      unit: 'PCS',
      unit_cost: 0.0,
      wastage_percentage: 0.0,
      is_optional: false,
      sequence: 1,
      notes: ''
    }
  ]
};

interface AddBOMModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (newBOM: BOM) => void;
  initialData?: BOM;
  mode: 'create' | 'edit';
}

const AddBOMModal: React.FC<AddBOMModalProps> = ({ open, onClose, onAdd, initialData, mode }) => {
  const queryClient = useQueryClient();
  const { control, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<BOM>({
    defaultValues: initialData || defaultBOM
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'components'
  });

  // Fetch products
  const { data: productList, isLoading: isLoadingProducts } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts
  });

  const productOptions = productList || [];

  // Mutation for create/edit
  const mutation = useMutation({
    mutationFn: (data: BOM) => {
      // Clean the data
      const cleanData = {
        ...data,
        output_item_id: data.output_item_id || null,
        output_quantity: Number(data.output_quantity) || 1.0,
        labor_cost: Number(data.labor_cost) || 0.0,
        overhead_cost: Number(data.overhead_cost) || 0.0,
        material_cost: Number(data.material_cost) || 0.0,
        components: data.components.map(comp => ({
          ...comp,
          component_item_id: Number(comp.component_item_id) || null,
          quantity_required: Number(comp.quantity_required) || 1.0,
          unit_cost: Number(comp.unit_cost) || 0.0,
          wastage_percentage: Number(comp.wastage_percentage) || 0.0,
          sequence: Number(comp.sequence) || 0,
          is_optional: Boolean(comp.is_optional)
        })).filter(comp => comp.component_item_id)
      };

      if (mode === 'create') {
        return api.post('/bom', cleanData).then(res => res.data);
      } else {
        return api.put(`/bom/${initialData?.id}`, cleanData).then(res => res.data);
      }
    },
    onSuccess: (newBOM) => {
      queryClient.invalidateQueries({ queryKey: ['boms'] });
      onAdd(newBOM);
      onClose();
      reset(defaultBOM);
    },
    onError: (error: any) => {
      console.error(`Error ${mode === 'create' ? 'creating' : 'updating'} BOM:`, error);
    }
  });

  const onSubmit = (data: BOM) => {
    // Validations
    if (!data.bom_name?.trim()) return;
    if (!data.output_item_id || data.output_item_id === 0) return;
    if (!data.components || data.components.length === 0) return;
    const invalidComponents = data.components.filter(comp => 
      !comp.component_item_id || comp.quantity_required <= 0
    );
    if (invalidComponents.length > 0) return;

    mutation.mutate(data);
  };

  const addComponent = () => {
    append({
      component_item_id: 0,
      quantity_required: 1.0,
      unit: 'PCS',
      unit_cost: 0.0,
      wastage_percentage: 0.0,
      is_optional: false,
      sequence: fields.length + 1,
      notes: ''
    });
  };

  const removeComponent = (index: number) => {
    if (fields.length > 1) {
      remove(index);
    }
  };

  const calculateTotalCost = () => {
    const components = watch('components') || [];
    const materialCost = components.reduce((sum, comp) => {
      const totalQty = comp.quantity_required * (1 + comp.wastage_percentage / 100);
      return sum + (totalQty * comp.unit_cost);
    }, 0);
    
    const laborCost = watch('labor_cost') || 0;
    const overheadCost = watch('overhead_cost') || 0;
    
    return materialCost + laborCost + overheadCost;
  };

  if (isLoadingProducts) {
    return <CircularProgress />;
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>{mode === 'create' ? 'Create BOM' : 'Edit BOM'}</DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid size={12}>
              <Typography variant="h6" gutterBottom>Basic Information</Typography>
            </Grid>
            
            <Grid size={6}>
              <TextField
                {...control.register('bom_name', { required: 'BOM name is required' })}
                label="BOM Name"
                fullWidth
                error={!!errors.bom_name}
                helperText={errors.bom_name?.message}
              />
            </Grid>
            
            <Grid size={3}>
              <TextField
                {...control.register('version', { required: 'Version is required' })}
                label="Version"
                fullWidth
                error={!!errors.version}
                helperText={errors.version?.message}
              />
            </Grid>

            <Grid size={3}>
              <TextField
                {...control.register('output_quantity', { required: 'Output quantity is required', min: 0.01 })}
                label="Output Quantity"
                type="number"
                fullWidth
                error={!!errors.output_quantity}
                helperText={errors.output_quantity?.message}
                InputProps={{ inputProps: { step: 0.01 } }}
              />
            </Grid>

            <Grid size={6}>
              <Autocomplete
                options={productOptions}
                getOptionLabel={(option) => option.product_name || ''}
                value={productOptions.find((p: any) => p.id === watch('output_item_id')) || null}
                onChange={(_, newValue) => setValue('output_item_id', newValue?.id || 0)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Output Item *"
                    error={!!errors.output_item_id}
                    helperText={errors.output_item_id?.message || 'Select the product that will be manufactured'}
                    required
                  />
                )}
              />
            </Grid>

            <Grid size={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={watch('is_active')}
                    onChange={(e) => setValue('is_active', e.target.checked)}
                  />
                }
                label="Active"
              />
            </Grid>

            <Grid size={6}>
              <TextField
                {...control.register('validity_start')}
                label="Validity Start"
                type="date"
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid size={6}>
              <TextField
                {...control.register('validity_end')}
                label="Validity End"
                type="date"
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid size={12}>
              <TextField
                {...control.register('description')}
                label="Description"
                fullWidth
                multiline
                rows={2}
              />
            </Grid>

            <Grid size={12}>
              <TextField
                {...control.register('notes')}
                label="Notes"
                fullWidth
                multiline
                rows={2}
              />
            </Grid>

            {/* Components */}
            <Grid size={12}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 3, mb: 2 }}>
                <Typography variant="h6">Components</Typography>
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={addComponent}
                >
                  Add Component
                </Button>
              </Box>
            </Grid>

            {fields.map((field, index) => (
              <Grid size={12} key={field.id}>
                <Paper sx={{ p: 2, mb: 2 }}>
                  <Grid container spacing={2}>
                    <Grid size={4}>
                      <Autocomplete
                        options={productOptions}
                        getOptionLabel={(option) => option.product_name || ''}
                        value={productOptions.find((p: any) => p.id === watch(`components.${index}.component_item_id`)) || null}
                        onChange={(_, newValue) => setValue(`components.${index}.component_item_id`, newValue?.id || 0)}
                        renderInput={(params) => (
                          <TextField
                            {...params}
                            label="Component Item *"
                            size="small"
                            required
                            error={!watch(`components.${index}.component_item_id`)}
                            helperText={!watch(`components.${index}.component_item_id`) ? 'Component item is required' : ''}
                          />
                        )}
                      />
                    </Grid>
                    
                    <Grid size={2}>
                      <TextField
                        {...control.register(`components.${index}.quantity_required` as const, { 
                          required: 'Quantity is required', 
                          min: { value: 0.01, message: 'Quantity must be greater than 0' }
                        })}
                        label="Quantity *"
                        type="number"
                        fullWidth
                        size="small"
                        error={!!errors.components?.[index]?.quantity_required}
                        helperText={errors.components?.[index]?.quantity_required?.message}
                        InputProps={{ inputProps: { step: 0.01, min: 0.01 } }}
                      />
                    </Grid>

                    <Grid size={1}>
                      <TextField
                        {...control.register(`components.${index}.unit` as const)}
                        label="Unit"
                        fullWidth
                        size="small"
                      />
                    </Grid>

                    <Grid size={2}>
                      <TextField
                        {...control.register(`components.${index}.unit_cost` as const, { min: 0 })}
                        label="Unit Cost"
                        type="number"
                        fullWidth
                        size="small"
                        InputProps={{ inputProps: { step: 0.01 } }}
                      />
                    </Grid>

                    <Grid size={2}>
                      <TextField
                        {...control.register(`components.${index}.wastage_percentage` as const, { min: 0, max: 100 })}
                        label="Wastage %"
                        type="number"
                        fullWidth
                        size="small"
                        InputProps={{ inputProps: { step: 0.1 } }}
                      />
                    </Grid>

                    <Grid size={1}>
                      <IconButton
                        onClick={() => removeComponent(index)}
                        color="error"
                        disabled={fields.length === 1}
                      >
                        <Remove />
                      </IconButton>
                    </Grid>

                    <Grid size={12}>
                      <TextField
                        {...control.register(`components.${index}.notes` as const)}
                        label="Component Notes"
                        fullWidth
                        size="small"
                      />
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            ))}

            {/* Costing */}
            <Grid size={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>Costing</Typography>
            </Grid>

            <Grid size={4}>
              <TextField
                {...control.register('labor_cost', { min: 0 })}
                label="Labor Cost"
                type="number"
                fullWidth
                InputProps={{ inputProps: { step: 0.01 } }}
              />
            </Grid>

            <Grid size={4}>
              <TextField
                {...control.register('overhead_cost', { min: 0 })}
                label="Overhead Cost"
                type="number"
                fullWidth
                InputProps={{ inputProps: { step: 0.01 } }}
              />
            </Grid>

            <Grid size={4}>
              <TextField
                label="Total Cost"
                value={calculateTotalCost().toFixed(2)}
                fullWidth
                disabled
                InputProps={{
                  readOnly: true,
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={mutation.isPending}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="contained" 
            disabled={mutation.isPending}
          >
            {mutation.isPending ? <CircularProgress size={20} /> : (mode === 'create' ? 'Create' : 'Update')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AddBOMModal;