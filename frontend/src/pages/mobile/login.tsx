import React, { useState } from 'react';
import { Box, TextField, Typography, Link, Divider, IconButton, InputAdornment } from '@mui/material';
import { Visibility, VisibilityOff, Phone, Email } from '@mui/icons-material';
import { 
  MobileLayout,
  MobileCard, 
  MobileButton 
} from '../../components/mobile';
import { useMobileDetection } from '../../hooks/useMobileDetection';

const MobileLogin: React.FC = () => {
  const { isMobile } = useMobileDetection();
  const [showPassword, setShowPassword] = useState(false);
  const [loginMethod, setLoginMethod] = useState<'email' | 'phone'>('email');
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);

  if (!isMobile) {
    // Redirect to desktop login or show desktop version
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate login
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setLoading(false);
    console.log('Login submitted:', formData);
  };

  const handleInputChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  return (
    <MobileLayout
      title="Sign In"
      showBottomNav={false}
      showMenuButton={false}
    >
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        minHeight: 'calc(100vh - 120px)',
        justifyContent: 'center',
        padding: 2
      }}>
        {/* Logo/Brand */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h3" sx={{ 
            fontWeight: 'bold', 
            color: 'primary.main',
            fontSize: '2.5rem',
            mb: 1
          }}>
            FastAPI
          </Typography>
          <Typography variant="body1" color="text.secondary">
            ERP Management System v1.6
          </Typography>
        </Box>

        {/* Login Form */}
        <MobileCard>
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* Login Method Toggle */}
              <Box sx={{ display: 'flex', gap: 1 }}>
                <MobileButton
                  variant={loginMethod === 'email' ? 'contained' : 'outlined'}
                  onClick={() => setLoginMethod('email')}
                  startIcon={<Email />}
                  fullWidth
                  size="small"
                >
                  Email
                </MobileButton>
                <MobileButton
                  variant={loginMethod === 'phone' ? 'contained' : 'outlined'}
                  onClick={() => setLoginMethod('phone')}
                  startIcon={<Phone />}
                  fullWidth
                  size="small"
                >
                  Phone
                </MobileButton>
              </Box>

              {/* Email/Phone Input */}
              {loginMethod === 'email' ? (
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange('email')}
                  required
                  autoComplete="email"
                  InputProps={{
                    style: { fontSize: '1rem' }
                  }}
                  sx={{
                    '& .MuiInputBase-root': {
                      minHeight: 56,
                    }
                  }}
                />
              ) : (
                <TextField
                  fullWidth
                  label="Phone Number"
                  type="tel"
                  value={formData.phone}
                  onChange={handleInputChange('phone')}
                  required
                  placeholder="+91 98765 43210"
                  InputProps={{
                    style: { fontSize: '1rem' }
                  }}
                  sx={{
                    '& .MuiInputBase-root': {
                      minHeight: 56,
                    }
                  }}
                />
              )}

              {/* Password Input */}
              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleInputChange('password')}
                required
                autoComplete="current-password"
                InputProps={{
                  style: { fontSize: '1rem' },
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                        sx={{ minWidth: 44, minHeight: 44 }}
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiInputBase-root': {
                    minHeight: 56,
                  }
                }}
              />

              {/* Forgot Password Link */}
              <Box sx={{ textAlign: 'right' }}>
                <Link href="#" variant="body2" sx={{ fontSize: '0.9rem' }}>
                  Forgot Password?
                </Link>
              </Box>

              {/* Login Button */}
              <MobileButton
                type="submit"
                variant="contained"
                fullWidth
                loading={loading}
                sx={{ minHeight: 56 }}
              >
                {loading ? 'Signing In...' : 'Sign In'}
              </MobileButton>

              {/* Divider */}
              <Divider sx={{ my: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  or
                </Typography>
              </Divider>

              {/* OTP Login */}
              <MobileButton
                variant="outlined"
                fullWidth
                sx={{ minHeight: 56 }}
              >
                Sign In with OTP
              </MobileButton>
            </Box>
          </form>
        </MobileCard>

        {/* Additional Links */}
        <Box sx={{ textAlign: 'center', mt: 3 }}>
          <Typography variant="body2" color="text.secondary">
            Need help? <Link href="#" sx={{ fontSize: '0.9rem' }}>Contact Support</Link>
          </Typography>
        </Box>

        {/* Version Info */}
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Version 1.6.0 • Build 2024.01.15
          </Typography>
        </Box>
      </Box>
    </MobileLayout>
  );
};

export default MobileLogin;