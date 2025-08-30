// Common types for UI components

import { ChipProps } from '@mui/material/Chip';

// Standardized Chip color types
export type ChipColorType = 
  | 'default'
  | 'primary'
  | 'secondary'
  | 'error'
  | 'info'
  | 'success'
  | 'warning';

// Status-based chip color mapping
export const STATUS_CHIP_COLORS: Record<string, ChipColorType> = {
  // Common status colors
  active: 'success',
  inactive: 'error',
  pending: 'warning',
  draft: 'default',
  completed: 'success',
  cancelled: 'error',
  approved: 'success',
  rejected: 'error',
  
  // Voucher status colors
  open: 'info',
  closed: 'success',
  partial: 'warning',
  
  // Payment status colors
  paid: 'success',
  unpaid: 'error',
  overdue: 'warning',
  
  // Quality status colors
  passed: 'success',
  failed: 'error',
  'under-review': 'warning',
} as const;

// Enhanced Chip props with standardized colors
export interface StandardChipProps extends Omit<ChipProps, 'color'> {
  color?: ChipColorType;
  status?: keyof typeof STATUS_CHIP_COLORS;
}

// Common table cell props
export interface TableCellConfig {
  width?: string;
  minWidth?: string;
  fontSize?: number;
  fontWeight?: string | number;
  padding?: string;
  textAlign?: 'left' | 'center' | 'right';
}

// Voucher form field types
export interface VoucherFieldProps {
  label: string;
  required?: boolean;
  disabled?: boolean;
  size?: 'small' | 'medium';
  fullWidth?: boolean;
  error?: boolean;
  helperText?: string;
}

// Grid size props for consistent layouts
export type GridSize = boolean | 'auto' | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;

export interface ResponsiveGridSize {
  xs?: GridSize;
  sm?: GridSize;
  md?: GridSize;
  lg?: GridSize;
  xl?: GridSize;
}