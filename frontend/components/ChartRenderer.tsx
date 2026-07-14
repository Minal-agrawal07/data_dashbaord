"use client";
import React from "react";
import ReactECharts from "echarts-for-react";

interface Props {
  chartConfig: Record<string, unknown>;
  chartType: string;
  data?: Record<string, unknown>[];
}

export default function ChartRenderer({ chartConfig, chartType, data }: Props) {
  if (!chartConfig || Object.keys(chartConfig).length === 0) return null;

  if (chartConfig.type === "empty") {
    return (
      <div className="flex items-center justify-center h-48 text-gray-500">
        {chartConfig.message as string}
      </div>
    );
  }

  if (chartConfig.type === "kpi") {
    const value = chartConfig.value as number | string;
    const label = chartConfig.label as string;
    const unit = (chartConfig.unit as string) || "";
    return (
      <div className="flex flex-col items-center justify-center h-48 gap-2">
        <div className="text-5xl font-bold text-indigo-400">
          {unit}{typeof value === "number" ? value.toLocaleString() : value}
        </div>
        <div className="text-gray-400 text-sm uppercase tracking-wider">{label}</div>
      </div>
    );
  }

  if (chartConfig.type === "table") {
    const columns = chartConfig.columns as string[];
    const rows = chartConfig.rows as Record<string, unknown>[];
    const displayColumns = columns || (data?.[0] ? Object.keys(data[0]) : []);
    const displayRows = rows || data || [];
    return (
      <div className="overflow-auto max-h-80 scrollbar-thin">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-gray-900">
            <tr>
              {displayColumns.map((col) => (
                <th key={col} className="px-3 py-2 text-left text-gray-400 font-medium border-b border-gray-800">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayRows.slice(0, 200).map((row, i) => (
              <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                {displayColumns.map((col) => (
                  <td key={col} className="px-3 py-1.5 text-gray-300">
                    {String(row[col] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  const echartsOption = {
    backgroundColor: "transparent",
    ...chartConfig,
    textStyle: { color: "#9ca3af", ...(chartConfig.textStyle as object || {}) },
    title: {
      textStyle: { color: "#f3f4f6", fontSize: 14 },
      ...(chartConfig.title as object || {}),
    },
    legend: {
      textStyle: { color: "#9ca3af" },
      ...(chartConfig.legend as object || {}),
    },
    xAxis: chartConfig.xAxis
      ? {
          axisLabel: { color: "#6b7280" },
          axisLine: { lineStyle: { color: "#374151" } },
          splitLine: { lineStyle: { color: "#1f2937" } },
          ...(chartConfig.xAxis as object),
        }
      : undefined,
    yAxis: chartConfig.yAxis
      ? {
          axisLabel: { color: "#6b7280" },
          axisLine: { lineStyle: { color: "#374151" } },
          splitLine: { lineStyle: { color: "#1f2937" } },
          ...(chartConfig.yAxis as object),
        }
      : undefined,
  };

  return (
    <ReactECharts
      option={echartsOption}
      style={{
    width:"100%",
    height:"300px"
}}
      theme="dark"
      opts={{ renderer: "canvas" }}
      notMerge
      lazyUpdate
    />
  );
}
