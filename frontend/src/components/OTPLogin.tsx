'use client';

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Container
} from '@mui/material';
import { useForm, FieldErrors } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { authService } from '../services/authService';

interface OTPLoginProps {
  onLogin: (token: string, loginResponse?: any) => void;
}

interface EmailFormData {
  email: string;
}

interface OTPFormData {
  otp: string;
}

const OTPLogin: React.FC<OTPLoginProps> = ({ onLogin }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [userEmail, setUserEmail] = useState('');
  
  const emailForm = useForm<EmailFormData>();
  const otpForm = useForm<OTPFormData>();
  const _router = useRouter(); // Prefixed unused router

  const steps = ['Enter Email', 'Verify OTP'];

  const handleEmailSubmit = async (data: EmailFormData) => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const response = await authService.requestOTP(data.email);
      setUserEmail(data.email);
      setSuccess(`OTP sent to ${data.email}. Please check your email.`);
      setActiveStep(1);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOTPSubmit = async (data: OTPFormData) => {
    setLoading(true);
    setError('');
    
    try {
      const _response = await authService.verifyOTP(userEmail, data.otp);
      setSuccess('Login successful!');
      
      // Login successful!
      localStorage.setItem('token', _response.access_token);
      localStorage.setItem('user_role', _response.user_role);
      // Organization context is managed by backend session only
      
      // Call parent callback with token and response
      onLogin(_response.access_token, _response);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setLoading(true);
    setError('');
    
    try {
      await authService.requestOTP(userEmail);
      setSuccess('OTP resent successfully!');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to resend OTP.');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setActiveStep(0);
    setError('');
    setSuccess('');
    emailForm.reset();
    otpForm.reset();
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Card>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom align="center">
              TRITIQ ERP
            </Typography>
            <Typography variant="h6" component="h2" gutterBottom align="center" color="textSecondary">
              OTP Authentication
            </Typography>

            <Stepper activeStep={activeStep} sx={{ mt: 3, mb: 4 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {success && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {success}
              </Alert>
            )}

            {activeStep === 0 && (
              <Box component="form" onSubmit={emailForm.handleSubmit(handleEmailSubmit)}>
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  {...emailForm.register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address'
                    }
                  })}
                  error={!!emailForm.formState.errors.email}
                  helperText={emailForm.formState.errors.email?.message}
                  margin="normal"
                  autoFocus
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  sx={{ mt: 3, mb: 2 }}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Send OTP'}
                </Button>

                <Typography variant="body2" color="textSecondary" align="center">
                  Enter your email address to receive an OTP for secure login.
                </Typography>
              </Box>
            )}

            {activeStep === 1 && (
              <Box component="form" onSubmit={otpForm.handleSubmit(handleOTPSubmit)}>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  Enter the 6-digit OTP sent to: <strong>{userEmail}</strong>
                </Typography>

                <TextField
                  fullWidth
                  label="OTP Code"
                  type="text"
                  inputProps={{ maxLength: 6, pattern: '[0-9]*' }}
                  {...otpForm.register('otp', {
                    required: 'OTP is required',
                    pattern: {
                      value: /^\d{6}$/,
                      message: 'OTP must be 6 digits'
                    }
                  })}
                  error={!!otpForm.formState.errors.otp}
                  helperText={otpForm.formState.errors.otp?.message}
                  margin="normal"
                  autoFocus
                />

                <Box sx={{ mt: 3, mb: 2, display: 'flex', gap: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={handleBack}
                    disabled={loading}
                    sx={{ flex: 1 }}
                  >
                    Back
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={loading}
                    sx={{ flex: 1 }}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Verify & Login'}
                  </Button>
                </Box>

                <Button
                  variant="text"
                  onClick={handleResendOTP}
                  disabled={loading}
                  fullWidth
                  sx={{ mt: 1 }}
                >
                  Resend OTP
                </Button>

                <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 2 }}>
                  OTP is valid for 10 minutes.
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default OTPLogin;