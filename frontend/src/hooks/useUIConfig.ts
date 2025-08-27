import { useState, useEffect } from 'react';
import uiConfig from '../config/ui-config.json';

interface UIConfig {
  tooltips: Record<string, any>;
  help_text: Record<string, any>;
  error_messages: Record<string, any>;
  success_messages: Record<string, any>;
}

interface UseUIConfigReturn {
  getTooltip: (path: string) => string;
  getHelpText: (path: string) => any;
  getErrorMessage: (path: string) => string;
  getSuccessMessage: (path: string) => string;
  config: UIConfig;
}

/**
 * Hook to access centralized UI configuration including tooltips, help text, and messages
 * 
 * @example
 * const { getTooltip, getHelpText } = useUIConfig();
 * const tooltip = getTooltip('masters.products.name');
 * const helpText = getHelpText('vouchers.pdf_extraction');
 */
export const useUIConfig = (): UseUIConfigReturn => {
  const [config] = useState<UIConfig>(uiConfig);

  const getNestedValue = (obj: any, path: string): any => {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : null;
    }, obj);
  };

  const getTooltip = (path: string): string => {
    const tooltip = getNestedValue(config.tooltips, path);
    return tooltip || '';
  };

  const getHelpText = (path: string): any => {
    const helpText = getNestedValue(config.help_text, path);
    return helpText || null;
  };

  const getErrorMessage = (path: string): string => {
    const errorMsg = getNestedValue(config.error_messages, path);
    return errorMsg || 'An error occurred';
  };

  const getSuccessMessage = (path: string): string => {
    const successMsg = getNestedValue(config.success_messages, path);
    return successMsg || 'Operation completed successfully';
  };

  return {
    getTooltip,
    getHelpText,
    getErrorMessage,
    getSuccessMessage,
    config
  };
};

export default useUIConfig;