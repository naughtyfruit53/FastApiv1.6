// frontend/src/services/masterService.ts
import { apiClient as api } from "./api/client";
import { QueryFunctionContext } from "@tanstack/react-query";

// Interface for stock response
interface StockResponse {
  id: number;
  organization_id: number;
  product_id: number;
  quantity: number;
  unit: string;
  location: string;
  last_updated: string;
  product_name: string;
  product_hsn_code?: string;
  product_part_number?: string;
  unit_price: number;
  reorder_level: number;
  gst_rate: number;
  is_active: boolean;
  total_value: number;
}

// Fetch all vendors
export const getVendors = async (context?: QueryFunctionContext): Promise<any> => {
  const params = context?.queryKey?.[3] ? { organization_id: context.queryKey[3] } : {};
  console.log("[getVendors] Request params:", params);
  const response = await api.get("/vendors", { params, signal: context?.signal });  # CHANGED: Removed extra /api/v1 (uses getApiUrl which has /api/v1)
  console.log("[getVendors] Response data:", response.data);
  return response.data;
};

// Search vendors for autocomplete/dropdown
export const searchVendors = async ({
  queryKey,
  signal,
}: QueryFunctionContext): Promise<any> => {
  const [, searchTerm, limit, organization_id] = queryKey;
  const params: any = {
    search: searchTerm || "",
    limit: limit || 1000000,
    active_only: false,
  };
  if (organization_id) {
    params.organization_id = organization_id;
  }
  console.log("[searchVendors] Request params:", params);
  try {
    const response = await api.get("/vendors", { params, signal });  # CHANGED: Removed extra /api/v1
    console.log("[searchVendors] Response data:", response.data);
    return response.data;
  } catch (error) {
    console.error("[searchVendors] Error:", error);
    throw error;
  }
};

// Fetch all customers
export const getCustomers = async (context?: QueryFunctionContext): Promise<any> => {
  const response = await api.get("/customers", { signal: context?.signal });  # CHANGED: Removed extra /api/v1
  console.log("[getCustomers] Response data:", response.data);
  return response.data;
};

// Fetch all products
export const getProducts = async (context?: QueryFunctionContext): Promise<any> => {
  const response = await api.get("/products", { 
    params: { active_only: false, limit: 1000000 }, 
    signal: context?.signal 
  });  # CHANGED: Removed extra /api/v1
  console.log("[getProducts] Response data:", response.data);
  return response.data;
};

// Fetch all employees
export const getEmployees = async (context?: QueryFunctionContext): Promise<any> => {
  const response = await api.get("/hr/employees", { signal: context?.signal });
  console.log("[getEmployees] Response data:", response.data);
  return response.data;
};

// Search customers for autocomplete/dropdown
export const searchCustomers = async ({
  queryKey,
  signal,
}: QueryFunctionContext): Promise<any> => {
  const [, searchTerm, limit] = queryKey;
  const response = await api.get("/customers", {
    params: {
      search: searchTerm,
      limit: limit || 1000000,
      active_only: false,
    },
    signal,
  });  # CHANGED: Removed extra /api/v1
  console.log("[searchCustomers] Response data:", response.data);
  return response.data;
};

