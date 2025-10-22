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

const exhibitionService = {
  // Get all exhibition events
  getEvents: async (params?: {
    status?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<ExhibitionEvent[]> => {
    const response = await api.get("/api/v1/exhibition/events", { params });
    return response.data;
  },

  // Get single exhibition event
  getEvent: async (eventId: number): Promise<ExhibitionEvent> => {
    const response = await api.get(`/api/v1/exhibition/events/${eventId}`);
    return response.data;
  },

  // Create exhibition event
  createEvent: async (eventData: Partial<ExhibitionEvent>): Promise<ExhibitionEvent> => {
    const response = await api.post("/api/v1/exhibition/events", eventData);
    return response.data;
  },

  // Update exhibition event
  updateEvent: async (eventId: number, eventData: Partial<ExhibitionEvent>): Promise<ExhibitionEvent> => {
    const response = await api.put(`/api/v1/exhibition/events/${eventId}`, eventData);
    return response.data;
  },

  // Get card scans for an event
  getCardScans: async (eventId: number, params?: {
    validation_status?: string;
    processing_status?: string;
    skip?: number;
    limit?: number;
  }): Promise<BusinessCardScan[]> => {
    const response = await api.get(`/api/v1/exhibition/events/${eventId}/scans`, { params });
    return response.data;
  },

  // Upload and scan business card
  scanBusinessCard: async (eventId: number, file: File): Promise<BusinessCardScan> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post(`/api/v1/exhibition/events/${eventId}/scans`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  // Get prospects for an event
  getProspects: async (eventId: number, params?: {
    qualification_status?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<ExhibitionProspect[]> => {
    const response = await api.get(`/api/v1/exhibition/events/${eventId}/prospects`, { params });
    return response.data;
  },

  // Create prospect
  createProspect: async (eventId: number, prospectData: Partial<ExhibitionProspect>): Promise<ExhibitionProspect> => {
    const response = await api.post(`/api/v1/exhibition/events/${eventId}/prospects`, prospectData);
    return response.data;
  },

  // Update prospect
  updateProspect: async (eventId: number, prospectId: number, prospectData: Partial<ExhibitionProspect>): Promise<ExhibitionProspect> => {
    const response = await api.put(`/api/v1/exhibition/events/${eventId}/prospects/${prospectId}`, prospectData);
    return response.data;
  },

  // Convert prospect to lead
  convertProspectToLead: async (eventId: number, prospectId: number): Promise<any> => {
    const response = await api.post(`/api/v1/exhibition/events/${eventId}/prospects/${prospectId}/convert-to-lead`);
    return response.data;
  },

  // Send intro email
  sendIntroEmail: async (eventId: number, prospectId: number): Promise<any> => {
    const response = await api.post(`/api/v1/exhibition/events/${eventId}/prospects/${prospectId}/send-intro-email`);
    return response.data;
  },
};

export default exhibitionService;
