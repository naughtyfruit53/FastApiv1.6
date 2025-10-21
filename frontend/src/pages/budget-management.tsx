// frontend/src/pages/budget-management.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Add,
  Edit,
  Delete,
  Visibility,
  Warning,
  CheckCircle
} from '@mui/icons-material';
import DashboardLayout from '../components/DashboardLayout';
import api from '../lib/api';
import { formatCurrency } from "../utils/currencyUtils";

interface Budget {
  id: number;
  name: string;
  department: string;
  fiscal_year: string;
  total_budget: number;
  allocated: number;
  spent: number;
  remaining: number;
  status: 'active' | 'inactive' | 'exceeded';
}

const BudgetManagementPage: React.FC = () => {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newBudget, setNewBudget] = useState({
    name: '',
    department: '',
    fiscal_year: '2024-2025',
    total_budget: 0
  });

  const [summary, setSummary] = useState({
    totalBudget: 0,
    totalAllocated: 0,
    totalSpent: 0,
    totalRemaining: 0,
    utilizationRate: 0
  });

  useEffect(() => {
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
    try {
      setLoading(true);
      // Fetch cost centers as budget items for now
      const response = await api.get('/erp/cost-centers');
      const costCenters = response.data || [];

      // Transform to budget format
      const budgetData: Budget[] = costCenters.map((cc: any) => ({
        id: cc.id,
        name: cc.cost_center_name,
        department: cc.department || 'General',
        fiscal_year: '2024-2025',
        total_budget: cc.budget_amount || 0,
        allocated: cc.budget_amount || 0,
        spent: cc.actual_amount || 0,
        remaining: (cc.budget_amount || 0) - (cc.actual_amount || 0),
        status: (cc.actual_amount || 0) > (cc.budget_amount || 0) ? 'exceeded' : 'active'
      }));

      setBudgets(budgetData);

      // Calculate summary
      const totalBudget = budgetData.reduce((sum, b) => sum + b.total_budget, 0);
      const totalAllocated = budgetData.reduce((sum, b) => sum + b.allocated, 0);
      const totalSpent = budgetData.reduce((sum, b) => sum + b.spent, 0);
      const totalRemaining = totalBudget - totalSpent;
      const utilizationRate = totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0;

      setSummary({
        totalBudget,
        totalAllocated,
        totalSpent,
        totalRemaining,
        utilizationRate
      });
    } catch (error) {
      console.error('Error fetching budgets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBudget = async () => {
    try {
      // Create as cost center for now
      await api.post('/erp/cost-centers', {
        cost_center_code: newBudget.name.substring(0, 4).toUpperCase(),
        cost_center_name: newBudget.name,
        department: newBudget.department,
        budget_amount: newBudget.total_budget
      });
      setCreateDialogOpen(false);
      setNewBudget({
        name: '',
        department: '',
        fiscal_year: '2024-2025',
        total_budget: 0
      });
      fetchBudgets();
    } catch (error) {
      console.error('Error creating budget:', error);
    }
  };

  const getUtilizationColor = (percentage: number) => {
    if (percentage < 70) return 'success';
    if (percentage < 90) return 'warning';
    return 'error';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'exceeded':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <DashboardLayout
        title="Budget Management"
        subtitle="Plan and track organizational budgets"
      >
        <LinearProgress />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      title="Budget Management"
      subtitle="Plan, allocate, and monitor budgets across departments"
    >
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Budget
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                {formatCurrency(summary.totalBudget)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                FY 2024-2025
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <CheckCircle color="success" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Allocated
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                {formatCurrency(summary.totalAllocated)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {((summary.totalAllocated / summary.totalBudget) * 100).toFixed(1)}% of budget
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingDown color="warning" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Spent
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold" color="warning.main">
                {formatCurrency(summary.totalSpent)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {summary.utilizationRate.toFixed(1)}% utilized
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Warning color="info" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Remaining
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold" color="info.main">
                {formatCurrency(summary.totalRemaining)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {((summary.totalRemaining / summary.totalBudget) * 100).toFixed(1)}% available
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Budget Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Budget Allocations
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setCreateDialogOpen(true)}
                >
                  Create Budget
                </Button>
              </Box>

              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Budget Name</TableCell>
                      <TableCell>Department</TableCell>
                      <TableCell>Fiscal Year</TableCell>
                      <TableCell align="right">Total Budget</TableCell>
                      <TableCell align="right">Spent</TableCell>
                      <TableCell align="right">Remaining</TableCell>
                      <TableCell align="center">Utilization</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {budgets.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={9} align="center">
                          <Typography color="textSecondary" py={4}>
                            No budgets found. Create a budget to start tracking expenses.
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      budgets.map((budget) => {
                        const utilization = budget.total_budget > 0
                          ? (budget.spent / budget.total_budget) * 100
                          : 0;
                        return (
                          <TableRow key={budget.id} hover>
                            <TableCell>
                              <Typography fontWeight="600">{budget.name}</Typography>
                            </TableCell>
                            <TableCell>{budget.department}</TableCell>
                            <TableCell>{budget.fiscal_year}</TableCell>
                            <TableCell align="right" fontWeight="bold">
                              {formatCurrency(budget.total_budget)}
                            </TableCell>
                            <TableCell align="right">
                              {formatCurrency(budget.spent)}
                            </TableCell>
                            <TableCell align="right" fontWeight="bold">
                              {formatCurrency(budget.remaining)}
                            </TableCell>
                            <TableCell align="center">
                              <Box display="flex" alignItems="center" justifyContent="center">
                                <LinearProgress
                                  variant="determinate"
                                  value={Math.min(utilization, 100)}
                                  color={getUtilizationColor(utilization)}
                                  sx={{ width: 80, mr: 1 }}
                                />
                                <Typography variant="caption">
                                  {utilization.toFixed(0)}%
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={budget.status}
                                color={getStatusColor(budget.status)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell align="center">
                              <Tooltip title="View Details">
                                <IconButton size="small">
                                  <Visibility fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Edit">
                                <IconButton size="small">
                                  <Edit fontSize="small" />
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
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Create Budget Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Budget</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Budget Name"
                value={newBudget.name}
                onChange={(e) => setNewBudget({ ...newBudget, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Department"
                value={newBudget.department}
                onChange={(e) => setNewBudget({ ...newBudget, department: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Fiscal Year</InputLabel>
                <Select
                  value={newBudget.fiscal_year}
                  onChange={(e) => setNewBudget({ ...newBudget, fiscal_year: e.target.value })}
                  label="Fiscal Year"
                >
                  <MenuItem value="2023-2024">2023-2024</MenuItem>
                  <MenuItem value="2024-2025">2024-2025</MenuItem>
                  <MenuItem value="2025-2026">2025-2026</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Total Budget Amount"
                type="number"
                value={newBudget.total_budget}
                onChange={(e) => setNewBudget({ ...newBudget, total_budget: parseFloat(e.target.value) || 0 })}
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateBudget} variant="contained" disabled={!newBudget.name || !newBudget.total_budget}>
            Create Budget
          </Button>
        </DialogActions>
      </Dialog>
    </DashboardLayout>
  );
};

export default BudgetManagementPage;