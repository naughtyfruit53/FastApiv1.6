"""
Localization utilities for multi-language support
Provides translation, formatting, and language detection capabilities
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LocalizationManager:
    """
    Centralized localization management for multi-language support.
    Handles translations, date/time formatting, and number formatting.
    """
    
    DEFAULT_LANGUAGE = "en"
    SUPPORTED_LANGUAGES = {
        "en": {"name": "English", "native_name": "English", "direction": "ltr", "currency": "USD"},
        "es": {"name": "Spanish", "native_name": "Español", "direction": "ltr", "currency": "EUR"},
        "fr": {"name": "French", "native_name": "Français", "direction": "ltr", "currency": "EUR"},
        "de": {"name": "German", "native_name": "Deutsch", "direction": "ltr", "currency": "EUR"},
        "zh": {"name": "Chinese", "native_name": "中文", "direction": "ltr", "currency": "CNY"},
        "ja": {"name": "Japanese", "native_name": "日本語", "direction": "ltr", "currency": "JPY"},
        "ar": {"name": "Arabic", "native_name": "العربية", "direction": "rtl", "currency": "SAR"},
        "hi": {"name": "Hindi", "native_name": "हिन्दी", "direction": "ltr", "currency": "INR"},
        "pt": {"name": "Portuguese", "native_name": "Português", "direction": "ltr", "currency": "BRL"},
        "ru": {"name": "Russian", "native_name": "Русский", "direction": "ltr", "currency": "RUB"},
    }
    
    def __init__(self, locale_path: Optional[str] = None):
        """
        Initialize localization manager.
        
        Args:
            locale_path: Path to locale files directory. If None, uses default app/locales
        """
        self.locale_path = locale_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "app", 
            "locales"
        )
        self._translations_cache: Dict[str, Dict[str, str]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files from locale directory"""
        locale_dir = Path(self.locale_path)
        
        if not locale_dir.exists():
            logger.warning(f"Locale directory not found: {self.locale_path}")
            return
        
        for locale_file in locale_dir.glob("*.json"):
            lang_code = locale_file.stem
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self._translations_cache[lang_code] = json.load(f)
                logger.info(f"Loaded translations for language: {lang_code}")
            except Exception as e:
                logger.error(f"Failed to load translations for {lang_code}: {str(e)}")
    
    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """
        Get list of supported languages with metadata.
        
        Returns:
            List of language dictionaries with code, name, native_name, etc.
        """
        return [
            {
                "code": code,
                **info
            }
            for code, info in self.SUPPORTED_LANGUAGES.items()
        ]
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            True if language is supported, False otherwise
        """
        return language_code in self.SUPPORTED_LANGUAGES
    
    def get_language_info(self, language_code: str) -> Dict[str, Any]:
        """
        Get language metadata.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            Dictionary with language information
        """
        return self.SUPPORTED_LANGUAGES.get(
            language_code, 
            self.SUPPORTED_LANGUAGES[self.DEFAULT_LANGUAGE]
        )
    
    def translate(
        self, 
        key: str, 
        language_code: str = DEFAULT_LANGUAGE, 
        fallback: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Translate a key to the specified language.
        
        Args:
            key: Translation key (dot notation supported, e.g., "user.welcome")
            language_code: Target language code
            fallback: Fallback text if translation not found
            **kwargs: Variables for string interpolation
            
        Returns:
            Translated string
        """
        # Get translations for language
        translations = self._translations_cache.get(
            language_code, 
            self._translations_cache.get(self.DEFAULT_LANGUAGE, {})
        )
        
        # Support dot notation for nested keys
        value = translations
        for part in key.split('.'):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        
        # Use fallback if translation not found
        if value is None:
            value = fallback or key
        
        # Convert to string
        result = str(value)
        
        # Perform string interpolation if kwargs provided
        if kwargs:
            try:
                result = result.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing interpolation variable: {e}")
        
        return result
    
    def format_date(
        self, 
        date_obj: date, 
        language_code: str = DEFAULT_LANGUAGE,
        format_style: str = "medium"
    ) -> str:
        """
        Format date according to locale.
        
        Args:
            date_obj: Date object to format
            language_code: Target language code
            format_style: Format style (short, medium, long, full)
            
        Returns:
            Formatted date string
        """
        # Simple formatting - can be enhanced with babel/pytz
        if format_style == "short":
            return date_obj.strftime("%m/%d/%Y")
        elif format_style == "long":
            return date_obj.strftime("%B %d, %Y")
        elif format_style == "full":
            return date_obj.strftime("%A, %B %d, %Y")
        else:  # medium
            return date_obj.strftime("%b %d, %Y")
    
    def format_datetime(
        self, 
        datetime_obj: datetime, 
        language_code: str = DEFAULT_LANGUAGE,
        format_style: str = "medium",
        include_timezone: bool = False
    ) -> str:
        """
        Format datetime according to locale.
        
        Args:
            datetime_obj: Datetime object to format
            language_code: Target language code
            format_style: Format style (short, medium, long, full)
            include_timezone: Whether to include timezone
            
        Returns:
            Formatted datetime string
        """
        # Simple formatting - can be enhanced with babel/pytz
        if format_style == "short":
            fmt = "%m/%d/%Y %H:%M"
        elif format_style == "long":
            fmt = "%B %d, %Y %I:%M %p"
        elif format_style == "full":
            fmt = "%A, %B %d, %Y %I:%M:%S %p"
        else:  # medium
            fmt = "%b %d, %Y %H:%M"
        
        if include_timezone and datetime_obj.tzinfo:
            fmt += " %Z"
        
        return datetime_obj.strftime(fmt)
    
    def format_number(
        self, 
        number: float, 
        language_code: str = DEFAULT_LANGUAGE,
        decimal_places: int = 2
    ) -> str:
        """
        Format number according to locale.
        
        Args:
            number: Number to format
            language_code: Target language code
            decimal_places: Number of decimal places
            
        Returns:
            Formatted number string
        """
        # Simple formatting - can be enhanced with babel
        if language_code in ["de", "fr", "es", "pt"]:
            # European format: 1.234.567,89
            formatted = f"{number:,.{decimal_places}f}"
            return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            # Default format: 1,234,567.89
            return f"{number:,.{decimal_places}f}"
    
    def detect_language(self, accept_language_header: Optional[str]) -> str:
        """
        Detect preferred language from HTTP Accept-Language header.
        
        Args:
            accept_language_header: HTTP Accept-Language header value
            
        Returns:
            Detected language code or default language
        """
        if not accept_language_header:
            return self.DEFAULT_LANGUAGE
        
        # Parse Accept-Language header (simplified)
        # Format: "en-US,en;q=0.9,es;q=0.8"
        languages = []
        for lang in accept_language_header.split(','):
            parts = lang.strip().split(';')
            code = parts[0].split('-')[0].lower()
            quality = 1.0
            if len(parts) > 1 and parts[1].startswith('q='):
                try:
                    quality = float(parts[1][2:])
                except ValueError:
                    pass
            languages.append((code, quality))
        
        # Sort by quality and find first supported language
        languages.sort(key=lambda x: x[1], reverse=True)
        for code, _ in languages:
            if self.is_language_supported(code):
                return code
        
        return self.DEFAULT_LANGUAGE
    
    def get_text_direction(self, language_code: str = DEFAULT_LANGUAGE) -> str:
        """
        Get text direction for a language.
        
        Args:
            language_code: Language code
            
        Returns:
            "ltr" or "rtl"
        """
        lang_info = self.get_language_info(language_code)
        return lang_info.get("direction", "ltr")


# Singleton instance
_localization_manager = None


def get_localization_manager(locale_path: Optional[str] = None) -> LocalizationManager:
    """
    Get singleton instance of LocalizationManager.
    
    Args:
        locale_path: Optional path to locale files
        
    Returns:
        LocalizationManager instance
    """
    global _localization_manager
    if _localization_manager is None:
        _localization_manager = LocalizationManager(locale_path)
    return _localization_manager


# Convenience functions
def translate(key: str, language_code: str = "en", **kwargs) -> str:
    """Translate a key"""
    return get_localization_manager().translate(key, language_code, **kwargs)


def format_date(date_obj: date, language_code: str = "en", format_style: str = "medium") -> str:
    """Format a date"""
    return get_localization_manager().format_date(date_obj, language_code, format_style)


def format_datetime(datetime_obj: datetime, language_code: str = "en", format_style: str = "medium") -> str:
    """Format a datetime"""
    return get_localization_manager().format_datetime(datetime_obj, language_code, format_style)


def format_number(number: float, language_code: str = "en", decimal_places: int = 2) -> str:
    """Format a number"""
    return get_localization_manager().format_number(number, language_code, decimal_places)
