"use client";

import { ChevronDown, ChevronUp, Copy, Check, Play } from "lucide-react";
import { useState, useEffect } from "react";
interface Props {
  sql: string;
  onRunSQL?: (sql: string) => void;
}

export default function SQLPanel({ sql, onRunSQL }: Props) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  

  const [editedSQL, setEditedSQL] = useState(sql);

useEffect(() => {
  setEditedSQL(sql);
}, [sql]);

  const copy = async () => {
    await navigator.clipboard.writeText(editedSQL);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="border border-gray-800 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2 bg-gray-900 hover:bg-gray-800 transition-colors text-sm text-gray-400"
      >
        <span className="font-mono text-xs">SQL</span>
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {open && (
        <div className="bg-gray-950">
          <textarea
            value={editedSQL}
            onChange={(e) => setEditedSQL(e.target.value)}
            className="w-full font-mono text-xs text-green-400 bg-transparent p-4 focus:outline-none resize-none min-h-[120px]"
            spellCheck={false}
          />
          <div className="flex gap-2 px-4 pb-3">
            <button
              onClick={copy}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-300 transition-colors"
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              {copied ? "Copied" : "Copy"}
            </button>
            {onRunSQL && (
              <button
                onClick={() => onRunSQL(editedSQL)}
                className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 transition-colors ml-2"
              >
                <Play size={12} /> Run edited SQL
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
