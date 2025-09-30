import React, { useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
} from "@mui/material";
import { getNextAccountCode } from "../services/masterService"; // Import the new service function

interface AddEditAccountModalProps {
  open: boolean;
  onClose: () => void;
  formData: any;
  setFormData: (data: any) => void;
  accounts: any[];
  accountTypes: { value: string; label: string; color: string }[];
  selectedAccount: any;
  handleSubmit: () => void;
}

const AddEditAccountModal: React.FC<AddEditAccountModalProps> = ({
  open,
  onClose,
  formData,
  setFormData,
  accounts,
  accountTypes,
  selectedAccount,
  handleSubmit,
}) => {
  const handleTypeChange = async (e: any) => {
    const newType = e.target.value.toUpperCase();
    console.log(newType); // Debug log for uppercased type
    setFormData({ ...formData, account_type: newType });

    // Auto-generate account code if creating new (not editing)
    if (!selectedAccount) {
      try {
        // Call backend to get next code
        const nextCode = await getNextAccountCode(newType);
        setFormData((prev: any) => ({ ...prev, account_code: nextCode }));
      } catch (error) {
        console.error("Failed to fetch next account code:", error);
        alert("Failed to generate account code. Using fallback method."); // Alert user for debugging
        // Fallback to client-side logic if API fails
        // Define minimum starting codes per type
        const minCodes: { [key: string]: number } = {
          CASH: 1000,
          BANK: 1100,
          ASSET: 1200,
          LIABILITY: 2000,
          EQUITY: 3000,
          INCOME: 4000,
          EXPENSE: 5000,
        };

        const minCode = minCodes[newType] || 9000;

        // Filter accounts by new type
        const typeAccounts = accounts.filter((acc: any) => acc.account_type === newType);
        
        // Find max code (assume 4-digit numeric codes)
        let maxCode = 0;
        typeAccounts.forEach((acc: any) => {
          const codeNum = parseInt(acc.account_code, 10);
          if (!isNaN(codeNum) && codeNum > maxCode) {
            maxCode = codeNum;
          }
        });
        
        // Calculate next code
        let nextCodeNum;
        if (maxCode < minCode) {
          nextCodeNum = minCode;
        } else {
          nextCodeNum = Math.floor(maxCode / 10) * 10 + 10;
        }

        // Suggest next code (pad to 4 digits)
        const nextCode = nextCodeNum.toString().padStart(4, '0');
        setFormData((prev: any) => ({ ...prev, account_code: nextCode }));
      }
    }
  };

  useEffect(() => {
    if (open && !selectedAccount && formData.account_type && !formData.account_code) {
      handleTypeChange({ target: { value: formData.account_type } });
    }
  }, [open, selectedAccount, formData.account_type, formData.account_code]);

  // Validate form before submit
  const isFormValid = () => {
    return formData.account_code && formData.account_name;
  };

  const onSubmit = () => {
    if (!isFormValid()) {
      alert("Account code and name are required.");
      return;
    }
    handleSubmit();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth={false} PaperProps={{ sx: { width: '360px' } }}>
      <DialogTitle sx={{ textAlign: 'center' }}>
        {selectedAccount ? "Edit Account" : "Add New Account"}
      </DialogTitle>
      <DialogContent>
        <Grid container direction="column" alignItems="center" spacing={2} sx={{ mt: 1 }}>
          <Grid item sx={{ width: '315px' }}>
            <TextField
              fullWidth
              label="Account Code *"
              value={formData?.account_code || ""}
              onChange={(e) =>
                setFormData({ ...formData, account_code: e.target.value })
              }
              required
              error={!formData?.account_code}
              helperText={!formData?.account_code ? "Required" : ""}
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <FormControl fullWidth>
              <InputLabel>Account Type</InputLabel>
              <Select
                value={formData?.account_type || ""}
                label="Account Type"
                onChange={handleTypeChange}
              >
                {accountTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <TextField
              fullWidth
              label="Account Name *"
              value={formData?.account_name || ""}
              onChange={(e) =>
                setFormData({ ...formData, account_name: e.target.value })
              }
              required
              error={!formData?.account_name}
              helperText={!formData?.account_name ? "Required" : ""}
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <FormControl fullWidth>
              <InputLabel>Parent Account</InputLabel>
              <Select
                value={formData?.parent_account_id || ""}
                label="Parent Account"
                onChange={(e) =>
                  setFormData({ ...formData, parent_account_id: e.target.value })
                }
              >
                <MenuItem value="">
                  <em>None (Top Level Account)</em>
                </MenuItem>
                {accounts
                  .filter((acc: any) => acc.account_type === formData?.account_type)
                  .map((account: any) => (
                    <MenuItem key={account.id} value={account.id}>
                      {account.account_code} - {account.account_name}
                    </MenuItem>
                  ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <TextField
              fullWidth
              label="Opening Balance"
              type="number"
              value={formData?.opening_balance || 0}
              onChange={(e) =>
                setFormData({ ...formData, opening_balance: Number(e.target.value) })
              }
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData?.is_group || false}
                  onChange={(e) =>
                    setFormData({ ...formData, is_group: e.target.checked })
                  }
                />
              }
              label="Is Group Account"
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData?.can_post || false}
                  onChange={(e) =>
                    setFormData({ ...formData, can_post: e.target.checked })
                  }
                />
              }
              label="Can Post Transactions"
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData?.is_reconcilable || false}
                  onChange={(e) =>
                    setFormData({ ...formData, is_reconcilable: e.target.checked })
                  }
                />
              }
              label="Is Reconcilable (Bank/Cash)"
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={2}
              value={formData?.description || ""}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={2}
              value={formData?.notes || ""}
              onChange={(e) =>
                setFormData({ ...formData, notes: e.target.value })
              }
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData?.is_active || false}
                  onChange={(e) =>
                    setFormData({ ...formData, is_active: e.target.checked })
                  }
                />
              }
              label="Active"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions sx={{ justifyContent: 'center' }}>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={onSubmit} variant="contained" disabled={!isFormValid()}>
          {selectedAccount ? "Update" : "Create"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddEditAccountModal;