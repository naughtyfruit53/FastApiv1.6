// src/services/notificationWorkflow.ts
// Workflow integration utilities for triggering notifications from other modules

import api from '../lib/api';

export interface WorkflowNotificationTrigger {
  trigger_event: string;
  context_data: Record<string, any>;
}

export interface JobNotificationContext {
  job_id: number;
  job_title?: string;
  customer_id?: number;
  customer_name?: string;
  technician_id?: number;
  technician_name?: string;
  due_date?: string;
  priority?: string;
  service_type?: string;
}

export interface SLANotificationContext {
  sla_id: number;
  job_id: number;
  customer_id: number;
  breach_type: 'warning' | 'critical' | 'overdue';
  time_remaining?: number;
  expected_completion?: string;
}

export interface FeedbackNotificationContext {
  feedback_id: number;
  job_id: number;
  customer_id: number;
  customer_name?: string;
  technician_id?: number;
  rating?: number;
  requires_attention?: boolean;
}

// Notification workflow triggers for different modules

export class NotificationWorkflow {
  
  // Job Management Notifications
  static async triggerJobAssignment(context: JobNotificationContext): Promise<void> {
    try {
      await api.post('/api/v1/notifications/trigger', {
        trigger_event: 'job_assignment',
        context_data: {
          ...context,
          notification_type: 'job_assignment',
          subject: `New Job Assignment: ${context.job_title || `Job #${context.job_id}`}`,
          message: `You have been assigned to ${context.job_title || `job #${context.job_id}`} for ${context.customer_name || 'a customer'}.`
        }
      });
    } catch (error) {
      console.error('Failed to trigger job assignment notification:', error);
    }
  }

  static async triggerJobUpdate(context: JobNotificationContext & { update_type: string; details?: string }): Promise<void> {
    try {
      await api.post('/api/v1/notifications/trigger', {
        trigger_event: 'job_update',
        context_data: {
          ...context,
          notification_type: 'job_update',
          subject: `Job Update: ${context.job_title || `Job #${context.job_id}`}`,
          message: `Job ${context.job_id} has been updated: ${context.update_type}. ${context.details || ''}`
        }
      });
    } catch (error) {
      console.error('Failed to trigger job update notification:', error);
    }
  }

  static async triggerJobCompletion(context: JobNotificationContext): Promise<void> {
    try {
      await api.post('/api/v1/notifications/trigger', {
        trigger_event: 'job_completion',
        context_data: {
          ...context,
          notification_type: 'service_completion',
          subject: `Job Completed: ${context.job_title || `Job #${context.job_id}`}`,
          message: `Job ${context.job_id} for ${context.customer_name || 'customer'} has been completed successfully.`
        }
      });
    } catch (error) {
      console.error('Failed to trigger job completion notification:', error);
    }
  }

  // SLA Management Notifications
  static async triggerSLABreach(context: SLANotificationContext): Promise<void> {
    try {
      const urgencyMap = {
        warning: 'SLA Warning',
        critical: 'SLA Critical',
        overdue: 'SLA Breach'
      };

      await api.post('/api/v1/notifications/trigger', {
        trigger_event: 'sla_breach',
        context_data: {
          ...context,
          notification_type: 'sla_breach',
          subject: `${urgencyMap[context.breach_type]}: Job #${context.job_id}`,
          message: `Job ${context.job_id} is ${context.breach_type === 'overdue' ? 'overdue' : `approaching SLA deadline (${context.time_remaining || 'soon'})`}.`
        }
      });
    } catch (error) {
      console.error('Failed to trigger SLA breach notification:', error);
    }
  }

  // Feedback Management Notifications
  static async triggerFeedbackRequest(context: FeedbackNotificationContext): Promise<void> {
    try {
      await api.post('/api/v1/notifications/trigger', {
        trigger_event: 'feedback_request',
        context_data: {
          ...context,
          notification_type: 'feedback_request',
          subject: `Feedback Request: Job #${context.job_id}`,
          message: `Please provide feedback for the completed service job #${context.job_id}.`
        }
      });
    } catch (error) {
      console.error('Failed to trigger feedback request notification:', error);
    }
  }

  static async triggerFeedbackReceived(context: FeedbackNotificationContext): Promise<void> {
    try {
      await api.post('/api/v1/notifications/trigger', {
        trigger_event: 'feedback_received',
        context_data: {
          ...context,
          notification_type: 'follow_up',
          subject: `Feedback Received: Job #${context.job_id}`,
          message: `New feedback received for job #${context.job_id} from ${context.customer_name || 'customer'}${context.rating ? ` (Rating: ${context.rating}/5)` : ''}.`
        }
      });
    } catch (error) {
      console.error('Failed to trigger feedback received notification:', error);
    }
  }

