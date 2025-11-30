/**
 * useCurrency Hook
 * 
 * Provides consistent currency formatting across the application.
 * Uses organization settings when available, with INR as default.
 * 
 * This hook ensures no hardcoded $ or ₹ symbols are used directly in components.
 */

import { useCallback, useMemo } from 'react';
import { formatCurrency as formatCurrencyUtil, getCurrencySymbol } from '../utils/currencyUtils';
import { useAuth } from '../context/AuthContext';

export interface CurrencyConfig {
  currencyCode: string;
  locale: string;
  symbol: string;
}

export interface UseCurrencyReturn {
  /** Format an amount using organization's currency settings */
  formatCurrency: (amount: number) => string;
  /** Format an amount with a specific currency override */
  formatWithCurrency: (amount: number, currencyCode?: string) => string;
  /** Get the currency symbol for the organization */
  currencySymbol: string;
  /** Get the currency code for the organization */
  currencyCode: string;
  /** Currency configuration */
  config: CurrencyConfig;
}

/**
 * Hook for consistent currency formatting across the application
 * 
 * @example
 * ```tsx
 * const { formatCurrency, currencySymbol } = useCurrency();
 * 
 * // Format amount using org currency
 * <span>{formatCurrency(1000)}</span> // ₹1,000.00
 * 
 * // Access currency symbol
 * <span>{currencySymbol} 1,000</span> // ₹ 1,000
 * ```
 */
export function useCurrency(): UseCurrencyReturn {
  const { user } = useAuth();
  
  // Get currency settings from organization or use defaults
  // Note: currency and locale can be stored in organization settings
  // Falls back to INR/en-IN if not available
  const config = useMemo<CurrencyConfig>(() => {
    // Check user's organization settings for currency preference
    // The organization may have settings nested or directly on the object
    const orgSettings = (user as any)?.organization?.settings || (user as any)?.organization;
    const orgCurrency = orgSettings?.currency || 'INR';
    const orgLocale = orgSettings?.locale || 'en-IN';
    
    return {
      currencyCode: orgCurrency,
      locale: orgLocale,
      symbol: getCurrencySymbol(orgCurrency),
    };
  }, [user]);
  
  // Format currency using organization settings
  const formatCurrency = useCallback((amount: number): string => {
    if (amount === null || amount === undefined || isNaN(amount)) {
      return formatCurrencyUtil(0, config.currencyCode, config.locale);
    }
    return formatCurrencyUtil(amount, config.currencyCode, config.locale);
  }, [config.currencyCode, config.locale]);
  
  // Format with explicit currency override
  const formatWithCurrency = useCallback((amount: number, currencyCode?: string): string => {
    const code = currencyCode || config.currencyCode;
    const locale = currencyCode === 'USD' ? 'en-US' : 
                   currencyCode === 'EUR' ? 'de-DE' : 
                   currencyCode === 'GBP' ? 'en-GB' : 
                   config.locale;
    
    if (amount === null || amount === undefined || isNaN(amount)) {
      return formatCurrencyUtil(0, code, locale);
    }
    return formatCurrencyUtil(amount, code, locale);
  }, [config.currencyCode, config.locale]);
  
  return {
    formatCurrency,
    formatWithCurrency,
    currencySymbol: config.symbol,
    currencyCode: config.currencyCode,
    config,
  };
}

/**
 * Standalone utility for formatting currency outside of React components
 * Uses default INR currency when organization context is not available
 * 
 * @param amount - The amount to format
 * @param currencyCode - Optional currency code (defaults to INR)
 * @param locale - Optional locale (defaults to en-IN)
 */
export function formatAmount(
  amount: number,
  currencyCode: string = 'INR',
  locale: string = 'en-IN'
): string {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return formatCurrencyUtil(0, currencyCode, locale);
  }
  return formatCurrencyUtil(amount, currencyCode, locale);
}

/**
 * Format amount as Indian currency (₹)
 * Convenience function for INR formatting
 */
export function formatINR(amount: number): string {
  return formatAmount(amount, 'INR', 'en-IN');
}

/**
 * Format amount as US Dollar ($)
 * Convenience function for USD formatting
 */
export function formatUSD(amount: number): string {
  return formatAmount(amount, 'USD', 'en-US');
}

export default useCurrency;
