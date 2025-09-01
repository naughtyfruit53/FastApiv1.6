// frontend/src/components/UnifiedLoginForm.tsx
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
  FormControlLabel,
  Checkbox,
  IconButton,
  InputAdornment,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { authService } from '../services/authService';
interface UnifiedLoginFormProps {
  onLogin: (_token: string, _loginResponse?: any) => void;
}
interface LoginFormData {
  email: string;
  password: string;
  phoneNumber: string;
  otp: string;
}
const UnifiedLoginForm: React.FC<UnifiedLoginFormProps> = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [useOTP, setUseOTP] = useState(false);
  const [otpStep, setOtpStep] = useState(0); // 0: credentials, 1: OTP entry
  const [otpSent, setOtpSent] = useState(false);
const { control, handleSubmit, formState: { errors }, watch, setValue} = useForm<LoginFormData>({
    defaultValues: {
      email: '',
      password: '',
      phoneNumber: '',
      otp: ''
    }
  });
  const email = watch('email');
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  const handleOTPToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUseOTP(event.target.checked);
    setError('');
    setSuccess('');
    if (!event.target.checked) {
      setOtpStep(0);
      setOtpSent(false);
      setValue('otp', '');
      setValue('phoneNumber', '');
    }
  };
  const requestOTP = async (email: string, phoneNumber: string) => {
    try {
      setLoading(true);
      setError('');
      // Determine delivery method based on phone number
      const deliveryMethod = phoneNumber ? 'auto' : 'email';
      const response = await authService.requestOTP(email, phoneNumber, deliveryMethod);
      setSuccess(response.delivery_method 
        ? `OTP sent via ${response.delivery_method}. Please check your messages.`
        : `OTP sent to ${email}. Please check your email.`);
      setOtpSent(true);
      setOtpStep(1);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      if (useOTP) {
        if (!otpSent) {
          // Step 1: Request OTP
          await requestOTP(data.email, data.phoneNumber);
          return; // Don't continue to login yet
        } else {
          // Step 2: Verify OTP and login
          const response = await authService.verifyOTP(data.email, data.otp);
          setSuccess('Login successful!');
          // Add flag to indicate OTP login (so password change is not mandatory)
          response.otp_login = true;
          // Call parent callback with token and response
          onLogin(response.access_token, response);
        }
      } else {
        // Standard email/password login
        // Clear any existing invalid token before login attempt
        localStorage.removeItem('token');
        const response = await authService.loginWithEmail(data.email, data.password);
        onLogin(response.access_token, response);
      }
    } catch (error: any) {
      const errorMessage = error.message || error.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError(errorMessage);
      // Clear potentially invalid token on failure
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };
  const handleBackToCredentials = () => {
    setOtpStep(0);
    setOtpSent(false);
    setError('');
    setSuccess('');
    setValue('otp', '');
  };
  const handleResendOTP = async () => {
    const phoneNumber = watch('phoneNumber');
    await requestOTP(email, phoneNumber);
  };
  const steps = ['Login Details', 'Verify OTP'];
  return (
    <Card>
      <CardContent sx={{ p: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom align="center">
          {useOTP ? 'OTP Login' : 'Login'}
        </Typography>
        {useOTP && (
          <Stepper activeStep={otpStep} sx={{ mt: 2, mb: 3 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        )}
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
        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          {/* Email field - always visible */}
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
                disabled={otpSent && useOTP}
              />
            )}
          />
          {/* Password field - hidden when OTP is active and step > 0 */}
          {!useOTP && (
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
                  type={showPassword ? 'text' : 'password'}
                  variant="outlined"
                  slotProps={{
                    inputLabel: {
                      shrink: field.value ? true : undefined
                    }
                  }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={togglePasswordVisibility}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  error={!!errors.password}
                  helperText={errors.password?.message}
                  margin="normal"
                  autoComplete="current-password"
                />
              )}
            />
          )}
          {/* Phone number field - shown when OTP is enabled and not yet sent */}
          {useOTP && !otpSent && (
            <Controller
              name="phoneNumber"
              control={control}
              rules={{
                pattern: {
                  value: /^[\+]?[1-9][\d]{0,15}$/,
                  message: 'Enter a valid phone number with country code (e.g., +91XXXXXXXXXX)'
                }
              }}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Phone Number (Optional for WhatsApp OTP)"
                  type="tel"
                  variant="outlined"
                  placeholder="+91XXXXXXXXXX"
                  slotProps={{
                    inputLabel: {
                      shrink: field.value ? true : undefined
                    }
                  }}
                  error={!!errors.phoneNumber}
                  helperText={errors.phoneNumber?.message || "Include country code for WhatsApp OTP, or leave blank for email OTP"}
                  margin="normal"
                  autoComplete="tel"
                />
              )}
            />
          )}
          {/* OTP field - shown when OTP step is active */}
          {useOTP && otpSent && (
            <Controller
              name="otp"
              control={control}
              rules={{
                required: 'OTP is required',
                pattern: {
                  value: /^\d{6}$/,
                  message: 'OTP must be 6 digits'
                }
              }}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="OTP Code"
                  type="text"
                  inputProps={{ maxLength: 6, pattern: '[0-9]*' }}
                  variant="outlined"
                  slotProps={{
                    inputLabel: {
                      shrink: field.value ? true : undefined
                    }
                  }}
                  error={!!errors.otp}
                  helperText={errors.otp?.message}
                  margin="normal"
                  autoFocus
                />
              )}
            />
          )}
          {/* Login with OTP checkbox */}
          <FormControlLabel
            control={
              <Checkbox
                checked={useOTP}
                onChange={handleOTPToggle}
                name="useOTP"
                color="primary"
                disabled={loading}
              />
            }
            label="Login with OTP"
            sx={{ mt: 2, mb: 1 }}
          />
          {/* Action buttons */}
          {!useOTP || !otpSent ? (
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? (
                <CircularProgress size={24} />
              ) : (
                useOTP ? 'Send OTP' : 'Login'
              )}
            </Button>
          ) : (
            <Box sx={{ mt: 3, mb: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                onClick={handleBackToCredentials}
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
          )}
          {/* Resend OTP button */}
          {useOTP && otpSent && (
            <Button
              variant="text"
              onClick={handleResendOTP}
              disabled={loading}
              fullWidth
              sx={{ mt: 1 }}
            >
              Resend OTP
            </Button>
          )}
        </Box>
        <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 2 }}>
          {useOTP 
            ? "Enter your email and optional phone number to receive an OTP for secure login."
            : "Use your email and password to login, or try OTP authentication for enhanced security."
          }
        </Typography>
      </CardContent>
    </Card>
  );
};
export default UnifiedLoginForm;