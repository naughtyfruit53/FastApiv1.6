// frontend/src/services/serviceDeskService.ts

import api from "../lib/api";

export interface Ticket {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  priority: string;
  status: string;
  category: string;
  customer_id?: number;
  assigned_to?: number;
  requested_by?: string;
  requested_email?: string;
  requested_phone?: string;
  resolution?: string;
  closed_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface ChatbotConversation {
  id: number;
  session_id: string;
  user_message: string;
  bot_response: string;
  intent_detected?: string;
  confidence_score?: number;
  escalated_to_human: boolean;
  conversation_stage: string;
  metadata?: any;
  created_at: string;
}

export interface ServiceDeskAnalytics {
  total_tickets: number;
  open_tickets: number;
  in_progress_tickets: number;
  resolved_tickets: number;
  pending_tickets: number;
  avg_resolution_time: number;
  first_response_time: number;
  customer_satisfaction_score: number;
  escalation_rate: number;
  chatbot_conversations: number;
  human_handoffs: number;
  chatbot_resolution_rate: number;
}

export interface SLAPolicy {
  id: number;
  name: string;
  priority: string;
  response_time_hours: number;
  resolution_time_hours: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

class ServiceDeskService {
  private endpoint = "/service-desk";

  /**
   * Get Service Desk analytics dashboard data
   */
  async getAnalytics(): Promise<ServiceDeskAnalytics> {
    try {
      const response = await api.get(`${this.endpoint}/analytics`);
      return response.data;
    } catch (error) {
      console.error("Error fetching Service Desk analytics:", error);
      throw error;
    }
  }

  /**
   * Get all tickets
   */
  async getTickets(
    skip: number = 0,
    limit: number = 100,
    status?: string,
  ): Promise<Ticket[]> {
    try {
      const params: any = { skip, limit };
      if (status) {
        params.status = status;
      }

      const response = await api.get(`${this.endpoint}/tickets`, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching tickets:", error);
      throw error;
    }
  }

  /**
   * Get ticket by ID
   */
  async getTicket(id: number): Promise<Ticket> {
    try {
      const response = await api.get(`${this.endpoint}/tickets/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching ticket ${id}:`, error);
      throw error;
    }
  }

  /**
   * Create new ticket
   */
  async createTicket(ticketData: any): Promise<Ticket> {
    try {
      const response = await api.post(`${this.endpoint}/tickets`, ticketData);
      return response.data;
    } catch (error) {
      console.error("Error creating ticket:", error);
      throw error;
    }
  }

  /**
   * Update ticket
   */
  async updateTicket(id: number, ticketData: any): Promise<Ticket> {
    try {
      const response = await api.put(
        `${this.endpoint}/tickets/${id}`,
        ticketData,
      );
      return response.data;
    } catch (error) {
      console.error(`Error updating ticket ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete ticket
   */
  async deleteTicket(id: number): Promise<void> {
    try {
      await api.delete(`${this.endpoint}/tickets/${id}`);
    } catch (error) {
      console.error(`Error deleting ticket ${id}:`, error);
      throw error;
    }
  }

  /**
   * Assign ticket to user
   */
  async assignTicket(id: number, userId: number): Promise<Ticket> {
    try {
      const response = await api.put(`${this.endpoint}/tickets/${id}/assign`, {
        assigned_to: userId,
      });
      return response.data;
    } catch (error) {
      console.error(`Error assigning ticket ${id}:`, error);
      throw error;
    }
  }

  /**
   * Close ticket
   */
  async closeTicket(id: number, resolution: string): Promise<Ticket> {
    try {
      const response = await api.put(`${this.endpoint}/tickets/${id}/close`, {
        resolution,
      });
      return response.data;
    } catch (error) {
      console.error(`Error closing ticket ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get chatbot conversations
   */
  async getChatbotConversations(
    skip: number = 0,
    limit: number = 100,
  ): Promise<ChatbotConversation[]> {
    try {
      const response = await api.get(`${this.endpoint}/chatbot/conversations`, {
        params: { skip, limit },
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching chatbot conversations:", error);
      throw error;
    }
  }

  /**
   * Get conversation by session ID
   */
  async getConversationBySession(
    sessionId: string,
  ): Promise<ChatbotConversation[]> {
    try {
      const response = await api.get(
        `${this.endpoint}/chatbot/conversations/${sessionId}`,
      );
      return response.data;
    } catch (error) {
      console.error(
        `Error fetching conversation for session ${sessionId}:`,
        error,
      );
      throw error;
    }
  }

  /**
   * Send message to chatbot
   */
  async sendChatbotMessage(
    sessionId: string,
    message: string,
  ): Promise<ChatbotConversation> {
    try {
      const response = await api.post(`${this.endpoint}/chatbot/message`, {
        session_id: sessionId,
        message: message,
      });
      return response.data;
    } catch (error) {
      console.error("Error sending chatbot message:", error);
      throw error;
    }
  }

  /**
   * Escalate conversation to human
   */
  async escalateToHuman(sessionId: string): Promise<Ticket> {
    try {
      const response = await api.post(`${this.endpoint}/chatbot/escalate`, {
        session_id: sessionId,
      });
      return response.data;
    } catch (error) {
      console.error(`Error escalating session ${sessionId} to human:`, error);
      throw error;
    }
  }

  /**
   * Get SLA policies
   */
  async getSLAPolicies(): Promise<SLAPolicy[]> {
    try {
      const response = await api.get(`${this.endpoint}/sla-policies`);
      return response.data;
    } catch (error) {
      console.error("Error fetching SLA policies:", error);
      throw error;
    }
  }

  /**
   * Get ticket SLA status
   */
  async getTicketSLA(ticketId: number): Promise<any> {
    try {
      const response = await api.get(
        `${this.endpoint}/tickets/${ticketId}/sla`,
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching SLA for ticket ${ticketId}:`, error);
      throw error;
    }
  }
}

export const serviceDeskService = new ServiceDeskService();
