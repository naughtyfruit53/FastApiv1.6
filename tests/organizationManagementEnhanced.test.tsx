// tests/organizationManagementEnhanced.test.tsx

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react';
import OrganizationSwitcher from '../src/components/OrganizationSwitcher';
import OrganizationMembersDialog from '../src/components/OrganizationMembersDialog';
import OrganizationForm from '../src/components/OrganizationForm';
import { organizationService } from '../src/services/organizationService';

// Mock the organization service
jest.mock('../src/services/organizationService', () => ({
  organizationService: {
    getUserOrganizations: jest.fn(),
    switchOrganization: jest.fn(),
    getOrganizationMembers: jest.fn(),
    inviteUserToOrganization: jest.fn(),
    createOrganization: jest.fn(),
    createLicense: jest.fn(),
  },
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock window.location.reload
Object.defineProperty(window, 'location', {
  value: {
    reload: jest.fn(),
  },
  writable: true,
});

describe('OrganizationSwitcher', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    (organizationService.getUserOrganizations as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<OrganizationSwitcher />);
    expect(screen.getByText('Loading organizations...')).toBeInTheDocument();
  });

  it('renders single organization without switcher', async () => {
    const mockOrgs = [
      {
        id: 1,
        name: 'Test Organization',
        subdomain: 'test',
        role: 'org_admin',
        is_current: true,
      },
    ];

    (organizationService.getUserOrganizations as jest.Mock).mockResolvedValue(mockOrgs);

    await act(async () => {
      render(<OrganizationSwitcher />);
    });

    await waitFor(() => {
      expect(screen.getByText('Test Organization')).toBeInTheDocument();
      expect(screen.getByText('Role: org_admin')).toBeInTheDocument();
    });
  });

  it('renders switcher for multiple organizations', async () => {
    const mockOrgs = [
      {
        id: 1,
        name: 'Organization 1',
        subdomain: 'org1',
        role: 'admin',
        is_current: true,
      },
      {
        id: 2,
        name: 'Organization 2',
        subdomain: 'org2',
        role: 'super_admin',
        is_current: false,
      },
    ];

    (organizationService.getUserOrganizations as jest.Mock).mockResolvedValue(mockOrgs);

    await act(async () => {
      render(<OrganizationSwitcher />);
    });

    await waitFor(() => {
      expect(screen.getByLabelText('Organization')).toBeInTheDocument();
    });
  });

  it('handles organization switching', async () => {
    const mockOrgs = [
      {
        id: 1,
        name: 'Organization 1',
        subdomain: 'org1',
        role: 'admin',
        is_current: true,
      },
      {
        id: 2,
        name: 'Organization 2',
        subdomain: 'org2',
        role: 'super_admin',
        is_current: false,
      },
    ];

    (organizationService.getUserOrganizations as jest.Mock).mockResolvedValue(mockOrgs);
    (organizationService.switchOrganization as jest.Mock).mockResolvedValue({
      message: 'Successfully switched organization',
    });

    await act(async () => {
      render(<OrganizationSwitcher />);
    });

    await waitFor(() => {
      const select = screen.getByLabelText('Organization');
      fireEvent.mouseDown(select);
    });

    await waitFor(() => {
      const org2Option = screen.getByText('Organization 2');
      fireEvent.click(org2Option);
    });

    expect(organizationService.switchOrganization).toHaveBeenCalledWith(2);
  });

  it('displays error when organization switching fails', async () => {
    const mockOrgs = [
      {
        id: 1,
        name: 'Organization 1',
        subdomain: 'org1',
        role: 'admin',
        is_current: true,
      },
      {
        id: 2,
        name: 'Organization 2',
        subdomain: 'org2',
        role: 'super_admin',
        is_current: false,
      },
    ];

    (organizationService.getUserOrganizations as jest.Mock).mockResolvedValue(mockOrgs);
    (organizationService.switchOrganization as jest.Mock).mockRejectedValue(
      new Error('Failed to switch organization')
    );

    await act(async () => {
      render(<OrganizationSwitcher />);
    });

    await waitFor(() => {
      const select = screen.getByLabelText('Organization');
      fireEvent.mouseDown(select);
    });

    await waitFor(() => {
      const org2Option = screen.getByText('Organization 2');
      fireEvent.click(org2Option);
    });

    await waitFor(() => {
      expect(screen.getByText('Failed to switch organization')).toBeInTheDocument();
    });
  });
});

