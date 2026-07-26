const SCORE_BANDS = [
  { minimum: 75, label: "Excellent", color: "#4fd1ae" },
  { minimum: 50, label: "Good", color: "#d4a54a" },
  { minimum: 25, label: "Needs attention", color: "#e08a5b" },
  { minimum: 0, label: "Underused", color: "#e0645b" },
];

function getScoreBand(score) {
  return SCORE_BANDS.find((band) => score >= band.minimum) ?? SCORE_BANDS[SCORE_BANDS.length - 1];
}

export default function HealthScoreGauge({ score }) {
  const band = getScoreBand(score);

  return (
    <div className="chart-panel health-score-panel">
      <p className="chart-panel-title">Benefit Health Score</p>
      <div className="health-score-value" style={{ color: band.color }}>
        {score}
      </div>
      <div className="health-score-label" style={{ color: band.color }}>
        {band.label}
      </div>
      <p className="health-score-caption">
        How much of your available credits and visits you're actually putting to use.
      </p>
    </div>
  );
}