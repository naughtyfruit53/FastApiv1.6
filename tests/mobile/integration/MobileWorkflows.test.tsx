import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Import mobile components for integration testing
import { MobileDashboardLayout } from '../../../frontend/src/components/mobile';
import MobileBottomSheet from '../../../frontend/src/components/mobile/MobileBottomSheet';
import SwipeableCard from '../../../frontend/src/components/mobile/SwipeableCard';
import MobileContextualMenu from '../../../frontend/src/components/mobile/MobileContextualMenu';

// Mock hooks
jest.mock('../../../frontend/src/hooks/useMobileDetection', () => ({
  useMobileDetection: () => ({ isMobile: true }),
}));

jest.mock('../../../frontend/src/hooks/useAuth', () => ({
  useAuth: () => ({
    user: { id: 1, name: 'Test User', email: 'test@example.com' },
    isAuthenticated: true,
    logout: jest.fn(),
  }),
}));

jest.mock('../../../frontend/src/hooks/useOrganization', () => ({
  useOrganization: () => ({
    currentOrganization: { id: 1, name: 'Test Org' },
    organizations: [{ id: 1, name: 'Test Org' }],
  }),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </BrowserRouter>
  </QueryClientProvider>
);

describe('Mobile Components Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Mobile Dashboard with Actions', () => {
    it('renders dashboard layout with interactive cards', async () => {
      const MockDashboard = () => {
        const [bottomSheetOpen, setBottomSheetOpen] = React.useState(false);
        const [selectedCard, setSelectedCard] = React.useState<string | null>(null);

        const handleArchive = (cardId: string) => {
          console.log('Archive card:', cardId);
          setSelectedCard(cardId);
        };

        const handleDelete = (cardId: string) => {
          console.log('Delete card:', cardId);
          setBottomSheetOpen(true);
          setSelectedCard(cardId);
        };

        return (
          <MobileDashboardLayout title="Integration Test Dashboard">
            <div>
              <SwipeableCard
                leftActions={[
                  {
                    label: 'Archive',
                    action: () => handleArchive('card-1'),
                    color: 'secondary',
                  },
                ]}
                rightActions={[
                  {
                    label: 'Delete',
                    action: () => handleDelete('card-1'),
                    color: 'error',
                  },
                ]}
              >
                <div>Card Content 1</div>
              </SwipeableCard>

              <SwipeableCard
                leftActions={[
                  {
                    label: 'Archive',
                    action: () => handleArchive('card-2'),
                    color: 'secondary',
                  },
                ]}
                rightActions={[
                  {
                    label: 'Delete',
                    action: () => handleDelete('card-2'),
                    color: 'error',
                  },
                ]}
              >
                <div>Card Content 2</div>
              </SwipeableCard>

              <MobileBottomSheet
                open={bottomSheetOpen}
                onClose={() => setBottomSheetOpen(false)}
                title="Confirm Delete"
                height="auto"
                showCloseButton
              >
                <div>
                  <p>Are you sure you want to delete {selectedCard}?</p>
                  <button onClick={() => setBottomSheetOpen(false)}>Cancel</button>
                  <button onClick={() => setBottomSheetOpen(false)}>Confirm</button>
                </div>
              </MobileBottomSheet>
            </div>
          </MobileDashboardLayout>
        );
      };

      render(
        <TestWrapper>
          <MockDashboard />
        </TestWrapper>
      );

      // Check dashboard renders
      expect(screen.getByText('Integration Test Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Card Content 1')).toBeInTheDocument();
      expect(screen.getByText('Card Content 2')).toBeInTheDocument();

      // Check swipe actions are available
      expect(screen.getAllByText('Archive')).toHaveLength(2);
      expect(screen.getAllByText('Delete')).toHaveLength(2);

      // Test delete action opens bottom sheet
      fireEvent.click(screen.getAllByText('Delete')[0]);
      
      await waitFor(() => {
        expect(screen.getByText('Confirm Delete')).toBeInTheDocument();
        expect(screen.getByText('Are you sure you want to delete card-1?')).toBeInTheDocument();
      });

      // Test bottom sheet close
      fireEvent.click(screen.getByText('Cancel'));
      
      await waitFor(() => {
        expect(screen.queryByText('Confirm Delete')).not.toBeInTheDocument();
      });
    });
  });

  describe('Contextual Menu Integration', () => {
    it('integrates contextual menu with cards and bottom sheet', async () => {
      const MockCardWithMenu = () => {
        const [bottomSheetOpen, setBottomSheetOpen] = React.useState(false);
        const [action, setAction] = React.useState<string>('');

        const contextActions = [
          {
            label: 'Edit',
            onClick: () => {
              setAction('edit');
              setBottomSheetOpen(true);
            },
          },
          {
            label: 'Share',
            onClick: () => {
              setAction('share');
              setBottomSheetOpen(true);
            },
          },
          {
            label: 'Delete',
            onClick: () => {
              setAction('delete');
              setBottomSheetOpen(true);
            },
            destructive: true,
            divider: true,
          },
        ];

        return (
          <div>
            <MobileContextualMenu actions={contextActions}>
              <SwipeableCard>
                <div>Long press or right-click this card</div>
              </SwipeableCard>
            </MobileContextualMenu>

            <MobileBottomSheet
              open={bottomSheetOpen}
              onClose={() => setBottomSheetOpen(false)}
              title={`${action.charAt(0).toUpperCase() + action.slice(1)} Action`}
              height="auto"
            >
              <div>
                <p>You selected: {action}</p>
                <button onClick={() => setBottomSheetOpen(false)}>Close</button>
              </div>
            </MobileBottomSheet>
          </div>
        );
      };

      render(
        <TestWrapper>
          <MockCardWithMenu />
        </TestWrapper>
      );

      const card = screen.getByText('Long press or right-click this card');
      expect(card).toBeInTheDocument();

      // Test context menu (simulate right-click on desktop)
      fireEvent.contextMenu(card);

      await waitFor(() => {
        expect(screen.getByText('Edit')).toBeInTheDocument();
        expect(screen.getByText('Share')).toBeInTheDocument();
        expect(screen.getByText('Delete')).toBeInTheDocument();
      });

      // Test menu action
      fireEvent.click(screen.getByText('Edit'));

      await waitFor(() => {
        expect(screen.getByText('Edit Action')).toBeInTheDocument();
        expect(screen.getByText('You selected: edit')).toBeInTheDocument();
      });

      // Close bottom sheet
      fireEvent.click(screen.getByText('Close'));

      await waitFor(() => {
        expect(screen.queryByText('Edit Action')).not.toBeInTheDocument();
      });
    });
  });

  describe('Navigation Integration', () => {
    it('integrates mobile navigation with dashboard layout', () => {
      render(
        <TestWrapper>
          <MobileDashboardLayout 
            title="Navigation Test"
            showBack={true}
            onBack={() => console.log('Back pressed')}
          >
            <div>Dashboard content with navigation</div>
          </MobileDashboardLayout>
        </TestWrapper>
      );

      expect(screen.getByText('Navigation Test')).toBeInTheDocument();
      expect(screen.getByText('Dashboard content with navigation')).toBeInTheDocument();
    });
  });

  describe('Error Handling Integration', () => {
    it('handles errors gracefully across components', () => {
      const ErrorTestComponent = () => {
        const [hasError, setHasError] = React.useState(false);

        if (hasError) {
          throw new Error('Test error');
        }

        return (
          <MobileDashboardLayout title="Error Test">
            <SwipeableCard
              rightActions={[
                {
                  label: 'Trigger Error',
                  action: () => setHasError(true),
                  color: 'error',
                },
              ]}
            >
              <div>Click delete to trigger error</div>
            </SwipeableCard>
          </MobileDashboardLayout>
        );
      };

      // Wrap with error boundary for testing
      const ErrorBoundary = ({ children }: { children: React.ReactNode }) => {
        const [hasError, setHasError] = React.useState(false);

        React.useEffect(() => {
          const handleError = () => setHasError(true);
          window.addEventListener('error', handleError);
          return () => window.removeEventListener('error', handleError);
        }, []);

        if (hasError) {
          return <div>Something went wrong</div>;
        }

        return <>{children}</>;
      };

      render(
        <TestWrapper>
          <ErrorBoundary>
            <ErrorTestComponent />
          </ErrorBoundary>
        </TestWrapper>
      );

      expect(screen.getByText('Error Test')).toBeInTheDocument();
      expect(screen.getByText('Click delete to trigger error')).toBeInTheDocument();
    });
  });
});