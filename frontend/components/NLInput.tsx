"use client";
import { useState, KeyboardEvent } from "react";
import { Wand2, Loader2 } from "lucide-react";

interface Props {
  onSubmit: (query: string) => void;
  loading?: boolean;
  placeholder?: string;
  value?: string;
}

const SUGGESTIONS = [
  "Show total sales by category as a bar chart",
  "Monthly revenue trend for the last 6 months",
  "Top 10 customers by order value",
  "Revenue breakdown by region as a pie chart",
];

export default function NLInput({ onSubmit, loading, placeholder, value }: Props) {
  const [query, setQuery] = useState(value || "");
  const [showSuggestions, setShowSuggestions] = useState(false);

  const submit = () => {
    const q = query.trim();
    if (q && !loading) onSubmit(q);
  };

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="relative">
      <div className="flex gap-2 items-end bg-gray-900 border border-gray-700 rounded-xl p-3 focus-within:border-indigo-500 transition-colors">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKey}
          onFocus={() => setShowSuggestions(!query)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          placeholder={placeholder || "Describe the chart you want... (e.g. \"Show monthly revenue by category as a bar chart\")"}
          className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none focus:outline-none text-sm leading-relaxed min-h-[44px] max-h-32"
          rows={2}
        />
        <button
          onClick={submit}
          disabled={loading || !query.trim()}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-white text-sm font-medium px-4 py-2 rounded-lg shrink-0"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
          {loading ? "Building..." : "Build Chart"}
        </button>
      </div>

      {showSuggestions && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-gray-900 border border-gray-800 rounded-xl shadow-xl z-10 overflow-hidden">
          <div className="px-3 py-2 text-xs text-gray-500 border-b border-gray-800">Try asking:</div>
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onMouseDown={() => { setQuery(s); setShowSuggestions(false); }}
              className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
