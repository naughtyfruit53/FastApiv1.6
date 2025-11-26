// Configuration and feature flags for the frontend application

/**
 * Get the base API URL without /api/v1
 * @returns Base URL (e.g., http://localhost:8000)
 */
export const getApiBaseUrl = (): string => {
  let baseUrl;
  
  // Force HTTPS in production regardless of env var
  if (process.env.NODE_ENV === 'development' || typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  } else {
    baseUrl = process.env.NEXT_PUBLIC_API_URL || "https://fastapiv16-production.up.railway.app";
    // Ensure HTTPS protocol
    if (baseUrl.startsWith('http://')) {
      baseUrl = baseUrl.replace('http://', 'https://');
    }
  }
  
  // Remove trailing slashes
  baseUrl = baseUrl.replace(/\/+$/, '');
  
  // Remove /api/v1 if it was accidentally included
  if (baseUrl.endsWith('/api/v1')) {
    baseUrl = baseUrl.slice(0, -7);
  }
  
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