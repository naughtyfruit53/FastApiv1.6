/**
 * Analytics Tracker Service
 * 
 * Tracks user behavior and interactions for mobile and demo UX optimization.
 * Collects page views, interactions, and user journey data.
 */

export interface AnalyticsEvent {
  id: string;
  type: 'page_view' | 'click' | 'form_submit' | 'navigation' | 'error' | 'custom';
  timestamp: Date;
  userId?: string;
  sessionId: string;
  page: string;
  module?: string;
  action?: string;
  element?: string;
  metadata?: Record<string, any>;
  deviceType: 'mobile' | 'tablet' | 'desktop';
  isDemoMode: boolean;
}

export interface UserSession {
  sessionId: string;
  userId?: string;
  startTime: Date;
  lastActivity: Date;
  events: AnalyticsEvent[];
  deviceType: 'mobile' | 'tablet' | 'desktop';
  isDemoMode: boolean;
}

export interface AnalyticsMetrics {
  totalPageViews: number;
  totalInteractions: number;
  averageSessionDuration: number;
  bounceRate: number;
  mostVisitedPages: Array<{ page: string; count: number }>;
  conversionFunnel: Array<{ step: string; completionRate: number }>;
}

class AnalyticsTracker {
  private sessionId: string;
  private userId?: string;
  private session: UserSession;
  private apiBaseUrl: string;
  private isEnabled: boolean;
  private eventQueue: AnalyticsEvent[] = [];
  private flushInterval: number = 30000; // 30 seconds
  private flushTimer: NodeJS.Timeout | null = null;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.isEnabled = true;
    
    this.session = {
      sessionId: this.sessionId,
      startTime: new Date(),
      lastActivity: new Date(),
      events: [],
      deviceType: this.detectDeviceType(),
      isDemoMode: this.checkDemoMode(),
    };

    // Start periodic flush
    this.startPeriodicFlush();
    
