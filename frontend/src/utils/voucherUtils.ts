// frontend/src/utils/voucherUtils.ts
import { UI_CONSTANTS } from "../constants/ui";

// Type definitions for voucher calculations
interface VoucherItem {
  quantity?: number;
  unit_price?: number;
  discount_percentage?: number;
  discount_amount?: number;
  gst_rate?: number;
  [key: string]: any;
}

interface CalculatedVoucherItem extends VoucherItem {
  discount_amount: number;
  taxable_amount: number;
  cgst_amount: number;
  sgst_amount: number;
  igst_amount: number;
  total_amount: number;
}

export const GST_SLABS = [0, 5, 12, 18, 28];
// State to GST state code mapping for GST calculations
export const STATE_TO_CODE_MAP: { [key: string]: string } = {
  "Andhra Pradesh": "37",
  "Arunachal Pradesh": "12",
  Assam: "18",
  Bihar: "10",
  Chhattisgarh: "22",
  Goa: "30",
  Gujarat: "24",
  Haryana: "06",
  "Himachal Pradesh": "02",
  "Jammu and Kashmir": "01",
  Jharkhand: "20",
  Karnataka: "29",
  Kerala: "32",
  "Madhya Pradesh": "23",
  Maharashtra: "27",
  Manipur: "14",
  Meghalaya: "17",
  Mizoram: "15",
  Nagaland: "13",
  Odisha: "21",
  Punjab: "03",
  Rajasthan: "08",
  Sikkim: "11",
  "Tamil Nadu": "33",
  Telangana: "36",
  Tripura: "16",
  "Uttar Pradesh": "09",
  Uttarakhand: "05",
  "West Bengal": "19",
  "Andaman and Nicobar Islands": "35",
  Chandigarh: "04",
  "Dadra and Nagar Haveli and Daman and Diu": "26",
  Lakshadweep: "31",
  Delhi: "07",
  Puducherry: "34",
  Ladakh: "38",
};
export const voucherTypes = {
  purchase: [
    { label: "Purchase Order", slug: "purchase-orders" },
    { label: "Purchase Voucher", slug: "purchase-vouchers" },
    { label: "Purchase Return", slug: "purchase-returns" },
    { label: "GRN", slug: "grns" },
  ],
  sales: [
    { label: "Quotation", slug: "quotations" },
    { label: "Proforma Invoice", slug: "proforma-invoices" },
    { label: "Sales Order", slug: "sales-orders" },
    { label: "Delivery Challan", slug: "delivery-challans" },
    { label: "Sales Voucher", slug: "sales-vouchers" },
    { label: "Sales Return", slug: "sales-returns" },
  ],
  financial: [
    { label: "Payment Voucher", slug: "payment-vouchers" },
    { label: "Receipt Voucher", slug: "receipt-vouchers" },
    { label: "Journal Voucher", slug: "journal-vouchers" },
    { label: "Contra Voucher", slug: "contra-vouchers" },
  ],
};
/**
 * Convert number to words in Indian format
 * This is the centralized implementation used across all voucher types
 */
export const numberToWordsInteger = (num: number): string => {
  if (num === 0 || isNaN(num)) {
    return "";
  }
  const belowTwenty = [
    "",
    "One",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
    "Eleven",
    "Twelve",
    "Thirteen",
    "Fourteen",
    "Fifteen",
    "Sixteen",
    "Seventeen",
    "Eighteen",
    "Nineteen",
  ];
  const tens = [
    "",
    "",
    "Twenty",
    "Thirty",
    "Forty",
    "Fifty",
    "Sixty",
    "Seventy",
    "Eighty",
    "Ninety",
  ];
  const thousands = ["", "Thousand", "Lakh", "Crore"];
  let word = "";
  let i = 0;
  while (num > 0) {
    let chunk: number;
    if (i === 0) {
      chunk = num % 1000; // Thousands
    } else if (i === 1) {
      chunk = num % 100; // Lakhs (2 digits)
    } else {
      chunk = num % 100; // Crores and above (2 digits each)
    }
    if (chunk) {
      let chunkWord = "";
      if (chunk >= 100) {
        chunkWord += belowTwenty[Math.floor(chunk / 100)] + " Hundred ";
      }
      let remain = chunk % 100;
      if (remain >= 20) {
        chunkWord += tens[Math.floor(remain / 10)] + " ";
        remain %= 10;
      }
      if (remain > 0) {
        chunkWord += belowTwenty[remain] + " ";
      }
      word = chunkWord + thousands[i] + " " + word;
    }
    if (i === 0) {
      num = Math.floor(num / 1000);
    } else {
      num = Math.floor(num / 100);
    }
    i++;
  }
  return word.trim();
};
/**
 * Convert number to words with decimal support
 * This is the the centralized implementation used across all voucher types
 */
