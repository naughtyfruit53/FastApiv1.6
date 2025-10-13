// frontend/src/services/masterService.ts

import { apiClient as api } from "./api/client";

export const getVendors = async (context?: QueryFunctionContext): Promise<any> => { // Made context optional to prevent destructuring undefined
  const response = await api.get("/api/v1/vendors", { signal: context?.signal });
  return response.data;
};

// Fetch all customers
export const getCustomers = async (context?: QueryFunctionContext): Promise<any> => { // Made context optional
  const response = await api.get("/api/v1/customers", { signal: context?.signal });
  return response.data;
};

// Fetch all products
export const getProducts = async (context?: QueryFunctionContext): Promise<any> => { // Made context optional
  const response = await api.get("/api/v1/products", { params: { active_only: false, limit: 1000000 }, signal: context?.signal });
  return response.data;
};

// Fetch all employees
export const getEmployees = async (context?: QueryFunctionContext): Promise<any> => { // Made context optional
  const response = await api.get("/api/v1/hr/employees", { signal: context?.signal });
  return response.data;
};

// Search customers for autocomplete/dropdown
export const searchCustomers = async ({
  queryKey,
  signal,
}: QueryFunctionContext): Promise<any> => {
  const [, searchTerm, limit] = queryKey;
  const response = await api.get("/api/v1/customers", {
    params: {
      search: searchTerm,
      limit: limit || 10,
      active_only: false,
    },
    signal,
  });
  return response.data;
};

// Search products for autocomplete/dropdown
export const searchProducts = async ({
  queryKey,
  signal,
}: QueryFunctionContext): Promise<any> => {
  const [, searchTerm, limit] = queryKey;
  const response = await api.get("/api/v1/products", {
    params: {
      search: searchTerm,
      limit: limit || 10,
      active_only: false,
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
}): Promise<any> => {
  const response = await api.post("/api/v1/customers", customerData);
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
}): Promise<any> => {
  const response = await api.post("/api/v1/vendors", vendorData);
  return response.data;
};

// Update vendor
export const updateVendor = async (id: number, vendorData: {
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
}): Promise<any> => {
  const response = await api.put(`/api/v1/vendors/${id}`, vendorData);
  return response.data;
};

// Delete vendor (added to support deletion in vendors.tsx)
export const deleteVendor = async (id: number): Promise<any> => {
  const response = await api.delete(`/api/v1/vendors/${id}`);
  return response.data;
};

// Create new product
export const createProduct = async (productData: {
  product_name: string;
  hsn_code?: string;
  part_number?: string;
  unit: string;
  unit_price: number;
  gst_rate?: number;
  is_gst_inclusive?: boolean;
  reorder_level?: number;
  description?: string;
  is_manufactured?: boolean;
}): Promise<any> => {
  const response = await api.post("/api/v1/products", productData);
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
}): Promise<any> => {
  const response = await api.post("/api/v1/hr/employees", employeeData);
  return response.data;
};

export const bulkImportVendors = async (data: any[]): Promise<any> => {
  const response = await api.post("/api/v1/vendors/bulk", data);
  return response.data;
};

export const bulkImportCustomers = async (data: any[]): Promise<any> => {
  const response = await api.post("/api/v1/customers/bulk", data);
  return response.data;
};

export const bulkImportProducts = async (data: any[]): Promise<any> => {
  const response = await api.post("/api/v1/products/bulk", data);
  return response.data;
};

export const bulkImportStock = async (data: any[]): Promise<any> => {
  const response = await api.post("/api/v1/stock/bulk", data);
  return response.data;
};

// Fetch stock with parameter cleaning to avoid 422 errors
export const getStock = async ({ queryKey, signal }: QueryFunctionContext): Promise<any> => {
  const [, rawParams = {}] = queryKey;
  const params: any = {
    skip: rawParams.skip || 0,
    limit: rawParams.limit || 100,
    low_stock_only: rawParams.low_stock_only || false,
    search: rawParams.search || "",
    show_zero: rawParams.show_zero || false,
  };
  const productId = rawParams.product_id;
  if (productId && !isNaN(Number(productId)) && productId !== "") {
    params.product_id = Number(productId);
  }
  const response = await api.get("/api/v1/stock", { params, signal });
  return response.data;
};

// HSN search for GST rate auto-population - now local from CSV
export const hsnSearch = async ({ queryKey }: QueryFunctionContext): Promise<any> => {
  const [, query, limit] = queryKey;
  try {
    const data = await loadGstData();
    
    // Fuzzy search on HSN code or description
    const results = data
      .filter((item: HsnResult) => 
        fuzzyMatch(query, item.hsn_code) || fuzzyMatch(query, item.description)
      )
      .sort((a: HsnResult, b: HsnResult) => {
        // Prioritize exact HSN matches
        if (a.hsn_code.startsWith(query)) return -1;
        if (b.hsn_code.startsWith(query)) return 1;
        return 0;
      })
      .slice(0, limit || 10);
    
    return results;
  } catch (error) {
    console.error('HSN Search Error:', error);
    return [];
  }
};

// New function: Get next account code for a type
export const getNextAccountCode = async (accountType: string): Promise<string> => {
  const response = await api.get("/api/v1/chart-of-accounts/get-next-code", {
    params: { type: accountType },
  });
  return response.data.next_code;
};