import { useState } from "react";

import { decideNudgeForTransaction } from "../api/client.js";

const DEMO_SCENARIOS = [
  {
    label: "$1,500 electronics purchase",
    transaction: {
      merchant_name: "Best Buy",
      category: "electronics",
      amount: 1500.0,
      location_type: null,
    },
  },
  {
    label: "$18 dinner",
    transaction: {
      merchant_name: "Chipotle",
      category: "dining",
      amount: 18.0,
      location_type: null,
    },
  },
  {
    label: "Airport check-in",
    transaction: {
      merchant_name: "Delta Airlines",
      category: "travel",
      amount: 60.0,
      location_type: "airport",
    },
  },
];

const CATEGORY_OPTIONS = ["dining", "transport", "travel", "electronics"];

const EMPTY_CUSTOM_FORM = {
  merchant_name: "",
  category: "dining",
  amount: "",
  location_type: "none",
};

export default function NudgeSimulator({ cardId }) {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [customForm, setCustomForm] = useState(EMPTY_CUSTOM_FORM);

  async function runTransaction(transaction) {
    setIsLoading(true);
    setErrorMessage(null);
    setResult(null);

    try {
      const payload = {
        card_id: cardId,
        transaction_date: new Date().toISOString().slice(0, 10),
        ...transaction,
      };
      const response = await decideNudgeForTransaction(payload);
      setResult(response);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  }

  function handleCustomFormSubmit(event) {
    event.preventDefault();

    if (!customForm.merchant_name.trim() || !customForm.amount) {
      setErrorMessage("Enter a merchant name and amount first.");
      return;
    }

    runTransaction({
      merchant_name: customForm.merchant_name.trim(),
      category: customForm.category,
      amount: parseFloat(customForm.amount),
      location_type: customForm.location_type === "none" ? null : customForm.location_type,
    });
  }

  function updateCustomFormField(fieldName, value) {
    setCustomForm((previousForm) => ({ ...previousForm, [fieldName]: value }));
  }

  return (
    <div className="chart-panel simulator-panel">
      <p className="chart-panel-title">Try a live nudge</p>
      <p className="simulator-caption">
        Simulate a transaction and watch the rule engine, ML engagement model, and expected-value
        decision run together.
      </p>

      <div className="simulator-button-row">
        {DEMO_SCENARIOS.map((scenario) => (
          <button
            key={scenario.label}
            className="simulator-button"
            onClick={() => runTransaction(scenario.transaction)}
            disabled={isLoading}
          >
            {scenario.label}
          </button>
        ))}
      </div>

      <form className="custom-transaction-form" onSubmit={handleCustomFormSubmit}>
        <p className="custom-form-label">Or try your own transaction:</p>
        <div className="custom-form-row">
          <input
            className="custom-form-input"
            type="text"
            placeholder="Merchant name"
            value={customForm.merchant_name}
            onChange={(event) => updateCustomFormField("merchant_name", event.target.value)}
            disabled={isLoading}
          />
          <select
            className="custom-form-input"
            value={customForm.category}
            onChange={(event) => updateCustomFormField("category", event.target.value)}
            disabled={isLoading}
          >
            {CATEGORY_OPTIONS.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
          <input
            className="custom-form-input custom-form-amount"
            type="number"
            step="0.01"
            min="0"
            placeholder="Amount"
            value={customForm.amount}
            onChange={(event) => updateCustomFormField("amount", event.target.value)}
            disabled={isLoading}
          />
          <select
            className="custom-form-input"
            value={customForm.location_type}
            onChange={(event) => updateCustomFormField("location_type", event.target.value)}
            disabled={isLoading}
          >
            <option value="none">No specific location</option>
            <option value="airport">Airport</option>
          </select>
          <button type="submit" className="simulator-button custom-form-submit" disabled={isLoading}>
            Simulate
          </button>
        </div>
      </form>

      {isLoading && <p className="state-message">Running the pipeline...</p>}
      {errorMessage && <p className="state-message">{errorMessage}</p>}

      {result && <SimulationResult result={result} />}
    </div>
  );
}

function SimulationResult({ result }) {
  if (!result.nudge) {
    return (
      <div className="simulation-result">
        <p className="simulation-no-nudge">No nudge triggered for this transaction.</p>
      </div>
    );
  }

  const { nudge, decision } = result;

  return (
    <div className="simulation-result">
      <p className="simulation-nudge-message">{nudge.message}</p>

      <div className="simulation-metrics-row">
        <div className="simulation-metric">
          <span className="simulation-metric-label">Engagement score</span>
          <span className="simulation-metric-value">{(decision.engagement_score * 100).toFixed(0)}%</span>
        </div>
        <div className="simulation-metric">
          <span className="simulation-metric-label">Expected value</span>
          <span className="simulation-metric-value">${decision.expected_value.toFixed(0)}</span>
        </div>
        <div className={`simulation-decision-badge ${decision.send ? "decision-send" : "decision-hold"}`}>
          {decision.send ? "SEND" : "HOLD"}
        </div>
      </div>
    </div>
  );
}