// frontend/src/hooks/useSharedCRM.ts
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';

export interface CRMContact {
  id: string;
  name: string;
  company?: string;
  email: string;
  phone: string;
  position?: string;
  status: 'active' | 'inactive' | 'prospect' | 'customer';
  source: 'website' | 'referral' | 'cold_call' | 'event' | 'social_media' | 'other';
  assigned_to?: string;
  tags: string[];
  notes?: string;
  last_contacted?: string;
  created_date: string;
  updated_date?: string;
}

export interface CRMInteraction {
  id: string;
  contact_id: string;
  contact_name: string;
  type: 'call' | 'email' | 'meeting' | 'note' | 'task';
  subject: string;
  description?: string;
  status: 'completed' | 'pending' | 'cancelled';
  scheduled_date?: string;
  completed_date?: string;
  created_by: string;
  duration_minutes?: number;
  outcome?: string;
}

export interface CRMSegment {
  id: string;
  name: string;
  description?: string;
  criteria: Record<string, any>;
  customer_count: number;
  total_value: number;
  formatted_total_value: string;
  growth_rate?: number;
  created_date: string;
}

export interface CRMAnalytics {
  total_contacts: number;
  contacts_this_month: number;
  contacts_trend: number;
  active_customers: number;
  prospects: number;
  total_interactions: number;
  interactions_this_week: number;
  avg_response_time_hours: number;
  conversion_rate: number;
  customer_lifetime_value: number;
  formatted_customer_lifetime_value: string;
  top_sources: Array<{
    source: string;
    count: number;
    percentage: number;
  }>;
}

