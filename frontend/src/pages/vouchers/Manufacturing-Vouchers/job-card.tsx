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
  CardContent,
  Checkbox,
  FormControlLabel,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { 
  Add, 
  Remove,
  Visibility, 
  Edit, 
  Delete, 
  Save,
  Cancel,
  ExpandMore
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../../lib/api';
import { getProducts, getVendors } from '../../../services/masterService';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';

interface JobCardSuppliedMaterial {
  product_id: number;
  quantity_supplied: number;
  unit: string;
  unit_rate: number;
  batch_number?: string;
  lot_number?: string;
  supply_date?: string;
}

interface JobCardReceivedOutput {
  product_id: number;
  quantity_received: number;
  unit: string;
  unit_rate: number;
  quality_status?: string;
  inspection_date?: string;
  inspection_remarks?: string;
  batch_number?: string;
  receipt_date?: string;
}

interface JobCardVoucher {
  id?: number;
  voucher_number: string;
  date: string;
  job_type: string;
  vendor_id: number;
  manufacturing_order_id?: number;
  job_description: string;
  job_category?: string;
  expected_completion_date?: string;
  actual_completion_date?: string;
  materials_supplied_by: string;
  delivery_address?: string;
  transport_mode?: string;
  job_status: string;
  quality_specifications?: string;
  quality_check_required: boolean;
  notes?: string;
  status: string;
  total_amount: number;
  supplied_materials: JobCardSuppliedMaterial[];
  received_outputs: JobCardReceivedOutput[];
}

const defaultValues: Partial<JobCardVoucher> = {
  voucher_number: '',
  date: new Date().toISOString().split('T')[0],
  job_type: 'outsourcing',
  materials_supplied_by: 'company',
  job_status: 'planned',
  quality_check_required: true,
  status: 'draft',
  total_amount: 0,
  supplied_materials: [],
  received_outputs: []
};

const jobTypeOptions = [
  { value: 'outsourcing', label: 'Outsourcing' },
  { value: 'subcontracting', label: 'Subcontracting' },
  { value: 'processing', label: 'Processing' }
];

const jobStatusOptions = [
  { value: 'planned', label: 'Planned' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' }
];

const materialsSuppliedByOptions = [
  { value: 'company', label: 'Company' },
  { value: 'vendor', label: 'Vendor' },
  { value: 'mixed', label: 'Mixed' }
];

const qualityStatusOptions = [
  { value: 'accepted', label: 'Accepted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'rework', label: 'Rework Required' }
];

function TabPanel({ children, value, index, ...other }: any) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`job-card-tabpanel-${index}`}
      aria-labelledby={`job-card-tab-${index}`}
      {...other}
    >
      {value === index && <Box p={3}>{children}</Box>}
    </div>
  );
}

