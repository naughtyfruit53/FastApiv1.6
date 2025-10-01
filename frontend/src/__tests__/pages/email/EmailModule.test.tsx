/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import EmailModule from '../../../pages/email/index';
import { emailService } from '../../../services/emailService';
import { useOAuth } from '../../../hooks/useOAuth';
import { useEmail } from '../../../context/EmailContext';

// Mock the services and hooks
jest.mock('../../../services/emailService');
jest.mock('../../../hooks/useOAuth');
jest.mock('../../../context/EmailContext');
jest.mock('../../../context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 1, email: 'test@example.com' }
  })
}));

// Mock child components
jest.mock('../../../pages/email/Inbox', () => {
  return function MockInbox({ onAccountSelect, onCompose }: any) {
    return (
      <div data-testid="inbox-component">
        <button onClick={() => onAccountSelect && onAccountSelect(1)}>Select Account 1</button>
        <button onClick={() => onCompose && onCompose()}>Compose</button>
      </div>
    );
  };
});

jest.mock('../../../pages/email/ThreadView', () => {
  return function MockThreadView() {
    return <div data-testid="thread-view-component">Thread View</div>;
  };
});

jest.mock('../../../pages/email/Composer', () => {
  return function MockComposer() {
    return <div data-testid="composer-component">Composer</div>;
  };
});

jest.mock('../../../components/email/EmailSelector', () => {
  return function MockEmailSelector({ onSelect }: any) {
    return (
      <div data-testid="email-selector">
        <button onClick={() => onSelect(1)}>Select Token 1</button>
      </div>
    );
  };
});

jest.mock('../../../components/OAuthLoginButton', () => {
  return function MockOAuthLoginButton() {
    return <div data-testid="oauth-login-button">OAuth Login Button</div>;
  };
});

const mockEmailService = emailService as jest.Mocked<typeof emailService>;
const mockUseOAuth = useOAuth as jest.MockedFunction<typeof useOAuth>;
const mockUseEmail = useEmail as jest.MockedFunction<typeof useEmail>;