export const numberToWords = (num: number): string => {
  if (num === 0 || isNaN(num)) {
    return "Zero only";
  }
  const integer = Math.floor(num);
  const decimal = Math.round((num - integer) * 100);
  let word = numberToWordsInteger(integer);
  if (decimal > 0) {
    word += " and " + numberToWordsInteger(decimal) + " Paise";
  }
  return word ? word + " only" : "";
};
/**
 * Wrapper for numberToWords to match getAmountInWords naming
 * Used in voucher forms for amount in words display
 */
export const getAmountInWords = (amount: number): string => {
  return numberToWords(Math.round(amount));
};
/**
 * Enhanced GST calculation utilities with state-based split logic
 * Supports both intrastate (CGST+SGST) and interstate (IGST) transactions
 */
// Helper function to determine if transaction is intrastate
export const isIntrastateTransaction = (
  companyStateCode: string,
  customerVendorStateCode: string,
): boolean => {
  return companyStateCode === customerVendorStateCode;
};
// Common voucher item calculation utilities with enhanced GST logic
export const calculateItemTotals = (
  item: VoucherItem,
  isIntrastate: boolean = true,
): CalculatedVoucherItem => {
  const subtotal = (item.quantity || 0) * (item.unit_price || 0);
  const discountAmount = subtotal * ((item.discount_percentage || 0) / 100);
  const taxableAmount = subtotal - discountAmount;
  const gstAmount = taxableAmount * ((item.gst_rate || 0) / 100);
  // GST split logic based on transaction type
  let cgstAmount = 0;
  let sgstAmount = 0;
  let igstAmount = 0;
  if (isIntrastate) {
    // Same state: Split GST into CGST and SGST (half each)
    cgstAmount = gstAmount / 2;
    sgstAmount = gstAmount / 2;
    igstAmount = 0;
  } else {
    // Different state: Use IGST (full GST rate)
    cgstAmount = 0;
    sgstAmount = 0;
    igstAmount = gstAmount;
  }
  const totalAmount = taxableAmount + gstAmount;
  return {
    ...item,
    discount_amount: parseFloat(discountAmount.toFixed(2)),
    taxable_amount: parseFloat(taxableAmount.toFixed(2)),
    cgst_amount: parseFloat(cgstAmount.toFixed(2)),
    sgst_amount: parseFloat(sgstAmount.toFixed(2)),
    igst_amount: parseFloat(igstAmount.toFixed(2)),
    total_amount: parseFloat(totalAmount.toFixed(2)),
  };
};
export const calculateVoucherTotals = (
  items: any[],
  isIntrastate: boolean = true,
  lineDiscountType?: 'percentage' | 'amount' | null,
  totalDiscountType?: 'percentage' | 'amount' | null,
  totalDiscountValue: number = 0,
  additionalCharges: any = {},
): any => {
  const safeNumber = (value: number) => isNaN(value) ? 0 : value;
  // First, calculate per item after line discount
  const itemsWithLineDisc = items.map(item => {
    const subtotal = safeNumber(item.quantity || 0) * safeNumber(item.unit_price || 0);
    let lineDiscAmount = 0;
    if (lineDiscountType === 'percentage') {
      lineDiscAmount = subtotal * safeNumber((item.discount_percentage || 0) / 100);
    } else if (lineDiscountType === 'amount') {
      lineDiscAmount = safeNumber(item.discount_amount || 0);
    }
    const afterLineDisc = subtotal - lineDiscAmount;
    return { ...item, subtotal, lineDiscAmount, afterLineDisc };
  });

  const sumAfterLine = itemsWithLineDisc.reduce((sum, item) => sum + item.afterLineDisc, 0);

  let totalDiscAmount = 0;
  if (totalDiscountType === 'percentage') {
    totalDiscAmount = sumAfterLine * (totalDiscountValue / 100);
  } else if (totalDiscountType === 'amount') {
    totalDiscAmount = totalDiscountValue;
  }

  const afterTotalDisc = sumAfterLine - totalDiscAmount;
  
  // Calculate total additional charges
  const totalAdditionalCharges = Object.keys(additionalCharges || {}).reduce((sum, key) => {
    return sum + safeNumber(parseFloat(additionalCharges[key]) || 0);
  }, 0);

  // Add additional charges to taxable amount before GST
  const taxableBeforeGst = afterTotalDisc + totalAdditionalCharges;
  const apportionFactor = sumAfterLine > 0 ? afterTotalDisc / sumAfterLine : 0;

  const computedItems = itemsWithLineDisc.map(item => {
    const taxableAmount = item.afterLineDisc * apportionFactor;
    const gstRate = safeNumber(item.gst_rate || 0);
    const gstAmount = taxableAmount * (gstRate / 100);
    let cgst = 0, sgst = 0, igst = 0;
    if (isIntrastate) {
      cgst = gstAmount / 2;
      sgst = gstAmount / 2;
    } else {
      igst = gstAmount;
    }
    const total = taxableAmount + gstAmount;
    return {
      ...item,
      discount_amount: item.lineDiscAmount, // for line
      taxable_amount: taxableAmount,
      cgst_amount: cgst,
      sgst_amount: sgst,
      igst_amount: igst,
      amount: total, // line total
    };
  });

  const totalSubtotal = itemsWithLineDisc.reduce((sum, item) => sum + item.subtotal, 0);
  
  // Calculate GST on the taxable amount including additional charges
  const totalTaxableFromItems = computedItems.reduce((sum, item) => sum + item.taxable_amount, 0);
  
  // Calculate GST on additional charges (apply weighted average GST rate)
  const totalGstRate = (computedItems.length > 0 && totalTaxableFromItems > 0)
    ? computedItems.reduce((sum, item) => sum + safeNumber((item.gst_rate || 0) * item.taxable_amount), 0) / totalTaxableFromItems
    : 0;
  
  const additionalChargesGst = totalAdditionalCharges * (totalGstRate / 100);
  let additionalChargesCgst = 0, additionalChargesSgst = 0, additionalChargesIgst = 0;
  if (isIntrastate) {
    additionalChargesCgst = additionalChargesGst / 2;
    additionalChargesSgst = additionalChargesGst / 2;
  } else {
    additionalChargesIgst = additionalChargesGst;
  }

  let totalAmount = computedItems.reduce((sum, item) => sum + item.amount, 0) + totalAdditionalCharges + additionalChargesGst;
  const totalCgst = computedItems.reduce((sum, item) => sum + item.cgst_amount, 0) + additionalChargesCgst;
  const totalSgst = computedItems.reduce((sum, item) => sum + item.sgst_amount, 0) + additionalChargesSgst;
  const totalIgst = computedItems.reduce((sum, item) => sum + item.igst_amount, 0) + additionalChargesIgst;
  const totalGst = totalCgst + totalSgst + totalIgst;

  // Aggregated GST breakdown
  const gstBreakdown: { [rate: number]: { cgst: number, sgst: number, igst: number, taxable: number } } = {};
  computedItems.forEach(item => {
    const rate = safeNumber(item.gst_rate || 0);
    if (!gstBreakdown[rate]) {
      gstBreakdown[rate] = { cgst: 0, sgst: 0, igst: 0, taxable: 0 };
    }
    gstBreakdown[rate].cgst += item.cgst_amount;
    gstBreakdown[rate].sgst += item.sgst_amount;
    gstBreakdown[rate].igst += item.igst_amount;
    gstBreakdown[rate].taxable += item.taxable_amount;
  });

  // Calculate round off
  const decimalPart = totalAmount - Math.floor(totalAmount);
  let totalRoundOff = 0;
  if (decimalPart < 0.5) {
    totalRoundOff = -decimalPart;
  } else {
    totalRoundOff = 1 - decimalPart;
  }
  totalAmount += totalRoundOff;

  return {
    computedItems,
    totalAmount: safeNumber(parseFloat(totalAmount.toFixed(2))),
    totalSubtotal: safeNumber(parseFloat(totalSubtotal.toFixed(2))),
    totalDiscount: safeNumber(parseFloat(totalDiscAmount.toFixed(2))),
    totalTaxable: safeNumber(parseFloat(afterTotalDisc.toFixed(2))),
    totalAdditionalCharges: safeNumber(parseFloat(totalAdditionalCharges.toFixed(2))),
    totalGst: safeNumber(parseFloat(totalGst.toFixed(2))),
    totalCgst: safeNumber(parseFloat(totalCgst.toFixed(2))),
    totalSgst: safeNumber(parseFloat(totalSgst.toFixed(2))),
    totalIgst: safeNumber(parseFloat(totalIgst.toFixed(2))),
    gstBreakdown,
    totalRoundOff: safeNumber(parseFloat(totalRoundOff.toFixed(2))),
  };
};
/**
 * Get GST breakdown labels based on transaction type
 */
