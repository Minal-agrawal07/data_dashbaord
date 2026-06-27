"use client";
import Link from "next/link";
import { BarChart2, Database, Wand2, ArrowRight } from "lucide-react";

export default function HomePage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-20 text-center">
      <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/30 rounded-full px-4 py-1 text-indigo-400 text-sm mb-8">
        <Wand2 size={14} /> AI-powered
      </div>

      <h1 className="text-5xl font-bold mb-4 text-white leading-tight">
        Describe a chart.<br />
        <span className="text-indigo-400">We'll build it.</span>
      </h1>

      <p className="text-gray-400 text-lg mb-10 max-w-xl mx-auto">
        Drop CSV files in the <code className="bg-gray-800 px-1 rounded text-gray-200">csvs/</code> folder,
        then ask for any chart in plain English. No SQL. No BI tools.
      </p>

      <div className="flex gap-4 justify-center mb-16">
        <Link
          href="/builder"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 transition-colors text-white font-medium px-6 py-3 rounded-lg"
        >
          Start Building <ArrowRight size={16} />
        </Link>
        <Link
          href="/setup"
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 transition-colors text-gray-200 font-medium px-6 py-3 rounded-lg"
        >
          <Database size={16} /> View Data Sources
        </Link>
      </div>

      <div className="grid grid-cols-3 gap-4 text-left">
        {[
          {
            icon: <Database size={20} className="text-indigo-400" />,
            title: "Drop CSV files",
            desc: "Put any CSV files in the csvs/ folder. Schema is auto-detected.",
          },
          {
            icon: <Wand2 size={20} className="text-emerald-400" />,
            title: "Describe in English",
            desc: "\"Show monthly revenue by category as a bar chart for Q1 2024\"",
          },
          {
            icon: <BarChart2 size={20} className="text-amber-400" />,
            title: "Chart appears",
            desc: "AI writes the SQL, picks the right chart, and renders it instantly.",
          },
        ].map((card) => (
          <div key={card.title} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <div className="mb-3">{card.icon}</div>
            <div className="font-semibold text-white mb-1">{card.title}</div>
            <div className="text-gray-400 text-sm">{card.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
