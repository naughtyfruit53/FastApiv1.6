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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Card,
  CardContent
} from '@mui/material';
import { 
  Add, 
  Remove,
  Visibility, 
  Edit, 
  Delete, 
  Save,
  Cancel
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../../lib/api';
import { getProducts } from '../../../services/masterService';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';

interface MaterialIssueItem {
  product_id: number;
  quantity: number;
  unit: string;
  unit_price: number;
  total_amount: number;
  notes?: string;
}

interface MaterialIssue {
  id?: number;
  voucher_number?: string;
  date: string;
  manufacturing_order_id?: number;
  issued_to_department?: string;
  issued_to_employee?: string;
  purpose: string;
  total_amount: number;
  notes?: string;
  items: MaterialIssueItem[];
}

const defaultValues: MaterialIssue = {
  date: new Date().toISOString().slice(0, 10),
  purpose: 'production',
  total_amount: 0,
  items: [
    {
      product_id: 0,
      quantity: 1,
      unit: 'PCS',
      unit_price: 0,
      total_amount: 0
    }
  ]
};

const MaterialRequisition: React.FC = () => {
  const router = useRouter();
  const { id, mode: queryMode } = router.query;
  const [mode, setMode] = useState<'create' | 'edit' | 'view'>((queryMode as 'create' | 'edit' | 'view') || 'create');
  const [selectedId, setSelectedId] = useState<number | null>(id ? Number(id) : null);
  const [contextMenu, setContextMenu] = useState<{ mouseX: number; mouseY: number; voucher: any } | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredVouchers, setFilteredVouchers] = useState<any[]>([]);
  const queryClient = useQueryClient();

  const { control, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<MaterialIssue>({
    defaultValues
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items'
  });

  // Fetch material issues
  const { data: issueList, isLoading: isLoadingList } = useQuery({
    queryKey: ['material-issues'],
    queryFn: () => api.get('/material-issues').then(res => res.data),
  });

  // Fetch products
  const { data: productList } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts
  });

  // Fetch manufacturing orders
  const { data: manufacturingOrders } = useQuery({
    queryKey: ['manufacturing-orders'],
    queryFn: () => api.get('/manufacturing-orders').then(res => res.data),
  });

  // Fetch specific material issue
  const { data: issueData, isLoading: isFetching } = useQuery({
    queryKey: ['material-issue', selectedId],
    queryFn: () => api.get(`/material-issues/${selectedId}`).then(res => res.data),
    enabled: !!selectedId
  });

  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ['nextMaterialIssueNumber'],
    queryFn: () => api.get('/material-issues/next-number').then(res => res.data),
    enabled: mode === 'create',
  });

  const sortedIssues = issueList ? [...issueList].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ) : [];

  const latestIssues = sortedIssues.slice(0, 10);
  const productOptions = productList || [];

  useEffect(() => {
    if (mode === 'create' && nextVoucherNumber) {
      setValue('voucher_number', nextVoucherNumber);
    } else if (issueData) {
      reset(issueData);
    } else if (mode === 'create') {
      reset(defaultValues);
    }
  }, [issueData, mode, reset, nextVoucherNumber, setValue]);

  // Calculate totals
  useEffect(() => {
    const items = watch('items') || [];
    const total = items.reduce((sum, item) => sum + (item.total_amount || 0), 0);
    setValue('total_amount', total);
  }, [watch('items'), setValue]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: MaterialIssue) => api.post('/material-issues', data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ['material-issues'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue('voucher_number', newNextNumber);
    },
    onError: (error: any) => {
      console.error('Error creating material issue:', error);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: MaterialIssue }) => 
      api.put(`/material-issues/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['material-issues'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
    },
    onError: (error: any) => {
      console.error('Error updating material issue:', error);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/material-issues/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['material-issues'] });
    },
    onError: (error: any) => {
      console.error('Error deleting material issue:', error);
    }
  });

  const onSubmit = (data: MaterialIssue) => {
    if (mode === 'create') {
      createMutation.mutate(data);
    } else if (mode === 'edit' && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    }
  };

  const handleEdit = (issue: any) => {
    setSelectedId(issue.id);
    setMode('edit');
  };

  const handleView = (issue: any) => {
    setSelectedId(issue.id);
    setMode('view');
  };

  const handleContextMenuClose = () => {
    setContextMenu(null);
  };

  const handleDeleteIssue = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this material issue?')) {
      deleteMutation.mutate(id);
    }
  };

  const addItem = () => {
    append({
      product_id: 0,
      quantity: 1,
      unit: 'PCS',
      unit_price: 0,
      total_amount: 0
    });
  };

  const removeItem = (index: number) => {
    if (fields.length > 1) {
      remove(index);
    }
  };

  const updateItemTotal = (index: number) => {
    const quantity = watch(`items.${index}.quantity`) || 0;
    const unitPrice = watch(`items.${index}.unit_price`) || 0;
    const total = quantity * unitPrice;
    setValue(`items.${index}.total_amount`, total);
  };

  return (
    <Container maxWidth="xl">
      <Grid container spacing={3}>
        {/* Left Panel - Issue List */}
        <Grid size={5}>
          <Box>
            <VoucherHeaderActions
              mode={mode}
              voucherType="Material Requisition"
              voucherRoute="/vouchers/Manufacturing-Vouchers/material-requisition"
              currentId={selectedId || undefined}
              onModeChange={setMode}
              onModalOpen={() => {}}
              voucherList={sortedIssues}
              onEdit={handleEdit}
              onView={handleView}
              isLoading={isLoadingList}
            />
            
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>Recent Requisitions</Typography>
              <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>Issue #</TableCell>
                      <TableCell>Purpose</TableCell>
                      <TableCell>Department</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {latestIssues.map((issue) => (
                      <TableRow 
                        key={issue.id}
                        hover
                        onClick={() => handleEdit(issue)}
                        sx={{ cursor: 'pointer' }}
                        onContextMenu={(e) => {
                          e.preventDefault();
                          setContextMenu({
                            mouseX: e.clientX - 2,
                            mouseY: e.clientY - 4,
                            voucher: issue,
                          });
                        }}
                      >
                        <TableCell>{issue.voucher_number}</TableCell>
                        <TableCell>{issue.purpose}</TableCell>
                        <TableCell>{issue.issued_to_department || 'N/A'}</TableCell>
                        <TableCell>{issue.total_amount?.toFixed(2) || '0.00'}</TableCell>
                        <TableCell>{new Date(issue.date).toLocaleDateString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </Box>
        </Grid>

        {/* Right Panel - Form */}
        <Grid size={7}>
          <form onSubmit={handleSubmit(onSubmit)}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                {mode === 'create' ? 'Create Material Requisition' : 
                 mode === 'edit' ? 'Edit Material Requisition' : 'View Material Requisition'}
              </Typography>

              <Grid container spacing={2}>
                {/* Header Information */}
                <Grid size={4}>
                  <TextField
                    {...control.register('voucher_number')}
                    label="Requisition Number"
                    fullWidth
                    disabled
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                <Grid size={4}>
                  <TextField
                    {...control.register('date', { required: true })}
                    label="Date"
                    type="date"
                    fullWidth
                    error={!!errors.date}
                    disabled={mode === 'view'}
                    size="small"
                    InputLabelProps={{ shrink: true }}
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                <Grid size={4}>
                  <TextField
                    {...control.register('purpose')}
                    label="Purpose"
                    fullWidth
                    disabled={mode === 'view'}
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                <Grid size={6}>
                  <Autocomplete
                    options={manufacturingOrders || []}
                    getOptionLabel={(option) => `${option.voucher_number} - ${option.bom?.bom_name || 'Unknown'}`}
                    value={manufacturingOrders?.find((mo: any) => mo.id === watch('manufacturing_order_id')) || null}
                    onChange={(_, newValue) => setValue('manufacturing_order_id', newValue?.id || 0)}
                    disabled={mode === 'view'}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Manufacturing Order (Optional)"
                        size="small"
                        sx={{ '& .MuiInputBase-root': { height: 27 } }}
                      /> */}
                    )}
                  /> */}
                </Grid>

                <Grid size={6}>
                  <TextField
                    {...control.register('issued_to_department')}
                    label="Department"
                    fullWidth
                    disabled={mode === 'view'}
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                <Grid size={6}>
                  <TextField
                    {...control.register('issued_to_employee')}
                    label="Issued To (Employee)"
                    fullWidth
                    disabled={mode === 'view'}
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                <Grid size={6}>
                  <TextField
                    label="Total Amount"
                    value={watch('total_amount')?.toFixed(2) || '0.00'}
                    fullWidth
                    disabled
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                {/* Items Section */}
                <Grid size={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2, mb: 1 }}>
                    <Typography variant="h6">Items</Typography>
                    {mode !== 'view' && (
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<Add />}
                        onClick={addItem}
                      >
                        Add Item
                      </Button>
                    )}
                  </Box>
                </Grid>

                {fields.map((field, index) => (
                  <Grid size={12} key={field.id}>
                    <Paper variant="outlined" sx={{ p: 2, mb: 1 }}>
                      <Grid container spacing={2} alignItems="center">
                        <Grid size={4}>
                          <Autocomplete
                            options={productOptions}
                            getOptionLabel={(option) => option.product_name || ''}
                            value={productOptions.find((p: any) => p.id === watch(`items.${index}.product_id`)) || null}
                            onChange={(_, newValue) => {
                              setValue(`items.${index}.product_id`, newValue?.id || 0);
                              if (newValue) {
                                setValue(`items.${index}.unit`, newValue.unit || 'PCS');
                                setValue(`items.${index}.unit_price`, newValue.unit_price || 0);
                                updateItemTotal(index);
                              }
                            }}
                            disabled={mode === 'view'}
                            renderInput={(params) => (
                              <TextField
                                {...params}
                                label="Product"
                                size="small"
                              /> */}
                            )}
                          /> */}
                        </Grid>

                        <Grid size={2}>
                          <TextField
                            {...control.register(`items.${index}.quantity` as const, { 
                              required: true, 
                              min: 0.01,
                              onChange: () => updateItemTotal(index)
                            })}
                            label="Quantity"
                            type="number"
                            fullWidth
                            size="small"
                            disabled={mode === 'view'}
                            InputProps={{ inputProps: { step: 0.01 } }}
                          /> */}
                        </Grid>

                        <Grid size={1}>
                          <TextField
                            {...control.register(`items.${index}.unit` as const)}
                            label="Unit"
                            fullWidth
                            size="small"
                            disabled={mode === 'view'}
                          /> */}
                        </Grid>

                        <Grid size={2}>
                          <TextField
                            {...control.register(`items.${index}.unit_price` as const, { 
                              min: 0,
                              onChange: () => updateItemTotal(index)
                            })}
                            label="Unit Price"
                            type="number"
                            fullWidth
                            size="small"
                            disabled={mode === 'view'}
                            InputProps={{ inputProps: { step: 0.01 } }}
                          /> */}
                        </Grid>

                        <Grid size={2}>
                          <TextField
                            label="Total"
                            value={watch(`items.${index}.total_amount`)?.toFixed(2) || '0.00'}
                            fullWidth
                            size="small"
                            disabled
                          /> */}
                        </Grid>

                        <Grid size={1}>
                          {mode !== 'view' && (
                            <IconButton
                              onClick={() => removeItem(index)}
                              color="error"
                              size="small"
                              disabled={fields.length === 1}
                            >
                              <Remove />
                            </IconButton>
                          )}
                        </Grid>

                        <Grid size={12}>
                          <TextField
                            {...control.register(`items.${index}.notes` as const)}
                            label="Item Notes"
                            fullWidth
                            size="small"
                            disabled={mode === 'view'}
                          /> */}
                        </Grid>
                      </Grid>
                    </Paper>
                  </Grid>
                ))}

                <Grid size={12}>
                  <TextField
                    {...control.register('notes')}
                    label="General Notes"
                    fullWidth
                    multiline
                    rows={2}
                    disabled={mode === 'view'}
                    size="small"
                  /> */}
                </Grid>

                {/* Action Buttons */}
                {mode !== 'view' && (
                  <Grid size={12}>
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
                      <Button
                        variant="outlined"
                        onClick={() => {
                          setMode('create');
                          setSelectedId(null);
                          reset(defaultValues);
                        }}
                      >
                        Cancel
                      </Button>
                      <Button
                        type="submit"
                        variant="contained"
                        disabled={createMutation.isPending || updateMutation.isPending}
                      >
                        {createMutation.isPending || updateMutation.isPending ? (
                          <CircularProgress size={20} />
                        ) : (
                          mode === 'create' ? 'Create Requisition' : 'Update Requisition'
                        )}
                      </Button>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Paper>
          </form>
        </Grid>
      </Grid>

      {/* Context Menu */}
      <VoucherContextMenu
        voucherType="Material Requisition"
        contextMenu={contextMenu}
        onClose={handleContextMenuClose}
        onEdit={() => {
          if (contextMenu?.voucher) {
            handleEdit(contextMenu.voucher);
          }
          setContextMenu(null);
        }}
        onView={() => {
          if (contextMenu?.voucher) {
            handleView(contextMenu.voucher);
          }
          setContextMenu(null);
        }}
        onDelete={() => {
          if (contextMenu?.voucher) {
            handleDeleteIssue(contextMenu.voucher.id);
          }
          setContextMenu(null);
        }}
      />
    </Container>
  );
};

export default MaterialRequisition;