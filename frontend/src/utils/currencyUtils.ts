/**
 * Currency utility functions for consistent currency formatting across the application
 * Supports organization-specific currency and dynamic locale handling
 */

// Currency metadata with locale information
const CURRENCY_CONFIG: Record<string, { symbol: string; locale: string; decimals: number }> = {
  INR: { symbol: "₹", locale: "en-IN", decimals: 2 },
  USD: { symbol: "$", locale: "en-US", decimals: 2 },
  EUR: { symbol: "€", locale: "de-DE", decimals: 2 },
  GBP: { symbol: "£", locale: "en-GB", decimals: 2 },
  JPY: { symbol: "¥", locale: "ja-JP", decimals: 0 },
  AUD: { symbol: "A$", locale: "en-AU", decimals: 2 },
  CAD: { symbol: "C$", locale: "en-CA", decimals: 2 },
  CHF: { symbol: "Fr", locale: "de-CH", decimals: 2 },
  CNY: { symbol: "¥", locale: "zh-CN", decimals: 2 },
  SAR: { symbol: "ر.س", locale: "ar-SA", decimals: 2 },
  AED: { symbol: "د.إ", locale: "ar-AE", decimals: 2 },
  ZAR: { symbol: "R", locale: "en-ZA", decimals: 2 },
  MXN: { symbol: "$", locale: "es-MX", decimals: 2 },
  BRL: { symbol: "R$", locale: "pt-BR", decimals: 2 },
  RUB: { symbol: "₽", locale: "ru-RU", decimals: 2 },
};

// Default currency for the application
const DEFAULT_CURRENCY = "INR";
const DEFAULT_LOCALE = "en-IN";

/**
 * Format currency based on organization settings
 * @param amount - The amount to format
 * @param currency - Optional currency code (defaults to INR)
 * @param locale - Optional locale for formatting (auto-detected from currency if not provided)
 */
export const formatCurrency = (
  amount: number,
  currency: string = DEFAULT_CURRENCY,
  locale?: string
): string => {
  const config = CURRENCY_CONFIG[currency] || CURRENCY_CONFIG[DEFAULT_CURRENCY];
  const finalLocale = locale || config.locale;
  
  try {
    return new Intl.NumberFormat(finalLocale, {
      style: "currency",
      currency: currency,
      minimumFractionDigits: config.decimals,
      maximumFractionDigits: config.decimals,
    }).format(amount);
  } catch (error) {
    // Log error for debugging in development
    if (process.env.NODE_ENV === "development") {
      console.warn(`Currency formatting failed for ${currency}:`, error);
    }
    // Fallback for unsupported currencies
    const symbol = getCurrencySymbol(currency);
    return `${symbol}${amount.toLocaleString(DEFAULT_LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
};

/**
 * Format currency with compact notation for large numbers (e.g., 1.5K, 2.3M)
 * @param amount - The amount to format
 * @param currency - Optional currency code (defaults to INR)
 */
export const formatCurrencyCompact = (
  amount: number,
  currency: string = DEFAULT_CURRENCY
): string => {
  const config = CURRENCY_CONFIG[currency] || CURRENCY_CONFIG[DEFAULT_CURRENCY];
  
  try {
    return new Intl.NumberFormat(config.locale, {
      style: "currency",
      currency: currency,
      notation: "compact",
      compactDisplay: "short",
    }).format(amount);
  } catch {
    const symbol = getCurrencySymbol(currency);
    if (amount >= 1000000) {
      return `${symbol}${(amount / 1000000).toFixed(1)}M`;
    }
    if (amount >= 1000) {
      return `${symbol}${(amount / 1000).toFixed(1)}K`;
    }
    return `${symbol}${amount.toFixed(2)}`;
  }
};

/**
 * Get currency symbol based on currency code
 * @param currency - Currency code (ISO 4217)
 */
export const getCurrencySymbol = (currency: string = DEFAULT_CURRENCY): string => {
  return CURRENCY_CONFIG[currency]?.symbol || currency;
};

/**
 * Get the default locale for a currency
 * @param currency - Currency code (ISO 4217)
 */
export const getCurrencyLocale = (currency: string = DEFAULT_CURRENCY): string => {
  return CURRENCY_CONFIG[currency]?.locale || DEFAULT_LOCALE;
};

/**
 * Get list of supported currencies
 */
export const getSupportedCurrencies = (): Array<{ code: string; symbol: string }> => {
  return Object.entries(CURRENCY_CONFIG).map(([code, config]) => ({
    code,
    symbol: config.symbol,
  }));
};

/**
 * Validate if a currency code is supported
 * @param currency - Currency code to validate
 */
export const isCurrencySupported = (currency: string): boolean => {
  return currency in CURRENCY_CONFIG;
};

/**
 * Format amount with just the symbol (no Intl formatting)
 * Useful for simple display without locale-specific formatting
 * @param amount - The amount to format
 * @param currency - Optional currency code (defaults to INR)
 */
export const formatAmountWithSymbol = (
  amount: number,
  currency: string = DEFAULT_CURRENCY
): string => {
  const symbol = getCurrencySymbol(currency);
  const config = CURRENCY_CONFIG[currency] || CURRENCY_CONFIG[DEFAULT_CURRENCY];
  const formattedAmount = amount.toLocaleString(config.locale, {
    minimumFractionDigits: config.decimals,
    maximumFractionDigits: config.decimals,
  });
  return `${symbol}${formattedAmount}`;
};