describe('OrganizationMembersDialog', () => {
  const defaultProps = {
    open: true,
    onClose: jest.fn(),
    organizationId: 1,
    organizationName: 'Test Organization',
    canInvite: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders member list correctly', async () => {
    const mockMembers = [
      {
        id: 1,
        email: 'admin@test.com',
        full_name: 'Admin User',
        role: 'org_admin',
        is_active: true,
        username: 'admin',
      },
      {
        id: 2,
        email: 'user@test.com',
        full_name: 'Regular User',
        role: 'standard_user',
        is_active: true,
        username: 'user',
      },
    ];

    (organizationService.getOrganizationMembers as jest.Mock).mockResolvedValue(mockMembers);

    await act(async () => {
      render(<OrganizationMembersDialog {...defaultProps} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Test Organization - Members')).toBeInTheDocument();
      expect(screen.getByText('Admin User')).toBeInTheDocument();
      expect(screen.getByText('Regular User')).toBeInTheDocument();
      expect(screen.getByText('admin@test.com')).toBeInTheDocument();
      expect(screen.getByText('user@test.com')).toBeInTheDocument();
    });
  });

  it('shows invite form when invite button is clicked', async () => {
    (organizationService.getOrganizationMembers as jest.Mock).mockResolvedValue([]);

    await act(async () => {
      render(<OrganizationMembersDialog {...defaultProps} />);
    });

    await waitFor(() => {
      const inviteButton = screen.getByText('Invite User');
      fireEvent.click(inviteButton);
    });

    expect(screen.getByText('Invite New User')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Full Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Temporary Password')).toBeInTheDocument();
  });

  it('handles user invitation successfully', async () => {
    (organizationService.getOrganizationMembers as jest.Mock).mockResolvedValue([]);
    (organizationService.inviteUserToOrganization as jest.Mock).mockResolvedValue({
      message: 'User invited successfully',
    });

    await act(async () => {
      render(<OrganizationMembersDialog {...defaultProps} />);
    });

    // Open invite form
    await waitFor(() => {
      const inviteButton = screen.getByText('Invite User');
      fireEvent.click(inviteButton);
    });

    // Fill form
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'newuser@test.com' },
    });
    fireEvent.change(screen.getByLabelText('Username'), {
      target: { value: 'newuser' },
    });
    fireEvent.change(screen.getByLabelText('Full Name'), {
      target: { value: 'New User' },
    });
    fireEvent.change(screen.getByLabelText('Temporary Password'), {
      target: { value: 'password123' },
    });

    // Submit invitation
    const sendButton = screen.getByText('Send Invitation');
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(organizationService.inviteUserToOrganization).toHaveBeenCalledWith(1, {
        email: 'newuser@test.com',
        username: 'newuser',
        full_name: 'New User',
        password: 'password123',
        role: 'standard_user',
      });
    });
  });

  it('hides invite button when canInvite is false', async () => {
    (organizationService.getOrganizationMembers as jest.Mock).mockResolvedValue([]);

    await act(async () => {
      render(<OrganizationMembersDialog {...defaultProps} canInvite={false} />);
    });

    await waitFor(() => {
      expect(screen.queryByText('Invite User')).not.toBeInTheDocument();
    });
  });
});

