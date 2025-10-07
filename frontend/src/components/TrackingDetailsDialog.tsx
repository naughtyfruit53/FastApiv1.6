// frontend/src/components/TrackingDetailsDialog.tsx

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  CircularProgress,
  Alert,
  Typography,
  Link,
  IconButton
} from '@mui/material';
import { Close as CloseIcon, Launch as LaunchIcon } from '@mui/icons-material';
import api from '../lib/api';

interface TrackingDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  voucherType: 'purchase_order' | 'delivery_challan';
  voucherId: number;
  voucherNumber?: string;
}

interface TrackingDetails {
  transporter_name?: string;
  tracking_number?: string;
  tracking_link?: string;
}

const TrackingDetailsDialog: React.FC<TrackingDetailsDialogProps> = ({
  open,
  onClose,
  voucherType,
  voucherId,
  voucherNumber
}) => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [transporterName, setTransporterName] = useState('');
  const [trackingNumber, setTrackingNumber] = useState('');
  const [trackingLink, setTrackingLink] = useState('');

  // Fetch existing tracking details when dialog opens
  useEffect(() => {
    if (open && voucherId) {
      fetchTrackingDetails();
    }
  }, [open, voucherId]);

  const fetchTrackingDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = voucherType === 'purchase_order' 
        ? `/api/v1/purchase-orders/${voucherId}/tracking`
        : `/api/v1/delivery-challans/${voucherId}/tracking`;
      
      const response = await api.get(endpoint);
      
      if (response.data) {
        setTransporterName(response.data.transporter_name || '');
        setTrackingNumber(response.data.tracking_number || '');
        setTrackingLink(response.data.tracking_link || '');
      }
    } catch (err: any) {
      console.error('Error fetching tracking details:', err);
      // Don't show error for 404 (no tracking details yet)
      if (err.response?.status !== 404) {
        setError('Failed to load tracking details');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);
    
    try {
      const endpoint = voucherType === 'purchase_order' 
        ? `/api/v1/purchase-orders/${voucherId}/tracking`
        : `/api/v1/delivery-challans/${voucherId}/tracking`;
      
      await api.put(endpoint, null, {
        params: {
          transporter_name: transporterName || undefined,
          tracking_number: trackingNumber || undefined,
          tracking_link: trackingLink || undefined
        }
      });
      
      setSuccess('Tracking details saved successfully');
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err: any) {
      console.error('Error saving tracking details:', err);
      setError(err.response?.data?.detail || 'Failed to save tracking details');
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateAfterShipLink = () => {
    if (!trackingNumber || !transporterName) {
      setError('Please enter both transporter name and tracking number first');
      return;
    }
    
    // Generate AfterShip tracking link
    // Format: https://track.aftership.com/{courier-slug}/{tracking-number}
    // For now, use a generic format - in production, you'd map courier names to slugs
    const courierSlug = transporterName.toLowerCase().replace(/\s+/g, '-');
    const aftershipLink = `https://track.aftership.com/${courierSlug}/${trackingNumber}`;
    setTrackingLink(aftershipLink);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            Add/Edit Tracking Details
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
        {voucherNumber && (
          <Typography variant="caption" color="text.secondary">
            {voucherType === 'purchase_order' ? 'Purchase Order' : 'Delivery Challan'}: {voucherNumber}
          </Typography>
        )}
      </DialogTitle>
      
      <DialogContent>
        {loading ? (
          <Box display="flex" justifyContent="center" py={3}>
            <CircularProgress />
          </Box>
        ) : (
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            {error && (
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            )}
            
            {success && (
              <Alert severity="success" onClose={() => setSuccess(null)}>
                {success}
              </Alert>
            )}
            
            <TextField
              label="Transporter/Courier Name"
              value={transporterName}
              onChange={(e) => setTransporterName(e.target.value)}
              fullWidth
              placeholder="e.g., Blue Dart, DTDC, FedEx"
            />
            
            <TextField
              label="Tracking Number"
              value={trackingNumber}
              onChange={(e) => setTrackingNumber(e.target.value)}
              fullWidth
              placeholder="Enter tracking number"
            />
            
            <TextField
              label="Tracking Link (Optional)"
              value={trackingLink}
              onChange={(e) => setTrackingLink(e.target.value)}
              fullWidth
              placeholder="https://..."
              helperText="Enter custom tracking URL or use the button below to generate AfterShip link"
            />
            
            <Button
              variant="outlined"
              onClick={handleGenerateAfterShipLink}
              disabled={!trackingNumber || !transporterName}
            >
              Generate AfterShip Tracking Link
            </Button>
            
            {trackingLink && (
              <Box>
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  Preview:
                </Typography>
                <Link 
                  href={trackingLink} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  display="flex"
                  alignItems="center"
                  gap={0.5}
                >
                  {trackingLink}
                  <LaunchIcon fontSize="small" />
                </Link>
              </Box>
            )}
          </Box>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={saving}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave} 
          variant="contained" 
          disabled={saving || loading}
          startIcon={saving ? <CircularProgress size={16} /> : null}
        >
          {saving ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TrackingDetailsDialog;
