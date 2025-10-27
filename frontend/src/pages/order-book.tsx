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
} from "@mui/material";
import { Refresh, Download, Add, Edit, CheckCircle } from "@mui/icons-material";
import axios from "axios";
import { formatCurrency } from "../utils/currencyUtils";

interface Order {
  id: number;
  order_number: string;
  customer_name: string;
  order_date: string;
  due_date: string;
  status: string;
  total_amount: number;
  workflow_stage: string;
}

const ORDER_STATUSES = ["pending", "confirmed", "in_production", "ready_to_dispatch", "dispatched", "completed", "cancelled"];
const WORKFLOW_STAGES = ["order_received", "in_production", "quality_check", "ready_to_dispatch", "dispatched", "completed"];

const OrderBookPage: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      // Placeholder endpoint - would need to be implemented
      const response = await axios.get("/api/v1/order-book/orders", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setOrders(response.data || []);
      setError(null);
    } catch (err: any) {
      // For now, use demo data since endpoint doesn't exist yet
      setOrders([
        {
          id: 1,
          order_number: "ORD-001",
          customer_name: "Customer A",
          order_date: "2025-01-01",
          due_date: "2025-02-01",
          status: "in_production",
          total_amount: 50000,
          workflow_stage: "in_production",
        },
        {
          id: 2,
          order_number: "ORD-002",
          customer_name: "Customer B",
          order_date: "2025-01-05",
          due_date: "2025-02-10",
          status: "confirmed",
          total_amount: 75000,
          workflow_stage: "order_received",
        },
      ]);
      setError(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleUpdateWorkflow = async (orderId: number, newStage: string) => {
    try {
      const token = localStorage.getItem("token");
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Order Book Management
        </Typography>
        <Box>
          <Button startIcon={<Add />} variant="contained" sx={{ mr: 1 }}>
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
                        onClick={() => {
                          setSelectedOrder(order);
                          setOpenDialog(true);
                        }}
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="success"
                        onClick={() => {
                          const currentIndex = WORKFLOW_STAGES.indexOf(order.workflow_stage);
                          if (currentIndex < WORKFLOW_STAGES.length - 1) {
                            handleUpdateWorkflow(order.id, WORKFLOW_STAGES[currentIndex + 1]);
                          }
                        }}
                        disabled={order.workflow_stage === "completed"}
                      >
                        <CheckCircle fontSize="small" />
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
    </Box>
  );
};

export default OrderBookPage;
