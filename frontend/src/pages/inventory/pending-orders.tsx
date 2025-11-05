// frontend/src/pages/inventory/pending-orders.tsx

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Chip,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Link,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  LocalShipping as ShippingIcon,
  Launch as LaunchIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import api from '../../lib/api';
import TrackingDetailsDialog from '../../components/DispatchManagement/TrackingDetailsDialog';
import { ProtectedPage } from '@/components/ProtectedPage';

interface PendingOrder {
  id: number;
  voucher_number: string;
  date: string;
  vendor_name: string;
  vendor_id: number;
  total_amount: number;
  status: string;
  total_ordered_qty: number;
  total_received_qty: number;
  pending_qty: number;
  grn_count: number;
  has_tracking: boolean;
  transporter_name?: string;
  tracking_number?: string;
  tracking_link?: string;
  color_status: 'red' | 'yellow' | 'green';
  days_pending: number;
}

interface Summary {
  total_orders: number;
  total_value: number;
  with_tracking: number;
  without_tracking: number;
}

const PendingOrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<PendingOrder[]>([]);
  const [summary, setSummary] = useState<Summary>({
    total_orders: 0,
    total_value: 0,
    with_tracking: 0,
    without_tracking: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [trackingDialogOpen, setTrackingDialogOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<PendingOrder | null>(null);

  useEffect(() => {
    fetchPendingOrders();
  }, []);

  const fetchPendingOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/reports/pending-purchase-orders-with-grn-status');
      setOrders(response.data.orders || []);
      setSummary(response.data.summary || {
        total_orders: 0,
        total_value: 0,
        with_tracking: 0,
        without_tracking: 0
      });
    } catch (err: any) {
      console.error('Error fetching pending orders:', err);
      setError(err.response?.data?.detail || 'Failed to load pending orders');
    } finally {
      setLoading(false);
    }
  };

  const handleEditTracking = (order: PendingOrder) => {
    setSelectedOrder(order);
    setTrackingDialogOpen(true);
  };

  const handleTrackingDialogClose = () => {
    setTrackingDialogOpen(false);
    setSelectedOrder(null);
    // Refresh data to show updated tracking
    fetchPendingOrders();
  };

  const getStatusColor = (colorStatus: string) => {
    switch (colorStatus) {
      case 'red':
        return '#f44336'; // Red - no tracking
      case 'yellow':
        return '#ff9800'; // Orange/Yellow - tracking present, GRN pending
      case 'green':
        return '#4caf50'; // Green - complete (shouldn't appear in this list)
      default:
        return '#9e9e9e'; // Grey
    }
  };

  const getStatusLabel = (colorStatus: string) => {
    switch (colorStatus) {
      case 'red':
        return 'No Tracking';
      case 'yellow':
        return 'Tracking Present';
      case 'green':
        return 'Complete';
      default:
        return 'Unknown';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (


    <ProtectedPage moduleKey="inventory" action="read">
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Pending Orders
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={fetchPendingOrders} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Pending Orders
              </Typography>
              <Typography variant="h4">
                {summary.total_orders}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Value
              </Typography>
              <Typography variant="h4">
                {formatCurrency(summary.total_value)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #4caf50' }}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                With Tracking
              </Typography>
              <Typography variant="h4" color="success.main">
                {summary.with_tracking}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #f44336' }}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Without Tracking
              </Typography>
              <Typography variant="h4" color="error.main">
                {summary.without_tracking}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Legend */}
      <Box display="flex" gap={2} mb={2} alignItems="center">
        <Typography variant="body2" color="text.secondary">
          Color Legend:
        </Typography>
        <Chip
          label="No Tracking"
          size="small"
          sx={{ backgroundColor: '#f44336', color: 'white' }}
        />
        <Chip
          label="Tracking Present, GRN Pending"
          size="small"
          sx={{ backgroundColor: '#ff9800', color: 'white' }}
        />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {orders.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No pending orders found. All purchase orders are either fully received or don't have any items yet.
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Status</TableCell>
                <TableCell>PO Number</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Vendor</TableCell>
                <TableCell align="right">Amount</TableCell>
                <TableCell align="center">Ordered Qty</TableCell>
                <TableCell align="center">Received Qty</TableCell>
                <TableCell align="center">Pending Qty</TableCell>
                <TableCell align="center">GRNs</TableCell>
                <TableCell>Tracking</TableCell>
                <TableCell align="center">Days Pending</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((order) => (
                <TableRow
                  key={order.id}
                  sx={{
                    borderLeft: `4px solid ${getStatusColor(order.color_status)}`,
                    '&:hover': { backgroundColor: 'action.hover' }
                  }}
                >
                  <TableCell>
                    <Chip
                      label={getStatusLabel(order.color_status)}
                      size="small"
                      sx={{
                        backgroundColor: getStatusColor(order.color_status),
                        color: 'white'
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {order.voucher_number}
                    </Typography>
                  </TableCell>
                  <TableCell>{formatDate(order.date)}</TableCell>
                  <TableCell>{order.vendor_name}</TableCell>
                  <TableCell align="right">{formatCurrency(order.total_amount)}</TableCell>
                  <TableCell align="center">{order.total_ordered_qty.toFixed(2)}</TableCell>
                  <TableCell align="center">{order.total_received_qty.toFixed(2)}</TableCell>
                  <TableCell align="center">
                    <Typography color="error" fontWeight="medium">
                      {order.pending_qty.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">{order.grn_count}</TableCell>
                  <TableCell>
                    {order.has_tracking ? (
                      <Box>
                        <Typography variant="body2" noWrap>
                          {order.transporter_name}
                        </Typography>
                        {order.tracking_number && (
                          <Typography variant="caption" color="text.secondary" noWrap>
                            {order.tracking_number}
                          </Typography>
                        )}
                        {order.tracking_link && (
                          <Link
                            href={order.tracking_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}
                          >
                            <Typography variant="caption">Track</Typography>
                            <LaunchIcon sx={{ fontSize: 12 }} />
                          </Link>
                        )}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Not set
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={`${order.days_pending}d`}
                      size="small"
                      color={order.days_pending > 30 ? 'error' : order.days_pending > 15 ? 'warning' : 'default'}
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="Add/Edit Tracking">
                      <IconButton
                        size="small"
                        onClick={() => handleEditTracking(order)}
                        color="primary"
                      >
                        {order.has_tracking ? <EditIcon fontSize="small" /> : <ShippingIcon fontSize="small" />}
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Tracking Details Dialog */}
      {selectedOrder && (
        <TrackingDetailsDialog
          open={trackingDialogOpen}
          onClose={handleTrackingDialogClose}
          voucherType="purchase_order"
          voucherId={selectedOrder.id}
          voucherNumber={selectedOrder.voucher_number}
        />
      )}
    </Box>


    </ProtectedPage>


  
  );
};

export default PendingOrdersPage;