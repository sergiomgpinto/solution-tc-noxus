import React, { useState, useEffect, useRef } from 'react';
import { Message, Configuration, Conversation } from './types';
import { chatApi } from './api';
import './App.css';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [configurations, setConfigurations] = useState<Configuration[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showConversations, setShowConversations] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConfigurations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConfigurations = async () => {
    try {
      const configs = await chatApi.getConfigurations();
      setConfigurations(configs);
    } catch (error) {
      console.error('Failed to load configurations:', error);
    }
  };

  const loadConversations = async () => {
    try {
      const convs = await chatApi.getConversations();
      setConversations(convs);
      setShowConversations(true);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadConversation = async (conversationId: number) => {
    try {
      const messages = await chatApi.getConversationMessages(conversationId);
      setMessages(messages.filter(m => m.role !== 'system'));
      setCurrentConversationId(conversationId);
      setShowConversations(false);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(
        userMessage.content,
        currentConversationId || undefined
      );

      const assistantMessage: Message = {
        id: response.message_id,
        role: 'assistant',
        content: response.response,
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (!currentConversationId) {
        setCurrentConversationId(response.conversation_id);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Sorry, I encountered an error. Please try again.',
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (messageId: number, feedbackType: 'thumbs_up' | 'thumbs_down') => {
    try {
      await chatApi.sendFeedback({
        message_id: messageId,
        feedback_type: feedbackType,
      });

      setMessages(prev => prev.map(msg =>
        msg.id === messageId ? { ...msg, feedback: feedbackType } : msg
      ));
    } catch (error) {
      console.error('Failed to send feedback:', error);
    }
  };

  const handleConfigChange = async (configId: string) => {
    try {
      await chatApi.activateConfiguration(parseInt(configId));
      await loadConfigurations();
      startNewConversation();
    } catch (error) {
      console.error('Failed to change configuration:', error);
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setCurrentConversationId(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Adaptive Chatbot</h1>
        <div className="config-selector">
          <label htmlFor="config-select">Personality:</label>
          <select
            id="config-select"
            value={configurations.find(c => c.is_active)?.id || ''}
            onChange={(e) => handleConfigChange(e.target.value)}
          >
            {configurations.map(config => (
              <option key={config.id} value={config.id}>
                {config.name} {config.is_active && '(Active)'}
              </option>
            ))}
          </select>
        </div>
      </header>

      <div className="chat-container">
        <div className="messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                {message.content}
              </div>
              {message.role === 'assistant' && message.id && (
                <div className="feedback-buttons">
                  <button
                    className={message.feedback === 'thumbs_up' ? 'active' : ''}
                    onClick={() => handleFeedback(message.id!, 'thumbs_up')}
                  >
                    👍
                  </button>
                  <button
                    className={message.feedback === 'thumbs_down' ? 'active' : ''}
                    onClick={() => handleFeedback(message.id!, 'thumbs_down')}
                  >
                    👎
                  </button>
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button onClick={handleSendMessage} disabled={isLoading || !input.trim()}>
            Send
          </button>
        </div>
      </div>

      <div className="conversation-controls">
        <button onClick={startNewConversation}>New Conversation</button>
        <button onClick={loadConversations}>Previous Conversations</button>
      </div>

      {showConversations && (
        <div className="modal" onClick={() => setShowConversations(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="close" onClick={() => setShowConversations(false)}>
              &times;
            </span>
            <h2>Previous Conversations</h2>
            <div className="conversations-list">
              {conversations.map(conv => (
                <div
                  key={conv.id}
                  className="conversation-item"
                  onClick={() => loadConversation(conv.id)}
                >
                  <strong>{conv.title || 'Untitled Conversation'}</strong>
                  <br />
                  <small>{new Date(conv.updated_at).toLocaleString()}</small>
                  <br />
                  <small>{conv.message_count} messages</small>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;