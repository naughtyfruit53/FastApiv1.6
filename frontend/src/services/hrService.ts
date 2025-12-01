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

// Department interfaces
export interface Department {
  id: number;
  name: string;
  code: string;
  description?: string;
  parent_id?: number;
  manager_id?: number;
  is_active: boolean;
  cost_center_code?: string;
  organization_id: number;
  created_at: string;
  updated_at?: string;
}

export interface DepartmentCreate {
  name: string;
  code: string;
  description?: string;
  parent_id?: number;
  manager_id?: number;
  is_active?: boolean;
  cost_center_code?: string;
}

export interface DepartmentUpdate {
  name?: string;
  code?: string;
  description?: string;
  parent_id?: number;
  manager_id?: number;
  is_active?: boolean;
  cost_center_code?: string;
}

// Position interfaces
export interface Position {
  id: number;
  title: string;
  code: string;
  description?: string;
  department_id?: number;
  level?: string;
  grade?: string;
  min_salary?: number;
  max_salary?: number;
  is_active: boolean;
  headcount?: number;
  organization_id: number;
  created_at: string;
  updated_at?: string;
}

export interface PositionCreate {
  title: string;
  code: string;
  description?: string;
  department_id?: number;
  level?: string;
  grade?: string;
  min_salary?: number;
  max_salary?: number;
  is_active?: boolean;
  headcount?: number;
}

export interface PositionUpdate {
  title?: string;
  code?: string;
  description?: string;
  department_id?: number;
  level?: string;
  grade?: string;
  min_salary?: number;
  max_salary?: number;
  is_active?: boolean;
  headcount?: number;
}

// Work Shift interfaces
export interface WorkShift {
  id: number;
  name: string;
  code: string;
  description?: string;
  start_time: string;
  end_time: string;
  break_start_time?: string;
  break_end_time?: string;
  working_hours: number;
  break_duration_minutes: number;
  shift_type: string;
  grace_period_minutes: number;
  overtime_threshold_minutes: number;
  is_active: boolean;
  is_default: boolean;
  organization_id: number;
  created_at: string;
  updated_at?: string;
}

export interface WorkShiftCreate {
  name: string;
  code: string;
  description?: string;
  start_time: string;
  end_time: string;
  break_start_time?: string;
  break_end_time?: string;
  working_hours?: number;
  break_duration_minutes?: number;
  shift_type?: string;
  grace_period_minutes?: number;
  overtime_threshold_minutes?: number;
  is_active?: boolean;
  is_default?: boolean;
}

export interface WorkShiftUpdate {
  name?: string;
  code?: string;
  description?: string;
  start_time?: string;
  end_time?: string;
  break_start_time?: string;
  break_end_time?: string;
  working_hours?: number;
  break_duration_minutes?: number;
  shift_type?: string;
  grace_period_minutes?: number;
  overtime_threshold_minutes?: number;
  is_active?: boolean;
  is_default?: boolean;
}

// Holiday Calendar interfaces
export interface Holiday {
  id: number;
  name: string;
  holiday_date: string;
  description?: string;
  holiday_type: string;
  is_mandatory: boolean;
  applicable_departments?: Record<string, unknown>;
  year: number;
  organization_id: number;
  created_at: string;
  updated_at?: string;
}

export interface HolidayCreate {
  name: string;
  holiday_date: string;
  description?: string;
  holiday_type?: string;
  is_mandatory?: boolean;
  applicable_departments?: Record<string, unknown>;
  year: number;
}

export interface HolidayUpdate {
  name?: string;
  holiday_date?: string;
  description?: string;
  holiday_type?: string;
  is_mandatory?: boolean;
  applicable_departments?: Record<string, unknown>;
  year?: number;
}

