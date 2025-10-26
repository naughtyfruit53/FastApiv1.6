// frontend/src/services/websiteAgentService.ts

import { apiClient as api } from './api/client'; // Changed to named import with alias

export interface WebsiteProject {
  id: number;
  organization_id: number;
  project_name: string;
  project_type: string;
  customer_id?: number;
  status: string;
  domain?: string;
  subdomain?: string;
  theme: string;
  primary_color?: string;
  secondary_color?: string;
  site_title?: string;
  site_description?: string;
  logo_url?: string;
  favicon_url?: string;
  pages_config?: any;
  seo_config?: any;
  analytics_config?: any;
  deployment_url?: string;
  deployment_provider?: string;
  last_deployed_at?: string;
  chatbot_enabled: boolean;
  chatbot_config?: any;
  created_by_id?: number;
  updated_by_id?: number;
  created_at: string;
  updated_at?: string;
}

export interface WebsiteProjectCreate {
  project_name: string;
  project_type?: string;
  customer_id?: number;
  status?: string;
  domain?: string;
  subdomain?: string;
  theme?: string;
  primary_color?: string;
  secondary_color?: string;
  site_title?: string;
  site_description?: string;
  logo_url?: string;
  favicon_url?: string;
  pages_config?: any;
  seo_config?: any;
  analytics_config?: any;
  deployment_url?: string;
  deployment_provider?: string;
  chatbot_enabled?: boolean;
  chatbot_config?: any;
}

export interface WebsiteProjectUpdate {
  project_name?: string;
  project_type?: string;
  customer_id?: number;
  status?: string;
  domain?: string;
  subdomain?: string;
  theme?: string;
  primary_color?: string;
  secondary_color?: string;
  site_title?: string;
  site_description?: string;
  logo_url?: string;
  favicon_url?: string;
  pages_config?: any;
  seo_config?: any;
  analytics_config?: any;
  deployment_url?: string;
  deployment_provider?: string;
  chatbot_enabled?: boolean;
  chatbot_config?: any;
}

export interface WebsitePage {
  id: number;
  organization_id: number;
  project_id: number;
  page_name: string;
  page_slug: string;
  page_type: string;
  title: string;
  meta_description?: string;
  content?: string;
  sections_config?: any;
  is_published: boolean;
  order_index: number;
  seo_keywords?: string;
  og_image?: string;
  created_at: string;
  updated_at?: string;
}

export interface WebsitePageCreate {
  project_id: number;
  page_name: string;
  page_slug: string;
  page_type?: string;
  title: string;
  meta_description?: string;
  content?: string;
  sections_config?: any;
  is_published?: boolean;
  order_index?: number;
  seo_keywords?: string;
  og_image?: string;
}

export interface WebsitePageUpdate {
  page_name?: string;
  page_slug?: string;
  page_type?: string;
  title?: string;
  meta_description?: string;
  content?: string;
  sections_config?: any;
  is_published?: boolean;
  order_index?: number;
  seo_keywords?: string;
  og_image?: string;
}

export interface WebsiteDeployment {
  id: number;
  organization_id: number;
  project_id: number;
  deployment_version: string;
  deployment_status: string;
  deployment_url?: string;
  deployment_provider: string;
  deployment_config?: any;
  deployment_log?: string;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  deployed_by_id?: number;
  created_at: string;
}

export interface WebsiteDeploymentCreate {
  project_id: number;
  deployment_version: string;
  deployment_provider: string;
  deployment_config?: any;
}

export interface WebsiteMaintenanceLog {
  id: number;
  organization_id: number;
  project_id: number;
  maintenance_type: string;
  title: string;
  description?: string;
  status: string;
  changes_summary?: string;
  files_affected?: any;
  automated: boolean;
  scheduled_at?: string;
  performed_by_id?: number;
  created_at: string;
  completed_at?: string;
}

export interface WebsiteMaintenanceLogCreate {
  project_id: number;
  maintenance_type: string;
  title: string;
  description?: string;
  status?: string;
  changes_summary?: string;
  files_affected?: any;
  automated?: boolean;
  scheduled_at?: string;
}

// Website Project API calls

export const listProjects = async (params?: {
  skip?: number;
  limit?: number;
  status?: string;
  project_type?: string;
}): Promise<WebsiteProject[]> => {
  const response = await api.get('/api/v1/website-agent/projects', { params });
  return response.data;
};

export const getProject = async (projectId: number): Promise<WebsiteProject> => {
  const response = await api.get(`/api/v1/website-agent/projects/${projectId}`);
  return response.data;
};

export const createProject = async (data: WebsiteProjectCreate): Promise<WebsiteProject> => {
  const response = await api.post('/api/v1/website-agent/projects', data);
  return response.data;
};

export const updateProject = async (
  projectId: number,
  data: WebsiteProjectUpdate
): Promise<WebsiteProject> => {
  const response = await api.put(`/api/v1/website-agent/projects/${projectId}`, data);
  return response.data;
};

export const deleteProject = async (projectId: number): Promise<void> => {
  await api.delete(`/api/v1/website-agent/projects/${projectId}`);
};

// Website Page API calls

export const listPages = async (projectId: number): Promise<WebsitePage[]> => {
  const response = await api.get(`/api/v1/website-agent/projects/${projectId}/pages`);
  return response.data;
};

export const createPage = async (
  projectId: number,
  data: WebsitePageCreate
): Promise<WebsitePage> => {
  const response = await api.post(`/api/v1/website-agent/projects/${projectId}/pages`, data);
  return response.data;
};

export const updatePage = async (
  pageId: number,
  data: WebsitePageUpdate
): Promise<WebsitePage> => {
  const response = await api.put(`/api/v1/website-agent/pages/${pageId}`, data);
  return response.data;
};

export const deletePage = async (pageId: number): Promise<void> => {
  await api.delete(`/api/v1/website-agent/pages/${pageId}`);
};

// Deployment API calls

export const deployProject = async (
  projectId: number,
  data: WebsiteDeploymentCreate
): Promise<WebsiteDeployment> => {
  const response = await api.post(`/api/v1/website-agent/projects/${projectId}/deploy`, data);
  return response.data;
};

export const listDeployments = async (projectId: number): Promise<WebsiteDeployment[]> => {
  const response = await api.get(`/api/v1/website-agent/projects/${projectId}/deployments`);
  return response.data;
};

// Maintenance Log API calls

export const createMaintenanceLog = async (
  projectId: number,
  data: WebsiteMaintenanceLogCreate
): Promise<WebsiteMaintenanceLog> => {
  const response = await api.post(
    `/api/v1/website-agent/projects/${projectId}/maintenance`,
    data
  );
  return response.data;
};

export const listMaintenanceLogs = async (
  projectId: number
): Promise<WebsiteMaintenanceLog[]> => {
  const response = await api.get(`/api/v1/website-agent/projects/${projectId}/maintenance`);
  return response.data;
};

export default {
  listProjects,
  getProject,
  createProject,
  updateProject,
  deleteProject,
  listPages,
  createPage,
  updatePage,
  deletePage,
  deployProject,
  listDeployments,
  createMaintenanceLog,
  listMaintenanceLogs,
};