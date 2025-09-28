// frontend/src/components/CompanySetupGuard.tsx
import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { useQuery } from "@tanstack/react-query";
import { organizationService } from "../services/organizationService";
import { useAuth } from "../context/AuthContext";
import CompanyDetailsModal from "./CompanyDetailsModal";
import { toast } from "react-toastify";


interface CompanySetupGuardProps {
  children: React.ReactNode;
}

const CompanySetupGuard: React.FC<CompanySetupGuardProps> = ({ children }) => {
  const { user, loading: authLoading } = useAuth(); // Use auth loading state
  const router = useRouter();
  const [showCompanyModal, setShowCompanyModal] = useState(false);
  const [hasShownToast, setHasShownToast] = useState(false);

  // Skip company setup requirement for these routes
  const exemptRoutes = ["/login", "/", "/password-reset", "/forgot-password"];

  // Routes that should trigger company setup warning/blocking
  const restrictedRoutes = [
    "/dashboard",
    "/masters",
    "/inventory",
    "/stock",
    "/products",
    "/customers",
    "/vendors",
    "/vouchers",
  ];

  const isExemptRoute = exemptRoutes.includes(router.pathname);
  const isRestrictedRoute = restrictedRoutes.some((route) =>
    router.pathname.startsWith(route),
  );

  // Only enable query when auth is ready, token exists, and not exempt
  const {
    data: organization,
    isLoading: organizationLoading,
    refetch: refetchOrganization,
  } = useQuery({
    queryKey: ["organization"],
    queryFn: organizationService.getCurrentOrganization,
    enabled:
      !!localStorage.getItem("token") &&
      !!user &&
      !user.is_super_admin &&
      !isExemptRoute &&
      !authLoading,
    retry: 1,
  });

  // Check if organization setup is required
  const isOrganizationSetupRequired = !organizationLoading && organization === null;

  useEffect(() => {
    // Skip if auth loading, user not loaded, is super admin, or on exempt route
    if (authLoading || !user || user.is_super_admin || isExemptRoute) {
      return;
    }

    // Skip if organization query is still loading to avoid premature modal display
    if (organizationLoading) {
      return;
    }

    // Only show modal if organization setup is actually required AND modal not already shown
    if (isOrganizationSetupRequired && !showCompanyModal) {
      setShowCompanyModal(true);

      // Show appropriate toast notification based on route
      if (!hasShownToast) {
        if (router.pathname === "/dashboard") {
          toast.info(
            "Welcome! Please complete your organization setup to get started.",
            {
              autoClose: 5000,
              toastId: "organization-setup-welcome",
            },
          );
        } else if (isRestrictedRoute) {
          toast.warning(
            "Please complete your organization setup to access this feature.",
            {
              autoClose: 5000,
              toastId: "organization-setup-required",
            },
          );
        }
        setHasShownToast(true);
      }
    }

    // If organization data exists, ensure modal is hidden
    if (organization && showCompanyModal) {
      setShowCompanyModal(false);
    }
  }, [
    authLoading,
    user,
    isOrganizationSetupRequired,
    isRestrictedRoute,
    hasShownToast,
    isExemptRoute,
    organizationLoading,
    organization,
    showCompanyModal,
  ]);

  const handleCompanyModalClose = () => {
    if (isOrganizationSetupRequired) {
      // Don't allow closing if organization setup is required
      return;
    }
    setShowCompanyModal(false);
  };

  const handleOrganizationSetupSuccess = () => {
    setShowCompanyModal(false);
    setHasShownToast(false);
    refetchOrganization();
    toast.success(
      "Organization details saved successfully! You can now access all features.",
      {
        autoClose: 3000,
      },
    );
  };

  // Don't render guard for super admins or exempt routes
  if (authLoading || !user || user.is_super_admin || isExemptRoute) {
    return <>{children}</>;
  }

  // Show loading state while checking organization
  if (organizationLoading) {
    return <>{children}</>;
  }

  return (
    <>
      {children}

      {/* Organization setup modal - required if no organization exists */}
      <CompanyDetailsModal
        open={showCompanyModal}
        onClose={handleCompanyModalClose}
        onSuccess={handleOrganizationSetupSuccess}
        isRequired={isOrganizationSetupRequired}
      />
    </>
  );
};

export default CompanySetupGuard;