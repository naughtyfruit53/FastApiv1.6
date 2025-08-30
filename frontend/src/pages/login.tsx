'use client';

import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Container,
  Button,
  Checkbox,
  FormControlLabel,
  IconButton,
  InputAdornment
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import Image from 'next/image';
import { toast } from 'react-toastify';
import UnifiedLoginForm from '../components/UnifiedLoginForm';
import ForgotPasswordModal from '../components/ForgotPasswordModal';
import { useRouter } from 'next/router';
import { useAuth } from '../context/AuthContext';

const LoginPage: React.FC = () => {
  const [forgotPasswordOpen, setForgotPasswordOpen] = useState(false);
  const router = useRouter();
  const { login } = useAuth();

  const handleLogin = async (token: string, loginResponse?: any) => {
    console.log('[Login] Login successful, processing response:', {
      hasToken: !!token,
      hasLoginResponse: !!loginResponse,
      organizationId: loginResponse?.organization_id,
      userRole: loginResponse?.user_role,
      mustChangePassword: loginResponse?.must_change_password,
      isSuperAdmin: loginResponse?.user?.is_super_admin,
      timestamp: new Date().toISOString()
    });

    // Always save token to localStorage before anything else
    if (token) {
      localStorage.setItem('token', token);
    }
    
    try {
      console.log('[Login] Calling AuthContext login method to establish session');
      // Use AuthContext login method to establish full context before navigation
      await login(loginResponse);
      
      console.log('[Login] AuthContext login completed - session established');
      console.log('[Login] Current localStorage state:', {
        hasToken: !!localStorage.getItem('token'),
        hasUserRole: !!localStorage.getItem('user_role'),
        hasSuperAdminFlag: !!localStorage.getItem('is_super_admin')
      });
      
      // Check if password change is required (not mandatory for OTP login)
      if (loginResponse?.must_change_password && !loginResponse?.otp_login) {
        console.log('[Login] Password change required - redirecting to password reset');
        // Use hard reload to avoid SPA race condition - ensures token is present for AuthProvider's effect
        window.location.href = '/password-reset';
      } else {
        console.log('[Login] Login complete - redirecting to dashboard');
        // Use hard reload to avoid SPA race condition - ensures token is present for AuthProvider's effect
        window.location.href = '/dashboard';
      }
    } catch (error) {
      console.error('[Login] Failed to establish session:', error);
      toast.error('Failed to establish secure session. Please try again.', {
        position: "top-right",
        autoClose: 5000,
      });
    }
  };

  return (
    <Container maxWidth="xs">
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Image 
          src="/Tritiq.png" 
          alt="TRITIQ ERP" 
          width={300}
          height={120}
          style={{ maxWidth: '100%', height: 'auto', marginBottom: '16px' }}
          priority
        />
        <Typography variant="h6" component="h2" gutterBottom color="textSecondary">
          Enterprise Resource Planning System
        </Typography>

        <Box sx={{ p: 3 }}>
          <UnifiedLoginForm onLogin={handleLogin} />
        </Box>

        <Box sx={{ mt: 2 }}>
          <Button
            variant="text"
            color="primary"
            onClick={() => setForgotPasswordOpen(true)}
          >
            Forgot Password?
          </Button>
        </Box>
      </Box>

      {/* Forgot Password Modal */}
      <ForgotPasswordModal
        open={forgotPasswordOpen}
        onClose={() => setForgotPasswordOpen(false)}
        onSuccess={() => {
          setForgotPasswordOpen(false);
          // Show success message or redirect
        }}
      />
    </Container>
  );
};

export default LoginPage;