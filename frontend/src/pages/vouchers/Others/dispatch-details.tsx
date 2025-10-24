// frontend/src/pages/vouchers/Others/dispatch-details.tsx
// Dispatch Details Voucher Page
import React, { useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Grid,
  CircularProgress,
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Divider,
} from "@mui/material";
import LocalShipping from "@mui/icons-material/LocalShipping";
import Visibility from "@mui/icons-material/Visibility";
import Search from "@mui/icons-material/Search";
import Person from "@mui/icons-material/Person";
import Phone from "@mui/icons-material/Phone";
import LocationOn from "@mui/icons-material/LocationOn";
import { useQuery } from "@tanstack/react-query";
import VoucherLayout from "../../../components/VoucherLayout";
import { dispatchService } from "../../../services/dispatchService";
const DispatchDetailsPage: React.FC = () => {
  const [selectedDispatch, setSelectedDispatch] = useState<any>(null);
  
  // State for voucher date conflict detection
  const [conflictInfo, setConflictInfo] = useState<any>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);
  const [pendingDate, setPendingDate] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  // Fetch dispatch orders
  const {
    data: dispatches = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["dispatch-orders", searchTerm, statusFilter],
    queryFn: () =>
      dispatchService.getDispatchOrders({
        search: searchTerm || undefined,
        status: statusFilter || undefined,
      }),
  });
  const handleView = (dispatch: any) => {
    setSelectedDispatch(dispatch);
    setIsDialogOpen(true);
  };
  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedDispatch(null);
  };
  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case "pending":
        return "warning";
      case "in_transit":
        return "info";
      case "delivered":
        return "success";
      case "cancelled":
        return "error";
      default:
        return "default";
    }
  };
  const formatDate = (dateString: string) => {
    if (!dateString) {
      return "-";
    }
    return new Date(dateString).toLocaleDateString();
  };
  const formatDateTime = (dateString: string) => {
    if (!dateString) {
      return "-";
    }
    return new Date(dateString).toLocaleString();
  };
  return (
    <VoucherLayout
      title="Dispatch Details"
      description="View and track dispatch dispatch order details and delivery status"
    >
      <Container maxWidth="xl">
        {/* Header Actions */}
        <Box
          sx={{
            mb: 3,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
            <TextField
              size="small"
              placeholder="Search dispatch orders..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <Search sx={{ mr: 1, color: "action.active" }} />
                ),
              }}
            />
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                label="Status"
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="in_transit">In Transit</MenuItem>
                <MenuItem value="delivered">Delivered</MenuItem>
                <MenuItem value="cancelled">Cancelled</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>
        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            Failed to load dispatch orders
          </Alert>
        )}
        {/* Loading */}
        {isLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
            <CircularProgress />
          </Box>
        )}
        {/* Dispatch Cards */}
        <Grid container spacing={3}>
          {dispatches.map((dispatch: any) => (
            <Grid item xs={12} md={6} lg={4} key={dispatch.id}>
              <Card>
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      mb: 2,
                    }}
                  >
                    <Typography variant="h6" component="div" noWrap>
                      {dispatch.order_number}
                    </Typography>
                    <Chip
                      label={dispatch.status?.replace("_", " ")}
                      color={getStatusColor(dispatch.status) as any}
                      size="small"
                    />
                  </Box>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mb: 1,
                    }}
                  >
                    <Person fontSize="small" color="action" />
                    <Typography variant="body2">
                      Customer ID: {dispatch.customer_id}
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mb: 1,
                    }}
                  >
                    <LocationOn fontSize="small" color="action" />
                    <Typography variant="body2" noWrap>
                      {dispatch.delivery_address}
                    </Typography>
                  </Box>
                  {dispatch.delivery_contact_person && (
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mb: 1,
                      }}
                    >
                      <Phone fontSize="small" color="action" />
                      <Typography variant="body2">
                        {dispatch.delivery_contact_person}
                      </Typography>
                    </Box>
                  )}
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Created:</strong> {formatDate(dispatch.created_at)}
                  </Typography>
                  {dispatch.expected_delivery_date && (
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Expected:</strong>{" "}
                      {formatDate(dispatch.expected_delivery_date)}
                    </Typography>
                  )}
                  <Typography variant="body2">
                    <strong>Items:</strong> {dispatch.items?.length || 0}
                  </Typography>
                  {dispatch.tracking_number && (
                    <Box
                      sx={{ mt: 2, p: 1, bgcolor: "grey.100", borderRadius: 1 }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <LocalShipping fontSize="small" />
                        <strong>Tracking:</strong> {dispatch.tracking_number}
                      </Typography>
                      {dispatch.courier_name && (
                        <Typography variant="body2" color="text.secondary">
                          Courier: {dispatch.courier_name}
                        </Typography>
                      )}
                    </Box>
                  )}
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    startIcon={<Visibility />}
                    onClick={() => handleView(dispatch)}
                  >
                    View Details
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
        {/* Empty State */}
        {!isLoading && dispatches.length === 0 && (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <LocalShipping
              sx={{ fontSize: 64, color: "text.secondary", mb: 2 }}
            />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No dispatch orders found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {searchTerm || statusFilter
                ? "Try adjusting your search criteria"
                : "Dispatch orders will appear here once created"}
            </Typography>
          </Box>
        )}
        {/* Dispatch Details Dialog */}
        <Dialog
          open={isDialogOpen}
          onClose={handleDialogClose}
          maxWidth="lg"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <LocalShipping />
              Dispatch Order Details
              {selectedDispatch && (
                <Chip
                  label={selectedDispatch.status?.replace("_", " ")}
                  color={getStatusColor(selectedDispatch.status) as any}
                  size="small"
                />
              )}
            </Box>
          </DialogTitle>
          <DialogContent dividers>
            {selectedDispatch && (
              <Grid container spacing={3}>
                {/* Basic Information */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Basic Information
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Order Number"
                    value={selectedDispatch.order_number || ""}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Customer ID"
                    value={selectedDispatch.customer_id || ""}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Ticket ID"
                    value={selectedDispatch.ticket_id || "N/A"}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Status"
                    value={selectedDispatch.status?.replace("_", " ") || ""}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                {/* Delivery Information */}
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Delivery Information
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Delivery Address"
                    multiline
                    rows={3}
                    value={selectedDispatch.delivery_address || ""}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Contact Person"
                    value={selectedDispatch.delivery_contact_person || "N/A"}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Contact Number"
                    value={selectedDispatch.delivery_contact_number || "N/A"}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                {/* Dates */}
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Important Dates
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Created At"
                    value={formatDateTime(selectedDispatch.created_at)}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Expected Delivery"
                    value={formatDateTime(
                      selectedDispatch.expected_delivery_date,
                    )}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Actual Delivery"
                    value={formatDateTime(
                      selectedDispatch.actual_delivery_date,
                    )}
                    InputProps={{ readOnly: true }}
                  />
                </Grid>
                {/* Tracking Information */}
                {(selectedDispatch.tracking_number ||
                  selectedDispatch.courier_name) && (
                  <>
                    <Grid item xs={12}>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="h6" gutterBottom>
                        Tracking Information
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Tracking Number"
                        value={selectedDispatch.tracking_number || "N/A"}
                        InputProps={{ readOnly: true }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Courier Name"
                        value={selectedDispatch.courier_name || "N/A"}
                        InputProps={{ readOnly: true }}
                      />
                    </Grid>
                  </>
                )}
                {/* Notes */}
                {selectedDispatch.notes && (
                  <>
                    <Grid item xs={12}>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="h6" gutterBottom>
                        Notes
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Notes"
                        multiline
                        rows={3}
                        value={selectedDispatch.notes}
                        InputProps={{ readOnly: true }}
                      />
                    </Grid>
                  </>
                )}
                {/* Items */}
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Dispatch Items
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Product ID</TableCell>
                          <TableCell>Quantity</TableCell>
                          <TableCell>Unit</TableCell>
                          <TableCell>Description</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedDispatch.items?.map(
                          (item: any, index: number) => (
                            <TableRow key={index}>
                              <TableCell>{item.product_id}</TableCell>
                              <TableCell>{item.quantity}</TableCell>
                              <TableCell>{item.unit}</TableCell>
                              <TableCell>{item.description || "-"}</TableCell>
                              <TableCell>
                                <Chip
                                  label={item.status}
                                  color={getStatusColor(item.status) as any}
                                  size="small"
                                />
                              </TableCell>
                            </TableRow>
                          ),
                        ) || (
                          <TableRow>
                            <TableCell colSpan={5} align="center">
                              No items found
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>
              </Grid>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDialogClose}>Close</Button>
          </DialogActions>
        </Dialog>
      </Container>
    </VoucherLayout>
  );
};
export default DispatchDetailsPage;