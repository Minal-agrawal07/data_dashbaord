"use client";

interface Props {
  card: any;
}

export default function TableRenderer({ card }: Props) {

  const config = card.chart_config;

  return (

    <div className="overflow-auto h-full">

      <table className="w-full text-sm">

        <thead>

          <tr>

            {config.columns.map((col: string) => (

              <th
                key={col}
                className="text-left border-b border-gray-700 py-2"
              >
                {col}
              </th>

            ))}

          </tr>

        </thead>

        <tbody>

          {config.rows.map((row: any, index: number) => (

            <tr key={index}>

              {config.columns.map((col: string) => (

                <td
                  key={col}
                  className="py-2 border-b border-gray-800"
                >
                  {String(row[col] ?? "-")}
                </td>

              ))}

            </tr>

          ))}

        </tbody>

      </table>

    </div>

  );

}