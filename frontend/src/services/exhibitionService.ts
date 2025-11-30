import api from "../lib/api";

export interface ExhibitionEvent {
  id: number;
  name: string;
  description?: string;
  location?: string;
  venue?: string;
  start_date?: string;
  end_date?: string;
  status: "planned" | "active" | "completed" | "cancelled";
  is_active: boolean;
  auto_send_intro_email: boolean;
  created_at: string;
  card_scan_count?: number;
  prospect_count?: number;
}

export interface BusinessCardScan {
  id: number;
  scan_id: string;
  exhibition_event_id: number;
  full_name?: string;
  company_name?: string;
  designation?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  address?: string;
  confidence_score?: number;
  validation_status: "pending" | "validated" | "rejected";
  processing_status: "scanned" | "processed" | "converted" | "failed";
  prospect_created: boolean;
  intro_email_sent: boolean;
  created_at: string;
}

export interface ExhibitionProspect {
  id: number;
  exhibition_event_id: number;
  card_scan_id?: number;
  full_name: string;
  company_name: string;
  designation?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  address?: string;
  lead_score?: number;
  qualification_status: "unqualified" | "qualified" | "hot" | "cold";
  interest_level?: "high" | "medium" | "low";
  status: "new" | "contacted" | "qualified" | "converted" | "lost";
  conversion_status: "prospect" | "lead" | "customer";
  created_at: string;
  intro_email_sent_at?: string;
  contact_attempts: number;
}

export interface ExhibitionAnalytics {
  total_events: number;
  active_events: number;
  total_scans: number;
  total_prospects: number;
  conversion_rate: number;
  top_companies: Array<{ name: string; count: number }>;
  scan_trends: Array<{ date: string; count: number }>;
  lead_quality_distribution: { [key: string]: number };
}

const exhibitionService = {
  // Get all exhibition events
  getEvents: async (params?: {
    status?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<ExhibitionEvent[]> => {
    const response = await api.get("/exhibition/events", { params });
    return response.data;
  },

  // Get single exhibition event
  getEvent: async (eventId: number): Promise<ExhibitionEvent> => {
    const response = await api.get(`/exhibition/events/${eventId}`);
    return response.data;
  },

  // Create exhibition event
  createEvent: async (eventData: Partial<ExhibitionEvent>): Promise<ExhibitionEvent> => {
    const response = await api.post("/exhibition/events", eventData);
    return response.data;
  },

  // Update exhibition event
  updateEvent: async (eventId: number, eventData: Partial<ExhibitionEvent>): Promise<ExhibitionEvent> => {
    const response = await api.put(`/exhibition/events/${eventId}`, eventData);
    return response.data;
  },

  // Delete exhibition event
  deleteEvent: async (eventId: number): Promise<void> => {
    await api.delete(`/exhibition/events/${eventId}`);
  },

  // Get card scans - organization wide
  getAllCardScans: async (params?: {
    event_id?: number;
    validation_status?: string;
    processing_status?: string;
    skip?: number;
    limit?: number;
  }): Promise<BusinessCardScan[]> => {
    const response = await api.get("/exhibition/card-scans", { params });
    return response.data;
  },

  // Get card scan by ID
  getCardScan: async (scanId: number): Promise<BusinessCardScan> => {
    const response = await api.get(`/exhibition/card-scans/${scanId}`);
    return response.data;
  },

  // Upload and scan business card
  scanBusinessCard: async (eventId: number, file: File): Promise<BusinessCardScan> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post(`/exhibition/events/${eventId}/scan-card`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  // Update card scan
  updateCardScan: async (scanId: number, scanData: Partial<BusinessCardScan>): Promise<BusinessCardScan> => {
    const response = await api.put(`/exhibition/card-scans/${scanId}`, scanData);
    return response.data;
  },

  // Get prospects - organization wide
  getAllProspects: async (params?: {
    event_id?: number;
    status?: string;
    qualification_status?: string;
    assigned_to_id?: number;
    skip?: number;
    limit?: number;
  }): Promise<ExhibitionProspect[]> => {
    const response = await api.get("/exhibition/prospects", { params });
    return response.data;
  },

  // Get prospect by ID
  getProspect: async (prospectId: number): Promise<ExhibitionProspect> => {
    const response = await api.get(`/exhibition/prospects/${prospectId}`);
    return response.data;
  },

  // Create prospect
  createProspect: async (prospectData: Partial<ExhibitionProspect> & { exhibition_event_id: number }): Promise<ExhibitionProspect> => {
    const response = await api.post("/exhibition/prospects", prospectData);
    return response.data;
  },

  // Update prospect
  updateProspect: async (prospectId: number, prospectData: Partial<ExhibitionProspect>): Promise<ExhibitionProspect> => {
    const response = await api.put(`/exhibition/prospects/${prospectId}`, prospectData);
    return response.data;
  },

  // Convert prospect to customer
  convertProspectToCustomer: async (prospectId: number): Promise<any> => {
    const response = await api.post(`/exhibition/prospects/${prospectId}/convert-to-customer`);
    return response.data;
  },

  // Get exhibition analytics
  getAnalytics: async (params?: { event_id?: number }): Promise<ExhibitionAnalytics> => {
    const response = await api.get("/exhibition/analytics", { params });
    return response.data;
  },

  // Get event metrics
  getEventMetrics: async (eventId: number): Promise<any> => {
    const response = await api.get(`/exhibition/events/${eventId}/metrics`);
    return response.data;
  },

  // Bulk scan cards
  bulkScanCards: async (eventId: number, files: File[]): Promise<any> => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append("files", file);
    });
    const response = await api.post(`/exhibition/events/${eventId}/bulk-scan`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  // Legacy methods - deprecated, use new methods instead
  // Get card scans for an event (legacy)
  getCardScans: async (eventId: number, params?: {
    validation_status?: string;
    processing_status?: string;
    skip?: number;
    limit?: number;
  }): Promise<BusinessCardScan[]> => {
    return exhibitionService.getAllCardScans({ ...params, event_id: eventId });
  },

  // Get prospects for an event (legacy)
  getProspects: async (eventId: number, params?: {
    qualification_status?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<ExhibitionProspect[]> => {
    return exhibitionService.getAllProspects({ ...params, event_id: eventId });
  },

  // Convert prospect to lead (legacy - alias for convertProspectToCustomer)
  convertProspectToLead: async (eventId: number, prospectId: number): Promise<any> => {
    return exhibitionService.convertProspectToCustomer(prospectId);
  },

  // Send intro email (placeholder - needs backend implementation)
  sendIntroEmail: async (eventId: number, prospectId: number): Promise<any> => {
    const response = await api.post(`/exhibition/prospects/${prospectId}/send-intro-email`);
    return response.data;
  },
};

export default exhibitionService;
