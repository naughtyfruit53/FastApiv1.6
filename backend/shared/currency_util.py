"""
Currency utilities for multi-currency support
Provides currency conversion, formatting, and exchange rate management
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import json

logger = logging.getLogger(__name__)


class CurrencyManager:
    """
    Multi-currency support with conversion and formatting.
    """
    
    # ISO 4217 currency codes with metadata
    CURRENCIES = {
        "USD": {
            "name": "US Dollar",
            "symbol": "$",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": ",",
            "decimal_separator": "."
        },
        "EUR": {
            "name": "Euro",
            "symbol": "€",
            "decimal_places": 2,
            "symbol_position": "after",
            "thousands_separator": ".",
            "decimal_separator": ","
        },
        "GBP": {
            "name": "British Pound",
            "symbol": "£",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": ",",
            "decimal_separator": "."
        },
        "JPY": {
            "name": "Japanese Yen",
            "symbol": "¥",
            "decimal_places": 0,
            "symbol_position": "before",
            "thousands_separator": ",",
            "decimal_separator": "."
        },
        "CNY": {
            "name": "Chinese Yuan",
            "symbol": "¥",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": ",",
            "decimal_separator": "."
        },
        "INR": {
            "name": "Indian Rupee",
            "symbol": "₹",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": ",",
            "decimal_separator": "."
        },
        "AUD": {
            "name": "Australian Dollar",
            "symbol": "A$",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": ",",
            "decimal_separator": "."
        },
        "CAD": {
            "name": "Canadian Dollar",
            "symbol": "C$",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": ",",
            "decimal_separator": "."
        },
        "CHF": {
            "name": "Swiss Franc",
            "symbol": "CHF",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": "'",
            "decimal_separator": "."
        },
        "BRL": {
            "name": "Brazilian Real",
            "symbol": "R$",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": ".",
            "decimal_separator": ","
        },
        "RUB": {
            "name": "Russian Ruble",
            "symbol": "₽",
            "decimal_places": 2,
            "symbol_position": "after",
            "thousands_separator": " ",
            "decimal_separator": ","
        },
        "SAR": {
            "name": "Saudi Riyal",
            "symbol": "ر.س",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": ",",
            "decimal_separator": "."
        },
        "AED": {
            "name": "UAE Dirham",
            "symbol": "د.إ",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": ",",
            "decimal_separator": "."
        },
        "ZAR": {
            "name": "South African Rand",
            "symbol": "R",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": " ",
            "decimal_separator": ","
        },
        "MXN": {
            "name": "Mexican Peso",
            "symbol": "$",
            "decimal_places": 2,
            "symbol_position": "before",
            "thousands_separator": ",",
            "decimal_separator": "."
        },
    }
    
    DEFAULT_CURRENCY = "USD"
    
    def __init__(self):
        """Initialize currency manager"""
        self._exchange_rates: Dict[str, Dict[str, float]] = {}
        self._exchange_rates_updated_at: Optional[datetime] = None
        self._cache_duration = timedelta(hours=24)  # Cache exchange rates for 24 hours
    
    def get_supported_currencies(self) -> List[Dict[str, Any]]:
        """
        Get list of supported currencies with metadata.
        
        Returns:
            List of currency dictionaries
        """
        return [
            {
                "code": code,
                **info
            }
            for code, info in self.CURRENCIES.items()
        ]
    
    def is_currency_supported(self, currency_code: str) -> bool:
        """
        Check if a currency is supported.
        
        Args:
            currency_code: ISO 4217 currency code
            
        Returns:
            True if currency is supported, False otherwise
        """
        return currency_code.upper() in self.CURRENCIES
    
    def get_currency_info(self, currency_code: str) -> Dict[str, Any]:
        """
        Get currency metadata.
        
        Args:
            currency_code: ISO 4217 currency code
            
        Returns:
            Dictionary with currency information
        """
        return self.CURRENCIES.get(
            currency_code.upper(), 
            self.CURRENCIES[self.DEFAULT_CURRENCY]
        )
    
    def format_amount(
        self, 
        amount: float, 
        currency_code: str = DEFAULT_CURRENCY,
        include_symbol: bool = True,
        include_code: bool = False
    ) -> str:
        """
        Format amount according to currency conventions.
        
        Args:
            amount: Amount to format
            currency_code: ISO 4217 currency code
            include_symbol: Whether to include currency symbol
            include_code: Whether to include currency code
            
        Returns:
            Formatted amount string
        """
        currency_code = currency_code.upper()
        currency_info = self.get_currency_info(currency_code)
        
        # Convert to Decimal for precise calculation
        amount_decimal = Decimal(str(amount))
        
        # Round to appropriate decimal places
        decimal_places = currency_info["decimal_places"]
        rounded = amount_decimal.quantize(
            Decimal(10) ** -decimal_places, 
            rounding=ROUND_HALF_UP
        )
        
        # Format with thousands separator
        amount_str = f"{rounded:,.{decimal_places}f}"
        
        # Replace separators according to currency
        thousands_sep = currency_info["thousands_separator"]
        decimal_sep = currency_info["decimal_separator"]
        
        if thousands_sep != "," or decimal_sep != ".":
            # Convert from default format
            amount_str = amount_str.replace(",", "TEMP")
            amount_str = amount_str.replace(".", decimal_sep)
            amount_str = amount_str.replace("TEMP", thousands_sep)
        
        # Add currency symbol
        if include_symbol:
            symbol = currency_info["symbol"]
            if currency_info["symbol_position"] == "before":
                amount_str = f"{symbol}{amount_str}"
            else:
                amount_str = f"{amount_str} {symbol}"
        
        # Add currency code
        if include_code:
            amount_str = f"{amount_str} {currency_code}"
        
        return amount_str
    
    def parse_amount(self, amount_str: str, currency_code: str = DEFAULT_CURRENCY) -> float:
        """
        Parse formatted amount string to float.
        
        Args:
            amount_str: Formatted amount string
            currency_code: ISO 4217 currency code
            
        Returns:
            Parsed amount as float
        """
        currency_info = self.get_currency_info(currency_code.upper())
        
        # Remove currency symbol and code
        cleaned = amount_str.strip()
        cleaned = cleaned.replace(currency_info["symbol"], "")
        cleaned = cleaned.replace(currency_code.upper(), "")
        
        # Remove thousands separators
        thousands_sep = currency_info["thousands_separator"]
        cleaned = cleaned.replace(thousands_sep, "")
        
        # Convert decimal separator to standard
        decimal_sep = currency_info["decimal_separator"]
        if decimal_sep != ".":
            cleaned = cleaned.replace(decimal_sep, ".")
        
        try:
            return float(cleaned.strip())
        except ValueError as e:
            logger.error(f"Failed to parse amount: {amount_str} - {str(e)}")
            return 0.0
    
    def set_exchange_rates(self, base_currency: str, rates: Dict[str, float]):
        """
        Set exchange rates for a base currency.
        
        Args:
            base_currency: Base currency code
            rates: Dictionary of currency_code -> exchange_rate
        """
        self._exchange_rates[base_currency.upper()] = rates
        self._exchange_rates_updated_at = datetime.utcnow()
    
    def get_exchange_rate(
        self, 
        from_currency: str, 
        to_currency: str,
        default_rate: float = 1.0
    ) -> float:
        """
        Get exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            default_rate: Default rate if not found
            
        Returns:
            Exchange rate
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Same currency
        if from_currency == to_currency:
            return 1.0
        
        # Check if we have rates for source currency
        if from_currency in self._exchange_rates:
            rates = self._exchange_rates[from_currency]
            if to_currency in rates:
                return rates[to_currency]
        
        # Try reverse conversion
        if to_currency in self._exchange_rates:
            rates = self._exchange_rates[to_currency]
            if from_currency in rates:
                return 1.0 / rates[from_currency]
        
        logger.warning(
            f"Exchange rate not found: {from_currency} -> {to_currency}, using default: {default_rate}"
        )
        return default_rate
    
    def convert(
        self, 
        amount: float, 
        from_currency: str, 
        to_currency: str,
        round_result: bool = True
    ) -> float:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            round_result: Whether to round to target currency's decimal places
            
        Returns:
            Converted amount
        """
        exchange_rate = self.get_exchange_rate(from_currency, to_currency)
        converted = amount * exchange_rate
        
        if round_result:
            currency_info = self.get_currency_info(to_currency)
            decimal_places = currency_info["decimal_places"]
            converted = round(converted, decimal_places)
        
        return converted
    
    def convert_and_format(
        self, 
        amount: float, 
        from_currency: str, 
        to_currency: str,
        include_symbol: bool = True,
        include_code: bool = False
    ) -> str:
        """
        Convert and format amount in one operation.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            include_symbol: Whether to include currency symbol
            include_code: Whether to include currency code
            
        Returns:
            Formatted converted amount
        """
        converted = self.convert(amount, from_currency, to_currency)
        return self.format_amount(converted, to_currency, include_symbol, include_code)
    
    def is_exchange_rates_stale(self) -> bool:
        """
        Check if cached exchange rates are stale.
        
        Returns:
            True if rates need to be updated
        """
        if not self._exchange_rates_updated_at:
            return True
        
        age = datetime.utcnow() - self._exchange_rates_updated_at
        return age > self._cache_duration
    
    def get_exchange_rates_age(self) -> Optional[timedelta]:
        """
        Get age of cached exchange rates.
        
        Returns:
            Timedelta representing age, or None if no rates cached
        """
        if not self._exchange_rates_updated_at:
            return None
        
        return datetime.utcnow() - self._exchange_rates_updated_at


# Singleton instance
_currency_manager = None


def get_currency_manager() -> CurrencyManager:
    """
    Get singleton instance of CurrencyManager.
    
    Returns:
        CurrencyManager instance
    """
    global _currency_manager
    if _currency_manager is None:
        _currency_manager = CurrencyManager()
    return _currency_manager


# Convenience functions
def format_amount(amount: float, currency_code: str = "USD", include_symbol: bool = True) -> str:
    """Format an amount in a specific currency"""
    return get_currency_manager().format_amount(amount, currency_code, include_symbol)


def convert(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert amount between currencies"""
    return get_currency_manager().convert(amount, from_currency, to_currency)


def convert_and_format(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert and format amount"""
    return get_currency_manager().convert_and_format(amount, from_currency, to_currency)
