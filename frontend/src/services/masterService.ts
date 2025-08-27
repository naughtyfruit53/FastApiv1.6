// src/services/masterService.ts
// masterService.ts - Service to fetch master data like vendors, customers, products

import api from '../lib/api';  // Import the axios instance for consistency with authService and automatic token handling

// Note: Functions are defined to accept React Query's QueryFunctionContext for proper integration.
// This allows using signal for cancellation and prevents accidental passing of context as query params.
// Each function ignores unnecessary context parts and uses only what is needed (e.g., signal).

interface QueryFunctionContext {
  queryKey: any[];
  signal?: AbortSignal;
}

// Fetch all vendors
export const getVendors = async ({ signal }: QueryFunctionContext) => {
  const response = await api.get('/vendors', { signal });
  return response.data;
};

// Fetch all customers
export const getCustomers = async ({ signal }: QueryFunctionContext) => {
  const response = await api.get('/customers', { signal });
  return response.data;
};

// Fetch all products
export const getProducts = async ({ signal }: QueryFunctionContext) => {
  const response = await api.get('/products', { signal });
  return response.data;
};

// Fetch all employees
export const getEmployees = async ({ signal }: QueryFunctionContext) => {
  const response = await api.get('/employees', { signal });
  return response.data;
};

// Search customers for autocomplete/dropdown
export const searchCustomers = async ({ queryKey, signal }: QueryFunctionContext) => {
  const [, searchTerm, limit] = queryKey;  // Expect queryKey = ['searchCustomers', searchTerm, limit]
  const response = await api.get('/customers', {
    params: {
      search: searchTerm,
      limit: limit || 10,
      active_only: true,
    },
    signal,
  });
  return response.data;
};

// Search products for autocomplete/dropdown
export const searchProducts = async ({ queryKey, signal }: QueryFunctionContext) => {
  const [, searchTerm, limit] = queryKey;  // Expect queryKey = ['searchProducts', searchTerm, limit]
  const response = await api.get('/products', {
    params: {
      search: searchTerm,
      limit: limit || 10,
      active_only: true,
    },
    signal,
  });
  return response.data;
};

// Create new customer
export const createCustomer = async (customerData: {
  name: string;
  contact_number: string;
  email?: string;
  address1: string;
  address2?: string;
  city: string;
  state: string;
  pin_code: string;
  state_code: string;
  gst_number?: string;
  pan_number?: string;
}) => {
  const response = await api.post('/customers', customerData);
  return response.data;
};

// Create new vendor
export const createVendor = async (vendorData: {
  name: string;
  contact_number: string;
  email?: string;
  address1: string;
  address2?: string;
  city: string;
  state: string;
  pin_code: string;
  state_code: string;
  gst_number?: string;
  pan_number?: string;
}) => {
  const response = await api.post('/vendors', vendorData);
  return response.data;
};

// Create new product
export const createProduct = async (productData: {
  name: string;
  hsn_code?: string;
  part_number?: string;
  unit: string;
  unit_price: number;
  gst_rate?: number;
  is_gst_inclusive?: boolean;
  reorder_level?: number;
  description?: string;
  is_manufactured?: boolean;
}) => {
  const response = await api.post('/products', productData);
  return response.data;
};

// Create new employee
export const createEmployee = async (employeeData: {
  name: string;
  employee_id?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
  department?: string;
  designation?: string;
  salary?: number;
}) => {
  const response = await api.post('/employees', employeeData);
  return response.data;
};

export const bulkImportVendors = async (data: any[]) => {
  const response = await api.post('/vendors/bulk', data);
  return response.data;
};

export const bulkImportCustomers = async (data: any[]) => {
  const response = await api.post('/customers/bulk', data);
  return response.data;
};

export const bulkImportProducts = async (data: any[]) => {
  const response = await api.post('/products/bulk', data);
  return response.data;
};

export const bulkImportStock = async (data: any[]) => {
  const response = await api.post('/stock/bulk', data);
  return response.data;
};

// Fetch stock with parameter cleaning to avoid 422 errors
export const getStock = async ({ queryKey, signal }: QueryFunctionContext) => {
  const [, rawParams = {}] = queryKey;  // Expect queryKey = ['stock', { skip: 0, limit: 100, product_id: ..., low_stock_only: ..., search: ..., show_zero: ... }]

  // Clean parameters to exclude invalid or empty values that cause validation errors
  const params: any = {
    skip: rawParams.skip || 0,
    limit: rawParams.limit || 100,
    low_stock_only: rawParams.low_stock_only || false,
    search: rawParams.search || '',
    show_zero: rawParams.show_zero || false,
  };

  // Include product_id only if it's a valid number (not empty string or NaN)
  const productId = rawParams.product_id;
  if (productId && !isNaN(Number(productId)) && productId !== '') {
    params.product_id = Number(productId);
  }

  const response = await api.get('/stock', { params, signal });
  return response.data;
};