export const getGstLabels = (isIntrastate: boolean): any => {
  if (isIntrastate) {
    return {
      tax1Label: "CGST",
      tax2Label: "SGST",
      showIgst: false,
    };
  } else {
    return {
      tax1Label: "IGST",
      tax2Label: "",
      showIgst: true,
    };
  }
};
// Common default values for voucher forms
export const getDefaultVoucherValues = (type: "purchase" | "sales"): any => {
  const baseValues = {
    voucher_number: "",
    date: new Date().toISOString().slice(0, 10),
    reference: "",
    payment_terms: "",
    notes: "",
    items: [
      {
        product_id: null as number | null,
        hsn_code: "",
        quantity: 0,
        unit: "",
        unit_price: 0.0,
        original_unit_price: 0.0,
        discount_percentage: 0,
        discount_amount: 0.0,
        taxable_amount: 0.0,
        gst_rate: 0,
        cgst_amount: 0.0,
        sgst_amount: 0.0,
        igst_amount: 0.0,
        total_amount: 0.0,
      },
    ],
    total_amount: 0.0,
    total_discount: 0.0,
  };
  if (type === "purchase") {
    return {
      ...baseValues,
      vendor_id: null as number | null,
    };
  } else {
    return {
      ...baseValues,
      customer_id: null as number | null,
    };
  }
};
/**
 * Format number to 2 decimal places for rate fields
 */
