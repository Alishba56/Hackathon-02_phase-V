'use client';

import { MessageCircle } from 'lucide-react';

interface ChatbotIconProps {
  onClick: () => void;
  hasNewMessages?: boolean;
}

export default function ChatbotIcon({ onClick, hasNewMessages = false }: ChatbotIconProps) {
  return (
    <button
      onClick={onClick}
      className={`
        fixed bottom-4 right-4 md:bottom-6 md:right-6 z-50
        w-12 h-12 md:w-14 md:h-14 rounded-full
        bg-gradient-to-r from-blue-500 to-purple-600
        hover:from-blue-600 hover:to-purple-700
        shadow-lg hover:shadow-xl
        transition-all duration-300 ease-in-out
        hover:scale-110
        flex items-center justify-center
        ${hasNewMessages ? 'animate-pulse' : ''}
      `}
      aria-label="Open chat"
    >
      <MessageCircle className="w-5 h-5 md:w-6 md:h-6 text-white" />
      {hasNewMessages && (
        <span className="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full border-2 border-white" />
      )}
    </button>
  );
}
