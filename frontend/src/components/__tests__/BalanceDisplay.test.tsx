import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import BalanceDisplay from '../BalanceDisplay';
import { getAccountBalance } from '../../services/stockService';

// Mock the stock service
jest.mock('../../services/stockService', () => ({
  getAccountBalance: jest.fn(),
}));

const mockGetAccountBalance = getAccountBalance as jest.MockedFunction<typeof getAccountBalance>;

// Helper to wrap component with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  
  const TestProvider = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
  
  TestProvider.displayName = 'TestProvider';
  
  return TestProvider;
};

describe('BalanceDisplay', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders nothing when accountType is null', () => {
    const { container } = render(
      <BalanceDisplay accountType={null} accountId={1} />,
      { wrapper: createWrapper() }
    );
    
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when accountId is null', () => {
    const { container } = render(
      <BalanceDisplay accountType="customer" accountId={null} />,
      { wrapper: createWrapper() }
    );
    
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when disabled', () => {
    const { container } = render(
      <BalanceDisplay accountType="customer" accountId={1} disabled={true} />,
      { wrapper: createWrapper() }
    );
    
    expect(container.firstChild).toBeNull();
  });

  it('displays customer balance - positive amount (receivable)', async () => {
    mockGetAccountBalance.mockResolvedValue({
      outstanding_amount: 5000,
      account_name: 'ABC Corp',
      account_type: 'customer'
    });

    render(
      <BalanceDisplay accountType="customer" accountId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Current Balance: ₹5,000 receivable')).toBeInTheDocument();
    });
  });

  it('displays customer balance - negative amount (advance)', async () => {
    mockGetAccountBalance.mockResolvedValue({
      outstanding_amount: -2000,
      account_name: 'XYZ Ltd',
      account_type: 'customer'
    });

    render(
      <BalanceDisplay accountType="customer" accountId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Current Balance: ₹2,000 advance')).toBeInTheDocument();
    });
  });

  it('displays vendor balance - negative amount (payable)', async () => {
    mockGetAccountBalance.mockResolvedValue({
      outstanding_amount: -3000,
      account_name: 'Supplier Co',
      account_type: 'vendor'
    });

    render(
      <BalanceDisplay accountType="vendor" accountId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Current Balance: ₹3,000 payable')).toBeInTheDocument();
    });
  });

  it('displays vendor balance - positive amount (advance)', async () => {
    mockGetAccountBalance.mockResolvedValue({
      outstanding_amount: 1500,
      account_name: 'Parts Supplier',
      account_type: 'vendor'
    });

    render(
      <BalanceDisplay accountType="vendor" accountId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Current Balance: ₹1,500 advance')).toBeInTheDocument();
    });
  });

  it('handles zero balance', async () => {
    mockGetAccountBalance.mockResolvedValue({
      outstanding_amount: 0,
      account_name: 'Zero Balance Corp',
      account_type: 'customer'
    });

    render(
      <BalanceDisplay accountType="customer" accountId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Current Balance: ₹0 advance')).toBeInTheDocument();
    });
  });

  it('renders nothing when balance data is null', async () => {
    mockGetAccountBalance.mockResolvedValue(null);

    const { container } = render(
      <BalanceDisplay accountType="customer" accountId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it('renders nothing when API call fails', async () => {
    mockGetAccountBalance.mockRejectedValue(new Error('API Error'));

    const { container } = render(
      <BalanceDisplay accountType="customer" accountId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it('formats large amounts with comma separation', async () => {
    mockGetAccountBalance.mockResolvedValue({
      outstanding_amount: 123456.78,
      account_name: 'Big Customer',
      account_type: 'customer'
    });

    render(
      <BalanceDisplay accountType="customer" accountId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Current Balance: ₹123,456.78 receivable')).toBeInTheDocument();
    });
  });
});