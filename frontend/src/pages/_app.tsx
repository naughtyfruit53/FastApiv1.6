import { AppProps } from 'next/app';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../styles/modern-theme.css';
import Layout from '../components/layout'; // Use lowercase layout
import { useRouter } from 'next/router';
import { AuthProvider, useAuth } from '../context/AuthContext';
// Create modern theme using our design system
const theme = createTheme({
  palette: {
    primary: {
      main: '#2563eb', // var(--primary-600)
      light: '#3b82f6', // var(--primary-500)
      dark: '#1d4ed8', // var(--primary-700)
    },
    secondary: {
      main: '#7c3aed', // var(--secondary-600)
      light: '#8b5cf6', // var(--secondary-500)
      dark: '#6d28d9', // var(--secondary-700)
    },
    success: {
      main: '#059669', // var(--success-600)
      light: '#10b981', // var(--success-500)
      dark: '#047857', // var(--success-700)
    },
    warning: {
      main: '#d97706', // var(--warning-600)
      light: '#f59e0b', // var(--warning-500)
      dark: '#b45309', // var(--warning-700)
    },
    error: {
      main: '#dc2626', // var(--error-600)
      light: '#ef4444', // var(--error-500)
      dark: '#b91c1c', // var(--error-700)
    },
    info: {
      main: '#0891b2', // var(--info-600)
      light: '#06b6d4', // var(--info-500)
      dark: '#0e7490', // var(--info-700)
    },
    background: {
      default: '#f8fafc', // var(--bg-secondary)
      paper: '#ffffff', // var(--bg-surface)
    },
    text: {
      primary: '#111827', // var(--text-primary)
      secondary: '#4b5563', // var(--text-secondary)
    },
  },
  typography: {
    fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
    h1: {
      fontSize: '2.25rem', // var(--font-size-4xl)
      fontWeight: 700,
      lineHeight: 1.25, // var(--leading-tight)
    },
    h2: {
      fontSize: '1.875rem', // var(--font-size-3xl)
      fontWeight: 700,
      lineHeight: 1.25,
    },
    h3: {
      fontSize: '1.5rem', // var(--font-size-2xl)
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h4: {
      fontSize: '1.25rem', // var(--font-size-xl)
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h5: {
      fontSize: '1.125rem', // var(--font-size-lg)
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h6: {
      fontSize: '1rem', // var(--font-size-base)
      fontWeight: 500,
      lineHeight: 1.25,
    },
    body1: {
      fontSize: '1rem', // var(--font-size-base)
      lineHeight: 1.5, // var(--leading-normal)
    },
    body2: {
      fontSize: '0.875rem', // var(--font-size-sm)
      lineHeight: 1.5,
    },
    caption: {
      fontSize: '0.75rem', // var(--font-size-xs)
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 8, // var(--radius-md) converted to px
  },
  shadows: [
    'none',
    '0 1px 2px 0 rgba(0, 0, 0, 0.05)', // var(--shadow-sm)
    '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)', // var(--shadow-md)
    '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)', // var(--shadow-lg)
    '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)', // var(--shadow-xl)
    // Continue with defaults for higher indices
    ...Array(20).fill('0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)')
  ],
  components: {
    // Set global defaults for TextField: small size and outlined variant
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
        size: 'small',
      },
      styleOverrides: {
        root: {
          // Removed custom height (27px) to avoid overlap - use MUI's small size (~40px) for proper animation space
          // Removed custom input padding - let MUI handle for floating labels
          // Removed custom label transforms - let MUI animate naturally
          '& .MuiInputBase-input': {
            fontSize: '12px', // Keep custom input font size
          },
          '& .MuiInputLabel-root': {
            fontSize: '12px', // Keep custom label font size
          },
          '& .MuiFormHelperText-root': {
            fontSize: '10px', // Keep custom helper text size
          },
        },
      },
    },
    // Dialog title styling (unchanged)
    MuiDialogTitle: {
      styleOverrides: {
        root: {
          '& .MuiTypography-h6': {
            fontSize: '18px',
            fontWeight: 600,
          },
        },
      },
    },
  },
});
// Create query client (unchanged)
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
function MyApp({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const LayoutWrapper = () => {
    const { user, logout } = useAuth();
    const showMegaMenu = !!user && router.pathname !== '/login' && router.pathname !== '/';
    return (
      <Layout user={user} onLogout={logout} showMegaMenu={showMegaMenu}>
        <Component {...pageProps} />
      </Layout>
    );
  };
  return (
    <AuthProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <LayoutWrapper />
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
        </ThemeProvider>
      </QueryClientProvider>
    </AuthProvider>
  );
}
export default MyApp;