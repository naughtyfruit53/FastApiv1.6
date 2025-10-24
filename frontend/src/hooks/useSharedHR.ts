// frontend/src/hooks/useSharedHR.ts
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

export interface Employee {
  id: string;
  employee_id: string;
  name: string;
  email: string;
  phone: string;
  position: string;
  department: string;
  hire_date: string;
  status: 'active' | 'inactive' | 'on_leave';
  salary?: number;
  formatted_salary?: string;
  manager?: string;
  location?: string;
  employment_type: 'full_time' | 'part_time' | 'contract' | 'intern';
}

export interface LeaveRequest {
  id: string;
  employee_id: string;
  employee_name: string;
  leave_type: 'annual' | 'sick' | 'personal' | 'maternity' | 'paternity';
  start_date: string;
  end_date: string;
  days_requested: number;
  status: 'pending' | 'approved' | 'rejected';
  reason?: string;
  approved_by?: string;
  created_date: string;
}

export interface PayrollSummary {
  period: string;
  total_employees: number;
  total_gross_pay: number;
  formatted_total_gross_pay: string;
  total_deductions: number;
  formatted_total_deductions: string;
  total_net_pay: number;
  formatted_total_net_pay: string;
  processed_date?: string;
  status: 'draft' | 'processing' | 'completed';
}

export interface HRMetrics {
  total_employees: number;
  active_employees: number;
  new_hires_this_month: number;
  turnover_rate: number;
  avg_tenure_months: number;
  employees_on_leave: number;
  pending_leave_requests: number;
  upcoming_reviews: number;
  departments: Array<{
    name: string;
    employee_count: number;
    percentage: number;
  }>;
  employment_types: Record<string, number>;
}

export interface HRState {
  employees: Employee[];
  leaveRequests: LeaveRequest[];
  payrollSummary: PayrollSummary | null;
  metrics: HRMetrics | null;
  loading: boolean;
  error: string | null;
  refreshing: boolean;
  pagination: {
    page: number;
    totalPages: number;
    totalRecords: number;
    pageSize: number;
  };
}

/**
 * Shared HR hook for both desktop and mobile interfaces
 * Provides unified business logic for human resources management
 */
