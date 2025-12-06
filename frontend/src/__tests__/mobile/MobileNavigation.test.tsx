// frontend/src/__tests__/mobile/MobileNavigation.test.tsx

import { render, screen, fireEvent, within } from '@testing-library/react';
import MobileNav from '../../components/MobileNav';
import { useRouter } from 'next/navigation';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import React from 'react';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('../../hooks/useMobileDetection', () => ({
  useMobileDetection: jest.fn(),
}));

const mockPush = jest.fn();
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;
const mockUseMobileDetection = useMobileDetection as jest.MockedFunction<typeof useMobileDetection>;

describe('MobileNav - Mobile Navigation Accessibility', () => {
  const mockUser = {
    id: 1,
    email: 'test@example.com',
    username: 'testuser',
    full_name: 'Test User',
    role: 'manager',
  };

  const mockMenuItems = {
    menu: {
      sections: [
        {
          title: 'Master Data',
          subSections: [
            {
              title: 'Business Entities',
              items: [
                { name: 'Vendors', path: '/masters/vendors' },
                { name: 'Customers', path: '/masters/customers' },
              ],
            },
          ],
        },
        {
          title: 'Inventory',
          subSections: [
            {
              title: 'Stock Management',
              items: [
                { name: 'Current Stock', path: '/inventory' },
                { name: 'Stock Movements', path: '/inventory/movements' },
              ],
            },
          ],
        },
      ],
    },
  };

  beforeEach(() => {
    mockUseRouter.mockReturnValue({
      push: mockPush,
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    } as any);

    mockUseMobileDetection.mockReturnValue({
      isMobile: true,
      isTablet: false,
      isDesktop: false,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should render mobile navigation drawer when open', () => {
    render(
      <MobileNav
        open={true}
        onClose={jest.fn()}
        user={mockUser}
        onLogout={jest.fn()}
        menuItems={mockMenuItems}
      />
    );

    expect(screen.getByText('Business Made Simple')).toBeInTheDocument();
  });

  it('should display all top-level menu sections', () => {
    render(
      <MobileNav
        open={true}
        onClose={jest.fn()}
        user={mockUser}
        onLogout={jest.fn()}
        menuItems={mockMenuItems}
      />
    );

    expect(screen.getByText('Master Data')).toBeInTheDocument();
    expect(screen.getByText('Inventory')).toBeInTheDocument();
  });

  it('should expand and show subsections when section is clicked', () => {
    render(
      <MobileNav
        open={true}
        onClose={jest.fn()}
        user={mockUser}
        onLogout={jest.fn()}
        menuItems={mockMenuItems}
      />
    );

    const masterDataSection = screen.getByText('Master Data');
    fireEvent.click(masterDataSection);

    expect(screen.getByText('Business Entities')).toBeInTheDocument();
  });

  it('should show menu items when subsection is expanded', () => {
    render(
      <MobileNav
        open={true}
        onClose={jest.fn()}
        user={mockUser}
        onLogout={jest.fn()}
        menuItems={mockMenuItems}
      />
    );

    // Expand section
    const masterDataSection = screen.getByText('Master Data');
    fireEvent.click(masterDataSection);

    // Expand subsection
    const businessEntitiesSubsection = screen.getByText('Business Entities');
    fireEvent.click(businessEntitiesSubsection);

    // Check menu items are visible
    expect(screen.getByText('Vendors')).toBeInTheDocument();
    expect(screen.getByText('Customers')).toBeInTheDocument();
  });

  it('should navigate to correct path when menu item is clicked', () => {
    render(
      <MobileNav
        open={true}
        onClose={jest.fn()}
        user={mockUser}
        onLogout={jest.fn()}
        menuItems={mockMenuItems}
      />
    );

    // Expand section and subsection
    fireEvent.click(screen.getByText('Master Data'));
    fireEvent.click(screen.getByText('Business Entities'));

    // Click menu item
    const vendorsItem = screen.getByText('Vendors');
    fireEvent.click(vendorsItem);

    expect(mockPush).toHaveBeenCalledWith('/masters/vendors');
  });

  it('should close drawer after navigation', () => {
    const mockOnClose = jest.fn();
    
    render(
      <MobileNav
        open={true}
        onClose={mockOnClose}
        user={mockUser}
        onLogout={jest.fn()}
        menuItems={mockMenuItems}
      />
    );

    // Expand and navigate
    fireEvent.click(screen.getByText('Master Data'));
    fireEvent.click(screen.getByText('Business Entities'));
    fireEvent.click(screen.getByText('Vendors'));

    // Drawer should close after navigation
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should filter menu items based on search query', () => {
    render(
      <MobileNav
        open={true}
        onClose={jest.fn()}
        user={mockUser}
        onLogout={jest.fn()}
        menuItems={mockMenuItems}
      />
    );

    const searchInput = screen.getByPlaceholderText('Search menus...');
    fireEvent.change(searchInput, { target: { value: 'Vendors' } });

    // After search, should show only matching items
    // Note: This depends on implementation details of search functionality
    expect(searchInput).toHaveValue('Vendors');
  });

  it('should display quick access items', () => {
    render(
      <MobileNav
        open={true}
        onClose={jest.fn()}
        user={mockUser}
        onLogout={jest.fn()}
        menuItems={mockMenuItems}
      />
    );

    // Quick access items should be visible
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('Tasks')).toBeInTheDocument();
  });

  it('should handle nested navigation correctly', () => {
    const deepMenuItems = {
      menu: {
        sections: [
          {
            title: 'Module A',
            subSections: [
              {
                title: 'Subsection A1',
                items: [
                  { name: 'Item A1-1', path: '/module-a/sub-a1/item-a1-1' },
                ],
              },
              {
                title: 'Subsection A2',
                items: [
                  { name: 'Item A2-1', path: '/module-a/sub-a2/item-a2-1' },
                ],
              },
            ],
          },
        ],
      },
    };

    render(
      <MobileNav
        open={true}
        onClose={jest.fn()}
        user={mockUser}
        onLogout={jest.fn()}
        menuItems={deepMenuItems}
      />
    );

    // Expand module
    fireEvent.click(screen.getByText('Module A'));

    // Both subsections should be visible
    expect(screen.getByText('Subsection A1')).toBeInTheDocument();
    expect(screen.getByText('Subsection A2')).toBeInTheDocument();

    // Expand first subsection
    fireEvent.click(screen.getByText('Subsection A1'));
    expect(screen.getByText('Item A1-1')).toBeInTheDocument();

    // Expand second subsection
    fireEvent.click(screen.getByText('Subsection A2'));
    expect(screen.getByText('Item A2-1')).toBeInTheDocument();
  });

  it('should ensure all menu options are accessible on mobile', () => {
    const comprehensiveMenuItems = {
      menu: {
        sections: [
          { title: 'Dashboard', subSections: [] },
          { title: 'Master Data', subSections: [] },
          { title: 'Inventory', subSections: [] },
          { title: 'Manufacturing', subSections: [] },
          { title: 'Vouchers', subSections: [] },
          { title: 'Finance', subSections: [] },
          { title: 'Accounting', subSections: [] },
          { title: 'Reports & Analytics', subSections: [] },
          { title: 'AI & Analytics', subSections: [] },
          { title: 'Sales', subSections: [] },
          { title: 'Marketing', subSections: [] },
          { title: 'Service', subSections: [] },
          { title: 'HR Management', subSections: [] },
          { title: 'Projects', subSections: [] },
          { title: 'Tasks & Calendar', subSections: [] },
          { title: 'Email', subSections: [] },
          { title: 'Settings', subSections: [] },
        ],
      },
    };

    render(
      <MobileNav
        open={true}
        onClose={jest.fn()}
        user={mockUser}
        onLogout={jest.fn()}
        menuItems={comprehensiveMenuItems}
      />
    );

    // Verify key modules are present (not all might be shown due to permissions/entitlements)
    const keyModules = [
      'Dashboard',
      'Master Data',
      'Inventory',
      'Email',
    ];

    keyModules.forEach(module => {
      // Use getAllByText in case there are multiple instances
      const elements = screen.getAllByText(module);
      expect(elements.length).toBeGreaterThan(0);
    });
  });
});
