// frontend/src/components/FactoryReset.tsx

import React, { useState } from "react";
import {
  Button,
  TextField,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import { requestResetOTP, confirmReset } from "../services/resetService";

const FactoryReset: React.FC = () => {
  const [scope, setScope] = useState("organization");
  const [organizationId, setOrganizationId] = useState<number | undefined>(
    undefined,
  );
  const [otp, setOtp] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);

  const handleRequestOTP = async () => {
    setLoading(true);
    setError("");
    setMessage("");
    try {
      await requestResetOTP(scope, organizationId);
      setMessage("OTP sent to your email.");
      setOtpSent(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmReset = async () => {
    setLoading(true);
    setError("");
    setMessage("");
    try {
      await confirmReset(otp);
      setMessage("Data reset successful.");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 400, margin: "auto", padding: 2 }}>
      <Typography variant="h5" gutterBottom>
        Factory Reset
      </Typography>

      {!otpSent ? (
        <>
          <FormControl fullWidth margin="normal">
            <InputLabel>Scope</InputLabel>
            <Select
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              label="Scope"
            >
              <MenuItem value="organization">Organization</MenuItem>
              <MenuItem value="all">All Organizations</MenuItem>
            </Select>
          </FormControl>

          {scope === "organization" && (
            <TextField
              fullWidth
              margin="normal"
              label="Organization ID"
              type="number"
              value={organizationId || ""}
              onChange={(e) =>
                setOrganizationId(parseInt(e.target.value) || undefined)
              }
            />
          )}

          <Button
            variant="contained"
            color="primary"
            onClick={handleRequestOTP}
            disabled={loading}
            fullWidth
          >
            {loading ? <CircularProgress size={24} /> : "Request OTP"}
          </Button>
        </>
      ) : (
        <>
          <TextField
            fullWidth
            margin="normal"
            label="Enter OTP"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
          />

          <Button
            variant="contained"
            color="warning"
            onClick={handleConfirmReset}
            disabled={loading}
            fullWidth
          >
            {loading ? <CircularProgress size={24} /> : "Confirm Reset"}
          </Button>
        </>
      )}

      {message && (
        <Alert severity="success" sx={{ mt: 2 }}>
          {message}
        </Alert>
      )}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default FactoryReset;
