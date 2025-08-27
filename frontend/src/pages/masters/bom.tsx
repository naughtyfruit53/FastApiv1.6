import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useForm, useFieldArray } from 'react-hook-form';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Grid, 
  IconButton, 
  Alert, 
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
  Tooltip,
  Chip
} from '@mui/material';
import { 
  Add, 
  Remove, 
  Visibility, 
  Edit, 
  Delete, 
  Save,
  Cancel,
  ContentCopy
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../lib/api';
import { getProducts } from '../../services/masterService';

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

const BOMManagement: React.FC = () => {
  const router = useRouter();
  const [mode, setMode] = useState<'list' | 'create' | 'edit' | 'view'>('list');
  const [selectedBOM, setSelectedBOM] = useState<BOM | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const queryClient = useQueryClient();

  const { control, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<BOM>({
    defaultValues: defaultBOM
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'components'
  });

  // Fetch BOMs
  const { data: bomList, isLoading: isLoadingBOMs } = useQuery({
    queryKey: ['boms'],
    queryFn: () => api.get('/bom').then(res => res.data),
  });

  // Fetch products
  const { data: productList } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts
  });

  const productOptions = productList || [];

  // Create BOM mutation
  const createMutation = useMutation({
    mutationFn: (data: BOM) => {
      // Clean the data to prevent validation errors
      const cleanData = {
        ...data,
        // Ensure required fields have valid values
        output_item_id: data.output_item_id || null,
        output_quantity: Number(data.output_quantity) || 1.0,
        labor_cost: Number(data.labor_cost) || 0.0,
        overhead_cost: Number(data.overhead_cost) || 0.0,
        material_cost: Number(data.material_cost) || 0.0,
        // Clean components array
        components: data.components.map(comp => ({
          ...comp,
          component_item_id: Number(comp.component_item_id) || null,
          quantity_required: Number(comp.quantity_required) || 1.0,
          unit_cost: Number(comp.unit_cost) || 0.0,
          wastage_percentage: Number(comp.wastage_percentage) || 0.0,
          sequence: Number(comp.sequence) || 0,
          is_optional: Boolean(comp.is_optional)
        })).filter(comp => comp.component_item_id) // Remove components without valid item_id
      };
      
      return api.post('/bom', cleanData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boms'] });
      setMode('list');
      reset(defaultBOM);
    },
    onError: (error: any) => {
      console.error('Error creating BOM:', error);
      // Show detailed error message for debugging
      if (error.response?.data?.detail) {
        console.error('Validation error:', error.response.data.detail);
      }
    }
  });

  // Update BOM mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: BOM }) => {
      // Clean the data to prevent validation errors
      const cleanData = {
        ...data,
        // Ensure required fields have valid values
        output_item_id: data.output_item_id || null,
        output_quantity: Number(data.output_quantity) || 1.0,
        labor_cost: Number(data.labor_cost) || 0.0,
        overhead_cost: Number(data.overhead_cost) || 0.0,
        material_cost: Number(data.material_cost) || 0.0,
        // Clean components array
        components: data.components.map(comp => ({
          ...comp,
          component_item_id: Number(comp.component_item_id) || null,
          quantity_required: Number(comp.quantity_required) || 1.0,
          unit_cost: Number(comp.unit_cost) || 0.0,
          wastage_percentage: Number(comp.wastage_percentage) || 0.0,
          sequence: Number(comp.sequence) || 0,
          is_optional: Boolean(comp.is_optional)
        })).filter(comp => comp.component_item_id) // Remove components without valid item_id
      };
      
      return api.put(`/bom/${id}`, cleanData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boms'] });
      setMode('list');
      reset(defaultBOM);
      setSelectedBOM(null);
    },
    onError: (error: any) => {
      console.error('Error updating BOM:', error);
      // Show detailed error message for debugging
      if (error.response?.data?.detail) {
        console.error('Validation error:', error.response.data.detail);
      }
    }
  });

  // Delete BOM mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/bom/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boms'] });
      setShowDeleteDialog(false);
      setSelectedBOM(null);
    },
    onError: (error: any) => {
      console.error('Error deleting BOM:', error);
    }
  });

  const onSubmit = (data: BOM) => {
    // Validate required fields
    if (!data.bom_name?.trim()) {
      console.error('BOM name is required');
      return;
    }
    
    if (!data.output_item_id || data.output_item_id === 0) {
      console.error('Output item must be selected');
      return;
    }
    
    if (!data.components || data.components.length === 0) {
      console.error('At least one component is required');
      return;
    }
    
    // Validate components
    const invalidComponents = data.components.filter(comp => 
      !comp.component_item_id || comp.component_item_id === 0 ||
      !comp.quantity_required || comp.quantity_required <= 0
    );
    
    if (invalidComponents.length > 0) {
      console.error('All components must have valid items and quantities');
      return;
    }
    
    if (mode === 'create') {
      createMutation.mutate(data);
    } else if (mode === 'edit' && selectedBOM?.id) {
      updateMutation.mutate({ id: selectedBOM.id, data });
    }
  };

  const handleEdit = (bom: BOM) => {
    setSelectedBOM(bom);
    reset(bom);
    setMode('edit');
  };

  const handleView = (bom: BOM) => {
    setSelectedBOM(bom);
    reset(bom);
    setMode('view');
  };

  const handleDelete = (bom: BOM) => {
    setSelectedBOM(bom);
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (selectedBOM?.id) {
      deleteMutation.mutate(selectedBOM.id);
    }
  };

  const handleCancel = () => {
    setMode('list');
    setSelectedBOM(null);
    reset(defaultBOM);
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

  if (mode === 'list') {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Bill of Materials (BOM)</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setMode('create')}
            >
              Create BOM
            </Button>
          </Box>

          {isLoadingBOMs ? (
            <CircularProgress />
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>BOM Name</TableCell>
                    <TableCell>Version</TableCell>
                    <TableCell>Output Item</TableCell>
                    <TableCell>Output Qty</TableCell>
                    <TableCell>Total Cost</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {bomList?.map((bom: any) => (
                    <TableRow key={bom.id}>
                      <TableCell>{bom.bom_name}</TableCell>
                      <TableCell>{bom.version}</TableCell>
                      <TableCell>{bom.output_item?.product_name || 'Unknown'}</TableCell>
                      <TableCell>{bom.output_quantity}</TableCell>
                      <TableCell>{bom.total_cost.toFixed(2)}</TableCell>
                      <TableCell>
                        <Chip 
                          label={bom.is_active ? 'Active' : 'Inactive'} 
                          color={bom.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton onClick={() => handleView(bom)} size="small">
                          <Visibility />
                        </IconButton>
                        <IconButton onClick={() => handleEdit(bom)} size="small">
                          <Edit />
                        </IconButton>
                        <IconButton onClick={() => handleDelete(bom)} size="small" color="error">
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>

        {/* Delete Confirmation Dialog */}
        <Dialog open={showDeleteDialog} onClose={() => setShowDeleteDialog(false)}>
          <DialogTitle>Confirm Delete</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete the BOM "{selectedBOM?.bom_name}"?
              This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowDeleteDialog(false)}>Cancel</Button>
            <Button onClick={confirmDelete} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    );
  }

  // Form view (create/edit/view)
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            {mode === 'create' ? 'Create BOM' : mode === 'edit' ? 'Edit BOM' : 'View BOM'}
          </Typography>
          <Button
            variant="outlined"
            onClick={handleCancel}
            startIcon={<Cancel />}
          >
            Back to List
          </Button>
        </Box>

        <form onSubmit={handleSubmit(onSubmit)}>
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
                disabled={mode === 'view'}
              />
            </Grid>
            
            <Grid size={3}>
              <TextField
                {...control.register('version', { required: 'Version is required' })}
                label="Version"
                fullWidth
                error={!!errors.version}
                helperText={errors.version?.message}
                disabled={mode === 'view'}
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
                disabled={mode === 'view'}
                InputProps={{ inputProps: { step: 0.01 } }}
              />
            </Grid>

            <Grid size={6}>
              <Autocomplete
                options={productOptions}
                getOptionLabel={(option) => option.product_name || ''}
                value={productOptions.find((p: any) => p.id === watch('output_item_id')) || null}
                onChange={(_, newValue) => setValue('output_item_id', newValue?.id || 0)}
                disabled={mode === 'view'}
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
                    disabled={mode === 'view'}
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
                disabled={mode === 'view'}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid size={6}>
              <TextField
                {...control.register('validity_end')}
                label="Validity End"
                type="date"
                fullWidth
                disabled={mode === 'view'}
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
                disabled={mode === 'view'}
              />
            </Grid>

            <Grid size={12}>
              <TextField
                {...control.register('notes')}
                label="Notes"
                fullWidth
                multiline
                rows={2}
                disabled={mode === 'view'}
              />
            </Grid>

            {/* Components */}
            <Grid size={12}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 3, mb: 2 }}>
                <Typography variant="h6">Components</Typography>
                {mode !== 'view' && (
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={addComponent}
                  >
                    Add Component
                  </Button>
                )}
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
                        disabled={mode === 'view'}
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
                        disabled={mode === 'view'}
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
                        disabled={mode === 'view'}
                      />
                    </Grid>

                    <Grid size={2}>
                      <TextField
                        {...control.register(`components.${index}.unit_cost` as const, { min: 0 })}
                        label="Unit Cost"
                        type="number"
                        fullWidth
                        size="small"
                        disabled={mode === 'view'}
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
                        disabled={mode === 'view'}
                        InputProps={{ inputProps: { step: 0.1 } }}
                      />
                    </Grid>

                    <Grid size={1}>
                      {mode !== 'view' && (
                        <IconButton
                          onClick={() => removeComponent(index)}
                          color="error"
                          disabled={fields.length === 1}
                        >
                          <Remove />
                        </IconButton>
                      )}
                    </Grid>

                    <Grid size={12}>
                      <TextField
                        {...control.register(`components.${index}.notes` as const)}
                        label="Component Notes"
                        fullWidth
                        size="small"
                        disabled={mode === 'view'}
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
                disabled={mode === 'view'}
                InputProps={{ inputProps: { step: 0.01 } }}
              />
            </Grid>

            <Grid size={4}>
              <TextField
                {...control.register('overhead_cost', { min: 0 })}
                label="Overhead Cost"
                type="number"
                fullWidth
                disabled={mode === 'view'}
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

            {/* Action Buttons */}
            {mode !== 'view' && (
              <Grid size={12}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 3 }}>
                  <Button
                    variant="outlined"
                    onClick={handleCancel}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<Save />}
                    disabled={createMutation.isPending || updateMutation.isPending}
                  >
                    {createMutation.isPending || updateMutation.isPending ? (
                      <CircularProgress size={20} />
                    ) : (
                      mode === 'create' ? 'Create BOM' : 'Update BOM'
                    )}
                  </Button>
                </Box>
              </Grid>
            )}
          </Grid>
        </form>
      </Box>
    </Container>
  );
};

export default BOMManagement;