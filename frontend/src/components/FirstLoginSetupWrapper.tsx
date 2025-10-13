// frontend/src/components/FirstLoginSetupWrapper.tsx
/**
 * Wrapper component for first login setup flow
 * Shows mandatory CompanyDetailsModal and BankAccountModal for org superadmin first login
 */

import React from "react";
import CompanyDetailsModal from "./CompanyDetailsModal";
import BankAccountModal from "./BankAccountModal";
import { useFirstLoginSetup } from "../hooks/useFirstLoginSetup";
import { CircularProgress, Box, Typography } from "@mui/material";

interface FirstLoginSetupWrapperProps {
  children: React.ReactNode;
}

const FirstLoginSetupWrapper: React.FC<FirstLoginSetupWrapperProps> = ({ children }) => {
  const {
    showCompanyModal,
    showBankModal,
    isCheckingSetup,
    handleCompanyDetailsSaved,
    handleBankModalClose,
  } = useFirstLoginSetup();

  // Show loading while checking setup status
  if (isCheckingSetup) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        gap={2}
      >
        <CircularProgress size={60} />
        <Typography variant="body1" color="text.secondary">
          Checking account setup...
        </Typography>
      </Box>
    );
  }

  return (
    <>
      {children}
      
      {/* Company Details Modal - Non-dismissible on first login */}
      <CompanyDetailsModal
        open={showCompanyModal}
        onClose={() => {}} // Non-dismissible - no close action
        onSuccess={handleCompanyDetailsSaved}
        isRequired={true} // Mark as required to prevent closing
        mode="create"
      />

      {/* Bank Account Modal - Shows after company details saved */}
      <BankAccountModal
        open={showBankModal}
        onClose={handleBankModalClose}
        onSuccess={handleBankModalClose}
      />
    </>
  );
};

export default FirstLoginSetupWrapper;
