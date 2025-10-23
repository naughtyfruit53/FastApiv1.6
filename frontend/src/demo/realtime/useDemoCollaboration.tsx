/**
 * React Hook for Demo Collaboration
 * 
 * Provides React hooks for integrating real-time demo collaboration
 * features into components.
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import demoWebSocketClient, { Participant, WSMessage } from './websocketClient';

export interface CollaborationState {
  isConnected: boolean;
  participants: Participant[];
  sessionId: string | null;
  currentUser: {
    userId: string;
    userName: string;
  } | null;
}

export interface UseDemoCollaborationOptions {
  sessionId: string;
  userId?: string;
  userName?: string;
  autoConnect?: boolean;
  onUserJoined?: (data: any) => void;
  onUserLeft?: (data: any) => void;
  onNavigation?: (data: any) => void;
  onInteraction?: (data: any) => void;
  onMessage?: (data: any) => void;
}

export function useDemoCollaboration(options: UseDemoCollaborationOptions) {
  const {
    sessionId,
    userId = 'anonymous',
    userName = 'Guest',
    autoConnect = true,
    onUserJoined,
    onUserLeft,
    onNavigation,
    onInteraction,
    onMessage,
  } = options;

  const [state, setState] = useState<CollaborationState>({
    isConnected: false,
    participants: [],
    sessionId: null,
    currentUser: null,
  });

  const [error, setError] = useState<Error | null>(null);
  const handlersRegistered = useRef(false);

  // Connect to session
  const connect = useCallback(async () => {
    try {
      await demoWebSocketClient.connect(sessionId, userId, userName);
      setState(prev => ({
        ...prev,
        isConnected: true,
        sessionId,
        currentUser: { userId, userName },
      }));
      setError(null);
    } catch (err) {
      setError(err as Error);
      console.error('Failed to connect to demo session:', err);
    }
  }, [sessionId, userId, userName]);

  // Disconnect from session
  const disconnect = useCallback(() => {
    demoWebSocketClient.disconnect();
    setState(prev => ({
      ...prev,
      isConnected: false,
      sessionId: null,
    }));
  }, []);

  // Send navigation event
  const sendNavigation = useCallback((path: string, pageTitle?: string) => {
    demoWebSocketClient.sendNavigation(path, pageTitle);
  }, []);

  // Send interaction event
  const sendInteraction = useCallback((action: string, element?: string, details?: any) => {
    demoWebSocketClient.sendInteraction(action, element, details);
  }, []);

  // Send chat message
  const sendChatMessage = useCallback((message: string) => {
    demoWebSocketClient.sendMessage(message);
  }, []);

  // Register event handlers
  useEffect(() => {
    if (handlersRegistered.current) return;

    // Handle connection established
    const handleConnected = (data: WSMessage) => {
      setState(prev => ({
        ...prev,
        participants: data.participants || [],
      }));
    };

    // Handle user joined
    const handleUserJoined = (data: WSMessage) => {
      if (data.data) {
        setState(prev => ({
          ...prev,
          participants: [
            ...prev.participants,
            {
              user_id: data.data.user_id,
              user_name: data.data.user_name,
              connected_at: data.timestamp || new Date().toISOString(),
            },
          ],
        }));
      }
      onUserJoined?.(data);
    };

    // Handle user left
    const handleUserLeft = (data: WSMessage) => {
      if (data.data) {
        setState(prev => ({
          ...prev,
          participants: prev.participants.filter(
            p => p.user_id !== data.data.user_id
          ),
        }));
      }
      onUserLeft?.(data);
    };

    // Handle navigation events
    const handleNavigation = (data: WSMessage) => {
      onNavigation?.(data);
    };

    // Handle interaction events
    const handleInteraction = (data: WSMessage) => {
      onInteraction?.(data);
    };

    // Handle chat messages
    const handleMessage = (data: WSMessage) => {
      onMessage?.(data);
    };

    // Register handlers
    demoWebSocketClient.on('connected', handleConnected);
    demoWebSocketClient.on('user_joined', handleUserJoined);
    demoWebSocketClient.on('user_left', handleUserLeft);
    demoWebSocketClient.on('navigation', handleNavigation);
    demoWebSocketClient.on('interaction', handleInteraction);
    demoWebSocketClient.on('message', handleMessage);

    handlersRegistered.current = true;

    // Cleanup
    return () => {
      demoWebSocketClient.off('connected', handleConnected);
      demoWebSocketClient.off('user_joined', handleUserJoined);
      demoWebSocketClient.off('user_left', handleUserLeft);
      demoWebSocketClient.off('navigation', handleNavigation);
      demoWebSocketClient.off('interaction', handleInteraction);
      demoWebSocketClient.off('message', handleMessage);
      handlersRegistered.current = false;
    };
  }, [onUserJoined, onUserLeft, onNavigation, onInteraction, onMessage]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect && sessionId) {
      connect();
    }

    return () => {
      if (autoConnect) {
        disconnect();
      }
    };
  }, [autoConnect, sessionId, connect, disconnect]);

  return {
    ...state,
    error,
    connect,
    disconnect,
    sendNavigation,
    sendInteraction,
    sendChatMessage,
  };
}

export default useDemoCollaboration;
