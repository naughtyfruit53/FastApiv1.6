"use client";
import React, { useState } from "react";
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
} from "@mui/material";
import { useForm } from "react-hook-form";
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
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<NewUserFormData>();

  const handleReset = () => {
    setUserType("");
    setStep(0);
    setError("");
    setSuccess("");
    setTempEmail("");
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
      // For demo purposes, simulate sending OTP to the email
      // In a real implementation, this would call an API endpoint
      console.log("[Demo] Simulating OTP send to:", data.email);
      setTempEmail(data.email);
      setSuccess(`Demo OTP sent to ${data.email}. Please check your email.`);
      setStep(2);
    } catch {
      setError("Failed to send demo OTP. Please try again.");
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
      // For demo purposes, accept any 6-digit OTP
      // Create a temporary demo token
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
      };
      // Set demo mode flag
      localStorage.setItem("demoMode", "true");
      localStorage.setItem("isDemoTempUser", "true");
      setSuccess("Demo login successful! Welcome to TRITIQ ERP Demo.");
      // Close dialog and start demo
      setTimeout(() => {
        onDemoStart(demoToken, demoResponse);
        onClose();
        handleReset();
      }, 1500);
    } catch {
      setError("Demo OTP verification failed. Please try again.");
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
          Experience TRITIQ ERP with sample data
        </Typography>
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
              account will be valid until you logout or close your browser.
            </Typography>
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
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  This is a temporary demo account. No real user will be created
                  in the database.
                </Typography>
              </Alert>
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
                email.
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
