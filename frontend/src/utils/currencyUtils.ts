/**
 * Format currency based on organization settings
 * Defaults to INR (₹) for Indian organizations
 * @param amount - The amount to format
 * @param currency - Optional currency code (defaults to INR)
 * @param locale - Optional locale for formatting (defaults to en-IN)
 */
export const formatCurrency = (
  amount: number,
  currency: string = "INR",
  locale: string = "en-IN"
): string => {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency: currency,
  }).format(amount);
};

/**
 * Get currency symbol based on currency code
 * @param currency - Currency code (ISO 4217)
 */
export const getCurrencySymbol = (currency: string = "INR"): string => {
  const symbols: { [key: string]: string } = {
    INR: "₹",
    USD: "$",
    EUR: "€",
    GBP: "£",
    JPY: "¥",
    AUD: "A$",
    CAD: "C$",
    CHF: "Fr",
  };
  return symbols[currency] || currency;
};