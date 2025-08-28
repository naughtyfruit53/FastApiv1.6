// frontend/src/pages/cost-centers.tsx
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
  Tooltip
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Refresh,
  TrendingUp,
  TrendingDown,
  CorporateFare
} from '@mui/icons-material';
import { TreeView, TreeItem } from '@mui/x-tree-view';
import axios from 'axios';

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
    cost_center_code: '',
    cost_center_name: '',
    budget_amount: 0,
    description: ''
  });

  const fetchCostCenters = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/v1/erp/cost-centers', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCostCenters(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch cost centers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCostCenters();
  }, []);

  const handleCreateCostCenter = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('/api/v1/erp/cost-centers', createData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setCreateDialogOpen(false);
      setCreateData({
        cost_center_code: '',
        cost_center_name: '',
        budget_amount: 0,
        description: ''
      });
      fetchCostCenters();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create cost center');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const calculateVariance = (budget: number, actual: number) => {
    if (budget === 0) return 0;
    return ((actual - budget) / budget) * 100;
  };

  const getVarianceColor = (variance: number) => {
    if (Math.abs(variance) <= 5) return 'success';
    if (Math.abs(variance) <= 15) return 'warning';
    return 'error';
  };

  const buildCostCenterTree = (costCenters: CostCenter[], parentId: number | null = null): CostCenter[] => {
    return costCenters
      .filter(cc => cc.parent_cost_center_id === parentId)
      .map(cc => ({
        ...cc,
        children: buildCostCenterTree(costCenters, cc.id)
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
            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
              {cc.cost_center_code} - {cc.cost_center_name}
            </Typography>
            <Chip
              label={cc.is_active ? 'Active' : 'Inactive'}
              color={cc.is_active ? 'success' : 'default'}
              size="small"
              sx={{ ml: 1 }}
            />
          </Box>
        }
      >
        {cc.children && cc.children.length > 0 && renderCostCenterTree(cc.children)}
      </TreeItem>
    ));
  };

  // Calculate totals
  const totalBudget = costCenters.reduce((sum, cc) => sum + cc.budget_amount, 0);
  const totalActual = costCenters.reduce((sum, cc) => sum + cc.actual_amount, 0);
  const totalVariance = calculateVariance(totalBudget, totalActual);

  const costCenterTree = buildCostCenterTree(costCenters);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
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
                <CorporateFare color={getVarianceColor(totalVariance)} sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Overall Variance
                  </Typography>
                  <Typography variant="h6" color={`${getVarianceColor(totalVariance)}.main`}>
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
          <Paper sx={{ p: 2, height: 500, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Cost Center Hierarchy
            </Typography>
            {loading ? (
              <CircularProgress />
            ) : (
              <TreeView>
                {renderCostCenterTree(costCenterTree)}
              </TreeView>
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
                      const variance = calculateVariance(cc.budget_amount, cc.actual_amount);
                      const utilization = cc.budget_amount > 0 ? (cc.actual_amount / cc.budget_amount) * 100 : 0;
                      
                      return (
                        <TableRow key={cc.id}>
                          <TableCell>{cc.cost_center_code}</TableCell>
                          <TableCell>
                            <Box>
                              <Typography variant="body2">{cc.cost_center_name}</Typography>
                              {cc.description && (
                                <Typography variant="caption" color="textSecondary">
                                  {cc.description}
                                </Typography>
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>{cc.department || '-'}</TableCell>
                          <TableCell align="right">{formatCurrency(cc.budget_amount)}</TableCell>
                          <TableCell align="right">{formatCurrency(cc.actual_amount)}</TableCell>
                          <TableCell align="right">
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <LinearProgress
                                variant="determinate"
                                value={Math.min(utilization, 100)}
                                color={utilization > 100 ? 'error' : utilization > 80 ? 'warning' : 'primary'}
                                sx={{ width: 60, mr: 1 }}
                              />
                              <Typography variant="caption">
                                {utilization.toFixed(1)}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            <Typography color={`${getVarianceColor(variance)}.main`}>
                              {variance.toFixed(2)}%
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={cc.is_active ? 'Active' : 'Inactive'}
                              color={cc.is_active ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Tooltip title="View Details">
                              <IconButton size="small">
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
                              <IconButton size="small" color="error">
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
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Cost Center</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Cost Center Code"
                value={createData.cost_center_code}
                onChange={(e) => setCreateData(prev => ({ ...prev, cost_center_code: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Cost Center Name"
                value={createData.cost_center_name}
                onChange={(e) => setCreateData(prev => ({ ...prev, cost_center_name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Parent Cost Center</InputLabel>
                <Select
                  value={createData.parent_cost_center_id || ''}
                  onChange={(e) => setCreateData(prev => ({ ...prev, parent_cost_center_id: e.target.value as number || undefined }))}
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
                value={createData.department || ''}
                onChange={(e) => setCreateData(prev => ({ ...prev, department: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Budget Amount"
                value={createData.budget_amount}
                onChange={(e) => setCreateData(prev => ({ ...prev, budget_amount: parseFloat(e.target.value) || 0 }))}
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
                value={createData.description || ''}
                onChange={(e) => setCreateData(prev => ({ ...prev, description: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateCostCenter} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CostCenters;