export const formatRateField = (value: number | string): string => {
  const numValue = typeof value === "string" ? parseFloat(value) : value;
  return isNaN(numValue) ? "0.00" : numValue.toFixed(2);
};
/**
 * Parse rate field input to ensure 2 decimal places max
 */
export const parseRateField = (value: string): number => {
  const parsed = parseFloat(value);
  return isNaN(parsed) ? 0 : Math.round(parsed * 100) / 100;
};
/**
 * Get financial voucher default values (no items array)
 */
export const getFinancialVoucherDefaults = (): any => ({
  voucher_number: "",
  date: new Date().toISOString().slice(0, 10),
  reference: "",
  notes: "",
  total_amount: 0,
  from_account: "",
  to_account: "",
  payment_method: "",
  receipt_method: "",
});
/**
 * Voucher configuration presets for common voucher types
 */
export const VOUCHER_CONFIGS = {
  "payment-voucher": {
    voucherType: "payment-vouchers",
    entityType: "financial" as const,
    endpoint: "/payment-vouchers",
    nextNumberEndpoint: "/payment-vouchers/next-number",
    hasItems: false,
    voucherTitle: "Payment Voucher",
  },
  "receipt-voucher": {
    voucherType: "receipt-vouchers",
    entityType: "financial" as const,
    endpoint: "/receipt-vouchers",
    nextNumberEndpoint: "/receipt-vouchers/next-number",
    hasItems: false,
    voucherTitle: "Receipt Voucher",
  },
  "journal-voucher": {
    voucherType: "journal-vouchers",
    entityType: "financial" as const,
    endpoint: "/journal-vouchers",
    nextNumberEndpoint: "/journal-vouchers/next-number",
    hasItems: false,
    voucherTitle: "Journal Voucher",
  },
  "contra-voucher": {
    voucherType: "contra-vouchers",
    entityType: "financial" as const,
    endpoint: "/contra-vouchers",
    nextNumberEndpoint: "/contra-vouchers/next-number",
    hasItems: false,
    voucherTitle: "Contra Voucher",
  },
  "purchase-voucher": {
    voucherType: "purchase-vouchers",
    entityType: "purchase" as const,
    endpoint: "/purchase-vouchers",
    nextNumberEndpoint: "/purchase-vouchers/next-number",
    hasItems: true,
    voucherTitle: "Purchase Voucher",
  },
  "purchase-order": {
    voucherType: "purchase-orders",
    entityType: "purchase" as const,
    endpoint: "/purchase-orders",
    nextNumberEndpoint: "/purchase-orders/next-number",
    hasItems: true,
    voucherTitle: "Purchase Order",
  },
  "purchase-return": {
    voucherType: "purchase-returns",
    entityType: "purchase" as const,
    endpoint: "/purchase-returns",
    nextNumberEndpoint: "/purchase-returns/next-number",
    hasItems: true,
    voucherTitle: "Purchase Return",
  },
  grn: {
    voucherType: "goods-receipt-notes",
    entityType: "purchase" as const,
    endpoint: "/goods-receipt-notes",
    nextNumberEndpoint: "/goods-receipt-notes/next-number",
    hasItems: true,
    voucherTitle: "GRN",
  },
  "sales-voucher": {
    voucherType: "sales-vouchers",
    entityType: "sales" as const,
    endpoint: "/sales-vouchers",
    nextNumberEndpoint: "/sales-vouchers/next-number",
    hasItems: true,
    voucherTitle: "Sales Voucher",
  },
  quotation: {
    voucherType: "quotations",
    entityType: "sales" as const,
    endpoint: "/quotations",
    nextNumberEndpoint: "/quotations/next-number",
    hasItems: true,
    voucherTitle: "Quotation",
  },
  "proforma-invoice": {
    voucherType: "proforma-invoices",
    entityType: "sales" as const,
    endpoint: "/proforma-invoices",
    nextNumberEndpoint: "/proforma-invoices/next-number",
    hasItems: true,
    voucherTitle: "Proforma Invoice",
  },
  "sales-order": {
    voucherType: "sales-orders",
    entityType: "sales" as const,
    endpoint: "/sales-orders",
    nextNumberEndpoint: "/sales-orders/next-number",
    hasItems: true,
    voucherTitle: "Sales Order",
  },
  "delivery-challan": {
    voucherType: "delivery-challans",
    entityType: "sales" as const,
    endpoint: "/delivery-challans",
    nextNumberEndpoint: "/delivery-challans/next-number",
    hasItems: true,
    voucherTitle: "Delivery Challan",
  },
  "sales-return": {
    voucherType: "sales-returns",
    entityType: "sales" as const,
    endpoint: "/sales-returns",
    nextNumberEndpoint: "/sales-returns/next-number",
    hasItems: true,
    voucherTitle: "Sales Return",
  },
  "credit-note": {
    voucherType: "credit-notes",
    entityType: "financial" as const,
    endpoint: "/credit-notes",
    nextNumberEndpoint: "/credit-notes/next-number",
    hasItems: false,
    voucherTitle: "Credit Note",
  },
  "debit-note": {
    voucherType: "debit-notes",
    entityType: "financial" as const,
    endpoint: "/debit-notes",
    nextNumberEndpoint: "/debit-notes/next-number",
    hasItems: false,
    voucherTitle: "Debit Note",
  },
  "non-sales-credit-note": {
    voucherType: "non-sales-credit-notes",
    entityType: "financial" as const,
    endpoint: "/non-sales-credit-notes",
    nextNumberEndpoint: "/non-sales-credit-notes/next-number",
    hasItems: false,
    voucherTitle: "Non-Sales Credit Note",
  },
  // Manufacturing Vouchers
  "job-card": {
    voucherType: "job-cards",
    entityType: "purchase" as const,
    endpoint: "/job-cards",
    nextNumberEndpoint: "/job-cards/next-number",
    hasItems: true,
    voucherTitle: "Job Card",
  },
  "production-order": {
    voucherType: "production-orders",
    entityType: "purchase" as const,
    endpoint: "/production-orders",
    nextNumberEndpoint: "/production-orders/next-number",
    hasItems: true,
    voucherTitle: "Production Order",
  },
  "work-order": {
    voucherType: "work-orders",
    entityType: "purchase" as const,
    endpoint: "/work-orders",
    nextNumberEndpoint: "/work-orders/next-number",
    hasItems: true,
    voucherTitle: "Work Order",
  },
  "material-receipt": {
    voucherType: "material-receipts",
    entityType: "purchase" as const,
    endpoint: "/material-receipts",
    nextNumberEndpoint: "/material-receipts/next-number",
    hasItems: true,
    voucherTitle: "Material Receipt",
  },
  "material-requisition": {
    voucherType: "material-requisitions",
    entityType: "purchase" as const,
    endpoint: "/material-requisitions",
    nextNumberEndpoint: "/material-requisitions/next-number",
    hasItems: true,
    voucherTitle: "Material Requisition",
  },
  "finished-good-receipt": {
    voucherType: "finished-good-receipts",
    entityType: "purchase" as const,
    endpoint: "/finished-good-receipts",
    nextNumberEndpoint: "/finished-good-receipts/next-number",
    hasItems: true,
    voucherTitle: "Finished Good Receipt",
  },
  "manufacturing-journal": {
    voucherType: "manufacturing-journals",
    entityType: "financial" as const,
    endpoint: "/manufacturing-journals",
    nextNumberEndpoint: "/manufacturing-journals/next-number",
    hasItems: false,
    voucherTitle: "Manufacturing Journal",
  },
  "stock-journal": {
    voucherType: "stock-journals",
    entityType: "financial" as const,
    endpoint: "/stock-journals",
    nextNumberEndpoint: "/stock-journals/next-number",
    hasItems: true,
    voucherTitle: "Stock Journal",
  },
} as const;
/**
 * Reference column configurations for voucher types
 * Defines which voucher types can reference which other voucher types
 */
