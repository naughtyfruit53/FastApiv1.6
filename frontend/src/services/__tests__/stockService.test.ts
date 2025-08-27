import { getProductStock, getAccountBalance } from '../stockService';
import api from '../../lib/api';

// Mock the api module
jest.mock('../../lib/api', () => ({
  get: jest.fn(),
}));

const mockApi = api as jest.Mocked<typeof api>;

describe('stockService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getProductStock', () => {
    it('fetches stock data for valid product ID', async () => {
      const mockStockData = {
        quantity: 50,
        unit: 'pcs',
        product_id: 1
      };

      mockApi.get.mockResolvedValue({ data: mockStockData });

      const result = await getProductStock({ 
        queryKey: ['productStock', 1], 
        signal: undefined 
      });

      expect(mockApi.get).toHaveBeenCalledWith('/stock/product/1', { signal: undefined });
      expect(result).toEqual(mockStockData);
    });

    it('returns null when product ID is not provided', async () => {
      const result = await getProductStock({ 
        queryKey: ['productStock', null], 
        signal: undefined 
      });

      expect(mockApi.get).not.toHaveBeenCalled();
      expect(result).toBeNull();
    });

    it('returns null on 404 error', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404 }
      });

      const result = await getProductStock({ 
        queryKey: ['productStock', 1], 
        signal: undefined 
      });

      expect(result).toBeNull();
    });

    it('returns null on 403 error (no access)', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 403 }
      });

      const result = await getProductStock({ 
        queryKey: ['productStock', 1], 
        signal: undefined 
      });

      expect(result).toBeNull();
    });

    it('throws error for other HTTP errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 500 }
      });

      await expect(getProductStock({ 
        queryKey: ['productStock', 1], 
        signal: undefined 
      })).rejects.toEqual({
        response: { status: 500 }
      });
    });
  });

  describe('getAccountBalance', () => {
    it('fetches balance data for valid account', async () => {
      const mockBalanceData = {
        outstanding_balances: [
          {
            account_type: 'customer',
            account_id: 1,
            account_name: 'Test Customer',
            outstanding_amount: 5000
          }
        ]
      };

      mockApi.get.mockResolvedValue({ data: mockBalanceData });

      const result = await getAccountBalance({ 
        queryKey: ['accountBalance', 'customer', 1], 
        signal: undefined 
      });

      expect(mockApi.get).toHaveBeenCalledWith('/reports/outstanding-ledger', {
        params: {
          account_type: 'customer',
          account_id: 1
        },
        signal: undefined
      });
      expect(result).toEqual(mockBalanceData.outstanding_balances[0]);
    });

    it('returns null when account type is not provided', async () => {
      const result = await getAccountBalance({ 
        queryKey: ['accountBalance', null, 1], 
        signal: undefined 
      });

      expect(mockApi.get).not.toHaveBeenCalled();
      expect(result).toBeNull();
    });

    it('returns null when account ID is not provided', async () => {
      const result = await getAccountBalance({ 
        queryKey: ['accountBalance', 'customer', null], 
        signal: undefined 
      });

      expect(mockApi.get).not.toHaveBeenCalled();
      expect(result).toBeNull();
    });

    it('returns null when account is not found in response', async () => {
      const mockBalanceData = {
        outstanding_balances: [
          {
            account_type: 'customer',
            account_id: 2, // Different ID
            account_name: 'Other Customer',
            outstanding_amount: 3000
          }
        ]
      };

      mockApi.get.mockResolvedValue({ data: mockBalanceData });

      const result = await getAccountBalance({ 
        queryKey: ['accountBalance', 'customer', 1], 
        signal: undefined 
      });

      expect(result).toBeUndefined();
    });

    it('returns null on 404 error', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 404 }
      });

      const result = await getAccountBalance({ 
        queryKey: ['accountBalance', 'customer', 1], 
        signal: undefined 
      });

      expect(result).toBeNull();
    });

    it('returns null on 403 error (no access)', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 403 }
      });

      const result = await getAccountBalance({ 
        queryKey: ['accountBalance', 'customer', 1], 
        signal: undefined 
      });

      expect(result).toBeNull();
    });

    it('throws error for other HTTP errors', async () => {
      mockApi.get.mockRejectedValue({
        response: { status: 500 }
      });

      await expect(getAccountBalance({ 
        queryKey: ['accountBalance', 'customer', 1], 
        signal: undefined 
      })).rejects.toEqual({
        response: { status: 500 }
      });
    });

    it('handles missing outstanding_balances in response', async () => {
      mockApi.get.mockResolvedValue({ data: {} });

      const result = await getAccountBalance({ 
        queryKey: ['accountBalance', 'customer', 1], 
        signal: undefined 
      });

      expect(result).toBeUndefined();
    });
  });
});