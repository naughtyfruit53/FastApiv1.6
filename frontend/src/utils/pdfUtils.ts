// frontend/src/utils/pdfUtils.ts

import api from "../lib/api";

export interface VoucherPdfConfig {
  voucherType: string;
  voucherTitle: string;
  showItems?: boolean;
  showTaxDetails?: boolean;
  entityType?: "vendor" | "customer";
}
export interface VoucherPdfData {
  voucher_number: string;
  date: string;
  reference?: string;
  notes?: string;
  total_amount: number;
  items?: any[];
  // Entity information (vendor/customer)
  vendor?: {
    id: number;
    name: string;
    address?: string;
    contact_number?: string;
    email?: string;
    gstin?: string;
  };
  customer?: {
    id: number;
    name: string;
    address?: string;
    contact_number?: string;
    email?: string;
    gstin?: string;
  };
  // Voucher specific fields
  payment_method?: string;
  receipt_method?: string;
  payment_terms?: string;
  from_account?: string;
  to_account?: string;
  // Additional fields for different voucher types
  [key: string]: any;
}
/**
 * Generate PDF for any voucher type using standardized configuration
 */
export const generateVoucherPDF = async (
  voucherId: number,
  config: VoucherPdfConfig,
): Promise<void> => {
  try {
    // Check authorization before generating PDF
    const token = localStorage.getItem("token");
    if (!token) {
      alert("You must be logged in to generate PDFs");
      return;
    }
    // Call backend API for PDF generation
    const response = await api.post(
      `/pdf-generation/voucher/${config.voucherType}/${voucherId}/download`,
      {},
      { responseType: 'blob' }
    );
    // Handle the response blob
    const blob = response.data;
    const url = window.URL.createObjectURL(blob);

    // Improved filename extraction from Content-Disposition
    let filename = `${config.voucherTitle.replace(/\s+/g, '_')}_${voucherId}.pdf`; // Fallback filename
    const contentDisposition = response.headers['content-disposition'];
    console.log('Content-Disposition header:', contentDisposition);
    if (contentDisposition) {
      // Better regex to handle filename with or without quotes
      const filenameRegex = /filename\*?=['"]?(?:UTF-\d['"]*)?([^;\r\n"']*)['"]?;?/i;
      const matches = filenameRegex.exec(contentDisposition);
      if (matches && matches[1]) {
        filename = matches[1].replace(/['"]/g, '');
        console.log('Extracted filename:', filename);
      } else {
        console.warn('Failed to extract filename from header');
      }
    } else {
      console.warn('No Content-Disposition header found');
    }

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error generating PDF:", error);
    alert("Failed to generate PDF. Please try again.");
  }
};
/**
 * Voucher type configurations for PDF generation
 */
export const VOUCHER_PDF_CONFIGS: Record<string, VoucherPdfConfig> = {
  // Financial Vouchers
  "payment-voucher": {
    voucherType: "payment-voucher",
    voucherTitle: "PAYMENT VOUCHER",
    showItems: false,
    showTaxDetails: false,
    entityType: "vendor",
  },
  "receipt-voucher": {
    voucherType: "receipt-voucher",
    voucherTitle: "RECEIPT VOUCHER",
    showItems: false,
    showTaxDetails: false,
    entityType: "customer",
  },
  "journal-voucher": {
    voucherType: "journal-voucher",
    voucherTitle: "JOURNAL VOUCHER",
    showItems: false,
    showTaxDetails: false,
  },
  "contra-voucher": {
    voucherType: "contra-voucher",
    voucherTitle: "CONTRA VOUCHER",
    showItems: false,
    showTaxDetails: false,
  },
  // Purchase Vouchers
  "purchase-voucher": {
    voucherType: "purchase-voucher",
    voucherTitle: "PURCHASE VOUCHER / BILL",
    showItems: true,
    showTaxDetails: true,
    entityType: "vendor",
  },
  "purchase-order": {
    voucherType: "purchase-orders",
    voucherTitle: "PURCHASE ORDER",
    showItems: true,
    showTaxDetails: true,
    entityType: "vendor",
  },
  grn: {
    voucherType: "grn",
    voucherTitle: "GOODS RECEIPT NOTE",
    showItems: true,
    showTaxDetails: false,
    entityType: "vendor",
  },
  "purchase-return": {
    voucherType: "purchase-return",
    voucherTitle: "PURCHASE RETURN",
    showItems: true,
    showTaxDetails: true,
    entityType: "vendor",
  },
  // Sales Vouchers
  "sales-voucher": {
    voucherType: "sales-voucher",
    voucherTitle: "SALES INVOICE",
    showItems: true,
    showTaxDetails: true,
    entityType: "customer",
  },
  quotation: {
    voucherType: "quotation",
    voucherTitle: "QUOTATION",
    showItems: true,
    showTaxDetails: true,
    entityType: "customer",
  },
  "proforma-invoice": {
    voucherType: "proforma-invoice",
    voucherTitle: "PROFORMA INVOICE",
    showItems: true,
    showTaxDetails: true,
    entityType: "customer",
  },
  "sales-order": {
    voucherType: "sales-order",
    voucherTitle: "SALES ORDER",
    showItems: true,
    showTaxDetails: true,
    entityType: "customer",
  },
  "delivery-challan": {
    voucherType: "delivery-challan",
    voucherTitle: "DELIVERY CHALLAN",
    showItems: true,
    showTaxDetails: false,
    entityType: "customer",
  },
  "sales-return": {
    voucherType: "sales-return",
    voucherTitle: "SALES RETURN",
    showItems: true,
    showTaxDetails: true,
    entityType: "customer",
  },
  "credit-note": {
    voucherType: "credit-note",
    voucherTitle: "CREDIT NOTE",
    showItems: true,
    showTaxDetails: true,
    entityType: "customer",
  },
  "debit-note": {
    voucherType: "debit-note",
    voucherTitle: "DEBIT NOTE",
    showItems: true,
    showTaxDetails: true,
    entityType: "vendor",
  },
  "non-sales-credit-note": {
    voucherType: "non-sales-credit-note",
    voucherTitle: "NON-SALES CREDIT NOTE",
    showItems: true,
    showTaxDetails: true,
    entityType: "customer",
  },
  // Manufacturing Vouchers
  "job-card": {
    voucherType: "job-card",
    voucherTitle: "JOB CARD",
    showItems: true,
    showTaxDetails: true,
    entityType: "vendor",
  },
  "production-order": {
    voucherType: "production-order",
    voucherTitle: "PRODUCTION ORDER",
    showItems: true,
    showTaxDetails: false,
  },
  "work-order": {
    voucherType: "work-order",
    voucherTitle: "WORK ORDER",
    showItems: true,
    showTaxDetails: false,
  },
  "material-receipt": {
    voucherType: "material-receipt",
    voucherTitle: "MATERIAL RECEIPT",
    showItems: true,
    showTaxDetails: false,
  },
  "material-requisition": {
    voucherType: "material-requisition",
    voucherTitle: "MATERIAL REQUISITION",
    showItems: true,
    showTaxDetails: false,
  },
  "finished-good-receipt": {
    voucherType: "finished-good-receipt",
    voucherTitle: "FINISHED GOODS RECEIPT",
    showItems: true,
    showTaxDetails: false,
  },
  "manufacturing-journal": {
    voucherType: "manufacturing-journal",
    voucherTitle: "MANUFACTURING JOURNAL",
    showItems: false,
    showTaxDetails: false,
  },
  "stock-journal": {
    voucherType: "stock-journal",
    voucherTitle: "STOCK JOURNAL",
    showItems: true,
    showTaxDetails: false,
  },
};
/**
 * Get PDF configuration for a voucher type
 */
export const getVoucherPdfConfig = (voucherType: string): VoucherPdfConfig => {
  const config = VOUCHER_PDF_CONFIGS[voucherType];
  if (!config) {
    console.warn(`No PDF configuration found for voucher type: {voucherType}`);
    return {
      voucherType,
      voucherTitle: voucherType.toUpperCase().replace(/-/g, " "),
      showItems: false,
      showTaxDetails: false,
    };
  }
  return config;
};
/**
 * Standalone PDF generation function for individual vouchers
 * Can be used in any voucher component without requiring useVoucherPage hook
 */
export const generateStandalonePDF = async (
  voucherId: number,
  voucherType: string,
): Promise<void> => {
  try {
    console.log(
      "[PDF] Generating standalone PDF for:",
      voucherType,
      voucherId,
    );
    // Check authorization
    const token = localStorage.getItem("token");
    if (!token) {
      alert("You must be logged in to generate PDFs");
      return;
    }
    // Get PDF configuration
    const pdfConfig = getVoucherPdfConfig(voucherType);
    // Generate PDF via backend
    await generateVoucherPDF(voucherId, pdfConfig);
  } catch (error) {
    console.error("[PDF] Error generating standalone PDF:", error);
    alert("Failed to generate PDF. Please try again.");
  }
};