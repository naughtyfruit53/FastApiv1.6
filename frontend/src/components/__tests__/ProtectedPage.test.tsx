// frontend/src/components/__tests__/ProtectedPage.test.tsx

import React from 'react';
import { render, screen } from '@testing-library/react';
import { ProtectedPage, withProtection } from '../ProtectedPage';
import { usePermissionCheck } from '../../hooks/usePermissionCheck';
import { useRouter } from 'next/navigation';

// Mock dependencies
jest.mock('../../hooks/usePermissionCheck');
jest.mock('next/navigation');

const mockUsePermissionCheck = usePermissionCheck as jest.MockedFunction<typeof usePermissionCheck>;
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;

describe('ProtectedPage', () => {
  const mockRouter = {
    push: jest.fn(),
    back: jest.fn(),
  };

  const mockPermissionCheck = {
    isReady: true,
    isLoading: false,
    user: { id: 1, role: 'manager' },
    organizationId: 100,
    userPermissions: ['crm.read'],
    entitlements: {},
    hasTenantContext: true,
    checkTenantAccess: jest.fn(),
    checkModuleEntitled: jest.fn(),
    checkSubmoduleEntitled: jest.fn(),
    getModuleEntitlementStatus: jest.fn(),
    checkPermission: jest.fn(),
    checkUserRole: jest.fn(),
    checkIsSuperAdmin: jest.fn(),
    checkIsOrgAdmin: jest.fn(),
    checkCanManageRole: jest.fn(),
    checkModuleAccess: jest.fn(),
    checkSubmoduleAccess: jest.fn(),
  };

  beforeEach(() => {
    mockUseRouter.mockReturnValue(mockRouter as any);
    mockUsePermissionCheck.mockReturnValue(mockPermissionCheck as any);
    jest.clearAllMocks();
  });

  describe('Loading State', () => {
    it('should show loading state when not ready', () => {
      mockUsePermissionCheck.mockReturnValue({
        ...mockPermissionCheck,
        isReady: false,
        isLoading: true,
      } as any);

      render(
        <ProtectedPage moduleKey="crm">
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.getByText('Verifying access...')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });

    it('should show custom loading component when provided', () => {
      mockUsePermissionCheck.mockReturnValue({
        ...mockPermissionCheck,
        isReady: false,
        isLoading: true,
      } as any);

      render(
        <ProtectedPage
          moduleKey="crm"
          loadingComponent={<div>Custom Loading...</div>}
        >
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.getByText('Custom Loading...')).toBeInTheDocument();
      expect(screen.queryByText('Verifying access...')).not.toBeInTheDocument();
    });
  });

  describe('Access Granted', () => {
    it('should render children when module access is granted', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: true,
        enforcementLevel: 'RBAC',
      });

      render(
        <ProtectedPage moduleKey="crm" action="read">
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
      expect(mockPermissionCheck.checkModuleAccess).toHaveBeenCalledWith('crm', 'read');
    });

    it('should render children when submodule access is granted', () => {
      mockPermissionCheck.checkSubmoduleAccess.mockReturnValue({
        hasPermission: true,
        enforcementLevel: 'RBAC',
      });

      render(
        <ProtectedPage moduleKey="crm" submoduleKey="leads" action="write">
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
      expect(mockPermissionCheck.checkSubmoduleAccess).toHaveBeenCalledWith(
        'crm',
        'leads',
        'write'
      );
    });

    it('should render children when custom check passes', () => {
      const customCheck = jest.fn().mockReturnValue(true);

      render(
        <ProtectedPage customCheck={customCheck}>
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
      expect(customCheck).toHaveBeenCalledWith(mockPermissionCheck);
    });
  });

  describe('Access Denied', () => {
    it('should show access denied UI when module access is denied', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Module not enabled',
        enforcementLevel: 'ENTITLEMENT',
      });

      render(
        <ProtectedPage moduleKey="crm" action="read">
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.getByText('Access Denied')).toBeInTheDocument();
      expect(screen.getByText('Module not enabled')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });

    it('should show access denied UI when permission is missing', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Insufficient permissions',
        enforcementLevel: 'RBAC',
      });

      render(
        <ProtectedPage moduleKey="crm" action="write">
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.getByText('Access Denied')).toBeInTheDocument();
      expect(screen.getByText('Insufficient permissions')).toBeInTheDocument();
    });

    it('should show custom access denied message', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Module not enabled',
        enforcementLevel: 'ENTITLEMENT',
      });

      render(
        <ProtectedPage
          moduleKey="crm"
          accessDeniedMessage="You need a premium subscription"
        >
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.getByText('You need a premium subscription')).toBeInTheDocument();
    });

    it('should call onAccessDenied callback when access is denied', () => {
      const onAccessDenied = jest.fn();

      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Module not enabled',
        enforcementLevel: 'ENTITLEMENT',
      });

      render(
        <ProtectedPage moduleKey="crm" onAccessDenied={onAccessDenied}>
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(onAccessDenied).toHaveBeenCalledWith('Module not enabled');
    });

    it('should show upgrade prompt for entitlement issues', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Module not enabled',
        enforcementLevel: 'ENTITLEMENT',
      });

      render(
        <ProtectedPage moduleKey="crm" showUpgradePrompt={true}>
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.getByText('Module Not Enabled')).toBeInTheDocument();
      expect(screen.getByText(/requires the.*crm.*module/i)).toBeInTheDocument();
      expect(screen.getByText('View Settings')).toBeInTheDocument();
    });

    it('should hide upgrade prompt when showUpgradePrompt is false', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Module not enabled',
        enforcementLevel: 'ENTITLEMENT',
      });

      render(
        <ProtectedPage moduleKey="crm" showUpgradePrompt={false}>
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.queryByText('Module Not Enabled')).not.toBeInTheDocument();
      expect(screen.queryByText('View Settings')).not.toBeInTheDocument();
    });

    it('should show custom access denied component', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Module not enabled',
        enforcementLevel: 'ENTITLEMENT',
      });

      render(
        <ProtectedPage
          moduleKey="crm"
          accessDeniedComponent={<div>Custom Access Denied</div>}
        >
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(screen.getByText('Custom Access Denied')).toBeInTheDocument();
      expect(screen.queryByText('Access Denied')).not.toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('should redirect to dashboard when redirectOnDenied is true', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Module not enabled',
        enforcementLevel: 'ENTITLEMENT',
      });

      render(
        <ProtectedPage moduleKey="crm" redirectOnDenied={true}>
          <div>Protected Content</div>
        </ProtectedPage>
      );

      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard');
    });

    it('should navigate back when Go Back button is clicked', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Module not enabled',
        enforcementLevel: 'ENTITLEMENT',
      });

      render(
        <ProtectedPage moduleKey="crm">
          <div>Protected Content</div>
        </ProtectedPage>
      );

      const goBackButton = screen.getByText('Go Back');
      goBackButton.click();

      expect(mockRouter.back).toHaveBeenCalled();
    });

    it('should navigate to dashboard when Go to Dashboard button is clicked', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Module not enabled',
        enforcementLevel: 'ENTITLEMENT',
      });

      render(
        <ProtectedPage moduleKey="crm">
          <div>Protected Content</div>
        </ProtectedPage>
      );

      const dashboardButton = screen.getByText('Go to Dashboard');
      dashboardButton.click();

      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard');
    });
  });

  describe('withProtection HOC', () => {
    it('should wrap component with protection', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: true,
        enforcementLevel: 'RBAC',
      });

      const TestComponent: React.FC<{ title: string }> = ({ title }) => (
        <div>{title}</div>
      );

      const ProtectedComponent = withProtection(TestComponent, {
        moduleKey: 'crm',
        action: 'read',
      });

      render(<ProtectedComponent title="Test Title" />);

      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(mockPermissionCheck.checkModuleAccess).toHaveBeenCalledWith('crm', 'read');
    });

    it('should deny access through HOC', () => {
      mockPermissionCheck.checkModuleAccess.mockReturnValue({
        hasPermission: false,
        reason: 'Access denied',
        enforcementLevel: 'RBAC',
      });

      const TestComponent: React.FC = () => <div>Test Content</div>;

      const ProtectedComponent = withProtection(TestComponent, {
        moduleKey: 'crm',
        action: 'write',
      });

      render(<ProtectedComponent />);

      expect(screen.queryByText('Test Content')).not.toBeInTheDocument();
      expect(screen.getByText('Access Denied')).toBeInTheDocument();
    });
  });
});
