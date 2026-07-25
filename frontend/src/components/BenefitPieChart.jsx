import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const USED_COLOR = "#8b90a3";
const UNUSED_COLOR = "#d4a54a";

export default function BenefitPieChart({ totalUsedValue, totalUnusedValue }) {
  const pieData = [
    { name: "Used", value: totalUsedValue },
    { name: "Unused", value: totalUnusedValue },
  ];

  return (
    <div className="chart-panel">
      <p className="chart-panel-title">Used vs. unused</p>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={pieData}
            dataKey="value"
            nameKey="name"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={3}
          >
            <Cell fill={USED_COLOR} />
            <Cell fill={UNUSED_COLOR} />
          </Pie>
          <Tooltip
            formatter={(value) => `$${value.toFixed(0)}`}
            contentStyle={{ background: "#1b1e2a", border: "1px solid #2a2e40", borderRadius: 8 }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