export const useSharedHR = () => {
  const { user } = useAuth();
  
  const [state, setState] = useState<HRState>({
    employees: [],
    leaveRequests: [],
    payrollSummary: null,
    metrics: null,
    loading: true,
    error: null,
    refreshing: false,
    pagination: {
      page: 1,
      totalPages: 1,
      totalRecords: 0,
      pageSize: 10,
    },
  });

  const [filters, setFilters] = useState({
    search: '',
    department: '',
    status: '',
    position: '',
    dateFrom: '',
    dateTo: '',
  });

  // TODO: Replace with real HR API endpoints
  const fetchHRMetrics = useCallback(async () => {
    try {
      // TODO: Implement real API call to /api/hr/metrics
      // const response = await api.get('/hr/metrics');
      
      // Mock data for now - replace with real API
      const mockMetrics: HRMetrics = {
        total_employees: 85,
        active_employees: 82,
        new_hires_this_month: 5,
        turnover_rate: 8.5,
        avg_tenure_months: 24,
        employees_on_leave: 3,
        pending_leave_requests: 7,
        upcoming_reviews: 12,
        departments: [
          { name: 'Engineering', employee_count: 35, percentage: 41.2 },
          { name: 'Sales', employee_count: 18, percentage: 21.2 },
          { name: 'Marketing', employee_count: 12, percentage: 14.1 },
          { name: 'Finance', employee_count: 8, percentage: 9.4 },
          { name: 'HR', employee_count: 5, percentage: 5.9 },
          { name: 'Operations', employee_count: 7, percentage: 8.2 },
        ],
        employment_types: {
          full_time: 68,
          part_time: 8,
          contract: 6,
          intern: 3,
        },
      };

      setState(prev => ({ 
        ...prev, 
        metrics: mockMetrics,
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch HR metrics" 
      }));
    }
  }, []);

  const fetchEmployees = useCallback(async (page: number = 1, pageSize: number = 10) => {
    try {
      // TODO: Implement real API call to /api/hr/employees
      // const response = await api.get('/hr/employees', {
      //   params: { page, page_size: pageSize, ...filters }
      // });

      // Mock data for now - replace with real API
      const mockEmployees: Employee[] = [
        {
          id: 'EMP-001',
          employee_id: 'E001',
          name: 'John Doe',
          email: 'john.doe@company.com',
          phone: '+91-9876543210',
          position: 'Senior Developer',
          department: 'Engineering',
          hire_date: '2022-03-15',
          status: 'active',
          salary: 85000,
          formatted_salary: '₹85,000',
          manager: 'Jane Smith',
          location: 'Bangalore',
          employment_type: 'full_time',
        },
        {
          id: 'EMP-002',
          employee_id: 'E002',
          name: 'Sarah Johnson',
          email: 'sarah.johnson@company.com',
          phone: '+91-9876543211',
          position: 'Sales Manager',
          department: 'Sales',
          hire_date: '2021-08-22',
          status: 'active',
          salary: 75000,
          formatted_salary: '₹75,000',
          manager: 'Mike Wilson',
          location: 'Mumbai',
          employment_type: 'full_time',
        },
        {
          id: 'EMP-003',
          employee_id: 'E003',
          name: 'Alex Chen',
          email: 'alex.chen@company.com',
          phone: '+91-9876543212',
          position: 'Marketing Specialist',
          department: 'Marketing',
          hire_date: '2023-01-10',
          status: 'on_leave',
          salary: 55000,
          formatted_salary: '₹55,000',
          manager: 'Lisa Brown',
          location: 'Delhi',
          employment_type: 'full_time',
        },
      ];

      setState(prev => ({ 
        ...prev, 
        employees: mockEmployees,
        pagination: {
          ...prev.pagination,
          page,
          pageSize,
          totalRecords: mockEmployees.length,
          totalPages: Math.ceil(mockEmployees.length / pageSize),
        },
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch employees" 
      }));
    }
  }, [filters]);

  const fetchLeaveRequests = useCallback(async (limit: number = 10) => {
    try {
      // TODO: Implement real API call to /api/hr/leave-requests/recent
      // const response = await api.get('/hr/leave-requests/recent', { params: { limit } });
      
      // Mock data for now - replace with real API
      const mockLeaveRequests: LeaveRequest[] = [
        {
          id: 'LR-001',
          employee_id: 'EMP-001',
          employee_name: 'John Doe',
          leave_type: 'annual',
          start_date: '2024-02-01',
          end_date: '2024-02-05',
          days_requested: 5,
          status: 'pending',
          reason: 'Family vacation',
          created_date: '2024-01-15',
        },
        {
          id: 'LR-002',
          employee_id: 'EMP-003',
          employee_name: 'Alex Chen',
          leave_type: 'sick',
          start_date: '2024-01-20',
          end_date: '2024-01-22',
          days_requested: 3,
          status: 'approved',
          reason: 'Medical treatment',
          approved_by: 'Lisa Brown',
          created_date: '2024-01-18',
        },
      ];

      setState(prev => ({ 
        ...prev, 
        leaveRequests: mockLeaveRequests,
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch leave requests" 
      }));
    }
  }, []);

  const fetchPayrollSummary = useCallback(async () => {
    try {
      // TODO: Implement real API call to /api/hr/payroll/current
      // const response = await api.get('/hr/payroll/current');
      
      // Mock data for now - replace with real API
      const mockPayrollSummary: PayrollSummary = {
        period: 'January 2024',
        total_employees: 85,
        total_gross_pay: 5400000,
        formatted_total_gross_pay: '₹54L',
        total_deductions: 810000,
        formatted_total_deductions: '₹8.1L',
        total_net_pay: 4590000,
        formatted_total_net_pay: '₹45.9L',
        processed_date: '2024-01-31',
        status: 'completed',
      };

      setState(prev => ({ 
        ...prev, 
        payrollSummary: mockPayrollSummary,
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch payroll summary" 
      }));
    }
  }, []);

  const refresh = useCallback(async () => {
    setState(prev => ({ ...prev, refreshing: true, error: null }));
    
    try {
      await Promise.all([
        fetchHRMetrics(),
        fetchEmployees(state.pagination.page, state.pagination.pageSize),
        fetchLeaveRequests(10),
        fetchPayrollSummary(),
      ]);
    } finally {
      setState(prev => ({ 
        ...prev, 
        refreshing: false, 
        loading: false 
      }));
    }
  }, [fetchHRMetrics, fetchEmployees, fetchLeaveRequests, fetchPayrollSummary, state.pagination]);

  const updateFilters = useCallback((newFilters: Partial<typeof filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const searchEmployees = useCallback((query: string) => {
    updateFilters({ search: query });
  }, [updateFilters]);

  const changePage = useCallback((page: number) => {
    fetchEmployees(page, state.pagination.pageSize);
  }, [fetchEmployees, state.pagination.pageSize]);

  // Get employee status options
  const getEmployeeStatuses = useCallback(() => {
    return [
      { name: 'Active', value: 'active', color: 'success' },
      { name: 'Inactive', value: 'inactive', color: 'default' },
      { name: 'On Leave', value: 'on_leave', color: 'warning' },
    ];
  }, []);

  // Get leave types
  const getLeaveTypes = useCallback(() => {
    return [
      { name: 'Annual Leave', value: 'annual', color: 'primary' },
      { name: 'Sick Leave', value: 'sick', color: 'error' },
      { name: 'Personal Leave', value: 'personal', color: 'info' },
      { name: 'Maternity Leave', value: 'maternity', color: 'secondary' },
      { name: 'Paternity Leave', value: 'paternity', color: 'secondary' },
    ];
  }, []);

  // Get employment types
  const getEmploymentTypes = useCallback(() => {
    return [
      { name: 'Full Time', value: 'full_time', color: 'primary' },
      { name: 'Part Time', value: 'part_time', color: 'info' },
      { name: 'Contract', value: 'contract', color: 'warning' },
      { name: 'Intern', value: 'intern', color: 'secondary' },
    ];
  }, []);

  // Initial data load
  useEffect(() => {
    if (user) {
      refresh();
    } else {
      setState(prev => ({ ...prev, loading: false }));
    }
  }, [user, refresh]);

  // Refetch when filters change
  useEffect(() => {
    if (!state.loading) {
      fetchEmployees(1, state.pagination.pageSize);
    }
  }, [filters, fetchEmployees, state.loading, state.pagination.pageSize]);

  // Filter employees based on current search
  const getFilteredEmployees = useCallback(() => {
    if (!filters.search) return state.employees;
    
    return state.employees.filter(employee =>
      employee.name.toLowerCase().includes(filters.search.toLowerCase()) ||
      employee.email.toLowerCase().includes(filters.search.toLowerCase()) ||
      employee.employee_id.toLowerCase().includes(filters.search.toLowerCase()) ||
      employee.department.toLowerCase().includes(filters.search.toLowerCase()) ||
      employee.position.toLowerCase().includes(filters.search.toLowerCase())
    );
  }, [state.employees, filters.search]);

  return {
    ...state,
    filters,
    filteredEmployees: getFilteredEmployees(),
    refresh,
    updateFilters,
    searchEmployees,
    changePage,
    getEmployeeStatuses,
    getLeaveTypes,
    getEmploymentTypes,
  };
};

export default useSharedHR;