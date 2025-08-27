// frontend/src/types/voucher.types.ts
// TypeScript types for voucher system

export interface VoucherPageConfig {
  voucherType: string;
  entityType: 'purchase' | 'sales' | 'financial';
  endpoint: string;
  nextNumberEndpoint: string;
  hasItems: boolean;
  voucherTitle: string;
  apiEndpoint?: string;
}

export interface VoucherItem {
  id?: number;
  product_id: number | null;
  product_name?: string;
  hsn_code?: string;
  quantity: number;
  unit: string;
  unit_price: number;
  original_unit_price?: number;
  discount_percentage: number;
  discount_amount: number;
  taxable_amount: number;
  gst_rate: number;
  cgst_amount: number;
  sgst_amount: number;
  igst_amount: number;
  total_amount: number;
  reorder_level?: number;
}

export interface VoucherBase {
  id?: number;
  voucher_number: string;
  date: string;
  reference?: string;
  notes?: string;
  total_amount: number;
  created_at?: string;
  updated_at?: string;
  created_by?: number;
  organization_id?: number;
  // Reference document fields
  reference_type?: string;
  reference_id?: number | null;
  reference_number?: string;
}

export interface PurchaseVoucher extends VoucherBase {
  vendor_id: number | null;
  vendor?: {
    id: number;
    name: string;
    email?: string;
    phone?: string;
  };
  payment_terms?: string;
  items: VoucherItem[];
}

export interface SalesVoucher extends VoucherBase {
  customer_id: number | null;
  customer?: {
    id: number;
    name: string;
    email?: string;
    phone?: string;
  };
  payment_terms?: string;
  items: VoucherItem[];
}

export interface FinancialVoucher extends VoucherBase {
  from_account: string;
  to_account: string;
  payment_method?: string;
  receipt_method?: string;
  name_id?: number | null;
  name_type?: 'Vendor' | 'Customer';
}

export interface VoucherFormData extends VoucherBase {
  items?: VoucherItem[];
  vendor_id?: number | null;
  customer_id?: number | null;
  from_account?: string;
  to_account?: string;
  payment_method?: string;
  receipt_method?: string;
  payment_terms?: string;
  name_id?: number | null;
  name_type?: 'Vendor' | 'Customer';
}

export interface VoucherListResponse {
  items: VoucherBase[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ReferenceDocumentData {
  id: number;
  voucher_number: string;
  date: string;
  total_amount: number;
  items?: VoucherItem[];
  customer_id?: number;
  vendor_id?: number;
  type: string;
}

export interface VoucherContextMenuProps {
  anchorEl: null | HTMLElement;
  open: boolean;
  onClose: () => void;
  voucher: VoucherBase;
  onEdit: (id: number) => void;
  onView: (id: number) => void;
  onDelete: (voucher: VoucherBase) => void;
  onGeneratePDF: (voucher: VoucherBase) => void;
}