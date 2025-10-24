/**
 * WebSocket Client for Real-Time Demo Collaboration
 * 
 * Provides a TypeScript client for connecting to demo collaboration sessions
 * and handling real-time synchronization events.
 */

export interface Participant {
  user_id: string;
  user_name: string;
  connected_at: string;
}

export interface WSMessage {
  type: string;
  data?: any;
  timestamp?: string;
  session_id?: string;
  participants?: Participant[];
  message?: string;
}

export interface NavigationEvent {
  user_id: string;
  user_name: string;
  path: string;
  page_title?: string;
}

export interface InteractionEvent {
  user_id: string;
  user_name: string;
  action: string;
  element?: string;
  details?: any;
}

export interface CursorMoveEvent {
  user_id: string;
  user_name: string;
  x: number;
  y: number;
}

export type EventHandler = (data: any) => void;

class DemoWebSocketClient {
  private ws: WebSocket | null = null;
  private sessionId: string | null = null;
  private userId: string | null = null;
  private userName: string;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 1000;
  private eventHandlers: Map<string, Set<EventHandler>> = new Map();
  private isConnecting: boolean = false;

  constructor() {
    this.userName = 'Guest';
  }

  /**
   * Connect to a demo collaboration session
   */
  connect(sessionId: string, userId?: string, userName?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        console.log('Already connected to WebSocket');
        resolve();
        return;
      }

      if (this.isConnecting) {
        console.log('Connection already in progress');
        reject(new Error('Connection already in progress'));
        return;
      }

      this.isConnecting = true;
      this.sessionId = sessionId;
      this.userId = userId || null;
      this.userName = userName || 'Guest';

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = process.env.NEXT_PUBLIC_WS_URL || window.location.host;
      const wsUrl = `${protocol}//${host}/api/ws/demo/${sessionId}?user_id=${userId || ''}&user_name=${encodeURIComponent(this.userName)}`;

      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log(`Connected to demo session: ${sessionId}`);
          this.reconnectAttempts = 0;
          this.isConnecting = false;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WSMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket connection closed');
          this.isConnecting = false;
          this.ws = null;
          this.attemptReconnect();
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * Disconnect from the current session
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.sessionId = null;
    this.reconnectAttempts = 0;
  }

  /**
   * Attempt to reconnect after disconnect
   */
  private attemptReconnect(): void {
    if (!this.sessionId || this.reconnectAttempts >= this.maxReconnectAttempts) {
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`);

    setTimeout(() => {
      if (this.sessionId) {
        this.connect(this.sessionId, this.userId || undefined, this.userName)
          .catch(error => console.error('Reconnection failed:', error));
      }
    }, delay);
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(message: WSMessage): void {
    const handlers = this.eventHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error(`Error in event handler for ${message.type}:`, error);
        }
      });
    }
  }

  /**
   * Register an event handler
   */
  on(eventType: string, handler: EventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, new Set());
    }
    this.eventHandlers.get(eventType)!.add(handler);
  }

  /**
   * Unregister an event handler
   */
  off(eventType: string, handler: EventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  /**
   * Send a message through the WebSocket
   */
  private send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  /**
   * Send a navigation event
   */
  sendNavigation(path: string, pageTitle?: string): void {
    this.send({
      type: 'navigation',
      path,
      page_title: pageTitle
    });
  }

  /**
   * Send an interaction event
   */
  sendInteraction(action: string, element?: string, details?: any): void {
    this.send({
      type: 'interaction',
      action,
      element,
      details
    });
  }

  /**
   * Send a cursor move event (should be throttled on client side)
   */
  sendCursorMove(x: number, y: number): void {
    this.send({
      type: 'cursor_move',
      x,
      y
    });
  }

  /**
   * Send a demo state update
   */
  sendDemoState(state: any, changes?: any): void {
    this.send({
      type: 'demo_state',
      state,
      changes
    });
  }

  /**
   * Send a chat message to other participants
   */
  sendMessage(message: string): void {
    this.send({
      type: 'message',
      message
    });
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get current session ID
   */
  getSessionId(): string | null {
    return this.sessionId;
  }
}

// Export singleton instance
export const demoWebSocketClient = new DemoWebSocketClient();
export default demoWebSocketClient;
