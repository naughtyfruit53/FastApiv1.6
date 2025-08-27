/**
 * Test file for AuthProvider race condition fix
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AuthProvider, useAuth } from '../AuthContext';
import { authService } from '../../services/authService';

// Mock dependencies
jest.mock('../../services/authService');
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    pathname: '/dashboard'
  })
}));
jest.mock('../../lib/api', () => ({
  markAuthReady: jest.fn(),
  resetAuthReady: jest.fn()
}));
jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn()
  }
}));

const mockedAuthService = authService as jest.Mocked<typeof authService>;

// Test component to access auth context
const TestComponent = () => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div data-testid="loading">Loading...</div>;
  }
  
  if (user) {
    return <div data-testid="user-info">{user.email}</div>;
  }
  
  return <div data-testid="no-user">No user</div>;
};

describe('AuthProvider Race Condition Fix', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });
  });

  it('should show loading spinner while fetching user data', async () => {
    // Mock localStorage to have a token
    (window.localStorage.getItem as jest.Mock).mockReturnValue('fake-token');
    
    // Mock authService to return user data after a delay
    mockedAuthService.getCurrentUser.mockImplementation(
      () => new Promise(resolve => {
        setTimeout(() => resolve({
          id: 1,
          email: 'test@example.com',
          role: 'user',
          is_super_admin: false,
          organization_id: 1,
          must_change_password: false
        }), 100);
      })
    );

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Should show loading initially
    expect(screen.getByTestId('loading')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();

    // Should show user info after loading completes
    await waitFor(() => {
      expect(screen.getByTestId('user-info')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    }, { timeout: 2000 });

    // Loading should be gone
    expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
  });

  it('should show proper loading state when no token is present', async () => {
    // Mock localStorage to have no token
    (window.localStorage.getItem as jest.Mock).mockReturnValue(null);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Should show loading initially
    expect(screen.getByTestId('loading')).toBeInTheDocument();

    // Should show no user after loading completes
    await waitFor(() => {
      expect(screen.getByTestId('no-user')).toBeInTheDocument();
    });

    // Loading should be gone
    expect(screen.queryByTestId('loading')).not.toBeInTheDocument();
  });

  it('should handle auth service errors gracefully', async () => {
    // Mock localStorage to have a token
    (window.localStorage.getItem as jest.Mock).mockReturnValue('fake-token');
    
    // Mock authService to throw an error
    mockedAuthService.getCurrentUser.mockRejectedValue(new Error('Auth failed'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Should show loading initially
    expect(screen.getByTestId('loading')).toBeInTheDocument();

    // Should handle error and show no user
    await waitFor(() => {
      expect(screen.getByTestId('no-user')).toBeInTheDocument();
    }, { timeout: 2000 });

    // Token should be removed from localStorage on error
    expect(window.localStorage.removeItem).toHaveBeenCalledWith('token');
  });

  it('should show loading fallback UI with proper styling', () => {
    // Mock localStorage to have a token
    (window.localStorage.getItem as jest.Mock).mockReturnValue('fake-token');
    
    // Mock authService to never resolve (simulate loading state)
    mockedAuthService.getCurrentUser.mockImplementation(() => new Promise(() => {}));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Check that the loading UI elements are present
    expect(screen.getByText('Loading authentication...')).toBeInTheDocument();
    expect(screen.getByText('Establishing secure session...')).toBeInTheDocument();
    
    // Check for the spinner element (should have the auth-spinner class)
    const spinner = document.querySelector('.auth-spinner');
    expect(spinner).toBeInTheDocument();
  });

  it('should not render children until loading is complete', async () => {
    // Mock localStorage to have a token
    (window.localStorage.getItem as jest.Mock).mockReturnValue('fake-token');
    
    let resolveAuthService: (value: any) => void;
    const authPromise = new Promise(resolve => {
      resolveAuthService = resolve;
    });
    
    mockedAuthService.getCurrentUser.mockReturnValue(authPromise);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Children should not be rendered while loading
    expect(screen.queryByTestId('user-info')).not.toBeInTheDocument();
    expect(screen.queryByTestId('no-user')).not.toBeInTheDocument();
    expect(screen.getByTestId('loading')).toBeInTheDocument();

    // Resolve the auth service
    act(() => {
      resolveAuthService!({
        id: 1,
        email: 'test@example.com',
        role: 'user',
        is_super_admin: false,
        organization_id: 1,
        must_change_password: false
      });
    });

    // Now children should render
    await waitFor(() => {
      expect(screen.getByTestId('user-info')).toBeInTheDocument();
    });
  });

  it('should not make duplicate getCurrentUser calls during login', async () => {
    // Mock localStorage to have no token initially
    (window.localStorage.getItem as jest.Mock).mockReturnValue(null);
    (window.localStorage.setItem as jest.Mock).mockImplementation(() => {});
    
    // Mock login response with user data
    const loginResponse = {
      access_token: 'new-token',
      user: {
        id: 1,
        email: 'test@example.com',
        role: 'user',
        is_super_admin: false
      },
      organization_id: 1,
      must_change_password: false,
      user_role: 'user'
    };

    let authProviderInstance: any;
    
    // Create a custom component that can access the login method
    const LoginTestComponent = () => {
      const auth = useAuth();
      authProviderInstance = auth;
      
      return (
        <div>
          <div data-testid="user-email">{auth.user?.email || 'no-user'}</div>
          <div data-testid="loading">{auth.loading.toString()}</div>
        </div>
      );
    };

    render(
      <AuthProvider>
        <LoginTestComponent />
      </AuthProvider>
    );

    // Wait for initial render to complete (no token, so should not be loading)
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    // Now call login method
    await act(async () => {
      await authProviderInstance.login(loginResponse);
    });

    // Verify getCurrentUser was never called during login
    expect(mockedAuthService.getCurrentUser).not.toHaveBeenCalled();
    
    // Verify user state was set from login response
    expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    
    // Verify token was stored
    expect(window.localStorage.setItem).toHaveBeenCalledWith('token', 'new-token');
  });
});