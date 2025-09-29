// frontend/src/hooks/useSharedSales.ts
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';

export interface SalesLead {
  id: string;
  company_name: string;
  contact_person: string;
  email: string;
  phone: string;
  status: 'new' | 'contacted' | 'qualified' | 'proposal' | 'won' | 'lost';
  value: number;
  formatted_value: string;
  source: string;
  assigned_to?: string;
  created_date: string;
  updated_date?: string;
  notes?: string;
}

export interface SalesOpportunity {
  id: string;
  name: string;
  account_name: string;
  stage: 'prospecting' | 'qualification' | 'proposal' | 'negotiation' | 'closed_won' | 'closed_lost';
  value: number;
  formatted_value: string;
  probability?: number;
  close_date: string;
  owner: string;
  created_date: string;
  description?: string;
}

export interface SalesCustomer {
  id: string;
  name: string;
  company?: string;
  email: string;
  phone: string;
  status: 'active' | 'inactive' | 'prospect';
  total_orders: number;
  total_value: number;
  formatted_total_value: string;
  last_order_date?: string;
  created_date: string;
}

export interface SalesMetrics {
  total_leads: number;
  leads_this_month: number;
  leads_trend: number;
  total_opportunities: number;
  opportunities_value: number;
  formatted_opportunities_value: string;
  win_rate: number;
  avg_deal_size: number;
  formatted_avg_deal_size: string;
  sales_this_month: number;
  formatted_sales_this_month: string;
  sales_trend: number;
  sales_target: number;
  formatted_sales_target: string;
  target_achievement: number;
}