export const REFERENCE_CONFIGS = {
  "purchase-voucher": {
    allowedTypes: ["purchase-order", "grn"],
    label: "Reference Document",
  },
  "purchase-return": {
    allowedTypes: ["purchase-voucher"],
    label: "Reference Purchase Voucher",
  },
  "sales-voucher": {
    allowedTypes: [
      "delivery-challan",
      "sales-order",
      "quotation",
      "proforma-invoice",
    ],
    label: "Reference Document",
  },
  "sales-return": {
    allowedTypes: ["delivery-challan", "sales-voucher"],
    label: "Reference Document",
  },
  "delivery-challan": {
    allowedTypes: ["sales-order", "quotation", "proforma-invoice"],
    label: "Reference Document",
  },
  "sales-order": {
    allowedTypes: ["quotation", "proforma-invoice"],
    label: "Reference Document",
  },
  "proforma-invoice": {
    allowedTypes: ["quotation", "sales-order"],
    label: "Reference Document",
  },
  // These voucher types don't have reference columns per requirements
  grn: null,
  quotation: null,
  "purchase-order": null,
} as const;
/**
 * Voucher types that should NOT have GST/totals sections
 */
export const NO_GST_VOUCHER_TYPES = ["grn", "delivery-challan"] as const;
/**
 * Default pagination settings for all voucher types
 */
