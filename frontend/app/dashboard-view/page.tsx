"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import DashboardGrid from "../dashboard-builder/components/DashboardGrid";

export default function DashboardViewPage() {
  const router = useRouter();

  const [cards, setCards] = useState<any[]>([]);
  const [fileName, setFileName] = useState("");

  useEffect(() => {
    const storedDashboard = sessionStorage.getItem("dashboard");

    if (!storedDashboard) {
      router.replace("/dashboard-builder");
      return;
    }

    setCards(JSON.parse(storedDashboard));

    setFileName(
      sessionStorage.getItem("dashboardFile") || ""
    );
  }, [router]);

  return (
    <div className="w-full max-w-[1800px] mx-auto px-8 py-10">

      <div className="flex justify-between items-center mb-10">

        <div>

          <h1 className="text-4xl font-bold text-white">
            AI Dashboard
          </h1>

          <p className="text-gray-400 mt-2">
            {fileName}
          </p>

        </div>

        <button
          onClick={() => router.push("/dashboard-builder")}
          className="bg-gray-800 hover:bg-gray-700 px-5 py-3 rounded-lg text-white"
        >
          Generate New Dashboard
        </button>

      </div>

      <DashboardGrid cards={cards} />

    </div>
  );
}