"use client";

import TextArea from "@/components/TextArea";
import { useState, FormEvent } from "react";
import ChatWindow from "@/components/ChatWindow";
import { Message, StreamResponse, SearchInfo } from "@/types/stream";
import { v4 as uuid } from "uuid";

export default function Home() {
  const [currentQuery, setCurrentQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  const handleStream = async (e: FormEvent) => {
    e.preventDefault();
    if (!currentQuery.trim()) return;

    // Add user message to the chat
    const userMessage: Message = {
      role: "user",
      content: currentQuery,
    };

    // Generate unique ID for AI response
    const aiResponseId = uuid();
    let streamedContent = "";
    let searchData: SearchInfo | null = null;

    const assistantMessage: Message = {
      id: aiResponseId,
      role: "assistant",
      content: "",
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setCurrentQuery("");

    try {
      const response = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL}/stream/${encodeURIComponent(
          userMessage.content
        )}`
      );

      response.onmessage = (event) => {
        try {
          const data: StreamResponse = JSON.parse(event.data);
          console.log("Received event:", data);

          switch (data.type) {
            case "content":
              if (data.content) {
                streamedContent += data.content;
                updateMessage(aiResponseId, {
                  content: streamedContent,
                  isLoading: true,
                });
              }
              break;

            case "search_start":
              if (data.query) {
                const newSearchInfo: SearchInfo = {
                  stages: ["searching"],
                  query: data.query,
                  urls: [],
                };
                searchData = newSearchInfo;
                updateMessage(aiResponseId, {
                  searchInfo: newSearchInfo,
                });
              }
              break;

            case "search_results":
              if (searchData && data.results) {
                const newSearchInfo: SearchInfo = {
                  stages: ["searching", "reading"],
                  query: searchData.query,
                  urls: data.urls || [],
                  results: data.results,
                };
                searchData = newSearchInfo;

                updateMessage(aiResponseId, {
                  content: streamedContent,
                  searchInfo: newSearchInfo,
                  isLoading: true,
                });
              }
              break;

            case "search_error":
              if (searchData) {
                const newSearchInfo: SearchInfo = {
                  stages: [...searchData.stages, "error"],
                  query: searchData.query,
                  urls: searchData.urls,
                  error: data.error,
                };
                searchData = newSearchInfo;
                updateMessage(aiResponseId, {
                  searchInfo: newSearchInfo,
                });
              }
              break;

            case "end":
              if (searchData) {
                const finalSearchInfo: SearchInfo = {
                  ...searchData,
                  stages: ["searching", "reading", "writing"],
                };
                updateMessage(aiResponseId, {
                  content: streamedContent,
                  searchInfo: finalSearchInfo,
                  isLoading: false,
                });
              } else {
                updateMessage(aiResponseId, {
                  content: streamedContent,
                  isLoading: false,
                });
              }
              response.close();
              break;

            case "error":
              updateMessage(aiResponseId, {
                error: data.error,
                isLoading: false,
              });
              response.close();
              break;
          }
        } catch (error) {
          console.error("Error parsing event data:", error);
        }
      };

      response.onerror = (error) => {
        console.error("EventSource error:", error);
        response.close();
      };
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const updateMessage = (id: string, updates: Partial<Message>) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === id ? { ...msg, ...updates } : msg))
    );
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container max-w-4xl mx-auto pt-6 pb-32">
        <ChatWindow messages={messages} />

        <TextArea
          onSubmit={handleStream}
          currentQuery={currentQuery}
          setCurrentQuery={setCurrentQuery}
        />
      </div>
    </main>
  );
}
