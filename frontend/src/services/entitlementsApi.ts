// frontend/src/services/entitlementsApi.ts

/**
 * API client for organization entitlements
 */

import axios from 'axios';

let API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Normalize base URL to ensure /api/v1 is appended if missing
if (!API_BASE_URL.endsWith('/api/v1')) {
  API_BASE_URL = `${API_BASE_URL.replace(/\/$/, '')}/api/v1`;
}

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
 * Fetch entitlements for an organization (app use, cached)
 */
export async function fetchOrgEntitlements(
  orgId: number,
  token: string
): Promise<AppEntitlementsResponse> {
  const response = await axios.get<AppEntitlementsResponse>(
    `${API_BASE_URL}/orgs/${orgId}/entitlements`,
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