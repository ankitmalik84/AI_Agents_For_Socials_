"use client";

import Output from "@/components/Output";
import TextArea from "@/components/TextArea";
import { type ChatOutput } from "@/types";
import { useState, FormEvent, useEffect } from "react";
import MessageBubble from "@/components/MessageBubble";
import ChatWindow from "@/components/ChatWindow";
import { Message, StreamResponse } from "@/types/stream";

interface StreamMessage extends Message {
  searchInfo?: {
    stages: string[];
    query: string;
    urls: string[];
    error?: string;
  };
}

export default function Home() {
  const [currentQuery, setCurrentQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentMessage, setCurrentMessage] = useState<StreamMessage | null>(
    null
  );

  const handleStream = async (e: FormEvent) => {
    e.preventDefault();
    if (!currentQuery.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: currentQuery,
    };

    setMessages((prev) => [...prev, userMessage]);
    setCurrentQuery("");
    setIsLoading(true);

    try {
      const assistantMessage: Message = {
        role: "assistant",
        content: "",
        isLoading: true,
        research: {
          queries: [],
          results: [],
        },
      };

      setCurrentMessage(assistantMessage);
      setMessages((prev) => [...prev, assistantMessage]);

      const response = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL}/stream/${encodeURIComponent(
          userMessage.content
        )}`
      );

      response.onmessage = (event) => {
        try {
          const data: StreamResponse = JSON.parse(event.data);

          setCurrentMessage((prev) => {
            if (!prev) return null;

            switch (data.type) {
              case "content":
                return {
                  ...prev,
                  content: prev.content + (data.content || ""),
                };

              case "research":
                if (!data.research) return prev;

                const research = prev.research || { queries: [], results: [] };

                switch (data.research.type) {
                  case "query":
                    return {
                      ...prev,
                      research: {
                        ...research,
                        queries: [...research.queries, data.research.query!],
                      },
                    };

                  case "result":
                    return {
                      ...prev,
                      research: {
                        ...research,
                        results: [
                          ...research.results,
                          ...(data.research.results || []),
                        ],
                      },
                    };

                  case "error":
                    return {
                      ...prev,
                      research: {
                        ...research,
                        error: data.research.message,
                      },
                    };

                  default:
                    return prev;
                }

              case "end":
                return {
                  ...prev,
                  isLoading: false,
                };

              case "error":
                return {
                  ...prev,
                  error: data.error,
                  isLoading: false,
                };

              default:
                return prev;
            }
          });
        } catch (error) {
          console.error("Error parsing SSE data:", error);
        }
      };

      response.onerror = (error) => {
        console.error("SSE error:", error);
        response.close();
        setIsLoading(false);
      };
    } catch (error) {
      console.error("Error:", error);
      setIsLoading(false);
    }
  };

  // Update messages when currentMessage changes
  useEffect(() => {
    if (currentMessage) {
      setMessages((prev) => [...prev.slice(0, -1), currentMessage]);
    }
  }, [currentMessage]);

  return (
    <div
      className={`container pt-10 pb-32 min-h-screen ${
        messages.length === 0 && "flex items-center justify-center"
      }`}
    >
      <div className="w-full">
        {messages.length === 0 && (
          <h1 className="text-4xl text-center mb-5">Ask me a Question!</h1>
        )}

        <ChatWindow messages={messages} />

        <TextArea
          onSubmit={handleStream}
          currentQuery={currentQuery}
          setCurrentQuery={setCurrentQuery}
        />
      </div>
    </div>
  );
}
