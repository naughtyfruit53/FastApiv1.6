// frontend/src/components/ExtendLicenseModal.tsx
import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Alert,
  CircularProgress,
} from "@mui/material";
import { organizationService } from "../services/organizationService";

interface ExtendLicenseModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  selectedOrg: any;
}

const ExtendLicenseModal: React.FC<ExtendLicenseModalProps> = ({
  open,
  onClose,
  onSuccess,
  selectedOrg,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [durationType, setDurationType] = useState<string>("");
  const [customNumber, setCustomNumber] = useState<number>(1);
  const [customUnit, setCustomUnit] = useState<string>("months");

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      let data: any = { extend: true };
      if (durationType === "custom") {
        data.license_type = "custom";
        data.custom_number = customNumber;
        data.custom_unit = customUnit;
      } else {
        data.license_type = durationType;
      }
      await organizationService.updateLicense(selectedOrg.id, data);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to extend license");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth={false}>
      <DialogTitle>Extend Validity</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error">{error}</Alert>}
        <FormControl fullWidth sx={{ mt: 2 }}>
          <InputLabel>Duration</InputLabel>
          <Select
            value={durationType}
            onChange={(e) => setDurationType(e.target.value as string)}
            label="Duration"
          >
            <MenuItem value="month_1">1 Month</MenuItem>
            <MenuItem value="month_3">3 Months</MenuItem>
            <MenuItem value="year_1">1 Year</MenuItem>
            <MenuItem value="perpetual">Perpetual</MenuItem>
            <MenuItem value="custom">Custom</MenuItem>
          </Select>
        </FormControl>
        {durationType === "custom" && (
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={6}>
              <TextField
                type="number"
                label="Number"
                value={customNumber}
                onChange={(e) => setCustomNumber(parseInt(e.target.value))}
                fullWidth
                inputProps={{ min: 1, max: 12 }}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Unit</InputLabel>
                <Select
                  value={customUnit}
                  onChange={(e) => setCustomUnit(e.target.value as string)}
                  label="Unit"
                >
                  <MenuItem value="days">Days</MenuItem>
                  <MenuItem value="months">Months</MenuItem>
                  <MenuItem value="years">Years</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading || !durationType}>
          {loading ? <CircularProgress size={24} /> : "Extend"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ExtendLicenseModal;
