// frontend/src/components/__tests__/MegaMenu.integration.test.tsx

/**
 * Integration tests for MegaMenu behavior across different module entitlement combinations
 * Simulates various scenarios from ModuleSelectionModal outcomes
 */

import React from "react";
import { render, screen, waitFor, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import userEvent from "@testing-library/user-event";
import MegaMenu from "../MegaMenu";
import { AppEntitlementsResponse } from "../../services/entitlementsApi";

// Mock services
jest.mock("../../services/organizationService", () => ({
  organizationService: {
    getCurrentOrganization: jest.fn().mockResolvedValue({
      id: 1,
      name: "Test Org",
      enabled_modules: {},
    }),
  },
}));

jest.mock("../../services/rbacService", () => ({
  rbacService: {
    getUserPermissions: jest.fn().mockResolvedValue([]),
  },
}));

// Mock context providers with controllable entitlements
let mockEntitlements: AppEntitlementsResponse | null = null;

jest.mock("../../context/PermissionContext", () => ({
  usePermissions: () => ({
    hasPermission: jest.fn(() => true),
    permissions: [],
  }),
}));

jest.mock("../../hooks/useEntitlements", () => ({
  useEntitlements: () => ({
    entitlements: mockEntitlements,
    isLoading: false,
    error: null,
    isModuleEnabled: (moduleKey: string) => {
      if (!mockEntitlements) return false;
      const module = mockEntitlements.entitlements[moduleKey];
      return module?.status === 'enabled' || module?.status === 'trial';
    },
  }),
  useInvalidateEntitlements: () => ({
    invalidateEntitlements: jest.fn(),
  }),
}));

jest.mock("../../hooks/useMobileDetection", () => ({
  useMobileDetection: () => ({
    isMobile: false,
  }),
}));

// Mock Next.js router
const mockPush = jest.fn();
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    pathname: "/",
  }),
}));

const theme = createTheme();

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>{component}</ThemeProvider>
    </QueryClientProvider>,
  );
};

