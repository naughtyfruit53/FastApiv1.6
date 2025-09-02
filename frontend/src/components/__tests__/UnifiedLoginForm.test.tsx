// frontend/src/components/__tests__/UnifiedLoginForm.test.tsx

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import UnifiedLoginForm from "../UnifiedLoginForm";
import { authService } from "../../services/authService";

// Mock the auth service
jest.mock("../../services/authService", () => ({
  authService: {
    loginWithEmail: jest.fn(),
    requestOTP: jest.fn(),
    verifyOTP: jest.fn(),
  },
}));

const mockedAuthService = authService as jest.Mocked<typeof authService>;

describe("UnifiedLoginForm", () => {
  const mockOnLogin = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockOnLogin.mockClear();
  });

  it("renders default login form with email and password fields", () => {
    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(
      screen.getByRole("checkbox", { name: /login with otp/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /^login$/i }),
    ).toBeInTheDocument();
  });

  it("shows password visibility toggle", () => {
    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const passwordField = screen.getByLabelText(/password/i);
    const toggleButton = screen.getByRole("button", {
      name: /toggle password visibility/i,
    });

    expect(passwordField).toHaveAttribute("type", "password");

    fireEvent.click(toggleButton);
    expect(passwordField).toHaveAttribute("type", "text");

    fireEvent.click(toggleButton);
    expect(passwordField).toHaveAttribute("type", "password");
  });

  it("switches to OTP mode when checkbox is checked", () => {
    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const otpCheckbox = screen.getByRole("checkbox", {
      name: /login with otp/i,
    });

    fireEvent.click(otpCheckbox);

    expect(screen.getByLabelText(/phone number/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/password/i)).not.toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /send otp/i }),
    ).toBeInTheDocument();
  });

  it("shows stepper in OTP mode", () => {
    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const otpCheckbox = screen.getByRole("checkbox", {
      name: /login with otp/i,
    });
    fireEvent.click(otpCheckbox);

    expect(screen.getByText("Login Details")).toBeInTheDocument();
    expect(screen.getByText("Verify OTP")).toBeInTheDocument();
  });

  it("validates email format", async () => {
    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const emailField = screen.getByLabelText(/email address/i);
    const submitButton = screen.getByRole("button", { name: /^login$/i });

    fireEvent.change(emailField, { target: { value: "invalid-email" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
    });
  });

  it("validates phone number format in OTP mode", async () => {
    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const otpCheckbox = screen.getByRole("checkbox", {
      name: /login with otp/i,
    });
    fireEvent.click(otpCheckbox);

    const phoneField = screen.getByLabelText(/phone number/i);
    const submitButton = screen.getByRole("button", { name: /send otp/i });

    fireEvent.change(phoneField, { target: { value: "invalid-phone" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(/enter a valid phone number/i),
      ).toBeInTheDocument();
    });
  });

  it("handles standard email/password login", async () => {
    const mockResponse = {
      access_token: "test-token",
      user_role: "user",
      organization_id: 1,
    };

    mockedAuthService.loginWithEmail.mockResolvedValue(mockResponse);

    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const emailField = screen.getByLabelText(/email address/i);
    const passwordField = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /^login$/i });

    fireEvent.change(emailField, { target: { value: "test@example.com" } });
    fireEvent.change(passwordField, { target: { value: "password123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockedAuthService.loginWithEmail).toHaveBeenCalledWith(
        "test@example.com",
        "password123",
      );
      expect(mockOnLogin).toHaveBeenCalledWith("test-token", mockResponse);
    });
  });

  it("handles OTP request with phone number", async () => {
    const mockOtpResponse = {
      message: "OTP sent via whatsapp",
      email: "test@example.com",
      delivery_method: "whatsapp",
    };

    mockedAuthService.requestOTP.mockResolvedValue(mockOtpResponse);

    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const otpCheckbox = screen.getByRole("checkbox", {
      name: /login with otp/i,
    });
    fireEvent.click(otpCheckbox);

    const emailField = screen.getByLabelText(/email address/i);
    const phoneField = screen.getByLabelText(/phone number/i);
    const submitButton = screen.getByRole("button", { name: /send otp/i });

    fireEvent.change(emailField, { target: { value: "test@example.com" } });
    fireEvent.change(phoneField, { target: { value: "+919876543210" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockedAuthService.requestOTP).toHaveBeenCalledWith(
        "test@example.com",
        "+919876543210",
        "auto",
        "login",
      );
      expect(screen.getByText(/otp sent via whatsapp/i)).toBeInTheDocument();
    });
  });

  it("handles OTP request without phone number (email only)", async () => {
    const mockOtpResponse = {
      message: "OTP sent to email",
      email: "test@example.com",
      delivery_method: "email",
    };

    mockedAuthService.requestOTP.mockResolvedValue(mockOtpResponse);

    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const otpCheckbox = screen.getByRole("checkbox", {
      name: /login with otp/i,
    });
    fireEvent.click(otpCheckbox);

    const emailField = screen.getByLabelText(/email address/i);
    const submitButton = screen.getByRole("button", { name: /send otp/i });

    fireEvent.change(emailField, { target: { value: "test@example.com" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockedAuthService.requestOTP).toHaveBeenCalledWith(
        "test@example.com",
        "",
        "auto",
        "login",
      );
      expect(screen.getByText(/otp sent to email/i)).toBeInTheDocument();
    });
  });

  it("shows OTP input after successful OTP request", async () => {
    const mockOtpResponse = {
      message: "OTP sent successfully",
      email: "test@example.com",
    };

    mockedAuthService.requestOTP.mockResolvedValue(mockOtpResponse);

    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const otpCheckbox = screen.getByRole("checkbox", {
      name: /login with otp/i,
    });
    fireEvent.click(otpCheckbox);

    const emailField = screen.getByLabelText(/email address/i);
    const submitButton = screen.getByRole("button", { name: /send otp/i });

    fireEvent.change(emailField, { target: { value: "test@example.com" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByLabelText(/otp code/i)).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /verify & login/i }),
      ).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /back/i })).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /resend otp/i }),
      ).toBeInTheDocument();
    });
  });

  it("handles OTP verification and login", async () => {
    const mockOtpResponse = {
      message: "OTP sent successfully",
      email: "test@example.com",
    };
    const mockVerifyResponse = {
      access_token: "test-token",
      user_role: "user",
      organization_id: 1,
    };

    mockedAuthService.requestOTP.mockResolvedValue(mockOtpResponse);
    mockedAuthService.verifyOTP.mockResolvedValue(mockVerifyResponse);

    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const otpCheckbox = screen.getByRole("checkbox", {
      name: /login with otp/i,
    });
    fireEvent.click(otpCheckbox);

    const emailField = screen.getByLabelText(/email address/i);
    fireEvent.change(emailField, { target: { value: "test@example.com" } });
    fireEvent.click(screen.getByRole("button", { name: /send otp/i }));

    await waitFor(() => {
      expect(screen.getByLabelText(/otp code/i)).toBeInTheDocument();
    });

    const otpField = screen.getByLabelText(/otp code/i);
    const verifyButton = screen.getByRole("button", {
      name: /verify & login/i,
    });

    fireEvent.change(otpField, { target: { value: "123456" } });
    fireEvent.click(verifyButton);

    await waitFor(() => {
      expect(mockedAuthService.verifyOTP).toHaveBeenCalledWith(
        "test@example.com",
        "123456",
      );
      expect(mockOnLogin).toHaveBeenCalledWith("test-token", {
        ...mockVerifyResponse,
        otp_login: true,
      });
    });
  });

  it("shows back button functionality", async () => {
    const mockOtpResponse = {
      message: "OTP sent successfully",
      email: "test@example.com",
    };
    mockedAuthService.requestOTP.mockResolvedValue(mockOtpResponse);

    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const otpCheckbox = screen.getByRole("checkbox", {
      name: /login with otp/i,
    });
    fireEvent.click(otpCheckbox);

    const emailField = screen.getByLabelText(/email address/i);
    fireEvent.change(emailField, { target: { value: "test@example.com" } });
    fireEvent.click(screen.getByRole("button", { name: /send otp/i }));

    await waitFor(() => {
      expect(screen.getByLabelText(/otp code/i)).toBeInTheDocument();
    });

    const backButton = screen.getByRole("button", { name: /back/i });
    fireEvent.click(backButton);

    expect(
      screen.getByRole("button", { name: /send otp/i }),
    ).toBeInTheDocument();
    expect(screen.queryByLabelText(/otp code/i)).not.toBeInTheDocument();
  });

  it("handles errors gracefully", async () => {
    mockedAuthService.loginWithEmail.mockRejectedValue(
      new Error("Invalid credentials"),
    );

    render(<UnifiedLoginForm onLogin={mockOnLogin} />);

    const emailField = screen.getByLabelText(/email address/i);
    const passwordField = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /^login$/i });

    fireEvent.change(emailField, { target: { value: "test@example.com" } });
    fireEvent.change(passwordField, { target: { value: "wrong-password" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});
