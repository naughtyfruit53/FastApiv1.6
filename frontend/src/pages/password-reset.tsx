'use client';

// fastapi_migration/frontend/src/pages/password-reset.tsx

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button, TextField, Box, Typography, Alert, CircularProgress } from '@mui/material';
import { useRouter } from 'next/router';
import { passwordService } from '../services/authService';
import { useAuth } from '../context/AuthContext';

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
  const router = useRouter();
  const { register, handleSubmit, formState: { errors }, watch } = useForm<FormData>();

  const new_password = watch('new_password');

  if (authLoading) {
    return <CircularProgress />;
  }

  if (!user) {
    router.push('/login');
    return null;
  }

  const isMandatory = user.must_change_password;

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);

    try {
      await passwordService.changePassword(
        isMandatory ? null : (data.current_password || null),
        data.new_password,
        data.confirm_password
      );
      // Immediately update local state to prevent redirect loop
      updateUser({ must_change_password: false });
      setSuccess(true);
      // Refresh from server to sync any other changes
      await refreshUser();
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 400, mx: 'auto', mt: 8, p: 3, border: '1px solid #ddd', borderRadius: 2 }}>
      <Typography variant="h5" gutterBottom>
        {isMandatory ? 'Required Password Change' : 'Change Password'}
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>Password changed successfully! Redirecting...</Alert>}
      
      <form onSubmit={handleSubmit(onSubmit)}>
        {!isMandatory && (
          <TextField
            fullWidth
            label="Current Password"
            type="password"
            margin="normal"
            {...register('current_password', { required: 'Current password is required' })}
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
          {...register('new_password', {
            required: 'New password is required',
            minLength: { value: 8, message: 'Password must be at least 8 characters' },
            pattern: {
              value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&].+$/,
              message: 'Password must contain uppercase, lowercase, number, and special character'
            }
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
          {...register('confirm_password', {
            required: 'Confirm password is required',
            validate: (value) => value === new_password || 'Passwords do not match'
          })}
          error={!!errors.confirm_password}
          helperText={errors.confirm_password?.message}
          disabled={loading}
        />
        
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Change Password'}
        </Button>
      </form>
    </Box>
  );
};

export default PasswordResetPage;