// frontend/src/services/hrService.ts

import api from "../lib/api";

export interface HRDashboardData {
  total_employees: number;
  active_employees: number;
  employees_on_leave: number;
  pending_leave_approvals: number;
  upcoming_performance_reviews: number;
  recent_joiners: number;
  employees_in_probation: number;
  average_attendance_rate: number;
}

export interface HRActivity {
  id: number;
  type: string;
  employee: string;
  action: string;
  date: string;
  status: string;
}

export interface HRTask {
  id: number;
  task: string;
  due_date: string;
  priority: string;
  category: string;
}

export interface Employee {
  id: number;
  employee_code: string;
  user_id: number;
  user?: {
    full_name: string;
    email: string;
  };
  department?: string;
  position?: string;
  hire_date: string;
  employment_status: string;
  manager_id?: number;
  salary_band?: string;
  work_location?: string;
  phone_number?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  created_at: string;
  updated_at?: string;
}

class HRService {
  private endpoint = "/hr";

  /**
   * Get HR dashboard data
   */
  async getDashboardData(): Promise<HRDashboardData> {
    try {
      const response = await api.get(`${this.endpoint}/dashboard`);
      return response.data;
    } catch (error) {
      console.error("Error fetching HR dashboard data:", error);
      throw error;
    }
  }

  /**
   * Get recent HR activities
   */
  async getRecentActivities(limit: number = 10): Promise<HRActivity[]> {
    try {
      const response = await api.get(`${this.endpoint}/recent-activities`, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching HR activities:", error);
      throw error;
    }
  }

  /**
   * Get upcoming HR tasks
   */
  async getUpcomingTasks(limit: number = 10): Promise<HRTask[]> {
    try {
      const response = await api.get(`${this.endpoint}/upcoming-tasks`, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching HR tasks:", error);
      throw error;
    }
  }

  /**
   * Get all employees
   */
  async getEmployees(
    skip: number = 0,
    limit: number = 100,
  ): Promise<Employee[]> {
    try {
      const response = await api.get(`${this.endpoint}/employees`, {
        params: { skip, limit },
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching employees:", error);
      throw error;
    }
  }

  /**
   * Get employee by ID
   */
  async getEmployee(id: number): Promise<Employee> {
    try {
      const response = await api.get(`${this.endpoint}/employees/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching employee ${id}:`, error);
      throw error;
    }
  }

  /**
   * Create new employee
   */
  async createEmployee(employeeData: any): Promise<Employee> {
    try {
      const response = await api.post(
        `${this.endpoint}/employees`,
        employeeData,
      );
      return response.data;
    } catch (error) {
      console.error("Error creating employee:", error);
      throw error;
    }
  }

  /**
   * Update employee
   */
  async updateEmployee(id: number, employeeData: any): Promise<Employee> {
    try {
      const response = await api.put(
        `${this.endpoint}/employees/${id}`,
        employeeData,
      );
      return response.data;
    } catch (error) {
      console.error(`Error updating employee ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete employee
   */
  async deleteEmployee(id: number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}/employees/${id}`);
    } catch (error) {
      console.error(`Error deleting employee ${id}:`, error);
      throw error;
    }
  }
}

export const hrService = new HRService();
