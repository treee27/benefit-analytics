import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const USED_COLOR = "#8b90a3";
const UNUSED_COLOR = "#d4a54a";

export default function BenefitBarChart({ chartRows }) {
  return (
    <div className="chart-panel">
      <p className="chart-panel-title">Per-benefit breakdown</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartRows} margin={{ left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2e40" />
          <XAxis dataKey="name" stroke="#8b90a3" fontSize={12} />
          <YAxis stroke="#8b90a3" fontSize={12} />
          <Tooltip
            formatter={(value) => `$${value.toFixed(0)}`}
            contentStyle={{ background: "#1b1e2a", border: "1px solid #2a2e40", borderRadius: 8 }}
          />
          <Legend />
          <Bar dataKey="used_value" name="Used" fill={USED_COLOR} radius={[4, 4, 0, 0]} />
          <Bar dataKey="unused_value" name="Unused" fill={UNUSED_COLOR} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
