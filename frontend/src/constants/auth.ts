// frontend/src/constants/auth.ts
/**
 * Authentication constants for standardized token storage and retrieval
 * 
 * Using these constants ensures consistent token management across the application
 * and prevents auth loops caused by inconsistent storage keys.
 */

/**
 * LocalStorage key for access token
 * This is the primary authentication token used for API requests
 */
export const ACCESS_TOKEN_KEY = 'access_token';

/**
 * LocalStorage key for refresh token
 * Used to obtain a new access token when the current one expires
 */
export const REFRESH_TOKEN_KEY = 'refresh_token';

/**
 * LocalStorage key for user role
 * Stores the user's role for quick access without parsing the token
 */
export const USER_ROLE_KEY = 'user_role';

/**
 * LocalStorage key for super admin flag
 * Indicates whether the user has super admin privileges
 */
export const IS_SUPER_ADMIN_KEY = 'is_super_admin';

/**
 * Legacy token key - for backward compatibility
 * @deprecated Use ACCESS_TOKEN_KEY instead
 */
export const LEGACY_TOKEN_KEY = 'token';
