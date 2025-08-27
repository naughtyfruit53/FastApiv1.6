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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { 
  Add, 
  Visibility, 
  Edit, 
  Delete, 
  Save,
  Cancel,
  PlayArrow,
  Stop,
  CheckCircle,
  Schedule
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../../lib/api';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';

interface ManufacturingOrder {
  id?: number;
  voucher_number?: string;
  date: string;
  bom_id: number;
  planned_quantity: number;
  produced_quantity?: number;
  scrap_quantity?: number;
  planned_start_date?: string;
  planned_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  production_status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  production_department?: string;
  production_location?: string;
  notes?: string;
  total_amount: number;
}

const defaultValues: ManufacturingOrder = {
  date: new Date().toISOString().slice(0, 10),
  bom_id: 0,
  planned_quantity: 1,
  produced_quantity: 0,
  scrap_quantity: 0,
  production_status: 'planned',
  priority: 'medium',
  total_amount: 0
};

const ProductionOrder: React.FC = () => {
  const router = useRouter();
  const { id, mode: queryMode } = router.query;
  const [mode, setMode] = useState<'create' | 'edit' | 'view'>((queryMode as 'create' | 'edit' | 'view') || 'create');
  const [selectedId, setSelectedId] = useState<number | null>(id ? Number(id) : null);
  const [contextMenu, setContextMenu] = useState<{ mouseX: number; mouseY: number; voucher: any } | null>(null);
  const [showFullModal, setShowFullModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [filteredVouchers, setFilteredVouchers] = useState<any[]>([]);
  const [selectedBOM, setSelectedBOM] = useState<any>(null);
  const [bomCostBreakdown, setBomCostBreakdown] = useState<any>(null);
  const queryClient = useQueryClient();

  const { control, handleSubmit, reset, setValue, watch, formState: { errors } } = useForm<ManufacturingOrder>({
    defaultValues
  });

  const watchedBomId = watch('bom_id');
  const watchedQuantity = watch('planned_quantity');

  // Fetch manufacturing orders
  const { data: orderList, isLoading: isLoadingList } = useQuery({
    queryKey: ['manufacturing-orders'],
    queryFn: () => api.get('/manufacturing-orders').then(res => res.data),
  });

  // Fetch BOMs
  const { data: bomList } = useQuery({
    queryKey: ['boms'],
    queryFn: () => api.get('/bom').then(res => res.data),
  });

  // Fetch specific manufacturing order
  const { data: orderData, isLoading: isFetching } = useQuery({
    queryKey: ['manufacturing-order', selectedId],
    queryFn: () => api.get(`/manufacturing-orders/${selectedId}`).then(res => res.data),
    enabled: !!selectedId
  });

  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ['nextManufacturingOrderNumber'],
    queryFn: () => api.get('/manufacturing-orders/next-number').then(res => res.data),
    enabled: mode === 'create',
  });

  // Fetch BOM cost breakdown
  const { data: costBreakdown } = useQuery({
    queryKey: ['bom-cost-breakdown', watchedBomId, watchedQuantity],
    queryFn: () => api.get(`/bom/${watchedBomId}/cost-breakdown?production_quantity=${watchedQuantity}`).then(res => res.data),
    enabled: !!watchedBomId && watchedQuantity > 0,
  });

  const sortedOrders = orderList ? [...orderList].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ) : [];

  const latestOrders = sortedOrders.slice(0, 10);

  useEffect(() => {
    if (mode === 'create' && nextVoucherNumber) {
      setValue('voucher_number', nextVoucherNumber);
    } else if (orderData) {
      reset(orderData);
    } else if (mode === 'create') {
      reset(defaultValues);
    }
  }, [orderData, mode, reset, nextVoucherNumber, setValue]);

  useEffect(() => {
    if (watchedBomId && bomList) {
      const bom = bomList.find((b: any) => b.id === watchedBomId);
      setSelectedBOM(bom);
    }
  }, [watchedBomId, bomList]);

  useEffect(() => {
    if (costBreakdown) {
      setBomCostBreakdown(costBreakdown);
      setValue('total_amount', costBreakdown.cost_breakdown.total_cost);
    }
  }, [costBreakdown, setValue]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: ManufacturingOrder) => api.post('/manufacturing-orders', data),
    onSuccess: async (newOrder) => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue('voucher_number', newNextNumber);
    },
    onError: (error: any) => {
      console.error('Error creating manufacturing order:', error);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ManufacturingOrder }) => 
      api.put(`/manufacturing-orders/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
    },
    onError: (error: any) => {
      console.error('Error updating manufacturing order:', error);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/manufacturing-orders/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
    },
    onError: (error: any) => {
      console.error('Error deleting manufacturing order:', error);
    }
  });

  const onSubmit = (data: ManufacturingOrder) => {
    if (mode === 'create') {
      createMutation.mutate(data);
    } else if (mode === 'edit' && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    }
  };

  const handleEdit = (order: any) => {
    setSelectedId(order.id);
    setMode('edit');
  };

  const handleView = (order: any) => {
    setSelectedId(order.id);
    setMode('view');
  };

  const handleContextMenuClose = () => {
    setContextMenu(null);
  };

  const handleDeleteOrder = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this manufacturing order?')) {
      deleteMutation.mutate(id);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planned': return 'default';
      case 'in_progress': return 'warning';
      case 'completed': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'success';
      case 'medium': return 'default';
      case 'high': return 'warning';
      case 'urgent': return 'error';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="xl">
      <Grid container spacing={3}>
        {/* Left Panel - Order List */}
        <Grid size={5}>
          <Box>
            <VoucherHeaderActions
              mode={mode}
              voucherType="Production Order"
              voucherRoute="/vouchers/Manufacturing-Vouchers/production-order"
              currentId={selectedId || undefined}
              onModeChange={setMode}
              onModalOpen={() => setShowFullModal(true)}
              voucherList={sortedOrders}
              onEdit={handleEdit}
              onView={handleView}
              isLoading={isLoadingList}
            />
            
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>Recent Orders</Typography>
              <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>Order #</TableCell>
                      <TableCell>BOM</TableCell>
                      <TableCell>Qty</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Priority</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {latestOrders.map((order) => (
                      <TableRow 
                        key={order.id}
                        hover
                        onClick={() => handleEdit(order)}
                        sx={{ cursor: 'pointer' }}
                        onContextMenu={(e) => {
                          e.preventDefault();
                          setContextMenu({
                            mouseX: e.clientX - 2,
                            mouseY: e.clientY - 4,
                            voucher: order,
                          });
                        }}
                      >
                        <TableCell>{order.voucher_number}</TableCell>
                        <TableCell>{order.bom?.bom_name || 'N/A'}</TableCell>
                        <TableCell>{order.planned_quantity}</TableCell>
                        <TableCell>
                          <Chip 
                            label={order.production_status} 
                            color={getStatusColor(order.production_status)}
                            size="small"
                          /> */}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={order.priority} 
                            color={getPriorityColor(order.priority)}
                            size="small"
                          /> */}
                        </TableCell>
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
                {mode === 'create' ? 'Create Production Order' : 
                 mode === 'edit' ? 'Edit Production Order' : 'View Production Order'}
              </Typography>

              <Grid container spacing={2}>
                {/* Basic Information */}
                <Grid size={4}>
                  <TextField
                    {...control.register('voucher_number')}
                    label="Order Number"
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
                  <FormControl fullWidth size="small">
                    <InputLabel>Priority</InputLabel>
                    <Select
                      {...control.register('priority')}
                      value={watch('priority')}
                      onChange={(e) => setValue('priority', e.target.value as 'low' | 'medium' | 'high' | 'urgent')}
                      disabled={mode === 'view'}
                      sx={{ height: 27 }}
                    >
                      <MenuItem value="low">Low</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                      <MenuItem value="urgent">Urgent</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                {/* BOM Selection */}
                <Grid size={6}>
                  <Autocomplete
                    options={bomList || []}
                    getOptionLabel={(option) => `${option.bom_name} v${option.version}`}
                    value={bomList?.find((b: any) => b.id === watch('bom_id')) || null}
                    onChange={(_, newValue) => setValue('bom_id', newValue?.id || 0)}
                    disabled={mode === 'view'}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Bill of Materials"
                        error={!!errors.bom_id}
                        size="small"
                        sx={{ '& .MuiInputBase-root': { height: 27 } }}
                      /> */}
                    )}
                  /> */}
                </Grid>

                <Grid size={3}>
                  <TextField
                    {...control.register('planned_quantity', { required: true, min: 0.01 })}
                    label="Planned Quantity"
                    type="number"
                    fullWidth
                    error={!!errors.planned_quantity}
                    disabled={mode === 'view'}
                    size="small"
                    InputProps={{ inputProps: { step: 0.01 } }}
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                <Grid size={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Status</InputLabel>
                    <Select
                      {...control.register('production_status')}
                      value={watch('production_status')}
                      onChange={(e) => setValue('production_status', e.target.value as 'planned' | 'in_progress' | 'completed' | 'cancelled')}
                      disabled={mode === 'view'}
                      sx={{ height: 27 }}
                    >
                      <MenuItem value="planned">Planned</MenuItem>
                      <MenuItem value="in_progress">In Progress</MenuItem>
                      <MenuItem value="completed">Completed</MenuItem>
                      <MenuItem value="cancelled">Cancelled</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                {/* Planning Dates */}
                <Grid size={6}>
                  <TextField
                    {...control.register('planned_start_date')}
                    label="Planned Start Date"
                    type="date"
                    fullWidth
                    disabled={mode === 'view'}
                    size="small"
                    InputLabelProps={{ shrink: true }}
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                <Grid size={6}>
                  <TextField
                    {...control.register('planned_end_date')}
                    label="Planned End Date"
                    type="date"
                    fullWidth
                    disabled={mode === 'view'}
                    size="small"
                    InputLabelProps={{ shrink: true }}
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                {/* Location Information */}
                <Grid size={6}>
                  <TextField
                    {...control.register('production_department')}
                    label="Department"
                    fullWidth
                    disabled={mode === 'view'}
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                <Grid size={6}>
                  <TextField
                    {...control.register('production_location')}
                    label="Location"
                    fullWidth
                    disabled={mode === 'view'}
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  /> */}
                </Grid>

                <Grid size={12}>
                  <TextField
                    {...control.register('notes')}
                    label="Notes"
                    fullWidth
                    multiline
                    rows={2}
                    disabled={mode === 'view'}
                    size="small"
                  /> */}
                </Grid>

                {/* BOM Details */}
                {selectedBOM && (
                  <Grid size={12}>
                    <Card variant="outlined" sx={{ mt: 2 }}>
                      <CardContent>
                        <Typography variant="subtitle1" gutterBottom>
                          BOM Details: {selectedBOM.bom_name} v{selectedBOM.version}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Output Item: {selectedBOM.output_item?.product_name || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Components: {selectedBOM.components?.length || 0}
                        </Typography>
                        {bomCostBreakdown && (
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="body2">
                              Estimated Cost: {bomCostBreakdown.cost_breakdown.total_cost.toFixed(2)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Material: {bomCostBreakdown.cost_breakdown.material_cost.toFixed(2)} | 
                              Labor: {bomCostBreakdown.cost_breakdown.labor_cost.toFixed(2)} | 
                              Overhead: {bomCostBreakdown.cost_breakdown.overhead_cost.toFixed(2)}
                            </Typography>
                          </Box>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                )}

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
                          mode === 'create' ? 'Create Order' : 'Update Order'
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
        voucherType="Production Order"
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
            handleDeleteOrder(contextMenu.voucher.id);
          }
          setContextMenu(null);
        }}
      />
    </Container>
  );
};

export default ProductionOrder;