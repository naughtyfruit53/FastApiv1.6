import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import StockDisplay from '../StockDisplay';
import { getProductStock } from '../../services/stockService';

// Mock the stock service
jest.mock('../../services/stockService', () => ({
  getProductStock: jest.fn(),
}));

const mockGetProductStock = getProductStock as jest.MockedFunction<typeof getProductStock>;

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

describe('StockDisplay', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders nothing when productId is null', () => {
    const { container } = render(
      <StockDisplay productId={null} />,
      { wrapper: createWrapper() }
    );
    
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when disabled', () => {
    const { container } = render(
      <StockDisplay productId={1} disabled={true} />,
      { wrapper: createWrapper() }
    );
    
    expect(container.firstChild).toBeNull();
  });

  it('displays stock information when product is selected', async () => {
    mockGetProductStock.mockResolvedValue({
      quantity: 100,
      unit: 'pcs'
    });

    render(
      <StockDisplay productId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Current Stock: 100 pcs')).toBeInTheDocument();
    });
  });

  it('handles zero stock quantity', async () => {
    mockGetProductStock.mockResolvedValue({
      quantity: 0,
      unit: 'kg'
    });

    render(
      <StockDisplay productId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Current Stock: 0 kg')).toBeInTheDocument();
    });
  });

  it('handles missing unit', async () => {
    mockGetProductStock.mockResolvedValue({
      quantity: 50,
      unit: null
    });

    render(
      <StockDisplay productId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(screen.getByText('Current Stock: 50')).toBeInTheDocument();
    });
  });

  it('renders nothing when stock data is null', async () => {
    mockGetProductStock.mockResolvedValue(null);

    const { container } = render(
      <StockDisplay productId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it('renders nothing when API call fails', async () => {
    mockGetProductStock.mockRejectedValue(new Error('API Error'));

    const { container } = render(
      <StockDisplay productId={1} />,
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });
});