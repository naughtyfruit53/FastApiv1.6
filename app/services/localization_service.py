"""
Localization Service for Multi-language Support
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from babel import Locale, dates, numbers
from babel.core import UnknownLocaleError
import pytz

from app.core.tenant_config import TenantConfig


class LocalizationService:
    """Service for handling multi-language localization and internationalization"""
    
    def __init__(self):
        self.config = TenantConfig.get_localization_config()
        self.supported_languages = self.config["supported_languages"]
        self.default_language = self.config["default_language"]
        self.fallback_language = self.config["fallback_language"]
        self._translations_cache = {}
    
    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """Get list of supported languages with metadata"""
        languages = []
        for code, config in self.supported_languages.items():
            languages.append({
                "code": code,
                "name": config["name"],
                "native_name": config["native_name"],
                "direction": config["direction"],
                "currency_code": config["currency_code"]
            })
        return languages
    
    def get_language_config(self, language_code: str) -> Dict[str, Any]:
        """Get configuration for a specific language"""
        return TenantConfig.get_language_config(language_code)
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported"""
        return language_code in self.supported_languages
    
    def detect_language_from_request(self, accept_language: str) -> str:
        """Detect preferred language from HTTP Accept-Language header"""
        if not accept_language or not self.config["auto_detect_language"]:
            return self.default_language
        
        # Parse Accept-Language header (simplified)
        languages = []
        for lang_range in accept_language.split(','):
            parts = lang_range.strip().split(';')
            lang = parts[0].strip()
            quality = 1.0
            
            if len(parts) > 1 and parts[1].strip().startswith('q='):
                try:
                    quality = float(parts[1].strip()[2:])
                except ValueError:
                    quality = 1.0
            
            # Extract language code (e.g., 'en' from 'en-US')
            lang_code = lang.split('-')[0].lower()
            if self.is_language_supported(lang_code):
                languages.append((lang_code, quality))
        
        # Sort by quality and return best match
        if languages:
            languages.sort(key=lambda x: x[1], reverse=True)
            return languages[0][0]
        
        return self.default_language
    
    def translate(self, key: str, language_code: str = None, **kwargs) -> str:
        """Translate a key to the specified language"""
        if language_code is None:
            language_code = self.default_language
        
        # Load translations for the language
        translations = self._get_translations(language_code)
        
        # Get translation or fallback
        text = translations.get(key)
        if text is None:
            # Try fallback language
            fallback_translations = self._get_translations(self.fallback_language)
            text = fallback_translations.get(key, key)
        
        # Format with parameters if provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass  # Return unformatted text if formatting fails
        
        return text
    
    def format_date(self, date: datetime, language_code: str = None, format_type: str = "medium") -> str:
        """Format a date according to language conventions"""
        if language_code is None:
            language_code = self.default_language
        
        lang_config = self.get_language_config(language_code)
        
        try:
            locale = Locale(language_code)
            
            # Convert to timezone
            timezone = pytz.timezone(lang_config.get("timezone", "UTC"))
            localized_date = date.astimezone(timezone)
            
            return dates.format_date(localized_date, format=format_type, locale=locale)
        except (UnknownLocaleError, pytz.exceptions.UnknownTimeZoneError):
            # Fallback to default format
            return date.strftime(lang_config.get("date_format", "%Y-%m-%d"))
    
    def format_datetime(self, datetime_obj: datetime, language_code: str = None, format_type: str = "medium") -> str:
        """Format a datetime according to language conventions"""
        if language_code is None:
            language_code = self.default_language
        
        lang_config = self.get_language_config(language_code)
        
        try:
            locale = Locale(language_code)
            
            # Convert to timezone
            timezone = pytz.timezone(lang_config.get("timezone", "UTC"))
            localized_datetime = datetime_obj.astimezone(timezone)
            
            return dates.format_datetime(localized_datetime, format=format_type, locale=locale)
        except (UnknownLocaleError, pytz.exceptions.UnknownTimeZoneError):
            # Fallback to default format
            date_format = lang_config.get("date_format", "%Y-%m-%d")
            time_format = lang_config.get("time_format", "%H:%M")
            return datetime_obj.strftime(f"{date_format} {time_format}")
    
    def format_currency(self, amount: float, language_code: str = None, currency_code: str = None) -> str:
        """Format currency according to language conventions"""
        if language_code is None:
            language_code = self.default_language
        
        lang_config = self.get_language_config(language_code)
        
        if currency_code is None:
            currency_code = lang_config.get("currency_code", "USD")
        
        try:
            locale = Locale(language_code)
            return numbers.format_currency(amount, currency_code, locale=locale)
        except UnknownLocaleError:
            # Fallback to simple format
            return f"{currency_code} {amount:,.2f}"
    
    def format_number(self, number: float, language_code: str = None) -> str:
        """Format number according to language conventions"""
        if language_code is None:
            language_code = self.default_language
        
        try:
            locale = Locale(language_code)
            return numbers.format_number(number, locale=locale)
        except UnknownLocaleError:
            # Fallback to default format
            return f"{number:,.2f}"
    
    def format_percentage(self, percentage: float, language_code: str = None) -> str:
        """Format percentage according to language conventions"""
        if language_code is None:
            language_code = self.default_language
        
        try:
            locale = Locale(language_code)
            return numbers.format_percent(percentage / 100, locale=locale)
        except UnknownLocaleError:
            # Fallback to default format
            return f"{percentage:.1f}%"
    
    def get_timezone(self, language_code: str = None) -> str:
        """Get timezone for a language"""
        if language_code is None:
            language_code = self.default_language
        
        lang_config = self.get_language_config(language_code)
        return lang_config.get("timezone", "UTC")
    
    def get_text_direction(self, language_code: str = None) -> str:
        """Get text direction (ltr or rtl) for a language"""
        if language_code is None:
            language_code = self.default_language
        
        lang_config = self.get_language_config(language_code)
        return lang_config.get("direction", "ltr")
    
    def localize_ai_insights(self, insight: Dict[str, Any], language_code: str = None) -> Dict[str, Any]:
        """Localize AI insights and recommendations"""
        if language_code is None:
            language_code = self.default_language
        
        localized_insight = insight.copy()
        
        # Translate insight type and category
        localized_insight["insight_type"] = self.translate(
            f"ai.insight_type.{insight['insight_type']}", 
            language_code
        )
        localized_insight["category"] = self.translate(
            f"ai.category.{insight['category']}", 
            language_code
        )
        localized_insight["priority"] = self.translate(
            f"ai.priority.{insight['priority']}", 
            language_code
        )
        
        # Format monetary values
        if "potential_impact_value" in insight and insight["potential_impact_value"]:
            localized_insight["potential_impact_value_formatted"] = self.format_currency(
                insight["potential_impact_value"], 
                language_code
            )
        
        # Format dates
        if "created_at" in insight:
            localized_insight["created_at_formatted"] = self.format_datetime(
                insight["created_at"], 
                language_code
            )
        
        if "valid_until" in insight and insight["valid_until"]:
            localized_insight["valid_until_formatted"] = self.format_datetime(
                insight["valid_until"], 
                language_code
            )
        
        return localized_insight
    
    def localize_analytics_dashboard(self, dashboard_data: Dict[str, Any], language_code: str = None) -> Dict[str, Any]:
        """Localize analytics dashboard data"""
        if language_code is None:
            language_code = self.default_language
        
        localized_data = dashboard_data.copy()
        
        # Format numbers and percentages
        if "average_model_accuracy" in dashboard_data and dashboard_data["average_model_accuracy"]:
            localized_data["average_model_accuracy_formatted"] = self.format_percentage(
                dashboard_data["average_model_accuracy"] * 100, 
                language_code
            )
        
        # Format generated timestamp
        if "generated_at" in dashboard_data:
            localized_data["generated_at_formatted"] = self.format_datetime(
                dashboard_data["generated_at"], 
                language_code
            )
        
        return localized_data
    
    def _get_translations(self, language_code: str) -> Dict[str, str]:
        """Load translations for a language (with caching)"""
        if language_code in self._translations_cache and self.config["cache_translations"]:
            return self._translations_cache[language_code]
        
        translations = {}
        
        # Try to load translations from file
        translations_file = f"app/locales/{language_code}.json"
        if os.path.exists(translations_file):
            try:
                with open(translations_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass  # Use empty translations if file can't be loaded
        
        # Cache translations if caching is enabled
        if self.config["cache_translations"]:
            self._translations_cache[language_code] = translations
        
        return translations
    
    def clear_translation_cache(self):
        """Clear the translation cache"""
        self._translations_cache.clear()
    
    def add_translation(self, language_code: str, key: str, value: str):
        """Add or update a translation"""
        if language_code not in self._translations_cache:
            self._translations_cache[language_code] = {}
        
        self._translations_cache[language_code][key] = value