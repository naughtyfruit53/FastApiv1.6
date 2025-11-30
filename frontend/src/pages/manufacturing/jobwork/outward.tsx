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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
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
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../../lib/api';
import { ProtectedPage } from '../../../components/ProtectedPage';
import JobworkModal from '../../../components/JobworkModal';

const OutwardJobworkPage: React.FC = () => {
  const [addDialog, setAddDialog] = useState(false);
  const [viewDialog, setViewDialog] = useState(false);
  const [selectedJobwork, setSelectedJobwork] = useState<any>(null);
  const queryClient = useQueryClient();

  // Fetch jobwork orders
  const { data: jobworkOrders = [] } = useQuery({
    queryKey: ['outward-jobwork-orders'],
    queryFn: async () => {
      const response = await api.get('/manufacturing/outward-jobwork');
      return response.data || [];
    },
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await api.post('/manufacturing/outward-jobwork', {
        customer_id: data.party_id,
        date: data.date,
        expected_return_date: data.expected_return_date,
        purpose: data.purpose,
        notes: data.notes,
        items: data.items.map((item: any) => ({
          product_id: item.product_id,
          quantity: item.quantity,
          unit: item.unit,
          remarks: item.remarks,
        })),
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['outward-jobwork-orders'] });
    },
  });

  const handleAddClick = () => {
    setAddDialog(true);
  };

  const handleViewClick = (jobwork: any) => {
    setSelectedJobwork(jobwork);
    setViewDialog(true);
  };

  const handleSubmit = async (formData: any) => {
    await createMutation.mutateAsync(formData);
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
    <ProtectedPage moduleKey="manufacturing" action="read">
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
                      {jobworkOrders.filter((j: any) => j.status === 'in_process').length}
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
                      {jobworkOrders.filter((j: any) => j.status === 'completed').length}
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
                      {jobworkOrders.filter((j: any) => j.status === 'received' || j.status === 'in_process').length}
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
                jobworkOrders.map((jobwork: any) => (
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

      {/* Create Jobwork Modal - Using reusable component */}
      <JobworkModal
        open={addDialog}
        onClose={() => setAddDialog(false)}
        onSubmit={handleSubmit}
        direction="outward"
        title="Create Outward Jobwork Order"
      />

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
    </ProtectedPage>
  );
};

export default OutwardJobworkPage;
