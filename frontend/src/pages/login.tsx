// frontend/src/pages/login.tsx
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
import useMobileRouting from "../hooks/mobile/useMobileRouting";
import { ACCESS_TOKEN_KEY } from "../constants/auth";
import { useCompany } from "../context/CompanyContext"; // Added import

const LoginPage: React.FC = () => {
  const [forgotPasswordOpen, setForgotPasswordOpen] = useState(false);
  const [demoModeOpen, setDemoModeOpen] = useState(false);
  const { login } = useAuth();
  const { getMobileRoute } = useMobileRouting();
  const { refetch: refetchCompany } = useCompany(); // Added to refetch company data

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

    if (token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
      console.log("[Login] Stored access token in localStorage");
    }

    try {
      console.log("[Login] Calling AuthContext login method to establish session");
      await login(loginResponse);
      console.log("[Login] AuthContext login completed - session established");

      // Force refetch company data to ensure CompanyContext is updated
      await refetchCompany();
      console.log("[Login] Company data refetched");

      console.log("[Login] Current localStorage state:", {
        hasToken: !!localStorage.getItem("access_token"),
        hasUserRole: !!localStorage.getItem("user_role"),
        hasSuperAdminFlag: !!localStorage.getItem("is_super_admin"),
        isDemoMode: !!localStorage.getItem("demoMode"),
      });

      if (
        loginResponse?.demo_mode ||
        (localStorage.getItem("demoMode") === "true" && !loginResponse?.organization_id)
      ) {
        console.log("[Login] Demo mode activated - redirecting to demo page");
        window.location.href = getMobileRoute("/demo");
        return;
      }

      if (loginResponse?.must_change_password && !loginResponse?.otp_login) {
        console.log("[Login] Password change required - redirecting to password reset");
        window.location.href = getMobileRoute("/password-reset");
      } else {
        console.log("[Login] Login complete - redirecting to dashboard");
        window.location.href = getMobileRoute("/dashboard");
      }
    } catch (err) {
      console.error("Failed to establish secure session:", err);
      toast.error("Failed to establish secure session. Please try again.", {
        position: "top-right",
        autoClose: 5000,
      });
    }
  };

  return (
    <Container maxWidth="lg">
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
          One-Stop Solution for All Your Entrepreneurial Needs
        </Typography>
        <Box sx={{ display: "flex", flexDirection: { xs: "column", sm: "row" }, justifyContent: "space-between", alignItems: "stretch", mt: 2, gap: 2 }}>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ p: 3 }}>
              <UnifiedLoginForm 
                onLogin={handleLogin} 
                onForgotPassword={() => setForgotPasswordOpen(true)}
              />
            </Box>
          </Box>
          <Divider orientation="vertical" flexItem sx={{ display: { xs: "none", sm: "block" } }} />
          <Divider orientation="horizontal" flexItem sx={{ display: { xs: "block", sm: "none" } }} />
          <Box sx={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
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
          </Box>
        </Box>
      </Box>
      <ForgotPasswordModal
        open={forgotPasswordOpen}
        onClose={() => setForgotPasswordOpen(false)}
        onSuccess={() => {
          setForgotPasswordOpen(false);
        }}
      />
      <DemoModeDialog
        open={demoModeOpen}
        onClose={() => setDemoModeOpen(false)}
        onDemoStart={handleLogin}
      />
    </Container>
  );
};

export default LoginPage;