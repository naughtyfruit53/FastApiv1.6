import React from "react";
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
  const handleTypeChange = (e: any) => {
    const newType = e.target.value;
    setFormData({ ...formData, account_type: newType });

    // Auto-generate account code if creating new (not editing)
    if (!selectedAccount) {
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
      
      // Suggest next code (increment by 10 for sub-group spacing)
      const nextCode = (maxCode + 10).toString().padStart(4, '0');
      setFormData((prev: any) => ({ ...prev, account_code: nextCode }));
    }
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
              value={formData.account_code}
              onChange={(e) =>
                setFormData({ ...formData, account_code: e.target.value })
              }
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <FormControl fullWidth>
              <InputLabel>Account Type</InputLabel>
              <Select
                value={formData.account_type}
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
              value={formData.account_name}
              onChange={(e) =>
                setFormData({ ...formData, account_name: e.target.value })
              }
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <FormControl fullWidth>
              <InputLabel>Parent Account</InputLabel>
              <Select
                value={formData.parent_account_id}
                label="Parent Account"
                onChange={(e) =>
                  setFormData({ ...formData, parent_account_id: e.target.value })
                }
              >
                <MenuItem value="">
                  <em>None (Top Level Account)</em>
                </MenuItem>
                {accounts
                  .filter((acc: any) => acc.account_type === formData.account_type)
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
              value={formData.opening_balance}
              onChange={(e) =>
                setFormData({ ...formData, opening_balance: Number(e.target.value) })
              }
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_group}
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
                  checked={formData.can_post}
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
                  checked={formData.is_reconcilable}
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
              value={formData.description}
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
              value={formData.notes}
              onChange={(e) =>
                setFormData({ ...formData, notes: e.target.value })
              }
            />
          </Grid>
          <Grid item sx={{ width: '315px' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
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
        <Button onClick={handleSubmit} variant="contained">
          {selectedAccount ? "Update" : "Create"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddEditAccountModal;