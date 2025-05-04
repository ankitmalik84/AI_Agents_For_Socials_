import { Message } from "@/types/stream";
import SearchResults from "./SearchResults";
import ReactMarkdown from "react-markdown";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isAssistant = message.role === "assistant";

  return (
    <div
      className={`flex ${isAssistant ? "justify-start" : "justify-end"} mb-4`}
    >
      <div
        className={`max-w-[85%] rounded-2xl p-4 shadow-sm ${
          isAssistant
            ? "bg-white border border-gray-200"
            : "bg-gradient-to-r from-blue-600 to-blue-700 text-white"
        }`}
      >
        {isAssistant && message.searchInfo && (
          <SearchResults
            query={message.searchInfo.query}
            results={message.searchInfo.results}
            isSearching={
              message.searchInfo.stages.includes("searching") &&
              !message.searchInfo.stages.includes("writing")
            }
          />
        )}

        <div
          className={`prose ${
            isAssistant ? "prose-gray" : "prose-invert"
          } max-w-none`}
        >
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {message.isLoading && (
          <div className="mt-2 flex items-center space-x-1">
            <div className="w-2 h-2 rounded-full bg-current animate-bounce"></div>
            <div className="w-2 h-2 rounded-full bg-current animate-bounce delay-100"></div>
            <div className="w-2 h-2 rounded-full bg-current animate-bounce delay-200"></div>
          </div>
        )}

        {message.error && (
          <div className="mt-2 text-red-500 text-sm font-medium">
            Error: {message.error}
          </div>
        )}
      </div>
    </div>
  );
}
