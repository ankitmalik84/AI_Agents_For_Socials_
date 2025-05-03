import { Message, SearchResult, StreamStatus } from "@/types/stream";
import MarkdownRenderer from "./MarkdownRenderer";

const MessageBubble = ({ message }: { message: Message }) => {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] p-4 rounded-lg ${
          isUser
            ? "bg-blue-600 text-white rounded-tr-none"
            : "bg-gray-800 rounded-tl-none"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="space-y-4">
            {/* Main content */}
            <div className="prose dark:prose-invert prose-pre:whitespace-pre-wrap">
              <MarkdownRenderer content={message.content} />
            </div>

            {/* Search Results */}
            {message.research?.results &&
              message.research.results.length > 0 && (
                <div className="text-sm text-gray-400">
                  <p className="font-medium mb-2">Research Sources:</p>
                  <ul className="space-y-3">
                    {message.research.results.map((result, idx) => (
                      <li key={idx} className="border-l-2 border-blue-500 pl-3">
                        <div className="flex items-center gap-2">
                          <span className="text-xs px-2 py-0.5 bg-blue-500/10 rounded">
                            {result.source}
                          </span>
                          <a
                            href={result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-medium hover:underline"
                          >
                            {result.title}
                          </a>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                          {result.content}
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            {/* Status Updates */}
            {message.research?.queries &&
              message.research.queries.length > 0 && (
                <div className="text-sm text-gray-400">
                  <p className="font-medium mb-2">Progress:</p>
                  <ul className="list-none space-y-2">
                    {message.research.queries.map((query, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="mt-1.5 w-2 h-2 bg-blue-500 rounded-full shrink-0" />
                        <div>
                          <span className="font-medium">Searching:</span>
                          <span className="ml-1">{query}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            {/* Loading State */}
            {message.isLoading && (
              <div className="flex items-center gap-2 text-blue-400">
                <div className="animate-pulse">Processing</div>
                <div className="animate-bounce">...</div>
              </div>
            )}

            {/* Error Message */}
            {message.error && (
              <div className="text-red-400 text-sm">Error: {message.error}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
