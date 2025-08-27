// Unified PDF generation utility for all voucher types
// frontend/src/utils/pdfUtils.ts

import pdfService from '../services/pdfService';

export interface VoucherPdfConfig {
  voucherType: string;
  voucherTitle: string;
  showItems?: boolean;
  showTaxDetails?: boolean;
  entityType?: 'vendor' | 'customer';
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
export const generateVoucherPDF = async (voucherData: VoucherPdfData, config: VoucherPdfConfig) => {
  try {
    // Check authorization before generating PDF
    const token = localStorage.getItem('token');
    if (!token) {
      alert('You must be logged in to generate PDFs');
      return;
    }

    // Prepare standardized voucher data for the PDF service
    const pdfVoucherData = {
      voucher_number: voucherData.voucher_number,
      date: voucherData.date,
      reference: voucherData.reference,
      notes: voucherData.notes,
      total_amount: voucherData.total_amount || 0,
      items: voucherData.items || [],
      // Map party information based on entity type
      party: config.entityType === 'vendor' && voucherData.vendor ? {
        name: voucherData.vendor.name,
        address: voucherData.vendor.address,
        contact_number: voucherData.vendor.contact_number,
        email: voucherData.vendor.email,
        gstin: voucherData.vendor.gstin
      } : config.entityType === 'customer' && voucherData.customer ? {
        name: voucherData.customer.name,
        address: voucherData.customer.address,
        contact_number: voucherData.customer.contact_number,
        email: voucherData.customer.email,
        gstin: voucherData.customer.gstin
      } : undefined,
      // Include voucher-specific fields
      payment_method: voucherData.payment_method,
      receipt_method: voucherData.receipt_method,
      payment_terms: voucherData.payment_terms,
      from_account: voucherData.from_account,
      to_account: voucherData.to_account,
      ...Object.fromEntries(
        Object.entries(voucherData).filter(([key]) => 
          !['voucher_number', 'date', 'reference', 'notes', 'total_amount', 'items', 'vendor', 'customer'].includes(key)
        )
      )
    };

    const pdfOptions = {
      voucherType: config.voucherType,
      voucherTitle: config.voucherTitle,
      filename: `${config.voucherTitle.replace(/\s+/g, '')}${voucherData.voucher_number?.replace(/[^a-zA-Z0-9]/g, '_') || 'Unknown'}.pdf`,
      showItems: config.showItems || false,
      showTaxDetails: config.showTaxDetails || false
    };

    await pdfService.generateVoucherPDF(pdfVoucherData, pdfOptions);
  } catch (error) {
    console.error('Error generating PDF:', error);
    alert('Failed to generate PDF. Please try again.');
  }
};

/**
 * Voucher type configurations for PDF generation
 */
export const VOUCHER_PDF_CONFIGS: Record<string, VoucherPdfConfig> = {
  // Financial Vouchers
  'payment-voucher': {
    voucherType: 'payment-voucher',
    voucherTitle: 'PAYMENT VOUCHER',
    showItems: false,
    showTaxDetails: false,
    entityType: 'vendor'
  },
  'receipt-voucher': {
    voucherType: 'receipt-voucher',
    voucherTitle: 'RECEIPT VOUCHER',
    showItems: false,
    showTaxDetails: false,
    entityType: 'customer'
  },
  'journal-voucher': {
    voucherType: 'journal-voucher',
    voucherTitle: 'JOURNAL VOUCHER',
    showItems: false,
    showTaxDetails: false
  },
  'contra-voucher': {
    voucherType: 'contra-voucher',
    voucherTitle: 'CONTRA VOUCHER',
    showItems: false,
    showTaxDetails: false
  },
  
  // Purchase Vouchers
  'purchase-voucher': {
    voucherType: 'purchase-voucher',
    voucherTitle: 'PURCHASE VOUCHER / BILL',
    showItems: true,
    showTaxDetails: true,
    entityType: 'vendor'
  },
  'purchase-order': {
    voucherType: 'purchase-order',
    voucherTitle: 'PURCHASE ORDER',
    showItems: true,
    showTaxDetails: true,
    entityType: 'vendor'
  },
  'grn': {
    voucherType: 'grn',
    voucherTitle: 'GOODS RECEIPT NOTE',
    showItems: true,
    showTaxDetails: false,
    entityType: 'vendor'
  },
  'purchase-return': {
    voucherType: 'purchase-return',
    voucherTitle: 'PURCHASE RETURN',
    showItems: true,
    showTaxDetails: true,
    entityType: 'vendor'
  },
  
  // Sales Vouchers
  'sales-voucher': {
    voucherType: 'sales-voucher',
    voucherTitle: 'SALES INVOICE',
    showItems: true,
    showTaxDetails: true,
    entityType: 'customer'
  },
  'quotation': {
    voucherType: 'quotation',
    voucherTitle: 'QUOTATION',
    showItems: true,
    showTaxDetails: true,
    entityType: 'customer'
  },
  'proforma-invoice': {
    voucherType: 'proforma-invoice',
    voucherTitle: 'PROFORMA INVOICE',
    showItems: true,
    showTaxDetails: true,
    entityType: 'customer'
  },
  'sales-order': {
    voucherType: 'sales-order',
    voucherTitle: 'SALES ORDER',
    showItems: true,
    showTaxDetails: true,
    entityType: 'customer'
  },
  'delivery-challan': {
    voucherType: 'delivery-challan',
    voucherTitle: 'DELIVERY CHALLAN',
    showItems: true,
    showTaxDetails: false,
    entityType: 'customer'
  },
  'sales-return': {
    voucherType: 'sales-return',
    voucherTitle: 'SALES RETURN',
    showItems: true,
    showTaxDetails: true,
    entityType: 'customer'
  },
  'credit-note': {
    voucherType: 'credit-note',
    voucherTitle: 'CREDIT NOTE',
    showItems: true,
    showTaxDetails: true,
    entityType: 'customer'
  },
  'debit-note': {
    voucherType: 'debit-note',
    voucherTitle: 'DEBIT NOTE',
    showItems: true,
    showTaxDetails: true,
    entityType: 'vendor'
  },
  'non-sales-credit-note': {
    voucherType: 'non-sales-credit-note',
    voucherTitle: 'NON-SALES CREDIT NOTE',
    showItems: true,
    showTaxDetails: true,
    entityType: 'customer'
  },
  
  // Manufacturing Vouchers
  'job-card': {
    voucherType: 'job-card',
    voucherTitle: 'JOB CARD',
    showItems: true,
    showTaxDetails: true,
    entityType: 'vendor'
  },
  'production-order': {
    voucherType: 'production-order',
    voucherTitle: 'PRODUCTION ORDER',
    showItems: true,
    showTaxDetails: false
  },
  'work-order': {
    voucherType: 'work-order',
    voucherTitle: 'WORK ORDER',
    showItems: true,
    showTaxDetails: false
  },
  'material-receipt': {
    voucherType: 'material-receipt',
    voucherTitle: 'MATERIAL RECEIPT',
    showItems: true,
    showTaxDetails: false
  },
  'material-requisition': {
    voucherType: 'material-requisition',
    voucherTitle: 'MATERIAL REQUISITION',
    showItems: true,
    showTaxDetails: false
  },
  'finished-good-receipt': {
    voucherType: 'finished-good-receipt',
    voucherTitle: 'FINISHED GOODS RECEIPT',
    showItems: true,
    showTaxDetails: false
  },
  'manufacturing-journal': {
    voucherType: 'manufacturing-journal',
    voucherTitle: 'MANUFACTURING JOURNAL',
    showItems: false,
    showTaxDetails: false
  },
  'stock-journal': {
    voucherType: 'stock-journal',
    voucherTitle: 'STOCK JOURNAL',
    showItems: true,
    showTaxDetails: false
  }
};

/**
 * Get PDF configuration for a voucher type
 */
export const getVoucherPdfConfig = (voucherType: string): VoucherPdfConfig => {
  const config = VOUCHER_PDF_CONFIGS[voucherType];
  if (!config) {
    console.warn(`No PDF configuration found for voucher type: ${voucherType}`);
    return {
      voucherType,
      voucherTitle: voucherType.toUpperCase().replace(/-/g, ' '),
      showItems: false,
      showTaxDetails: false
    };
  }
  return config;
};

/**
 * Standalone PDF generation function for individual vouchers
 * Can be used in any voucher component without requiring useVoucherPage hook
 */
export const generateStandalonePDF = async (
  voucherData: any, 
  voucherType: string, 
  entityData?: { vendor?: any; customer?: any; employee?: any }
) => {
  try {
    console.log('[PDF] Generating standalone PDF for:', voucherType, voucherData);
    
    // Check authorization
    const token = localStorage.getItem('token');
    if (!token) {
      alert('You must be logged in to generate PDFs');
      return;
    }

    // Get PDF configuration
    const pdfConfig = getVoucherPdfConfig(voucherType);
    
    // Prepare PDF data with entity information
    const pdfData: VoucherPdfData = {
      voucher_number: voucherData.voucher_number || voucherData.job_number || 'Unknown',
      date: voucherData.date || new Date().toISOString().split('T')[0],
      reference: voucherData.reference || voucherData.po_number,
      notes: voucherData.notes || voucherData.description,
      total_amount: voucherData.total_amount || voucherData.total_cost || 0,
      items: voucherData.items || voucherData.materials || [],
      // Map entity information
      vendor: entityData?.vendor,
      customer: entityData?.customer,
      // Additional voucher-specific fields
      payment_method: voucherData.payment_method,
      receipt_method: voucherData.receipt_method,
      payment_terms: voucherData.payment_terms,
      from_account: voucherData.from_account,
      to_account: voucherData.to_account,
      // Manufacturing-specific fields
      job_type: voucherData.job_type,
      job_description: voucherData.job_description,
      expected_completion_date: voucherData.expected_completion_date,
      actual_completion_date: voucherData.actual_completion_date,
      materials_supplied_by: voucherData.materials_supplied_by,
      quality_specifications: voucherData.quality_specifications
    };

    // Generate PDF
    await generateVoucherPDF(pdfData, pdfConfig);
    
    console.log('[PDF] PDF generated successfully for:', voucherType);
  } catch (error) {
    console.error('[PDF] Error generating standalone PDF:', error);
    alert('Failed to generate PDF. Please try again.');
  }
};