// frontend/src/components/CompanySetupGuard.tsx
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import { companyService } from '../services/authService';
import { useAuth } from '../context/AuthContext';
import CompanyDetailsModal from './CompanyDetailsModal';
import { toast } from 'react-toastify';
import StickyNotesPanel from './StickyNotes/StickyNotesPanel';

interface CompanySetupGuardProps {
  children: React.ReactNode;
}

const CompanySetupGuard: React.FC<CompanySetupGuardProps> = ({ children }) => {
  const { user, loading: authLoading } = useAuth();  // Use auth loading state
  const router = useRouter();
  const [showCompanyModal, setShowCompanyModal] = useState(false);
  const [hasShownToast, setHasShownToast] = useState(false);

  // Skip company setup requirement for these routes
  const exemptRoutes = ['/login', '/', '/password-reset', '/forgot-password'];
  
  // Routes that should trigger company setup warning/blocking
  const restrictedRoutes = [
    '/dashboard',
    '/masters',
    '/inventory',
    '/stock',
    '/products',
    '/customers',
    '/vendors',
    '/vouchers'
  ];

  const isExemptRoute = exemptRoutes.includes(router.pathname);
  const isRestrictedRoute = restrictedRoutes.some(route => router.pathname.startsWith(route));

  // Only enable query when auth is ready, token exists, and not exempt
  const { data: company, isLoading: companyLoading, refetch: refetchCompany } = useQuery({
    queryKey: ['company'],
    queryFn: companyService.getCurrentCompany,
    enabled: !!localStorage.getItem('token') && !!user && !user.is_super_admin && !isExemptRoute && !authLoading,
    retry: 1,
  });

  // Check if company setup is required
  const isCompanySetupRequired = !companyLoading && company === null;

  useEffect(() => {
    // Skip if auth loading, user not loaded, is super admin, or on exempt route
    if (authLoading || !user || user.is_super_admin || isExemptRoute) {
      return;
    }

    // Skip if company query is still loading to avoid premature modal display
    if (companyLoading) {
      return;
    }

    // Only show modal if company setup is actually required AND modal not already shown
    if (isCompanySetupRequired && !showCompanyModal) {
      setShowCompanyModal(true);
      
      // Show appropriate toast notification based on route
      if (!hasShownToast) {
        if (router.pathname === '/dashboard') {
          toast.info('Welcome! Please complete your company setup to get started.', {
            autoClose: 5000,
            toastId: 'company-setup-welcome'
          });
        } else if (isRestrictedRoute) {
          toast.warning('Please complete your company setup to access this feature.', {
            autoClose: 5000,
            toastId: 'company-setup-required'
          });
        }
        setHasShownToast(true);
      }
    }
    
    // If company data exists, ensure modal is hidden
    if (company && showCompanyModal) {
      setShowCompanyModal(false);
    }
  }, [authLoading, user, isCompanySetupRequired, isRestrictedRoute, hasShownToast, isExemptRoute, companyLoading, company, showCompanyModal]);

  const handleCompanyModalClose = () => {
    if (isCompanySetupRequired) {
      // Don't allow closing if company setup is required
      return;
    }
    setShowCompanyModal(false);
  };

  const handleCompanySetupSuccess = () => {
    setShowCompanyModal(false);
    setHasShownToast(false);
    refetchCompany();
    toast.success('Company details saved successfully! You can now access all features.', {
      autoClose: 3000,
    });
  };

  // Don't render guard for super admins or exempt routes
  if (authLoading || !user || user.is_super_admin || isExemptRoute) {
    return (
      <>
        {children}
        <StickyNotesPanel />
      </>
    );
  }

  // Show loading state while checking company
  if (companyLoading) {
    return (
      <>
        {children}
        <StickyNotesPanel />
      </>
    );
  }

  return (
    <>
      {children}
      <StickyNotesPanel />
      
      {/* Company setup modal - required if no company exists */}
      <CompanyDetailsModal
        open={showCompanyModal}
        onClose={handleCompanyModalClose}
        onSuccess={handleCompanySetupSuccess}
        isRequired={isCompanySetupRequired}
      />
    </>
  );
};

export default CompanySetupGuard;