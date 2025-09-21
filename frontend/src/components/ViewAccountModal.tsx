import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Typography,
  Switch,
  FormControlLabel,
} from "@mui/material";

interface ViewAccountModalProps {
  open: boolean;
  onClose: () => void;
  account: any;
}

const ViewAccountModal: React.FC<ViewAccountModalProps> = ({ open, onClose, account }) => {
  if (!account) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Account Details</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Account Code</Typography>
            <Typography>{account.account_code}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Account Type</Typography>
            <Typography>{account.account_type.charAt(0).toUpperCase() + account.account_type.slice(1)}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Account Name</Typography>
            <Typography>{account.account_name}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Parent Account</Typography>
            <Typography>{account.parent_account_id ? 'Yes' : 'None (Top Level)'}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Opening Balance</Typography>
            <Typography>₹{parseFloat(account.opening_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</Typography>
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={<Switch checked={account.is_group} disabled />}
              label="Is Group Account"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={<Switch checked={account.can_post} disabled />}
              label="Can Post Transactions"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={<Switch checked={account.is_reconcilable} disabled />}
              label="Is Reconcilable (Bank/Cash)"
            />
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Description</Typography>
            <Typography>{account.description || 'N/A'}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Notes</Typography>
            <Typography>{account.notes || 'N/A'}</Typography>
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={<Switch checked={account.is_active} disabled />}
              label="Active"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ViewAccountModal;