export interface CRMState {
  contacts: CRMContact[];
  interactions: CRMInteraction[];
  segments: CRMSegment[];
  analytics: CRMAnalytics | null;
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
 * Shared CRM hook for both desktop and mobile interfaces
 * Provides unified business logic for customer relationship management
 */
export const useSharedCRM = () => {
  const { user } = useAuth();
  
  const [state, setState] = useState<CRMState>({
    contacts: [],
    interactions: [],
    segments: [],
    analytics: null,
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
    assignedTo: '',
    tags: [] as string[],
    dateFrom: '',
    dateTo: '',
  });

  // TODO: Replace with real CRM API endpoints
  const fetchCRMAnalytics = useCallback(async () => {
    try {
      // TODO: Implement real API call to /api/crm/analytics
      // const response = await api.get('/crm/analytics');
      
      // Mock data for now - replace with real API
      const mockAnalytics: CRMAnalytics = {
        total_contacts: 342,
        contacts_this_month: 45,
        contacts_trend: 18.5,
        active_customers: 198,
        prospects: 144,
        total_interactions: 1256,
        interactions_this_week: 78,
        avg_response_time_hours: 4.2,
        conversion_rate: 23.5,
        customer_lifetime_value: 85000,
        formatted_customer_lifetime_value: '₹85,000',
        top_sources: [
          { source: 'website', count: 125, percentage: 36.5 },
          { source: 'referral', count: 89, percentage: 26.0 },
          { source: 'cold_call', count: 67, percentage: 19.6 },
          { source: 'event', count: 34, percentage: 9.9 },
          { source: 'social_media', count: 27, percentage: 8.0 },
        ],
      };

      setState(prev => ({ 
        ...prev, 
        analytics: mockAnalytics,
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch CRM analytics" 
      }));
    }
  }, []);

  const fetchContacts = useCallback(async (page: number = 1, pageSize: number = 10) => {
    try {
      // TODO: Implement real API call to /api/crm/contacts
      // const response = await api.get('/crm/contacts', {
      //   params: { page, page_size: pageSize, ...filters }
      // });

      // Mock data for now - replace with real API
      const mockContacts: CRMContact[] = [
        {
          id: 'CONT-001',
          name: 'Alice Johnson',
          company: 'TechnoGen Solutions',
          email: 'alice@technogen.com',
          phone: '+91-9876543210',
          position: 'CEO',
          status: 'customer',
          source: 'website',
          assigned_to: 'Sales Rep 1',
          tags: ['enterprise', 'high-priority'],
          notes: 'Key decision maker for enterprise solutions',
          last_contacted: '2024-01-10',
          created_date: '2023-08-15',
          updated_date: '2024-01-10',
        },
        {
          id: 'CONT-002',
          name: 'Robert Chen',
          company: 'InnovaCorp',
          email: 'robert@innovacorp.com',
          phone: '+91-9876543211',
          position: 'CTO',
          status: 'prospect',
          source: 'referral',
          assigned_to: 'Sales Rep 2',
          tags: ['tech-focused', 'medium-priority'],
          notes: 'Interested in API integrations',
          last_contacted: '2024-01-08',
          created_date: '2024-01-05',
        },
        {
          id: 'CONT-003',
          name: 'Sarah Williams',
          company: 'DataFlow Inc',
          email: 'sarah@dataflow.com',
          phone: '+91-9876543212',
          position: 'VP Operations',
          status: 'active',
          source: 'cold_call',
          assigned_to: 'Sales Rep 1',
          tags: ['operations', 'recurring'],
          notes: 'Regular customer with monthly orders',
          last_contacted: '2024-01-12',
          created_date: '2023-12-01',
          updated_date: '2024-01-12',
        },
      ];

      setState(prev => ({ 
        ...prev, 
        contacts: mockContacts,
        pagination: {
          ...prev.pagination,
          page,
          pageSize,
          totalRecords: mockContacts.length,
          totalPages: Math.ceil(mockContacts.length / pageSize),
        },
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch contacts" 
      }));
    }
  }, [filters]);

  const fetchInteractions = useCallback(async (limit: number = 10) => {
    try {
      // TODO: Implement real API call to /api/crm/interactions/recent
      // const response = await api.get('/crm/interactions/recent', { params: { limit } });
      
      // Mock data for now - replace with real API
      const mockInteractions: CRMInteraction[] = [
        {
          id: 'INT-001',
          contact_id: 'CONT-001',
          contact_name: 'Alice Johnson',
          type: 'call',
          subject: 'Quarterly Review Call',
          description: 'Discussed Q4 performance and Q1 plans',
          status: 'completed',
          scheduled_date: '2024-01-10T14:00:00Z',
          completed_date: '2024-01-10T14:30:00Z',
          created_by: 'Sales Rep 1',
          duration_minutes: 30,
          outcome: 'Positive - planning expansion',
        },
        {
          id: 'INT-002',
          contact_id: 'CONT-002',
          contact_name: 'Robert Chen',
          type: 'email',
          subject: 'API Integration Proposal',
          description: 'Sent detailed proposal for API integration',
          status: 'completed',
          scheduled_date: '2024-01-08T10:00:00Z',
          completed_date: '2024-01-08T10:15:00Z',
          created_by: 'Sales Rep 2',
          outcome: 'Awaiting technical review',
        },
        {
          id: 'INT-003',
          contact_id: 'CONT-003',
          contact_name: 'Sarah Williams',
          type: 'meeting',
          subject: 'Monthly Check-in',
          description: 'Scheduled monthly business review',
          status: 'pending',
          scheduled_date: '2024-01-20T11:00:00Z',
          created_by: 'Sales Rep 1',
        },
      ];

      setState(prev => ({ 
        ...prev, 
        interactions: mockInteractions,
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch interactions" 
      }));
    }
  }, []);

  const fetchSegments = useCallback(async () => {
    try {
      // TODO: Implement real API call to /api/crm/segments
      // const response = await api.get('/crm/segments');
      
      // Mock data for now - replace with real API
      const mockSegments: CRMSegment[] = [
        {
          id: 'SEG-001',
          name: 'Enterprise Customers',
          description: 'Large companies with 500+ employees',
          criteria: { company_size: '>500', annual_revenue: '>50M' },
          customer_count: 45,
          total_value: 2500000,
          formatted_total_value: '₹25L',
          growth_rate: 12.5,
          created_date: '2023-06-01',
        },
        {
          id: 'SEG-002',
          name: 'High-Value Prospects',
          description: 'Prospects with potential value >1L',
          criteria: { estimated_value: '>100000', status: 'prospect' },
          customer_count: 23,
          total_value: 3200000,
          formatted_total_value: '₹32L',
          growth_rate: 8.3,
          created_date: '2023-09-15',
        },
      ];

      setState(prev => ({ 
        ...prev, 
        segments: mockSegments,
        error: null 
      }));
    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        error: err instanceof Error ? err.message : "Failed to fetch segments" 
      }));
    }
  }, []);

  const refresh = useCallback(async () => {
    setState(prev => ({ ...prev, refreshing: true, error: null }));
    
    try {
      await Promise.all([
        fetchCRMAnalytics(),
        fetchContacts(state.pagination.page, state.pagination.pageSize),
        fetchInteractions(10),
        fetchSegments(),
      ]);
    } finally {
      setState(prev => ({ 
        ...prev, 
        refreshing: false, 
        loading: false 
      }));
    }
  }, [fetchCRMAnalytics, fetchContacts, fetchInteractions, fetchSegments, state.pagination]);

  const updateFilters = useCallback((newFilters: Partial<typeof filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const searchContacts = useCallback((query: string) => {
    updateFilters({ search: query });
  }, [updateFilters]);

  const changePage = useCallback((page: number) => {
    fetchContacts(page, state.pagination.pageSize);
  }, [fetchContacts, state.pagination.pageSize]);

  // Get contact status options
  const getContactStatuses = useCallback(() => {
    return [
      { name: 'Active', value: 'active', color: 'success' },
      { name: 'Prospect', value: 'prospect', color: 'warning' },
      { name: 'Customer', value: 'customer', color: 'primary' },
      { name: 'Inactive', value: 'inactive', color: 'default' },
    ];
  }, []);

  // Get interaction types
  const getInteractionTypes = useCallback(() => {
    return [
      { name: 'Call', value: 'call', icon: 'phone' },
      { name: 'Email', value: 'email', icon: 'email' },
      { name: 'Meeting', value: 'meeting', icon: 'meeting_room' },
      { name: 'Note', value: 'note', icon: 'note' },
      { name: 'Task', value: 'task', icon: 'task' },
    ];
  }, []);

  // Get lead sources
  const getLeadSources = useCallback(() => {
    return [
      { name: 'Website', value: 'website', color: 'primary' },
      { name: 'Referral', value: 'referral', color: 'success' },
      { name: 'Cold Call', value: 'cold_call', color: 'warning' },
      { name: 'Event', value: 'event', color: 'info' },
      { name: 'Social Media', value: 'social_media', color: 'secondary' },
      { name: 'Other', value: 'other', color: 'default' },
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
      fetchContacts(1, state.pagination.pageSize);
    }
  }, [filters, fetchContacts, state.loading, state.pagination.pageSize]);

  // Filter contacts based on current search
  const getFilteredContacts = useCallback(() => {
    if (!filters.search) return state.contacts;
    
    return state.contacts.filter(contact =>
      contact.name.toLowerCase().includes(filters.search.toLowerCase()) ||
      contact.email.toLowerCase().includes(filters.search.toLowerCase()) ||
      (contact.company && contact.company.toLowerCase().includes(filters.search.toLowerCase())) ||
      contact.phone.includes(filters.search)
    );
  }, [state.contacts, filters.search]);

  // Get recent interactions for a specific contact
  const getContactInteractions = useCallback((contactId: string) => {
    return state.interactions.filter(interaction => interaction.contact_id === contactId);
  }, [state.interactions]);

  return {
    ...state,
    filters,
    filteredContacts: getFilteredContacts(),
    refresh,
    updateFilters,
    searchContacts,
    changePage,
    getContactStatuses,
    getInteractionTypes,
    getLeadSources,
    getContactInteractions,
  };
};

export default useSharedCRM;