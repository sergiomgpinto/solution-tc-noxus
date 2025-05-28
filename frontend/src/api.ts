import axios from 'axios';
import { ChatResponse, Configuration, Conversation, Message, FeedbackRequest } from './types';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatApi = {
  sendMessage: async (message: string, conversationId?: number): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat', {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  },

  getConversations: async (): Promise<Conversation[]> => {
    const response = await api.get<Conversation[]>('/conversations');
    return response.data;
  },

  getConversationMessages: async (conversationId: number): Promise<Message[]> => {
    const response = await api.get<Message[]>(`/conversations/${conversationId}/messages`);
    return response.data;
  },

  sendFeedback: async (feedback: FeedbackRequest): Promise<void> => {
    await api.post('/feedback', feedback);
  },

  getConfigurations: async (): Promise<Configuration[]> => {
    const response = await api.get<Configuration[]>('/configurations');
    return response.data;
  },

  activateConfiguration: async (configId: number): Promise<void> => {
    await api.post(`/configurations/${configId}/activate`);
  },
};