import React, { useState } from 'react';
import {
  Typography,
  Container,
  Box,
  Alert,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Stack,
  Divider,
} from '@mui/material';
import {
  CheckCircle,
  Schedule,
  Build,
  Inventory,
  LocalShipping,
  Assignment,
  Add,
  ArrowForward,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { toast } from 'react-toastify';
import { useRouter } from 'next/router';
import { ProtectedPage } from '../../../components/ProtectedPage';
import api from '../../../lib/api';

const FinishedGoodsReceipt: React.FC = () => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [receiptDialogOpen, setReceiptDialogOpen] = useState(false);
  const [batchDialogOpen, setBatchDialogOpen] = useState(false);
  const [qcDialogOpen, setQcDialogOpen] = useState(false);

  // Fetch production orders ready for receipt
  const { data: productionOrders, isLoading } = useQuery({
    queryKey: ['production-orders-ready'],
    queryFn: async () => {
      const response = await api.get('/manufacturing/manufacturing-orders?status=completed');
      return response.data || [];
    },
  });

  // Fetch recent FG receipts
  const { data: fgReceipts } = useQuery({
    queryKey: ['fg-receipts'],
    queryFn: async () => {
      const response = await api.get('/manufacturing/fg-receipts');
      return response.data || [];
    },
  });

  const { control: receiptControl, handleSubmit: handleReceiptSubmit, reset: resetReceipt, formState: { errors: receiptErrors } } = useForm({
    defaultValues: {
      production_order_id: 0,
      received_quantity: 0,
      good_quantity: 0,
      reject_quantity: 0,
      warehouse_id: 0,
      bin_location: '',
      notes: '',
    },
  });

  const { control: batchControl, handleSubmit: handleBatchSubmit, reset: resetBatch, formState: { errors: batchErrors } } = useForm({
    defaultValues: {
      batch_number: '',
      manufacturing_date: new Date().toISOString().slice(0, 10),
      expiry_date: '',
      quantity: 0,
      notes: '',
    },
  });

  const createReceiptMutation = useMutation({
    mutationFn: (data: any) => api.post('/manufacturing/fg-receipts', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fg-receipts'] });
      queryClient.invalidateQueries({ queryKey: ['production-orders-ready'] });
      setReceiptDialogOpen(false);
      resetReceipt();
      toast.success('Finished goods receipt created successfully');
    },
    onError: () => toast.error('Failed to create receipt'),
  });

  const createBatchMutation = useMutation({
    mutationFn: (data: any) => api.post('/manufacturing/batches', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batches'] });
      setBatchDialogOpen(false);
      resetBatch();
      toast.success('Batch/Lot created successfully');
    },
    onError: () => toast.error('Failed to create batch'),
  });

  const handleSectionClick = (section: string) => {
    setSelectedSection(section);
    switch (section) {
      case 'grn':
        setReceiptDialogOpen(true);
        break;
      case 'batch':
        setBatchDialogOpen(true);
        break;
      case 'quality':
        router.push('/vouchers/Manufacturing-Vouchers/quality-control');
        break;
      default:
        break;
    }
  };

  const onReceiptSubmit = (data: any) => {
    createReceiptMutation.mutate(data);
  };

  const onBatchSubmit = (data: any) => {
    createBatchMutation.mutate(data);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'warning';
      case 'quality_check': return 'info';
      default: return 'default';
    }
  };

  return (
    <ProtectedPage moduleKey="manufacturing" action="write">
      <Container maxWidth="lg">
        <Box sx={{ mt: 3 }}>
          <Typography variant="h4" gutterBottom>
            Finished Goods Receipt
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Track and receive finished goods from production orders.
          </Typography>
          
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              Click on any section below to access the operational page or create new entries.
            </Typography>
          </Alert>

          {/* Three Clickable Sections */}
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Operations
          </Typography>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* GRN/FG Receipt Lines */}
            <Grid item xs={12} md={4}>
              <Card 
                sx={{ 
                  height: '100%',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  }
                }}
              >
                <CardActionArea 
                  onClick={() => handleSectionClick('grn')}
                  sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
                >
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box sx={{ 
                      bgcolor: 'primary.light', 
                      borderRadius: 2, 
                      p: 2, 
                      mb: 2,
                      display: 'inline-flex'
                    }}>
                      <LocalShipping sx={{ fontSize: 48, color: 'primary.main' }} />
                    </Box>
                    <Typography variant="h6" gutterBottom>
                      GRN/FG Receipt Lines
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Record finished goods received from production. Link to work orders and post to stock.
                    </Typography>
                    <Chip 
                      label="Create Receipt" 
                      color="primary" 
                      icon={<Add />}
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>

            {/* Batch/Lot Management */}
            <Grid item xs={12} md={4}>
              <Card 
                sx={{ 
                  height: '100%',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  }
                }}
              >
                <CardActionArea 
                  onClick={() => handleSectionClick('batch')}
                  sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
                >
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box sx={{ 
                      bgcolor: 'success.light', 
                      borderRadius: 2, 
                      p: 2, 
                      mb: 2,
                      display: 'inline-flex'
                    }}>
                      <Assignment sx={{ fontSize: 48, color: 'success.main' }} />
                    </Box>
                    <Typography variant="h6" gutterBottom>
                      Batch/Lot Management
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Manage batch numbers, lot tracking, expiry dates, and serial numbers for finished goods.
                    </Typography>
                    <Chip 
                      label="Manage Batches" 
                      color="success" 
                      icon={<ArrowForward />}
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>

            {/* Quality Checks */}
            <Grid item xs={12} md={4}>
              <Card 
                sx={{ 
                  height: '100%',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  }
                }}
              >
                <CardActionArea 
                  onClick={() => handleSectionClick('quality')}
                  sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
                >
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box sx={{ 
                      bgcolor: 'warning.light', 
                      borderRadius: 2, 
                      p: 2, 
                      mb: 2,
                      display: 'inline-flex'
                    }}>
                      <CheckCircle sx={{ fontSize: 48, color: 'warning.main' }} />
                    </Box>
                    <Typography variant="h6" gutterBottom>
                      Quality Checks
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Run quality inspections on finished goods before posting to stock. Pass/fail criteria.
                    </Typography>
                    <Chip 
                      label="Go to QC" 
                      color="warning" 
                      icon={<ArrowForward />}
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          </Grid>

          {/* Recent FG Receipts */}
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            Recent FG Receipts
          </Typography>
          
          {isLoading ? (
            <CircularProgress />
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Receipt #</TableCell>
                    <TableCell>Production Order</TableCell>
                    <TableCell>Received Qty</TableCell>
                    <TableCell>Good Qty</TableCell>
                    <TableCell>Reject Qty</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {fgReceipts?.length > 0 ? (
                    fgReceipts.slice(0, 10).map((receipt: any) => (
                      <TableRow key={receipt.id}>
                        <TableCell>FGR-{receipt.id}</TableCell>
                        <TableCell>{receipt.production_order_number || '-'}</TableCell>
                        <TableCell>{receipt.received_quantity}</TableCell>
                        <TableCell>{receipt.good_quantity}</TableCell>
                        <TableCell>{receipt.reject_quantity}</TableCell>
                        <TableCell>
                          <Chip
                            label={receipt.status}
                            color={getStatusColor(receipt.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{new Date(receipt.created_at).toLocaleDateString()}</TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        No FG receipts found. Click "GRN/FG Receipt Lines" to create one.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Integration Info */}
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Integration Points
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                      <Inventory color="primary" />
                      <Typography variant="subtitle1">
                        Inventory Update
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Automatically update finished goods inventory upon receipt confirmation.
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                      <Schedule color="primary" />
                      <Typography variant="subtitle1">
                        Audit Trail
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Complete audit trail of all receipts, approvals, and stock postings.
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                      <Build color="primary" />
                      <Typography variant="subtitle1">
                        Cost Calculation
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Calculate actual production costs vs. planned costs for analysis.
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        </Box>

        {/* GRN/FG Receipt Dialog */}
        <Dialog open={receiptDialogOpen} onClose={() => setReceiptDialogOpen(false)} maxWidth="md" fullWidth>
          <form onSubmit={handleReceiptSubmit(onReceiptSubmit)}>
            <DialogTitle>Create FG Receipt</DialogTitle>
            <DialogContent>
              <Stack spacing={2} sx={{ mt: 1 }}>
                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 600 }}>
                  Production Order
                </Typography>

                <Controller
                  name="production_order_id"
                  control={receiptControl}
                  rules={{ required: "Production order is required" }}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!receiptErrors.production_order_id}>
                      <InputLabel>Production Order *</InputLabel>
                      <Select {...field} label="Production Order *">
                        <MenuItem value={0}>Select Production Order...</MenuItem>
                        {productionOrders?.map((order: any) => (
                          <MenuItem key={order.id} value={order.id}>
                            {order.voucher_number || `PO-${order.id}`}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />

                <Divider sx={{ my: 1 }} />

                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 600 }}>
                  Quantities
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Controller
                      name="received_quantity"
                      control={receiptControl}
                      rules={{ required: "Required" }}
                      render={({ field }) => (
                        <TextField 
                          {...field} 
                          fullWidth 
                          label="Received Qty *" 
                          type="number"
                          error={!!receiptErrors.received_quantity}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <Controller
                      name="good_quantity"
                      control={receiptControl}
                      render={({ field }) => (
                        <TextField 
                          {...field} 
                          fullWidth 
                          label="Good Qty" 
                          type="number"
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <Controller
                      name="reject_quantity"
                      control={receiptControl}
                      render={({ field }) => (
                        <TextField 
                          {...field} 
                          fullWidth 
                          label="Reject Qty" 
                          type="number"
                        />
                      )}
                    />
                  </Grid>
                </Grid>

                <Divider sx={{ my: 1 }} />

                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 600 }}>
                  Storage Location
                </Typography>

                <Controller
                  name="bin_location"
                  control={receiptControl}
                  render={({ field }) => (
                    <TextField 
                      {...field} 
                      fullWidth 
                      label="Bin Location"
                      helperText="Warehouse bin or location"
                    />
                  )}
                />

                <Divider sx={{ my: 1 }} />

                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 600 }}>
                  Notes
                </Typography>

                <Controller
                  name="notes"
                  control={receiptControl}
                  render={({ field }) => (
                    <TextField 
                      {...field} 
                      fullWidth 
                      label="Notes" 
                      multiline 
                      rows={3}
                    />
                  )}
                />
              </Stack>
            </DialogContent>
            <DialogActions sx={{ px: 3, py: 2 }}>
              <Button onClick={() => setReceiptDialogOpen(false)} color="inherit">Cancel</Button>
              <Button type="submit" variant="contained" disabled={createReceiptMutation.isPending}>
                {createReceiptMutation.isPending ? <CircularProgress size={24} /> : "Save & Post to Stock"}
              </Button>
            </DialogActions>
          </form>
        </Dialog>

        {/* Batch/Lot Management Dialog */}
        <Dialog open={batchDialogOpen} onClose={() => setBatchDialogOpen(false)} maxWidth="md" fullWidth>
          <form onSubmit={handleBatchSubmit(onBatchSubmit)}>
            <DialogTitle>Create Batch/Lot</DialogTitle>
            <DialogContent>
              <Stack spacing={2} sx={{ mt: 1 }}>
                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 600 }}>
                  Batch Information
                </Typography>

                <Controller
                  name="batch_number"
                  control={batchControl}
                  rules={{ required: "Batch number is required" }}
                  render={({ field }) => (
                    <TextField 
                      {...field} 
                      fullWidth 
                      label="Batch Number *"
                      error={!!batchErrors.batch_number}
                      helperText={batchErrors.batch_number?.message as string || "Unique batch/lot identifier"}
                    />
                  )}
                />

                <Divider sx={{ my: 1 }} />

                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 600 }}>
                  Dates
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Controller
                      name="manufacturing_date"
                      control={batchControl}
                      render={({ field }) => (
                        <TextField 
                          {...field} 
                          fullWidth 
                          label="Manufacturing Date"
                          type="date"
                          InputLabelProps={{ shrink: true }}
                        />
                      )}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Controller
                      name="expiry_date"
                      control={batchControl}
                      render={({ field }) => (
                        <TextField 
                          {...field} 
                          fullWidth 
                          label="Expiry Date"
                          type="date"
                          InputLabelProps={{ shrink: true }}
                        />
                      )}
                    />
                  </Grid>
                </Grid>

                <Divider sx={{ my: 1 }} />

                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 600 }}>
                  Quantity
                </Typography>

                <Controller
                  name="quantity"
                  control={batchControl}
                  rules={{ required: "Quantity is required" }}
                  render={({ field }) => (
                    <TextField 
                      {...field} 
                      fullWidth 
                      label="Quantity *"
                      type="number"
                      error={!!batchErrors.quantity}
                    />
                  )}
                />

                <Divider sx={{ my: 1 }} />

                <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 600 }}>
                  Notes
                </Typography>

                <Controller
                  name="notes"
                  control={batchControl}
                  render={({ field }) => (
                    <TextField 
                      {...field} 
                      fullWidth 
                      label="Notes" 
                      multiline 
                      rows={3}
                    />
                  )}
                />
              </Stack>
            </DialogContent>
            <DialogActions sx={{ px: 3, py: 2 }}>
              <Button onClick={() => setBatchDialogOpen(false)} color="inherit">Cancel</Button>
              <Button type="submit" variant="contained" disabled={createBatchMutation.isPending}>
                {createBatchMutation.isPending ? <CircularProgress size={24} /> : "Save"}
              </Button>
            </DialogActions>
          </form>
        </Dialog>
      </Container>
    </ProtectedPage>
  );
};
export default FinishedGoodsReceipt;
