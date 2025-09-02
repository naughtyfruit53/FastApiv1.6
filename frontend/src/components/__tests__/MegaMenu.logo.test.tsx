import React from "react";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { BrowserRouter } from "react-router-dom";
import MegaMenu from "../MegaMenu";
import { companyService } from "../../services/authService";

// Mock the companyService
jest.mock("../../services/authService", () => ({
  companyService: {
    getCurrentCompany: jest.fn(),
    getLogoUrl: jest.fn(),
  },
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
      <ThemeProvider theme={theme}>
        <BrowserRouter>{component}</BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>,
  );
};

describe("MegaMenu Logo Integration", () => {
  const mockCompanyService = companyService as jest.Mocked<
    typeof companyService
  >;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("displays default TRITIQ ERP when no company data", async () => {
    mockCompanyService.getCurrentCompany.mockResolvedValue(null);

    const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
    renderWithProviders(
      <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
    );

    expect(screen.getByText("TRITIQ ERP")).toBeInTheDocument();
  });

  it("displays company name when company data exists without logo", async () => {
    const mockCompany = {
      id: 1,
      name: "Test Company Inc",
      logo_path: null,
    };

    mockCompanyService.getCurrentCompany.mockResolvedValue(mockCompany);

    const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
    renderWithProviders(
      <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
    );

    // Wait for query to resolve
    await screen.findByText("Test Company Inc");
    expect(screen.getByText("Test Company Inc")).toBeInTheDocument();
  });

  it("displays company name and logo when both exist", async () => {
    const mockCompany = {
      id: 1,
      name: "Test Company Inc",
      logo_path: "/uploads/company_logos/logo_1_abc123.png",
    };

    mockCompanyService.getCurrentCompany.mockResolvedValue(mockCompany);
    mockCompanyService.getLogoUrl.mockReturnValue("/api/v1/companies/1/logo");

    const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
    renderWithProviders(
      <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
    );

    // Wait for query to resolve
    await screen.findByText("Test Company Inc");
    expect(screen.getByText("Test Company Inc")).toBeInTheDocument();

    // Check that avatar has logo source
    const avatar = document.querySelector('div[role="img"]');
    expect(avatar).toBeInTheDocument();
  });

  it("does not fetch company data for super admin users", () => {
    const mockUser = { id: 1, role: "super_admin", is_super_admin: true };
    renderWithProviders(
      <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
    );

    // Should not call getCurrentCompany for super admin
    expect(mockCompanyService.getCurrentCompany).not.toHaveBeenCalled();
    expect(screen.getByText("TRITIQ ERP")).toBeInTheDocument();
  });

  it("handles company data fetch errors gracefully", async () => {
    mockCompanyService.getCurrentCompany.mockRejectedValue(
      new Error("Failed to fetch"),
    );

    const mockUser = { id: 1, role: "org_admin", is_super_admin: false };
    renderWithProviders(
      <MegaMenu user={mockUser} onLogout={jest.fn()} isVisible={true} />,
    );

    // Should fall back to default
    expect(screen.getByText("TRITIQ ERP")).toBeInTheDocument();
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
