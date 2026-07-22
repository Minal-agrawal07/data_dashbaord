"use client";
import { useState } from "react";
import { MessageSquare, Plus, LayoutDashboard, AlertCircle, RefreshCw, Download } from "lucide-react";
import NLInput from "@/components/NLInput";
import ChartRenderer from "@/components/ChartRenderer";
import SQLPanel from "@/components/SQLPanel";
import { api, type GenerateResponse, type ConversationTurn } from "@/lib/api";

interface ChartState {
  chartId?: number;
  response: GenerateResponse;
  history: ConversationTurn[];
}

export default function BuilderPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [current, setCurrent] = useState<ChartState | null>(null);
  const [pendingClarification, setPendingClarification] = useState<string | null>(null);

  const handleQuery = async (query: string) => {
    setLoading(true);
    setError(null);
    setPendingClarification(null);

    const history: ConversationTurn[] = current
      ? [...current.history, { role: "user", content: query }]
      : [{ role: "user", content: query }];

    try {
      let res: GenerateResponse;

      if (current?.chartId) {
        res = await api.refineChart(current.chartId, {
          nl_query: query,
          chart_id: current.chartId,
          conversation_history: history,
        });
      } else {
        res = await api.generateChart({ nl_query: query, conversation_history: history });
      }

      if (res.clarification_needed) {
        setPendingClarification(res.question || "Can you clarify your request?");
        return;
      }

      const newHistory: ConversationTurn[] = [
        ...history,
        { role: "assistant", content: "Chart generated.", sql: res.sql },
      ];

      setCurrent({ chartId: res.chart_id, response: res, history: newHistory });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleRunSQL = async (sql: string) => {
    setLoading(true);
    setError(null);
    try {
      const intent = current?.response.intent;
      const res = await api.runSQL(sql, typeof intent === "string" ? intent : "");
      if (current) {
        setCurrent({ ...current, response: { ...current.response, ...res } });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "SQL failed");
    } finally {
      setLoading(false);
    }
  };

  const startFresh = () => {
    setCurrent(null);
    setError(null);
    setPendingClarification(null);
  };

  const res = current?.response;

const BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const downloadChart = () => {
  window.open(
    `${BASE}/api/charts/download?t=${Date.now()}`,
    "_blank"
  );
};
  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Chart Builder</h1>
        {current && (
          <button
            onClick={startFresh}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            <RefreshCw size={14} /> New chart
          </button>
        )}
      </div>

      <NLInput
        onSubmit={handleQuery}
        loading={loading}
        placeholder={
          current
            ? "Refine: \"make it a line chart\", \"add a filter\", \"break down by region\"..."
            : undefined
        }
      />

      {pendingClarification && (
        <div className="flex gap-3 bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
          <AlertCircle size={18} className="text-amber-400 shrink-0 mt-0.5" />
          <div>
            <div className="text-amber-300 font-medium text-sm mb-1">Clarification needed</div>
            <div className="text-amber-200/80 text-sm">{pendingClarification}</div>
          </div>
        </div>
      )}

      {error && (
        <div className="flex gap-3 bg-red-500/10 border border-red-500/30 rounded-xl p-4">
          <AlertCircle size={18} className="text-red-400 shrink-0 mt-0.5" />
          <div className="text-red-300 text-sm">{error}</div>
        </div>
      )}

      {res && !res.clarification_needed && (
        <div className="space-y-4">
          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <MessageSquare size={14} />
                <span className="font-mono text-xs truncate max-w-md">
                  {current?.history.filter(h => h.role === "user").slice(-1)[0]?.content}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-600 bg-gray-800 px-2 py-0.5 rounded">
                  {res.chart_type} · {res.row_count?.toLocaleString()} rows
                </span>
              </div>
            </div>

            <div className="p-4 space-y-5">
              {res.chart_config && (
                <>
                <ChartRenderer
                  chartConfig={res.chart_config}
                  chartType={res.chart_type || "bar"}
                  data={res.data}
                />
                <div className="flex justify-end">
  <button
  onClick={downloadChart}
  className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg text-white text-sm transition"
>
  <Download size={16} />
  Download Chart
</button>
</div>
</>
                
              )}
            </div>
          </div>

          {res.sql && (
            <SQLPanel sql={res.sql} onRunSQL={handleRunSQL} />
          )}

          {/* {current?.history && current.history.length > 2 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-2">
              <div className="text-xs text-gray-500 mb-3 uppercase tracking-wider">Conversation</div>
              {current.history.map((turn, i) => (
                <div
                  key={i}
                  className={`text-sm px-3 py-2 rounded-lg ${
                    turn.role === "user"
                      ? "bg-indigo-500/10 text-indigo-200"
                      : "bg-gray-800 text-gray-300"
                  }`}
                >
                  <span className="font-medium text-xs opacity-60 mr-2">
                    {turn.role === "user" ? "You" : "AI"}
                  </span>
                  {turn.content}
                </div>
              ))}
            </div>
          )} */}
        </div>
      )}

      {!current && !loading && !error && !pendingClarification && (
        <div className="border-2 border-dashed border-gray-800 rounded-xl p-12 text-center">
          <LayoutDashboard size={32} className="text-gray-700 mx-auto mb-3" />
          <div className="text-gray-500 text-sm">
            Describe a chart above to get started
          </div>
        </div>
      )}
    </div>
  );
}