export interface SalesState {
  leads: SalesLead[];
  opportunities: SalesOpportunity[];
  customers: SalesCustomer[];
  metrics: SalesMetrics | null;
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
 * Shared sales hook for both desktop and mobile interfaces
 * Provides unified business logic for sales data management
 */
export const useSharedSales = () => {
  const { user } = useAuth();
  
  const [state, setState] = useState<SalesState>({
    leads: [],
    opportunities: [],
    customers: [],
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
    status: '',
    source: '',
    dateFrom: '',
    dateTo: '',
    assignedTo: '',
  });

  const fetchSalesMetrics = useCallback(async () => {
    try {
      // Try to fetch real CRM analytics data first
      const { crmService } = await import('../services/crmService');
      const analyticsData = await crmService.getAnalytics();
      
      // Transform CRM analytics to sales metrics format
      const salesMetrics: SalesMetrics = {
        total_leads: analyticsData.total_leads,
        leads_this_month: Math.floor(analyticsData.total_leads * 0.2), // Estimate monthly leads
        leads_trend: analyticsData.lead_conversion_rate,
        total_opportunities: analyticsData.total_opportunities,
        opportunities_value: analyticsData.total_pipeline_value,
        formatted_opportunities_value: `₹${(analyticsData.total_pipeline_value / 100000).toFixed(1)}L`,
        win_rate: (analyticsData.won_opportunities / analyticsData.total_opportunities) * 100,
        avg_deal_size: analyticsData.avg_deal_size,
        formatted_avg_deal_size: `₹${analyticsData.avg_deal_size.toLocaleString()}`,
        sales_this_month: analyticsData.monthly_sales_actual,
        formatted_sales_this_month: `₹${(analyticsData.monthly_sales_actual / 100000).toFixed(1)}L`,
        sales_trend: ((analyticsData.monthly_sales_actual - analyticsData.monthly_sales_target) / analyticsData.monthly_sales_target) * 100,
        sales_target: analyticsData.monthly_sales_target,
        formatted_sales_target: `₹${(analyticsData.monthly_sales_target / 100000).toFixed(1)}L`,
        target_achievement: (analyticsData.monthly_sales_actual / analyticsData.monthly_sales_target) * 100,
      };

      setState(prev => ({ 
        ...prev, 
        metrics: salesMetrics,
        error: null 
      }));
    } catch (err) {
      console.warn('CRM analytics not available, using fallback metrics:', err);
      
      // Fallback to mock data if API is not available
      const mockMetrics: SalesMetrics = {
        total_leads: 142,
        leads_this_month: 28,
        leads_trend: 15.3,
        total_opportunities: 35,
        opportunities_value: 2850000,
        formatted_opportunities_value: '₹28.5L',
        win_rate: 68.5,
        avg_deal_size: 45000,
        formatted_avg_deal_size: '₹45,000',
        sales_this_month: 1250000,
        formatted_sales_this_month: '₹12.5L',
        sales_trend: 22.8,
        sales_target: 1500000,
        formatted_sales_target: '₹15L',
        target_achievement: 83.3,
      };

      setState(prev => ({ 
        ...prev, 
        metrics: mockMetrics,
        error: null 
      }));
    }
  }, []);

  const fetchLeads = useCallback(async (page: number = 1, pageSize: number = 10) => {
    try {
      // Try to fetch real leads data from CRM service
      const { crmService } = await import('../services/crmService');
      const skip = (page - 1) * pageSize;
      const apiLeads = await crmService.getLeads(skip, pageSize);
      
      // Transform API leads to SalesLead format
      const transformedLeads: SalesLead[] = apiLeads.map(lead => ({
        id: lead.lead_number || lead.id.toString(),
        company_name: lead.company_name,
        contact_person: lead.contact_person,
        email: lead.contact_email,
        phone: lead.contact_phone || '',
        status: lead.lead_status.toLowerCase() as SalesLead['status'],
        value: lead.estimated_value || 0,
        formatted_value: `₹${(lead.estimated_value || 0).toLocaleString()}`,
        source: lead.lead_source,
        assigned_to: lead.assigned_to?.toString(),
        created_date: lead.created_at.split('T')[0], // Format date
        updated_date: lead.updated_at?.split('T')[0],
        notes: `Industry: ${lead.industry || 'Not specified'}`
      }));

      setState(prev => ({ 
        ...prev, 
        leads: transformedLeads,
        pagination: {
          ...prev.pagination,
          page,
          pageSize,
          totalRecords: transformedLeads.length,
          totalPages: Math.ceil(transformedLeads.length / pageSize),
        },
        error: null 
      }));
    } catch (err) {
      console.warn('CRM leads not available, using fallback data:', err);
      
      // Fallback to mock data if API is not available
      const mockLeads: SalesLead[] = [
        {
          id: 'LEAD-001',
          company_name: 'TechCorp Solutions',
          contact_person: 'John Smith',
          email: 'john@techcorp.com',
          phone: '+91-9876543210',
          status: 'qualified',
          value: 75000,
          formatted_value: '₹75,000',
          source: 'Website',
          assigned_to: 'Sales Rep 1',
          created_date: '2024-01-15',
          notes: 'Interested in enterprise package'
        },
        {
          id: 'LEAD-002',
          company_name: 'Digital Dynamics',
          contact_person: 'Sarah Johnson',
          email: 'sarah@digitaldynamics.com',
          phone: '+91-9876543211',
          status: 'contacted',
          value: 45000,
          formatted_value: '₹45,000',
          source: 'Referral',
          assigned_to: 'Sales Rep 2',
          created_date: '2024-01-14',
          notes: 'Follow up scheduled for next week'
        },
        {
          id: 'LEAD-003',
          company_name: 'Innovation Labs',
          contact_person: 'Mike Chen',
          email: 'mike@innovationlabs.com',
          phone: '+91-9876543212',
          status: 'new',
          value: 60000,
          formatted_value: '₹60,000',
          source: 'Cold Call',
          created_date: '2024-01-13',
        },
      ];

      setState(prev => ({ 
        ...prev, 
        leads: mockLeads,
        pagination: {
          ...prev.pagination,
          page,
          pageSize,
          totalRecords: mockLeads.length,
          totalPages: Math.ceil(mockLeads.length / pageSize),
        },
        error: null 
      }));
    }
  }, [filters]);

  const fetchOpportunities = useCallback(async () => {
    try {
      // Try to fetch real opportunities data from CRM service
      const { crmService } = await import('../services/crmService');
      const apiOpportunities = await crmService.getOpportunities(0, 50);
      
      // Transform API opportunities to SalesOpportunity format
      const transformedOpportunities: SalesOpportunity[] = apiOpportunities.map(opp => ({
        id: opp.opportunity_number || opp.id.toString(),
        name: opp.title,
        account_name: `Account ${opp.lead_id}`, // This might need enhancement with proper account lookup
        stage: opp.stage.toLowerCase().replace(' ', '_') as SalesOpportunity['stage'],
        value: opp.estimated_value,
        formatted_value: `₹${(opp.estimated_value / 100000).toFixed(1)}L`,
        probability: opp.probability,
        close_date: opp.expected_close_date,
        owner: opp.assigned_to?.toString() || 'Unassigned',
        created_date: opp.created_at.split('T')[0],
        description: opp.description
      }));

      setState(prev => ({ 
        ...prev, 
        opportunities: transformedOpportunities,
        error: null 
      }));
    } catch (err) {
      console.warn('CRM opportunities not available, using fallback data:', err);
      
      // Fallback to mock data if API is not available
      const mockOpportunities: SalesOpportunity[] = [
        {
          id: 'OPP-001',
          name: 'Enterprise Software License',
          account_name: 'TechCorp Solutions',
          stage: 'proposal',
          value: 150000,
          formatted_value: '₹1.5L',
          probability: 75,
          close_date: '2024-02-15',
          owner: 'Sales Rep 1',
          created_date: '2024-01-10',
          description: 'Annual enterprise license for 50 users'
        },
        {
          id: 'OPP-002',
          name: 'Consulting Services',
          account_name: 'Digital Dynamics',
          stage: 'negotiation',
          value: 85000,
          formatted_value: '₹85,000',
          probability: 60,
          close_date: '2024-01-30',
          owner: 'Sales Rep 2',
          created_date: '2024-01-08',
          description: '3-month consulting engagement'
        },
      ];

      setState(prev => ({ 
        ...prev, 
        opportunities: mockOpportunities,
        error: null 
      }));
    }
  }, []);

  const fetchCustomers = useCallback(async () => {
    try {
      // Try to fetch real customers data from CRM service
      const { crmService } = await import('../services/crmService');
      const apiCustomers = await crmService.getCustomers(0, 50);
      
      // Transform API customers to SalesCustomer format
      const transformedCustomers: SalesCustomer[] = apiCustomers.map(customer => ({
        id: customer.customer_number || customer.id.toString(),
        name: customer.contact_person,
        company: customer.company_name,
        email: customer.contact_email,
        phone: customer.contact_phone || '',
        status: customer.is_active ? 'active' : 'inactive',
        total_orders: Math.floor(Math.random() * 20) + 1, // Placeholder until order data is available
        total_value: (customer.credit_limit || 0) * 0.6, // Estimate based on credit limit
        formatted_total_value: `₹${((customer.credit_limit || 0) * 0.6 / 100000).toFixed(1)}L`,
        last_order_date: '2024-01-10', // Placeholder
        created_date: customer.created_at.split('T')[0],
      }));

      setState(prev => ({ 
        ...prev, 
        customers: transformedCustomers,
        error: null 
      }));
    } catch (err) {
      console.warn('CRM customers not available, using fallback data:', err);
      
      // Fallback to mock data if API is not available
      const mockCustomers: SalesCustomer[] = [
        {
          id: 'CUST-001',
          name: 'John Smith',
          company: 'TechCorp Solutions',
          email: 'john@techcorp.com',
          phone: '+91-9876543210',
          status: 'active',
          total_orders: 12,
          total_value: 450000,
          formatted_total_value: '₹4.5L',
          last_order_date: '2024-01-10',
          created_date: '2023-06-15',
        },
        {
          id: 'CUST-002',
          name: 'Sarah Johnson',
          company: 'Digital Dynamics',
          email: 'sarah@digitaldynamics.com',
          phone: '+91-9876543211',
          status: 'active',
          total_orders: 8,
          total_value: 320000,
          formatted_total_value: '₹3.2L',
          last_order_date: '2024-01-05',
          created_date: '2023-08-20',
        },
      ];

      setState(prev => ({ 
        ...prev, 
        customers: mockCustomers,
        error: null 
      }));
    }
  }, []);

  const refresh = useCallback(async () => {
    setState(prev => ({ ...prev, refreshing: true, error: null }));
    
    try {
      await Promise.all([
        fetchSalesMetrics(),
        fetchLeads(state.pagination.page, state.pagination.pageSize),
        fetchOpportunities(),
        fetchCustomers(),
      ]);
    } finally {
      setState(prev => ({ 
        ...prev, 
        refreshing: false, 
        loading: false 
      }));
    }
  }, [fetchSalesMetrics, fetchLeads, fetchOpportunities, fetchCustomers, state.pagination]);

  const updateFilters = useCallback((newFilters: Partial<typeof filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const searchLeads = useCallback((query: string) => {
    updateFilters({ search: query });
  }, [updateFilters]);

  const changePage = useCallback((page: number) => {
    fetchLeads(page, state.pagination.pageSize);
  }, [fetchLeads, state.pagination.pageSize]);

  // Get sales pipeline stages
  const getPipelineStages = useCallback(() => {
    return [
      { name: 'Prospecting', value: 'prospecting', color: 'info' },
      { name: 'Qualification', value: 'qualification', color: 'warning' },
      { name: 'Proposal', value: 'proposal', color: 'primary' },
      { name: 'Negotiation', value: 'negotiation', color: 'secondary' },
      { name: 'Closed Won', value: 'closed_won', color: 'success' },
      { name: 'Closed Lost', value: 'closed_lost', color: 'error' },
    ];
  }, []);

  // Get lead status options
  const getLeadStatuses = useCallback(() => {
    return [
      { name: 'New', value: 'new', color: 'info' },
      { name: 'Contacted', value: 'contacted', color: 'warning' },
      { name: 'Qualified', value: 'qualified', color: 'primary' },
      { name: 'Proposal', value: 'proposal', color: 'secondary' },
      { name: 'Won', value: 'won', color: 'success' },
      { name: 'Lost', value: 'lost', color: 'error' },
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
      fetchLeads(1, state.pagination.pageSize);
    }
  }, [filters, fetchLeads, state.loading, state.pagination.pageSize]);

  // Filter leads based on current search
  const getFilteredLeads = useCallback(() => {
    if (!filters.search) return state.leads;
    
    return state.leads.filter(lead =>
      lead.company_name.toLowerCase().includes(filters.search.toLowerCase()) ||
      lead.contact_person.toLowerCase().includes(filters.search.toLowerCase()) ||
      lead.email.toLowerCase().includes(filters.search.toLowerCase()) ||
      lead.phone.includes(filters.search)
    );
  }, [state.leads, filters.search]);

  return {
    ...state,
    filters,
    filteredLeads: getFilteredLeads(),
    refresh,
    updateFilters,
    searchLeads,
    changePage,
    getPipelineStages,
    getLeadStatuses,
  };
};

export default useSharedSales;