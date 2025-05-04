"use client";

import ArrowIcon from "./ArrowIcon";
import { FormEvent } from "react";

interface TextAreaProps {
  onSubmit: (e: FormEvent, query: string) => Promise<void>;
  currentQuery: string;
  setCurrentQuery: (query: string) => void;
}

const TextArea = ({
  onSubmit,
  currentQuery,
  setCurrentQuery,
}: TextAreaProps) => {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-gray-50 via-gray-50 to-transparent pb-6 pt-10">
      <form
        onSubmit={(e) => onSubmit(e, currentQuery)}
        className="container max-w-4xl mx-auto flex gap-3"
      >
        <div className="w-full flex items-center bg-white rounded-2xl border shadow-sm">
          <textarea
            value={currentQuery}
            onChange={(e) => setCurrentQuery(e.target.value)}
            className="w-full p-4 bg-transparent text-gray-800 min-h-[60px] max-h-[200px] focus:outline-none resize-none placeholder-gray-400"
            placeholder="Ask me anything..."
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSubmit(e, currentQuery);
              }
            }}
          />

          <button
            type="submit"
            disabled={!currentQuery.trim()}
            className="disabled:opacity-50 disabled:cursor-not-allowed bg-blue-600 hover:bg-blue-700 transition-colors w-10 h-10 rounded-full shrink-0 flex items-center justify-center mr-2 text-white"
          >
            <ArrowIcon />
          </button>
        </div>
      </form>
    </div>
  );
};

export default TextArea;
