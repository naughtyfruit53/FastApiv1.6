import React, { useState, useEffect } from 'react';
import { Autocomplete, TextField, Button, Dialog, DialogActions, DialogContent, DialogTitle, Snackbar, Alert, Box, CircularProgress } from '@mui/material';
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
  const [generatedLink, setGeneratedLink] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Load couriers + existing tracking when dialog OPENS
  useEffect(() => {
    if (open) {
      const loadData = async () => {
        setLoading(true);
        setError(null);
        setSelectedCourier(null);
        setTrackingNumber('');
        setGeneratedLink('');

        try {
          // Parallel load: couriers + existing tracking
          const [courierRes, trackingRes] = await Promise.all([
            api.get<Courier[]>('/transport/couriers'),
            dispatchService.getPurchaseOrderTracking(voucherId).catch(() => ({
              transporter_name: null,
              tracking_number: null,
              tracking_link: null,
            })),
          ]);

          setCouriers(courierRes.data);

          // If tracking exists, populate fields
          if (trackingRes.tracking_number || trackingRes.transporter_name) {
            setTrackingNumber(trackingRes.tracking_number || '');

            // Find courier by name (case-insensitive)
            let courier = courierRes.data.find(
              (c) => c.name.toLowerCase() === (trackingRes.transporter_name || '').toLowerCase()
            );

            if (courier) {
              setSelectedCourier(courier);
              setGeneratedLink(
                courier.trackingLink.replace('{tracking_number}', trackingRes.tracking_number || '')
              );
            } else if (trackingRes.transporter_name) {
              // Fallback for custom courier names
              const fallback = {
                name: trackingRes.transporter_name,
                trackingLink: trackingRes.tracking_link || '',
              };
              setSelectedCourier(fallback);
              setCouriers((prev) => [...prev, fallback]);
              setGeneratedLink(trackingRes.tracking_link || '');
            }
          }
        } catch (err: any) {
          setError('Failed to load couriers or tracking data');
          console.error(err);
        } finally {
          setLoading(false);
        }
      };

      loadData();
    }
  }, [open, voucherId]);

  const handleSubmit = async () => {
    if (!selectedCourier || !trackingNumber.trim()) {
      setError('Courier and Tracking Number are required');
      return;
    }

    setLoading(true);
    try {
      const finalLink = selectedCourier.trackingLink.replace('{tracking_number}', trackingNumber.trim());

      await dispatchService.updatePurchaseOrderTracking(voucherId, {
        transporter_name: selectedCourier.name,
        tracking_number: trackingNumber.trim(),
        tracking_link: finalLink,
      });

      setSuccess('Tracking details saved successfully!');
      setTimeout(onClose, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to save tracking details');
    } finally {
      setLoading(false);
    }
  };

  const handleTrackConsignment = () => {
    if (!selectedCourier || !trackingNumber.trim()) {
      setError('Please fill courier and tracking number first');
      return;
    }

    const url = selectedCourier.trackingLink.replace('{tracking_number}', trackingNumber.trim());
    navigator.clipboard.writeText(trackingNumber.trim());
    window.open(url, '_blank');
    setSuccess('Tracking number copied & link opened');
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <TrackingIcon color="primary" />
          Tracking Details — {voucherNumber}
        </Box>
      </DialogTitle>

      <DialogContent>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
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
              onChange={(_, newValue) => {
                setSelectedCourier(newValue);
                if (newValue && trackingNumber) {
                  setGeneratedLink(newValue.trackingLink.replace('{tracking_number}', trackingNumber));
                }
              }}
              renderInput={(params) => (
                <TextField {...params} label="Courier Name" margin="normal" required />
              )}
              noOptionsText="No couriers loaded"
            />

            <TextField
              label="Tracking Number"
              value={trackingNumber}
              onChange={(e) => {
                const num = e.target.value;
                setTrackingNumber(num);
                if (selectedCourier) {
                  setGeneratedLink(selectedCourier.trackingLink.replace('{tracking_number}', num));
                }
              }}
              fullWidth
              margin="normal"
              required
            />

            {generatedLink && (
              <TextField
                label="Generated Tracking Link"
                value={generatedLink}
                fullWidth
                margin="normal"
                disabled
                helperText="This link is saved automatically"
              />
            )}
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} disabled={loading}>Cancel</Button>
        <Button
          onClick={handleTrackConsignment}
          variant="outlined"
          disabled={loading || !selectedCourier || !trackingNumber.trim()}
        >
          Track Consignment
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading || !selectedCourier || !trackingNumber.trim()}
        >
          {loading ? <CircularProgress size={24} /> : 'Save'}
        </Button>
      </DialogActions>

      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
        <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>
      </Snackbar>

      <Snackbar open={!!success} autoHideDuration={4000} onClose={() => setSuccess(null)}>
        <Alert severity="success" onClose={() => setSuccess(null)}>{success}</Alert>
      </Snackbar>
    </Dialog>
  );
};

export default TrackingDetailsDialog;