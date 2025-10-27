// frontend/src/pages/expense-analysis.tsx
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
  TextField,
} from "@mui/material";
import { Refresh, Download, Print } from "@mui/icons-material";
import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import axios from "axios";
import { formatCurrency } from "../utils/currencyUtils";

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface ExpenseData {
  period: {
    start_date: string;
    end_date: string;
  };
  expenses: Array<{
    account_code: string;
    account_name: string;
    amount: number;
    parent_account: string;
    percentage: number;
  }>;
  summary: {
    total_expenses: number;
    expense_count: number;
    top_expense: {
      account_code: string;
      account_name: string;
      amount: number;
      percentage: number;
    } | null;
  };
}

const ExpenseAnalysisPage: React.FC = () => {
  const [data, setData] = useState<ExpenseData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periodMonths, setPeriodMonths] = useState(6);

  const fetchExpenseData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get("/api/v1/finance/analytics/expense-analysis", {
        params: { period_months: periodMonths },
        headers: { Authorization: `Bearer ${token}` },
      });
      setData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch expense data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExpenseData();
  }, [periodMonths]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert
        severity="error"
        action={
          <Button color="inherit" size="small" onClick={fetchExpenseData}>
            Retry
          </Button>
        }
      >
        {error}
      </Alert>
    );
  }

  if (!data) {
    return null;
  }

  const topExpenses = data.expenses.slice(0, 10);
  
  const pieData = {
    labels: topExpenses.map((e) => e.account_name),
    datasets: [
      {
        data: topExpenses.map((e) => e.amount),
        backgroundColor: [
          "#f44336",
          "#e91e63",
          "#9c27b0",
          "#673ab7",
          "#3f51b5",
          "#2196f3",
          "#03a9f4",
          "#00bcd4",
          "#009688",
          "#4caf50",
        ],
        borderWidth: 1,
      },
    ],
  };

  const barData = {
    labels: topExpenses.map((e) => e.account_name),
    datasets: [
      {
        label: "Expense Amount",
        data: topExpenses.map((e) => e.amount),
        backgroundColor: "#f44336",
      },
    ],
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Expense Analysis
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <TextField
            type="number"
            label="Period (Months)"
            value={periodMonths}
            onChange={(e) => setPeriodMonths(parseInt(e.target.value))}
            size="small"
            sx={{ width: 150 }}
          />
          <IconButton onClick={fetchExpenseData} color="primary">
            <Refresh />
          </IconButton>
          <Button startIcon={<Download />} variant="outlined">
            Export
          </Button>
          <Button startIcon={<Print />} variant="outlined">
            Print
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Expenses
              </Typography>
              <Typography variant="h5" color="error.main">
                {formatCurrency(data.summary.total_expenses)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Expense Categories
              </Typography>
              <Typography variant="h5">{data.summary.expense_count}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Top Expense
              </Typography>
              {data.summary.top_expense && (
                <>
                  <Typography variant="h6" noWrap>
                    {data.summary.top_expense.account_name}
                  </Typography>
                  <Typography variant="body2" color="error.main">
                    {formatCurrency(data.summary.top_expense.amount)} (
                    {data.summary.top_expense.percentage.toFixed(1)}%)
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Expense Distribution (Top 10)
              </Typography>
              <Box sx={{ height: 350 }}>
                <Pie data={pieData} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Expense Breakdown (Top 10)
              </Typography>
              <Box sx={{ height: 350 }}>
                <Bar data={barData} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            All Expenses
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Account Code</TableCell>
                  <TableCell>Account Name</TableCell>
                  <TableCell>Parent Account</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell align="right">Percentage</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.expenses.map((expense, index) => (
                  <TableRow key={index}>
                    <TableCell>{expense.account_code}</TableCell>
                    <TableCell>{expense.account_name}</TableCell>
                    <TableCell>{expense.parent_account}</TableCell>
                    <TableCell align="right">
                      {formatCurrency(expense.amount)}
                    </TableCell>
                    <TableCell align="right">
                      {expense.percentage.toFixed(2)}%
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ExpenseAnalysisPage;
