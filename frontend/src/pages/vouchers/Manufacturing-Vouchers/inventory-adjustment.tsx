// frontend/src/pages/vouchers/Manufacturing-Vouchers/inventory-adjustment.tsx
import React, { useState, useEffect } from "react";
import {
  Typography,
  Container,
  Box,
  Button,
  Grid,
  CircularProgress,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  IconButton,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import { Refresh, History, CheckCircle, Cancel } from "@mui/icons-material";
import { useForm, Controller } from "react-hook-form";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { ProtectedPage } from "../../../components/ProtectedPage";
import api from "../../../lib/api";

interface Product {
  id: number;
  product_name: string;
  unit: string;
}

interface InventoryAdjustment {
  id: number;
  type: string;
  item_id: number;
  batch_number?: string;
  old_quantity: number;
  new_quantity: number;
  reason: string;
  reason_code?: string;
  reference_doc?: string;
  comment?: string;
  status: string;
  approved_by?: string;
  created_at: string;
}

interface AdjustmentFormData {
  type: string;
  item_id: number;
  batch_number?: string;
  old_quantity: number;
  new_quantity: number;
  reason: string;
  reason_code?: string;
  reference_doc?: string;
  comment: string;
}

const ADJUSTMENT_TYPES = [
  { value: "increase", label: "Increase" },
  { value: "decrease", label: "Decrease" },
  { value: "conversion", label: "Conversion" },
  { value: "wip", label: "Work in Progress" },
  { value: "write-off", label: "Write-off" },
];

const REASON_CODES = [
  { value: "audit", label: "Physical Count/Audit" },
  { value: "damage", label: "Damaged Goods" },
  { value: "wastage", label: "Wastage" },
  { value: "theft", label: "Theft/Loss" },
  { value: "error", label: "Data Entry Error" },
  { value: "remeasure", label: "Re-measurement" },
];

const InventoryAdjustment: React.FC = () => {
  const queryClient = useQueryClient();
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [pendingAdjustment, setPendingAdjustment] = useState<AdjustmentFormData | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  // Fetch products
  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const response = await api.get("/products");
      return response.data;
    },
  });

  // Fetch stock data for selected product
  const { data: stockData } = useQuery({
    queryKey: ["product-stock", selectedProduct?.id],
    queryFn: async () => {
      if (!selectedProduct?.id) return null;
      const response = await api.get(`/stock/product/${selectedProduct.id}`);
      return response.data;
    },
    enabled: !!selectedProduct?.id,
  });

  // Fetch adjustment history
  const { data: adjustments, isLoading: adjustmentsLoading, refetch: refetchAdjustments } = useQuery({
    queryKey: ["inventory-adjustments"],
    queryFn: async () => {
      const response = await api.get("/manufacturing/inventory-adjustment");
      return response.data;
    },
  });

  const { control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm<AdjustmentFormData>({
    defaultValues: {
      type: "decrease",
      item_id: 0,
      batch_number: "",
      old_quantity: 0,
      new_quantity: 0,
      reason: "audit",
      reason_code: "",
      reference_doc: "",
      comment: "",
    },
  });

  const watchItemId = watch("item_id");
  const watchOldQuantity = watch("old_quantity");
  const watchNewQuantity = watch("new_quantity");

  // Update selected product when item changes
  useEffect(() => {
    if (watchItemId && products) {
      const product = products.find((p: Product) => p.id === watchItemId);
      setSelectedProduct(product || null);
    }
  }, [watchItemId, products]);

  // Update old quantity when stock data loads
  useEffect(() => {
    if (stockData?.quantity !== undefined) {
      setValue("old_quantity", stockData.quantity);
    }
  }, [stockData, setValue]);

  // Submit mutation
  const submitMutation = useMutation({
    mutationFn: async (data: AdjustmentFormData) => {
      const response = await api.post("/manufacturing/inventory-adjustment/submit", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory-adjustments"] });
      queryClient.invalidateQueries({ queryKey: ["stock"] });
      queryClient.invalidateQueries({ queryKey: ["product-stock"] });
      setConfirmDialogOpen(false);
      setPendingAdjustment(null);
      reset();
      setSelectedProduct(null);
      toast.success("Inventory adjustment submitted successfully!");
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || error?.userMessage || "Failed to submit adjustment";
      toast.error(message);
    },
  });

  // Handle form submission - show confirmation dialog
  const onSubmit = (data: AdjustmentFormData) => {
    // Validate comment
    if (!data.comment || data.comment.trim().length < 5) {
      toast.error("Please provide a comment with at least 5 characters");
      return;
    }

    setPendingAdjustment(data);
    setConfirmDialogOpen(true);
  };

  // Confirm and submit adjustment
  const handleConfirmSubmit = () => {
    if (pendingAdjustment) {
      submitMutation.mutate(pendingAdjustment);
    }
  };

  // Cancel confirmation
  const handleCancelConfirm = () => {
    setConfirmDialogOpen(false);
    setPendingAdjustment(null);
  };

  // Calculate adjustment quantity
  const adjustmentQty = watchNewQuantity - watchOldQuantity;

  if (productsLoading) {
    return (
      <ProtectedPage moduleKey="manufacturing" action="write">
        <Container maxWidth="lg">
          <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
            <CircularProgress />
          </Box>
        </Container>
      </ProtectedPage>
    );
  }

  return (
    <ProtectedPage moduleKey="manufacturing" action="write">
      <Container maxWidth="lg">
        <Box sx={{ mt: 3 }}>
          <Typography variant="h4" gutterBottom>
            Inventory Adjustment
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Adjust inventory for production variances, waste, or discrepancies.
          </Typography>

          <Alert severity="info" sx={{ mb: 3 }}>
            All adjustments require a comment and are logged for audit purposes.
          </Alert>

          <Grid container spacing={3}>
            {/* Adjustment Form */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  New Adjustment
                </Typography>
                <form onSubmit={handleSubmit(onSubmit)}>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Controller
                        name="item_id"
                        control={control}
                        rules={{ required: "Item is required", min: { value: 1, message: "Please select an item" } }}
                        render={({ field }) => (
                          <FormControl fullWidth error={!!errors.item_id}>
                            <InputLabel>Item</InputLabel>
                            <Select {...field} label="Item">
                              <MenuItem value={0}>Select an item...</MenuItem>
                              {products?.map((product: Product) => (
                                <MenuItem key={product.id} value={product.id}>
                                  {product.product_name}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        )}
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Controller
                        name="type"
                        control={control}
                        render={({ field }) => (
                          <FormControl fullWidth>
                            <InputLabel>Adjustment Type</InputLabel>
                            <Select {...field} label="Adjustment Type">
                              {ADJUSTMENT_TYPES.map((type) => (
                                <MenuItem key={type.value} value={type.value}>
                                  {type.label}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        )}
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Controller
                        name="batch_number"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} fullWidth label="Batch/Lot Number (Optional)" />
                        )}
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Controller
                        name="old_quantity"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            label="Current Quantity"
                            type="number"
                            disabled
                            InputProps={{
                              endAdornment: selectedProduct?.unit ? (
                                <Typography variant="body2" color="text.secondary">
                                  {selectedProduct.unit}
                                </Typography>
                              ) : null,
                            }}
                          />
                        )}
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Controller
                        name="new_quantity"
                        control={control}
                        rules={{ required: "New quantity is required" }}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            label="New Quantity"
                            type="number"
                            error={!!errors.new_quantity}
                            InputProps={{
                              endAdornment: selectedProduct?.unit ? (
                                <Typography variant="body2" color="text.secondary">
                                  {selectedProduct.unit}
                                </Typography>
                              ) : null,
                            }}
                          />
                        )}
                      />
                    </Grid>

                    {/* Adjustment Preview */}
                    {watchItemId > 0 && (
                      <Grid item xs={12}>
                        <Alert severity={adjustmentQty >= 0 ? "success" : "warning"}>
                          Adjustment: {adjustmentQty >= 0 ? "+" : ""}{adjustmentQty} {selectedProduct?.unit || "units"}
                        </Alert>
                      </Grid>
                    )}

                    <Grid item xs={12} md={6}>
                      <Controller
                        name="reason"
                        control={control}
                        rules={{ required: "Reason is required" }}
                        render={({ field }) => (
                          <FormControl fullWidth error={!!errors.reason}>
                            <InputLabel>Reason</InputLabel>
                            <Select {...field} label="Reason">
                              {REASON_CODES.map((reason) => (
                                <MenuItem key={reason.value} value={reason.value}>
                                  {reason.label}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        )}
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Controller
                        name="reference_doc"
                        control={control}
                        render={({ field }) => (
                          <TextField {...field} fullWidth label="Reference Document (Optional)" />
                        )}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Controller
                        name="comment"
                        control={control}
                        rules={{ 
                          required: "Comment is required",
                          minLength: { value: 5, message: "Comment must be at least 5 characters" }
                        }}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            fullWidth
                            label="Comment (Required)"
                            multiline
                            rows={3}
                            error={!!errors.comment}
                            helperText={errors.comment?.message || "Explain the reason for this adjustment"}
                          />
                        )}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Button
                        type="submit"
                        variant="contained"
                        fullWidth
                        size="large"
                        disabled={submitMutation.isPending}
                      >
                        {submitMutation.isPending ? <CircularProgress size={24} /> : "Submit Adjustment"}
                      </Button>
                    </Grid>
                  </Grid>
                </form>
              </Paper>
            </Grid>

            {/* Recent Adjustments */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
                  <Typography variant="h6">Recent Adjustments</Typography>
                  <IconButton onClick={() => refetchAdjustments()} size="small">
                    <Refresh />
                  </IconButton>
                </Box>

                {adjustmentsLoading ? (
                  <CircularProgress />
                ) : (
                  <TableContainer sx={{ maxHeight: 400 }}>
                    <Table size="small" stickyHeader>
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell>Type</TableCell>
                          <TableCell>Change</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {adjustments?.length > 0 ? (
                          adjustments.slice(0, 10).map((adj: InventoryAdjustment) => (
                            <TableRow key={adj.id}>
                              <TableCell>
                                {new Date(adj.created_at).toLocaleDateString()}
                              </TableCell>
                              <TableCell>{adj.type}</TableCell>
                              <TableCell>
                                {adj.new_quantity - adj.old_quantity >= 0 ? "+" : ""}
                                {adj.new_quantity - adj.old_quantity}
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={adj.status}
                                  color={adj.status === "approved" ? "success" : "default"}
                                  size="small"
                                />
                              </TableCell>
                            </TableRow>
                          ))
                        ) : (
                          <TableRow>
                            <TableCell colSpan={4} align="center">
                              No adjustments found
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </Paper>
            </Grid>
          </Grid>
        </Box>

        {/* Confirmation Dialog */}
        <Dialog
          open={confirmDialogOpen}
          onClose={handleCancelConfirm}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Confirm Inventory Adjustment</DialogTitle>
          <DialogContent>
            {pendingAdjustment && (
              <Box>
                <Alert severity="warning" sx={{ mb: 2 }}>
                  Please review the adjustment details before submitting.
                </Alert>

                <List dense>
                  <ListItem>
                    <ListItemText
                      primary="Item"
                      secondary={products?.find((p: Product) => p.id === pendingAdjustment.item_id)?.product_name || "-"}
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Batch/Lot Number"
                      secondary={pendingAdjustment.batch_number || "N/A"}
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Current Quantity"
                      secondary={`${pendingAdjustment.old_quantity} ${selectedProduct?.unit || "units"}`}
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="New Quantity"
                      secondary={`${pendingAdjustment.new_quantity} ${selectedProduct?.unit || "units"}`}
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Adjustment"
                      secondary={
                        <Chip
                          label={`${(pendingAdjustment.new_quantity - pendingAdjustment.old_quantity) >= 0 ? "+" : ""}${pendingAdjustment.new_quantity - pendingAdjustment.old_quantity} ${selectedProduct?.unit || "units"}`}
                          color={(pendingAdjustment.new_quantity - pendingAdjustment.old_quantity) >= 0 ? "success" : "error"}
                          size="small"
                        />
                      }
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Reason"
                      secondary={REASON_CODES.find(r => r.value === pendingAdjustment.reason)?.label || pendingAdjustment.reason}
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Reference Document"
                      secondary={pendingAdjustment.reference_doc || "N/A"}
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Comment"
                      secondary={pendingAdjustment.comment}
                    />
                  </ListItem>
                </List>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button
              onClick={handleCancelConfirm}
              startIcon={<Cancel />}
              disabled={submitMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmSubmit}
              variant="contained"
              color="primary"
              startIcon={submitMutation.isPending ? <CircularProgress size={20} /> : <CheckCircle />}
              disabled={submitMutation.isPending}
            >
              {submitMutation.isPending ? "Submitting..." : "Confirm & Submit"}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </ProtectedPage>
  );
};

export default InventoryAdjustment;