import React from "react";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import MegaMenu from "../MegaMenu";

// Mock services
jest.mock("../../services/organizationService", () => ({
  organizationService: {
    getCurrentOrganization: jest.fn(),
  },
}));

jest.mock("../../services/rbacService", () => ({
  rbacService: {
    getUserPermissions: jest.fn(),
  },
}));

// Mock context providers
jest.mock("../../context/PermissionContext", () => ({
  usePermissions: () => ({
    hasPermission: jest.fn(() => true),
    permissions: [],
  }),
}));

jest.mock("../../hooks/useEntitlements", () => ({
  useEntitlements: () => ({
    entitlements: null,
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

describe("MegaMenu Basic Rendering", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("displays ERP when no organization data", () => {
    const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
    renderWithProviders(
      <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
    );

    expect(screen.getByText("ERP")).toBeInTheDocument();
  });

  it("renders menu buttons for non-super admin", () => {
    const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
    renderWithProviders(
      <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
    );

    expect(screen.getByText("Menu")).toBeInTheDocument();
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("is not visible when isVisible is false", () => {
    const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
    const { container } = renderWithProviders(
      <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={false} />,
    );

    // Should render nothing when not visible
    expect(container.firstChild).toBeNull();
  });
});