// Payslip interfaces
export interface Payslip {
  id: number;
  payslip_number: string;
  employee_id: number;
  payroll_period_id: number;
  salary_structure_id: number;
  pay_date: string;
  working_days: number;
  present_days: number;
  absent_days: number;
  leave_days: number;
  overtime_hours: number;
  basic_salary: number;
  hra: number;
  transport_allowance: number;
  medical_allowance: number;
  special_allowance: number;
  overtime_amount: number;
  other_allowances: number;
  provident_fund: number;
  professional_tax: number;
  income_tax: number;
  loan_deduction: number;
  other_deductions: number;
  gross_pay: number;
  total_deductions: number;
  net_pay: number;
  status: string;
  pdf_path?: string;
  email_sent: boolean;
  organization_id: number;
  created_at: string;
  updated_at?: string;
}

// Attendance interfaces
export interface AttendanceRecord {
  id: number;
  employee_id: number;
  attendance_date: string;
  check_in_time?: string;
  check_out_time?: string;
  total_hours?: number;
  overtime_hours?: number;
  attendance_status: string;
  work_type: string;
  check_in_location?: string;
  check_out_location?: string;
  check_in_device?: string;
  is_approved: boolean;
  employee_remarks?: string;
  manager_remarks?: string;
  organization_id: number;
  created_at: string;
  updated_at?: string;
}

export interface ClockInRequest {
  employee_id: number;
  work_type?: string;
  location?: string;
  device?: string;
  remarks?: string;
}

export interface ClockOutRequest {
  employee_id: number;
  location?: string;
  remarks?: string;
}

// Leave Application interfaces
export interface LeaveApplication {
  id: number;
  employee_id: number;
  leave_type_id: number;
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  status: string;
  is_half_day: boolean;
  half_day_period?: string;
  applied_date: string;
  approved_by_id?: number;
  approved_date?: string;
  approval_remarks?: string;
  organization_id: number;
  created_at: string;
  updated_at?: string;
}

export interface LeaveApplicationCreate {
  employee_id: number;
  leave_type_id: number;
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  is_half_day?: boolean;
  half_day_period?: string;
  contact_number?: string;
  emergency_contact?: string;
}

// Leave Type interfaces
export interface LeaveType {
  id: number;
  name: string;
  code: string;
  description?: string;
  annual_allocation?: number;
  carry_forward_allowed: boolean;
  max_carry_forward_days?: number;
  cash_conversion_allowed: boolean;
  min_days_per_application?: number;
  max_days_per_application?: number;
  advance_notice_days?: number;
  requires_approval: boolean;
  is_active: boolean;
  organization_id: number;
  created_at: string;
  updated_at?: string;
}

export interface LeaveTypeCreate {
  name: string;
  code: string;
  description?: string;
  annual_allocation?: number;
  carry_forward_allowed?: boolean;
  max_carry_forward_days?: number;
  cash_conversion_allowed?: boolean;
  min_days_per_application?: number;
  max_days_per_application?: number;
  advance_notice_days?: number;
  requires_approval?: boolean;
  is_active?: boolean;
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

  // ==========================================================================
  // Department Management
  // ==========================================================================

