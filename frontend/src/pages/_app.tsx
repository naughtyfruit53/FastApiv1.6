import { AppProps } from 'next/app';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Layout from '../components/layout'; // Use lowercase layout
import { useRouter } from 'next/router';
import { AuthProvider, useAuth } from '../context/AuthContext';

// Create theme with enhanced typography for UI requirements
const theme = createTheme({
  palette: {
    primary: {
      main: '#0D47A1',
    },
    secondary: {
      main: '#1976D2',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    // Page titles - 18px
    h4: {
      fontSize: '18px',
      fontWeight: 600,
    },
    // Section/subsection titles - 15px
    h6: {
      fontSize: '15px',
      fontWeight: 500,
    },
    // Modal input labels - 12px
    body2: {
      fontSize: '12px',
    },
  },
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