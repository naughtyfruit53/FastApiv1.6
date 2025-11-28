// frontend/src/pages/order-book.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Button,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Menu,
} from "@mui/material";
import { Refresh, Download, Add, Edit, CheckCircle, MoreVert } from "@mui/icons-material";
import axios from "axios";
import { formatCurrency } from "../utils/currencyUtils";
import { ProtectedPage } from "../components/ProtectedPage";
import { useRouter } from "next/router";

interface Order {
  id: number;
  order_number: string;
  customer_name: string;
  order_date: string;
  due_date: string;
  status: string;
  total_amount: number;
  workflow_stage: string;
  sales_order_id: number;
  customer_id: number;
}

const ORDER_STATUSES = ["pending", "confirmed", "in_production", "ready_to_dispatch", "dispatched", "completed", "cancelled"];
const WORKFLOW_STAGES = ["order_received", "in_production", "quality_check", "ready_to_dispatch", "dispatched", "completed"];

const OrderBookPage: React.FC = () => {
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedMenuOrder, setSelectedMenuOrder] = useState<Order | null>(null);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      if (!token || token === 'undefined' || token.split('.').length !== 3) {
        setError("Invalid authentication token. Please login again.");
        return;
      }
      const response = await axios.get("/api/v1/order-book/orders", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setOrders(response.data || []);
      setError(null);
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError("Session expired. Please login again.");
      } else {
        setError(err.message || "Failed to fetch orders");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleUpdateWorkflow = async (orderId: number, newStage: string) => {
    try {
      const token = localStorage.getItem("access_token");
      await axios.patch(
        `/api/v1/order-book/orders/${orderId}/workflow`,
        { workflow_stage: newStage },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchOrders();
    } catch (err: any) {
      setError("Failed to update workflow stage");
    }
  };

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, "default" | "primary" | "secondary" | "success" | "error" | "info" | "warning"> = {
      pending: "default",
      confirmed: "info",
      in_production: "primary",
      ready_to_dispatch: "secondary",
      dispatched: "warning",
      completed: "success",
      cancelled: "error",
    };
    return colorMap[status] || "default";
  };

  const getWorkflowStageColor = (stage: string) => {
    const colorMap: Record<string, "default" | "primary" | "secondary" | "success" | "error" | "info" | "warning"> = {
      order_received: "info",
      in_production: "primary",
      quality_check: "secondary",
      ready_to_dispatch: "warning",
      dispatched: "warning",
      completed: "success",
    };
    return colorMap[stage] || "default";
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, order: Order) => {
    setAnchorEl(event.currentTarget);
    setSelectedMenuOrder(order);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedMenuOrder(null);
  };

  const handleView = (order: Order) => {
    router.push(`/vouchers/Pre-Sales-Voucher/sales-order?mode=view&id=${order.sales_order_id}`);
    handleMenuClose();
  };

  const handleCreateProductionOrder = (order: Order) => {
    router.push(`/vouchers/Manufacturing-Vouchers/production-order?from_sales_order=${order.sales_order_id}`);
    handleMenuClose();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <ProtectedPage moduleKey="sales" action="read">
      <Box sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Order Book Management
          </Typography>
          <Box>
            <Button startIcon={<Add />} variant="contained" sx={{ mr: 1 }} onClick={() => router.push('/vouchers/Manufacturing-Vouchers/production-order')}>
              New Order
            </Button>
            <IconButton onClick={fetchOrders} color="primary">
              <Refresh />
            </IconButton>
            <Button startIcon={<Download />} variant="outlined" sx={{ ml: 1 }}>
              Export
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Summary Cards */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Orders
                </Typography>
                <Typography variant="h5">{orders.length}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  In Production
                </Typography>
                <Typography variant="h5" color="primary.main">
                  {orders.filter((o) => o.status === "in_production").length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Ready to Dispatch
                </Typography>
                <Typography variant="h5" color="warning.main">
                  {orders.filter((o) => o.status === "ready_to_dispatch").length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Completed
                </Typography>
                <Typography variant="h5" color="success.main">
                  {orders.filter((o) => o.status === "completed").length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Orders Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Order List
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Order Number</TableCell>
                    <TableCell>Customer</TableCell>
                    <TableCell>Order Date</TableCell>
                    <TableCell>Due Date</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Workflow Stage</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {orders.map((order) => (
                    <TableRow key={order.id}>
                      <TableCell>{order.order_number}</TableCell>
                      <TableCell>{order.customer_name}</TableCell>
                      <TableCell>{new Date(order.order_date).toLocaleDateString()}</TableCell>
                      <TableCell>{new Date(order.due_date).toLocaleDateString()}</TableCell>
                      <TableCell align="right">{formatCurrency(order.total_amount)}</TableCell>
                      <TableCell>
                        <Chip
                          label={order.status.replace("_", " ").toUpperCase()}
                          color={getStatusColor(order.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={order.workflow_stage.replace("_", " ").toUpperCase()}
                          color={getWorkflowStageColor(order.workflow_stage)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          onClick={(e) => handleMenuClick(e, order)}
                        >
                          <MoreVert fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* Update Workflow Dialog */}
        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Update Order Workflow</DialogTitle>
          <DialogContent>
            {selectedOrder && (
              <Box sx={{ pt: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Order: {selectedOrder.order_number}
                </Typography>
                <TextField
                  select
                  fullWidth
                  label="Workflow Stage"
                  value={selectedOrder.workflow_stage}
                  onChange={(e) => {
                    setSelectedOrder({ ...selectedOrder, workflow_stage: e.target.value });
                  }}
                  sx={{ mt: 2 }}
                >
                  {WORKFLOW_STAGES.map((stage) => (
                    <MenuItem key={stage} value={stage}>
                      {stage.replace("_", " ").toUpperCase()}
                    </MenuItem>
                  ))}
                </TextField>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={() => {
                if (selectedOrder) {
                  handleUpdateWorkflow(selectedOrder.id, selectedOrder.workflow_stage);
                  setOpenDialog(false);
                }
              }}
            >
              Update
            </Button>
          </DialogActions>
        </Dialog>

        {/* Kebab Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => selectedMenuOrder && handleView(selectedMenuOrder)}>View</MenuItem>
          <MenuItem onClick={() => selectedMenuOrder && handleCreateProductionOrder(selectedMenuOrder)}>Create Production Order</MenuItem>
        </Menu>
      </Box>
    </ProtectedPage>
  );
};

export default OrderBookPage;