  /**
   * Get all departments
   */
  async getDepartments(isActive?: boolean): Promise<Department[]> {
    try {
      const response = await api.get(`${this.endpoint}/departments`, {
        params: isActive !== undefined ? { is_active: isActive } : {},
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching departments:", error);
      throw error;
    }
  }

  /**
   * Get department by ID
   */
  async getDepartment(id: number): Promise<Department> {
    try {
      const response = await api.get(`${this.endpoint}/departments/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching department ${id}:`, error);
      throw error;
    }
  }

  /**
   * Create new department
   */
  async createDepartment(data: DepartmentCreate): Promise<Department> {
    try {
      const response = await api.post(`${this.endpoint}/departments`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating department:", error);
      throw error;
    }
  }

  /**
   * Update department
   */
  async updateDepartment(id: number, data: DepartmentUpdate): Promise<Department> {
    try {
      const response = await api.put(`${this.endpoint}/departments/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating department ${id}:`, error);
      throw error;
    }
  }

  // ==========================================================================
  // Position Management
  // ==========================================================================

  /**
   * Get all positions
   */
  async getPositions(departmentId?: number, isActive?: boolean): Promise<Position[]> {
    try {
      const params: Record<string, unknown> = {};
      if (departmentId !== undefined) params.department_id = departmentId;
      if (isActive !== undefined) params.is_active = isActive;
      
      const response = await api.get(`${this.endpoint}/positions`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching positions:", error);
      throw error;
    }
  }

  /**
   * Create new position
   */
  async createPosition(data: PositionCreate): Promise<Position> {
    try {
      const response = await api.post(`${this.endpoint}/positions`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating position:", error);
      throw error;
    }
  }

  /**
   * Update position
   */
  async updatePosition(id: number, data: PositionUpdate): Promise<Position> {
    try {
      const response = await api.put(`${this.endpoint}/positions/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating position ${id}:`, error);
      throw error;
    }
  }

  // ==========================================================================
  // Work Shift Management
  // ==========================================================================

  /**
   * Get all work shifts
   */
  async getWorkShifts(isActive?: boolean): Promise<WorkShift[]> {
    try {
      const response = await api.get(`${this.endpoint}/shifts`, {
        params: isActive !== undefined ? { is_active: isActive } : {},
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching work shifts:", error);
      throw error;
    }
  }

  /**
   * Create new work shift
   */
  async createWorkShift(data: WorkShiftCreate): Promise<WorkShift> {
    try {
      const response = await api.post(`${this.endpoint}/shifts`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating work shift:", error);
      throw error;
    }
  }

  /**
   * Update work shift
   */
  async updateWorkShift(id: number, data: WorkShiftUpdate): Promise<WorkShift> {
    try {
      const response = await api.put(`${this.endpoint}/shifts/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating work shift ${id}:`, error);
      throw error;
    }
  }

  // ==========================================================================
  // Holiday Calendar Management
  // ==========================================================================

  /**
   * Get all holidays
   */
  async getHolidays(year?: number, holidayType?: string): Promise<Holiday[]> {
    try {
      const params: Record<string, unknown> = {};
      if (year !== undefined) params.year = year;
      if (holidayType !== undefined) params.holiday_type = holidayType;
      
      const response = await api.get(`${this.endpoint}/holidays`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching holidays:", error);
      throw error;
    }
  }

  /**
   * Create new holiday
   */
  async createHoliday(data: HolidayCreate): Promise<Holiday> {
    try {
      const response = await api.post(`${this.endpoint}/holidays`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating holiday:", error);
      throw error;
    }
  }

  /**
   * Update holiday
   */
  async updateHoliday(id: number, data: HolidayUpdate): Promise<Holiday> {
    try {
      const response = await api.put(`${this.endpoint}/holidays/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating holiday ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete holiday
   */
  async deleteHoliday(id: number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}/holidays/${id}`);
    } catch (error) {
      console.error(`Error deleting holiday ${id}:`, error);
      throw error;
    }
  }

  // ==========================================================================
  // Attendance Clock-In/Out
  // ==========================================================================

  /**
   * Clock in an employee
   */
  async clockIn(data: ClockInRequest): Promise<AttendanceRecord> {
    try {
      const response = await api.post(`${this.endpoint}/attendance/clock-in`, null, {
        params: {
          employee_id: data.employee_id,
          work_type: data.work_type || "office",
          location: data.location,
          device: data.device,
          remarks: data.remarks,
        },
      });
      return response.data;
    } catch (error) {
      console.error("Error clocking in:", error);
      throw error;
    }
  }

  /**
   * Clock out an employee
   */
  async clockOut(data: ClockOutRequest): Promise<AttendanceRecord> {
    try {
      const response = await api.post(`${this.endpoint}/attendance/clock-out`, null, {
        params: {
          employee_id: data.employee_id,
          location: data.location,
          remarks: data.remarks,
        },
      });
      return response.data;
    } catch (error) {
      console.error("Error clocking out:", error);
      throw error;
    }
  }

  /**
   * Get attendance records
   */
  async getAttendanceRecords(
    employeeId?: number,
    startDate?: string,
    endDate?: string,
    status?: string,
    skip: number = 0,
    limit: number = 100,
  ): Promise<AttendanceRecord[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (status) params.status = status;

      const response = await api.get(`${this.endpoint}/attendance`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching attendance records:", error);
      throw error;
    }
  }

  // ==========================================================================
  // Leave Management
  // ==========================================================================

  /**
   * Get leave types
   */
  async getLeaveTypes(isActive?: boolean): Promise<LeaveType[]> {
    try {
      const response = await api.get(`${this.endpoint}/leave-types`, {
        params: isActive !== undefined ? { is_active: isActive } : {},
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching leave types:", error);
      throw error;
    }
  }

  /**
   * Create leave type
   */
  async createLeaveType(data: LeaveTypeCreate): Promise<LeaveType> {
    try {
      const response = await api.post(`${this.endpoint}/leave-types`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating leave type:", error);
      throw error;
    }
  }

  /**
   * Get leave applications
   */
  async getLeaveApplications(
    employeeId?: number,
    status?: string,
    startDate?: string,
    endDate?: string,
    skip: number = 0,
    limit: number = 100,
  ): Promise<LeaveApplication[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (status) params.status = status;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const response = await api.get(`${this.endpoint}/leave-applications`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching leave applications:", error);
      throw error;
    }
  }

  /**
   * Create leave application
   */
  async createLeaveApplication(data: LeaveApplicationCreate): Promise<LeaveApplication> {
    try {
      const response = await api.post(`${this.endpoint}/leave-applications`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating leave application:", error);
      throw error;
    }
  }

  /**
   * Approve leave application
   */
  async approveLeaveApplication(id: number, remarks?: string): Promise<{ message: string }> {
    try {
      const response = await api.put(`${this.endpoint}/leave-applications/${id}/approve`, null, {
        params: remarks ? { approval_remarks: remarks } : {},
      });
      return response.data;
    } catch (error) {
      console.error(`Error approving leave application ${id}:`, error);
      throw error;
    }
  }

  /**
   * Reject leave application
   */
  async rejectLeaveApplication(id: number, remarks: string): Promise<{ message: string }> {
    try {
      const response = await api.put(`${this.endpoint}/leave-applications/${id}/reject`, null, {
        params: { approval_remarks: remarks },
      });
      return response.data;
    } catch (error) {
      console.error(`Error rejecting leave application ${id}:`, error);
      throw error;
    }
  }

  // ==========================================================================
  // HR Phase 2 Methods - Attendance Policies, Leave Balances, Timesheets
  // ==========================================================================

  /**
   * Get attendance policies
   */
  async getAttendancePolicies(isActive?: boolean): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = {};
      if (isActive !== undefined) params.is_active = isActive;
      const response = await api.get(`${this.endpoint}/attendance-policies`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching attendance policies:", error);
      throw error;
    }
  }

  /**
   * Create attendance policy
   */
  async createAttendancePolicy(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/attendance-policies`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating attendance policy:", error);
      throw error;
    }
  }

  /**
   * Get leave balances
   */
  async getLeaveBalances(
    employeeId?: number,
    leaveTypeId?: number,
    year?: number
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = {};
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (leaveTypeId !== undefined) params.leave_type_id = leaveTypeId;
      if (year !== undefined) params.year = year;
      const response = await api.get(`${this.endpoint}/leave-balances`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching leave balances:", error);
      throw error;
    }
  }

  /**
   * Get timesheets
   */
  async getTimesheets(
    employeeId?: number,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/timesheets`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching timesheets:", error);
      throw error;
    }
  }

  /**
   * Create timesheet
   */
  async createTimesheet(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/timesheets`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating timesheet:", error);
      throw error;
    }
  }

  /**
   * Submit timesheet
   */
  async submitTimesheet(timesheetId: number): Promise<{ message: string }> {
    try {
      const response = await api.put(`${this.endpoint}/timesheets/${timesheetId}/submit`);
      return response.data;
    } catch (error) {
      console.error("Error submitting timesheet:", error);
      throw error;
    }
  }

  /**
   * Approve timesheet
   */
  async approveTimesheet(timesheetId: number): Promise<{ message: string }> {
    try {
      const response = await api.put(`${this.endpoint}/timesheets/${timesheetId}/approve`);
      return response.data;
    } catch (error) {
      console.error("Error approving timesheet:", error);
      throw error;
    }
  }

  // ==========================================================================
  // Statutory Deductions & Payroll Arrears
  // ==========================================================================

  /**
   * Get statutory deductions
   */
  async getStatutoryDeductions(isActive?: boolean): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = {};
      if (isActive !== undefined) params.is_active = isActive;
      const response = await api.get(`${this.endpoint}/statutory-deductions`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching statutory deductions:", error);
      throw error;
    }
  }

  /**
   * Get payroll arrears
   */
  async getPayrollArrears(
    employeeId?: number,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/payroll-arrears`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching payroll arrears:", error);
      throw error;
    }
  }

  // ==========================================================================
  // Payslip Methods
  // ==========================================================================

  /**
   * Get payslips for an employee
   */
  async getPayslips(
    employeeId?: number,
    periodId?: number,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<Payslip[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (periodId !== undefined) params.payroll_period_id = periodId;
      if (status) params.status = status;
      const response = await api.get("/payroll/payslips", { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching payslips:", error);
      throw error;
    }
  }

  /**
   * Download payslip PDF
   */
  async downloadPayslipPdf(payslipId: number): Promise<Blob> {
    try {
      const response = await api.get(`/payroll/payslips/${payslipId}/pdf`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error("Error downloading payslip PDF:", error);
      throw error;
    }
  }

  // ==========================================================================
  // Phase 4 Methods - Analytics, Position Budgets, Transfers
  // ==========================================================================

  /**
   * Get HR analytics snapshots (Feature-flagged)
   */
  async getHRAnalyticsSnapshots(
    snapshotType?: string,
    startDate?: string,
    endDate?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (snapshotType) params.snapshot_type = snapshotType;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      const response = await api.get(`${this.endpoint}/analytics/snapshots`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching HR analytics snapshots:", error);
      throw error;
    }
  }

  /**
   * Get position budgets (Feature-flagged)
   */
  async getPositionBudgets(
    fiscalYear?: string,
    departmentId?: number,
    status?: string
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = {};
      if (fiscalYear) params.fiscal_year = fiscalYear;
      if (departmentId !== undefined) params.department_id = departmentId;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/position-budgets`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching position budgets:", error);
      throw error;
    }
  }

  /**
   * Get employee transfers (Feature-flagged)
   */
  async getEmployeeTransfers(
    employeeId?: number,
    transferType?: string,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (transferType) params.transfer_type = transferType;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/employee-transfers`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching employee transfers:", error);
      throw error;
    }
  }

  /**
   * Get integration adapters (Feature-flagged)
   */
  async getIntegrationAdapters(
    adapterType?: string,
    isActive?: boolean
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = {};
      if (adapterType) params.adapter_type = adapterType;
      if (isActive !== undefined) params.is_active = isActive;
      const response = await api.get(`${this.endpoint}/integration-adapters`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching integration adapters:", error);
      throw error;
    }
  }

  // ==========================================================================
  // Export Methods
  // ==========================================================================

  /**
   * Export payroll data
   */
  async exportPayrollData(
    payrollPeriodId: number,
    format: string = "csv",
    includeHeaders: boolean = true,
    dateFormat: string = "%Y-%m-%d",
    decimalPlaces: number = 2
  ): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/export/payroll`, {
        payroll_period_id: payrollPeriodId,
        export_format: {
          format,
          include_headers: includeHeaders,
          date_format: dateFormat,
          decimal_places: decimalPlaces
        }
      });
      return response.data;
    } catch (error) {
      console.error("Error exporting payroll data:", error);
      throw error;
    }
  }

  /**
   * Export attendance data
   */
  async exportAttendanceData(
    startDate: string,
    endDate: string,
    format: string = "csv",
    includeHeaders: boolean = true,
    dateFormat: string = "%Y-%m-%d",
    decimalPlaces: number = 2
  ): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/export/attendance`, {
        start_date: startDate,
        end_date: endDate,
        export_format: {
          format,
          include_headers: includeHeaders,
          date_format: dateFormat,
          decimal_places: decimalPlaces
        }
      });
      return response.data;
    } catch (error) {
      console.error("Error exporting attendance data:", error);
      throw error;
    }
  }

  /**
   * Export leave data
   */
  async exportLeaveData(
    startDate: string,
    endDate: string,
    format: string = "csv",
    includeHeaders: boolean = true,
    dateFormat: string = "%Y-%m-%d",
    decimalPlaces: number = 2
  ): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/export/leave`, {
        start_date: startDate,
        end_date: endDate,
        export_format: {
          format,
          include_headers: includeHeaders,
          date_format: dateFormat,
          decimal_places: decimalPlaces
        }
      });
      return response.data;
    } catch (error) {
      console.error("Error exporting leave data:", error);
      throw error;
    }
  }

  // ==========================================================================
  // HR Phase 3 Methods - Goals/OKRs, Review Cycles, 360 Feedback
  // ==========================================================================

  /**
   * Get goals
   */
  async getGoals(
    employeeId?: number,
    goalType?: string,
    status?: string,
    reviewCycleId?: number,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (goalType) params.goal_type = goalType;
      if (status) params.status = status;
      if (reviewCycleId !== undefined) params.review_cycle_id = reviewCycleId;
      const response = await api.get(`${this.endpoint}/goals`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching goals:", error);
      throw error;
    }
  }

  /**
   * Create goal
   */
  async createGoal(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/goals`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating goal:", error);
      throw error;
    }
  }

  /**
   * Update goal
   */
  async updateGoal(goalId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/goals/${goalId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating goal:", error);
      throw error;
    }
  }

  /**
   * Delete goal
   */
  async deleteGoal(goalId: number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}/goals/${goalId}`);
    } catch (error) {
      console.error("Error deleting goal:", error);
      throw error;
    }
  }

  /**
   * Get review cycles
   */
  async getReviewCycles(
    status?: string,
    cycleType?: string,
    isActive?: boolean
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = {};
      if (status) params.status = status;
      if (cycleType) params.cycle_type = cycleType;
      if (isActive !== undefined) params.is_active = isActive;
      const response = await api.get(`${this.endpoint}/review-cycles`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching review cycles:", error);
      throw error;
    }
  }

  /**
   * Create review cycle
   */
  async createReviewCycle(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/review-cycles`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating review cycle:", error);
      throw error;
    }
  }

  /**
   * Update review cycle
   */
  async updateReviewCycle(cycleId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/review-cycles/${cycleId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating review cycle:", error);
      throw error;
    }
  }

  /**
   * Get feedback forms
   */
  async getFeedbackForms(
    isTemplate?: boolean,
    feedbackType?: string,
    revieweeId?: number,
    reviewCycleId?: number,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (isTemplate !== undefined) params.is_template = isTemplate;
      if (feedbackType) params.feedback_type = feedbackType;
      if (revieweeId !== undefined) params.reviewee_id = revieweeId;
      if (reviewCycleId !== undefined) params.review_cycle_id = reviewCycleId;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/feedback-forms`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching feedback forms:", error);
      throw error;
    }
  }

  /**
   * Create feedback form
   */
  async createFeedbackForm(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/feedback-forms`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating feedback form:", error);
      throw error;
    }
  }

  /**
   * Update feedback form
   */
  async updateFeedbackForm(formId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/feedback-forms/${formId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating feedback form:", error);
      throw error;
    }
  }

  // ==========================================================================
  // Recruitment Methods
  // ==========================================================================

  /**
   * Get job postings
   */
  async getJobPostings(
    status?: string,
    departmentId?: number,
    employmentType?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (status) params.status = status;
      if (departmentId !== undefined) params.department_id = departmentId;
      if (employmentType) params.employment_type = employmentType;
      const response = await api.get(`${this.endpoint}/job-postings`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching job postings:", error);
      throw error;
    }
  }

  /**
   * Create job posting
   */
  async createJobPosting(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/job-postings`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating job posting:", error);
      throw error;
    }
  }

  /**
   * Update job posting
   */
  async updateJobPosting(postingId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/job-postings/${postingId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating job posting:", error);
      throw error;
    }
  }

  /**
   * Get candidates
   */
  async getCandidates(
    jobPostingId?: number,
    stage?: string,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (jobPostingId !== undefined) params.job_posting_id = jobPostingId;
      if (stage) params.stage = stage;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/candidates`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching candidates:", error);
      throw error;
    }
  }

  /**
   * Create candidate
   */
  async createCandidate(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/candidates`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating candidate:", error);
      throw error;
    }
  }

  /**
   * Update candidate
   */
  async updateCandidate(candidateId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/candidates/${candidateId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating candidate:", error);
      throw error;
    }
  }

  /**
   * Update candidate stage (Kanban)
   */
  async updateCandidateStage(candidateId: number, stage: string): Promise<{ message: string }> {
    try {
      const response = await api.put(`${this.endpoint}/candidates/${candidateId}/stage`, null, {
        params: { stage }
      });
      return response.data;
    } catch (error) {
      console.error("Error updating candidate stage:", error);
      throw error;
    }
  }

  /**
   * Get interviews
   */
  async getInterviews(
    candidateId?: number,
    status?: string,
    scheduledDate?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (candidateId !== undefined) params.candidate_id = candidateId;
      if (status) params.status = status;
      if (scheduledDate) params.scheduled_date = scheduledDate;
      const response = await api.get(`${this.endpoint}/interviews`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching interviews:", error);
      throw error;
    }
  }

  /**
   * Create interview
   */
  async createInterview(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/interviews`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating interview:", error);
      throw error;
    }
  }

  /**
   * Update interview
   */
  async updateInterview(interviewId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/interviews/${interviewId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating interview:", error);
      throw error;
    }
  }

  /**
   * Get job offers
   */
  async getJobOffers(
    candidateId?: number,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (candidateId !== undefined) params.candidate_id = candidateId;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/job-offers`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching job offers:", error);
      throw error;
    }
  }

  /**
   * Create job offer
   */
  async createJobOffer(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/job-offers`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating job offer:", error);
      throw error;
    }
  }

  /**
   * Update job offer
   */
  async updateJobOffer(offerId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/job-offers/${offerId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating job offer:", error);
      throw error;
    }
  }

  /**
   * Get onboarding tasks
   */
  async getOnboardingTasks(
    employeeId?: number,
    isTemplate?: boolean,
    status?: string,
    category?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (isTemplate !== undefined) params.is_template = isTemplate;
      if (status) params.status = status;
      if (category) params.category = category;
      const response = await api.get(`${this.endpoint}/onboarding-tasks`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching onboarding tasks:", error);
      throw error;
    }
  }

  /**
   * Create onboarding task
   */
  async createOnboardingTask(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/onboarding-tasks`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating onboarding task:", error);
      throw error;
    }
  }

  /**
   * Update onboarding task
   */
  async updateOnboardingTask(taskId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/onboarding-tasks/${taskId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating onboarding task:", error);
      throw error;
    }
  }

  // ==========================================================================
  // Compliance & Policies Methods
  // ==========================================================================

  /**
   * Get policy documents
   */
  async getPolicyDocuments(
    category?: string,
    status?: string,
    isActive?: boolean,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (category) params.category = category;
      if (status) params.status = status;
      if (isActive !== undefined) params.is_active = isActive;
      const response = await api.get(`${this.endpoint}/policy-documents`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching policy documents:", error);
      throw error;
    }
  }

  /**
   * Create policy document
   */
  async createPolicyDocument(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/policy-documents`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating policy document:", error);
      throw error;
    }
  }

  /**
   * Update policy document
   */
  async updatePolicyDocument(documentId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/policy-documents/${documentId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating policy document:", error);
      throw error;
    }
  }

  /**
   * Get policy acknowledgments
   */
  async getPolicyAcknowledgments(
    policyDocumentId?: number,
    employeeId?: number,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (policyDocumentId !== undefined) params.policy_document_id = policyDocumentId;
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/policy-acknowledgments`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching policy acknowledgments:", error);
      throw error;
    }
  }

  /**
   * Acknowledge policy
   */
  async acknowledgePolicy(ackId: number, ipAddress?: string): Promise<{ message: string }> {
    try {
      const response = await api.put(`${this.endpoint}/policy-acknowledgments/${ackId}/acknowledge`, null, {
        params: ipAddress ? { ip_address: ipAddress } : {}
      });
      return response.data;
    } catch (error) {
      console.error("Error acknowledging policy:", error);
      throw error;
    }
  }

  /**
   * Get training programs
   */
  async getTrainingPrograms(
    category?: string,
    trainingType?: string,
    isMandatory?: boolean,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (category) params.category = category;
      if (trainingType) params.training_type = trainingType;
      if (isMandatory !== undefined) params.is_mandatory = isMandatory;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/training-programs`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching training programs:", error);
      throw error;
    }
  }