    // Track page unload
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        this.flush();
      });
    }
  }

  /**
   * Initialize analytics with user information
   */
  initialize(userId?: string): void {
    this.userId = userId;
    this.session.userId = userId;
  }

  /**
   * Track a page view
   */
  trackPageView(page: string, module?: string, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const event: AnalyticsEvent = {
      id: this.generateEventId(),
      type: 'page_view',
      timestamp: new Date(),
      userId: this.userId,
      sessionId: this.sessionId,
      page,
      module,
      metadata,
      deviceType: this.session.deviceType,
      isDemoMode: this.session.isDemoMode,
    };

    this.addEvent(event);
  }

  /**
   * Track a click event
   */
  trackClick(element: string, page: string, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const event: AnalyticsEvent = {
      id: this.generateEventId(),
      type: 'click',
      timestamp: new Date(),
      userId: this.userId,
      sessionId: this.sessionId,
      page,
      element,
      metadata,
      deviceType: this.session.deviceType,
      isDemoMode: this.session.isDemoMode,
    };

    this.addEvent(event);
  }

  /**
   * Track a form submission
   */
  trackFormSubmit(formName: string, page: string, success: boolean, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const event: AnalyticsEvent = {
      id: this.generateEventId(),
      type: 'form_submit',
      timestamp: new Date(),
      userId: this.userId,
      sessionId: this.sessionId,
      page,
      element: formName,
      metadata: {
        ...metadata,
        success,
      },
      deviceType: this.session.deviceType,
      isDemoMode: this.session.isDemoMode,
    };

    this.addEvent(event);
  }

  /**
   * Track a navigation event
   */
  trackNavigation(from: string, to: string, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const event: AnalyticsEvent = {
      id: this.generateEventId(),
      type: 'navigation',
      timestamp: new Date(),
      userId: this.userId,
      sessionId: this.sessionId,
      page: to,
      metadata: {
        ...metadata,
        from,
        to,
      },
      deviceType: this.session.deviceType,
      isDemoMode: this.session.isDemoMode,
    };

    this.addEvent(event);
  }

  /**
   * Track an error
   */
  trackError(error: Error, page: string, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const event: AnalyticsEvent = {
      id: this.generateEventId(),
      type: 'error',
      timestamp: new Date(),
      userId: this.userId,
      sessionId: this.sessionId,
      page,
      metadata: {
        ...metadata,
        error: error.message,
        stack: error.stack,
      },
      deviceType: this.session.deviceType,
      isDemoMode: this.session.isDemoMode,
    };

    this.addEvent(event);
  }

  /**
   * Track a custom event
   */
  trackCustomEvent(action: string, page: string, metadata?: Record<string, any>): void {
    if (!this.isEnabled) return;

    const event: AnalyticsEvent = {
      id: this.generateEventId(),
      type: 'custom',
      timestamp: new Date(),
      userId: this.userId,
      sessionId: this.sessionId,
      page,
      action,
      metadata,
      deviceType: this.session.deviceType,
      isDemoMode: this.session.isDemoMode,
    };

    this.addEvent(event);
  }

  /**
   * Add event to session and queue
   */
  private addEvent(event: AnalyticsEvent): void {
    this.session.events.push(event);
    this.session.lastActivity = new Date();
    this.eventQueue.push(event);

    // Flush if queue is large
    if (this.eventQueue.length >= 10) {
      this.flush();
    }
  }

  /**
   * Flush events to backend
   */
  async flush(): Promise<void> {
    if (this.eventQueue.length === 0) return;

    const eventsToSend = [...this.eventQueue];
    this.eventQueue = [];

    try {
      // In production, send to backend
      console.log('Flushing analytics events:', eventsToSend.length);
      
      // Mock API call - in production, uncomment and implement
      // await fetch(`${this.apiBaseUrl}/api/v1/analytics/events`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ events: eventsToSend }),
      // });
    } catch (error) {
      console.error('Error flushing analytics events:', error);
      // Re-queue events on failure
      this.eventQueue.unshift(...eventsToSend);
    }
  }

  /**
   * Start periodic flush timer
   */
  private startPeriodicFlush(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }

    this.flushTimer = setInterval(() => {
      this.flush();
    }, this.flushInterval);
  }

  /**
   * Get current session data
   */
  getSession(): UserSession {
    return this.session;
  }

  /**
   * Get session metrics
   */
  getSessionMetrics(): Partial<AnalyticsMetrics> {
    const events = this.session.events;
    const pageViews = events.filter(e => e.type === 'page_view');
    const interactions = events.filter(e => e.type === 'click' || e.type === 'form_submit');

    const sessionDuration = (this.session.lastActivity.getTime() - this.session.startTime.getTime()) / 1000;

    const pageCounts = pageViews.reduce((acc, event) => {
      acc[event.page] = (acc[event.page] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const mostVisitedPages = Object.entries(pageCounts)
      .map(([page, count]) => ({ page, count }))
      .sort((a, b) => b.count - a.count);

    return {
      totalPageViews: pageViews.length,
      totalInteractions: interactions.length,
      averageSessionDuration: sessionDuration,
      mostVisitedPages,
    };
  }

  /**
   * Enable/disable analytics
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  /**
   * Generate unique session ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate unique event ID
   */
  private generateEventId(): string {
    return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Detect device type
   */
  private detectDeviceType(): 'mobile' | 'tablet' | 'desktop' {
    if (typeof window === 'undefined') return 'desktop';
    
    const width = window.innerWidth;
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    return 'desktop';
  }

  /**
   * Check if in demo mode
   */
  private checkDemoMode(): boolean {
    if (typeof window === 'undefined') return false;
    return window.location.pathname.includes('/demo') || 
           localStorage.getItem('demoMode') === 'true';
  }

  /**
   * Cleanup
   */
  destroy(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    this.flush();
  }
}

// Export singleton instance
export const analyticsTracker = new AnalyticsTracker();
export default analyticsTracker;
