// services/assetService.ts
// Asset Management service for API interactions

import api from "../lib/api";

export interface Asset {
  id: number;
  asset_code: string;
  asset_name: string;
  description?: string;
  category: string;
  subcategory?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  purchase_cost?: number;
  purchase_date?: string;
  location?: string;
  department?: string;
  assigned_to_employee?: string;
  status: "active" | "inactive" | "maintenance" | "retired" | "disposed";
  condition: "excellent" | "good" | "fair" | "poor" | "critical";
  useful_life_years?: number;
  salvage_value?: number;
  created_at: string;
}

export interface MaintenanceSchedule {
  id: number;
  asset_id: number;
  schedule_name: string;
  maintenance_type: "preventive" | "corrective" | "emergency" | "inspection";
  description?: string;
  frequency_type: string;
  frequency_value?: number;
  next_due_date?: string;
  estimated_cost?: number;
  priority: string;
  is_active: boolean;
  created_at: string;
}

export interface MaintenanceRecord {
  id: number;
  work_order_number: string;
  asset_id: number;
  maintenance_type: "preventive" | "corrective" | "emergency" | "inspection";
  priority: string;
  scheduled_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  status: "scheduled" | "in_progress" | "completed" | "cancelled" | "overdue";
  description: string;
  total_cost: number;
  created_at: string;
}

export interface AssetDashboard {
  total_assets: number;
  active_assets: number;
  maintenance_assets: number;
  due_maintenance: number;
  overdue_maintenance: number;
  total_asset_value: number;
}

export interface AssetCreate {
  asset_code: string;
  asset_name: string;
  description?: string;
  category: string;
  subcategory?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  year_of_manufacture?: number;
  purchase_cost?: number;
  purchase_date?: string;
  vendor_id?: number;
  warranty_start_date?: string;
  warranty_end_date?: string;
  location?: string;
  department?: string;
  assigned_to_employee?: string;
  status?: "active" | "inactive" | "maintenance" | "retired" | "disposed";
  condition?: "excellent" | "good" | "fair" | "poor" | "critical";
  specifications?: string;
  operating_capacity?: string;
  power_rating?: string;
  depreciation_method?:
    | "straight_line"
    | "declining_balance"
    | "units_of_production"
    | "sum_of_years";
  useful_life_years?: number;
  salvage_value?: number;
  depreciation_rate?: number;
  insurance_provider?: string;
  insurance_policy_number?: string;
  insurance_expiry_date?: string;
  notes?: string;
}

export interface MaintenanceScheduleCreate {
  asset_id: number;
  schedule_name: string;
  maintenance_type: "preventive" | "corrective" | "emergency" | "inspection";
  description?: string;
  frequency_type: string;
  frequency_value?: number;
  estimated_duration_hours?: number;
  meter_type?: string;
  meter_frequency?: number;
  estimated_cost?: number;
  required_skills?: string;
  required_parts?: string;
  assigned_technician?: string;
  assigned_department?: string;
  priority?: string;
  advance_notice_days?: number;
}

export interface MaintenanceRecordCreate {
  asset_id: number;
  schedule_id?: number;
  maintenance_type: "preventive" | "corrective" | "emergency" | "inspection";
  priority?: string;
  scheduled_date?: string;
  description: string;
  work_performed?: string;
  findings?: string;
  recommendations?: string;
  assigned_technician?: string;
  performed_by?: string;
  supervised_by?: string;
  labor_cost?: number;
  parts_cost?: number;
  external_cost?: number;
  meter_reading_before?: number;
  meter_reading_after?: number;
  condition_before?: "excellent" | "good" | "fair" | "poor" | "critical";
  condition_after?: "excellent" | "good" | "fair" | "poor" | "critical";
  quality_check_passed?: boolean;
  quality_remarks?: string;
  parts_used?: Array<{
    product_id: number;
    quantity_used: number;
    unit: string;
    unit_cost?: number;
    batch_number?: string;
    serial_number?: string;
    notes?: string;
  }>;
}

class AssetService {
  // Asset Management
  async getAssets(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    status?: string;
    location?: string;
    department?: string;
  }): Promise<Asset[]> {
    const response = await api.get("/api/v1/assets/", { params });
    return response.data;
  }

  async getAsset(id: number): Promise<Asset> {
    const response = await api.get(`/api/v1/assets/${id}`);
    return response.data;
  }

  async createAsset(data: AssetCreate): Promise<Asset> {
    const response = await api.post("/api/v1/assets/", data);
    return response.data;
  }

  async updateAsset(id: number, data: Partial<AssetCreate>): Promise<Asset> {
    const response = await api.put(`/api/v1/assets/${id}`, data);
    return response.data;
  }

  async deleteAsset(id: number): Promise<void> {
    await api.delete(`/api/v1/assets/${id}`);
  }

  async getAssetCategories(): Promise<string[]> {
    const response = await api.get("/api/v1/assets/categories/");
    return response.data;
  }

  // Maintenance Schedules
  async getMaintenanceSchedules(params?: {
    skip?: number;
    limit?: number;
    asset_id?: number;
    maintenance_type?: string;
    is_active?: boolean;
  }): Promise<MaintenanceSchedule[]> {
    const response = await api.get("/api/v1/assets/maintenance-schedules/", {
      params,
    });
    return response.data;
  }

  async createMaintenanceSchedule(
    data: MaintenanceScheduleCreate,
  ): Promise<MaintenanceSchedule> {
    const response = await api.post(
      "/api/v1/assets/maintenance-schedules/",
      data,
    );
    return response.data;
  }

  async getDueMaintenance(
    daysAhead: number = 30,
  ): Promise<MaintenanceSchedule[]> {
    const response = await api.get(
      "/api/v1/assets/maintenance-schedules/due/",
      {
        params: { days_ahead: daysAhead },
      },
    );
    return response.data;
  }

  // Maintenance Records
  async getMaintenanceRecords(params?: {
    skip?: number;
    limit?: number;
    asset_id?: number;
    maintenance_type?: string;
    status?: string;
  }): Promise<MaintenanceRecord[]> {
    const response = await api.get("/api/v1/assets/maintenance-records/", {
      params,
    });
    return response.data;
  }

  async createMaintenanceRecord(
    data: MaintenanceRecordCreate,
  ): Promise<MaintenanceRecord> {
    const response = await api.post(
      "/api/v1/assets/maintenance-records/",
      data,
    );
    return response.data;
  }

  async completeMaintenanceRecord(
    id: number,
    data: {
      actual_end_date?: string;
      work_performed?: string;
      findings?: string;
    },
  ): Promise<MaintenanceRecord> {
    const response = await api.put(
      `/api/v1/assets/maintenance-records/${id}/complete`,
      data,
    );
    return response.data;
  }

  // Asset Depreciation
  async getAssetDepreciation(assetId: number, year?: number): Promise<any[]> {
    const response = await api.get(`/api/v1/assets/${assetId}/depreciation`, {
      params: year ? { year } : {},
    });
    return response.data;
  }

  async calculateDepreciation(assetId: number, year: number): Promise<any> {
    const response = await api.post(`/api/v1/assets/${assetId}/depreciation`, {
      year,
    });
    return response.data;
  }

  // Dashboard
  async getDashboardSummary(): Promise<AssetDashboard> {
    const response = await api.get("/api/v1/assets/dashboard/summary");
    return response.data;
  }
}

export const assetService = new AssetService();
