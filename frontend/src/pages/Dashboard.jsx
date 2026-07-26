import { useEffect, useState } from "react";

import { fetchDashboardData } from "../api/client.js";
import BenefitBarChart from "../components/BenefitBarChart.jsx";
import BenefitPieChart from "../components/BenefitPieChart.jsx";
import HealthScoreGauge from "../components/HealthScoreGauge.jsx";
import NudgeSimulator from "../components/NudgeSimulator.jsx";
import SummaryCard from "../components/SummaryCard.jsx";

export default function Dashboard({ userId }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    fetchDashboardData(userId)
      .then(setDashboardData)
      .catch((error) => setLoadError(error.message));
  }, [userId]);

  if (loadError) {
    return <p className="state-message">Couldn't load dashboard: {loadError}</p>;
  }

  if (!dashboardData) {
    return <p className="state-message">Loading your benefits...</p>;
  }

  const {
    card_name,
    total_unused_value,
    total_used_value,
    total_budget_value,
    chart_rows,
    suggestions,
    benefit_health_score,
  } = dashboardData;

  return (
    <>
      <div className="masthead">
        <span className="masthead-eyebrow">Benefit Reclaim</span>
        <span className="card-name-tag">{card_name} Card</span>
      </div>
      <div className="headline-number">${total_unused_value.toFixed(0)}</div>
      <p className="headline-caption">left unclaimed this year</p>

      <div className="summary-row">
        <SummaryCard label="Total benefit budget" value={`$${total_budget_value.toFixed(0)}`} />
        <SummaryCard label="Used so far" value={`$${total_used_value.toFixed(0)}`} />
        <SummaryCard label="Unclaimed" value={`$${total_unused_value.toFixed(0)}`} />
      </div>

      <div className="charts-row">
        <HealthScoreGauge score={benefit_health_score} />
        <BenefitPieChart totalUsedValue={total_used_value} totalUnusedValue={total_unused_value} />
        <BenefitBarChart chartRows={chart_rows} />
      </div>

      {/* Demo seed data creates user 1 with card_id 1, so userId doubles as
          cardId here. If real auth/multiple cards per user gets added later,
          this needs its own card lookup instead. */}
      <NudgeSimulator cardId={userId} />

      <div>
        <p className="suggestions-section-title">Ways to use what's left</p>
        {suggestions.length === 0 ? (
          <p className="state-message">No suggestions right now — everything's being used well.</p>
        ) : (
          suggestions.map((suggestion) => (
            <div className="suggestion-row" key={suggestion.benefit_name}>
              <span className="suggestion-value-badge">${suggestion.unused_value.toFixed(0)}</span>
              <span>{suggestion.text}</span>
            </div>
          ))
        )}
      </div>
    </>
  );
}