  /**
   * Create training program
   */
  async createTrainingProgram(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/training-programs`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating training program:", error);
      throw error;
    }
  }

  /**
   * Update training program
   */
  async updateTrainingProgram(programId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/training-programs/${programId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating training program:", error);
      throw error;
    }
  }

  /**
   * Get training assignments
   */
  async getTrainingAssignments(
    employeeId?: number,
    trainingProgramId?: number,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (employeeId !== undefined) params.employee_id = employeeId;
      if (trainingProgramId !== undefined) params.training_program_id = trainingProgramId;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/training-assignments`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching training assignments:", error);
      throw error;
    }
  }

  /**
   * Create training assignment
   */
  async createTrainingAssignment(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/training-assignments`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating training assignment:", error);
      throw error;
    }
  }

  /**
   * Update training assignment
   */
  async updateTrainingAssignment(assignmentId: number, data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.put(`${this.endpoint}/training-assignments/${assignmentId}`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating training assignment:", error);
      throw error;
    }
  }

  /**
   * Get compliance exports
   */
  async getComplianceExports(
    exportType?: string,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<unknown[]> {
    try {
      const params: Record<string, unknown> = { skip, limit };
      if (exportType) params.export_type = exportType;
      if (status) params.status = status;
      const response = await api.get(`${this.endpoint}/compliance-exports`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching compliance exports:", error);
      throw error;
    }
  }

  /**
   * Create compliance export
   */
  async createComplianceExport(data: Record<string, unknown>): Promise<unknown> {
    try {
      const response = await api.post(`${this.endpoint}/compliance-exports`, data);
      return response.data;
    } catch (error) {
      console.error("Error creating compliance export:", error);
      throw error;
    }
  }
}

export const hrService = new HRService();
