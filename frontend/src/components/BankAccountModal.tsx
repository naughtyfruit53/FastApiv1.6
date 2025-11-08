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
import { apiClient } from "@/services/api/client"; // Import the configured apiClient
import AddEditAccountModal from "./AddEditAccountModal"; // Use the existing AddEditAccountModal

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

interface BankAccount extends CreateBankAccountData {
  id: number;
  current_balance: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  swift_code?: string;
}

interface BankAccountModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  account?: BankAccount | null;
  mode: 'add' | 'edit' | 'view';
}

const BankAccountModal: React.FC<BankAccountModalProps> = ({
  open,
  onClose,
  onSuccess,
  account,
  mode,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chartAccounts, setChartAccounts] = useState<ChartAccount[]>([]);
  const [openChartModal, setOpenChartModal] = useState(false); // State for chart account modal
  const [chartFormData, setChartFormData] = useState({
    account_code: "",
    account_type: "BANK",
    account_name: "",
    parent_account_id: null, // Reset to null
    opening_balance: 0,
    is_group: false,
    can_post: true,
    is_reconcilable: true,
    description: "",
    notes: "",
    is_active: true,
  });
  const accountTypesList = [
    { value: "ASSET", label: "Asset", color: "success" },
    { value: "LIABILITY", label: "Liability", color: "error" },
    { value: "EQUITY", label: "Equity", color: "info" },
    { value: "INCOME", label: "Income", color: "primary" },
    { value: "EXPENSE", label: "Expense", color: "warning" },
    { value: "BANK", label: "Bank", color: "secondary" },
    { value: "CASH", label: "Cash", color: "default" },
  ];
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
      console.log("Fetching chart accounts..."); // Debug log
      const response = await apiClient.get("/chart-of-accounts?account_type=BANK");
      console.log("Chart accounts response:", response.data); // Added for debugging
      setChartAccounts(response.data.items || []);
    } catch (err: any) {
      console.error("Failed to fetch chart accounts:", err);
      console.error("Error response:", err.response?.data); // Added for debugging
      setError("Failed to fetch chart accounts. Please check console for details.");
    }
  };

  useEffect(() => {
    if (open) {
      fetchChartAccounts();
      if (account) {
        setCreateData({
          chart_account_id: account.chart_account_id,
          bank_name: account.bank_name,
          account_number: account.account_number,
          account_type: account.account_type,
          currency: account.currency,
          opening_balance: account.opening_balance,
          is_default: account.is_default,
          auto_reconcile: account.auto_reconcile,
          branch_name: account.branch_name || "",
          ifsc_code: account.ifsc_code || "",
        });
      } else {
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
      }
    }
  }, [open, account]);

  const handleCreateOrUpdateBankAccount = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log("Creating/Updating bank account..."); // Debug log
      if (mode === 'add') {
        await apiClient.post("/erp/bank-accounts", createData);
      } else if (mode === 'edit' && account) {
        await apiClient.put(`/erp/bank-accounts/${account.id}`, createData);
      }
      
      if (onSuccess) {
        onSuccess();
      }
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to ${mode === 'add' ? 'create' : 'update'} bank account`);
    } finally {
      setLoading(false);
    }
  };

  const handleChartSubmit = async () => {
    if (!chartFormData.account_code.trim() || !chartFormData.account_name.trim()) {
      setError("Account code and name are required");
      return;
    }
    try {
      console.log(`Account type before send: ${chartFormData.account_type}`);
      const payload = { ...chartFormData };
      if (payload.account_type && typeof payload.account_type === "string") {
        payload.account_type = payload.account_type.toUpperCase();
      }
      console.log("Payload being sent to backend:", payload); // Debug log
      await apiClient.post("/chart-of-accounts", payload);
      fetchChartAccounts();
      setOpenChartModal(false);
      // Reset chart form
      setChartFormData({
        account_code: "",
        account_type: "BANK",
        account_name: "",
        parent_account_id: null, // Reset to null
        opening_balance: 0,
        is_group: false,
        can_post: true,
        is_reconcilable: true,
        description: "",
        notes: "",
        is_active: true,
      });
    } catch (err: any) {
      console.error("Failed to create chart account:", err);
      setError("Failed to create chart account: " + (err.response?.data?.detail || "Unknown error"));
    }
  };

  const handleOpenChartModal = () => {
    setOpenChartModal(true);
  };

  const handleClose = () => {
    setError(null);
    onClose();
  };

  const isFormValid = () => {
    return createData.chart_account_id && createData.bank_name && createData.account_number;
  };

  const onSubmit = () => {
    if (!isFormValid()) {
      alert("Chart Account, Bank Name, and Account Number are required.");
      return;
    }
    handleCreateOrUpdateBankAccount();
  };

  const title = mode === 'add' ? 'Add Bank Account' : mode === 'edit' ? 'Edit Bank Account' : 'View Bank Account';
  const isViewMode = mode === 'view';

  return (
    <Dialog open={open} onClose={handleClose} maxWidth={false} PaperProps={{ sx: { width: '360px' } }}>
      <DialogTitle sx={{ textAlign: 'center' }}>
        {title}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        <Grid container direction="column" alignItems="center" spacing={2} sx={{ mt: 1 }}>
          <Grid item sx={{ width: '315px' }}>
            <FormControl fullWidth required>
              <InputLabel>Chart Account *</InputLabel>
              <Select
                disabled={isViewMode}
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
                {!isViewMode && (
                  <MenuItem onClick={handleOpenChartModal}>
                    Create New Chart Account
                  </MenuItem>
                )}
              </Select>
            </FormControl>
            {chartAccounts.length === 0 && (
              <Alert severity="info" sx={{ mt: 1 }}>
                No bank chart accounts found. Please create a bank-type chart account first in the Chart of Accounts section.
              </Alert>
            )}
          </Grid>
          
          <Grid item sx={{ width: '315px' }}>
            <TextField
              disabled={isViewMode}
              fullWidth
              required
              label="Bank Name *"
              value={createData.bank_name}
              onChange={(e) =>
                setCreateData({ ...createData, bank_name: e.target.value })
              }
              error={!createData.bank_name}
              helperText={!createData.bank_name ? "Required" : ""}
            />
          </Grid>
          
          <Grid item sx={{ width: '315px' }}>
            <TextField
              disabled={isViewMode}
              fullWidth
              label="Branch Name"
              value={createData.branch_name}
              onChange={(e) =>
                setCreateData({ ...createData, branch_name: e.target.value })
              }
            />
          </Grid>
          
          <Grid item sx={{ width: '315px' }}>
            <TextField
              disabled={isViewMode}
              fullWidth
              required
              label="Account Number *"
              value={createData.account_number}
              onChange={(e) =>
                setCreateData({ ...createData, account_number: e.target.value })
              }
              error={!createData.account_number}
              helperText={!createData.account_number ? "Required" : ""}
            />
          </Grid>
          
          <Grid item sx={{ width: '315px' }}>
            <TextField
              disabled={isViewMode}
              fullWidth
              label="IFSC Code"
              value={createData.ifsc_code}
              onChange={(e) =>
                setCreateData({ ...createData, ifsc_code: e.target.value })
              }
            />
          </Grid>
          
          <Grid item sx={{ width: '315px' }}>
            <FormControl fullWidth required>
              <InputLabel>Account Type *</InputLabel>
              <Select
                disabled={isViewMode}
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
          
          <Grid item sx={{ width: '315px' }}>
            <FormControl fullWidth>
              <InputLabel>Currency</InputLabel>
              <Select
                disabled={isViewMode}
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
          
          <Grid item sx={{ width: '315px' }}>
            <TextField
              disabled={isViewMode}
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
          
          <Grid item sx={{ width: '315px' }}>
            <FormControlLabel
              control={
                <Switch
                  disabled={isViewMode}
                  checked={createData.is_default}
                  onChange={(e) =>
                    setCreateData({ ...createData, is_default: e.target.checked })
                  }
                />
              }
              label="Set as Default Account"
            />
          </Grid>
          
          <Grid item sx={{ width: '315px' }}>
            <FormControlLabel
              control={
                <Switch
                  disabled={isViewMode}
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
      {isViewMode ? (
        <DialogActions sx={{ justifyContent: 'center' }}>
          <Button onClick={handleClose}>
            Close
          </Button>
        </DialogActions>
      ) : (
        <DialogActions sx={{ justifyContent: 'center' }}>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={onSubmit}
            variant="contained"
            disabled={loading || !isFormValid()}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {mode === 'add' ? 'Add Bank Account' : 'Save Changes'}
          </Button>
        </DialogActions>
      )}
      <AddEditAccountModal 
        open={openChartModal} 
        onClose={() => setOpenChartModal(false)} 
        formData={chartFormData}
        setFormData={setChartFormData}
        accounts={chartAccounts.filter(acc => acc.account_type === "BANK")} // Filter for bank parents
        accountTypes={accountTypesList}
        selectedAccount={null} // Add mode
        handleSubmit={handleChartSubmit}
      />
    </Dialog>
  );
};

export default BankAccountModal;