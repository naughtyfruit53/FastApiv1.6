// Configuration and feature flags for the frontend application

/**
 * Get the base API URL without /api/v1
 * @returns Base URL (e.g., http://localhost:8000)
 */
export const getApiBaseUrl = (): string => {
  let baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  const isProduction = process.env.NODE_ENV === 'production';
  
  // In production, force HTTPS
  if (isProduction) {
    if (baseUrl.startsWith('http://')) {
      baseUrl = baseUrl.replace('http://', 'https://');
      console.warn('[Config] Forced HTTPS in production for API base URL');
    } else if (!baseUrl.startsWith('https://') && !baseUrl.startsWith('http://')) {
      // If no protocol, add https://
      baseUrl = `https://${baseUrl}`;
      console.warn('[Config] Added HTTPS protocol in production for API base URL');
    }
  }
  
  // Remove trailing slashes
  baseUrl = baseUrl.replace(/\/+$/, '');
  
  // Remove /api/v1 if it was accidentally included
  if (baseUrl.endsWith('/api/v1')) {
    baseUrl = baseUrl.slice(0, -7);
  }
  
  // REMOVED: Force 'localhost' instead of '127.0.0.1' - this was causing ERR_NAME_NOT_RESOLVED
  // If localhost doesn't resolve, set NEXT_PUBLIC_API_URL to http://127.0.0.1:8000 in .env.local
  // and restart the dev server.
  
  // Log for debugging
  if (typeof console !== 'undefined') {
    console.log('[config] Using API base URL:', baseUrl, 'NODE_ENV:', process.env.NODE_ENV);
  }
  
  return baseUrl;
};

/**
 * Get the full API URL with /api/v1
 * @returns Full API URL (e.g., http://localhost:8000/api/v1)
 */
export const getApiUrl = (): string => {
  return `${getApiBaseUrl()}/api/v1`;
};

export const config = {
  apiUrl: getApiBaseUrl(),
  apiUrlWithPath: getApiUrl(),

  // Feature flags
  features: {
    passwordChange: process.env.NEXT_PUBLIC_ENABLE_PASSWORD_CHANGE !== "false",
    
    // Chart of Accounts Integration Feature Flags (Phase 1)
    coaRequiredStrict: process.env.NEXT_PUBLIC_COA_REQUIRED_STRICT === "true",
    payrollEnabled: process.env.NEXT_PUBLIC_PAYROLL_ENABLED === "true",
    
    // Phase 2 Enhanced Feature Flags
    coaEnforcementMode: process.env.NEXT_PUBLIC_COA_ENFORCEMENT_MODE || "observe", // observe, warn, enforce
    coaLegacyModeEnabled: process.env.NEXT_PUBLIC_COA_LEGACY_MODE_ENABLED === "true",
    
    // Advanced Payroll Features
    advancedPayrollEnabled: process.env.NEXT_PUBLIC_ADVANCED_PAYROLL_ENABLED === "true",
    bulkPayrollPostingEnabled: process.env.NEXT_PUBLIC_BULK_PAYROLL_POSTING_ENABLED === "true",
    payrollReversalEnabled: process.env.NEXT_PUBLIC_PAYROLL_REVERSAL_ENABLED === "true",
    multiComponentPayrollEnabled: process.env.NEXT_PUBLIC_MULTI_COMPONENT_PAYROLL_ENABLED === "true",
    
    // Advanced Settings & Configuration
    advancedAccountMappingEnabled: process.env.NEXT_PUBLIC_ADVANCED_ACCOUNT_MAPPING_ENABLED === "true",
    departmentAccountMappingEnabled: process.env.NEXT_PUBLIC_DEPARTMENT_ACCOUNT_MAPPING_ENABLED === "true",
    coaOverrideEnabled: process.env.NEXT_PUBLIC_COA_OVERRIDE_ENABLED === "true",
    
    // Migration & Backfill
    migrationSystemEnabled: process.env.NEXT_PUBLIC_MIGRATION_SYSTEM_ENABLED === "true",
    backfillPreviewEnabled: process.env.NEXT_PUBLIC_BACKFILL_PREVIEW_ENABLED === "true",
    
    // Observability & Monitoring
    coaDashboardEnabled: process.env.NEXT_PUBLIC_COA_DASHBOARD_ENABLED === "true",
    payrollMonitoringEnabled: process.env.NEXT_PUBLIC_PAYROLL_MONITORING_ENABLED === "true",
    coaWarningsEnabled: process.env.NEXT_PUBLIC_COA_WARNINGS_ENABLED === "true",
  },
};

export const getFeatureFlag = (
  feature: keyof typeof config.features,
): boolean => {
  return config.features[feature];
};

// Phase 2: Enhanced feature flag utilities
export const getEnforcementLevel = (): "observe" | "warn" | "enforce" => {
  const mode = config.features.coaEnforcementMode as string;
  if (["observe", "warn", "enforce"].includes(mode)) {
    return mode as "observe" | "warn" | "enforce";
  }
  return "observe";
};

export const shouldEnforceCoA = (): boolean => {
  return getEnforcementLevel() === "enforce" || config.features.coaRequiredStrict;
};

export const shouldWarnAboutCoA = (): boolean => {
  return getEnforcementLevel() === "warn" || getEnforcementLevel() === "enforce";
};

export const isLegacyModeAllowed = (): boolean => {
  return config.features.coaLegacyModeEnabled && getEnforcementLevel() !== "enforce";
};

// Advanced payroll feature checks
export const getAdvancedPayrollFeatures = () => ({
  bulkPosting: config.features.bulkPayrollPostingEnabled,
  reversal: config.features.payrollReversalEnabled,
  multiComponent: config.features.multiComponentPayrollEnabled,
  advancedReporting: config.features.advancedPayrollEnabled,
});

export default config;
