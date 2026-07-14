"use client";

import ReactECharts from "echarts-for-react";
import TableRenderer from "./TableRenderer";

interface Props {
  card: any;
}

export default function ChartRenderer({ card }: Props) {

  if (card.chart_type === "table") {
    return <TableRenderer card={card} />;
  }

  return (
    <ReactECharts
      option={card.chart_config}
      style={{
        width: "100%",
        height: "100%",
      }}
    />
  );
}