const theme = createTheme();

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        {component}
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('EmailModule Component', () => {
  const mockToken = {
    id: 1,
    user_id: 1,
    organization_id: 1,
    provider: 'gmail',
    email_address: 'test@example.com',
    display_name: 'Test User',
    token_type: 'Bearer',
    expires_at: null,
    status: 'active',
    sync_enabled: true,
    sync_folders: ['INBOX'],
    last_sync_at: null,
    last_sync_status: null,
    last_sync_error: null,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    last_used_at: null,
    refresh_count: 0,
    has_access_token: true,
    has_refresh_token: true,
    is_expired: false,
    is_active: true
  };

  const mockAccount = {
    id: 1,
    name: 'Test Account',
    email_address: 'test@example.com',
    display_name: 'Test User',
    account_type: 'gmail_api' as const,
    oauth_token_id: 1,
    sync_enabled: true,
    sync_frequency_minutes: 15,
    is_active: true,
    sync_status: 'active',
    total_messages_synced: 100,
    organization_id: 1,
    user_id: 1,
    created_at: '2023-01-01T00:00:00Z'
  };

  const mockSetSelectedToken = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default mock implementations
    mockUseOAuth.mockReturnValue({
      getUserTokens: jest.fn().mockResolvedValue([mockToken]),
      getTokenDetails: jest.fn(),
      initiateOAuthLogin: jest.fn(),
      completeOAuthLogin: jest.fn(),
      revokeToken: jest.fn(),
      refreshToken: jest.fn(),
      getProviders: jest.fn(),
      syncEmails: jest.fn(),
      loading: false,
      error: null
    });

    mockUseEmail.mockReturnValue({
      selectedToken: 1,
      setSelectedToken: mockSetSelectedToken
    });

    mockEmailService.getMailAccounts.mockResolvedValue([mockAccount]);
  });

  it('renders inbox view when account is selected', async () => {
    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByTestId('inbox-component')).toBeInTheDocument();
    });
  });

  it('shows OAuth login button when no tokens exist', async () => {
    mockUseOAuth.mockReturnValue({
      getUserTokens: jest.fn().mockResolvedValue([]),
      getTokenDetails: jest.fn(),
      initiateOAuthLogin: jest.fn(),
      completeOAuthLogin: jest.fn(),
      revokeToken: jest.fn(),
      refreshToken: jest.fn(),
      getProviders: jest.fn(),
      syncEmails: jest.fn(),
      loading: false,
      error: null
    });

    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByText('No Email Accounts Connected')).toBeInTheDocument();
      expect(screen.getByTestId('oauth-login-button')).toBeInTheDocument();
    });
  });

  it('shows account selector when no account is selected', async () => {
    mockUseEmail.mockReturnValue({
      selectedToken: null,
      setSelectedToken: mockSetSelectedToken
    });

    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByText('Select Email Account')).toBeInTheDocument();
      expect(screen.getByTestId('email-selector')).toBeInTheDocument();
    });
  });

  it('handles account selection from inbox', async () => {
    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByTestId('inbox-component')).toBeInTheDocument();
    });

    const selectAccountButton = screen.getByText('Select Account 1');
    fireEvent.click(selectAccountButton);

    expect(mockSetSelectedToken).toHaveBeenCalledWith(1);
  });

  it('navigates to settings view when settings icon is clicked', async () => {
    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByTestId('inbox-component')).toBeInTheDocument();
    });

    // Find and click the settings icon
    const settingsButton = screen.getByRole('button', { name: /settings/i });
    fireEvent.click(settingsButton);

    await waitFor(() => {
      expect(screen.getByText('Email Settings')).toBeInTheDocument();
    });
  });

  it('navigates to composer when compose button is clicked', async () => {
    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByTestId('inbox-component')).toBeInTheDocument();
    });

    const composeButton = screen.getByText('Compose');
    fireEvent.click(composeButton);

    await waitFor(() => {
      expect(screen.getByTestId('composer-component')).toBeInTheDocument();
    });
  });

  it('shows settings view with back button', async () => {
    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByTestId('inbox-component')).toBeInTheDocument();
    });

    const settingsButton = screen.getByRole('button', { name: /settings/i });
    fireEvent.click(settingsButton);

    await waitFor(() => {
      expect(screen.getByText('Email Settings')).toBeInTheDocument();
      expect(screen.getByText('Back to Inbox')).toBeInTheDocument();
    });
  });

  it('returns to inbox from settings view', async () => {
    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByTestId('inbox-component')).toBeInTheDocument();
    });

    // Navigate to settings
    const settingsButton = screen.getByRole('button', { name: /settings/i });
    fireEvent.click(settingsButton);

    await waitFor(() => {
      expect(screen.getByText('Email Settings')).toBeInTheDocument();
    });

    // Navigate back to inbox
    const backButton = screen.getByText('Back to Inbox');
    fireEvent.click(backButton);

    await waitFor(() => {
      expect(screen.getByTestId('inbox-component')).toBeInTheDocument();
    });
  });

  it('displays account name in toolbar', async () => {
    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByText(/Email - Test User/)).toBeInTheDocument();
    });
  });

  it('opens drawer when menu button is clicked', async () => {
    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByTestId('inbox-component')).toBeInTheDocument();
    });

    const menuButton = screen.getByRole('button', { name: /menu/i });
    fireEvent.click(menuButton);

    await waitFor(() => {
      expect(screen.getByText('Accounts')).toBeInTheDocument();
    });
  });

  it('handles loading state', () => {
    mockUseOAuth.mockReturnValue({
      getUserTokens: jest.fn().mockResolvedValue([mockToken]),
      getTokenDetails: jest.fn(),
      initiateOAuthLogin: jest.fn(),
      completeOAuthLogin: jest.fn(),
      revokeToken: jest.fn(),
      refreshToken: jest.fn(),
      getProviders: jest.fn(),
      syncEmails: jest.fn(),
      loading: true,
      error: null
    });

    renderWithProviders(<EmailModule />);

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('handles error state', async () => {
    mockUseOAuth.mockReturnValue({
      getUserTokens: jest.fn().mockRejectedValue(new Error('API Error')),
      getTokenDetails: jest.fn(),
      initiateOAuthLogin: jest.fn(),
      completeOAuthLogin: jest.fn(),
      revokeToken: jest.fn(),
      refreshToken: jest.fn(),
      getProviders: jest.fn(),
      syncEmails: jest.fn(),
      loading: false,
      error: 'API Error'
    });

    renderWithProviders(<EmailModule />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load email accounts/)).toBeInTheDocument();
    });
  });
});
