// frontend/src/pages/dashboard/index.tsx

import React, { useEffect, useState } from "react";  // NEW: Add useState for loader timeout
import { useRouter } from "next/router";
import { useAuth } from "../../context/AuthContext";
import { useMobileDetection } from "../../hooks/useMobileDetection";
import AppSuperAdminDashboard from "./AppSuperAdminDashboard";
import OrgDashboard from "./OrgDashboard";
import RoleGate from "../../components/RoleGate";  // Import RoleGate
import { toast } from "react-toastify";  // NEW: Import toast for timeout message

const Dashboard: React.FC = () => {
  console.count('Render: Dashboard');
  const { user, loading, permissionsLoading } = useAuth();  // NEW: Added permissionsLoading to check full auth load
  const { isMobile } = useMobileDetection();
  const router = useRouter();
  const [showTimeoutToast, setShowTimeoutToast] = useState(false);  // NEW: State for loader timeout

  const isSuperAdmin =
    user?.is_super_admin ||
    user?.role === "super_admin" ||
    !user?.organization_id ||
    user?.email === "naughtyfruit53@gmail.com";

  useEffect(() => {
    console.log("[Dashboard] Component mounted, checking auth state:", {
      hasUser: !!user,
      loading,
      permissionsLoading,
      userRole: user?.role,
      organizationId: user?.organization_id,
      timestamp: new Date().toISOString(),
    });

    if (!loading && !permissionsLoading && !user) {  // NEW: Wait for permissions too
      console.log(
        "[Dashboard] No user found and not loading - redirecting to login",
      );
      router.push("/login");
    } else if (!loading && !permissionsLoading && user && isMobile && !isSuperAdmin) {
      console.log("[Dashboard] Mobile detected for org user - redirecting to mobile dashboard");
      router.push("/mobile/dashboard");
    }
  }, [user, loading, permissionsLoading, router, isMobile, isSuperAdmin]);  // NEW: Added permissionsLoading to dependency

  // NEW: Timeout for loader - show toast if loading > 5s
  useEffect(() => {
    if (loading || permissionsLoading) {
      const timeoutId = setTimeout(() => {
        setShowTimeoutToast(true);
        toast.error("Verification taking longer than expected. Please refresh or check connection.", {
          position: "top-right",
          autoClose: 5000,
        });
      }, 5000);  // 5 second timeout
      return () => clearTimeout(timeoutId);
    }
  }, [loading, permissionsLoading]);

  // Prevent any rendering until we have confirmed auth state
  if (loading || permissionsLoading) {  // NEW: Check both loading states
    console.log("[Dashboard] Still loading auth/permissions - showing loader");
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          flexDirection: "column",
        }}
      >
        <div>Loading user context...</div>
        <div style={{ marginTop: "10px", fontSize: "12px", color: "#666" }}>
          Verifying access...
        </div>
      </div>
    );
  }

  if (!user) {
    console.log("[Dashboard] No user available - preventing render");
    return null; // Prevent flash of content while redirecting
  }

  // Additional safety check: Ensure we have minimum required auth context
  if (!user.id || !user.email) {
    console.error("[Dashboard] User object incomplete:", user);
    return (
      <div style={{ padding: "20px", textAlign: "center" }}>
        <div>Authentication error - incomplete user data</div>
        <button
          onClick={() => {
            localStorage.clear();
            window.location.href = "/login";
          }}
        >
          Return to Login
        </button>
      </div>
    );
  }

  console.log("[Dashboard] Auth context ready - determining dashboard type:", {
    isSuperAdmin,
    userRole: user?.role,
    isSuperAdminFlag: user?.is_super_admin,
    organizationId: user?.organization_id,
    userEmail: user?.email,
    timestamp: new Date().toISOString(),
  });

  const dashboardContent = isSuperAdmin ? (
    <>
      {console.log("[Dashboard] Rendering App Super Admin Dashboard")}
      <AppSuperAdminDashboard />
    </>
  ) : (
    <>
      {console.log("[Dashboard] Rendering Organization Dashboard")}
      <OrgDashboard />
    </>
  );

  return (
    <RoleGate requiredPermissions={['dashboard.read']}>
      <div className="modern-dashboard" style={{ padding: "20px" }}>
        {dashboardContent}
      </div>
    </RoleGate>
  );
};

export default Dashboard;
