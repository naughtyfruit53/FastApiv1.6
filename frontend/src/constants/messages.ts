// frontend/src/constants/messages.ts
// Centralized success and error messages for consistency across the application

export const SUCCESS_MESSAGES = {
  // Master Data
  CUSTOMER_ADDED: "Customer added successfully!",
  CUSTOMER_UPDATED: "Customer updated successfully!",
  CUSTOMER_DELETED: "Customer deleted successfully!",
  
  VENDOR_ADDED: "Vendor added successfully!",
  VENDOR_UPDATED: "Vendor updated successfully!",
  VENDOR_DELETED: "Vendor deleted successfully!",
  
  PRODUCT_ADDED: "Product added successfully!",
  PRODUCT_UPDATED: "Product updated successfully!",
  PRODUCT_DELETED: "Product deleted successfully!",
  
  EMPLOYEE_ADDED: "Employee added successfully!",
  EMPLOYEE_UPDATED: "Employee updated successfully!",
  EMPLOYEE_DELETED: "Employee deleted successfully!",
  
  // Vouchers
  VOUCHER_CREATED: "Voucher created successfully!",
  VOUCHER_UPDATED: "Voucher updated successfully!",
  VOUCHER_DELETED: "Voucher deleted successfully!",
  VOUCHER_DUPLICATED: "Voucher duplicated successfully!",
  
  // Company
  COMPANY_DETAILS_SAVED: "Company details saved successfully!",
  COMPANY_LOGO_UPLOADED: "Company logo uploaded successfully!",
  BANK_ACCOUNT_ADDED: "Bank account added successfully!",
  
  // Organization Settings
  SETTINGS_UPDATED: "Settings updated successfully!",
  TALLY_CONNECTED: "Tally connection established successfully!",
  TALLY_SYNC_COMPLETED: "Tally sync completed successfully!",
  
  // General
  SAVED: "Saved successfully!",
  UPDATED: "Updated successfully!",
  DELETED: "Deleted successfully!",
  COPIED: "Copied successfully!",
} as const;

export const ERROR_MESSAGES = {
  // Master Data
  CUSTOMER_ADD_FAILED: "Failed to add customer",
  CUSTOMER_UPDATE_FAILED: "Failed to update customer",
  CUSTOMER_DELETE_FAILED: "Failed to delete customer",
  
  VENDOR_ADD_FAILED: "Failed to add vendor",
  VENDOR_UPDATE_FAILED: "Failed to update vendor",
  VENDOR_DELETE_FAILED: "Failed to delete vendor",
  
  PRODUCT_ADD_FAILED: "Failed to add product",
  PRODUCT_UPDATE_FAILED: "Failed to update product",
  PRODUCT_DELETE_FAILED: "Failed to delete product",
  
  // Vouchers
  VOUCHER_CREATE_FAILED: "Failed to create voucher",
  VOUCHER_UPDATE_FAILED: "Failed to update voucher",
  VOUCHER_DELETE_FAILED: "Failed to delete voucher",
  VOUCHER_LOAD_FAILED: "Failed to load voucher",
  
  // Company
  COMPANY_DETAILS_FAILED: "Failed to save company details",
  COMPANY_LOGO_FAILED: "Failed to upload company logo",
  
  // Organization Settings
  SETTINGS_UPDATE_FAILED: "Failed to update settings",
  SETTINGS_LOAD_FAILED: "Failed to load settings",
  
  // Tally
  TALLY_CONNECTION_FAILED: "Failed to connect to Tally",
  TALLY_SYNC_FAILED: "Failed to sync with Tally",
  
  // General
  SAVE_FAILED: "Failed to save",
  UPDATE_FAILED: "Failed to update",
  DELETE_FAILED: "Failed to delete",
  LOAD_FAILED: "Failed to load",
  UNKNOWN_ERROR: "An unknown error occurred",
} as const;

export const CONFIRM_MESSAGES = {
  // Delete confirmations
  DELETE_CUSTOMER: "Are you sure you want to delete this customer?",
  DELETE_VENDOR: "Are you sure you want to delete this vendor?",
  DELETE_PRODUCT: "Are you sure you want to delete this product?",
  DELETE_VOUCHER: "Are you sure you want to delete this voucher?",
  
  // Action confirmations
  DISCARD_CHANGES: "Are you sure you want to discard your changes?",
  RESET_FORM: "Are you sure you want to reset the form?",
  CANCEL_OPERATION: "Are you sure you want to cancel this operation?",
  
  // Voucher specific
  DUPLICATE_VOUCHER: "Are you sure you want to duplicate this voucher?",
  REVISE_VOUCHER: "Are you sure you want to create a revision of this voucher?",
} as const;

export const INFO_MESSAGES = {
  NO_DATA: "No data available",
  LOADING: "Loading...",
  SAVING: "Saving...",
  PROCESSING: "Processing...",
  SYNCING: "Syncing with Tally...",
  
  // Company setup
  COMPANY_SETUP_REQUIRED: "Please complete your company setup to continue",
  BANK_ACCOUNT_SETUP: "Would you like to add a bank account now?",
  
  // Vouchers
  VOUCHER_NUMBER_GENERATING: "Generating voucher number...",
  INTERSTATE_TRANSACTION: "This is an interstate transaction (IGST will be applied)",
  INTRASTATE_TRANSACTION: "This is an intrastate transaction (CGST + SGST will be applied)",
} as const;

// Helper function to get dynamic messages
export const getDynamicMessage = {
  voucherDeleted: (voucherNumber: string) => `Voucher ${voucherNumber} deleted successfully!`,
  entityDeleted: (entityName: string) => `${entityName} deleted successfully!`,
  entitySaved: (entityName: string) => `${entityName} saved successfully!`,
  confirmDelete: (entityName: string, identifier: string) => 
    `Are you sure you want to delete ${entityName} "${identifier}"?`,
};
