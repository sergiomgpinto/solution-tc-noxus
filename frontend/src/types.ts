export interface Message {
  id?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at?: string;
  feedback?: 'thumbs_up' | 'thumbs_down';
}

export interface ChatResponse {
  response: string;
  conversation_id: number;
  message_id: number;
}

export interface Configuration {
  id: number;
  name: string;
  description?: string;
  version: number;
  is_active: boolean;
  tags: string[];
  updated_at: string;
}

export interface Conversation {
  id: number;
  title?: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface FeedbackRequest {
  message_id: number;
  feedback_type: 'thumbs_up' | 'thumbs_down';
}