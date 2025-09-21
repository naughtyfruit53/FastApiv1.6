// Configuration and feature flags for the frontend application

export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",

  // Feature flags
  features: {
    passwordChange: process.env.NEXT_PUBLIC_ENABLE_PASSWORD_CHANGE !== "false",
    // Chart of Accounts Integration Feature Flags
    coaRequiredStrict: process.env.NEXT_PUBLIC_COA_REQUIRED_STRICT === "true",
    payrollEnabled: process.env.NEXT_PUBLIC_PAYROLL_ENABLED === "true",
    // Add more feature flags here as needed
  },
};

export const getFeatureFlag = (
  feature: keyof typeof config.features,
): boolean => {
  return config.features[feature];
};

export default config;
