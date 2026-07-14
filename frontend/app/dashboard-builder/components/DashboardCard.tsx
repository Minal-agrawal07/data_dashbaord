"use client";

import ChartRenderer from "./ChartRenderer";

interface Props {
  card: any;
}

export default function DashboardCard({ card }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 h-[420px] flex flex-col">

      <div className="flex justify-between items-start">

        <div>

          <h2 className="text-white font-semibold text-lg">
            {card.title}
          </h2>

          <p className="text-gray-400 text-sm mt-1">
            {card.description}
          </p>

        </div>

      </div>

      <div className="mt-5 flex-1">

        <ChartRenderer card={card} />

      </div>

    </div>
  );
}