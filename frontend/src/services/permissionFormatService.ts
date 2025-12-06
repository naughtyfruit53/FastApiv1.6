/**
 * Service for fetching permission format configuration from backend
 * Provides feature detection for permission format and compatibility mode
 */

import axios from 'axios';

export interface PermissionFormatConfig {
  primary_format: string;
  compatibility: boolean;
  legacy_formats: string[];
  hierarchy_enabled: boolean;
  version: string;
  migration_status: string;
  total_legacy_mappings?: number;
  total_hierarchy_rules?: number;
}

export interface PermissionMapping {
  [key: string]: string;
}

/**
 * Get permission format configuration
 * @returns Permission format configuration
 */
export async function getPermissionFormat(): Promise<PermissionFormatConfig> {
  const response = await axios.get<PermissionFormatConfig>('/api/v1/system/permission-format');
  return response.data;
}

/**
 * Get legacy permission mappings (for debugging/development)
 * Requires admin privileges
 * @returns Mapping of legacy to new permission formats
 */
export async function getPermissionMappings(): Promise<PermissionMapping> {
  const response = await axios.get<PermissionMapping>('/api/v1/system/permission-format/mappings');
  return response.data;
}

/**
 * Get permission hierarchy configuration (for debugging/development)
 * Requires admin privileges
 * @returns Permission hierarchy mapping
 */
export async function getPermissionHierarchy(): Promise<Record<string, string[]>> {
  const response = await axios.get<Record<string, string[]>>('/api/v1/system/permission-format/hierarchy');
  return response.data;
}

const permissionFormatService = {
  getPermissionFormat,
  getPermissionMappings,
  getPermissionHierarchy,
};

export default permissionFormatService;
