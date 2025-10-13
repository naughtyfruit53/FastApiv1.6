// frontend/src/hooks/useFirstLoginSetup.ts
/**
 * Hook to manage first login setup flow for org superadmin
 * Shows mandatory CompanyDetailsModal followed by BankAccountModal
 */

import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { companyService } from "../services/authService";

export const useFirstLoginSetup = () => {
  const { user } = useAuth();
  const [showCompanyModal, setShowCompanyModal] = useState(false);
  const [showBankModal, setShowBankModal] = useState(false);
  const [isCheckingSetup, setIsCheckingSetup] = useState(true);
  const [companySetupComplete, setCompanySetupComplete] = useState(false);

  // Check if first login setup is required
  useEffect(() => {
    const checkFirstLoginSetup = async () => {
      if (!user) {
        setIsCheckingSetup(false);
        return;
      }

      // Only check for org superadmin (non-app superadmin with organization)
      const isOrgSuperAdmin = !user.is_super_admin && 
                              user.organization_id && 
                              user.role === "super_admin";
      
      if (!isOrgSuperAdmin) {
        setIsCheckingSetup(false);
        return;
      }

      try {
        // Check if user has completed first login setup
        const setupKey = `first_login_setup_complete_${user.id}`;
        const setupComplete = localStorage.getItem(setupKey) === "true";

        if (setupComplete) {
          setIsCheckingSetup(false);
          setCompanySetupComplete(true);
          return;
        }

        // Check if company details exist
        const company = await companyService.getCompanyDetails();
        
        if (!company) {
          // No company details - show modal (non-dismissible)
          setShowCompanyModal(true);
          setIsCheckingSetup(false);
        } else {
          // Company exists, mark as complete
          localStorage.setItem(setupKey, "true");
          setCompanySetupComplete(true);
          setIsCheckingSetup(false);
        }
      } catch (error: any) {
        // If 404 or no company, show modal
        if (error.response?.status === 404 || error.message?.includes("not found")) {
          setShowCompanyModal(true);
        }
        setIsCheckingSetup(false);
      }
    };

    checkFirstLoginSetup();
  }, [user]);

  // Handle company details saved successfully
  const handleCompanyDetailsSaved = () => {
    if (!user) return;
    
    // Mark setup as complete
    const setupKey = `first_login_setup_complete_${user.id}`;
    localStorage.setItem(setupKey, "true");
    setCompanySetupComplete(true);
    setShowCompanyModal(false);
    
    // Now show bank account modal
    setShowBankModal(true);
  };

  // Handle bank account modal close
  const handleBankModalClose = () => {
    setShowBankModal(false);
  };

  // Reset first login setup (for testing/debugging)
  const resetFirstLoginSetup = () => {
    if (!user) return;
    const setupKey = `first_login_setup_complete_${user.id}`;
    localStorage.removeItem(setupKey);
    setCompanySetupComplete(false);
    setShowCompanyModal(true);
  };

  return {
    showCompanyModal,
    showBankModal,
    isCheckingSetup,
    companySetupComplete,
    handleCompanyDetailsSaved,
    handleBankModalClose,
    setShowCompanyModal,
    resetFirstLoginSetup,
  };
};
