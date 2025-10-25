// frontend/src/pages/financial-reports.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  TextField,
  IconButton,
  Divider,
} from "@mui/material";
import { Download, Print, Refresh } from "@mui/icons-material";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import axios from "axios";
import { formatCurrency } from "../utils/currencyUtils";
// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
);
interface TrialBalanceItem {
  account_code: string;
  account_name: string;
  debit_balance: number;
  credit_balance: number;
}
interface TrialBalance {
  trial_balance: TrialBalanceItem[];
  total_debits: number;
  total_credits: number;
  as_of_date: string;
  organization_id: number;
}
interface ProfitLossItem {
  account_code: string;
  account_name: string;
  amount: number;
}
interface ProfitLoss {
  income: ProfitLossItem[];
  expenses: ProfitLossItem[];
  total_income: number;
  total_expenses: number;
  net_profit_loss: number;
  from_date: string;
  to_date: string;
}
interface BalanceSheetItem {
  account_code: string;
  account_name: string;
  amount: number;
}
interface BalanceSheet {
  assets: BalanceSheetItem[];
  liabilities: BalanceSheetItem[];
  equity: BalanceSheetItem[];
  total_assets: number;
  total_liabilities: number;
  total_equity: number;
  as_of_date: string;
}
interface CashFlowItem {
  account_code: string;
  account_name: string;
  amount: number;
}
interface CashFlow {
  operating_activities: CashFlowItem[];
  investing_activities: CashFlowItem[];
  financing_activities: CashFlowItem[];
  net_operating_cash: number;
  net_investing_cash: number;
  net_financing_cash: number;
  net_cash_flow: number;
  opening_cash: number;
  closing_cash: number;
  from_date: string;
  to_date: string;
}
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}
function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`reports-tabpanel-${index}`}
      aria-labelledby={`reports-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}
const FinancialReports: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Date filters
  const [fromDate, setFromDate] = useState<Date | null>(
    new Date(new Date().getFullYear(), 0, 1),
  ); // Start of year
  const [toDate, setToDate] = useState<Date | null>(new Date()); // Today
  const [asOfDate, setAsOfDate] = useState<Date | null>(new Date()); // For balance sheet and trial balance
  // Report data
  const [trialBalance, setTrialBalance] = useState<TrialBalance | null>(null);
  const [profitLoss, setProfitLoss] = useState<ProfitLoss | null>(null);
  const [balanceSheet, setBalanceSheet] = useState<BalanceSheet | null>(null);
  const [cashFlow, setCashFlow] = useState<CashFlow | null>(null);
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };
  const formatDate = (date: Date | null) => {
    if (!date) {
      return "";
    }
    return date.toISOString().split("T")[0];
  };
  const fetchTrialBalance = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get("/api/v1/erp/trial-balance", {
        params: { as_of_date: formatDate(asOfDate) },
        headers: { Authorization: `Bearer ${token}` },
      });
      setTrialBalance(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch trial balance");
    } finally {
      setLoading(false);
    }
  };
  const fetchProfitLoss = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get("/api/v1/erp/profit-loss", {
        params: {
          from_date: formatDate(fromDate),
          to_date: formatDate(toDate),
        },
        headers: { Authorization: `Bearer ${token}` },
      });
      setProfitLoss(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch profit & loss");
    } finally {
      setLoading(false);
    }
  };
  const fetchBalanceSheet = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get("/api/v1/erp/balance-sheet", {
        params: { as_of_date: formatDate(asOfDate) },
        headers: { Authorization: `Bearer ${token}` },
      });
      setBalanceSheet(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch balance sheet");
    } finally {
      setLoading(false);
    }
  };
  const fetchCashFlow = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      // Note: This endpoint would need to be implemented in the backend
      const response = await axios.get("/api/v1/erp/cash-flow", {
        params: {
          from_date: formatDate(fromDate),
          to_date: formatDate(toDate),
        },
        headers: { Authorization: `Bearer ${token}` },
      });
      setCashFlow(response.data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Failed to fetch cash flow statement",
      );
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    if (activeTab === 0 && !trialBalance) {
      fetchTrialBalance();
    } else if (activeTab === 1 && !profitLoss) {
      fetchProfitLoss();
    } else if (activeTab === 2 && !balanceSheet) {
      fetchBalanceSheet();
    } else if (activeTab === 3 && !cashFlow) {
      fetchCashFlow();
    }
  }, [activeTab]);
  // Chart data for P&L
  const profitLossChartData = profitLoss
    ? {
        labels: ["Income", "Expenses", "Net Profit/Loss"],
        datasets: [
          {
            label: "Amount",
            data: [
              profitLoss.total_income,
              profitLoss.total_expenses,
              profitLoss.net_profit_loss,
            ],
            backgroundColor: [
              "#4caf50",
              "#f44336",
              profitLoss.net_profit_loss >= 0 ? "#4caf50" : "#f44336",
            ],
            borderWidth: 1,
          },
        ],
      }
    : null;
  // Chart data for Balance Sheet
  const balanceSheetChartData = balanceSheet
    ? {
        labels: ["Assets", "Liabilities", "Equity"],
        datasets: [
          {
            label: "Amount",
            data: [
              balanceSheet.total_assets,
              balanceSheet.total_liabilities,
              balanceSheet.total_equity,
            ],
            backgroundColor: ["#2196f3", "#ff9800", "#9c27b0"],
            borderWidth: 1,
          },
        ],
      }
    : null;
  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          mb={3}
        >
          <Typography variant="h4" component="h1">
            Financial Reports
          </Typography>
          <Box>
            <IconButton
              onClick={() => {
                if (activeTab === 0) {
                  fetchTrialBalance();
                } else if (activeTab === 1) {
                  fetchProfitLoss();
                } else if (activeTab === 2) {
                  fetchBalanceSheet();
                } else if (activeTab === 3) {
                  fetchCashFlow();
                }
              }}
              color="primary"
            >
              <Refresh />
            </IconButton>
            <Button startIcon={<Download />} variant="outlined" sx={{ ml: 1 }}>
              Export
            </Button>
            <Button startIcon={<Print />} variant="outlined" sx={{ ml: 1 }}>
              Print
            </Button>
          </Box>
        </Box>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {/* Tabs */}
        <Paper sx={{ width: "100%" }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            aria-label="financial reports tabs"
          >
            <Tab label="Trial Balance" />
            <Tab label="Profit & Loss" />
            <Tab label="Balance Sheet" />
            <Tab label="Cash Flow" />
          </Tabs>
          {/* Trial Balance */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <DatePicker
                        label="As of Date"
                        value={asOfDate}
                        onChange={setAsOfDate}
                        renderInput={(params) => (
                          <TextField {...params} fullWidth />
                        )}
                      />
                      <Button
                        onClick={fetchTrialBalance}
                        variant="contained"
                        sx={{ ml: 1 }}
                      >
                        Generate
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={8}>
                {trialBalance && (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Card>
                        <CardContent>
                          <Typography color="textSecondary" gutterBottom>
                            Total Debits
                          </Typography>
                          <Typography variant="h6" color="error.main">
                            {formatCurrency(trialBalance.total_debits)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={6}>
                      <Card>
                        <CardContent>
                          <Typography color="textSecondary" gutterBottom>
                            Total Credits
                          </Typography>
                          <Typography variant="h6" color="success.main">
                            {formatCurrency(trialBalance.total_credits)}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                )}
              </Grid>
            </Grid>
            {loading ? (
              <Box display="flex" justifyContent="center" my={4}>
                <CircularProgress />
              </Box>
            ) : trialBalance ? (
              <TableContainer component={Paper} sx={{ mt: 3 }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Account Code</TableCell>
                      <TableCell>Account Name</TableCell>
                      <TableCell align="right">Debit Balance</TableCell>
                      <TableCell align="right">Credit Balance</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {trialBalance.trial_balance.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>{item.account_code}</TableCell>
                        <TableCell>{item.account_name}</TableCell>
                        <TableCell align="right">
                          {item.debit_balance > 0
                            ? formatCurrency(item.debit_balance)
                            : "-"}
                        </TableCell>
                        <TableCell align="right">
                          {item.credit_balance > 0
                            ? formatCurrency(item.credit_balance)
                            : "-"}
                        </TableCell>
                      </TableRow>
                    ))}
                    <TableRow sx={{ borderTop: 2 }}>
                      <TableCell colSpan={2}>
                        <strong>Total</strong>
                      </TableCell>
                      <TableCell align="right">
                        <strong>
                          {formatCurrency(trialBalance.total_debits)}
                        </strong>
                      </TableCell>
                      <TableCell align="right">
                        <strong>
                          {formatCurrency(trialBalance.total_credits)}
                        </strong>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            ) : null}
          </TabPanel>
          {/* Profit & Loss */}
          <TabPanel value={activeTab} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={5}>
                        <DatePicker
                          label="From Date"
                          value={fromDate}
                          onChange={setFromDate}
                          renderInput={(params) => (
                            <TextField {...params} fullWidth />
                          )}
                        />
                      </Grid>
                      <Grid item xs={5}>
                        <DatePicker
                          label="To Date"
                          value={toDate}
                          onChange={setToDate}
                          renderInput={(params) => (
                            <TextField {...params} fullWidth />
                          )}
                        />
                      </Grid>
                      <Grid item xs={2}>
                        <Button
                          onClick={fetchProfitLoss}
                          variant="contained"
                          fullWidth
                        >
                          Generate
                        </Button>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                {profitLoss && profitLossChartData && (
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        P&L Summary
                      </Typography>
                      <Box sx={{ height: 200 }}>
                        <Bar data={profitLossChartData} />
                      </Box>
                    </CardContent>
                  </Card>
                )}
              </Grid>
            </Grid>
            {loading ? (
              <Box display="flex" justifyContent="center" my={4}>
                <CircularProgress />
              </Box>
            ) : profitLoss ? (
              <Grid container spacing={3} sx={{ mt: 1 }}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography
                        variant="h6"
                        color="success.main"
                        gutterBottom
                      >
                        Income
                      </Typography>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Account</TableCell>
                            <TableCell align="right">Amount</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {profitLoss.income.map((item, index) => (
                            <TableRow key={index}>
                              <TableCell>{item.account_name}</TableCell>
                              <TableCell align="right">
                                {formatCurrency(item.amount)}
                              </TableCell>
                            </TableRow>
                          ))}
                          <TableRow sx={{ borderTop: 1 }}>
                            <TableCell>
                              <strong>Total Income</strong>
                            </TableCell>
                            <TableCell align="right">
                              <strong>
                                {formatCurrency(profitLoss.total_income)}
                              </strong>
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" color="error.main" gutterBottom>
                        Expenses
                      </Typography>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Account</TableCell>
                            <TableCell align="right">Amount</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {profitLoss.expenses.map((item, index) => (
                            <TableRow key={index}>
                              <TableCell>{item.account_name}</TableCell>
                              <TableCell align="right">
                                {formatCurrency(item.amount)}
                              </TableCell>
                            </TableRow>
                          ))}
                          <TableRow sx={{ borderTop: 1 }}>
                            <TableCell>
                              <strong>Total Expenses</strong>
                            </TableCell>
                            <TableCell align="right">
                              <strong>
                                {formatCurrency(profitLoss.total_expenses)}
                              </strong>
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Box
                        display="flex"
                        justifyContent="center"
                        alignItems="center"
                      >
                        <Typography variant="h5">
                          Net{" "}
                          {profitLoss.net_profit_loss >= 0 ? "Profit" : "Loss"}:
                        </Typography>
                        <Typography
                          variant="h4"
                          color={
                            profitLoss.net_profit_loss >= 0
                              ? "success.main"
                              : "error.main"
                          }
                          sx={{ ml: 2 }}
                        >
                          {formatCurrency(Math.abs(profitLoss.net_profit_loss))}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            ) : null}
          </TabPanel>
          {/* Balance Sheet */}
          <TabPanel value={activeTab} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <DatePicker
                        label="As of Date"
                        value={asOfDate}
                        onChange={setAsOfDate}
                        renderInput={(params) => (
                          <TextField {...params} fullWidth />
                        )}
                      />
                      <Button
                        onClick={fetchBalanceSheet}
                        variant="contained"
                        sx={{ ml: 1 }}
                      >
                        Generate
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={8}>
                {balanceSheet && balanceSheetChartData && (
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Balance Sheet Summary
                      </Typography>
                      <Box sx={{ height: 200 }}>
                        <Bar data={balanceSheetChartData} />
                      </Box>
                    </CardContent>
                  </Card>
                )}
              </Grid>
            </Grid>
            {loading ? (
              <Box display="flex" justifyContent="center" my={4}>
                <CircularProgress />
              </Box>
            ) : balanceSheet ? (
              <Grid container spacing={3} sx={{ mt: 1 }}>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography
                        variant="h6"
                        color="primary.main"
                        gutterBottom
                      >
                        Assets
                      </Typography>
                      <Table size="small">
                        <TableBody>
                          {balanceSheet.assets.map((item, index) => (
                            <TableRow key={index}>
                              <TableCell>{item.account_name}</TableCell>
                              <TableCell align="right">
                                {formatCurrency(item.amount)}
                              </TableCell>
                            </TableRow>
                          ))}
                          <TableRow sx={{ borderTop: 1 }}>
                            <TableCell>
                              <strong>Total Assets</strong>
                            </TableCell>
                            <TableCell align="right">
                              <strong>
                                {formatCurrency(balanceSheet.total_assets)}
                              </strong>
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography
                        variant="h6"
                        color="warning.main"
                        gutterBottom
                      >
                        Liabilities
                      </Typography>
                      <Table size="small">
                        <TableBody>
                          {balanceSheet.liabilities.map((item, index) => (
                            <TableRow key={index}>
                              <TableCell>{item.account_name}</TableCell>
                              <TableCell align="right">
                                {formatCurrency(item.amount)}
                              </TableCell>
                            </TableRow>
                          ))}
                          <TableRow sx={{ borderTop: 1 }}>
                            <TableCell>
                              <strong>Total Liabilities</strong>
                            </TableCell>
                            <TableCell align="right">
                              <strong>
                                {formatCurrency(balanceSheet.total_liabilities)}
                              </strong>
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <Typography
                        variant="h6"
                        color="secondary.main"
                        gutterBottom
                      >
                        Equity
                      </Typography>
                      <Table size="small">
                        <TableBody>
                          {balanceSheet.equity.map((item, index) => (
                            <TableRow key={index}>
                              <TableCell>{item.account_name}</TableCell>
                              <TableCell align="right">
                                {formatCurrency(item.amount)}
                              </TableCell>
                            </TableRow>
                          ))}
                          <TableRow sx={{ borderTop: 1 }}>
                            <TableCell>
                              <strong>Total Equity</strong>
                            </TableCell>
                            <TableCell align="right">
                              <strong>
                                {formatCurrency(balanceSheet.total_equity)}
                              </strong>
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            ) : null}
          </TabPanel>
          {/* Cash Flow */}
          <TabPanel value={activeTab} index={3}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={5}>
                        <DatePicker
                          label="From Date"
                          value={fromDate}
                          onChange={setFromDate}
                          renderInput={(params) => (
                            <TextField {...params} fullWidth />
                          )}
                        />
                      </Grid>
                      <Grid item xs={5}>
                        <DatePicker
                          label="To Date"
                          value={toDate}
                          onChange={setToDate}
                          renderInput={(params) => (
                            <TextField {...params} fullWidth />
                          )}
                        />
                      </Grid>
                      <Grid item xs={2}>
                        <Button
                          onClick={fetchCashFlow}
                          variant="contained"
                          fullWidth
                        >
                          Generate
                        </Button>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                {cashFlow && (
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Net Cash Flow:
                        <Typography
                          component="span"
                          color={
                            cashFlow.net_cash_flow >= 0
                              ? "success.main"
                              : "error.main"
                          }
                          sx={{ ml: 1 }}
                        >
                          {formatCurrency(cashFlow.net_cash_flow)}
                        </Typography>
                      </Typography>
                    </CardContent>
                  </Card>
                )}
              </Grid>
            </Grid>
            {loading ? (
              <Box display="flex" justifyContent="center" my={4}>
                <CircularProgress />
              </Box>
            ) : cashFlow ? (
              <Card sx={{ mt: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Cash Flow Statement
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle1" gutterBottom>
                        Operating Activities
                      </Typography>
                      {cashFlow.operating_activities.map((item, index) => (
                        <Box
                          key={index}
                          display="flex"
                          justifyContent="space-between"
                        >
                          <Typography variant="body2">
                            {item.account_name}
                          </Typography>
                          <Typography variant="body2">
                            {formatCurrency(item.amount)}
                          </Typography>
                        </Box>
                      ))}
                      <Divider sx={{ my: 1 }} />
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body1">
                          <strong>Net Operating Cash</strong>
                        </Typography>
                        <Typography variant="body1">
                          <strong>
                            {formatCurrency(cashFlow.net_operating_cash)}
                          </strong>
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle1" gutterBottom>
                        Investing Activities
                      </Typography>
                      {cashFlow.investing_activities.map((item, index) => (
                        <Box
                          key={index}
                          display="flex"
                          justifyContent="space-between"
                        >
                          <Typography variant="body2">
                            {item.account_name}
                          </Typography>
                          <Typography variant="body2">
                            {formatCurrency(item.amount)}
                          </Typography>
                        </Box>
                      ))}
                      <Divider sx={{ my: 1 }} />
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body1">
                          <strong>Net Investing Cash</strong>
                        </Typography>
                        <Typography variant="body1">
                          <strong>
                            {formatCurrency(cashFlow.net_investing_cash)}
                          </strong>
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle1" gutterBottom>
                        Financing Activities
                      </Typography>
                      {cashFlow.financing_activities.map((item, index) => (
                        <Box
                          key={index}
                          display="flex"
                          justifyContent="space-between"
                        >
                          <Typography variant="body2">
                            {item.account_name}
                          </Typography>
                          <Typography variant="body2">
                            {formatCurrency(item.amount)}
                          </Typography>
                        </Box>
                      ))}
                      <Divider sx={{ my: 1 }} />
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="body1">
                          <strong>Net Financing Cash</strong>
                        </Typography>
                        <Typography variant="body1">
                          <strong>
                            {formatCurrency(cashFlow.net_financing_cash)}
                          </strong>
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            ) : null}
          </TabPanel>
        </Paper>
      </Box>
    </LocalizationProvider>
  );
};
export default FinancialReports;  