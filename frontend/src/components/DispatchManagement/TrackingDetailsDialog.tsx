import React, { useState, useEffect } from 'react';
import { Autocomplete, TextField, Button, Dialog, DialogActions, DialogContent, DialogTitle, Snackbar, Alert, Box } from '@mui/material';
import { LocalShipping as TrackingIcon } from '@mui/icons-material';
import dispatchService from '../../services/dispatchService';
import api from '../../lib/api';

interface Courier {
  name: string;
  trackingLink: string;
}

interface TrackingDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  voucherId: number;
  voucherNumber: string;
}

const TrackingDetailsDialog: React.FC<TrackingDetailsDialogProps> = ({ open, onClose, voucherId, voucherNumber }) => {
  const [couriers, setCouriers] = useState<Courier[]>([]);
  const [selectedCourier, setSelectedCourier] = useState<Courier | null>(null);
  const [trackingNumber, setTrackingNumber] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const fetchCouriers = async () => {
      try {
        const response = await api.get<Courier[]>('/transport/couriers');
        setCouriers(response.data);
      } catch (err) {
        if (retryCount < 3) {
          setRetryCount(retryCount + 1);
          setTimeout(fetchCouriers, 1000);
        } else {
          setError('Failed to load couriers after retries');
        }
      }
    };
    if (open) {
      fetchCouriers();
    }
  }, [open, retryCount]);

  const handleSubmit = async () => {
    if (!selectedCourier || !trackingNumber) {
      setError('Courier Name and Tracking Number are required');
      return;
    }
    try {
      await dispatchService.updatePurchaseOrderTracking(voucherId, {
        transporter_name: selectedCourier.name,
        tracking_number: trackingNumber,
        tracking_link: selectedCourier.trackingLink.replace('{tracking_number}', trackingNumber),
      });
      setSuccess('Tracking details saved successfully');
      setTimeout(onClose, 2000);
    } catch (err) {
      setError('Failed to save tracking details');
    }
  };

  const handleTrackConsignment = () => {
    if (!selectedCourier || !trackingNumber) {
      setError('Please select a courier and enter a tracking number');
      return;
    }
    try {
      // Copy tracking number to clipboard
      navigator.clipboard.writeText(trackingNumber);
      // Construct and open tracking URL
      const trackingUrl = selectedCourier.trackingLink.replace('{tracking_number}', trackingNumber);
      window.open(trackingUrl, '_blank');
      setSuccess('Tracking number copied and URL opened');
    } catch (err) {
      setError('Failed to copy tracking number or open URL');
    }
  };

  const handleRetry = () => {
    setRetryCount(0);
    setError(null);
  };

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <TrackingIcon color="primary" />
            Add Tracking Details
          </Box>
        </DialogTitle>
        <DialogContent>
          <TextField
            label="Voucher Number"
            value={voucherNumber}
            fullWidth
            margin="normal"
            disabled
          />
          <Autocomplete
            options={couriers}
            getOptionLabel={(option) => option.name}
            value={selectedCourier}
            onChange={(event, newValue) => setSelectedCourier(newValue)}
            renderInput={(params) => <TextField {...params} label="Courier Name" margin="normal" />}
            disabled={couriers.length === 0}
          />
          <TextField
            label="Tracking Number"
            value={trackingNumber}
            onChange={(e) => setTrackingNumber(e.target.value)}
            fullWidth
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button onClick={handleTrackConsignment} variant="outlined">
            Track Consignment
          </Button>
          <Button onClick={handleSubmit} variant="contained" disabled={!selectedCourier || !trackingNumber}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error} {retryCount < 3 && typeof error === 'string' && error.includes('couriers') && <Button onClick={handleRetry}>Retry</Button>}
        </Alert>
      </Snackbar>
      <Snackbar open={!!success} autoHideDuration={6000} onClose={() => setSuccess(null)}>
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>
    </>
  );
};

export default TrackingDetailsDialog;