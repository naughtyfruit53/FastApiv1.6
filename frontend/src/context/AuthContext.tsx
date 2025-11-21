// frontend/src/context/AuthContext.tsx
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useRef,
} from "react";
import { useRouter } from "next/router";
import { toast } from "react-toastify";
import { authService } from "../services/authService";
import { User, getDisplayRole } from "../types/user.types";
import { markAuthReady, resetAuthReady } from "../lib/api";
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY, USER_ROLE_KEY, IS_SUPER_ADMIN_KEY } from "../constants/auth";
import { Role } from "../types/rbac.types";
import { rbacService } from "../services/rbacService";
interface UserPermissions {
  role: string;
  roles: Role[];
  permissions: string[];
  modules: string[];
  submodules: Record<string, string[]>;
}
interface AuthContextType {
  user: User | null;
  loading: boolean;
  permissionsLoading: boolean;
  displayRole: string | null;
  userPermissions: UserPermissions | null;
  login: (loginResponse: any) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  updateUser: (updatedData: Partial<User>) => void;
  isOrgContextReady: boolean;
  getAuthHeaders: () => { Authorization?: string };
  refreshPermissions: () => Promise<void>;
}
export const AuthContext = createContext<AuthContextType | undefined>(undefined); // Changed to named export
export function AuthProvider({ children }: { children: ReactNode }): any {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [permissionsLoading, setPermissionsLoading] = useState(true);
  const [userPermissions, setUserPermissions] = useState<UserPermissions | null>(null);
  const router = useRouter();
  const hasFetched = useRef(false); // Prevent multiple fetches
  const isFetching = useRef(false); // Prevent concurrent fetches
  const computeRoleBasedPermissions = (user: User | null): UserPermissions => {
    if (!user) {
      return {
        role: 'user',
        roles: [],
        permissions: [],
        modules: [],
        submodules: {},
      };
    }
    // STRICT ENFORCEMENT: No computed permissions for super admins
    // All permissions must come from backend RBAC system
    const isOrgSuperAdmin = ['super_admin', 'admin', 'management'].includes(user.role || '');
    let permissions: string[] = [];
    let modules: string[] = [];
    let submodules: Record<string, string[]> = {};
    if (isOrgSuperAdmin) {
      // Organization admin has most permissions except super admin functions
      permissions = [
        'dashboard.*',
        'finance.*',
        'sales.*',
        'crm.*',
        'inventory.*',
        'hr.*',
        'service.*',
        'reports.*',
        'settings.view',
        'settings.manageUsers',
        'settings.manageRoles',
        'settings.manageOrganization',
        'master_data.*',
        'manufacturing.*',
        'vouchers.*',
        'accounting.*',
        'reportsAnalytics.*',
        'aiAnalytics.*',
        'marketing.*',
        'projects.*',
        'tasks_calendar.*',
        'email.*',
      ];
      modules = [
        'dashboard', 'finance', 'sales', 'crm', 'inventory', 'hr', 'service', 'reports', 'settings',
        'master_data', 'manufacturing', 'vouchers', 'accounting', 'reportsAnalytics', 'aiAnalytics',
        'marketing', 'projects', 'tasks_calendar', 'email'
      ];
      submodules = modules.reduce((acc, mod) => {
        acc[mod] = ['all'];
        return acc;
      }, {} as Record<string, string[]>);
    } else {
      // Regular user - permissions based on role
      switch (user.role) {
        case 'finance_manager':
          permissions = ['dashboard.view', 'finance.*', 'reports.viewFinancial'];
          modules = ['dashboard', 'finance', 'reports'];
          submodules = {
            dashboard: ['view'],
            finance: ['view', 'create', 'edit', 'delete', 'viewReports', 'manageBanks'],
            reports: ['viewFinancial'],
          };
          break;
        case 'sales_manager':
          permissions = ['dashboard.view', 'sales.*', 'crm.*', 'reports.viewOperational'];
          modules = ['dashboard', 'sales', 'crm', 'reports'];
          submodules = {
            dashboard: ['view'],
            sales: ['view', 'create', 'edit', 'delete', 'manageCustomers', 'viewAnalytics'],
            crm: ['view', 'create', 'edit', 'delete', 'manageContacts', 'viewAnalytics'],
            reports: ['viewOperational'],
          };
          break;
        case 'inventory_manager':
          permissions = ['dashboard.view', 'inventory.*', 'reports.viewOperational'];
          modules = ['dashboard', 'inventory', 'reports'];
          submodules = {
            dashboard: ['view'],
            inventory: ['view', 'create', 'edit', 'delete', 'manageStock', 'viewReports'],
            reports: ['viewOperational'],
          };
          break;
        case 'hr_manager':
          permissions = ['dashboard.view', 'hr.*', 'reports.viewOperational'];
          modules = ['dashboard', 'hr', 'reports'];
          submodules = {
            dashboard: ['view'],
            hr: ['view', 'create', 'edit', 'delete', 'manageEmployees', 'viewPayroll'],
            reports: ['viewOperational'],
          };
          break;
        case 'service_manager':
          permissions = ['dashboard.view', 'service.*', 'reports.viewOperational'];
          modules = ['dashboard', 'service', 'reports'];
          submodules = {
            dashboard: ['view'],
            service: ['view', 'create', 'edit', 'delete', 'manageTickets', 'viewAnalytics'],
            reports: ['viewOperational'],
          };
          break;
        case 'user':
        case 'employee':
        default:
          permissions = [
            'dashboard.view',
            'master_data.view',
            'inventory.view',
            'manufacturing.view',
            'vouchers.view',
            'finance.view',
            'accounting.view',
            'reportsAnalytics.view',
            'aiAnalytics.view',
            'sales.view',
            'marketing.view',
            'service.view',
            'projects.view',
            'hrManagement.view',
            'tasks_calendar.view',
            'email.view',
          ];
          modules = [
            'dashboard', 'master_data', 'inventory', 'manufacturing', 'vouchers',
            'finance', 'accounting', 'reportsAnalytics', 'aiAnalytics', 'sales',
            'marketing', 'service', 'projects', 'hrManagement', 'tasks_calendar', 'email'
          ];
          submodules = modules.reduce((acc, mod) => {
            acc[mod] = ['view'];
            return acc;
          }, {} as Record<string, string[]>);
          break;
      }
    }
    return {
      role: user.role || 'user',
      roles: [],
      permissions,
      modules,
      submodules,
    };
  };
  // Fetch user permissions from RBAC service
  const fetchUserPermissions = async (userId: number) => {
    setPermissionsLoading(true);
    try {
      console.log("[AuthProvider] Fetching user permissions for user:", userId);
     
      // Fetch user permissions
      const permissionsData = await rbacService.getUserPermissions(userId) || { permissions: [], modules: [], submodules: {} };
      const rolesData = await rbacService.getUserServiceRoles(userId);
     
      // Compute fallback
      const fallback = computeRoleBasedPermissions(user);
     
      // Ensure submodules are objects
      const safePermissionsSubmodules = permissionsData.submodules || {};
      const safeFallbackSubmodules = fallback.submodules || {};
     
      // Merge fetched with fallback
      const mergedPermissions = [...new Set([...fallback.permissions, ...(permissionsData.permissions || [])])];
      const mergedModules = [...new Set([...fallback.modules, ...(permissionsData.modules || [])])];
      const mergedSubmodules: Record<string, string[]> = {};
     
      // Merge submodules
      const allKeys = new Set([...Object.keys(safeFallbackSubmodules), ...Object.keys(safePermissionsSubmodules)]);
      allKeys.forEach(key => {
        mergedSubmodules[key] = [...new Set([
          ...(safeFallbackSubmodules[key] || []),
          ...(safePermissionsSubmodules[key] || [])
        ])];
      });
      // Process and structure the permissions
      const permissions: UserPermissions = {
        role: permissionsData.role || fallback.role,
        roles: [...new Set([...fallback.roles, ...rolesData])],
        permissions: mergedPermissions,
        modules: mergedModules,
        submodules: mergedSubmodules,
      };
      setUserPermissions(permissions);
      console.log("[AuthProvider] User permissions fetched and merged successfully");
      return permissions;
    } catch (error) {
      console.error("[AuthProvider] Error fetching user permissions:", error);
      // Set fallback permissions
      const fallbackPermissions = computeRoleBasedPermissions(user);
      setUserPermissions(fallbackPermissions);
      return fallbackPermissions;
    } finally {
      setPermissionsLoading(false);
    }
  };
  // Fetch the current user from API using the token in localStorage
  const fetchUser = async (retryCount = 0) => {
    if (isFetching.current) return; // Prevent concurrent
    isFetching.current = true;
    const maxRetries = 2;
    console.log(
      `[AuthProvider] fetchUser started - attempt ${retryCount + 1}/${maxRetries + 1}`,
      {
        hasToken: !!localStorage.getItem(ACCESS_TOKEN_KEY),
        hasRefreshToken: !!localStorage.getItem(REFRESH_TOKEN_KEY),
        timestamp: new Date().toISOString(),
      },
    );
    try {
      const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
      // Validate token format before proceeding
      if (accessToken === 'null' || (accessToken && accessToken.split('.').length !== 3)) {
        console.log('[AuthProvider] Invalid token format detected - clearing storage');
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        throw new Error('Invalid token format');
      }
      if (!accessToken) {
        console.log("[AuthProvider] No token found in localStorage");
        throw new Error("No token found");
      }
      console.log("[AuthProvider] Token found, fetching user data from API");
      const userData = await authService.getCurrentUser();
      console.log("[AuthProvider] User data received from API:", {
        userId: userData.id,
        email: userData.email,
        role: userData.role,
        isSuperAdmin: userData.is_super_admin,
        hasOrgId: !!userData.organization_id,
        mustChangePassword: userData.must_change_password,
      });
      // Defensive: org ID should never be leaked between users
      const newUser = {
        id: userData.id,
        email: userData.email,
        role: userData.role,
        is_super_admin: userData.is_super_admin,
        organization_id: userData.organization_id, // note: it's from loginResponse, not user
        must_change_password: userData.must_change_password,
      };
      setUser(newUser);
      console.log("[AuthProvider] User state updated successfully");
     
      // Fetch user permissions from RBAC service
      await fetchUserPermissions(userData.id);
     
      // Check org context for non-super-admins
      if (!userData.is_super_admin && !userData.organization_id) {
        console.error(
          "[AuthProvider] Organization context missing for regular user",
        );
        throw new Error(
          "User account is not properly configured with organization context",
        );
      }
      markAuthReady();
      console.log("[AuthProvider] Auth context marked as ready");
      // If on login page after successful fetch, redirect to dashboard
      if (router.pathname === "/login") {
        handlePostLoginRedirect();
      }
    } catch (error: any) {
      console.error(
        `[AuthProvider] fetchUser error on attempt ${retryCount + 1}:`,
        {
          error: error.message,
          status: error?.status,
          willRetry:
            retryCount < maxRetries &&
            error?.status !== 401 &&
            error?.status !== 403,
        },
      );
      // Attempt token refresh before giving up
      if (retryCount < maxRetries && (error?.status === 401 || error?.status === 403)) {
        console.log("[AuthProvider] Attempting token refresh before retry");
        const refreshResult = await authService.refreshToken();
        if (refreshResult) {
          console.log("[AuthProvider] Token refresh successful, retrying fetchUser");
          await fetchUser(retryCount + 1);
          return;
        }
      }
      // Only retry on non-auth errors
      if (
        retryCount < maxRetries &&
        error?.status !== 401 &&
        error?.status !== 403
      ) {
        const retryDelay = Math.pow(2, retryCount) * 1000;
        console.log(`[AuthProvider] Retrying fetchUser in ${retryDelay}ms`);
        setTimeout(() => fetchUser(retryCount + 1), retryDelay);
        return;
      }
      // On error, clear sensitive data and force re-auth
      console.log("[AuthProvider] Auth error - clearing data");
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      localStorage.removeItem(USER_ROLE_KEY);
      localStorage.removeItem(IS_SUPER_ADMIN_KEY);
      // Preserve refresh_token for potential recovery
      console.log("[AuthProvider] Preserving refresh_token for potential recovery");
      setUser(null);
      resetAuthReady();
      if (error?.userMessage) {
        toast.error(`Authentication failed: ${error.userMessage}`, {
          position: "top-right",
          autoClose: 5000,
        });
      } else {
        toast.error(
          "Failed to establish secure session. Please log in again.",
          { position: "top-right", autoClose: 5000 },
        );
      }
      // Only redirect if not already on login page to prevent loop
      if (router.pathname !== "/login") {
        console.log("[AuthProvider] Redirecting to login");
        router.push("/login");
      } else {
        console.log("[AuthProvider] Already on login - no redirect needed");
      }
    } finally {
      isFetching.current = false;
      setLoading(false); // Ensure loading is set to false in finally
    }
  };
  // On mount, check for token and initialize user session
  useEffect(() => {
    console.log("[AuthProvider] Component mounted, initializing auth state");
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    console.log("[AuthProvider] Token check result:", {
      hasToken: !!token,
      hasRefreshToken: !!localStorage.getItem(REFRESH_TOKEN_KEY),
      pathname: router.pathname,
      timestamp: new Date().toISOString(),
    });
    if (token && !hasFetched.current) {
      hasFetched.current = true; // Mark as fetched to prevent multiple calls
      console.log("[AuthProvider] Token found - starting user fetch");
      fetchUser();
    } else {
      console.log(
        "[AuthProvider] No token found - marking auth ready and stopping loading",
      );
      markAuthReady();
      setLoading(false);
    }
  }, []); // Removed router.pathname dependency to prevent re-runs on path change
  // Handle post-login redirect with state preservation
  const handlePostLoginRedirect = () => {
    try {
      // Check for return URL
      const returnUrl = sessionStorage.getItem("returnUrlAfterLogin");
      if (returnUrl) {
        console.log("[AuthProvider] Redirecting to saved URL:", returnUrl);
        sessionStorage.removeItem("returnUrlAfterLogin");
        router.replace(returnUrl);
        setTimeout(() => {
          restoreFormData();
        }, 500);
        return;
      }
      console.log(
        "[AuthProvider] No return URL found, redirecting to dashboard",
      );
      router.push("/dashboard");
    } catch (err) {
      console.error("[AuthProvider] Error in post-login redirect:", err);
      router.push("/dashboard");
    }
  };
  // Attempt to restore form data after login
  const restoreFormData = () => {
    try {
      const savedFormData = sessionStorage.getItem("formDataBeforeExpiry");
      if (savedFormData) {
        const formData = JSON.parse(savedFormData);
        console.log(
          "[AuthProvider] Attempting to restore form data:",
          formData,
        );
        Object.entries(formData).forEach(
          ([formKey, formValues]: [string, any]) => {
            if (formValues && typeof formValues === "object") {
              Object.entries(formValues).forEach(([fieldName, fieldValue]) => {
                const field = document.querySelector(
                  `[name="${fieldName}"]`,
                ) as HTMLInputElement;
                if (field && typeof fieldValue === "string") {
                  field.value = fieldValue;
                  field.dispatchEvent(new Event("input", { bubbles: true }));
                }
              });
            }
          },
        );
        sessionStorage.removeItem("formDataBeforeExpiry");
        toast.info("Form data has been restored from before session expiry.", {
          position: "top-right",
          autoClose: 5000,
        });
      }
    } catch (err) {
      console.warn("[AuthProvider] Could not restore form data:", err);
    }
  };
  // Force password reset if required
  useEffect(() => {
    if (
      user &&
      user.must_change_password &&
      router.pathname !== "/password-reset"
    ) {
      console.log("[AuthProvider] Must change password - redirecting to password-reset");
      router.push("/password-reset");
    }
  }, [user, router]);
  // Login: store token, hydrate user, and mark ready
  const login = async (loginResponse: any) => {
    console.log("[AuthProvider] Login process started:", {
      hasToken: !!loginResponse.access_token,
      hasRefresh: !!loginResponse.refresh_token,
      userRole: loginResponse.user_role,
      isSuperAdmin: loginResponse.user?.is_super_admin,
      hasOrgId: !!loginResponse.user.organization_id,
      timestamp: new Date().toISOString(),
    });
    localStorage.setItem(ACCESS_TOKEN_KEY, loginResponse.access_token);
    if (loginResponse.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, loginResponse.refresh_token);
      console.log("[AuthProvider] Stored refresh token");
    } else {
      console.warn("[AuthProvider] No refresh token in login response");
    }
    console.log("[AuthProvider] Token stored in localStorage");
    if (loginResponse.user_role) {
      localStorage.setItem(USER_ROLE_KEY, loginResponse.user_role);
      console.log("[AuthProvider] Stored user_role:", loginResponse.user_role);
    }
    localStorage.setItem(
      IS_SUPER_ADMIN_KEY,
      loginResponse.user?.is_super_admin ? "true" : "false",
    );
    console.log(
      "[AuthProvider] Stored is_super_admin:",
      loginResponse.user?.is_super_admin,
    );
    // Clear any OTP-related fields
    console.log("[AuthProvider] Clearing OTP-related fields");
    // Defensive: never store org_id in localStorage
    const userData = loginResponse.user;
    // Validate org context for regular users
    if (!userData.is_super_admin && !userData.organization_id) {
      console.error(
        "[AuthProvider] Organization context validation failed for regular user",
      );
      throw new Error(
        "Login failed: User account is not properly configured with organization context",
      );
    }
    const newUser = {
      id: userData.id,
      email: userData.email,
      role: userData.role,
      is_super_admin: userData.is_super_admin,
      organization_id: loginResponse.organization_id, // note: it's from loginResponse, not user
      must_change_password: loginResponse.must_change_password,
    };
    setUser(newUser);
    console.log("[AuthProvider] User state set from login response");
    // Verify session immediately after setting token and user
    await refreshUser();
   
    // Fetch user permissions
    await fetchUserPermissions(userData.id);
   
    resetAuthReady();
    markAuthReady();
    console.log("[AuthProvider] Auth ready state reset and marked");
    // Handle post-login redirect and form state restoration
    handlePostLoginRedirect();
    console.log(
      "[AuthProvider] Login process completed successfully - user context established from login response",
    );
  };
  // Logout: clear all sensitive data and redirect
  const logout = () => {
    console.log("[AuthProvider] Logout initiated");
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_ROLE_KEY);
    localStorage.removeItem(IS_SUPER_ADMIN_KEY);
    setUser(null);
    setUserPermissions(null);
    resetAuthReady();
    console.log("[AuthProvider] Auth data cleared");
    if (router.pathname !== "/login") {
      console.log("[AuthProvider] Redirecting to login");
      router.push("/login");
    } else {
      console.log("[AuthProvider] Already on login - no redirect needed");
    }
  };
  // Manual refresh of user (e.g., after profile update)
  const refreshUser = async () => {
    await fetchUser();
  };
  // Refresh permissions without fetching full user data
  const refreshPermissions = async () => {
    if (user) {
      await fetchUserPermissions(user.id);
    }
  };
  // Update the user object in memory only
  const updateUser = (updatedData: Partial<User>) => {
    setUser((prev) => (prev ? { ...prev, ...updatedData } : null));
  };
  // Get auth headers for API requests
  const getAuthHeaders = () => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) {
      console.warn("[AuthProvider] No token found when getting auth headers");
    } else if (token.split('.').length !== 3) {
      console.error("[AuthProvider] Malformed token when getting auth headers:", token.substring(0, 20) + '...');
    } else {
      console.log("[AuthProvider] Valid token format for auth headers");
    }
    return token ? { Authorization: `Bearer ${token}` } : {};
  };
  // Only ready if user is super admin or has org context
  const isOrgContextReady =
    !user || user.is_super_admin || !!user.organization_id;
  console.log("[AuthProvider] Render phase:", {
    loading,
    hasUser: !!user,
    userEmail: user?.email,
    isOrgContextReady,
    willRenderChildren: !loading,
    timestamp: new Date().toISOString(),
  });
  // Timeout for loading
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (loading) {
        setLoading(false);
        toast.error('Loading timeout. Please refresh the page or check your connection.');
      }
    }, 10000); // 10 seconds timeout
    return () => clearTimeout(timeout);
  }, [loading]);
  // Show loading spinner while auth state is being determined
  if (loading) {
    console.log("[AuthProvider] Rendering loading state");
    const spinnerStyles = `
      @keyframes authSpinner {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      .auth-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        animation: authSpinner 2s linear infinite;
        margin-bottom: 15px;
      }
      @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
      }
      .auth-pulse {
        animation: pulse 2s ease-in-out infinite;
      }
    `;
    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: spinnerStyles }} />
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100vh",
            flexDirection: "column",
            backgroundColor: "#f8fafc",
            backgroundImage:
              "linear-gradient(to bottom right, #f8fafc, #e2e8f0)",
          }}
        >
          <div
            style={{
              fontSize: "24px",
              fontWeight: 600,
              marginBottom: "10px",
              color: "#1e293b",
              textAlign: "center",
            }}
          >
            TRITIQ BOS
          </div>
          <div
            style={{
              fontSize: "14px",
              marginBottom: "30px",
              color: "#64748b",
              textAlign: "center",
            }}
          >
            Business Management System
          </div>
          <div className="auth-spinner"></div>
          <div
            style={{
              marginTop: "20px",
              fontSize: "14px",
              color: "#475569",
              fontWeight: 500,
              textAlign: "center",
            }}
            className="auth-pulse"
          >
            Loading your workspace...
          </div>
          <div
            style={{
              marginTop: "5px",
              fontSize: "12px",
              color: "#94a3b8",
              textAlign: "center",
            }}
          >
            Establishing secure connection
          </div>
        </div>
      </>
    );
  }
  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        permissionsLoading,
        displayRole: user
          ? getDisplayRole(user.role, user.is_super_admin)
          : null,
        userPermissions,
        login,
        logout,
        refreshUser,
        updateUser,
        isOrgContextReady,
        getAuthHeaders,
        refreshPermissions,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
export const useAuthWithOrgContext = (): any => {
  const auth = useAuth();
  return {
    ...auth,
    isReady: !auth.loading && !auth.permissionsLoading && auth.isOrgContextReady,
  };
};