// Search products for autocomplete/dropdown
export const searchProducts = async ({
  queryKey,
  signal,
}: QueryFunctionContext): Promise<any> => {
  const [, searchTerm, limit] = queryKey;
  const response = await api.get("/products", {
    params: {
      search: searchTerm,
      limit: limit || 1000000,
      active_only: false,
    },
    signal,
  });  # CHANGED: Removed extra /api/v1
  console.log("[searchProducts] Response data:", response.data);
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
  organization_id?: number;
}): Promise<any> => {
  const response = await api.post("/customers", customerData);  # CHANGED: Removed extra /api/v1
  console.log("[createCustomer] Response data:", response.data);
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
  organization_id?: number;
}): Promise<any> => {
  const requiredFields = ['name', 'contact_number', 'address1', 'city', 'state', 'pin_code', 'state_code'];
  for (const field of requiredFields) {
    if (!vendorData[field] || String(vendorData[field]).trim() === '') {
      throw new Error(`${field.replace('_', ' ')} is required`);
    }
  }
  console.log("[createVendor] Request data:", vendorData);
  const response = await api.post("/vendors", vendorData);  # CHANGED: Removed extra /api/v1
  console.log("[createVendor] Response data:", response.data);
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
  organization_id?: number;
}): Promise<any> => {
  const requiredFields = ['name', 'contact_number', 'address1', 'city', 'state', 'pin_code', 'state_code'];
  for (const field of requiredFields) {
    if (!vendorData[field] || String(vendorData[field]).trim() === '') {
      throw new Error(`${field.replace('_', ' ')} is required`);
    }
  }
  const response = await api.put(`/vendors/${id}`, vendorData);  # CHANGED: Removed extra /api/v1
  console.log("[updateVendor] Response data:", response.data);
  return response.data;
};

// Delete vendor
export const deleteVendor = async (id: number): Promise<any> => {
  const response = await api.delete(`/vendors/${id}`);  # CHANGED: Removed extra /api/v1
  console.log("[deleteVendor] Response data:", response.data);
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
  const response = await api.post("/products", productData);  # CHANGED: Removed extra /api/v1
  console.log("[createProduct] Response data:", response.data);
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
  const response = await api.post("/hr/employees", employeeData);
  console.log("[createEmployee] Response data:", response.data);
  return response.data;
};

export const bulkImportVendors = async (data: any[]): Promise<any> => {
  const response = await api.post("/vendors/bulk", data);  # CHANGED: Removed extra /api/v1
  console.log("[bulkImportVendors] Response data:", response.data);
  return response.data;
};

export const bulkImportCustomers = async (data: any[]): Promise<any> => {
  const response = await api.post("/customers/bulk", data);  # CHANGED: Removed extra /api/v1
  console.log("[bulkImportCustomers] Response data:", response.data);
  return response.data;
};

export const bulkImportProducts = async (data: any[]): Promise<any> => {
  const response = await api.post("/products/bulk", data);  # CHANGED: Removed extra /api/v1
  console.log("[bulkImportProducts] Response data:", response.data);
  return response.data;
};

export const bulkImportStock = async (data: any[]): Promise<any> => {
  const response = await api.post("/stock/bulk", data);  # CHANGED: Removed extra /api/v1
  console.log("[bulkImportStock] Response data:", response.data);
  return response.data;
};

// Fetch stock with parameter cleaning and type checking
export const getStock = async ({ queryKey, signal }: QueryFunctionContext): Promise<StockResponse[]> => {
  const [, rawParams = {}] = queryKey;
  const defaultParams = {
    skip: 0,
    limit: 1000000,
    low_stock_only: false,
    search: "",
    show_zero: true,
  };
  const params: any = { ...defaultParams, ...rawParams };
  if (params.product_id && !isNaN(Number(params.product_id)) && params.product_id !== "") {
    params.product_id = Number(params.product_id);
  } else {
    delete params.product_id;
  }
  console.log("[getStock] Request params:", params);
  try {
    const response = await api.get("/stock", { params, signal });  # CHANGED: Removed extra /api/v1
    console.log("[getStock] Response data:", {
      response: response.data,
      type: typeof response.data,
      isArray: Array.isArray(response.data),
    });
    if (!Array.isArray(response.data)) {
      console.warn("[getStock] Response is not an array:", response.data);
      return [{ quantity: 0, product_id: params.product_id || 0 } as StockResponse];
    }
    if (params.product_id) {
      const stockItem = response.data.find((item: StockResponse) => item.product_id === params.product_id);
      if (!stockItem) {
        console.warn(`[getStock] No stock found for product_id ${params.product_id}`);
        return [{ quantity: 0, product_id: params.product_id } as StockResponse];
      }
      return [stockItem];
    }
    return response.data as StockResponse[];
  } catch (error) {
    console.error("[getStock] Error fetching stock:", error);
    return [{ quantity: 0, product_id: params.product_id || 0 } as StockResponse];
  }
};

