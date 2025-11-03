// frontend/src/services/entitlementsApi.ts

/**
 * API client for organization entitlements
 */

import axios from 'axios';
import { getApiUrl } from '../utils/config';

// Use centralized config to prevent URL duplication
const API_BASE_URL = getApiUrl();

export interface SubmoduleEntitlement {
  [key: string]: boolean; // submodule_key -> enabled
}

export interface ModuleEntitlement {
  module_key: string;
  status: 'enabled' | 'disabled' | 'trial';
  trial_expires_at?: string | null;
  submodules: SubmoduleEntitlement;
}

export interface AppEntitlementsResponse {
  org_id: number;
  entitlements: {
    [module_key: string]: ModuleEntitlement;
  };
}

export interface SubmoduleInfo {
  id: number;
  submodule_key: string;
  display_name: string;
  description?: string;
  menu_path?: string;
  permission_key?: string;
  sort_order: number;
  is_active: boolean;
}

export interface ModuleInfo {
  id: number;
  module_key: string;
  display_name: string;
  description?: string;
  icon?: string;
  sort_order: number;
  is_active: boolean;
  submodules: SubmoduleInfo[];
}

export interface ModulesListResponse {
  modules: ModuleInfo[];
}

export interface SubmoduleEntitlementDetail {
  submodule_id: number;
  submodule_key: string;
  submodule_display_name: string;
  enabled: boolean;
  effective_status: 'enabled' | 'disabled' | 'trial';
  source?: string;
}

export interface ModuleEntitlementDetail {
  module_id: number;
  module_key: string;
  module_display_name: string;
  status: 'enabled' | 'disabled' | 'trial';
  trial_expires_at?: string | null;
  source: string;
  submodules: SubmoduleEntitlementDetail[];
}

export interface OrgEntitlementsResponse {
  org_id: number;
  org_name: string;
  entitlements: ModuleEntitlementDetail[];
}

export interface ModuleChange {
  module_key: string;
  status: 'enabled' | 'disabled' | 'trial';
  trial_expires_at?: string | null;
}

export interface SubmoduleChange {
  module_key: string;
  submodule_key: string;
  enabled: boolean;
}

export interface UpdateEntitlementsRequest {
  reason: string;
  changes: {
    modules: ModuleChange[];
    submodules: SubmoduleChange[];
  };
}

export interface UpdateEntitlementsResponse {
  success: boolean;
  message: string;
  event_id: number;
  updated_entitlements: OrgEntitlementsResponse;
}

/**
 * Fetch entitlements for the current organization (app use, cached)
 * Changed: No orgId in path, backend handles current org
 */
export async function fetchEntitlements(
  token: string
): Promise<AppEntitlementsResponse> {
  const response = await axios.get<AppEntitlementsResponse>(
    `${API_BASE_URL}/organizations/entitlements`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
}

/**
 * Fetch all modules (admin only)
 */
export async function fetchAllModules(
  token: string
): Promise<ModulesListResponse> {
  const response = await axios.get<ModulesListResponse>(
    `${API_BASE_URL}/admin/modules`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
}

/**
 * Fetch org entitlements with details (admin only)
 */
export async function fetchOrgEntitlementsAdmin(
  orgId: number,
  token: string
): Promise<OrgEntitlementsResponse> {
  const response = await axios.get<OrgEntitlementsResponse>(
    `${API_BASE_URL}/admin/orgs/${orgId}/entitlements`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
}

/**
 * Update org entitlements (admin only)
 */
export async function updateOrgEntitlements(
  orgId: number,
  request: UpdateEntitlementsRequest,
  token: string
): Promise<UpdateEntitlementsResponse> {
  const response = await axios.put<UpdateEntitlementsResponse>(
    `${API_BASE_URL}/admin/orgs/${orgId}/entitlements`,
    request,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );
  return response.data;
}

// ===== Category-Based Entitlements (10-Category Structure) =====

export interface CategoryInfo {
  key: string;
  display_name: string;
  description: string;
  modules: string[];
  module_count: number;
}

export interface CategoryListResponse {
  categories: CategoryInfo[];
}

export interface ActivateCategoryRequest {
  category: string;
  reason: string;
}

export interface DeactivateCategoryRequest {
  category: string;
  reason: string;
}

export interface OrgActivatedCategoriesResponse {
  org_id: number;
  activated_categories: string[];
}

/**
 * Fetch all available product categories (super admin only)
 */
export async function fetchCategories(
  token: string
): Promise<CategoryListResponse> {
  const response = await axios.get<CategoryListResponse>(
    `${API_BASE_URL}/admin/categories`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
}

/**
 * Get details of a specific category (super admin only)
 */
export async function fetchCategory(
  category: string,
  token: string
): Promise<CategoryInfo> {
  const response = await axios.get<CategoryInfo>(
    `${API_BASE_URL}/admin/categories/${category}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
}

/**
 * Activate a category for an organization (super admin only)
 */
export async function activateCategory(
  orgId: number,
  request: ActivateCategoryRequest,
  token: string
): Promise<UpdateEntitlementsResponse> {
  const response = await axios.post<UpdateEntitlementsResponse>(
    `${API_BASE_URL}/admin/categories/orgs/${orgId}/activate`,
    request,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );
  return response.data;
}

/**
 * Deactivate a category for an organization (super admin only)
 */
export async function deactivateCategory(
  orgId: number,
  request: DeactivateCategoryRequest,
  token: string
): Promise<UpdateEntitlementsResponse> {
  const response = await axios.post<UpdateEntitlementsResponse>(
    `${API_BASE_URL}/admin/categories/orgs/${orgId}/deactivate`,
    request,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );
  return response.data;
}

/**
 * Get activated categories for an organization (super admin only)
 */
export async function fetchActivatedCategories(
  orgId: number,
  token: string
): Promise<OrgActivatedCategoriesResponse> {
  const response = await axios.get<OrgActivatedCategoriesResponse>(
    `${API_BASE_URL}/admin/categories/orgs/${orgId}/activated`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
}