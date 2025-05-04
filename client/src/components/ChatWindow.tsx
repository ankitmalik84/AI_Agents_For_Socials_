import { useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import { Message } from "@/types/stream";

interface ChatWindowProps {
  messages: Message[];
}

const ChatWindow = ({ messages }: ChatWindowProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="w-full max-w-4xl mx-auto mb-6">
      {messages.length === 0 ? (
        <div className="text-center my-20">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-cyan-400 bg-clip-text text-transparent">
            Welcome to AI Chat
          </h1>
          <p className="text-gray-500 text-lg">
            Start a conversation by typing your question below
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
