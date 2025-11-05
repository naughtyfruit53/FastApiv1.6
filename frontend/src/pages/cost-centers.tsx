// frontend/src/pages/cost-centers.tsx
import React, { useState, useEffect } from "react";
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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  LinearProgress,
  Tooltip,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Refresh,
  TrendingUp,
  TrendingDown,
  CorporateFare,
} from "@mui/icons-material";
import { SimpleTreeView } from "@mui/x-tree-view/SimpleTreeView";
import { TreeItem } from "@mui/x-tree-view/TreeItem";
import axios from "axios";

import { ProtectedPage } from '../components/ProtectedPage';
interface CostCenter {
  id: number;
  cost_center_code: string;
  cost_center_name: string;
  parent_cost_center_id?: number;
  level: number;
  budget_amount: number;
  actual_amount: number;
  is_active: boolean;
  department?: string;
  manager_id?: number;
  description?: string;
  created_at: string;
  updated_at: string;
}

interface CreateCostCenterData {
  cost_center_code: string;
  cost_center_name: string;
  parent_cost_center_id?: number;
  budget_amount: number;
  department?: string;
  manager_id?: number;
  description?: string;
}

const CostCenters: React.FC = () => {
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedCostCenter, setSelectedCostCenter] = useState<CostCenter | null>(null);
  // Create cost center form state
  const [createData, setCreateData] = useState<CreateCostCenterData>({
    cost_center_code: "",
    cost_center_name: "",
    budget_amount: 0,
    description: "",
  });

  const fetchCostCenters = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get("/api/v1/erp/cost-centers", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCostCenters(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch cost centers");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCostCenters();
  }, []);

  const handleCreateCostCenter = async () => {
    try {
      // Auto-generate code if not provided
      let finalCode = createData.cost_center_code;
      if (!finalCode) {
        finalCode = generateCostCenterCode();
      }

      const token = localStorage.getItem("token");
      await axios.post("/api/v1/erp/cost-centers", {
        ...createData,
        cost_center_code: finalCode
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCreateDialogOpen(false);
      setCreateData({
        cost_center_code: "",
        cost_center_name: "",
        budget_amount: 0,
        description: "",
      });
      setShowStandardNames(false);
      fetchCostCenters();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create cost center");
    }
  };

  const generateCostCenterCode = () => {
    // Generate code based on name or use sequential number
    const count = costCenters.length + 1;
    if (createData.cost_center_name) {
      // Extract first 3-4 letters from name
      const prefix = createData.cost_center_name
        .replace(/[^a-zA-Z]/g, '')
        .substring(0, 4)
        .toUpperCase();
      return `${prefix}${count.toString().padStart(3, '0')}`;
    }
    return `CC${count.toString().padStart(4, '0')}`;
  };

  const selectStandardCostCenter = (standard: typeof standardCostCenters[0]) => {
    setCreateData({
      ...createData,
      cost_center_code: standard.code,
      cost_center_name: standard.name,
      description: standard.description
    });
    setShowStandardNames(false);
  };

  // Stub for edit - implement API call as needed
  const handleEditCostCenter = async () => {
    if (selectedCostCenter) {
      try {
        const token = localStorage.getItem("token");
        await axios.put(`/api/v1/erp/cost-centers/${selectedCostCenter.id}`, selectedCostCenter, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setEditDialogOpen(false);
        setSelectedCostCenter(null);
        fetchCostCenters();
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to update cost center");
      }
    }
  };

  // Stub for delete - implement API call as needed
  const handleDeleteCostCenter = async (id: number) => {
    if (window.confirm("Are you sure you want to delete this cost center?")) {
      try {
        const token = localStorage.getItem("token");
        await axios.delete(`/api/v1/erp/cost-centers/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        fetchCostCenters();
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to delete cost center");
      }
    }
  };

  // Stub for view - e.g., open details modal
  const handleViewCostCenter = (cc: CostCenter) => {
    alert(`Viewing details for ${cc.cost_center_name}`);
    // Implement modal or navigation as needed
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const calculateVariance = (budget: number, actual: number) => {
    if (budget === 0) {
      return 0;
    }
    return ((actual - budget) / budget) * 100;
  };

  const getVarianceColor = (variance: number) => {
    if (Math.abs(variance) <= 5) {
      return "success";
    }
    if (Math.abs(variance) <= 15) {
      return "warning";
    }
    return "error";
  };

  const buildCostCenterTree = (
    costCenters: CostCenter[],
    parentId: number | null = null,
  ): CostCenter[] => {
    return costCenters
      .filter((cc) => cc.parent_cost_center_id === parentId)
      .map((cc) => ({
        ...cc,
        children: buildCostCenterTree(costCenters, cc.id),
      }));
  };

  const renderCostCenterTree = (costCenters: any[]) => {
    return costCenters.map((cc) => (
      <TreeItem
        key={cc.id}
        nodeId={cc.id.toString()}
        label={
          <Box display="flex" alignItems="center" sx={{ py: 1 }}>
            <CorporateFare sx={{ mr: 1, fontSize: 16 }} />
            <Typography variant="body2" sx={{ fontWeight: "medium" }}>
              {cc.cost_center_code} - {cc.cost_center_name}
            </Typography>
            <Chip
              label={cc.is_active ? "Active" : "Inactive"}
              color={cc.is_active ? "success" : "default"}
              size="small"
              sx={{ ml: 1 }}
            />
          </Box>
        }
      >
        {cc.children &&
          cc.children.length > 0 &&
          renderCostCenterTree(cc.children)}
      </TreeItem>
    ));
  };

  // Calculate totals
  const totalBudget = costCenters.reduce(
    (sum, cc) => sum + cc.budget_amount,
    0,
  );
  const totalActual = costCenters.reduce(
    (sum, cc) => sum + cc.actual_amount,
    0,
  );
  const totalVariance = calculateVariance(totalBudget, totalActual);
  const costCenterTree = buildCostCenterTree(costCenters);

  return (
    <ProtectedPage moduleKey="finance" action="read">
      ox sx={{ p: 3 }}>
      {/* Header */}
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Typography variant="h4" component="h1">
          Cost Centers
        </Typography>
        <Box>
          <Button
            startIcon={<Add />}
            variant="contained"
            onClick={() => setCreateDialogOpen(true)}
            sx={{ mr: 1 }}
          >
            New Cost Center
          </Button>
          <IconButton onClick={fetchCostCenters} color="primary">
            <Refresh />
          </IconButton>
        </Box>
      </Box>
      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Budget
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(totalBudget)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingDown color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Actual
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(totalActual)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <CorporateFare
                  color={getVarianceColor(totalVariance)}
                  sx={{ mr: 2 }}
                />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Overall Variance
                  </Typography>
                  <Typography
                    variant="h6"
                    color={`${getVarianceColor(totalVariance)}.main`}
                  >
                    {totalVariance.toFixed(2)}%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <Grid container spacing={3}>
        {/* Cost Center Hierarchy */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: 500, overflow: "auto" }}>
            <Typography variant="h6" gutterBottom>
              Cost Center Hierarchy
            </Typography>
            {loading ? (
              <CircularProgress />
            ) : (
              <SimpleTreeView>{renderCostCenterTree(costCenterTree)}</SimpleTreeView>
            )}
          </Paper>
        </Grid>
        {/* Cost Centers Table */}
        <Grid item xs={12} md={8}>
          <Paper>
            <TableContainer sx={{ maxHeight: 500 }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>Code</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Department</TableCell>
                    <TableCell align="right">Budget</TableCell>
                    <TableCell align="right">Actual</TableCell>
                    <TableCell align="right">Utilization</TableCell>
                    <TableCell align="right">Variance %</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={9} align="center">
                        <CircularProgress />
                      </TableCell>
                    </TableRow>
                  ) : costCenters.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={9} align="center">
                        No cost centers found
                      </TableCell>
                    </TableRow>
                  ) : (
                    costCenters.map((cc) => {
                      const variance = calculateVariance(
                        cc.budget_amount,
                        cc.actual_amount,
                      );
                      const utilization =
                        cc.budget_amount > 0
                          ? (cc.actual_amount / cc.budget_amount) * 100
                          : 0;
                      return (
                        <TableRow key={cc.id}>
                          <TableCell>{cc.cost_center_code}</TableCell>
                          <TableCell>
                            <Box>
                              <Typography variant="body2">
                                {cc.cost_center_name}
                              </Typography>
                              {cc.description && (
                                <Typography
                                  variant="caption"
                                  color="textSecondary"
                                >
                                  {cc.description}
                                </Typography>
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>{cc.department || "-"}</TableCell>
                          <TableCell align="right">
                            {formatCurrency(cc.budget_amount)}
                          </TableCell>
                          <TableCell align="right">
                            {formatCurrency(cc.actual_amount)}
                          </TableCell>
                          <TableCell align="right">
                            <Box sx={{ display: "flex", alignItems: "center" }}>
                              <LinearProgress
                                variant="determinate"
                                value={Math.min(utilization, 100)}
                                color={
                                  utilization > 100
                                    ? "error"
                                    : utilization > 80
                                      ? "warning"
                                      : "primary"
                                }
                                sx={{ width: 60, mr: 1 }}
                              />
                              <Typography variant="caption">
                                {utilization.toFixed(1)}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            <Typography
                              color={`${getVarianceColor(variance)}.main`}
                            >
                              {variance.toFixed(2)}%
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={cc.is_active ? "Active" : "Inactive"}
                              color={cc.is_active ? "success" : "default"}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Tooltip title="View Details">
                              <IconButton size="small" onClick={() => handleViewCostCenter(cc)}>
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Edit">
                              <IconButton
                                size="small"
                                onClick={() => {
                                  setSelectedCostCenter(cc);
                                  setEditDialogOpen(true);
                                }}
                              >
                                <Edit />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton size="small" color="error" onClick={() => handleDeleteCostCenter(cc.id)}>
                                <Delete />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
      {/* Create Cost Center Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create Cost Center</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => setShowStandardNames(!showStandardNames)}
              >
                {showStandardNames ? "Hide Standard Names" : "Choose from Standard Names"}
              </Button>
            </Grid>
            
            {showStandardNames && (
              <Grid item xs={12}>
                <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1, maxHeight: 200, overflow: 'auto' }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                    Quick Selection:
                  </Typography>
                  <Grid container spacing={1}>
                    {standardCostCenters.map((standard) => (
                      <Grid item xs={6} sm={4} key={standard.code}>
                        <Button
                          variant="outlined"
                          size="small"
                          fullWidth
                          onClick={() => selectStandardCostCenter(standard)}
                          sx={{ textAlign: 'left', justifyContent: 'flex-start' }}
                        >
                          {standard.name}
                        </Button>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              </Grid>
            )}

            <Grid item xs={12} sm={6}>
              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  label="Cost Center Code"
                  value={createData.cost_center_code}
                  onChange={(e) =>
                    setCreateData((prev) => ({
                      ...prev,
                      cost_center_code: e.target.value.toUpperCase(),
                    }))
                  }
                  helperText="Leave empty to auto-generate"
                />
                <Button
                  variant="outlined"
                  onClick={() => {
                    const code = generateCostCenterCode();
                    setCreateData({ ...createData, cost_center_code: code });
                  }}
                  sx={{ minWidth: 100 }}
                >
                  Auto
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Cost Center Name"
                value={createData.cost_center_name}
                onChange={(e) =>
                  setCreateData((prev) => ({
                    ...prev,
                    cost_center_name: e.target.value,
                  }))
                }
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Parent Cost Center</InputLabel>
                <Select
                  value={createData.parent_cost_center_id || ""}
                  onChange={(e) =>
                    setCreateData((prev) => ({
                      ...prev,
                      parent_cost_center_id:
                        (e.target.value as number) || undefined,
                    }))
                  }
                  label="Parent Cost Center"
                >
                  <MenuItem value="">None (Top Level)</MenuItem>
                  {costCenters.map((cc) => (
                    <MenuItem key={cc.id} value={cc.id}>
                      {cc.cost_center_code} - {cc.cost_center_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Department"
                value={createData.department || ""}
                onChange={(e) =>
                  setCreateData((prev) => ({
                    ...prev,
                    department: e.target.value,
                  }))
                }
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Budget Amount"
                value={createData.budget_amount}
                onChange={(e) =>
                  setCreateData((prev) => ({
                    ...prev,
                    budget_amount: parseFloat(e.target.value) || 0,
                  }))
                }
                inputProps={{ min: 0, step: 0.01 }}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={createData.description || ""}
                onChange={(e) =>
                  setCreateData((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateCostCenter} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
      {/* Edit Cost Center Dialog - Basic stub, expand as needed */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit Cost Center</DialogTitle>
        <DialogContent>
          {selectedCostCenter && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              {/* Add form fields similar to create, pre-filled with selectedCostCenter data */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Cost Center Name"
                  value={selectedCostCenter.cost_center_name}
                  onChange={(e) =>
                    setSelectedCostCenter((prev) => prev ? ({ ...prev, cost_center_name: e.target.value }) : null)
                  }
                />
              </Grid>
              {/* Add other fields as needed */}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleEditCostCenter} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
    </ProtectedPage>
  );
};
export default CostCenters;