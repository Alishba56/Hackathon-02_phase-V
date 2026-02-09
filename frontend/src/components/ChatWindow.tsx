'use client';

import { useState, useRef, useEffect } from 'react';
import { X, Send, Loader2 } from 'lucide-react';
import type { ChatMessage } from '@/types/chat';

interface ChatWindowProps {
  isOpen: boolean;
  onClose: () => void;
  messages: ChatMessage[];
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
  error?: string | null;
  onRetry?: () => void;
}

export default function ChatWindow({
  isOpen,
  onClose,
  messages,
  onSendMessage,
  isLoading,
  error,
  onRetry
}: ChatWindowProps) {
  const [inputMessage, setInputMessage] = useState('');
  const [displayedMessages, setDisplayedMessages] = useState<ChatMessage[]>([]);
  const [typingMessageIndex, setTypingMessageIndex] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Simulate typing effect for new assistant messages
  useEffect(() => {
    if (messages.length === 0) {
      setDisplayedMessages([]);
      return;
    }

    const lastMessage = messages[messages.length - 1];
    const lastDisplayedMessage = displayedMessages[displayedMessages.length - 1];

    // Check if there's a new message
    if (!lastDisplayedMessage || lastMessage.id !== lastDisplayedMessage.id) {
      if (lastMessage.role === 'assistant') {
        // Start typing effect for assistant message
        setTypingMessageIndex(messages.length - 1);

        // Add message with empty content first
        setDisplayedMessages([...messages.slice(0, -1), { ...lastMessage, content: '' }]);

        // Simulate typing
        let currentIndex = 0;
        const typingInterval = setInterval(() => {
          currentIndex++;
          if (currentIndex <= lastMessage.content.length) {
            setDisplayedMessages(prev => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                ...lastMessage,
                content: lastMessage.content.substring(0, currentIndex)
              };
              return updated;
            });
          } else {
            clearInterval(typingInterval);
            setTypingMessageIndex(null);
          }
        }, 20); // 20ms per character for smooth typing

        return () => clearInterval(typingInterval);
      } else {
        // User message - display immediately
        setDisplayedMessages(messages);
      }
    }
  }, [messages]);

  // Auto-scroll to bottom when displayed messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [displayedMessages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSend = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const message = inputMessage.trim();
    setInputMessage('');
    await onSendMessage(message);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-20 right-4 md:bottom-24 md:right-6 z-50 w-[calc(100vw-2rem)] md:w-96 h-[70vh] md:h-[600px] max-h-[600px] bg-white dark:bg-gray-800 rounded-lg shadow-2xl flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-3 md:p-4 border-b dark:border-gray-700 bg-gradient-to-r from-blue-500 to-purple-600 rounded-t-lg">
        <h3 className="text-base md:text-lg font-semibold text-white">AI Todo Assistant</h3>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-200 transition-colors"
          aria-label="Close chat"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 md:p-4 space-y-3 md:space-y-4">
        {displayedMessages.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
            <p className="text-sm">👋 Hi! I&apos;m your AI assistant.</p>
            <p className="text-sm mt-2">Ask me to manage your tasks!</p>
            <p className="text-xs mt-4 text-gray-400">
              Try: &quot;Add task: Buy groceries&quot; or &quot;Show all my tasks&quot;
            </p>
          </div>
        ) : (
          displayedMessages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`
                  max-w-[85%] md:max-w-[80%] rounded-lg px-3 md:px-4 py-2
                  ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                  }
                `}
              >
                <p className="text-xs md:text-sm whitespace-pre-wrap break-words">{message.content}</p>
                {message.toolCalls && message.toolCalls.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600">
                    <p className="text-xs opacity-75">
                      🔧 {message.toolCalls.length} tool{message.toolCalls.length > 1 ? 's' : ''} used
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-2">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        {/* Error message with retry */}
        {error && (
          <div className="flex justify-center">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg px-4 py-3 max-w-[80%]">
              <p className="text-sm text-red-800 dark:text-red-200 mb-2">{error}</p>
              {onRetry && (
                <button
                  onClick={onRetry}
                  className="text-xs text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 underline"
                >
                  Try again
                </button>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 md:p-4 border-t dark:border-gray-700">
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            className="
              flex-1 px-3 md:px-4 py-2 rounded-lg text-sm md:text-base
              border border-gray-300 dark:border-gray-600
              bg-white dark:bg-gray-700
              text-gray-900 dark:text-gray-100
              placeholder-gray-400 dark:placeholder-gray-500
              focus:outline-none focus:ring-2 focus:ring-blue-500
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          />
          <button
            onClick={handleSend}
            disabled={!inputMessage.trim() || isLoading}
            className="
              px-3 md:px-4 py-2 rounded-lg
              bg-blue-500 hover:bg-blue-600
              text-white
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
              flex items-center justify-center
            "
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 md:w-5 md:h-5 animate-spin" />
            ) : (
              <Send className="w-4 h-4 md:w-5 md:h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
