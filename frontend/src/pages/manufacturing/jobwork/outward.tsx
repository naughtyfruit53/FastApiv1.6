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
} from '@mui/material';
import {
  Add,
  Edit,
  Visibility,
  LocalShipping,
  CheckCircle,
  Schedule,
} from '@mui/icons-material';

const OutwardJobworkPage: React.FC = () => {
  const [addDialog, setAddDialog] = useState(false);
  const [viewDialog, setViewDialog] = useState(false);
  const [selectedJobwork, setSelectedJobwork] = useState<any>(null);
  const [formData, setFormData] = useState({
    jobwork_order_no: '',
    customer_id: '',
    date: new Date().toISOString().split('T')[0],
    expected_return_date: '',
    jobwork_type: '',
    notes: '',
    items: [] as any[],
  });

  // Empty arrays - to be loaded from API
  const jobworkOrders: any[] = [];
  const customers: any[] = [];

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
  };

  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };

  const handleViewClick = (jobwork: any) => {
    setSelectedJobwork(jobwork);
    setViewDialog(true);
  };

  const handleSubmit = () => {
    // TODO: Implement create functionality
    console.log('Create outward jobwork order:', formData);
    setAddDialog(false);
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

      {/* Add Dialog */}
      <Dialog
        open={addDialog}
        onClose={() => setAddDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create Outward Jobwork Order</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Jobwork Order No"
                value={formData.jobwork_order_no}
                onChange={(e) =>
                  setFormData({ ...formData, jobwork_order_no: e.target.value })
                }
                required
                helperText="Auto-generated if left empty"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Customer</InputLabel>
                <Select
                  value={formData.customer_id}
                  label="Customer"
                  onChange={(e) =>
                    setFormData({ ...formData, customer_id: e.target.value })
                  }
                  required
                >
                  {customers.length === 0 ? (
                    <MenuItem value="" disabled>
                      No customers available
                    </MenuItem>
                  ) : (
                    customers.map((customer) => (
                      <MenuItem key={customer.id} value={customer.id}>
                        {customer.name}
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
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
            <Grid item xs={12}>
              <Alert severity="info">
                Add material items and processing details in the next step after creating the order.
              </Alert>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            Create Order
          </Button>
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
