// frontend/src/pages/_app.tsx
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
import { useRouter } from "next/router";
import { AuthProvider } from "../context/AuthContext";
import { CompanyProvider } from "../context/CompanyContext"; // Updated import
import { EmailProvider } from "../context/EmailContext"; // Added import for EmailProvider
import { PermissionProvider } from "../context/PermissionContext";  // Added import for PermissionProvider
import { useState, useEffect } from "react"; // Added import for useState and useEffect
import Head from 'next/head';  // Added import for Head to handle meta tags
import AppLayout from "../components/AppLayout"; // Global layout with MegaMenu
// Removed ChatbotNavigator import as it may be causing the undefined component error

// Create modern theme using our design system
const theme = createTheme({
  palette: {
    primary: {
      main: "#2563eb", // var(--primary-600)
      light: "#3b82f6", // var(--primary-500)
      dark: "#1d4ed8", // var(--primary-700) - fixed typo from "#1dasc"
    },
    secondary: {
      main: "#7c3aed", // var(--secondary-600)
      light: "#8b5cf6", // var(--secondary-500)
      dark: "#6d28d9", // var(--secondary-700)
    },
    success: {
      main: "#059669", // var(--success-600)
      light: "#10b981", // var(--success-500)
      dark: "#047857", // var(--success-700)
    },
    warning: {
      main: "#d97706", // var(--warning-600)
      light: "#f59e0b", // var(--warning-500)
      dark: "#b45309", // var(--warning-700)
    },
    error: {
      main: "#dc2626", // var(--error-600)
      light: "#ef4444", // var(--error-500)
      dark: "#b91c1c", // var(--error-700)
    },
    info: {
      main: "#0891b2", // var(--info-600)
      light: "#06b6d4", // var(--info-500)
      dark: "#0e7490", // var(--info-700)
    },
    background: {
      default: "#f8fafc", // var(--bg-secondary)
      paper: "#ffffff", // var(--bg-surface)
    },
    text: {
      primary: "#111827", // var(--text-primary)
      secondary: "#4b5563", // var(--text-secondary)
    },
  },
  typography: {
    fontFamily:
      'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
    h1: {
      fontSize: "2.25rem", // var(--font-size-4xl)
      fontWeight: 700,
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
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />  {/* Updated for iOS safe area support */}
      </Head>
      <AuthProvider>
        <QueryClientProvider client={queryClient}>
          <PermissionProvider>
            <CompanyProvider>
              <EmailProvider>
                <ThemeProvider theme={theme}>
                  <CssBaseline />
                  <ClientOnly>
                    {/* Global AppLayout wraps all pages and conditionally shows MegaMenu */}
                    <AppLayout>
                      {getLayout(<Component {...pageProps} />)}
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
                  </ClientOnly>
                </ThemeProvider>
              </EmailProvider>
            </CompanyProvider>
          </PermissionProvider>
        </QueryClientProvider>
      </AuthProvider>
    </>
  );
}

export default MyApp;