export const VOUCHER_PAGINATION_DEFAULTS = {
  pageSize: 5,
  sortOrder: "desc", // Latest on top
  sortBy: "created_at",
} as const;
/**
 * Get voucher configuration by type
 */
export const getVoucherConfig = (
  voucherType: keyof typeof VOUCHER_CONFIGS,
): any => {
  const baseConfig = VOUCHER_CONFIGS[voucherType];
  const referenceConfig =
    REFERENCE_CONFIGS[voucherType as keyof typeof REFERENCE_CONFIGS];
  const hasGstSection = !NO_GST_VOUCHER_TYPES.includes(voucherType as any);
  return {
    ...baseConfig,
    referenceConfig,
    hasGstSection,
    pagination: VOUCHER_PAGINATION_DEFAULTS,
  };
};
/**
 * Get reference voucher options for a given voucher type
 */
export const getReferenceVoucherOptions = (
  voucherType: keyof typeof REFERENCE_CONFIGS,
): any => {
  const config = REFERENCE_CONFIGS[voucherType];
  if (!config) {
    return [{ value: "new", label: "New", endpoint: "" }];
  }
  const options = config.allowedTypes.map((type) => ({
    value: type,
    label: VOUCHER_CONFIGS[type]?.voucherTitle || type,
    endpoint: VOUCHER_CONFIGS[type]?.endpoint || `/${type}s`,
  }));
  // Add 'New' as the first option instead of 'None'
  return [{ value: "new", label: "New", endpoint: "" }, ...options];
};
/**
 * Check if a voucher type should have GST/totals section
 */
export const shouldShowGstSection = (voucherType: string): boolean => {
  return !NO_GST_VOUCHER_TYPES.includes(voucherType as any);
};
/**
 * Enhanced rate field utilities with strict 2 decimal place formatting
 */
export const enhancedRateUtils = {
  /**
   * Format rate to exactly 2 decimal places
   */
  formatRate: (value: number | string): string => {
    const numValue = typeof value === "string" ? parseFloat(value) : value;
    return isNaN(numValue) ? "0.00" : numValue.toFixed(2);
  },
  /**
   * Parse rate input ensuring 2 decimal places max
   */
  parseRate: (value: string): number => {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? 0 : Math.round(parsed * 100) / 100;
  },
  /**
   * Validate rate input (positive number with max 2 decimal places)
   */
  validateRate: (value: string): boolean => {
    const regex = /^\d+(\.\d{1,2})?$/;
    return regex.test(value) && parseFloat(value) >= 0;
  },
};
/**
 * Enhanced voucher list utilities with minimal pagination and sorting
 */
