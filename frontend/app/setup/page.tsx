"use client";
import { useEffect, useState } from "react";
import { Database, RefreshCw, Table, ChevronDown, ChevronRight } from "lucide-react";
import { api, type SchemaFile } from "@/lib/api";

export default function SetupPage() {
  const [files, setFiles] = useState<SchemaFile[]>([]);
  const [health, setHealth] = useState<{ csv_files: number; model_path_set: boolean } | null>(null);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      const [schema, h] = await Promise.all([api.getSchema(), api.health()]);
      setFiles(schema.files);
      setHealth(h);
      if (schema.files.length > 0) {
        setExpanded(new Set([schema.files[0].id]));
      }
    } finally {
      setLoading(false);
    }
  };

  const refresh = async () => {
    setRefreshing(true);
    try {
      const schema = await api.refreshSchema();
      setFiles(schema.files);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, []);

  const toggle = (id: number) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Data Sources</h1>
        <button
          onClick={refresh}
          disabled={refreshing}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={refreshing ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {health && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <div className="text-xs text-gray-500 mb-1">CSV Files Loaded</div>
            <div className="text-2xl font-bold text-white">{health.csv_files}</div>
          </div>

        </div>
      )}

      <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 text-sm text-amber-200/80">
        <span className="font-medium text-amber-300">How to add data:</span> Drop any{" "}
        <code className="bg-amber-500/20 px-1 rounded">.csv</code> files into the{" "}
        <code className="bg-amber-500/20 px-1 rounded">data_dashboard/csvs/</code> folder.
        Schema is auto-detected within seconds.
      </div>

      {loading && (
        <div className="text-center text-gray-500 py-12">Loading schema...</div>
      )}

      {!loading && files.length === 0 && (
        <div className="border-2 border-dashed border-gray-800 rounded-xl p-12 text-center">
          <Database size={32} className="text-gray-700 mx-auto mb-3" />
          <div className="text-gray-400 font-medium mb-1">No CSV files found</div>
          <div className="text-gray-600 text-sm">
            Add CSV files to <code className="text-gray-500">data_dashboard/csvs/</code>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {files.map((file) => (
          <div key={file.id} className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <button
              onClick={() => toggle(file.id)}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-800/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Table size={16} className="text-indigo-400" />
                <span className="font-medium text-white">{file.filename}</span>
                <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">
                  {file.row_count?.toLocaleString()} rows · {file.columns.length} columns
                </span>
              </div>
              {expanded.has(file.id) ? (
                <ChevronDown size={16} className="text-gray-500" />
              ) : (
                <ChevronRight size={16} className="text-gray-500" />
              )}
            </button>

            {expanded.has(file.id) && (
              <div className="border-t border-gray-800 overflow-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-950">
                      <th className="px-4 py-2 text-left text-gray-500 font-medium">Column</th>
                      <th className="px-4 py-2 text-left text-gray-500 font-medium">Type</th>
                      <th className="px-4 py-2 text-left text-gray-500 font-medium">Sample Values</th>
                    </tr>
                  </thead>
                  <tbody>
                    {file.columns.map((col, i) => (
                      <tr key={i} className="border-t border-gray-800/50">
                        <td className="px-4 py-2 font-mono text-gray-200 text-xs">{col.column_name}</td>
                        <td className="px-4 py-2">
                          <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded font-mono">
                            {col.data_type}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-gray-500 text-xs">
                          {col.sample_values.slice(0, 4).join(", ")}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
