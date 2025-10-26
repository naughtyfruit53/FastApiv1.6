import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Autocomplete,
} from '@mui/material';
import {
  Add,
  Edit,
  Visibility,
  LocalShipping,
  CheckCircle,
  Schedule,
  Delete,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import api from '../../../lib/api';
import { getProducts, getCustomers } from '../../../services/masterService';

const OutwardJobworkPage: React.FC = () => {
  const [addDialog, setAddDialog] = useState(false);
  const [viewDialog, setViewDialog] = useState(false);
  const [selectedJobwork, setSelectedJobwork] = useState<any>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    jobwork_order_no: '',
    customer_id: '',
    date: new Date().toISOString().split('T')[0],
    expected_return_date: '',
    jobwork_type: '',
    notes: '',
    items: [] as any[],
  });

  const steps = ['Basic Details', 'Items to Process', 'Review & Submit'];

  // Fetch jobwork orders
  const { data: jobworkOrders = [] } = useQuery({
    queryKey: ['outward-jobwork-orders'],
    queryFn: async () => {
      const response = await api.get('/manufacturing/outward-jobwork');
      return response.data || [];
    },
  });

  // Fetch customers
  const { data: customerList = [] } = useQuery({
    queryKey: ['customers'],
    queryFn: getCustomers,
  });

  // Fetch products
  const { data: productList = [] } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts,
  });

  const customers = customerList || [];
  const products = productList || [];

  const jobworkTypes = [
    { value: 'machining', label: 'Machining' },
    { value: 'painting', label: 'Painting' },
    { value: 'coating', label: 'Coating' },
    { value: 'assembly', label: 'Assembly' },
    { value: 'packaging', label: 'Packaging' },
    { value: 'other', label: 'Other' },
  ];

  const resetForm = () => {
    setFormData({
      jobwork_order_no: '',
      customer_id: '',
      date: new Date().toISOString().split('T')[0],
      expected_return_date: '',
      jobwork_type: '',
      notes: '',
      items: [],
    });
    setActiveStep(0);
  };

  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };

  const handleViewClick = (jobwork: any) => {
    setSelectedJobwork(jobwork);
    setViewDialog(true);
  };

  const handleNext = () => {
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleAddItem = () => {
    setFormData({
      ...formData,
      items: [
        ...formData.items,
        { product_id: '', quantity: 1, unit: 'PCS', remarks: '' },
      ],
    });
  };

  const handleRemoveItem = (index: number) => {
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  const handleItemChange = (index: number, field: string, value: any) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, items: newItems });
  };

  const handleSubmit = () => {
    // TODO: Implement create functionality
    console.log('Create outward jobwork order:', formData);
    setAddDialog(false);
    resetForm();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'default';
      case 'received':
        return 'info';
      case 'in_process':
        return 'warning';
      case 'completed':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Outward Jobwork
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Receive materials from customers for jobwork processing
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Create Jobwork Order
          </Button>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          Outward Jobwork allows you to receive materials from customers for
          processing and track the delivery of finished goods back to them.
        </Alert>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Orders
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {jobworkOrders.length}
                    </Typography>
                  </Box>
                  <LocalShipping sx={{ fontSize: 40, color: 'primary.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      In Process
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {jobworkOrders.filter((j) => j.status === 'in_process').length}
                    </Typography>
                  </Box>
                  <Schedule sx={{ fontSize: 40, color: 'warning.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Completed
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {jobworkOrders.filter((j) => j.status === 'completed').length}
                    </Typography>
                  </Box>
                  <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Pending Delivery
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {jobworkOrders.filter((j) => j.status === 'received' || j.status === 'in_process').length}
                    </Typography>
                  </Box>
                  <LocalShipping sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Jobwork Orders Table */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Order No</TableCell>
                <TableCell>Customer</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Expected Delivery</TableCell>
                <TableCell>Jobwork Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {jobworkOrders.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="textSecondary" sx={{ py: 3 }}>
                      No jobwork orders found. Click "Create Jobwork Order" to create one.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                jobworkOrders.map((jobwork) => (
                  <TableRow key={jobwork.id}>
                    <TableCell>{jobwork.jobwork_order_no}</TableCell>
                    <TableCell>{jobwork.customer_name}</TableCell>
                    <TableCell>{jobwork.date}</TableCell>
                    <TableCell>{jobwork.expected_return_date}</TableCell>
                    <TableCell>
                      <Chip
                        label={jobwork.jobwork_type}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={jobwork.status}
                        size="small"
                        color={getStatusColor(jobwork.status)}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleViewClick(jobwork)}
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton size="small">
                        <Edit />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>

      {/* Add Dialog - Multi-Step */}
      <Dialog
        open={addDialog}
        onClose={() => {
          setAddDialog(false);
          resetForm();
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create Outward Jobwork Order</DialogTitle>
        <DialogContent>
          <Stepper activeStep={activeStep} sx={{ pt: 3, pb: 5 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Step 1: Basic Details */}
          {activeStep === 0 && (
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Jobwork Order No"
                  value={formData.jobwork_order_no}
                  onChange={(e) =>
                    setFormData({ ...formData, jobwork_order_no: e.target.value })
                  }
                  helperText="Auto-generated if left empty"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Autocomplete
                  options={customers}
                  getOptionLabel={(option: any) => option.name || ''}
                  value={customers.find((c: any) => c.id === formData.customer_id) || null}
                  onChange={(_, newValue) =>
                    setFormData({ ...formData, customer_id: newValue?.id || '' })
                  }
                  renderInput={(params) => (
                    <TextField {...params} label="Customer" required />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Date"
                  type="date"
                  value={formData.date}
                  onChange={(e) =>
                    setFormData({ ...formData, date: e.target.value })
                  }
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Expected Delivery Date"
                  type="date"
                  value={formData.expected_return_date}
                  onChange={(e) =>
                    setFormData({ ...formData, expected_return_date: e.target.value })
                  }
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Jobwork Type</InputLabel>
                  <Select
                    value={formData.jobwork_type}
                    label="Jobwork Type"
                    onChange={(e) =>
                      setFormData({ ...formData, jobwork_type: e.target.value })
                    }
                  >
                    {jobworkTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notes"
                  value={formData.notes}
                  onChange={(e) =>
                    setFormData({ ...formData, notes: e.target.value })
                  }
                  multiline
                  rows={3}
                />
              </Grid>
            </Grid>
          )}

          {/* Step 2: Items to Process */}
          {activeStep === 1 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Items to Process</Typography>
                <Button startIcon={<Add />} onClick={handleAddItem}>
                  Add Item
                </Button>
              </Box>
              
              {formData.items.length === 0 ? (
                <Alert severity="info">
                  Click "Add Item" to add items that will be sent for jobwork processing.
                </Alert>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Product</TableCell>
                        <TableCell>Quantity</TableCell>
                        <TableCell>Unit</TableCell>
                        <TableCell>Remarks</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {formData.items.map((item, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Autocomplete
                              options={products}
                              getOptionLabel={(option: any) => option.name || ''}
                              value={
                                products.find((p: any) => p.id === item.product_id) || null
                              }
                              onChange={(_, newValue) =>
                                handleItemChange(index, 'product_id', newValue?.id || '')
                              }
                              renderInput={(params) => (
                                <TextField {...params} size="small" />
                              )}
                              sx={{ minWidth: 200 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={item.quantity}
                              onChange={(e) =>
                                handleItemChange(
                                  index,
                                  'quantity',
                                  parseFloat(e.target.value) || 1
                                )
                              }
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              value={item.unit}
                              onChange={(e) =>
                                handleItemChange(index, 'unit', e.target.value)
                              }
                              sx={{ width: 70 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              value={item.remarks}
                              onChange={(e) =>
                                handleItemChange(index, 'remarks', e.target.value)
                              }
                              sx={{ width: 150 }}
                            />
                          </TableCell>
                          <TableCell>
                            <IconButton
                              size="small"
                              onClick={() => handleRemoveItem(index)}
                            >
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
          )}

          {/* Step 3: Review & Submit */}
          {activeStep === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Review Jobwork Order
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Basic Details
                    </Typography>
                    <Typography variant="body2">
                      Customer:{' '}
                      {customers.find((c: any) => c.id === formData.customer_id)?.name || 'N/A'}
                    </Typography>
                    <Typography variant="body2">Date: {formData.date}</Typography>
                    <Typography variant="body2">
                      Expected Delivery: {formData.expected_return_date || 'Not set'}
                    </Typography>
                    <Typography variant="body2">
                      Jobwork Type: {jobworkTypes.find(t => t.value === formData.jobwork_type)?.label || 'N/A'}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Items ({formData.items.length} items)
                    </Typography>
                    {formData.items.map((item, index) => (
                      <Typography variant="body2" key={index}>
                        • {products.find((p: any) => p.id === item.product_id)?.name || 'Unknown'}{' '}
                        - {item.quantity} {item.unit}
                      </Typography>
                    ))}
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setAddDialog(false);
            resetForm();
          }}>
            Cancel
          </Button>
          <Box sx={{ flex: '1 1 auto' }} />
          {activeStep > 0 && (
            <Button onClick={handleBack}>Back</Button>
          )}
          {activeStep < steps.length - 1 ? (
            <Button variant="contained" onClick={handleNext}>
              Next
            </Button>
          ) : (
            <Button variant="contained" onClick={handleSubmit}>
              Create Order
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* View Dialog */}
      <Dialog
        open={viewDialog}
        onClose={() => setViewDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Jobwork Order Details</DialogTitle>
        <DialogContent>
          {selectedJobwork && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Order No: {selectedJobwork.jobwork_order_no}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Customer: {selectedJobwork.customer_name}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Date: {selectedJobwork.date}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Expected Delivery: {selectedJobwork.expected_return_date}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Jobwork Type: {selectedJobwork.jobwork_type}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Status: {selectedJobwork.status}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default OutwardJobworkPage;