export const voucherListUtils = {
  /**
   * Sort vouchers with latest first
   */
  sortLatestFirst: (vouchers: any[]): any => {
    return [...vouchers].sort((a, b) => {
      const dateA = new Date(a.created_at || a.date);
      const dateB = new Date(b.created_at || b.date);
      return dateB.getTime() - dateA.getTime();
    });
  },
  /**
   * Paginate vouchers with default 5 per page
   */
  paginate: (vouchers: any[], page: number = 1, pageSize: number = 5): any => {
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return {
      items: vouchers.slice(startIndex, endIndex),
      totalPages: Math.ceil(vouchers.length / pageSize),
      currentPage: page,
      totalItems: vouchers.length,
      hasNext: endIndex < vouchers.length,
      hasPrev: page > 1,
    };
  },
  /**
   * Get latest vouchers for dashboard display
   */
  getLatestVouchers: (vouchers: any[], count: number = 7): any => {
    return voucherListUtils.sortLatestFirst(vouchers).slice(0, count);
  },
};
/**
 * Common styling utilities for voucher forms and tables with minimal gaps
 */
export const getVoucherStyles = (): any => ({
  // Center alignment for all text elements
  centerText: {
    textAlign: "center" as const,
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  // Center alignment for form fields
  centerField: {
    textAlign: "center" as const,
    "& .MuiInputBase-input": {
      textAlign: "center" as const,
    },
  },
  // Center alignment for table headers
  centerHeader: {
    textAlign: "center" as const,
    fontWeight: "bold",
  },
  // Center alignment for table cells
  centerCell: {
    textAlign: "center" as const,
  },
  // Container for voucher layout with minimal padding
  voucherContainer: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    width: "100%",
    margin: 0,
    padding: 0,
  },
  // Full-width edge-to-edge layout container
  edgeToEdgeContainer: {
    width: "100%",
    margin: 0,
    padding: 0,
    boxSizing: "border-box" as const,
    "& .MuiContainer-root": {
      maxWidth: "none !important",
      padding: "0 !important",
      margin: "0 !important",
    },
    "& .MuiBox-root": {
      margin: "0 !important",
    },
  },
  // Index and form layout containers
  indexContainer: {
    width: "100%",
    padding: 0,
    margin: 0,
  },
  formContainer: {
    width: "100%",
    padding: 0,
    margin: 0,
    boxSizing: "border-box" as const,
    "& .MuiTextField-root": {
      "& .MuiInputBase-input": {
        textAlign: "center" as const,
      },
    },
    "& .MuiFormLabel-root": {
      textAlign: "center" as const,
    },
    // Enhanced dropdown width for voucher numbers
    "& .voucher-dropdown": {
      minWidth: `${UI_CONSTANTS.WIDTH.VOUCHER_MIN}px`,
      "& .MuiSelect-select": {
        minWidth: `${UI_CONSTANTS.WIDTH.VOUCHER_MIN - 20}px`,
        textOverflow: "ellipsis",
        overflow: "hidden",
        whiteSpace: "nowrap",
      },
    },
    // Reference dropdown width
    "& .reference-dropdown": {
      minWidth: `${UI_CONSTANTS.WIDTH.REFERENCE_MIN}px`,
      "& .MuiSelect-select": {
        minWidth: `${UI_CONSTANTS.WIDTH.REFERENCE_MIN - 20}px`,
        textOverflow: "ellipsis",
        overflow: "hidden",
        whiteSpace: "nowrap",
      },
    },
  },
  // Table with center-aligned content
  centeredTable: {
    "& .MuiTableCell-root": {
      textAlign: "center" as const,
    },
    "& .MuiTableCell-head": {
      textAlign: "center" as const,
      fontWeight: "bold",
    },
  },
  // Rate field styling with 2 decimal places
  rateField: {
    "& .MuiInputBase-input": {
      textAlign: "center" as const,
    },
    "& input[type=number]": {
      "-moz-appearance": "textfield",
    },
    "& input[type=number]::-webkit-outer-spin-button": {
      "-webkit-appearance": "none",
      margin: 0,
    },
    "& input[type=number]::-webkit-inner-spin-button": {
      "-webkit-appearance": "none",
      margin: 0,
    },
  },
  // Enhanced title styling with center alignment
  voucherTitle: {
    textAlign: "center" as const,
    fontWeight: "bold",
    fontSize: "1.25rem",
    marginBottom: "16px",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  // Date field styling to ensure visibility in view mode
  dateField: {
    "& .MuiInputBase-input": {
      textAlign: "center" as const,
    },
    "& .MuiFormLabel-root": {
      display: "block !important",
      visibility: "visible !important",
    },
  },
  // Pagination styling for 5 per page standard
  paginationContainer: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "16px",
    "& .MuiPagination-root": {
      "& .MuiPaginationItem-root": {
        fontSize: "0.875rem",
      },
    },
  },
  // Optimized table column widths for voucher product tables
  productTableColumns: {
    productName: {
      width: "35%",
      minWidth: "200px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    quantity: {
      width: "12%",
      minWidth: "80px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    rate: {
      width: "10%",
      minWidth: "70px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    discount: {
      width: "8%",
      minWidth: "60px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    gst: {
      width: "8%",
      minWidth: "60px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    amount: {
      width: "12%",
      minWidth: "90px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    hsn: {
      width: "10%",
      minWidth: "80px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    action: {
      width: "8%",
      minWidth: "60px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
  },
  // GRN specific column widths (different from standard vouchers)
  grnTableColumns: {
    productName: {
      width: "30%",
      minWidth: "200px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    orderQty: {
      width: "17.5%",
      minWidth: "80px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    receivedQty: {
      width: "17.5%",
      minWidth: "80px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    acceptedQty: {
      width: "17.5%",
      minWidth: "80px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
    rejectedQty: {
      width: "17.5%",
      minWidth: "80px",
      fontSize: 12,
      fontWeight: "bold",
      padding: "4px 8px",
      textAlign: "center" as const,
    },
  },
  // Enhanced table container with minimal gaps
  optimizedTableContainer: {
    "& .MuiTableContainer-root": {
      borderRadius: "4px",
    },
    "& .MuiTable-root": {
      borderCollapse: "separate",
      borderSpacing: 0,
    },
    "& .MuiTableCell-root": {
      padding: "4px 4px",
      "&:last-child": {
        borderRight: "none",
      },
    },
    "& .MuiTableHead-root .MuiTableCell-root": {
      backgroundColor: "#fafafa",
      fontSize: "12px",
      fontWeight: "bold",
    },
    "& .MuiTableBody-root .MuiTableRow-root": {
      "&:hover": {
        backgroundColor: "#f8f9fa",
      },
      "&:nth-of-type(even)": {
        backgroundColor: "#fafbfc",
      },
    },
  },
  
  // Enhanced button styling for voucher forms
  voucherActionButtons: {
    display: "flex",
    gap: "8px",
    justifyContent: "center",
    alignItems: "center",
    "& .MuiButton-root": {
      textTransform: "none",
      borderRadius: "6px",
      fontWeight: "500",
      boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
      "&:hover": {
        boxShadow: "0 4px 8px rgba(0,0,0,0.15)",
        transform: "translateY(-1px)",
      },
      transition: "all 0.2s ease-in-out",
    },
    "& .MuiButton-contained": {
      background: "linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)",
      color: "white",
    },
    "& .MuiButton-outlined": {
      borderColor: "#2196F3",
      color: "#2196F3",
      "&:hover": {
        backgroundColor: "rgba(33, 150, 243, 0.04)",
      },
    },
  },

  // Enhanced form field styling
  enhancedFormField: {
    "& .MuiTextField-root": {
      "& .MuiOutlinedInput-root": {
        borderRadius: "6px",
        "&:hover": {
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "#2196F3",
          },
        },
        "&.Mui-focused": {
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "#2196F3",
            borderWidth: "2px",
          },
        },
      },
      "& .MuiInputLabel-root": {
        color: "#666",
        "&.Mui-focused": {
          color: "#2196F3",
        },
      },
    },
  },

  // Enhanced table styling with better visual hierarchy
  enhancedTable: {
    "& .MuiTableContainer-root": {
      borderRadius: "8px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
      border: "1px solid #e0e0e0",
    },
    "& .MuiTableHead-root": {
      background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
      "& .MuiTableCell-root": {
        fontWeight: "600",
        color: "#2c3e50",
        borderBottom: "2px solid #e0e0e0",
      },
    },
    "& .MuiTableBody-root .MuiTableRow-root": {
      "&:hover": {
        backgroundColor: "#f8f9fa",
        transform: "scale(1.01)",
        transition: "all 0.2s ease-in-out",
      },
    },
  },

  // Loading and error states styling
  loadingContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "200px",
    gap: "16px",
    "& .MuiCircularProgress-root": {
      color: "#2196F3",
    },
    "& .MuiTypography-root": {
      color: "#666",
      textAlign: "center",
    },
  },

  // Success and error feedback styling
  feedbackContainer: {
    "& .MuiAlert-root": {
      borderRadius: "8px",
      fontWeight: "500",
      "& .MuiAlert-icon": {
        alignItems: "center",
      },
    },
    "& .MuiAlert-standardSuccess": {
      backgroundColor: "#e8f5e8",
      color: "#2e7d32",
    },
    "& .MuiAlert-standardError": {
      backgroundColor: "#ffeaea",
      color: "#d32f2f",
    },
  },
});