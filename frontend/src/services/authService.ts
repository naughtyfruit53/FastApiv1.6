// frontend/src/services/authService.ts
// Revised: frontend/src/services/authService.ts
// frontend/src/services/authService.ts (Revised for detailed error handling in companyService)
import api from "../lib/api"; // Use the api client
export const authService = {
  login: async (username: string, password: string): Promise<any> => {
    try {
      console.log("[AuthService] Starting login process for:", username);
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);
      const response = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      console.log("[AuthService] Login API response received:", {
        hasToken: !!response.data.access_token,
        organizationId: response.data.organization_id,
        userRole: response.data.user_role,
        mustChangePassword: response.data.must_change_password,
      });
      // Store token FIRST
      localStorage.setItem("token", response.data.access_token);
      // Store refresh token if provided
      if (response.data.refresh_token) {
        localStorage.setItem("refresh_token", response.data.refresh_token);
        console.log("[AuthService] Stored refresh token");
      }
      // Store authentication context data (NOT organization_id - that stays in memory)
      if (response.data.user_role) {
        localStorage.setItem("user_role", response.data.user_role);
        console.log("[AuthService] Stored user_role:", response.data.user_role);
      }
      localStorage.setItem(
        "is_super_admin",
        response.data.user?.is_super_admin ? "true" : "false",
      );
      console.log(
        "[AuthService] Stored is_super_admin:",
        response.data.user?.is_super_admin,
      );
      console.log(
        "[AuthService] Organization context managed by backend session only",
      );
      console.log("[AuthService] Login complete - auth context established");
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Login failed:", error);
      throw new Error(error.userMessage || "Login failed");
    }
  },
  loginWithEmail: async (email: string, password: string): Promise<any> => {
    try {
      console.log("[AuthService] Starting email login process for:", email);
      const formData = new FormData();
      formData.append("username", email);
      formData.append("password", password);
      const response = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      console.log("[AuthService] Email login API response received:", {
        hasToken: !!response.data.access_token,
        organizationId: response.data.organization_id,
        userRole: response.data.user_role,
        mustChangePassword: response.data.must_change_password,
      });
      // Store token FIRST
      localStorage.setItem("token", response.data.access_token);
      // Store ALL authentication context data immediately after token
      // Store authentication context data (NOT organization_id - that stays in memory)
      if (response.data.user_role) {
        localStorage.setItem("user_role", response.data.user_role);
        console.log("[AuthService] Stored user_role:", response.data.user_role);
      }
      localStorage.setItem(
        "is_super_admin",
        response.data.user?.is_super_admin ? "true" : "false",
      );
      console.log(
        "[AuthService] Stored is_super_admin:",
        response.data.user?.is_super_admin,
      );
      console.log(
        "[AuthService] Organization context managed by backend session only",
      );
      console.log(
        "[AuthService] Email login complete - all context established",
      );
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Email login failed:", error);
      throw new Error(error.userMessage || "Email login failed");
    }
  },
  // NOTE: This method should only be called by AuthProvider for:
  // 1. Initial user fetch on app mount
  // 2. Manual user refresh operations
  // DO NOT call this directly from components - use useAuth() hook instead
  getCurrentUser: async (): Promise<any> => {
    try {
      console.log("[AuthService] Fetching current user data");
      const response = await api.get("/users/me");
      console.log("[AuthService] User data received from /users/me:", {
        id: response.data.id,
        email: response.data.email,
        role: response.data.role,
        is_super_admin: response.data.is_super_admin,
        organization_id: response.data.organization_id,
        must_change_password: response.data.must_change_password,
      });
      // Update stored auth context if needed (e.g., role changed)
      if (response.data.role) {
        localStorage.setItem("user_role", response.data.role);
      }
      localStorage.setItem(
        "is_super_admin",
        response.data.is_super_admin ? "true" : "false",
      );
      // Organization ID is returned but NOT stored - managed by backend session
      console.log(
        "[AuthService] User fetch complete - auth context refreshed (organization in session only)",
      );
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Failed to fetch current user:", error);
      throw new Error(
        error.userMessage || "Failed to fetch current user data",
      );
    }
  },
  logout: async (): Promise<void> => {
    try {
      console.log("[AuthService] Starting logout process");
      await api.post("/auth/logout");
      // Clear ALL auth-related storage
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user_role");
      localStorage.removeItem("is_super_admin");
      // Organization context cleared by backend session
      console.log("[AuthService] Logout complete - all auth data cleared");
    } catch (error: any) {
      console.error("[AuthService] Logout failed:", error);
      // Clear storage even if API fails
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user_role");
      localStorage.removeItem("is_super_admin");
      throw new Error(error.userMessage || "Logout failed");
    }
  },
  refreshToken: async (): Promise<any> => {
    try {
      console.log("[AuthService] Starting token refresh");
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        throw new Error("No refresh token available");
      }
      const response = await api.post("/auth/refresh", {
        refresh_token: refreshToken,
      });
      // Update token
      localStorage.setItem("token", response.data.access_token);
      // Update refresh token if new one provided
      if (response.data.refresh_token) {
        localStorage.setItem("refresh_token", response.data.refresh_token);
      }
      console.log("[AuthService] Token refresh successful");
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Token refresh failed:", error);
      // Clear invalid tokens on failure
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      throw new Error(error.userMessage || "Session expired. Please log in again.");
    }
  },
  register: async (data: any): Promise<any> => {
    try {
      console.log("[AuthService] Starting registration process");
      const response = await api.post("/auth/register", data);
      console.log("[AuthService] Registration successful");
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Registration failed:", error);
      throw new Error(error.userMessage || "Registration failed");
    }
  },
  verifyOTP: async (email: string, otp: string): Promise<any> => {
    try {
      console.log("[AuthService] Verifying OTP for:", email);
      const response = await api.post("/auth/verify-otp", { email, otp });
      // Store token if verification succeeds
      if (response.data.access_token) {
        localStorage.setItem("token", response.data.access_token);
      }
      console.log("[AuthService] OTP verification successful");
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] OTP verification failed:", error);
      throw new Error(error.userMessage || "OTP verification failed");
    }
  },
  resendOTP: async (email: string): Promise<any> => {
    try {
      console.log("[AuthService] Resending OTP to:", email);
      const response = await api.post("/auth/resend-otp", { email });
      console.log("[AuthService] OTP resent successfully");
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Failed to resend OTP:", error);
      throw new Error(error.userMessage || "Failed to resend OTP");
    }
  },
  getUserOrganizations: async (): Promise<any> => {
    try {
      console.log("[AuthService] Fetching user organizations");
      const response = await api.get("/users/me/organizations");
      console.log("[AuthService] User organizations fetched");
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Failed to fetch user organizations:", error);
      throw new Error(error.userMessage || "Failed to fetch organizations");
    }
  },
  switchOrganization: async (organizationId: number): Promise<any> => {
    try {
      console.log("[AuthService] Switching to organization:", organizationId);
      const response = await api.put("/users/me/organization", {
        organization_id: organizationId,
      });
      // Organization context updated in backend session - no local storage needed
      console.log("[AuthService] Organization switch successful (session updated)");
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Organization switch failed:", error);
      throw new Error(error.userMessage || "Failed to switch organization");
    }
  },
  // Company/Organization related methods (moved from companyService)
  createOrganizationLicense: async (data: any): Promise<any> => {
    try {
      console.log("[AuthService] Creating organization license");
      const response = await api.post("/organizations/license/create", data);
      // Organization context managed by backend
      console.log("[AuthService] Organization license created");
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Failed to create organization license:", error);
      // Provide detailed error for UI
      const userMessage = error.response?.data?.detail || error.userMessage || "Failed to create organization license. Please check your input and try again.";
      throw new Error(userMessage);
    }
  },
  getCurrentOrganization: async (): Promise<any> => {
    try {
      console.log("[AuthService] Fetching current organization");
      const response = await api.get("/organizations/current");
      console.log("[AuthService] Current organization fetched");
      return response.data;
    } catch (error: any) {
      console.error("[AuthService] Failed to get current organization:", error);
      throw new Error(error.userMessage || "Failed to get current organization");
    }
  },
  updateOrganization: async (data: any): Promise<any> => {
    try {
      const response = await api.put("/organizations/current", data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update organization");
    }
  },
  // Admin-only endpoints
  getAllOrganizations: async (): Promise<any> => {
    try {
      const response = await api.get("/organizations/");
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organizations");
    }
  },
  getOrganization: async (id: number): Promise<any> => {
    try {
      const response = await api.get(`/organizations/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organization");
    }
  },
  updateOrganizationById: async (id: number, data: any): Promise<any> => {
    try {
      const response = await api.put(`/organizations/${id}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update organization");
    }
  },
};
export const passwordService = {
  changePassword: async (
    currentPassword: string | null,
    newPassword: string,
    confirmPassword?: string,
  ): Promise<any> => {
    try {
      const payload: {
        new_password: string;
        current_password?: string;
        confirm_password?: string;
      } = {
        new_password: newPassword,
      };
      if (currentPassword) {
        payload.current_password = currentPassword;
      }
      if (confirmPassword) {
        payload.confirm_password = confirmPassword;
      }
      const response = await api.post("/password/change", payload);
      // Handle new token if provided in response (password change returns new JWT)
      if (response.data.access_token) {
        console.log(
          "[PasswordService] New token received after password change, updating storage",
        );
        localStorage.setItem("token", response.data.access_token);
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to change password");
    }
  },
  forgotPassword: async (email: string): Promise<any> => {
    try {
      const response = await api.post("/password/forgot", { email });
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.userMessage || "Failed to send password reset email",
      );
    }
  },
  resetPassword: async (email: string, otp: string, newPassword: string): Promise<any> => {
    try {
      const response = await api.post("/password/reset", {
        email,
        otp,
        new_password: newPassword,
      });
      // Handle new token if provided in response (password reset returns new JWT)
      if (response.data.access_token) {
        console.log(
          "[PasswordService] New token received after password reset, updating storage",
        );
        localStorage.setItem("token", response.data.access_token);
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to reset password");
    }
  },
};
export const userService = {
  // Organization user management (for org admins)
  getOrganizationUsers: async (params?: any): Promise<any> => {
    try {
      const response = await api.get("/users/", { params });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to get organization users");
    }
  },
  createUser: async (data: any): Promise<any> => {
    try {
      const response = await api.post("/users/", data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to create user");
    }
  },
  updateUser: async (id: number, data: any): Promise<any> => {
    try {
      const response = await api.put(`/users/${id}`, data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update user");
    }
  },
  deleteUser: async (id: number): Promise<any> => {
    try {
      const response = await api.delete(`/users/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to delete user");
    }
  },
  resetUserPassword: async (userId: number): Promise<any> => {
    try {
      const response = await api.post(`/auth/reset/${userId}/password`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to reset user password");
    }
  },
  toggleUserStatus: async (userId: number, isActive: boolean): Promise<any> => {
    try {
      const response = await api.put(`/users/${userId}`, {
        is_active: isActive,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.userMessage || "Failed to update user status");
    }
  },
};