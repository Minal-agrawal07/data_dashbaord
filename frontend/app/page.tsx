"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  BarChart2,
  Database,
  Wand2,
  ArrowRight,
  Upload,
} from "lucide-react";
import { api } from "@/lib/api";

export default function HomePage() {
  const [showUpload, setShowUpload] = useState(false);
  const [showAccessModal, setShowAccessModal] = useState(false);
  const [accessKey, setAccessKey] = useState("");
  const [verifying, setVerifying] = useState(false);
  const [keyError, setKeyError] = useState("");
  const [isAuthorized, setIsAuthorized] = useState(false);
  const router = useRouter();

  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
const MAX_FILE_SIZE = 100 * 1024 // 100kb

const handleFile = async (file: File) => {
  // Check file extension
  if (!file.name.toLowerCase().endsWith(".csv")) {
    alert("Only CSV files are allowed.");
    return;
  }

  // Check file size
 if (!isAuthorized && file.size > MAX_FILE_SIZE) {
    setShowUpload(false);
    setShowAccessModal(true);
    return;
}

  try {
    setUploading(true);

    await api.uploadCSV(file,accessKey);

    alert(`${file.name} uploaded successfully!`);

    router.push("/setup");
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

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);

    const file = e.dataTransfer.files?.[0];

    if (file) {
      handleFile(file);
    }
  };
  const verifyAccessKey = async () => {
  if (!accessKey.trim()) {
    setKeyError("Please enter an access key.");
    return;
  }

  try {
    setVerifying(true);
    setKeyError("");

    const res = await api.verifyAccessKey(accessKey);

   if (res.valid) {
    setIsAuthorized(true);
    setShowAccessModal(false);

    // Reopen upload dialog
    setShowUpload(true);

    // Open the file picker
    setTimeout(() => {
        fileInputRef.current?.click();
    }, 100);
}else {
      setKeyError("Invalid access key.");
    }
  } catch (err) {
    setKeyError(
      err instanceof Error ? err.message : "Verification failed."
    );
  } finally {
    setVerifying(false);
  }
};

  const handleBrowse = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];

    if (file) {
      handleFile(file);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-16">

      <div className="text-center">

        <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/30 rounded-full px-4 py-1 text-indigo-400 text-sm mb-8">
          <Wand2 size={14} />
          AI Powered Dashboard Builder
        </div>

        <h1 className="text-5xl font-bold text-white leading-tight">
          Describe a chart.
          <br />
          <span className="text-indigo-400">
            We'll build it.
          </span>
        </h1>

        <p className="text-gray-400 text-lg mt-6 max-w-2xl mx-auto">
          Upload a CSV, then ask questions in plain English.
          No SQL. No BI tools.
        </p>

      </div>
{/* 
      <div className="mt-12">

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
            dragging
              ? "border-indigo-500 bg-indigo-500/10"
              : "border-gray-700 bg-gray-900"
          }`}
        >
          <Upload
            size={50}
            className="mx-auto mb-4 text-indigo-400"
          />

          <h2 className="text-2xl text-white font-semibold">
            Upload CSV Dataset
          </h2>

          <p className="text-gray-400 mt-3">
            Drag & Drop your CSV here
          </p>

          <p className="text-gray-500 my-4">
            or
          </p>

          <label
  htmlFor="csv-upload"
  className="inline-flex cursor-pointer bg-indigo-600 hover:bg-indigo-500 px-6 py-3 rounded-lg text-white font-medium"
>
  {uploading ? "Uploading..." : "Choose CSV File"}
</label>

<input
  id="csv-upload"
  type="file"
  accept=".csv"
  style={{ display: "none" }}
  onChange={handleBrowse}
/>

        </div>
              </div> */}

      <div className="flex justify-center gap-4 mt-10">
        <Link
          href="/builder"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 transition-colors text-white font-medium px-6 py-3 rounded-lg"
        >
          Start Building
          <ArrowRight size={16} />
        </Link>

        <Link
          href="/setup"
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 transition-colors text-gray-200 font-medium px-6 py-3 rounded-lg"
        >
          <Database size={16} />
          View Data Sources
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-16">
        <div
  onClick={() => setShowUpload(true)}
  className="bg-gray-900 border border-gray-800 rounded-xl p-6 cursor-pointer hover:border-indigo-500 transition"
>
          <Database
            size={24}
            className="text-indigo-400 mb-4"
          />

          <h3 className="text-white font-semibold text-lg">
            Upload CSV
          </h3>

          <p className="text-gray-400 text-sm mt-2">
            Upload one or more CSV datasets directly from
            your computer.
          </p>
        </div>


        <div
  onClick={() => router.push("/dashboard-builder")}
  className="bg-gray-900 border border-gray-800 rounded-xl p-6 cursor-pointer hover:border-indigo-500 transition"
>
          <BarChart2
            size={24}
            className="text-amber-400 mb-4"
          />

          <h3 className="text-white font-semibold text-lg">
            Instant Charts
          </h3>

          <p className="text-gray-400 text-sm mt-2">
            AI generates SQL, executes it and renders the
            best visualization automatically.
          </p>
        </div>
      </div>
       {showUpload && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">

          <div className="bg-gray-900 rounded-2xl p-10 w-[750px] relative">

            <button
              onClick={() => setShowUpload(false)}
              className="absolute top-5 right-5 text-gray-400 hover:text-white text-xl"
            >
              ✕
            </button>

            <Upload
              size={55}
              className="mx-auto text-indigo-400 mb-5"
            />

            <h2 className="text-3xl text-center font-bold text-white">
              Upload CSV Dataset
            </h2>

            <p className="text-center text-gray-400 mt-3">
              Drag & Drop your CSV here.
              File should be less than 100kb. If it's larger, please enter your access key.
            </p>

            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              className={`mt-8 border-2 border-dashed rounded-xl p-10 text-center transition ${
                dragging
                  ? "border-indigo-500 bg-indigo-500/10"
                  : "border-gray-700"
              }`}
            >

              

              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-indigo-600 hover:bg-indigo-500 px-6 py-3 rounded-lg text-white"
              >
                {uploading ? "Uploading..." : "Choose CSV File"}
              </button>

              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                hidden
                onChange={handleBrowse}
              />

            </div>

          </div>

        </div>
      )}
      {showAccessModal && (
  <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">

    <div className="bg-gray-900 rounded-2xl p-8 w-[500px] relative border border-gray-700">

      <button
        onClick={() => setShowAccessModal(false)}
        className="absolute top-4 right-4 text-gray-400 hover:text-white"
      >
        ✕
      </button>

    

      <p className="text-gray-400 text-center mt-3">
        Enter your access key to continue.
      </p>

      <input
        type="password"
        placeholder="Enter Access Key"
        value={accessKey}
        onChange={(e) => setAccessKey(e.target.value)}
        className="w-full mt-6 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
      />

      {keyError && (
        <p className="text-red-400 mt-3 text-sm">
          {keyError}
        </p>
      )}

      <button
  onClick={verifyAccessKey}
  disabled={verifying}
  className="w-full mt-6 bg-indigo-600 hover:bg-indigo-500 rounded-lg py-3 text-white disabled:opacity-50"
>
  {verifying ? "Verifying..." : "Verify Access"}
</button>

      <div className="border-t border-gray-700 mt-8 pt-5 text-center">

        <p className="text-gray-400">
          Don't have an access key?
        </p>

        <button className="mt-2 text-indigo-400 hover:text-indigo-300">
          Request Access
        </button>

      </div>

    </div>

  </div>
)}
    </div>
  );
}
