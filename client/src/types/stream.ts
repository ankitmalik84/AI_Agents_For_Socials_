export interface StreamStatus {
  stage: string;
  details: string;
}

export interface SearchResult {
  title: string;
  url: string;
  content: string;
  source: "Research" | "Knowledge Base";
}

export interface ResearchEvent {
  type: "query" | "result" | "error" | "complete";
  query?: string;
  results?: SearchResult[];
  message?: string;
}

export interface StreamResponse {
  type: "status" | "content" | "research" | "error" | "end";
  content?: string;
  status?: {
    stage: string;
    details: string;
  };
  research?: ResearchEvent;
  error?: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  isLoading?: boolean;
  error?: string;
  research?: {
    queries: string[];
    results: SearchResult[];
    error?: string;
  };
}
