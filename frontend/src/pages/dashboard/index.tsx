// frontend/src/pages/dashboard/index.tsx

import React, { useEffect } from "react";
import { useRouter } from "next/router";
import { useAuth } from "../../context/AuthContext";
import { useMobileDetection } from "../../hooks/useMobileDetection";  // Added import for mobile detection
import AppSuperAdminDashboard from "./AppSuperAdminDashboard";
import OrgDashboard from "./OrgDashboard";

import { ProtectedPage } from '../../components/ProtectedPage';
const Dashboard: React.FC = () => {
  console.count('Render: Dashboard');
  const { productId, vendorId } = useRouter().query;  // Added to prevent unused warning if needed
  const { user, loading } = useAuth();
  const { isMobile } = useMobileDetection();  // Added for mobile check
  const router = useRouter();

  const isSuperAdmin =
    user?.is_super_admin ||
    user?.role === "super_admin" ||
    !user?.organization_id ||
    user?.email === "naughtyfruit53@gmail.com";

  useEffect(() => {
    console.log("[Dashboard] Component mounted, checking auth state:", {
      hasUser: !!user,
      loading,
      userRole: user?.role,
      organizationId: user?.organization_id,
      timestamp: new Date().toISOString(),
    });

    if (!loading && !user) {
      console.log(
        "[Dashboard] No user found and not loading - redirecting to login",
      );
      router.push("/login");
    } else if (!loading && user && isMobile && !isSuperAdmin) {  // Added mobile redirect for non-super admins
      console.log("[Dashboard] Mobile detected for org user - redirecting to mobile dashboard");
      router.push("/mobile/dashboard");
    }
  }, [user, loading, router, isMobile, isSuperAdmin]);

  // Prevent any rendering until we have confirmed auth state
  if (loading) {
    console.log("[Dashboard] Still loading auth state - showing loader");
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
          Establishing secure session...
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

  return (
    <div className="modern-dashboard" style={{ padding: "20px" }}>
      {isSuperAdmin ? (
        <>
          {console.log("[Dashboard] Rendering App Super Admin Dashboard")}
          <AppSuperAdminDashboard />
        </>
      ) : (
        <>
          {console.log("[Dashboard] Rendering Organization Dashboard")}
          <OrgDashboard />
        </>
      )}
    </div>
  );
};

export default Dashboard;