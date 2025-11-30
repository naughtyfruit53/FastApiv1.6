// frontend/src/pages/_app.tsx
// TritIQ BOS Brand Kit v1
import { AppProps } from "next/app";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "../styles/modern-theme.css";
import "../styles/print.css";
import "../styles/mobile/mobile-theme.css";
import "../styles/email-reader.css";  // Moved global CSS import here
import { AuthProvider } from "../context/AuthContext";
import { CompanyProvider } from "../context/CompanyContext"; // Updated import
import { EmailProvider } from "../context/EmailContext"; // Added import for EmailProvider
import { PermissionProvider } from "../context/PermissionContext";  // Added import for PermissionProvider
import { OrganizationProvider } from "../context/OrganizationContext";  // NEW: Added import for OrganizationProvider to fix undefined context error
import { useState, useEffect } from "react"; // Added import for useState and useEffect
import Head from 'next/head';  // Added import for Head to handle meta tags
import AppLayout from "../components/AppLayout"; // Global layout with MegaMenu
import ErrorBoundary from "../components/ErrorBoundary"; // Error boundary for catching runtime errors
// Removed ChatbotNavigator import as it may be causing the undefined component error
import CompanySetupGuard from "../components/CompanySetupGuard";  // NEW: Import CompanySetupGuard to show modal on login if company details missing

// TritIQ BOS Brand Tokens
const tritiqBrandTokens = {
  blue: "#0A2A43",
  cyan: "#18E0B5",
  slate: "#4A5568",
  cloud: "#F7FAFC",
  black: "#0D0D0D",
  success: "#16A34A",
  warning: "#F59E0B",
  danger: "#EF4444",
  info: "#3B82F6",
};

// Create modern theme using TritIQ BOS design system
const theme = createTheme({
  palette: {
    primary: {
      main: tritiqBrandTokens.blue, // TritIQ Blue
      light: "#0D3A5C",
      dark: "#081F33",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: tritiqBrandTokens.cyan, // TritIQ Cyan
      light: "#3DE6C2",
      dark: "#10A888",
      contrastText: tritiqBrandTokens.black,
    },
    success: {
      main: tritiqBrandTokens.success,
      light: "#22C55E",
      dark: "#15803D",
    },
    warning: {
      main: tritiqBrandTokens.warning,
      light: "#FBBF24",
      dark: "#D97706",
    },
    error: {
      main: tritiqBrandTokens.danger,
      light: "#F87171",
      dark: "#DC2626",
    },
    info: {
      main: tritiqBrandTokens.info,
      light: "#60A5FA",
      dark: "#2563EB",
    },
    background: {
      default: tritiqBrandTokens.cloud, // TritIQ Cloud
      paper: "#FFFFFF",
    },
    text: {
      primary: tritiqBrandTokens.black, // TritIQ Black
      secondary: tritiqBrandTokens.slate, // TritIQ Slate
    },
  },
  typography: {
    fontFamily: '"Inter", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
    h1: {
      fontSize: "2.25rem", // var(--font-size-4xl)
      fontWeight: 700, // Heading primary weight
      lineHeight: 1.25, // var(--leading-tight)
    },
    h2: {
      fontSize: "1.875rem", // var(--font-size-3xl)
      fontWeight: 700,
      lineHeight: 1.25,
    },
    h3: {
      fontSize: "1.5rem", // var(--font-size-2xl)
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h4: {
      fontSize: "1.25rem", // var(--font-size-xl)
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h5: {
      fontSize: "1.125rem", // var(--font-size-lg)
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h6: {
      fontSize: "1rem", // var(--font-size-base)
      fontWeight: 500,
      lineHeight: 1.25,
    },
    body1: {
      fontSize: "1rem", // var(--font-size-base)
      lineHeight: 1.5, // var(--leading-normal)
    },
    body2: {
      fontSize: "0.875rem", // var(--font-size-sm)
      lineHeight: 1.5,
    },
    caption: {
      fontSize: "0.75rem", // var(--font-size-xs)
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 8, // var(--radius-md) converted to px
  },
  shadows: [
    "none",
    "0 1px 2px 0 rgba(0, 0, 0, 0.05)", // var(--shadow-sm)
    "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)", // var(--shadow-md)
    "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)", // var(--shadow-lg)
    "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)", // var(--shadow-xl)
    ...Array(20).fill(
      "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
    ),
  ],
  components: {
    MuiTextField: {
      defaultProps: {
        variant: "outlined",
        size: "small",
      },
      styleOverrides: {
        root: {
          "& .MuiInputBase-input": {
            fontSize: "12px",
          },
          "& .MuiInputLabel-root": {
            fontSize: "12px",
          },
          "& .MuiFormHelperText-root": {
            fontSize: "10px",
          },
        },
      },
    },
    MuiDialogTitle: {
      styleOverrides: {
        root: {
          "& .MuiTypography-h6": {
            fontSize: "18px",
            fontWeight: 600,
          },
        },
      },
    },
  },
});

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const ClientOnly = ({ children }: { children: React.ReactNode }) => {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);
  return mounted ? <>{children}</> : null;
};

function MyApp({ Component, pageProps }: AppProps) {
  // Use the layout defined at the page level, if available
  const getLayout = Component.getLayout || ((page) => page);

  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        {/* TritIQ BOS Brand Kit - Favicon and Icons */}
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#0A2A43" />
        <meta name="description" content="TritIQ BOS - Business Made Simple" />
        {/* Inter Font from Google Fonts */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet" />
      </Head>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <ClientOnly>
          <ErrorBoundary>
            <AuthProvider>
              <OrganizationProvider>
                <QueryClientProvider client={queryClient}>
                  <PermissionProvider>
                    <CompanyProvider>
                      <EmailProvider>
                        <AppLayout>
                          <CompanySetupGuard>
                            {getLayout(<Component {...pageProps} />)}
                          </CompanySetupGuard>
                        </AppLayout>
                        <ToastContainer
                          position="top-right"
                          autoClose={5000}
                          hideProgressBar={false}
                          newestOnTop={false}
                          closeOnClick
                          rtl={false}
                          pauseOnFocusLoss
                          draggable
                          pauseOnHover
                        />
                      </EmailProvider>
                    </CompanyProvider>
                  </PermissionProvider>
                </QueryClientProvider>
              </OrganizationProvider>
            </AuthProvider>
          </ErrorBoundary>
        </ClientOnly>
      </ThemeProvider>
    </>
  );
}

export default MyApp;