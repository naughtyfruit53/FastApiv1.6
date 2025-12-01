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
  const isMounted = useRef(true);  // NEW: Track if component is mounted to prevent memory leaks

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

  // Fetch user permissions from RBAC service with timeout
  const fetchUserPermissions = async (userId: number) => {
    setPermissionsLoading(true);
    try {
     
      // Add timeout to prevent hanging
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Permissions fetch timeout')), 30000) // Increased timeout to 30s
      );
     
      // Race the API call with timeout
      const permissionsData = await Promise.race([
        timeoutPromise,
        rbacService.getUserPermissions(userId)
      ]) as { permissions: string[]; modules: string[]; submodules: Record<string, string[]> } || { permissions: [], modules: [], submodules: {} };
     
      const rolesData = await Promise.race([
        timeoutPromise,
        rbacService.getUserServiceRoles(userId)
      ]) as Role[] || [];
     
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
      return permissions;
    } catch (error) {
      // Set fallback permissions on error
      const fallbackPermissions = computeRoleBasedPermissions(user);
      setUserPermissions(fallbackPermissions);
      toast.error('Failed to load user permissions - using default access. Some features may be unavailable.', {
        position: "top-right",
        autoClose: 5000,
      });
      return fallbackPermissions;
    } finally {
      setPermissionsLoading(false);
    }
  };

  // Fetch the current user from API using the token in localStorage with timeout
  const fetchUser = async (retryCount = 0) => {
    if (isFetching.current || !isMounted.current) return; // NEW: Prevent concurrent and unmounted fetches
    isFetching.current = true;
    const maxRetries = 1; // Reduced to 1 for faster failure
    try {
      const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
      // Validate token format before proceeding
      if (accessToken === 'null' || accessToken === 'undefined' || (accessToken && accessToken.split('.').length !== 3)) {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        throw new Error('Invalid token format');
      }
      if (!accessToken) {
        throw new Error("No token found");
      }
      const userData = await authService.getCurrentUser();
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
     
      // Fetch user permissions from RBAC service
      await fetchUserPermissions(userData.id);
     
      // Check org context for non-super-admins
      if (!userData.is_super_admin && !userData.organization_id) {
        throw new Error(
          "User account is not properly configured with organization context",
        );
      }
      markAuthReady();
      // If on login page after successful fetch, redirect to dashboard
      if (router.pathname === "/login") {
        handlePostLoginRedirect();
      }
    } catch (error: any) {
      // Only retry on non-auth errors
      if (
        retryCount < maxRetries &&
        error?.status !== 401 &&
        error?.status !== 403
      ) {
        const retryDelay = Math.pow(2, retryCount) * 1000;
        setTimeout(() => fetchUser(retryCount + 1), retryDelay);
        return;
      }
      // Improved error handling: Don't clear storage on connection/network errors
      if (error.response) {
        const status = error.response.status;
        if (status === 401 || status === 403) {
          // Auth errors: Clear and redirect
          localStorage.removeItem(ACCESS_TOKEN_KEY);
          localStorage.removeItem(REFRESH_TOKEN_KEY);
          localStorage.removeItem(USER_ROLE_KEY);
          localStorage.removeItem(IS_SUPER_ADMIN_KEY);
          setUser(null);
          resetAuthReady();
          toast.error(error?.userMessage || "Authentication failed. Please log in again.", {
            position: "top-right",
            autoClose: 5000,
          });
          if (router.pathname !== "/login") {
            // Save current path as return URL before redirect
            // NEW: Don't save if pathname includes '404' or invalid
            if (
              router.pathname !== '/login' && 
              !router.pathname.includes('404') && 
              !sessionStorage.getItem("returnUrlAfterLogin")
            ) {
              sessionStorage.setItem("returnUrlAfterLogin", router.asPath);
            } else if (router.pathname.includes('404')) {
            }
            router.push("/login");
          }
        } else {
          // Server errors (500 etc.): Don't clear token, just notify
          toast.error(error?.userMessage || "Server error occurred. Please try refreshing the page.", {
            position: "top-right",
            autoClose: 5000,
          });
        }
      } else {
        // Network/connection errors: Don't clear token, allow retry on refresh
        toast.error("Unable to connect to the server. Please check if the backend is running on port 8000, your network connection, then try refreshing the page.", {
          position: "top-right",
          autoClose: 5000,
        });
      }
    } finally {
      isFetching.current = false;
      setLoading(false); // Ensure loading is set to false in finally
      setPermissionsLoading(false); // NEW: Ensure permissionsLoading false even on error
    }
  };

  // On mount, check for token and initialize user session
  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token && !hasFetched.current) {
      hasFetched.current = true; // Mark as fetched to prevent multiple calls
      fetchUser();
    } else {
      markAuthReady();
      setLoading(false);
      setPermissionsLoading(false); // NEW: Critical fix for no-token case (e.g., login page)
    }

    return () => {
      isMounted.current = false;  // NEW: Set unmounted on cleanup to prevent async updates
    };
  }, [router]); // NEW: Added router to dependency list to handle path changes properly

  // Handle post-login redirect with state preservation
  const handlePostLoginRedirect = () => {
    try {
      // Check for return URL
      const returnUrl = sessionStorage.getItem("returnUrlAfterLogin");
      if (returnUrl) {
        sessionStorage.removeItem("returnUrlAfterLogin");
        router.replace(returnUrl);
        setTimeout(() => {
          restoreFormData();
        }, 500);
        return;
      }
      router.push("/dashboard");
    } catch (err) {
      router.push("/dashboard");
    }
  };

  // Attempt to restore form data after login
  const restoreFormData = () => {
    try {
      const savedFormData = sessionStorage.getItem("formDataBeforeExpiry");
      if (savedFormData) {
        const formData = JSON.parse(savedFormData);
        sessionStorage.removeItem("formDataBeforeExpiry");
        toast.info("Form data from previous session detected and cleared. Please re-enter if needed.", {
          position: "top-right",
          autoClose: 5000,
        });
      }
    } catch (err) {
    }
  };

  // Force password reset if required
  useEffect(() => {
    if (
      user &&
      user.must_change_password &&
      router.pathname !== "/password-reset"
    ) {
      router.push("/password-reset");
    }
  }, [user, router]);

  const login = async (loginResponse: any) => {
    if (!loginResponse.access_token || loginResponse.access_token.split('.').length !== 3) {
      throw new Error('Invalid access token received');
    }
    localStorage.setItem(ACCESS_TOKEN_KEY, loginResponse.access_token);
    // Store refresh token if provided
    if (loginResponse.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, loginResponse.refresh_token);
    }
    // Store authentication context data (NOT organization_id - that stays in memory)
    if (loginResponse.user_role) {
      localStorage.setItem(USER_ROLE_KEY, loginResponse.user_role);
    }
    localStorage.setItem(
      IS_SUPER_ADMIN_KEY,
      loginResponse.user?.is_super_admin ? "true" : "false",
    );
    // Clear any OTP-related fields
    // Defensive: never store org_id in localStorage
    const userData = loginResponse.user;
    // Validate org context for regular users
    if (!userData.is_super_admin && !userData.organization_id) {
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
    // Verify session immediately after setting token and user
    await refreshUser();
   
    // Fetch user permissions
    await fetchUserPermissions(userData.id);
   
    resetAuthReady();
    markAuthReady();
    // Handle post-login redirect and form state restoration
    handlePostLoginRedirect();
  };

  // Logout: clear all sensitive data and redirect
  const logout = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_ROLE_KEY);
    localStorage.removeItem(IS_SUPER_ADMIN_KEY);
    setUser(null);
    setUserPermissions(null);
    resetAuthReady();
    if (router.pathname !== "/login") {
      router.push("/login");
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
    } else if (token === 'null' || token === 'undefined' || token.split('.').length !== 3) {
    } else {
    }
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  // Only ready if user is super admin or has org context
  const isOrgContextReady =
    !user || user.is_super_admin || !!user.organization_id;

  // Timeout for loading
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (loading) {
        setLoading(false);
        toast.error('Loading timeout. Please refresh the page or check your connection.');
      }
    }, 15000); // Increased timeout to 15 seconds
    return () => clearTimeout(timeout);
  }, [loading]);

  // NEW: Handle unauthorized redirect in useEffect to prevent side effects in render
  useEffect(() => {
    if (!loading && !user && router.pathname !== "/login") {
      // Save current path as return URL before redirect
      // NEW: Don't save if pathname includes '404' or invalid
      if (
        router.pathname !== '/login' && 
        !router.pathname.includes('404') && 
        !sessionStorage.getItem("returnUrlAfterLogin")
      ) {
        sessionStorage.setItem("returnUrlAfterLogin", router.asPath);
      } else if (router.pathname.includes('404')) {
      }
      router.push("/login");
    }
  }, [loading, user, router]);

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