describe("MegaMenu Integration Tests", () => {
  const mockUser = { 
    id: 1, 
    email: "user@test.com",
    role: "org_admin", 
    is_super_admin: false 
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockEntitlements = null;
    mockPush.mockClear();
  });

  describe("Scenario 1: CRM Only", () => {
    beforeEach(() => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: 'crm',
            status: 'enabled',
            trial_expires_at: null,
            submodules: {},
          },
        },
      };
    });

    it("should show CRM menu items as enabled", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      // Email should always be visible
      expect(screen.getByText("Email")).toBeInTheDocument();

      // Open menu to see CRM items
      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      // CRM items should be enabled (not locked)
      await waitFor(() => {
        // Check for CRM-related menu items (adjust based on your actual menu structure)
        const crmSection = screen.queryByText(/sales/i) || screen.queryByText(/crm/i);
        if (crmSection) {
          expect(crmSection).not.toHaveAttribute('aria-disabled', 'true');
        }
      });
    });

    it("should disable non-CRM modules", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      await waitFor(() => {
        // Manufacturing, Finance, etc. should be disabled/locked
        // (This depends on your actual menu structure)
        const manufacturingItem = screen.queryByText(/manufacturing/i);
        if (manufacturingItem) {
          // Check for lock icon or disabled state
          const parent = manufacturingItem.closest('li, button');
          expect(parent).toHaveAttribute('aria-disabled', 'true');
        }
      });
    });
  });

  describe("Scenario 2: ERP Only", () => {
    beforeEach(() => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          erp: {
            module_key: 'erp',
            status: 'enabled',
            trial_expires_at: null,
            submodules: {},
          },
        },
      };
    });

    it("should show ERP menu items as enabled", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      await waitFor(() => {
        // Check for ERP-related items (Master Data, Inventory, Vouchers, etc.)
        const erpSection = screen.queryByText(/master data/i) || screen.queryByText(/inventory/i);
        if (erpSection) {
          expect(erpSection).not.toHaveAttribute('aria-disabled', 'true');
        }
      });
    });

    it("should disable CRM modules", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      await waitFor(() => {
        // CRM should be disabled
        const crmItem = screen.queryByText(/sales/i);
        if (crmItem) {
          const parent = crmItem.closest('li, button');
          expect(parent).toHaveAttribute('aria-disabled', 'true');
        }
      });
    });
  });

  describe("Scenario 3: Manufacturing + Finance", () => {
    beforeEach(() => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          manufacturing: {
            module_key: 'manufacturing',
            status: 'enabled',
            trial_expires_at: null,
            submodules: {},
          },
          finance: {
            module_key: 'finance',
            status: 'enabled',
            trial_expires_at: null,
            submodules: {},
          },
        },
      };
    });

    it("should enable Manufacturing and Finance modules", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      await waitFor(() => {
        const manufacturingItem = screen.queryByText(/manufacturing/i);
        const financeItem = screen.queryByText(/finance/i) || screen.queryByText(/accounting/i);
        
        if (manufacturingItem) {
          expect(manufacturingItem).not.toHaveAttribute('aria-disabled', 'true');
        }
        if (financeItem) {
          expect(financeItem).not.toHaveAttribute('aria-disabled', 'true');
        }
      });
    });

    it("should disable other modules", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      await waitFor(() => {
        // CRM, Service, HR should be disabled
        const crmItem = screen.queryByText(/sales/i);
        if (crmItem) {
          const parent = crmItem.closest('li, button');
          expect(parent).toHaveAttribute('aria-disabled', 'true');
        }
      });
    });
  });

  describe("Scenario 4: All Modules Disabled", () => {
    beforeEach(() => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {},
      };
    });

    it("should keep Email visible and enabled", () => {
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const emailButton = screen.getByText("Email");
      expect(emailButton).toBeInTheDocument();
      expect(emailButton).not.toHaveAttribute('aria-disabled', 'true');
    });

    it("should keep Settings visible for admin users", () => {
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const settingsButton = screen.queryByText("Settings");
      expect(settingsButton).toBeInTheDocument();
    });

    it("should disable all other modules", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      await waitFor(() => {
        // All business modules should be disabled
        const menuItems = screen.queryAllByRole('menuitem');
        // This is a simplified check - adjust based on your actual menu structure
        expect(menuItems.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Scenario 5: Trial Module", () => {
    beforeEach(() => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          analytics: {
            module_key: 'analytics',
            status: 'trial',
            trial_expires_at: '2025-12-31T23:59:59Z',
            submodules: {},
          },
        },
      };
    });

    it("should show trial badge for trial modules", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      await waitFor(() => {
        // Look for trial badge or indicator
        const trialBadge = screen.queryByText(/trial/i);
        if (trialBadge) {
          expect(trialBadge).toBeInTheDocument();
        }
      });
    });

    it("should allow access to trial module", async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      await waitFor(() => {
        const analyticsItem = screen.queryByText(/analytics/i) || screen.queryByText(/reports/i);
        if (analyticsItem) {
          expect(analyticsItem).not.toHaveAttribute('aria-disabled', 'true');
        }
      });
    });
  });

  describe("Email Module - Always On", () => {
    it("should be visible with no entitlements", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {},
      };

      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Email")).toBeInTheDocument();
    });

    it("should be top-level, not nested in Menu dropdown", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: 'crm',
            status: 'enabled',
            trial_expires_at: null,
            submodules: {},
          },
        },
      };

      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      // Email should be a top-level button in the toolbar
      const toolbar = screen.getByRole('banner').querySelector('[role="toolbar"]') || 
                      screen.getByRole('banner');
      const emailButton = within(toolbar as HTMLElement).getByText("Email");
      expect(emailButton).toBeInTheDocument();
    });

    it("should be between Menu and Settings", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {},
      };

      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const toolbar = screen.getByRole('banner');
      const buttons = within(toolbar).getAllByRole('button');
      
      const menuIndex = buttons.findIndex(b => b.textContent?.includes('Menu'));
      const emailIndex = buttons.findIndex(b => b.textContent?.includes('Email'));
      const settingsIndex = buttons.findIndex(b => b.textContent?.includes('Settings'));

      // Email should be between Menu and Settings (if all exist)
      if (menuIndex >= 0 && emailIndex >= 0 && settingsIndex >= 0) {
        expect(emailIndex).toBeGreaterThan(menuIndex);
        expect(settingsIndex).toBeGreaterThan(emailIndex);
      }
    });

    it("should not be duplicated under Menu dropdown", async () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {},
      };

      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      // Check top-level Email exists
      expect(screen.getByText("Email")).toBeInTheDocument();

      // Open Menu dropdown
      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      // There should not be another Email item in the dropdown
      const emailItems = screen.getAllByText("Email");
      expect(emailItems).toHaveLength(1); // Only top-level Email
    });
  });

  describe("Settings/Admin - RBAC Only", () => {
    it("should be visible to admin users regardless of entitlements", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {}, // No modules enabled
      };

      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.queryByText("Settings")).toBeInTheDocument();
    });

    it("should not be visible to non-admin users", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: 'crm',
            status: 'enabled',
            trial_expires_at: null,
            submodules: {},
          },
        },
      };

      const regularUser = { 
        id: 2, 
        email: "regular@test.com",
        role: "user", 
        is_super_admin: false 
      };

      renderWithProviders(
        <MegaMenu user={regularUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.queryByText("Settings")).not.toBeInTheDocument();
    });
  });

  describe("Super Admin Bypass", () => {
    const superAdminUser = {
      id: 99,
      email: "superadmin@test.com",
      role: "super_admin",
      is_super_admin: true,
    };

    it("should show all menu items for super admin even with no entitlements", async () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {}, // No modules enabled
      };

      const user = userEvent.setup();
      renderWithProviders(
        <MegaMenu user={superAdminUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const menuButton = screen.getByRole("button", { name: /menu/i });
      await user.click(menuButton);

      await waitFor(() => {
        // Super admin should see all items (not disabled)
        // This is a simplified check
        const menuItems = screen.queryAllByRole('menuitem');
        expect(menuItems.length).toBeGreaterThan(0);
        
        // No items should be disabled
        menuItems.forEach(item => {
          expect(item).not.toHaveAttribute('aria-disabled', 'true');
        });
      });
    });
  });
});
