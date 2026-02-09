/**
 * Chat types for AI chatbot integration
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
}

export interface ToolCall {
  name: string;
  parameters: Record<string, any>;
  result: {
    success: boolean;
    data?: any;
    error?: string;
  };
}

export interface ChatRequest {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls?: ToolCall[];
}

export interface Conversation {
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}
