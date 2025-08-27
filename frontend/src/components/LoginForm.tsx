'use client';

import React, { useState, useEffect } from 'react';
import { 
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { authService } from '../services/authService';

interface LoginFormProps {
  onLogin: (token: string, loginResponse?: any) => void;
}

interface LoginFormData {
  email: string;
  password: string;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { control, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    defaultValues: {
      email: '',
      password: ''
    }
  });
  const _router = useRouter(); // Prefixed unused router

  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await authService.loginWithEmail(data.email, data.password);
      
      // Store user info - removed redundant localStorage sets since AuthContext handles it
      onLogin(response.access_token, response);
    } catch (error: any) {
      // Better error handling to prevent flicker
      const errorMessage = error.message || error.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent sx={{ p: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom align="center">
          Standard Login
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          <Controller
            name="email"
            control={control}
            rules={{
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address'
              }
            }}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Email Address"
                type="email"
                variant="outlined"
                slotProps={{
                  inputLabel: {
                    shrink: field.value ? true : undefined
                  }
                }}
                error={!!errors.email}
                helperText={errors.email?.message}
                margin="normal"
                autoComplete="email"
                autoFocus
              />
            )}
          />

          <Controller
            name="password"
            control={control}
            rules={{
              required: 'Password is required'
            }}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                label="Password"
                type="password"
                variant="outlined"
                slotProps={{
                  inputLabel: {
                    shrink: field.value ? true : undefined
                  }
                }}
                error={!!errors.password}
                helperText={errors.password?.message}
                margin="normal"
                autoComplete="current-password"
              />
            )}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Login'}
          </Button>
        </Box>

        <Typography variant="body2" color="textSecondary" align="center">
          Use your email and password to login, or try OTP authentication for enhanced security.
        </Typography>
      </CardContent>
    </Card>
  );
};

export default LoginForm;