describe('OrganizationForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders license creation form correctly', () => {
    render(<OrganizationForm onSubmit={mockOnSubmit} mode="license" />);

    expect(screen.getByLabelText('Organization Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Admin Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Primary Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Primary Phone')).toBeInTheDocument();
    expect(screen.getByText('Create License')).toBeInTheDocument();
  });

  it('renders direct organization creation form correctly', () => {
    render(<OrganizationForm onSubmit={mockOnSubmit} mode="create" />);

    expect(screen.getByLabelText('Organization Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Subdomain')).toBeInTheDocument();
    expect(screen.getByLabelText('Business Type')).toBeInTheDocument();
    expect(screen.getByLabelText('Industry')).toBeInTheDocument();
    expect(screen.getByLabelText('Website')).toBeInTheDocument();
    expect(screen.getByLabelText('Max Users')).toBeInTheDocument();
    expect(screen.getByText('Create Organization')).toBeInTheDocument();
  });

  it('handles form submission for license creation', () => {
    render(<OrganizationForm onSubmit={mockOnSubmit} mode="license" />);

    // Fill required fields
    fireEvent.change(screen.getByLabelText('Organization Name'), {
      target: { value: 'Test Organization' },
    });
    fireEvent.change(screen.getByLabelText('Admin Password'), {
      target: { value: 'password123' },
    });
    fireEvent.change(screen.getByLabelText('Primary Email'), {
      target: { value: 'admin@test.com' },
    });
    fireEvent.change(screen.getByLabelText('Primary Phone'), {
      target: { value: '1234567890' },
    });
    fireEvent.change(screen.getByLabelText('Address'), {
      target: { value: '123 Test St' },
    });
    fireEvent.change(screen.getByLabelText('City'), {
      target: { value: 'Test City' },
    });
    fireEvent.change(screen.getByLabelText('State'), {
      target: { value: 'Test State' },
    });
    fireEvent.change(screen.getByLabelText('PIN Code'), {
      target: { value: '123456' },
    });

    // Submit form
    fireEvent.click(screen.getByText('Create License'));

    expect(mockOnSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        organization_name: 'Test Organization',
        admin_password: 'password123',
        superadmin_email: 'admin@test.com',
        primary_phone: '1234567890',
        address1: '123 Test St',
        city: 'Test City',
        state: 'Test State',
        pin_code: '123456',
      })
    );
  });

  it('handles form submission for direct organization creation', () => {
    render(<OrganizationForm onSubmit={mockOnSubmit} mode="create" />);

    // Fill required fields
    fireEvent.change(screen.getByLabelText('Organization Name'), {
      target: { value: 'Test Organization' },
    });
    fireEvent.change(screen.getByLabelText('Subdomain'), {
      target: { value: 'testorg' },
    });
    fireEvent.change(screen.getByLabelText('Primary Email'), {
      target: { value: 'admin@test.com' },
    });
    fireEvent.change(screen.getByLabelText('Primary Phone'), {
      target: { value: '1234567890' },
    });
    fireEvent.change(screen.getByLabelText('Address'), {
      target: { value: '123 Test St' },
    });
    fireEvent.change(screen.getByLabelText('City'), {
      target: { value: 'Test City' },
    });
    fireEvent.change(screen.getByLabelText('State'), {
      target: { value: 'Test State' },
    });
    fireEvent.change(screen.getByLabelText('PIN Code'), {
      target: { value: '123456' },
    });

    // Submit form
    fireEvent.click(screen.getByText('Create Organization'));

    expect(mockOnSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Test Organization',
        subdomain: 'testorg',
        primary_email: 'admin@test.com',
        primary_phone: '1234567890',
        address1: '123 Test St',
        city: 'Test City',
        state: 'Test State',
        pin_code: '123456',
      })
    );
  });

  it('populates form with initial data when editing', () => {
    const initialData = {
      name: 'Existing Organization',
      subdomain: 'existing',
      primary_email: 'admin@existing.com',
      primary_phone: '0987654321',
      city: 'Existing City',
    };

    render(
      <OrganizationForm
        onSubmit={mockOnSubmit}
        mode="create"
        initialData={initialData}
        isEditing={true}
      />
    );

    expect(screen.getByDisplayValue('Existing Organization')).toBeInTheDocument();
    expect(screen.getByDisplayValue('existing')).toBeInTheDocument();
    expect(screen.getByDisplayValue('admin@existing.com')).toBeInTheDocument();
    expect(screen.getByDisplayValue('0987654321')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Existing City')).toBeInTheDocument();
    expect(screen.getByText('Update Organization')).toBeInTheDocument();
  });
});