/**
 * API client for backend communication.
 */

import { supabase } from './supabase';
import type { Session, User, AgentType } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

/**
 * Get authorization headers with JWT token.
 */
async function getAuthHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();

  return {
    'Content-Type': 'application/json',
    ...(session?.access_token && {
      'Authorization': `Bearer ${session.access_token}`,
    }),
  };
}

/**
 * Custom API error class to preserve error details.
 */
export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    const message = typeof detail === 'string'
      ? detail
      : (detail as { message?: string })?.message || 'Request failed';
    super(message);
    this.status = status;
    this.detail = detail;
    this.name = 'ApiError';
  }
}

/**
 * API request wrapper with authentication.
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new ApiError(response.status, error.detail || 'Request failed');
  }

  return response.json();
}

// Auth API
export const authApi = {
  getMe: () => apiRequest<User>('/api/auth/me'),
  verify: () => apiRequest<{ valid: boolean; user_id: string }>('/api/auth/verify'),
};

// Conversation from database
interface ConversationRecord {
  id: string;
  session_id: string;
  role: string;
  content: string;
  thinking?: string;
  action?: Record<string, unknown>;
  created_at: string;
}

// Sessions API
export const sessionsApi = {
  create: (name?: string, agentType: AgentType = 'glm') =>
    apiRequest<Session>('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({ name, agent_type: agentType }),
    }),

  list: () => apiRequest<Session[]>('/api/sessions'),

  get: (sessionId: string) => apiRequest<Session>(`/api/sessions/${sessionId}`),

  delete: (sessionId: string) =>
    apiRequest<{ status: string }>(`/api/sessions/${sessionId}`, {
      method: 'DELETE',
    }),

  getConversations: (sessionId: string) =>
    apiRequest<{ conversations: ConversationRecord[] }>(`/api/sessions/${sessionId}/conversations`),
};

// Agent API
export const agentApi = {
  /**
   * Stop the currently running task.
   */
  stopTask: (sessionId: string) =>
    apiRequest<{ stopped: boolean; message: string }>(`/api/agent/${sessionId}/stop`, {
      method: 'POST',
    }),

  /**
   * Signal that manual takeover is complete.
   */
  completeTakeover: (sessionId: string) =>
    apiRequest<{ completed: boolean; message?: string }>(`/api/agent/${sessionId}/takeover/complete`, {
      method: 'POST',
    }),

  /**
   * Get session agent status.
   */
  getStatus: (sessionId: string) =>
    apiRequest<{
      is_connected: boolean;
      is_task_running: boolean;
      has_takeover: boolean;
    }>(`/api/agent/${sessionId}/status`),

  /**
   * Disconnect agent from session.
   */
  disconnectAgent: (sessionId: string) =>
    apiRequest<{ disconnected: boolean }>(`/api/agent/${sessionId}/agent`, {
      method: 'DELETE',
    }),
};

/**
 * SSE Event types from server
 */
export type SSEEventType =
  | 'ready'
  | 'thinking'
  | 'action'
  | 'screenshot'
  | 'takeover'
  | 'completed'
  | 'error'
  | 'stopped';

/**
 * SSE Event data structures
 */
export interface SSEEventData {
  ready: { session_id: string; device_id: string };
  thinking: { chunk?: string; full: string; duration?: number; timestamp: string };
  action: { action: Record<string, unknown>; duration?: number; timestamp: string };
  screenshot: { base64: string; width: number; height: number; timestamp: string };
  takeover: { message: string; timestamp: string };
  completed: { message?: string; timestamp: string };
  error: { message: string; timestamp?: string };
  stopped: { message: string; timestamp?: string };
}

/**
 * SSE connection handler type
 */
export interface SSEHandlers {
  onReady?: (data: SSEEventData['ready']) => void;
  onThinking?: (data: SSEEventData['thinking']) => void;
  onAction?: (data: SSEEventData['action']) => void;
  onScreenshot?: (data: SSEEventData['screenshot']) => void;
  onTakeover?: (data: SSEEventData['takeover']) => void;
  onCompleted?: (data: SSEEventData['completed']) => void;
  onError?: (data: SSEEventData['error']) => void;
  onStopped?: (data: SSEEventData['stopped']) => void;
  onConnectionError?: (error: Error) => void;
}

/**
 * Create SSE connection for task execution.
 * Returns an AbortController to allow cancellation.
 */
export async function runTaskWithSSE(
  sessionId: string,
  task: string,
  handlers: SSEHandlers,
  agentType: AgentType = 'glm'
): Promise<AbortController> {
  const abortController = new AbortController();
  const headers = await getAuthHeaders();

  // Start the fetch request
  const fetchPromise = fetch(
    `${API_URL}/api/agent/${sessionId}/task?agent_type=${agentType}`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify({ task }),
      signal: abortController.signal,
    }
  );

  // Process the response in the background
  fetchPromise
    .then(async (response) => {
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new ApiError(response.status, error.detail || 'Request failed');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // Process complete events in buffer
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // Keep incomplete event in buffer

        for (const eventStr of events) {
          if (!eventStr.trim()) continue;

          // Parse SSE format: "event: type\ndata: json"
          const lines = eventStr.split('\n');
          let eventType = '';
          let eventData = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.slice(7);
            } else if (line.startsWith('data: ')) {
              eventData = line.slice(6);
            }
          }

          if (!eventType || !eventData) continue;

          try {
            const data = JSON.parse(eventData);

            // Call appropriate handler based on event type
            switch (eventType as SSEEventType) {
              case 'ready':
                handlers.onReady?.(data);
                break;
              case 'thinking':
                handlers.onThinking?.(data);
                break;
              case 'action':
                handlers.onAction?.(data);
                break;
              case 'screenshot':
                handlers.onScreenshot?.(data);
                break;
              case 'takeover':
                handlers.onTakeover?.(data);
                break;
              case 'completed':
                handlers.onCompleted?.(data);
                break;
              case 'error':
                handlers.onError?.(data);
                break;
              case 'stopped':
                handlers.onStopped?.(data);
                break;
            }
          } catch (parseError) {
            console.error('Failed to parse SSE event data:', parseError, eventData);
          }
        }
      }
    })
    .catch((error) => {
      if (error.name === 'AbortError') {
        // Request was aborted, this is expected
        return;
      }
      console.error('SSE connection error:', error);
      handlers.onConnectionError?.(error);
    });

  return abortController;
}