  // Appointment Management Notifications
  static async triggerAppointmentReminder(context: {
    appointment_id: number;
    customer_id: number;
    customer_name?: string;
    technician_id?: number;
    appointment_date: string;
    service_type?: string;
    location?: string;
  }): Promise<void> {
    try {
      await api.post('/api/v1/notifications/trigger', {
        trigger_event: 'appointment_reminder',
        context_data: {
          ...context,
          notification_type: 'appointment_reminder',
          subject: `Appointment Reminder: ${context.service_type || 'Service'} on ${new Date(context.appointment_date).toLocaleDateString()}`,
          message: `Reminder: You have an appointment scheduled for ${context.service_type || 'service'} on ${new Date(context.appointment_date).toLocaleString()}.`
        }
      });
    } catch (error) {
      console.error('Failed to trigger appointment reminder notification:', error);
    }
  }

  // Dispatch Management Notifications
  static async triggerDispatchUpdate(context: {
    dispatch_id: number;
    technician_id: number;
    job_id: number;
    status: string;
    eta?: string;
    location?: string;
  }): Promise<void> {
    try {
      await api.post('/api/v1/notifications/trigger', {
        trigger_event: 'dispatch_update',
        context_data: {
          ...context,
          notification_type: 'job_update',
          subject: `Dispatch Update: Job #${context.job_id}`,
          message: `Dispatch status updated for job #${context.job_id}: ${context.status}${context.eta ? ` (ETA: ${context.eta})` : ''}.`
        }
      });
    } catch (error) {
      console.error('Failed to trigger dispatch update notification:', error);
    }
  }

  // System Notifications
  static async triggerSystemAlert(context: {
    alert_type: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    message: string;
    affected_users?: number[];
    organization_id?: number;
  }): Promise<void> {
    try {
      await api.post('/api/v1/notifications/trigger', {
        trigger_event: 'system_alert',
        context_data: {
          ...context,
          notification_type: 'system',
          subject: `System Alert: ${context.alert_type}`,
          message: context.message
        }
      });
    } catch (error) {
      console.error('Failed to trigger system alert notification:', error);
    }
  }

  // Batch notification utilities
  static async triggerBatchNotifications(triggers: WorkflowNotificationTrigger[]): Promise<void> {
    try {
      await Promise.all(
        triggers.map(trigger => 
          api.post('/api/v1/notifications/trigger', trigger)
        )
      );
    } catch (error) {
      console.error('Failed to trigger batch notifications:', error);
    }
  }

  // Utility method to trigger custom notifications
  static async triggerCustomNotification(
    eventType: string,
    subject: string,
    message: string,
    context: Record<string, any> = {}
  ): Promise<void> {
    try {
      await api.post('/api/v1/notifications/trigger', {
        trigger_event: eventType,
        context_data: {
          ...context,
          subject,
          message,
          custom_trigger: true
        }
      });
    } catch (error) {
      console.error('Failed to trigger custom notification:', error);
    }
  }
}

// React hooks for workflow integration
export const useNotificationWorkflow = () => {
  return {
    triggerJobAssignment: NotificationWorkflow.triggerJobAssignment,
    triggerJobUpdate: NotificationWorkflow.triggerJobUpdate,
    triggerJobCompletion: NotificationWorkflow.triggerJobCompletion,
    triggerSLABreach: NotificationWorkflow.triggerSLABreach,
    triggerFeedbackRequest: NotificationWorkflow.triggerFeedbackRequest,
    triggerFeedbackReceived: NotificationWorkflow.triggerFeedbackReceived,
    triggerAppointmentReminder: NotificationWorkflow.triggerAppointmentReminder,
    triggerDispatchUpdate: NotificationWorkflow.triggerDispatchUpdate,
    triggerSystemAlert: NotificationWorkflow.triggerSystemAlert,
    triggerCustomNotification: NotificationWorkflow.triggerCustomNotification,
  };
};

// Integration helper for existing modules
export const integrateNotificationsWithModule = (moduleName: string) => {
  console.log(`Notification integration available for ${moduleName} module`);
  
  return {
    // Generic trigger method for module-specific events
    trigger: (eventType: string, context: Record<string, any>) => {
      return NotificationWorkflow.triggerCustomNotification(
        `${moduleName}_${eventType}`,
        context.subject || `${moduleName} Event`,
        context.message || `Event triggered in ${moduleName}`,
        { ...context, module: moduleName }
      );
    },
    
    // Batch trigger for multiple events
    triggerBatch: (events: Array<{ eventType: string; context: Record<string, any> }>) => {
      const triggers = events.map(event => ({
        trigger_event: `${moduleName}_${event.eventType}`,
        context_data: { ...event.context, module: moduleName }
      }));
      return NotificationWorkflow.triggerBatchNotifications(triggers);
    }
  };
};

export default NotificationWorkflow;