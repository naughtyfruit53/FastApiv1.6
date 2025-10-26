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
import { getProducts, getVendors } from '../../../services/masterService';

const InwardJobworkPage: React.FC = () => {
  const [addDialog, setAddDialog] = useState(false);
  const [viewDialog, setViewDialog] = useState(false);
  const [selectedJobwork, setSelectedJobwork] = useState<any>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    jobwork_order_no: '',
    vendor_id: '',
    date: new Date().toISOString().split('T')[0],
    expected_return_date: '',
    purpose: '',
    notes: '',
    items: [] as any[],
  });

  const steps = ['Basic Details', 'Materials to Send', 'Review & Submit'];

  // Fetch jobwork orders
  const { data: jobworkOrders = [] } = useQuery({
    queryKey: ['inward-jobwork-orders'],
    queryFn: async () => {
      const response = await api.get('/manufacturing/inward-jobwork');
      return response.data || [];
    },
  });

  // Fetch vendors
  const { data: vendorList = [] } = useQuery({
    queryKey: ['vendors'],
    queryFn: getVendors,
  });

  // Fetch products
  const { data: productList = [] } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts,
  });

  const vendors = vendorList || [];
  const products = productList || [];

  const resetForm = () => {
    setFormData({
      jobwork_order_no: '',
      vendor_id: '',
      date: new Date().toISOString().split('T')[0],
      expected_return_date: '',
      purpose: '',
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
    console.log('Create inward jobwork order:', formData);
    setAddDialog(false);
    resetForm();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'default';
      case 'sent':
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
              Inward Jobwork
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Send materials to vendors for jobwork processing
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
          Inward Jobwork allows you to send raw materials or semi-finished goods to
          vendors for processing. Track material sent out and received back after
          jobwork completion.
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
                      Pending Return
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {jobworkOrders.filter((j) => j.status === 'sent' || j.status === 'in_process').length}
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
                <TableCell>Vendor</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Expected Return</TableCell>
                <TableCell>Purpose</TableCell>
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
                    <TableCell>{jobwork.vendor_name}</TableCell>
                    <TableCell>{jobwork.date}</TableCell>
                    <TableCell>{jobwork.expected_return_date}</TableCell>
                    <TableCell>{jobwork.purpose}</TableCell>
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
        <DialogTitle>Create Inward Jobwork Order</DialogTitle>
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
                  options={vendors}
                  getOptionLabel={(option: any) => option.name || ''}
                  value={vendors.find((v: any) => v.id === formData.vendor_id) || null}
                  onChange={(_, newValue) =>
                    setFormData({ ...formData, vendor_id: newValue?.id || '' })
                  }
                  renderInput={(params) => (
                    <TextField {...params} label="Vendor" required />
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
                  label="Expected Return Date"
                  type="date"
                  value={formData.expected_return_date}
                  onChange={(e) =>
                    setFormData({ ...formData, expected_return_date: e.target.value })
                  }
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Purpose"
                  value={formData.purpose}
                  onChange={(e) =>
                    setFormData({ ...formData, purpose: e.target.value })
                  }
                  placeholder="e.g., Machining, Painting, Assembly"
                />
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

          {/* Step 2: Materials to Send */}
          {activeStep === 1 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Materials to Send</Typography>
                <Button startIcon={<Add />} onClick={handleAddItem}>
                  Add Item
                </Button>
              </Box>
              
              {formData.items.length === 0 ? (
                <Alert severity="info">
                  Click "Add Item" to add materials that will be sent for jobwork.
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
                      Vendor:{' '}
                      {vendors.find((v: any) => v.id === formData.vendor_id)?.name || 'N/A'}
                    </Typography>
                    <Typography variant="body2">Date: {formData.date}</Typography>
                    <Typography variant="body2">
                      Expected Return: {formData.expected_return_date || 'Not set'}
                    </Typography>
                    <Typography variant="body2">Purpose: {formData.purpose}</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Materials ({formData.items.length} items)
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
                Vendor: {selectedJobwork.vendor_name}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Date: {selectedJobwork.date}
              </Typography>
              <Typography variant="body2" gutterBottom>
                Expected Return: {selectedJobwork.expected_return_date}
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

export default InwardJobworkPage;
