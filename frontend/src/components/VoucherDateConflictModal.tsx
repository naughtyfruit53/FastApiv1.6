// frontend/src/components/VoucherDateConflictModal.tsx

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert,
  Box,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { format, parseISO } from 'date-fns';

interface ConflictInfo {
  has_conflict: boolean;
  later_voucher_count: number;
  suggested_date: string;
  period: string;
  later_vouchers?: any[];
}

interface VoucherDateConflictModalProps {
  open: boolean;
  onClose: () => void;
  conflictInfo: ConflictInfo | null;
  onChangeDateToSuggested: () => void;
  onProceedAnyway: () => void;
  voucherType?: string;
}

/**
 * Modal to warn users about back-dated voucher conflicts
 * Shows when a user tries to create a voucher with a date earlier than existing vouchers
 */
const VoucherDateConflictModal: React.FC<VoucherDateConflictModalProps> = ({
  open,
  onClose,
  conflictInfo,
  onChangeDateToSuggested,
  onProceedAnyway,
  voucherType = 'voucher'
}) => {
  if (!conflictInfo?.has_conflict) return null;

  const formatDate = (dateString: string) => {
    try {
      return format(parseISO(dateString), 'MMM dd, yyyy');
    } catch {
      return dateString;
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
        }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1.5}>
          <WarningIcon color="warning" fontSize="large" />
          <Box>
            <Typography variant="h6" fontWeight="bold">
              Back-dated {voucherType.charAt(0).toUpperCase() + voucherType.slice(1)} Detected
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Numbering sequence conflict detected
            </Typography>
          </Box>
        </Box>
      </DialogTitle>
      
      <Divider />
      
      <DialogContent sx={{ pt: 3 }}>
        <Alert 
          severity="warning" 
          icon={<InfoOutlinedIcon fontSize="inherit" />}
          sx={{ mb: 3 }}
        >
          <Typography variant="body2" fontWeight="medium">
            You are creating a {voucherType} with a date earlier than{' '}
            <strong>{conflictInfo.later_voucher_count} existing {voucherType}(s)</strong>{' '}
            in the <Chip label={conflictInfo.period} size="small" color="warning" /> period.
          </Typography>
        </Alert>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" paragraph color="text.secondary">
            This will create a numbering discrepancy where vouchers with <strong>later dates</strong> 
            will have <strong>earlier voucher numbers</strong>, which can cause confusion in reporting 
            and auditing.
          </Typography>
        </Box>

        <Box 
          sx={{ 
            bgcolor: 'primary.50', 
            border: 1, 
            borderColor: 'primary.200',
            borderRadius: 1,
            p: 2,
            mb: 3 
          }}
        >
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <CalendarTodayIcon color="primary" fontSize="small" />
            <Typography variant="subtitle2" fontWeight="bold" color="primary.main">
              Recommended Action
            </Typography>
          </Box>
          <Typography variant="body2">
            Change the {voucherType} date to{' '}
            <strong>{formatDate(conflictInfo.suggested_date)}</strong>{' '}
            (the date of the last {voucherType} in this period) to maintain proper sequence.
          </Typography>
        </Box>

        <Box>
          <Typography variant="body2" fontWeight="medium" gutterBottom>
            Your Options:
          </Typography>
          <List dense>
            <ListItem>
              <ListItemText
                primary="1. Change to Suggested Date (Recommended)"
                secondary={`Automatically updates the date to ${formatDate(conflictInfo.suggested_date)} to avoid conflicts`}
                primaryTypographyProps={{ variant: 'body2', fontWeight: 'medium' }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="2. Proceed with Current Date"
                secondary="Continue with the entered date. This may affect reporting and require manual number adjustments for later vouchers."
                primaryTypographyProps={{ variant: 'body2', fontWeight: 'medium' }}
                secondaryTypographyProps={{ variant: 'caption', color: 'warning.main' }}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="3. Cancel and Review"
                secondary="Cancel this action and verify if the date is correct"
                primaryTypographyProps={{ variant: 'body2', fontWeight: 'medium' }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
            </ListItem>
          </List>
        </Box>
      </DialogContent>
      
      <Divider />
      
      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button 
          onClick={onClose}
          variant="outlined"
          color="inherit"
        >
          Cancel & Review
        </Button>
        <Button 
          onClick={onProceedAnyway}
          variant="outlined"
          color="warning"
          startIcon={<WarningIcon />}
        >
          Proceed Anyway
        </Button>
        <Button 
          onClick={onChangeDateToSuggested}
          variant="contained"
          color="primary"
          startIcon={<CalendarTodayIcon />}
          sx={{ ml: 'auto' }}
        >
          Use Suggested Date
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default VoucherDateConflictModal;