export default function JobCardVoucher() {
  const router = useRouter();
  const [mode, setMode] = useState<'create' | 'edit' | 'view'>('create');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const queryClient = useQueryClient();

  const { control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm<JobCardVoucher>({
    defaultValues
  });

  const {
    fields: materialFields,
    append: appendMaterial,
    remove: removeMaterial
  } = useFieldArray({
    control,
    name: 'supplied_materials'
  });

  const {
    fields: outputFields,
    append: appendOutput,
    remove: removeOutput
  } = useFieldArray({
    control,
    name: 'received_outputs'
  });

  // Fetch vouchers list
  const { data: voucherList, isLoading } = useQuery({
    queryKey: ['job-card-vouchers'],
    queryFn: () => api.get('/job-card-vouchers').then(res => res.data),
  });

  // Fetch vendors
  const { data: vendorList } = useQuery({
    queryKey: ['vendors'],
    queryFn: getVendors
  });

  // Fetch manufacturing orders
  const { data: manufacturingOrders } = useQuery({
    queryKey: ['manufacturing-orders'],
    queryFn: () => api.get('/manufacturing-orders').then(res => res.data),
  });

  // Fetch products
  const { data: productList } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts
  });

  // Fetch specific voucher
  const { data: voucherData, isFetching } = useQuery({
    queryKey: ['job-card-voucher', selectedId],
    queryFn: () => api.get(`/job-card-vouchers/${selectedId}`).then(res => res.data),
    enabled: !!selectedId
  });

  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ['nextJobCardNumber'],
    queryFn: () => api.get('/job-card-vouchers/next-number').then(res => res.data),
    enabled: mode === 'create',
  });

  const sortedVouchers = voucherList ? [...voucherList].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ) : [];

  const latestVouchers = sortedVouchers.slice(0, 10);
  const productOptions = productList || [];
  const vendorOptions = vendorList || [];
  const manufacturingOrderOptions = manufacturingOrders || [];

  useEffect(() => {
    if (mode === 'create' && nextVoucherNumber) {
      setValue('voucher_number', nextVoucherNumber);
    } else if (voucherData) {
      reset(voucherData);
    } else if (mode === 'create') {
      reset(defaultValues);
    }
  }, [voucherData, mode, reset, nextVoucherNumber, setValue]);

  // Calculate totals
  useEffect(() => {
    const suppliedMaterials = watch('supplied_materials') || [];
    const receivedOutputs = watch('received_outputs') || [];
    
    const suppliedValue = suppliedMaterials.reduce((sum, item) => 
      sum + (item.quantity_supplied * item.unit_rate), 0);
    const outputValue = receivedOutputs.reduce((sum, item) => 
      sum + (item.quantity_received * item.unit_rate), 0);
    
    // Net job work value
    const total = outputValue - suppliedValue;
    setValue('total_amount', total);
  }, [watch('supplied_materials'), watch('received_outputs'), setValue]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: JobCardVoucher) => api.post('/job-card-vouchers', data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ['job-card-vouchers'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue('voucher_number', newNextNumber);
    },
    onError: (error: any) => {
      console.error('Error creating job card voucher:', error);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: JobCardVoucher }) => 
      api.put(`/job-card-vouchers/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-card-vouchers'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
    },
    onError: (error: any) => {
      console.error('Error updating job card voucher:', error);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/job-card-vouchers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-card-vouchers'] });
      if (selectedId) {
        setSelectedId(null);
        setMode('create');
        reset(defaultValues);
      }
    }
  });

  const onSubmit = (data: JobCardVoucher) => {
    if (mode === 'edit' && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (voucher: JobCardVoucher) => {
    setSelectedId(voucher.id!);
    setMode('edit');
  };

  const handleView = (voucher: JobCardVoucher) => {
    setSelectedId(voucher.id!);
    setMode('view');
  };

  const handleDelete = (voucherId: number) => {
    if (window.confirm('Are you sure you want to delete this voucher?')) {
      deleteMutation.mutate(voucherId);
    }
  };

  const handleCancel = () => {
    setMode('create');
    setSelectedId(null);
    reset(defaultValues);
  };

  const addMaterial = () => {
    appendMaterial({
      product_id: 0,
      quantity_supplied: 0,
      unit: '',
      unit_rate: 0
    });
  };

  const addOutput = () => {
    appendOutput({
      product_id: 0,
      quantity_received: 0,
      unit: '',
      unit_rate: 0
    });
  };

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" component="h1" gutterBottom>
        Job Card Vouchers
      </Typography>

      <Grid container spacing={3}>
        {/* Voucher List - Left Side */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">Recent Vouchers</Typography>
                {/* VoucherHeaderActions commented out */}
              </Box>
              
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Voucher No.</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Vendor</TableCell>
                      <TableCell>Job Type</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {latestVouchers.map((voucher, index) => (
                      <TableRow key={voucher.id}>
                        <TableCell>{voucher.voucher_number}</TableCell>
                        <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                        <TableCell>{voucher.vendor?.name}</TableCell>
                        <TableCell>
                          <Chip 
                            label={voucher.job_type} 
                            size="small"
                            color="primary"
                          /> */}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={voucher.job_status} 
                            size="small"
                            color={voucher.job_status === 'completed' ? 'success' : 'default'}
                          /> */}
                        </TableCell>
                        <TableCell align="center">
                          <VoucherContextMenu
                            voucher={voucher}
                            voucherType="Job Card"
                            onView={() => handleView(voucher)}
                            onEdit={() => handleEdit(voucher)}
                            onDelete={() => handleDelete(voucher.id!)}
                            onClose={() => {}}
                          /> */}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Voucher Form - Right Side */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  {mode === 'create' && 'Create Job Card Voucher'}
                  {mode === 'edit' && 'Edit Job Card Voucher'}
                  {mode === 'view' && 'View Job Card Voucher'}
                </Typography>
                {mode !== 'create' && (
                  <Button 
                    variant="outlined" 
                    onClick={handleCancel}
                    startIcon={<Cancel />}
                  >
                    Cancel
                  </Button>
                )}
              </Box>

              <form onSubmit={handleSubmit(onSubmit)}>
                {/* Basic Details */}
                <Grid container spacing={2} mb={3}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Voucher Number"
                      {...control.register('voucher_number')}
                      fullWidth
                      disabled
                      value={watch('voucher_number')}
                    /> */}
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Date"
                      type="date"
                      {...control.register('date')}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      disabled={mode === 'view'}
                    /> */}
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <FormControl fullWidth>
                      <InputLabel>Job Type</InputLabel>
                      <Select
                        value={watch('job_type')}
                        onChange={(e) => setValue('job_type', e.target.value)}
                        disabled={mode === 'view'}
                      >
                        {jobTypeOptions.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Autocomplete
                      options={vendorOptions}
                      getOptionLabel={(option) => option.name || ''}
                      value={vendorOptions.find((vendor: any) => vendor.id === watch('vendor_id')) || null}
                      onChange={(_, newValue) => setValue('vendor_id', newValue?.id || 0)}
                      renderInput={(params) => (
                        <TextField {...params} label="Vendor" required />
                      )}
                      disabled={mode === 'view'}
                    /> */}
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Autocomplete
                      options={manufacturingOrderOptions}
                      getOptionLabel={(option) => option.voucher_number || ''}
                      value={manufacturingOrderOptions.find((mo: any) => mo.id === watch('manufacturing_order_id')) || null}
                      onChange={(_, newValue) => setValue('manufacturing_order_id', newValue?.id || undefined)}
                      renderInput={(params) => (
                        <TextField {...params} label="Manufacturing Order (Optional)" />
                      )}
                      disabled={mode === 'view'}
                    /> */}
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <FormControl fullWidth>
                      <InputLabel>Job Status</InputLabel>
                      <Select
                        value={watch('job_status')}
                        onChange={(e) => setValue('job_status', e.target.value)}
                        disabled={mode === 'view'}
                      >
                        {jobStatusOptions.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>

                {/* Job Details */}
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Job Details</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid size={12}>
                        <TextField
                          label="Job Description"
                          {...control.register('job_description')}
                          fullWidth
                          required
                          multiline
                          rows={3}
                          disabled={mode === 'view'}
                        /> */}
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <TextField
                          label="Job Category"
                          {...control.register('job_category')}
                          fullWidth
                          placeholder="e.g., Machining, Assembly, Finishing"
                          disabled={mode === 'view'}
                        /> */}
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <FormControl fullWidth>
                          <InputLabel>Materials Supplied By</InputLabel>
                          <Select
                            value={watch('materials_supplied_by')}
                            onChange={(e) => setValue('materials_supplied_by', e.target.value)}
                            disabled={mode === 'view'}
                          >
                            {materialsSuppliedByOptions.map((option) => (
                              <MenuItem key={option.value} value={option.value}>
                                {option.label}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <TextField
                          label="Expected Completion Date"
                          type="date"
                          {...control.register('expected_completion_date')}
                          fullWidth
                          InputLabelProps={{ shrink: true }}
                          disabled={mode === 'view'}
                        /> */}
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <TextField
                          label="Actual Completion Date"
                          type="date"
                          {...control.register('actual_completion_date')}
                          fullWidth
                          InputLabelProps={{ shrink: true }}
                          disabled={mode === 'view'}
                        /> */}
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <TextField
                          label="Transport Mode"
                          {...control.register('transport_mode')}
                          fullWidth
                          disabled={mode === 'view'}
                        /> */}
                      </Grid>
                      <Grid size={12}>
                        <TextField
                          label="Delivery Address"
                          {...control.register('delivery_address')}
                          fullWidth
                          multiline
                          rows={2}
                          disabled={mode === 'view'}
                        /> */}
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>

                {/* Quality Requirements */}
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Quality Requirements</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid size={12}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={watch('quality_check_required')}
                              onChange={(e) => setValue('quality_check_required', e.target.checked)}
                              disabled={mode === 'view'}
                            /> */}
                          }
                          label="Quality Check Required"
                        /> */}
                      </Grid>
                      <Grid size={12}>
                        <TextField
                          label="Quality Specifications"
                          {...control.register('quality_specifications')}
                          fullWidth
                          multiline
                          rows={3}
                          disabled={mode === 'view'}
                        /> */}
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>

                {/* Materials and Outputs Tabs */}
                <Box mt={3}>
                  <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
                    <Tab label="Supplied Materials" />
                    <Tab label="Received Outputs" />
                  </Tabs>

                  {/* Supplied Materials Tab */}
                  <TabPanel value={activeTab} index={0}>
                    {mode !== 'view' && (
                      <Box mb={2}>
                        <Button
                          variant="outlined"
                          onClick={addMaterial}
                          startIcon={<Add />}
                        >
                          Add Material
                        </Button>
                      </Box>
                    )}

                    <TableContainer component={Paper}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Product</TableCell>
                            <TableCell>Quantity</TableCell>
                            <TableCell>Unit</TableCell>
                            <TableCell>Rate</TableCell>
                            <TableCell>Value</TableCell>
                            <TableCell>Batch</TableCell>
                            <TableCell>Supply Date</TableCell>
                            {mode !== 'view' && <TableCell>Actions</TableCell>}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {materialFields.map((field, index) => (
                            <TableRow key={field.id}>
                              <TableCell>
                                <Autocomplete
                                  options={productOptions}
                                  getOptionLabel={(option) => option.name || ''}
                                  value={productOptions.find((p: any) => p.id === watch(`supplied_materials.${index}.product_id`)) || null}
                                  onChange={(_, newValue) => {
                                    setValue(`supplied_materials.${index}.product_id`, newValue?.id || 0);
                                    setValue(`supplied_materials.${index}.unit`, newValue?.unit || '');
                                    setValue(`supplied_materials.${index}.unit_rate`, newValue?.price || 0);
                                  }}
                                  renderInput={(params) => (
                                    <TextField {...params} size="small" />
                                  )}
                                  disabled={mode === 'view'}
                                  sx={{ minWidth: 150 }}
                                /> */}
                              </TableCell>
                              <TableCell>
                                <TextField
                                  type="number"
                                  size="small"
                                  value={watch(`supplied_materials.${index}.quantity_supplied`)}
                                  onChange={(e) => setValue(`supplied_materials.${index}.quantity_supplied`, parseFloat(e.target.value) || 0)}
                                  disabled={mode === 'view'}
                                  sx={{ width: 80 }}
                                /> */}
                              </TableCell>
                              <TableCell>
                                <TextField
                                  size="small"
                                  value={watch(`supplied_materials.${index}.unit`)}
                                  onChange={(e) => setValue(`supplied_materials.${index}.unit`, e.target.value)}
                                  disabled={mode === 'view'}
                                  sx={{ width: 70 }}
                                /> */}
                              </TableCell>
                              <TableCell>
                                <TextField
                                  type="number"
                                  size="small"
                                  value={watch(`supplied_materials.${index}.unit_rate`)}
                                  onChange={(e) => setValue(`supplied_materials.${index}.unit_rate`, parseFloat(e.target.value) || 0)}
                                  disabled={mode === 'view'}
                                  sx={{ width: 80 }}
                                /> */}
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2">
                                  ₹{((watch(`supplied_materials.${index}.quantity_supplied`) || 0) * (watch(`supplied_materials.${index}.unit_rate`) || 0)).toFixed(2)}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <TextField
                                  size="small"
                                  value={watch(`supplied_materials.${index}.batch_number`)}
                                  onChange={(e) => setValue(`supplied_materials.${index}.batch_number`, e.target.value)}
                                  disabled={mode === 'view'}
                                  sx={{ width: 100 }}
                                /> */}
                              </TableCell>
                              <TableCell>
                                <TextField
                                  type="date"
                                  size="small"
                                  value={watch(`supplied_materials.${index}.supply_date`)}
                                  onChange={(e) => setValue(`supplied_materials.${index}.supply_date`, e.target.value)}
                                  disabled={mode === 'view'}
                                  sx={{ width: 120 }}
                                /> */}
                              </TableCell>
                              {mode !== 'view' && (
                                <TableCell>
                                  <IconButton
                                    onClick={() => removeMaterial(index)}
                                    size="small"
                                    color="error"
                                  >
                                    <Remove />
                                  </IconButton>
                                </TableCell>
                              )}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </TabPanel>

                  {/* Received Outputs Tab */}
                  <TabPanel value={activeTab} index={1}>
                    {mode !== 'view' && (
                      <Box mb={2}>
                        <Button
                          variant="outlined"
                          onClick={addOutput}
                          startIcon={<Add />}
                        >
                          Add Output
                        </Button>
                      </Box>
                    )}

                    <TableContainer component={Paper}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Product</TableCell>
                            <TableCell>Quantity</TableCell>
                            <TableCell>Unit</TableCell>
                            <TableCell>Rate</TableCell>
                            <TableCell>Value</TableCell>
                            <TableCell>Quality</TableCell>
                            <TableCell>Receipt Date</TableCell>
                            {mode !== 'view' && <TableCell>Actions</TableCell>}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {outputFields.map((field, index) => (
                            <TableRow key={field.id}>
                              <TableCell>
                                <Autocomplete
                                  options={productOptions}
                                  getOptionLabel={(option) => option.name || ''}
                                  value={productOptions.find((p: any) => p.id === watch(`received_outputs.${index}.product_id`)) || null}
                                  onChange={(_, newValue) => {
                                    setValue(`received_outputs.${index}.product_id`, newValue?.id || 0);
                                    setValue(`received_outputs.${index}.unit`, newValue?.unit || '');
                                    setValue(`received_outputs.${index}.unit_rate`, newValue?.price || 0);
                                  }}
                                  renderInput={(params) => (
                                    <TextField {...params} size="small" />
                                  )}
                                  disabled={mode === 'view'}
                                  sx={{ minWidth: 150 }}
                                /> */}
                              </TableCell>
                              <TableCell>
                                <TextField
                                  type="number"
                                  size="small"
                                  value={watch(`received_outputs.${index}.quantity_received`)}
                                  onChange={(e) => setValue(`received_outputs.${index}.quantity_received`, parseFloat(e.target.value) || 0)}
                                  disabled={mode === 'view'}
                                  sx={{ width: 80 }}
                                /> */}
                              </TableCell>
                              <TableCell>
                                <TextField
                                  size="small"
                                  value={watch(`received_outputs.${index}.unit`)}
                                  onChange={(e) => setValue(`received_outputs.${index}.unit`, e.target.value)}
                                  disabled={mode === 'view'}
                                  sx={{ width: 70 }}
                                /> */}
                              </TableCell>
                              <TableCell>
                                <TextField
                                  type="number"
                                  size="small"
                                  value={watch(`received_outputs.${index}.unit_rate`)}
                                  onChange={(e) => setValue(`received_outputs.${index}.unit_rate`, parseFloat(e.target.value) || 0)}
                                  disabled={mode === 'view'}
                                  sx={{ width: 80 }}
                                /> */}
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2">
                                  ₹{((watch(`received_outputs.${index}.quantity_received`) || 0) * (watch(`received_outputs.${index}.unit_rate`) || 0)).toFixed(2)}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Select
                                  size="small"
                                  value={watch(`received_outputs.${index}.quality_status`) || ''}
                                  onChange={(e) => setValue(`received_outputs.${index}.quality_status`, e.target.value)}
                                  disabled={mode === 'view'}
                                  sx={{ width: 100 }}
                                >
                                  {qualityStatusOptions.map((option) => (
                                    <MenuItem key={option.value} value={option.value}>
                                      {option.label}
                                    </MenuItem>
                                  ))}
                                </Select>
                              </TableCell>
                              <TableCell>
                                <TextField
                                  type="date"
                                  size="small"
                                  value={watch(`received_outputs.${index}.receipt_date`)}
                                  onChange={(e) => setValue(`received_outputs.${index}.receipt_date`, e.target.value)}
                                  disabled={mode === 'view'}
                                  sx={{ width: 120 }}
                                /> */}
                              </TableCell>
                              {mode !== 'view' && (
                                <TableCell>
                                  <IconButton
                                    onClick={() => removeOutput(index)}
                                    size="small"
                                    color="error"
                                  >
                                    <Remove />
                                  </IconButton>
                                </TableCell>
                              )}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </TabPanel>
                </Box>

                {/* Notes */}
                <Grid container spacing={2} mt={2}>
                  <Grid size={12}>
                    <TextField
                      label="Notes"
                      {...control.register('notes')}
                      fullWidth
                      multiline
                      rows={3}
                      disabled={mode === 'view'}
                    /> */}
                  </Grid>
                </Grid>

                {/* Total Amount */}
                <Box display="flex" justifyContent="flex-end" mt={2}>
                  <Typography variant="h6">
                    Net Job Work Value: ₹{(watch('total_amount') || 0).toFixed(2)}
                  </Typography>
                </Box>

                {/* Action Buttons */}
                {mode !== 'view' && (
                  <Box mt={3} display="flex" gap={2}>
                    <Button
                      type="submit"
                      variant="contained"
                      color="primary"
                      disabled={createMutation.isPending || updateMutation.isPending}
                      startIcon={<Save />}
                    >
                      {mode === 'edit' ? 'Update' : 'Create'} Voucher
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={handleCancel}
                      startIcon={<Cancel />}
                    >
                      Cancel
                    </Button>
                  </Box>
                )}
              </form>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}