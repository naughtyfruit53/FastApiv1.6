import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Switch,
  FormControlLabel,
} from "@mui/material";
import axios from "axios";

interface ChartAccount {
  id: number;
  account_code: string;
  account_name: string;
  account_type: string;
}

interface CreateBankAccountData {
  chart_account_id: number;
  bank_name: string;
  account_number: string;
  account_type: string;
  currency: string;
  opening_balance: number;
  is_default: boolean;
  auto_reconcile: boolean;
  branch_name?: string;
  ifsc_code?: string;
}

interface BankAccountModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const BankAccountModal: React.FC<BankAccountModalProps> = ({
  open,
  onClose,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chartAccounts, setChartAccounts] = useState<ChartAccount[]>([]);
  const [createData, setCreateData] = useState<CreateBankAccountData>({
    chart_account_id: 0,
    bank_name: "",
    account_number: "",
    account_type: "Savings",
    currency: "INR",
    opening_balance: 0,
    is_default: false,
    auto_reconcile: false,
    branch_name: "",
    ifsc_code: "",
  });

  const accountTypes = [
    "Savings",
    "Current",
    "Fixed Deposit",
    "Recurring Deposit",
    "NRI Account",
    "Overdraft",
    "Cash Credit",
  ];
  
  const currencies = ["INR", "USD", "EUR", "GBP", "AED", "SAR"];

  const fetchChartAccounts = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(
        "/api/v1/erp/chart-of-accounts?account_type=bank",
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      setChartAccounts(response.data);
    } catch (err: any) {
      console.error("Failed to fetch chart accounts:", err);
      setError("Failed to fetch chart accounts. Please try again.");
    }
  };

  useEffect(() => {
    if (open) {
      fetchChartAccounts();
    }
  }, [open]);

  const handleCreateBankAccount = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem("token");
      await axios.post("/api/v1/erp/bank-accounts", createData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      // Reset form
      setCreateData({
        chart_account_id: 0,
        bank_name: "",
        account_number: "",
        account_type: "Savings",
        currency: "INR",
        opening_balance: 0,
        is_default: false,
        auto_reconcile: false,
        branch_name: "",
        ifsc_code: "",
      });
      
      if (onSuccess) {
        onSuccess();
      }
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create bank account");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Add Bank Account</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <FormControl fullWidth required>
              <InputLabel>Chart Account</InputLabel>
              <Select
                value={createData.chart_account_id}
                onChange={(e) =>
                  setCreateData({
                    ...createData,
                    chart_account_id: Number(e.target.value),
                  })
                }
                label="Chart Account"
              >
                <MenuItem value={0}>
                  <em>Select Chart Account</em>
                </MenuItem>
                {chartAccounts.map((account) => (
                  <MenuItem key={account.id} value={account.id}>
                    {account.account_code} - {account.account_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Bank Name"
              value={createData.bank_name}
              onChange={(e) =>
                setCreateData({ ...createData, bank_name: e.target.value })
              }
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Branch Name"
              value={createData.branch_name}
              onChange={(e) =>
                setCreateData({ ...createData, branch_name: e.target.value })
              }
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Account Number"
              value={createData.account_number}
              onChange={(e) =>
                setCreateData({ ...createData, account_number: e.target.value })
              }
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="IFSC Code"
              value={createData.ifsc_code}
              onChange={(e) =>
                setCreateData({ ...createData, ifsc_code: e.target.value })
              }
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required>
              <InputLabel>Account Type</InputLabel>
              <Select
                value={createData.account_type}
                onChange={(e) =>
                  setCreateData({ ...createData, account_type: e.target.value })
                }
                label="Account Type"
              >
                {accountTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Currency</InputLabel>
              <Select
                value={createData.currency}
                onChange={(e) =>
                  setCreateData({ ...createData, currency: e.target.value })
                }
                label="Currency"
              >
                {currencies.map((currency) => (
                  <MenuItem key={currency} value={currency}>
                    {currency}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Opening Balance"
              type="number"
              value={createData.opening_balance}
              onChange={(e) =>
                setCreateData({
                  ...createData,
                  opening_balance: Number(e.target.value),
                })
              }
            />
          </Grid>
          
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={createData.is_default}
                  onChange={(e) =>
                    setCreateData({ ...createData, is_default: e.target.checked })
                  }
                />
              }
              label="Set as Default Account"
            />
          </Grid>
          
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={createData.auto_reconcile}
                  onChange={(e) =>
                    setCreateData({
                      ...createData,
                      auto_reconcile: e.target.checked,
                    })
                  }
                />
              }
              label="Enable Auto Reconciliation"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleCreateBankAccount}
          variant="contained"
          disabled={loading || !createData.chart_account_id || !createData.bank_name || !createData.account_number}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          Add Bank Account
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BankAccountModal;