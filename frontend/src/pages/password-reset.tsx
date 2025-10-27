"use client";

// frontend/src/pages/password-reset.tsx

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import {
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  CircularProgress,
  IconButton,
  InputAdornment,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { useRouter } from "next/router";
import { passwordService } from "../services/authService";
import { useAuth } from "../context/AuthContext";

interface FormData {
  current_password?: string;
  new_password: string;
  confirm_password: string;
}

const PasswordResetPage: React.FC = () => {
  const { user, loading: authLoading, refreshUser, updateUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<FormData>();

  const new_password = watch("new_password");

  if (authLoading) {
    return <CircularProgress />;
  }

  if (!user) {
    router.push("/login");
    return null;
  }

  const isMandatory = user.must_change_password;

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await passwordService.changePassword(
        isMandatory ? null : data.current_password || null,
        data.new_password,
        data.confirm_password,
      );
      console.log("[PasswordResetPage] Password change response:", response); // ADDED FOR DEBUGGING
      updateUser({ must_change_password: false });
      setSuccess(true);
      await refreshUser();
      setTimeout(() => {
        router.push("/dashboard");
      }, 2000);
    } catch (err: any) {
      console.error("[PasswordResetPage] Password change error:", err); // ADDED FOR DEBUGGING
      let errorMessage = err.message || "Failed to change password";
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        maxWidth: 400,
        mx: "auto",
        mt: 8,
        p: 3,
        border: "1px solid #ddd",
        borderRadius: 2,
      }}
    >
      <Typography variant="h5" gutterBottom>
        {isMandatory ? "Required Password Change" : "Change Password"}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Password changed successfully! Redirecting...
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        {!isMandatory && (
          <TextField
            fullWidth
            label="Current Password"
            type={showCurrentPassword ? "text" : "password"}
            margin="normal"
            {...register("current_password", {
              required: "Current password is required",
            })}
            error={!!errors.current_password}
            helperText={errors.current_password?.message}
            disabled={loading}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle current password visibility"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    edge="end"
                  >
                    {showCurrentPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        )}

        <TextField
          fullWidth
          label="New Password"
          type={showNewPassword ? "text" : "password"}
          margin="normal"
          {...register("new_password", {
            required: "New password is required",
            minLength: {
              value: 8,
              message: "Password must be at least 8 characters",
            },
            pattern: {
              value:
                /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&].+$/,
              message:
                "Password must contain uppercase, lowercase, number, and special character",
            },
          })}
          error={!!errors.new_password}
          helperText={errors.new_password?.message}
          disabled={loading}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle new password visibility"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  edge="end"
                >
                  {showNewPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <TextField
          fullWidth
          label="Confirm New Password"
          type={showConfirmPassword ? "text" : "password"}
          margin="normal"
          {...register("confirm_password", {
            required: "Confirm password is required",
            validate: (value) =>
              value === new_password || "Passwords do not match",
          })}
          error={!!errors.confirm_password}
          helperText={errors.confirm_password?.message}
          disabled={loading}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle confirm password visibility"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  edge="end"
                >
                  {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : "Change Password"}
        </Button>
      </form>
    </Box>
  );
};

export default PasswordResetPage;