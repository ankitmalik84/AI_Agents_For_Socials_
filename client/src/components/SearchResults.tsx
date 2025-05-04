import { SearchResult } from "@/types/stream";

interface SearchResultsProps {
  query?: string;
  results?: SearchResult[];
  isSearching?: boolean;
}

export default function SearchResults({
  query,
  results,
  isSearching,
}: SearchResultsProps) {
  // Show component if we have any search activity
  const shouldShow = query || (results && results.length > 0) || isSearching;
  if (!shouldShow) return null;

  return (
    <div className="mt-4 mb-2 bg-gray-50 rounded-lg p-4">
      {/* Always show the search query */}
      <div className="mb-3">
        <p className="text-sm text-gray-600">
          {isSearching ? (
            <span className="flex items-center">
              <span className="animate-spin mr-2">⌛</span>
              Searching for: {query}
            </span>
          ) : (
            <span>Search results for: {query}</span>
          )}
        </p>
      </div>

      {/* Show results if available */}
      {results && results.length > 0 && (
        <div className="space-y-3">
          <div className="space-y-2">
            {results.map((result, idx) => (
              <div
                key={idx}
                className="border border-gray-200 rounded p-3 hover:border-blue-300 transition-colors"
              >
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 font-medium block"
                >
                  {result.title || "Untitled"}
                </a>
                <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                  {result.content.replace(/<[^>]*>?/g, "")}
                </p>
                <div className="flex justify-between items-center mt-2">
                  <p className="text-xs text-gray-400">
                    Relevance: {Math.round(result.score * 100)}%
                  </p>
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-500 hover:text-blue-700"
                  >
                    Read more →
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
