"use client";
import React, { useState, useEffect } from "react";
import { Box, Typography, Container, Button, Divider } from "@mui/material";
import { PlayArrow } from "@mui/icons-material";
import Image from "next/image";
import { toast } from "react-toastify";
import UnifiedLoginForm from "../components/UnifiedLoginForm";
import ForgotPasswordModal from "../components/ForgotPasswordModal";
import DemoModeDialog from "../components/DemoModeDialog";
import { useAuth } from "../context/AuthContext";
const LoginPage: React.FC = () => {
  const [forgotPasswordOpen, setForgotPasswordOpen] = useState(false);
  const [demoModeOpen, setDemoModeOpen] = useState(false);
  const { login } = useAuth();
  // Check if demo mode should be activated after login
  useEffect(() => {
    const pendingDemo = localStorage.getItem("pendingDemoMode");
    if (pendingDemo === "true") {
      localStorage.removeItem("pendingDemoMode");
      localStorage.setItem("demoMode", "true");
    }
  }, []);
  const handleLogin = async (token: string, loginResponse?: any) => {
    console.log("[Login] Login successful, processing response:", {
      hasToken: !!token,
      hasLoginResponse: !!loginResponse,
      organizationId: loginResponse?.organization_id,
      userRole: loginResponse?.user_role,
      mustChangePassword: loginResponse?.must_change_password,
      isSuperAdmin: loginResponse?.user?.is_super_admin,
      isDemoMode: loginResponse?.demo_mode,
      timestamp: new Date().toISOString(),
    });
    // Always save token to localStorage before anything else
    if (token) {
      localStorage.setItem("token", token);
    }
    try {
      console.log(
        "[Login] Calling AuthContext login method to establish session",
      );
      // Use AuthContext login method to establish full context before navigation
      await login(loginResponse);
      console.log("[Login] AuthContext login completed - session established");
      console.log("[Login] Current localStorage state:", {
        hasToken: !!localStorage.getItem("token"),
        hasUserRole: !!localStorage.getItem("user_role"),
        hasSuperAdminFlag: !!localStorage.getItem("is_super_admin"),
        isDemoMode: !!localStorage.getItem("demoMode"),
      });
      // Check if this is demo mode
      if (
        loginResponse?.demo_mode ||
        localStorage.getItem("demoMode") === "true"
      ) {
        console.log("[Login] Demo mode activated - redirecting to demo page");
        window.location.href = "/demo";
        return;
      }
      // Check if password change is required (not mandatory for OTP login)
      if (loginResponse?.must_change_password && !loginResponse?.otp_login) {
        console.log(
          "[Login] Password change required - redirecting to password reset",
        );
        // Use hard reload to avoid SPA race condition - ensures token is present for AuthProvider's effect
        window.location.href = "/password-reset";
      } else {
        console.log("[Login] Login complete - redirecting to dashboard");
        // Use hard reload to avoid SPA race condition - ensures token is present for AuthProvider's effect
        window.location.href = "/dashboard";
      }
    } catch (err) {
      console.error(msg, err);
      toast.error("Failed to establish secure session. Please try again.", {
        position: "top-right",
        autoClose: 5000,
      });
    }
  };
  return (
    <Container maxWidth="xs">
      <Box sx={{ mt: 4, textAlign: "center" }}>
        <Image
          src="/Tritiq.png"
          alt="TritIQ Business Suite"
          width={300}
          height={120}
          style={{ maxWidth: "100%", height: "auto", marginBottom: "16px" }}
          priority
        />
        <Typography
          variant="h6"
          component="h2"
          gutterBottom
          color="textSecondary"
        >
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
        {/* Demo Mode Section */}
        <Box sx={{ mt: 3, mb: 2 }}>
          <Divider sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              OR
            </Typography>
          </Divider>
          <Button
            variant="outlined"
            fullWidth
            startIcon={<PlayArrow />}
            onClick={() => setDemoModeOpen(true)}
            sx={{
              borderRadius: 2,
              py: 1.5,
              borderColor: "primary.light",
              "&:hover": {
                borderColor: "primary.main",
                backgroundColor: "primary.light",
                color: "primary.contrastText",
              },
            }}
          >
            Try Demo Mode
          </Button>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mt: 1, textAlign: "center" }}
          >
            Experience all features with sample data
          </Typography>
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
      {/* Demo Mode Dialog */}
      <DemoModeDialog
        open={demoModeOpen}
        onClose={() => setDemoModeOpen(false)}
        onDemoStart={handleLogin}
      />
    </Container>
  );
};
export default LoginPage;
