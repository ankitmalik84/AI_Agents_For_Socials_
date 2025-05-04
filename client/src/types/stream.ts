export interface StreamStatus {
  stage: string;
  details: string;
}

export interface SearchInfo {
  stages: string[]; // ['searching', 'reading', 'writing', 'error']
  query: string;
  urls: string[];
  error?: string;
  results?: SearchResult[];
}

export interface SearchResult {
  title: string;
  url: string;
  content: string;
  score: number;
}

export interface ResearchEvent {
  type: "query" | "result" | "error" | "complete";
  query?: string;
  results?: SearchResult[];
  message?: string;
}

export interface StreamResponse {
  type:
    | "thread_id"
    | "content"
    | "search_start"
    | "search_results"
    | "search_error"
    | "end"
    | "error";
  thread_id?: string;
  content?: string;
  query?: string;
  results?: SearchResult[];
  urls?: string[];
  error?: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  id?: string;
  isLoading?: boolean;
  error?: string;
  searchInfo?: SearchInfo;
}
