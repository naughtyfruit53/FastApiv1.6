// UI Constants for consistent styling across the application

export const UI_CONSTANTS = {
  // Input field heights
  INPUT_HEIGHT: {
    SMALL: 27,
    MEDIUM: 40,
    LARGE: 56,
  },
  
  // Common spacing values
  SPACING: {
    XS: 4,
    SM: 8,
    MD: 16,
    LG: 24,
    XL: 32,
  },
  
  // Common breakpoints
  BREAKPOINTS: {
    XS: 600,
    SM: 900,
    MD: 1200,
    LG: 1536,
  },
  
  // Common font sizes
  FONT_SIZE: {
    XS: '0.75rem',    // 12px
    SM: '0.875rem',   // 14px
    MD: '1rem',       // 16px
    LG: '1.125rem',   // 18px
    XL: '1.25rem',    // 20px
  },
  
  // Common component widths
  WIDTH: {
    DROPDOWN_MIN: 180,
    REFERENCE_MIN: 230,
    VOUCHER_MIN: 200,
    FIELD_MIN: 70,
  },
} as const;

// Type for UI constants
export type UIConstants = typeof UI_CONSTANTS;

// Common sx styles for reuse
export const COMMON_STYLES = {
  smallInput: {
    '& .MuiInputBase-root': { 
      height: UI_CONSTANTS.INPUT_HEIGHT.SMALL 
    }
  },
  
  centeredText: {
    textAlign: 'center' as const,
  },
  
  boldText: {
    fontWeight: 'bold',
  },
  
  // Dropdown styles from voucherUtils
  voucherDropdown: {
    minWidth: UI_CONSTANTS.WIDTH.VOUCHER_MIN,
    '& .MuiSelect-select': {
      minWidth: UI_CONSTANTS.WIDTH.VOUCHER_MIN - 20,
      textOverflow: 'ellipsis',
      overflow: 'hidden',
      whiteSpace: 'nowrap'
    }
  },
  
  referenceDropdown: {
    minWidth: UI_CONSTANTS.WIDTH.REFERENCE_MIN,
    '& .MuiSelect-select': {
      minWidth: UI_CONSTANTS.WIDTH.REFERENCE_MIN - 20,
      textOverflow: 'ellipsis',
      overflow: 'hidden',
      whiteSpace: 'nowrap'
    }
  },
} as const;