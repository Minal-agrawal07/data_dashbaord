"use client";

import DashboardCard from "./DashboardCard";

interface Props {
  cards: any[];
}

export default function DashboardGrid({ cards }: Props) {
  return (
    <div className="mt-10 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      {cards.map((card, index) => (
        <DashboardCard
          key={index}
          card={card}
        />
      ))}
    </div>
  );
}