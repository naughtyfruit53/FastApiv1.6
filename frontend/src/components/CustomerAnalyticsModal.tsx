// frontend/src/components/CustomerAnalyticsModal.tsx

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  IconButton,
  Box
} from '@mui/material';
import { Close } from '@mui/icons-material';
import CustomerAnalytics from './CustomerAnalytics';

interface CustomerAnalyticsModalProps {
  open: boolean;
  onClose: () => void;
  customerId: number;
  customerName?: string;
}

const CustomerAnalyticsModal: React.FC<CustomerAnalyticsModalProps> = ({
  open,
  onClose,
  customerId,
  customerName
}) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          height: '90vh',
          maxHeight: '90vh'
        }
      }}
    >
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        Customer Analytics
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{
            color: (theme) => theme.palette.grey[500],
          }}
        >
          <Close />
        </IconButton>
      </DialogTitle>
      
      <DialogContent dividers sx={{ p: 0 }}>
        <CustomerAnalytics customerId={customerId} customerName={customerName} />
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CustomerAnalyticsModal;