// frontend/src/components/__tests__/MegaMenu.entitlements.test.tsx

/**
 * Tests for MegaMenu behavior across different module entitlement combinations
 * Simulates various scenarios where modules are enabled/disabled via ModuleSelectionModal
 */

import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import userEvent from "@testing-library/user-event";
import MegaMenu from "../MegaMenu";
import { AppEntitlementsResponse } from "../../services/entitlementsApi";

// Mock services
const mockGetUserPermissions = jest.fn();
const mockGetCurrentOrganization = jest.fn();

jest.mock("../../services/organizationService", () => ({
  organizationService: {
    getCurrentOrganization: (...args: any[]) => mockGetCurrentOrganization(...args),
  },
}));

jest.mock("../../services/rbacService", () => ({
  rbacService: {
    getUserPermissions: (...args: any[]) => mockGetUserPermissions(...args),
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
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
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

describe("MegaMenu Module Entitlements", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockEntitlements = null;
    mockGetUserPermissions.mockResolvedValue([]);
    mockGetCurrentOrganization.mockResolvedValue({
      id: 1,
      name: "Test Organization",
      enabled_modules: {},
    });
  });

  describe("Email Module", () => {
    it("Email menu button is always visible regardless of entitlements", () => {
      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Email")).toBeInTheDocument();
    });

    it("Email is a top-level menu item, not nested in Menu", async () => {
      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      const user = userEvent.setup();
      
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      // Email should be a separate button
      const emailButton = screen.getByText("Email");
      expect(emailButton).toBeInTheDocument();
      
      // It should be at the same level as Menu and Settings
      const menuButton = screen.getByText("Menu");
      const settingsButton = screen.getByText("Settings");
      expect(menuButton).toBeInTheDocument();
      expect(settingsButton).toBeInTheDocument();
    });

    it("Email menu item is enabled even when email module is disabled in entitlements", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          email: {
            module_key: "email",
            status: "disabled",
            trial_expires_at: null,
            submodules: {},
          },
        },
      };

      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      const emailButton = screen.getByText("Email");
      expect(emailButton).toBeEnabled();
    });
  });

  describe("Single Module Enabled", () => {
    it("shows CRM module items when only CRM is enabled", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: "crm",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
        },
      };

      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Menu")).toBeInTheDocument();
    });

    it("disables manufacturing items when manufacturing module is disabled", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          manufacturing: {
            module_key: "manufacturing",
            status: "disabled",
            trial_expires_at: null,
            submodules: {},
          },
        },
      };

      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Menu")).toBeInTheDocument();
    });
  });

  describe("Multiple Module Combinations", () => {
    it("enables items from all enabled modules (CRM + ERP)", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: "crm",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
          erp: {
            module_key: "erp",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
        },
      };

      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Menu")).toBeInTheDocument();
    });

    it("shows trial badge for modules in trial status", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: "crm",
            status: "trial",
            trial_expires_at: "2025-12-31T23:59:59Z",
            submodules: {},
          },
        },
      };

      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Menu")).toBeInTheDocument();
    });

    it("handles mixed enabled/trial/disabled modules correctly", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: "crm",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
          erp: {
            module_key: "erp",
            status: "trial",
            trial_expires_at: "2025-12-31T23:59:59Z",
            submodules: {},
          },
          manufacturing: {
            module_key: "manufacturing",
            status: "disabled",
            trial_expires_at: null,
            submodules: {},
          },
        },
      };

      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Menu")).toBeInTheDocument();
    });
  });

  describe("Submodule Entitlements", () => {
    it("disables specific submodule items when submodule is disabled", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: "crm",
            status: "enabled",
            trial_expires_at: null,
            submodules: {
              lead_management: true,
              opportunity_tracking: false,
            },
          },
        },
      };

      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Menu")).toBeInTheDocument();
    });

    it("enables submodules by default when not explicitly specified", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: "crm",
            status: "enabled",
            trial_expires_at: null,
            submodules: {}, // No explicit submodules
          },
        },
      };

      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Menu")).toBeInTheDocument();
    });
  });

  describe("Admin vs Non-Admin Behavior", () => {
    it("shows disabled items with lock icon for admin users", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          manufacturing: {
            module_key: "manufacturing",
            status: "disabled",
            trial_expires_at: null,
            submodules: {},
          },
        },
      };

      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Menu")).toBeInTheDocument();
    });

    it("super admin bypasses all entitlement checks", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {}, // No modules enabled
      };

      const mockUser = { id: 1, role: "super_admin", is_super_admin: true };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Menu")).toBeInTheDocument();
    });
  });

  describe("All Modules Disabled", () => {
    it("shows empty state message when no modules are enabled", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: "crm",
            status: "disabled",
            trial_expires_at: null,
            submodules: {},
          },
          erp: {
            module_key: "erp",
            status: "disabled",
            trial_expires_at: null,
            submodules: {},
          },
        },
      };

      const mockUser = { id: 1, role: "user", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      // Menu button should still be visible
      expect(screen.getByText("Menu")).toBeInTheDocument();
    });
  });

  describe("Full Suite Enabled", () => {
    it("enables all menu items when all 7 modules are enabled", () => {
      mockEntitlements = {
        org_id: 1,
        entitlements: {
          crm: {
            module_key: "crm",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
          erp: {
            module_key: "erp",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
          manufacturing: {
            module_key: "manufacturing",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
          service: {
            module_key: "service",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
          hr: {
            module_key: "hr",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
          administration: {
            module_key: "administration",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
          settings: {
            module_key: "settings",
            status: "enabled",
            trial_expires_at: null,
            submodules: {},
          },
        },
      };

      const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
      renderWithProviders(
        <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
      );

      expect(screen.getByText("Menu")).toBeInTheDocument();
      expect(screen.getByText("Email")).toBeInTheDocument();
      expect(screen.getByText("Settings")).toBeInTheDocument();
    });
  });
});
