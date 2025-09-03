"use client";
import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  CircularProgress,
} from "@mui/material";
import { useForm } from "react-hook-form";
import { getFeatureFlag } from "../utils/config";
import { passwordService } from "../services/authService"; // ADDED IMPORT FOR PASSWORD SERVICE

interface PasswordChangeModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  isRequired?: boolean; // For mandatory password changes
}
interface PasswordFormData {
  current_password?: string;
  new_password: string;
  confirm_password: string;
}
const PasswordChangeModal: React.FC<PasswordChangeModalProps> = ({
  open,
  onClose,
  onSuccess,
  isRequired = false,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  // Check if password change functionality is enabled
  const passwordChangeEnabled = getFeatureFlag("passwordChange");
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<PasswordFormData>();
  const new_password = watch("new_password");
  const handleClose = () => {
    if (!isRequired || success) {
      reset();
      setError(null);
      setSuccess(false);
      onClose();
    }
  };
  const onSubmit = async (data: PasswordFormData) => {
    // Validation checks
    if (data.new_password !== data.confirm_password) {
      setError("New passwords do not match");
      return;
    }
    if (!isRequired && !data.current_password) {
      setError("Current password is required");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // Use passwordService instead of direct fetch - handles token update automatically
      await passwordService.changePassword(
        isRequired ? null : data.current_password!,
        data.new_password,
        data.confirm_password
      );
      setSuccess(true);
      if (onSuccess) {
        onSuccess();
      }
      if (!isRequired) {
        setTimeout(() => {
          handleClose();
        }, 2000);
      }
    } catch (err: any) {
      let errorMessage = "Failed to change password";
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      disableEscapeKeyDown={isRequired && !success}
    >
      <DialogTitle>
        {isRequired ? "Change Your Password" : "Change Password"}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          {isRequired && !success && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              You are required to change your password before continuing.
            </Alert>
          )}
          {!passwordChangeEnabled && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Password change functionality is temporarily disabled. Please
              contact your administrator.
            </Alert>
          )}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Password changed successfully!
              {isRequired && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  You can now continue using the application.
                </Typography>
              )}
            </Alert>
          )}
          {!success && passwordChangeEnabled && (
            <form onSubmit={handleSubmit(onSubmit)}>
              {!isRequired && (
                <TextField
                  fullWidth
                  label="Current Password"
                  type="password"
                  margin="normal"
                  {...register("current_password", {
                    required: "Current password is required",
                  })}
                  error={!!errors.current_password}
                  helperText={errors.current_password?.message}
                  disabled={loading}
                />
              )}
              <TextField
                fullWidth
                label="New Password"
                type="password"
                margin="normal"
                {...register("new_password", {
                  required: "New password is required",
                  minLength: {
                    value: 8,
                    message: "Password must be at least 8 characters long",
                  },
                  pattern: {
                    value:
                      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&].+$/,
                    message:
                      "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character",
                  },
                })}
                error={!!errors.new_password}
                helperText={errors.new_password?.message}
                disabled={loading}
              />
              <TextField
                fullWidth
                label="Confirm New Password"
                type="password"
                margin="normal"
                {...register("confirm_password", {
                  required: "Please confirm your new password",
                  validate: (value) =>
                    value === new_password || "Passwords do not match",
                })}
                error={!!errors.confirm_password}
                helperText={errors.confirm_password?.message}
                disabled={loading}
              />
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Password must be at least 8 characters long and contain at
                  least one uppercase letter, one lowercase letter, one number,
                  and one special character (@$!%*?&).
                </Typography>
              </Box>
            </form>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        {!isRequired && (
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
        )}
        {success && isRequired && (
          <Button onClick={handleClose} variant="contained">
            Continue
          </Button>
        )}
        {!success && passwordChangeEnabled && (
          <Button
            onClick={handleSubmit(onSubmit)}
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            Change Password
          </Button>
        )}
        {!passwordChangeEnabled &&
          (isRequired ? (
            <Button onClick={handleClose} variant="contained">
              Continue Without Changing Password
            </Button>
          ) : (
            <Button onClick={handleClose}>Close</Button>
          ))}
      </DialogActions>
    </Dialog>
  );
};
export default PasswordChangeModal;