/**
 * Test file for Ledger Report functionality
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ReportsPage from '../reports';
import { reportsService } from '../../services/authService';
import { canAccessLedger } from '../../types/user.types';

// Mock the services
jest.mock('../../services/authService');
jest.mock('../../types/user.types');
jest.mock('../../components/MegaMenu', () => {
  return function MockMegaMenu() {
    return <div data-testid="mega-menu">Mock MegaMenu</div>;
  };
});

const mockReportsService = reportsService as jest.Mocked<typeof reportsService>;
const mockCanAccessLedger = canAccessLedger as jest.MockedFunction<typeof canAccessLedger>;

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });
  
  const TestProvider = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
  
  TestProvider.displayName = 'TestProvider';
  
  return TestProvider;
};

describe('Ledger Report', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock default service responses
    mockReportsService.getDashboardStats.mockResolvedValue({
      masters: { vendors: 10, customers: 15, products: 50 }
    });
    mockReportsService.getCompleteLedger.mockResolvedValue({
      transactions: [
        {
          id: 1,
          voucher_type: 'sales_voucher',
          voucher_number: 'SV001',
          date: '2024-01-15T10:30:00Z',
          account_type: 'customer',
          account_id: 1,
          account_name: 'Test Customer',
          debit_amount: 0,
          credit_amount: 5000,
          balance: 5000,
          status: 'confirmed'
        }
      ],
      summary: { transaction_count: 1 },
      total_debit: 0,
      total_credit: 5000,
      net_balance: 5000,
      filters_applied: {}
    });
    mockReportsService.getOutstandingLedger.mockResolvedValue({
      outstanding_balances: [
        {
          account_type: 'customer',
          account_id: 1,
          account_name: 'Test Customer',
          outstanding_amount: 5000,
          last_transaction_date: '2024-01-15T10:30:00Z',
          transaction_count: 1,
          contact_info: 'test@customer.com'
        },
        {
          account_type: 'vendor',
          account_id: 1,
          account_name: 'Test Vendor',
          outstanding_amount: -3000,
          last_transaction_date: '2024-01-10T09:00:00Z',
          transaction_count: 2,
          contact_info: 'vendor@test.com'
        }
      ],
      summary: { total_accounts: 2 },
      total_payable: -3000,
      total_receivable: 5000,
      net_outstanding: 2000,
      filters_applied: {}
    });
  });

  describe('Ledger Tab Access', () => {
    it('shows ledger tab when user has access', async () => {
      mockCanAccessLedger.mockReturnValue(true);
      
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Check if Ledger tab is present
      expect(screen.getByText('Ledger')).toBeInTheDocument();
    });

    it('shows access denied message when user lacks permission', async () => {
      mockCanAccessLedger.mockReturnValue(false);
      
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      await waitFor(() => {
        expect(screen.getByText(/You don't have permission to access the Ledger report/)).toBeInTheDocument();
      });
    });
  });

  describe('Ledger Type Toggle', () => {
    beforeEach(() => {
      mockCanAccessLedger.mockReturnValue(true);
    });

    it('defaults to Complete Ledger view', async () => {
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      await waitFor(() => {
        expect(screen.getByText('Complete Ledger')).toBeInTheDocument();
      });
    });

    it('toggles to Outstanding Ledger when switch is clicked', async () => {
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      // Find and click the toggle switch
      await waitFor(() => {
        const toggle = screen.getByRole('checkbox');
        fireEvent.click(toggle);
      });
      
      await waitFor(() => {
        expect(screen.getByText('Outstanding Ledger')).toBeInTheDocument();
      });
    });
  });

  describe('Complete Ledger View', () => {
    beforeEach(() => {
      mockCanAccessLedger.mockReturnValue(true);
    });

    it('displays complete ledger data correctly', async () => {
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      await waitFor(() => {
        // Check summary
        expect(screen.getByText('Total Transactions: 1')).toBeInTheDocument();
        expect(screen.getByText('Total Credit: ₹5,000')).toBeInTheDocument();
        expect(screen.getByText('Net Balance: ₹5,000')).toBeInTheDocument();
        
        // Check transaction data
        expect(screen.getByText('SV001')).toBeInTheDocument();
        expect(screen.getByText('Test Customer')).toBeInTheDocument();
        expect(screen.getByText('SALES VOUCHER')).toBeInTheDocument();
      });
    });

    it('applies filters correctly', async () => {
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      await waitFor(() => {
        // Find and change account type filter
        const accountTypeSelect = screen.getByLabelText('Account Type');
        fireEvent.mouseDown(accountTypeSelect);
      });
      
      // Select 'Customers' option
      fireEvent.click(screen.getByText('Customers'));
      
      // Verify the filter was applied
      await waitFor(() => {
        expect(mockReportsService.getCompleteLedger).toHaveBeenCalledWith(
          expect.objectContaining({
            account_type: 'customer'
          })
        );
      });
    });
  });

  describe('Outstanding Ledger View', () => {
    beforeEach(() => {
      mockCanAccessLedger.mockReturnValue(true);
    });

    it('displays outstanding ledger data with proper visual distinction', async () => {
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      // Toggle to outstanding ledger
      await waitFor(() => {
        const toggle = screen.getByRole('checkbox');
        fireEvent.click(toggle);
      });
      
      await waitFor(() => {
        // Check summary
        expect(screen.getByText('Total Accounts: 2')).toBeInTheDocument();
        expect(screen.getByText('Total Payable: ₹3,000 (Amount owed to vendors)')).toBeInTheDocument();
        expect(screen.getByText('Total Receivable: ₹5,000 (Amount owed by customers)')).toBeInTheDocument();
        
        // Check account data
        expect(screen.getByText('Test Customer')).toBeInTheDocument();
        expect(screen.getByText('Test Vendor')).toBeInTheDocument();
        expect(screen.getByText('₹5,000 (Receivable)')).toBeInTheDocument();
        expect(screen.getByText('₹3,000 (Payable)')).toBeInTheDocument();
      });
    });

    it('displays different chips for vendor and customer accounts', async () => {
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      // Toggle to outstanding ledger
      await waitFor(() => {
        const toggle = screen.getByRole('checkbox');
        fireEvent.click(toggle);
      });
      
      await waitFor(() => {
        expect(screen.getByText('CUSTOMER')).toBeInTheDocument();
        expect(screen.getByText('VENDOR')).toBeInTheDocument();
      });
    });
  });

  describe('Filter Functionality', () => {
    beforeEach(() => {
      mockCanAccessLedger.mockReturnValue(true);
    });

    it('updates filters when date range is changed', async () => {
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      await waitFor(() => {
        // Find start date input
        const startDateInput = screen.getByLabelText('Start Date');
        fireEvent.change(startDateInput, { target: { value: '2024-01-01' } });
        
        const endDateInput = screen.getByLabelText('End Date');
        fireEvent.change(endDateInput, { target: { value: '2024-01-31' } });
      });
      
      // Verify the filters were updated
      await waitFor(() => {
        expect(mockReportsService.getCompleteLedger).toHaveBeenCalledWith(
          expect.objectContaining({
            start_date: '2024-01-01',
            end_date: '2024-01-31'
          })
        );
      });
    });

    it('refreshes data when refresh button is clicked', async () => {
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      await waitFor(() => {
        const refreshButton = screen.getByText('Refresh');
        fireEvent.click(refreshButton);
      });
      
      // Verify service was called again
      expect(mockReportsService.getCompleteLedger).toHaveBeenCalledTimes(2);
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      mockCanAccessLedger.mockReturnValue(true);
    });

    it('displays error message when complete ledger fails to load', async () => {
      mockReportsService.getCompleteLedger.mockRejectedValue(new Error('API Error'));
      
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      await waitFor(() => {
        expect(screen.getByText('No complete ledger data available')).toBeInTheDocument();
      });
    });

    it('displays error message when outstanding ledger fails to load', async () => {
      mockReportsService.getOutstandingLedger.mockRejectedValue(new Error('API Error'));
      
      const Wrapper = createWrapper();
      render(<ReportsPage />, { wrapper: Wrapper });
      
      // Click on Ledger tab
      fireEvent.click(screen.getByText('Ledger'));
      
      // Toggle to outstanding ledger
      await waitFor(() => {
        const toggle = screen.getByRole('checkbox');
        fireEvent.click(toggle);
      });
      
      await waitFor(() => {
        expect(screen.getByText('No outstanding ledger data available')).toBeInTheDocument();
      });
    });
  });
});