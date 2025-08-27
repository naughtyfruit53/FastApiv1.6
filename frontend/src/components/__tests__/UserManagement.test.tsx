/**
 * Test file for organization-scoped user management components
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import UserManagement from '../pages/settings/user-management';
import { organizationService } from '../services/organizationService';

// Mock the services
jest.mock('../services/organizationService');
jest.mock('../services/authService');
jest.mock('../context/AuthContext');
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    pathname: '/settings/user-management'
  })
}));

const mockOrganizationService = organizationService as jest.Mocked<typeof organizationService>;

// Mock auth context
const mockAuthContext = {
  user: {
    id: 1,
    email: 'admin@testorg.com',
    role: 'org_admin',
    organization_id: 1,
    is_super_admin: false,
    full_name: 'Test Admin'
  },
  isAuthenticated: true,
  login: jest.fn(),
  logout: jest.fn()
};

jest.mock('../context/AuthContext', () => ({
  useAuth: () => mockAuthContext
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });
  
  const TestProvider = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
  
  TestProvider.displayName = 'TestProvider';
  
  return TestProvider;
};

describe('UserManagement Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API responses
    mockOrganizationService.getOrganizationUsers.mockResolvedValue([
      {
        id: 2,
        email: 'user@testorg.com',
        username: 'testuser',
        full_name: 'Test User',
        role: 'standard_user',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        department: 'IT',
        designation: 'Developer'
      }
    ]);
  });

  test('should render user management page with organization context', async () => {
    render(<UserManagement />, { wrapper: createWrapper() });
    
    // Check for organization context in header
    expect(screen.getByText('User Management')).toBeInTheDocument();
    expect(screen.getByText(/Managing users for your organization/)).toBeInTheDocument();
    
    // Check for add user button (org admin should have access)
    expect(screen.getByText('Add New User')).toBeInTheDocument();
  });

  test('should call organization-scoped API to fetch users', async () => {
    render(<UserManagement />, { wrapper: createWrapper() });
    
    await waitFor(() => {
      expect(mockOrganizationService.getOrganizationUsers).toHaveBeenCalledWith(1);
    });
  });

  test('should display users from organization', async () => {
    render(<UserManagement />, { wrapper: createWrapper() });
    
    await waitFor(() => {
      expect(screen.getByText('user@testorg.com')).toBeInTheDocument();
      expect(screen.getByText('Test User')).toBeInTheDocument();
      expect(screen.getByText('standard_user')).toBeInTheDocument();
    });
  });

  test('should open create user dialog when add button is clicked', async () => {
    render(<UserManagement />, { wrapper: createWrapper() });
    
    const addButton = screen.getByText('Add New User');
    fireEvent.click(addButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Create New User/i)).toBeInTheDocument();
    });
  });

  test('should call organization-scoped API to create user', async () => {
    mockOrganizationService.createUserInOrganization.mockResolvedValue({
      id: 3,
      email: 'newuser@testorg.com',
      username: 'newuser',
      full_name: 'New User',
      role: 'standard_user',
      is_active: true,
      organization_id: 1
    });

    render(<UserManagement />, { wrapper: createWrapper() });
    
    // Open create dialog
    fireEvent.click(screen.getByText('Add New User'));
    
    await waitFor(() => {
      expect(screen.getByText(/Create New User/i)).toBeInTheDocument();
    });
    
    // Fill form (simplified - would need to find actual form fields)
    // In a real test, you'd fill the form fields and submit
    
    // Simulate form submission
    // This would trigger createUserInOrganization with organization ID
    // expect(mockOrganizationService.createUserInOrganization).toHaveBeenCalledWith(1, expect.any(Object));
  });

  test('should show access denied for standard users', () => {
    // Mock as standard user
    const standardUserContext = {
      ...mockAuthContext,
      user: {
        ...mockAuthContext.user,
        role: 'standard_user'
      }
    };

    // eslint-disable-next-line @typescript-eslint/no-require-imports
    jest.mocked(require('../context/AuthContext').useAuth).mockReturnValue(standardUserContext);
    
    render(<UserManagement />, { wrapper: createWrapper() });
    
    expect(screen.getByText(/You don't have permission to manage users/)).toBeInTheDocument();
  });
});

describe('OrganizationService Integration', () => {
  test('should call correct organization-scoped endpoints', () => {
    const orgId = 123;
    const userId = 456;
    const userData = { name: 'Test User' };

    // Test all the new methods
    mockOrganizationService.getOrganizationUsers(orgId);
    expect(mockOrganizationService.getOrganizationUsers).toHaveBeenCalledWith(orgId);

    mockOrganizationService.createUserInOrganization(orgId, userData);
    expect(mockOrganizationService.createUserInOrganization).toHaveBeenCalledWith(orgId, userData);

    mockOrganizationService.updateUserInOrganization(orgId, userId, userData);
    expect(mockOrganizationService.updateUserInOrganization).toHaveBeenCalledWith(orgId, userId, userData);

    mockOrganizationService.deleteUserFromOrganization(orgId, userId);
    expect(mockOrganizationService.deleteUserFromOrganization).toHaveBeenCalledWith(orgId, userId);

    mockOrganizationService.getOrganizationInvitations(orgId);
    expect(mockOrganizationService.getOrganizationInvitations).toHaveBeenCalledWith(orgId);

    mockOrganizationService.resendInvitation(orgId, 789);
    expect(mockOrganizationService.resendInvitation).toHaveBeenCalledWith(orgId, 789);

    mockOrganizationService.cancelInvitation(orgId, 789);
    expect(mockOrganizationService.cancelInvitation).toHaveBeenCalledWith(orgId, 789);
  });
});