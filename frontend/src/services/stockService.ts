// frontend/src/services/stockService.ts
// services/stockService.ts
// Service for fetching stock and balance information for voucher forms
import api from "../lib/api";
interface QueryFunctionContext {
  queryKey: any[];
  signal?: AbortSignal;
}
// Fetch stock quantity for a specific product
export const getProductStock = async ({
  queryKey,
  signal,
}: QueryFunctionContext): Promise<any> => {
  const [, productId] = queryKey; // Expect queryKey = ['productStock', productId]
  if (!productId) {
    return null;
  }
  try {
    const response = await api.get(`/stock/product/${productId}`, { signal });
    return response.data;
  } catch (error: any) {
    // Return null if no stock data found or access denied (instead of throwing)
    if (error.response?.status === 404 || error.response?.status === 403) {
      return null;
    }
    throw error;
  }
};
// Fetch outstanding balance for a specific customer or vendor
export const getAccountBalance = async ({
  queryKey,
  signal,
}: QueryFunctionContext): Promise<any> => {
  const [, accountType, accountId] = queryKey; // Expect queryKey = ['accountBalance', accountType, accountId]
  if (!accountType || !accountId) {
    return null;
  }
  try {
    const response = await api.get("/reports/outstanding-ledger", {
      params: {
        account_type: accountType,
        account_id: accountId,
      },
      signal,
    });
    // Find the specific account in the response
    const balances = response.data?.outstanding_balances || [];
    const accountBalance = balances.find(
      (balance: any) =>
        balance.account_type === accountType &&
        balance.account_id === accountId,
    );
    return accountBalance;
  } catch (error: any) {
    // Return null if no balance data found or access denied (instead of throwing)
    if (error.response?.status === 404 || error.response?.status === 403) {
      return null;
    }
    throw error;
  }
};
// Fetch stock movements
export const getStockMovements = async ({
  queryKey,
  signal,
}: QueryFunctionContext): Promise<any> => {
  const [, params] = queryKey; // Expect queryKey = ['stockMovements', { search, recent }]
  const response = await api.get("/stock/movements", {
    params,
    signal,
  });
  return response.data;
};
// Fetch low stock report
export const getLowStockReport = async ({
  signal,
}: QueryFunctionContext): Promise<any> => {
  const response = await api.get("/stock/low-stock", { signal });
  return response.data;
};
// Fetch movements for specific product
export const getProductMovements = async (productId: number): Promise<any> => {
  const response = await api.get("/stock/movements", {
    params: { product_id: productId },
  });
  return response.data;
};
// Fetch last vendor for product
export const getLastVendorForProduct = async (
  productId: number,
): Promise<any> => {
  try {
    const response = await api.get(`/stock/product/${productId}/last-vendor`);
    return response.data;
  } catch (_error) {
    return null;
  }
};
