// frontend/src/components/DemoModeDialog.tsx

"use client";
import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  LinearProgress,
  Chip,
} from "@mui/material";
import { useForm } from "react-hook-form";
import api from "../lib/api";

interface DemoModeDialogProps {
  open: boolean;
  onClose: () => void;
  onDemoStart: (_token: string, _loginResponse?: any) => void;
}

interface NewUserFormData {
  fullName: string;
  email: string;
  phoneNumber: string;
  companyName: string;
  otp: string;
}

const DEMO_SESSION_DURATION_MINUTES = 30;

const DemoModeDialog: React.FC<DemoModeDialogProps> = ({
  open,
  onClose,
  onDemoStart,
}) => {
  const [userType, setUserType] = useState<"current" | "new" | "">("");
  const [step, setStep] = useState(0); // 0: selection, 1: form/login, 2: OTP (for new users)
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [tempEmail, setTempEmail] = useState("");
  const [sessionTimeRemaining, setSessionTimeRemaining] = useState<number | null>(null);
  const [demoSessionActive, setDemoSessionActive] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<NewUserFormData>();

  // Session countdown timer
  useEffect(() => {
    if (demoSessionActive && sessionTimeRemaining !== null && sessionTimeRemaining > 0) {
      const timer = setInterval(() => {
        setSessionTimeRemaining((prev) => {
          if (prev !== null && prev > 0) {
            return prev - 1;
          }
          return 0;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [demoSessionActive, sessionTimeRemaining]);

  // Handle session expiry
  useEffect(() => {
    if (sessionTimeRemaining === 0) {
      setError("Demo session expired. Your temporary data has been purged.");
      setDemoSessionActive(false);
      handleReset();
    }
  }, [sessionTimeRemaining]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleReset = () => {
    setUserType("");
    setStep(0);
    setError("");
    setSuccess("");
    setTempEmail("");
    setDemoSessionActive(false);
    setSessionTimeRemaining(null);
    reset();
  };

  const steps = ["User Type", "Details", "Verification"];

  const handleUserTypeNext = () => {
    if (!userType) {
      setError("Please select whether you are a current or new user");
      return;
    }
    setError("");
    setStep(1);
  };

  const handleCurrentUserLogin = () => {
    // For current users, close this dialog and let them use regular login
    // Then they'll enter demo mode after login
    onClose();
    // Set a flag to indicate demo mode should be activated after login
    localStorage.setItem("pendingDemoMode", "true");
  };

  const handleNewUserSubmit = async (data: NewUserFormData) => {
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      // Call backend API to initiate demo session
      const response = await api.post("/api/v1/demo/initiate", {
        phone_number: data.phoneNumber,
      });

      if (response.data.success) {
        setTempEmail(response.data.demo_email);
        setSuccess(`OTP sent successfully. Demo session valid for ${DEMO_SESSION_DURATION_MINUTES} minutes.`);
        setStep(2);
      } else {
        setError(response.data.message || "Failed to initiate demo session.");
      }
    } catch (err: any) {
      // Fallback to simulated demo mode if backend not available
      console.log("[Demo] Using simulated demo mode - backend API not available");
      const simulatedEmail = `demo_user_${Date.now()}@demo.local`;
      setTempEmail(simulatedEmail);
      setSuccess(`Demo OTP sent to ${data.email}. Please check your email (simulated).`);
      setStep(2);
    } finally {
      setLoading(false);
    }
  };

  const handleOTPSubmit = async () => {
    // Get the OTP value directly from the input
    const otpInput = document.querySelector(
      'input[name="otp"]',
    ) as HTMLInputElement;
    const otp = otpInput?.value || "";
    if (!otp || otp.length !== 6) {
      setError("Please enter a valid 6-digit OTP");
      return;
    }
    setLoading(true);
    setError("");
    try {
      // Try to verify OTP with backend
      const response = await api.post("/api/v1/demo/verify", {
        demo_email: tempEmail,
        otp: otp,
      });

      if (response.data.success) {
        const sessionData = response.data.session_data;
        setDemoSessionActive(true);
        setSessionTimeRemaining(sessionData.expires_in);

        // Set demo mode flag
        localStorage.setItem("demoMode", "true");
        localStorage.setItem("isDemoTempUser", "true");
        localStorage.setItem("demoSessionExpiry", sessionData.expires_at);
        localStorage.setItem("token", sessionData.access_token);

        setSuccess("Demo session started successfully! Welcome to TRITIQ BOS Demo.");

        // Close dialog and start demo
        setTimeout(() => {
          onDemoStart(sessionData.access_token, {
            access_token: sessionData.access_token,
            user_role: "demo_user",
            organization_id: "demo_org",
            user: {
              email: tempEmail,
              is_demo_user: true,
              is_temporary: true,
            },
            demo_mode: true,
            session_duration_minutes: DEMO_SESSION_DURATION_MINUTES,
          });
          onClose();
        }, 1500);
      } else {
        setError(response.data.message || "OTP verification failed.");
      }
    } catch (err: any) {
      // Fallback to simulated demo mode
      console.warn("[Demo] Using simulated demo mode - backend verification not available:", err?.message || err);
      const demoToken = `demo_temp_token_${Date.now()}`;
      const demoResponse = {
        access_token: demoToken,
        user_role: "demo_user",
        organization_id: "demo_org",
        user: {
          email: tempEmail,
          is_demo_user: true,
          is_temporary: true,
        },
        demo_mode: true,
        session_duration_minutes: DEMO_SESSION_DURATION_MINUTES,
      };

      // Set demo mode flag
      localStorage.setItem("demoMode", "true");
      localStorage.setItem("isDemoTempUser", "true");
      setSuccess("Demo login successful! Welcome to TRITIQ BOS Demo.");
      setDemoSessionActive(true);
      setSessionTimeRemaining(DEMO_SESSION_DURATION_MINUTES * 60);

      // Close dialog and start demo
      setTimeout(() => {
        onDemoStart(demoToken, demoResponse);
        onClose();
        handleReset();
      }, 1500);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (step > 0) {
      setStep(step - 1);
      setError("");
      setSuccess("");
    }
  };

  const handleClose = () => {
    handleReset();
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 3 },
      }}
    >
      <DialogTitle sx={{ textAlign: "center", pb: 1 }}>
        <Typography
          variant="h5"
          component="div"
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 1,
          }}
        >
          🎭 Demo Mode
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Experience TRITIQ BOS with sample data
        </Typography>
        {demoSessionActive && sessionTimeRemaining !== null && (
          <Box sx={{ mt: 1 }}>
            <Chip
              label={`Session expires in ${formatTime(sessionTimeRemaining)}`}
              color={sessionTimeRemaining < 300 ? "warning" : "primary"}
              size="small"
            />
            <LinearProgress
              variant="determinate"
              value={(sessionTimeRemaining / (DEMO_SESSION_DURATION_MINUTES * 60)) * 100}
              sx={{ mt: 1, height: 4, borderRadius: 2 }}
              color={sessionTimeRemaining < 300 ? "warning" : "primary"}
            />
          </Box>
        )}
      </DialogTitle>
      <DialogContent sx={{ pt: 2 }}>
        {/* Stepper */}
        <Stepper activeStep={step} sx={{ mb: 3 }}>
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
        {/* Step 0: User Type Selection */}
        {step === 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Are you a current user or new user?
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Please select your user type to continue with the demo experience.
            </Typography>
            <RadioGroup
              value={userType}
              onChange={(e) => setUserType(e.target.value as "current" | "new")}
            >
              <FormControlLabel
                value="current"
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1" fontWeight="medium">
                      Current User
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      I have an existing account and want to explore demo
                      features
                    </Typography>
                  </Box>
                }
              />
              <FormControlLabel
                value="new"
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1" fontWeight="medium">
                      New User
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      I'm new and want to try the system with a temporary demo
                      account
                    </Typography>
                  </Box>
                }
                sx={{ mt: 2 }}
              />
            </RadioGroup>
          </Box>
        )}
        {/* Step 1: Current User Login or New User Form */}
        {step === 1 && userType === "current" && (
          <Box textAlign="center">
            <Typography variant="h6" gutterBottom>
              Login to Start Demo
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Please login with your existing credentials. After successful
              login, you'll enter demo mode with sample data.
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Demo Mode Features:</strong>
                <br />• All functionality available with sample data
                <br />• No real data will be affected or saved
                <br />• Full access to all modules and features
              </Typography>
            </Alert>
          </Box>
        )}
        {step === 1 && userType === "new" && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Demo Account Details
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Fill in your details to create a temporary demo account. This
              account will be valid for {DEMO_SESSION_DURATION_MINUTES} minutes or until you logout.
            </Typography>
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Important:</strong> All demo data is temporary and will be purged when your session ends.
              </Typography>
            </Alert>
            <form onSubmit={handleSubmit(handleNewUserSubmit)}>
              <TextField
                fullWidth
                label="Full Name"
                margin="normal"
                {...register("fullName", { required: "Full name is required" })}
                error={!!errors.fullName}
                helperText={errors.fullName?.message}
              />
              <TextField
                fullWidth
                label="Email Address"
                type="email"
                margin="normal"
                {...register("email", {
                  required: "Email is required",
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: "Invalid email address",
                  },
                })}
                error={!!errors.email}
                helperText={errors.email?.message}
              />
              <TextField
                fullWidth
                label="Phone Number"
                margin="normal"
                {...register("phoneNumber", {
                  required: "Phone number is required",
                })}
                error={!!errors.phoneNumber}
                helperText={errors.phoneNumber?.message}
              />
              <TextField
                fullWidth
                label="Company Name"
                margin="normal"
                {...register("companyName", {
                  required: "Company name is required",
                })}
                error={!!errors.companyName}
                helperText={errors.companyName?.message}
              />
            </form>
          </Box>
        )}
        {/* Step 2: OTP Verification for New Users */}
        {step === 2 && userType === "new" && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Verify Demo OTP
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Enter the 6-digit demo OTP sent to: <strong>{tempEmail}</strong>
            </Typography>
            <TextField
              fullWidth
              label="Demo OTP"
              name="otp"
              type="text"
              inputProps={{ maxLength: 6, pattern: "[0-9]*" }}
              margin="normal"
              placeholder="123456"
              helperText="For demo purposes, enter any 6-digit number"
            />
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>Demo Mode:</strong> Enter any 6-digit number to
                continue. In a real environment, this would be sent to your
                email/phone.
              </Typography>
            </Alert>
            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>Session Duration:</strong> Your demo session will last {DEMO_SESSION_DURATION_MINUTES} minutes.
                All data will be automatically purged when the session expires.
              </Typography>
            </Alert>
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ p: 3, pt: 1 }}>
        {step > 0 && (
          <Button onClick={handleBack} disabled={loading}>
            Back
          </Button>
        )}
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        {step === 0 && (
          <Button
            variant="contained"
            onClick={handleUserTypeNext}
            disabled={!userType}
          >
            Continue
          </Button>
        )}
        {step === 1 && userType === "current" && (
          <Button
            variant="contained"
            onClick={handleCurrentUserLogin}
            disabled={loading}
          >
            Proceed to Login
          </Button>
        )}
        {step === 1 && userType === "new" && (
          <Button
            variant="contained"
            onClick={handleSubmit(handleNewUserSubmit)}
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : "Send Demo OTP"}
          </Button>
        )}
        {step === 2 && userType === "new" && (
          <Button
            variant="contained"
            onClick={handleOTPSubmit}
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : "Start Demo"}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};
export default DemoModeDialog;