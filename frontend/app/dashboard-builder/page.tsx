"use client";
import DashboardGrid from "./components/DashboardGrid";
import { useRef, useState } from "react";
import { Upload, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import mockDashboard from "./mockDashboard.json";
import { useRouter } from "next/navigation";
export default function DashboardBuilderPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [dashboard, setDashboard] = useState<any[]>([]);
  const [showAccessModal, setShowAccessModal] = useState(false);
  const [accessKey, setAccessKey] = useState("");
  const [verifying, setVerifying] = useState(false);
  const [keyError, setKeyError] = useState("");
  const USE_MOCK = true;
  const router = useRouter();
const handleFile = async (selected: File) => {
  try {
    setUploading(true);

    if (USE_MOCK) {
      setFile(selected);
      return;
    }

    await api.uploadCSV(selected);

    setFile(selected);

    alert(`${selected.name} uploaded successfully!`);
  } catch (err) {
    console.error(err);

    alert(
      err instanceof Error
        ? err.message
        : "Failed to upload CSV."
    );
  } finally {
    setUploading(false);
  }
};

  async function generateDashboard() {
  try {
    setGenerating(true);

    let cards;

    if (USE_MOCK) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      cards = mockDashboard;
    } else {
      if (!file) {
        alert("Please upload a CSV first.");
        return;
      }

      const result = await api.generateDashboard(file.name);

      cards = result.cards ?? [];
    }

    sessionStorage.setItem(
      "dashboard",
      JSON.stringify(cards)
    );

    if (file) {
      sessionStorage.setItem(
        "dashboardFile",
        file.name
      );
    }

    router.replace("/dashboard-view");

  } catch (err) {
    console.error(err);

    alert(
      err instanceof Error
        ? err.message
        : "Failed to generate dashboard."
    );
  } finally {
    setGenerating(false);
  }
}

  return (
    <div className="w-full max-w-[1800px] mx-auto px-8 py-12">

      <div className="text-center">

        <Sparkles
          className="mx-auto text-indigo-400 mb-4"
          size={45}
        />

        <h1 className="text-4xl font-bold text-white">
          AI Dashboard Generator
        </h1>

        <p className="text-gray-400 mt-3">
          Upload your CSV and let AI automatically build an executive dashboard.
        </p>

      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);

          const f = e.dataTransfer.files[0];

          if (f) handleFile(f);
        }}
        className={`mt-12 rounded-2xl border-2 border-dashed p-14 text-center transition ${
          dragging
            ? "border-indigo-500 bg-indigo-500/10"
            : "border-gray-700"
        }`}
      >

        <Upload
          className="mx-auto text-indigo-400"
          size={55}
        />

        <h2 className="text-2xl text-white font-semibold mt-5">
          Upload CSV Dataset
        </h2>

        <p className="text-gray-400 mt-3">
          Drag & Drop your CSV here
        </p>

        <button
          onClick={() => fileInputRef.current?.click()}
          className="mt-8 bg-indigo-600 hover:bg-indigo-500 px-7 py-3 rounded-lg text-white"
        >
          {uploading ? "Uploading..." : "Choose CSV"}
        </button>

        <input
          hidden
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={(e) => {
            const f = e.target.files?.[0];

            if (f) handleFile(f);
          }}
        />

      </div>

      {file && (
        <div className="mt-8 flex items-center justify-between bg-gray-900 rounded-xl p-5">

          <div>

            <h3 className="text-white font-semibold">
              {file.name}
            </h3>

            <p className="text-green-400 text-sm">
              Uploaded Successfully
            </p>

          </div>

          <button
            onClick={generateDashboard}
            disabled={generating}
            className="bg-indigo-600 hover:bg-indigo-500 px-7 py-3 rounded-lg text-white"
          >
            {generating
              ? "Generating..."
              : "Generate Dashboard"}
          </button>

        </div>
      )}
      

    </div>
  );
}