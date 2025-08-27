/**
 * Test file for Export and Print functionality
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

// Mock file-saver
jest.mock('file-saver', () => ({
  saveAs: jest.fn()
}));

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

describe('Export and Print Functionality', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock default service responses
    mockReportsService.getDashboardStats.mockResolvedValue({
      masters: { vendors: 10, customers: 15, products: 50 }
    });
    
    mockReportsService.getSalesReport.mockResolvedValue({
      vouchers: [
        {
          id: 1,
          voucher_number: 'SV001',
          date: '2024-01-15',
          customer_name: 'Test Customer',
          total_amount: 1000,
          gst_amount: 180,
          status: 'confirmed'
        }
      ],
      summary: {
        total_vouchers: 1,
        total_sales: 1000,
        total_gst: 180
      }
    });

    mockReportsService.getPurchaseReport.mockResolvedValue({
      vouchers: [
        {
          id: 1,
          voucher_number: 'PV001',
          date: '2024-01-15',
          vendor_name: 'Test Vendor',
          total_amount: 2000,
          gst_amount: 360,
          status: 'confirmed'
        }
      ],
      summary: {
        total_vouchers: 1,
        total_purchases: 2000,
        total_gst: 360
      }
    });

    mockReportsService.getInventoryReport.mockResolvedValue({
      items: [
        {
          product_id: 1,
          product_name: 'Test Product',
          quantity: 100,
          unit: 'pcs',
          unit_price: 50,
          total_value: 5000,
          is_low_stock: false
        }
      ],
      summary: {
        total_items: 1,
        total_value: 5000,
        low_stock_items: 0
      }
    });

    mockReportsService.getPendingOrders.mockResolvedValue({
      orders: [
        {
          id: 1,
          type: 'Purchase Order',
          number: 'PO001',
          date: '2024-01-15',
          party: 'Test Vendor',
          amount: 1500,
          status: 'pending'
        }
      ],
      summary: {
        total_orders: 1,
        total_value: 1500
      }
    });

    // Mock export functions
    mockReportsService.exportSalesReportExcel.mockResolvedValue(new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
    mockReportsService.exportPurchaseReportExcel.mockResolvedValue(new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
    mockReportsService.exportInventoryReportExcel.mockResolvedValue(new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
    mockReportsService.exportPendingOrdersExcel.mockResolvedValue(new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
    
    mockCanAccessLedger.mockReturnValue(true);
  });

  describe('Sales Report Export', () => {
    it('should show export button in sales report', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Sales Report tab
      const salesTab = screen.getByText('Sales Report');
      fireEvent.click(salesTab);
      
      await waitFor(() => {
        expect(screen.getByText('Export')).toBeInTheDocument();
      });
    });

    it('should call export function when export button is clicked', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Sales Report tab
      const salesTab = screen.getByText('Sales Report');
      fireEvent.click(salesTab);
      
      await waitFor(() => {
        const exportButton = screen.getByText('Export');
        fireEvent.click(exportButton);
      });

      await waitFor(() => {
        const excelOption = screen.getByText('Export to Excel');
        fireEvent.click(excelOption);
      });

      await waitFor(() => {
        expect(mockReportsService.exportSalesReportExcel).toHaveBeenCalled();
      });
    });
  });

  describe('Purchase Report Export', () => {
    it('should show export button in purchase report', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Purchase Report tab
      const purchaseTab = screen.getByText('Purchase Report');
      fireEvent.click(purchaseTab);
      
      await waitFor(() => {
        expect(screen.getByText('Export')).toBeInTheDocument();
      });
    });

    it('should call export function when export button is clicked', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Purchase Report tab
      const purchaseTab = screen.getByText('Purchase Report');
      fireEvent.click(purchaseTab);
      
      await waitFor(() => {
        const exportButton = screen.getByText('Export');
        fireEvent.click(exportButton);
      });

      await waitFor(() => {
        const excelOption = screen.getByText('Export to Excel');
        fireEvent.click(excelOption);
      });

      await waitFor(() => {
        expect(mockReportsService.exportPurchaseReportExcel).toHaveBeenCalled();
      });
    });
  });

  describe('Inventory Report Export', () => {
    it('should show export button in inventory report', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Inventory Report tab
      const inventoryTab = screen.getByText('Inventory Report');
      fireEvent.click(inventoryTab);
      
      await waitFor(() => {
        expect(screen.getByText('Export')).toBeInTheDocument();
      });
    });

    it('should call export function when export button is clicked', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Inventory Report tab
      const inventoryTab = screen.getByText('Inventory Report');
      fireEvent.click(inventoryTab);
      
      await waitFor(() => {
        const exportButton = screen.getByText('Export');
        fireEvent.click(exportButton);
      });

      await waitFor(() => {
        const excelOption = screen.getByText('Export to Excel');
        fireEvent.click(excelOption);
      });

      await waitFor(() => {
        expect(mockReportsService.exportInventoryReportExcel).toHaveBeenCalled();
      });
    });
  });

  describe('Pending Orders Export', () => {
    it('should show export button in pending orders report', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Pending Orders tab
      const ordersTab = screen.getByText('Pending Orders');
      fireEvent.click(ordersTab);
      
      await waitFor(() => {
        expect(screen.getByText('Export')).toBeInTheDocument();
      });
    });

    it('should call export function when export button is clicked', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Pending Orders tab
      const ordersTab = screen.getByText('Pending Orders');
      fireEvent.click(ordersTab);
      
      await waitFor(() => {
        const exportButton = screen.getByText('Export');
        fireEvent.click(exportButton);
      });

      await waitFor(() => {
        const excelOption = screen.getByText('Export to Excel');
        fireEvent.click(excelOption);
      });

      await waitFor(() => {
        expect(mockReportsService.exportPendingOrdersExcel).toHaveBeenCalled();
      });
    });
  });

  describe('Print Functionality', () => {
    beforeEach(() => {
      // Mock window.print
      Object.defineProperty(window, 'print', {
        value: jest.fn(),
        writable: true
      });
    });

    it('should show print button in all reports', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Check Sales Report
      const salesTab = screen.getByText('Sales Report');
      fireEvent.click(salesTab);
      
      await waitFor(() => {
        expect(screen.getByLabelText('Print report')).toBeInTheDocument();
      });

      // Check Purchase Report
      const purchaseTab = screen.getByText('Purchase Report');
      fireEvent.click(purchaseTab);
      
      await waitFor(() => {
        expect(screen.getByLabelText('Print report')).toBeInTheDocument();
      });

      // Check Inventory Report
      const inventoryTab = screen.getByText('Inventory Report');
      fireEvent.click(inventoryTab);
      
      await waitFor(() => {
        expect(screen.getByLabelText('Print report')).toBeInTheDocument();
      });

      // Check Pending Orders
      const ordersTab = screen.getByText('Pending Orders');
      fireEvent.click(ordersTab);
      
      await waitFor(() => {
        expect(screen.getByLabelText('Print report')).toBeInTheDocument();
      });
    });

    it('should call window.print when print button is clicked', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Sales Report tab
      const salesTab = screen.getByText('Sales Report');
      fireEvent.click(salesTab);
      
      await waitFor(() => {
        const printButton = screen.getByLabelText('Print report');
        fireEvent.click(printButton);
      });

      expect(window.print).toHaveBeenCalled();
    });
  });

  describe('Advanced Filtering', () => {
    it('should show search filters in sales report', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Sales Report tab
      const salesTab = screen.getByText('Sales Report');
      fireEvent.click(salesTab);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search vouchers...')).toBeInTheDocument();
      });
    });

    it('should show search filters in purchase report', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Purchase Report tab
      const purchaseTab = screen.getByText('Purchase Report');
      fireEvent.click(purchaseTab);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search vouchers...')).toBeInTheDocument();
      });
    });

    it('should show search and toggle filters in inventory report', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Inventory Report tab
      const inventoryTab = screen.getByText('Inventory Report');
      fireEvent.click(inventoryTab);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search products...')).toBeInTheDocument();
        expect(screen.getByText('Include Zero Stock')).toBeInTheDocument();
      });
    });

    it('should show order type and search filters in pending orders', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Pending Orders tab
      const ordersTab = screen.getByText('Pending Orders');
      fireEvent.click(ordersTab);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search orders...')).toBeInTheDocument();
        expect(screen.getByText('Order Type')).toBeInTheDocument();
      });
    });

    it('should update search filter when typing', async () => {
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Sales Report tab
      const salesTab = screen.getByText('Sales Report');
      fireEvent.click(salesTab);
      
      await waitFor(() => {
        const searchInput = screen.getByPlaceholderText('Search vouchers...');
        fireEvent.change(searchInput, { target: { value: 'test search' } });
        expect(searchInput).toHaveValue('test search');
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle export errors gracefully', async () => {
      mockReportsService.exportSalesReportExcel.mockRejectedValue(new Error('Export failed'));
      
      render(<ReportsPage />, { wrapper: createWrapper() });
      
      // Switch to Sales Report tab
      const salesTab = screen.getByText('Sales Report');
      fireEvent.click(salesTab);
      
      await waitFor(() => {
        const exportButton = screen.getByText('Export');
        fireEvent.click(exportButton);
      });

      await waitFor(() => {
        const excelOption = screen.getByText('Export to Excel');
        fireEvent.click(excelOption);
      });

      // Should not throw an error and the component should still be functional
      await waitFor(() => {
        expect(screen.getByText('Sales Report')).toBeInTheDocument();
      });
    });
  });
});