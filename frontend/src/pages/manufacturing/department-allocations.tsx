// frontend/src/pages/manufacturing/department-allocations.tsx
/**
 * Department Material Allocations Page
 * Shows material allotted to departments and flow to mark returned items
 * in working/bad condition
 */

import React, { useState, useMemo } from "react";
import {
  Box,
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  IconButton,
  Tooltip,
  CircularProgress,
  Grid,
  Card,
  CardContent,
} from "@mui/material";
import {
  Refresh,
  AssignmentReturn,
  Inventory,
  CheckCircle,
  Warning,
  Search,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../lib/api";
import { ProtectedPage } from "../../components/ProtectedPage";
import DashboardLayout from "../../components/DashboardLayout";
import { DEFAULT_DEPARTMENTS } from "../../constants/ui";
import { useCurrency } from "../../hooks/useCurrency";

interface DepartmentAllocation {
  id: number;
  material_requisition_id: number;
  requisition_number: string;
  department: string;
  product_id: number;
  product_name: string;
  quantity_allocated: number;
  quantity_returned: number;
  quantity_pending: number;
  unit: string;
  allocated_date: string;
  allocated_by: string;
  status: "allocated" | "partially_returned" | "fully_returned";
  unit_value: number;
  total_value: number;
}

interface ReturnFormData {
  allocation_id: number;
  quantity_returned: number;
  condition: "working" | "damaged" | "scrap";
  return_notes: string;
}

const DepartmentAllocationsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { formatCurrency } = useCurrency();
  const [selectedDepartment, setSelectedDepartment] = useState<string>("");
  const [returnDialogOpen, setReturnDialogOpen] = useState(false);
  const [selectedAllocation, setSelectedAllocation] = useState<DepartmentAllocation | null>(null);
  const [returnForm, setReturnForm] = useState<ReturnFormData>({
    allocation_id: 0,
    quantity_returned: 0,
    condition: "working",
    return_notes: "",
  });
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch department allocations
  const {
    data: allocations,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["department-allocations", selectedDepartment],
    queryFn: async () => {
      const params = selectedDepartment ? { department: selectedDepartment } : {};
      const response = await api.get("/manufacturing/department-allocations", { params });
      return response.data;
    },
  });

  // Fetch departments list
  const { data: departments } = useQuery({
    queryKey: ["departments"],
    queryFn: async () => {
      try {
        const response = await api.get("/manufacturing/departments");
        return response.data;
      } catch {
        // Return default departments from constants if API fails
        return [...DEFAULT_DEPARTMENTS];
      }
    },
  });

  // Return material mutation
  const returnMutation = useMutation({
    mutationFn: async (data: ReturnFormData) => {
      const response = await api.post("/manufacturing/department-allocations/return", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["department-allocations"] });
      setReturnDialogOpen(false);
      setSelectedAllocation(null);
      setReturnForm({
        allocation_id: 0,
        quantity_returned: 0,
        condition: "working",
        return_notes: "",
      });
    },
  });

  const handleOpenReturnDialog = (allocation: DepartmentAllocation) => {
    setSelectedAllocation(allocation);
    setReturnForm({
      allocation_id: allocation.id,
      quantity_returned: allocation.quantity_pending,
      condition: "working",
      return_notes: "",
    });
    setReturnDialogOpen(true);
  };

  const handleReturnSubmit = () => {
    if (returnForm.quantity_returned > 0) {
      returnMutation.mutate(returnForm);
    }
  };

  const getStatusChip = (status: DepartmentAllocation["status"]) => {
    const config = {
      allocated: { label: "Allocated", color: "info" as const },
      partially_returned: { label: "Partial Return", color: "warning" as const },
      fully_returned: { label: "Fully Returned", color: "success" as const },
    };
    const { label, color } = config[status] || config.allocated;
    return <Chip label={label} color={color} size="small" />;
  };

  const getConditionColor = (condition: string) => {
    const colors: Record<string, "success" | "warning" | "error"> = {
      working: "success",
      damaged: "warning",
      scrap: "error",
    };
    return colors[condition] || "default";
  };

  // Filter allocations based on search - memoized for performance
  const filteredAllocations = useMemo(() => {
    if (!allocations) return [];
    const searchLower = searchQuery.toLowerCase();
    return allocations.filter((allocation: DepartmentAllocation) =>
      allocation.product_name.toLowerCase().includes(searchLower) ||
      allocation.requisition_number.toLowerCase().includes(searchLower) ||
      allocation.department.toLowerCase().includes(searchLower)
    );
  }, [allocations, searchQuery]);

  // Calculate summary stats - memoized
  const summaryStats = useMemo(() => ({
    totalAllocated: filteredAllocations.reduce((sum: number, a: DepartmentAllocation) => sum + a.quantity_allocated, 0),
    totalReturned: filteredAllocations.reduce((sum: number, a: DepartmentAllocation) => sum + a.quantity_returned, 0),
    totalPending: filteredAllocations.reduce((sum: number, a: DepartmentAllocation) => sum + a.quantity_pending, 0),
    totalValue: filteredAllocations.reduce((sum: number, a: DepartmentAllocation) => sum + (a.total_value || 0), 0),
  }), [filteredAllocations]);

  if (error) {
    return (
      <ProtectedPage moduleKey="manufacturing" action="read">
        <Container maxWidth="xl">
          <Alert severity="error" sx={{ mt: 4 }}>
            Error loading department allocations: {(error as Error).message}
          </Alert>
        </Container>
      </ProtectedPage>
    );
  }

  return (
    <ProtectedPage moduleKey="manufacturing" action="read">
      <DashboardLayout title="Department Material Allocations">
        <Container maxWidth="xl">
          {/* Summary Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Allocated
                  </Typography>
                  <Typography variant="h5" color="info.main">
                    {summaryStats.totalAllocated}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Returned
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {summaryStats.totalReturned}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Pending Returns
                  </Typography>
                  <Typography variant="h5" color="warning.main">
                    {summaryStats.totalPending}
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
                  <Typography variant="h5" color="primary.main">
                    {formatCurrency(summaryStats.totalValue)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Filters */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "center" }}>
              <TextField
                placeholder="Search by product, requisition..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                size="small"
                sx={{ minWidth: 250 }}
                InputProps={{
                  startAdornment: <Search sx={{ color: "text.secondary", mr: 1 }} />,
                }}
              />
              <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel>Department</InputLabel>
                <Select
                  value={selectedDepartment}
                  label="Department"
                  onChange={(e) => setSelectedDepartment(e.target.value)}
                >
                  <MenuItem value="">All Departments</MenuItem>
                  {(departments || []).map((dept: string) => (
                    <MenuItem key={dept} value={dept}>
                      {dept}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => refetch()}
              >
                Refresh
              </Button>
            </Box>
          </Paper>

          {/* Allocations Table */}
          <TableContainer component={Paper}>
            {isLoading ? (
              <Box sx={{ p: 4, display: "flex", justifyContent: "center" }}>
                <CircularProgress />
              </Box>
            ) : filteredAllocations.length === 0 ? (
              <Box sx={{ p: 4, textAlign: "center" }}>
                <Inventory sx={{ fontSize: 64, color: "text.disabled", mb: 2 }} />
                <Typography color="text.secondary">
                  No department allocations found
                </Typography>
              </Box>
            ) : (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Requisition #</TableCell>
                    <TableCell>Department</TableCell>
                    <TableCell>Product</TableCell>
                    <TableCell align="right">Allocated</TableCell>
                    <TableCell align="right">Returned</TableCell>
                    <TableCell align="right">Pending</TableCell>
                    <TableCell align="right">Value</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredAllocations.map((allocation: DepartmentAllocation) => (
                    <TableRow key={allocation.id} hover>
                      <TableCell>{allocation.requisition_number}</TableCell>
                      <TableCell>{allocation.department}</TableCell>
                      <TableCell>{allocation.product_name}</TableCell>
                      <TableCell align="right">
                        {allocation.quantity_allocated} {allocation.unit}
                      </TableCell>
                      <TableCell align="right">
                        {allocation.quantity_returned} {allocation.unit}
                      </TableCell>
                      <TableCell align="right">
                        <Typography
                          color={allocation.quantity_pending > 0 ? "warning.main" : "success.main"}
                          fontWeight={allocation.quantity_pending > 0 ? 600 : 400}
                        >
                          {allocation.quantity_pending} {allocation.unit}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(allocation.total_value || 0)}
                      </TableCell>
                      <TableCell>
                        {new Date(allocation.allocated_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{getStatusChip(allocation.status)}</TableCell>
                      <TableCell>
                        {allocation.quantity_pending > 0 && (
                          <Tooltip title="Record Return">
                            <IconButton
                              color="primary"
                              size="small"
                              onClick={() => handleOpenReturnDialog(allocation)}
                            >
                              <AssignmentReturn />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </TableContainer>

          {/* Return Dialog */}
          <Dialog
            open={returnDialogOpen}
            onClose={() => setReturnDialogOpen(false)}
            maxWidth="sm"
            fullWidth
          >
            <DialogTitle>Record Material Return</DialogTitle>
            <DialogContent>
              {selectedAllocation && (
                <Box sx={{ pt: 2 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    <strong>Product:</strong> {selectedAllocation.product_name}
                    <br />
                    <strong>Department:</strong> {selectedAllocation.department}
                    <br />
                    <strong>Pending Quantity:</strong> {selectedAllocation.quantity_pending}{" "}
                    {selectedAllocation.unit}
                  </Typography>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        label="Quantity Returned"
                        type="number"
                        fullWidth
                        value={returnForm.quantity_returned}
                        onChange={(e) =>
                          setReturnForm({
                            ...returnForm,
                            quantity_returned: Math.min(
                              Number(e.target.value),
                              selectedAllocation.quantity_pending
                            ),
                          })
                        }
                        inputProps={{
                          min: 0,
                          max: selectedAllocation.quantity_pending,
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Condition</InputLabel>
                        <Select
                          value={returnForm.condition}
                          label="Condition"
                          onChange={(e) =>
                            setReturnForm({
                              ...returnForm,
                              condition: e.target.value as "working" | "damaged" | "scrap",
                            })
                          }
                        >
                          <MenuItem value="working">
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                              <CheckCircle color="success" fontSize="small" />
                              Working Condition
                            </Box>
                          </MenuItem>
                          <MenuItem value="damaged">
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                              <Warning color="warning" fontSize="small" />
                              Damaged
                            </Box>
                          </MenuItem>
                          <MenuItem value="scrap">
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                              <Warning color="error" fontSize="small" />
                              Scrap
                            </Box>
                          </MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        label="Return Notes"
                        fullWidth
                        multiline
                        rows={3}
                        value={returnForm.return_notes}
                        onChange={(e) =>
                          setReturnForm({
                            ...returnForm,
                            return_notes: e.target.value,
                          })
                        }
                        placeholder="Add any notes about the returned material..."
                      />
                    </Grid>
                  </Grid>
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setReturnDialogOpen(false)}>Cancel</Button>
              <Button
                variant="contained"
                onClick={handleReturnSubmit}
                disabled={returnMutation.isPending || returnForm.quantity_returned <= 0}
              >
                {returnMutation.isPending ? (
                  <CircularProgress size={20} />
                ) : (
                  "Record Return"
                )}
              </Button>
            </DialogActions>
          </Dialog>
        </Container>
      </DashboardLayout>
    </ProtectedPage>
  );
};

export default DepartmentAllocationsPage;
