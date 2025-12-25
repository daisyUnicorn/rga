/**
 * Type definitions for the Phone Agent Web application.
 */

// User types
export interface User {
  id: string;
  email?: string;
  name?: string;
  avatar_url?: string;
}

// Session types
export type SessionStatus = 'creating' | 'active' | 'paused' | 'closed' | 'error';

// Agent types
export type AgentType = 'glm' | 'gelab';

export interface AgentOption {
  value: AgentType;
  label: string;
  description: string;
}

export const AGENT_OPTIONS: AgentOption[] = [
  {
    value: 'glm',
    label: 'AutoGLM Agent',
    description: '基于 AutoGLM GLM phone 模型，思考更强',
  },
  {
    value: 'gelab',
    label: 'StepFun Agent',
    description: '基于 Step GUI 模型，推理更快',
  },
];

export interface Session {
  id: string;
  user_id: string;
  agentbay_session_id?: string;
  resource_url?: string;
  device_id?: string;
  status: SessionStatus;
  name?: string;
  agent_type?: AgentType;
  created_at: string;
  updated_at: string;
}

// Message types
export type MessageRole = 'user' | 'assistant' | 'system';

// Step in agent execution
export interface AgentStep {
  id: string;
  stepNumber: number;
  thinking?: string;
  thinkingDuration?: number; // Duration in seconds for thinking/model inference
  action?: Record<string, unknown>;
  actionDuration?: number; // Duration in seconds for action execution
  status: 'thinking' | 'acting' | 'completed' | 'error';
  timestamp: Date;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  thinking?: string;
  action?: Record<string, unknown>;
  steps?: AgentStep[]; // Array of execution steps
  timestamp: Date;
  isStreaming?: boolean;
}

// SSE event types
export type EventType =
  | 'ready'
  | 'thinking'
  | 'action'
  | 'screenshot'
  | 'takeover'
  | 'completed'
  | 'error'
  | 'stopped';

export interface StreamEvent {
  type: EventType;
  data: unknown;
  timestamp: string;
}

// Takeover types
export interface TakeoverState {
  isActive: boolean;
  message?: string;
}