// HSN search for GST rate auto-population - now local from CSV
export const hsnSearch = async ({ queryKey }: QueryFunctionContext): Promise<any> => {
  const [, query, limit] = queryKey;
  try {
    const data = await loadGstData();
    const results = data
      .filter((item: HsnResult) => 
        fuzzyMatch(query, item.hsn_code) || fuzzyMatch(query, item.description)
      )
      .sort((a: HsnResult, b: HsnResult) => {
        if (a.hsn_code.startsWith(query)) return -1;
        if (b.hsn_code.startsWith(query)) return 1;
        return 0;
      })
      .slice(0, limit || 10);
    console.log("[hsnSearch] Response data:", results);
    return results;
  } catch (error) {
    console.error("[hsnSearch] Error:", error);
    return [];
  }
};

// Get next account code for a type - revised to use manual URL construction to avoid params serialization issues
export const getNextAccountCode = async (accountType: string): Promise<string> => {
  try {
    const params = new URLSearchParams({ type: accountType });
    const url = `/chart-of-accounts/get-next-code?${params}`;
    const response = await api.get(url);
    console.log("[getNextAccountCode] Response data:", response.data);
    return response.data.next_code;
  } catch (error) {
    console.error("[getNextAccountCode] Error:", error);
    throw error; // Rethrow to handle in caller
  }
};

// Tax Code Management
export interface TaxCode {
  id: number;
  organization_id: number;
  company_id?: number;
  name: string;
  code: string;
  tax_type: string;
  tax_rate: number;
  is_compound: boolean;
  is_active: boolean;
  components?: Record<string, number>;
  tax_account_id?: number;
  effective_from?: string;
  effective_to?: string;
  description?: string;
  hsn_sac_codes?: string[];
  created_at: string;
  updated_at?: string;
}

export interface TaxCodeUpdate {
  name?: string;
  code?: string;
  tax_type?: string;
  tax_rate?: number;
  is_compound?: boolean;
  is_active?: boolean;
  components?: Record<string, number>;
  tax_account_id?: number;
  effective_from?: string;
  effective_to?: string;
  description?: string;
  hsn_sac_codes?: string[];
}

// Get all tax codes
export const getTaxCodes = async (params?: {
  tax_type?: string;
  is_active?: boolean;
  skip?: number;
  limit?: number;
}): Promise<TaxCode[]> => {
  try {
    const response = await api.get("/master-data/tax-codes", { params });
    console.log("[getTaxCodes] Response:", response.data);
    return response.data.items || response.data;
  } catch (error) {
    console.error("[getTaxCodes] Error:", error);
    throw error;
  }
};

// Get single tax code
export const getTaxCode = async (taxCodeId: number): Promise<TaxCode> => {
  try {
    const response = await api.get(`/master-data/tax-codes/${taxCodeId}`);
    console.log("[getTaxCode] Response:", response.data);
    return response.data;
  } catch (error) {
    console.error("[getTaxCode] Error:", error);
    throw error;
  }
};

// Update tax code (including toggle active/inactive)
export const updateTaxCode = async (
  taxCodeId: number,
  data: TaxCodeUpdate
): Promise<TaxCode> => {
  try {
    const response = await api.put(`/master-data/tax-codes/${taxCodeId}`, data);
    console.log("[updateTaxCode] Response:", response.data);
    return response.data;
  } catch (error) {
    console.error("[updateTaxCode] Error:", error);
    throw error;
  }
};

// Toggle tax code active status
export const toggleTaxCodeStatus = async (
  taxCodeId: number,
  isActive: boolean
): Promise<TaxCode> => {
  return updateTaxCode(taxCodeId, { is_active: isActive });
};