"""
Dashboard Builder (Phase 4, backend half)

Takes the raw benefit breakdown from benefit_calculator.py and reshapes it
into exactly what the React dashboard needs: totals for the summary cards,
a list of rows for the bar/pie charts, and plain-English suggestions
sorted by dollar impact.
"""


def build_dashboard_response(unclaimed_breakdown: dict) -> dict:
    benefits = unclaimed_breakdown["benefits"]

    chart_rows = []
    total_budget_value = 0.0
    total_used_value = 0.0
    total_unused_value = unclaimed_breakdown["total_unclaimed_value"]

    for benefit_name, benefit_info in benefits.items():
        chart_rows.append(
            {
                "name": benefit_name,
                "type": benefit_info["type"],
                "used_value": benefit_info["dollar_value_used"],
                "unused_value": benefit_info["unused_value"],
                "has_fixed_budget": benefit_info["dollar_value_limit"] is not None,
            }
        )

        if benefit_info["dollar_value_limit"] is not None:
            total_budget_value += benefit_info["dollar_value_limit"]
            total_used_value += benefit_info["dollar_value_used"]

    suggestions = _build_suggestions(benefits)
    benefit_health_score = _calculate_benefit_health_score(chart_rows)

    return {
        "card_name": unclaimed_breakdown["card_name"],
        "total_budget_value": round(total_budget_value, 2),
        "total_used_value": round(total_used_value, 2),
        "total_unused_value": round(total_unused_value, 2),
        "chart_rows": chart_rows,
        "suggestions": suggestions,
        "benefit_health_score": benefit_health_score,
    }


def _calculate_benefit_health_score(chart_rows: list[dict]) -> int:
    """
    Averages the utilization ratio (used / limit) across every benefit
    that has a fixed budget (credit + visit types). Purchase Protection
    is excluded — it's a coverage cap, not a spending budget, so "using"
    it isn't a meaningful concept the way spending a credit is.

    Returns a whole number 0-100. Higher = better overall utilization.
    """
    utilization_ratios = []

    for row in chart_rows:
        if not row["has_fixed_budget"]:
            continue

        benefit_limit = row["used_value"] + row["unused_value"]
        if benefit_limit <= 0:
            continue

        utilization_ratios.append(row["used_value"] / benefit_limit)

    if not utilization_ratios:
        return 0

    average_utilization = sum(utilization_ratios) / len(utilization_ratios)
    return round(average_utilization * 100)


def _build_suggestions(benefits: dict) -> list[dict]:
    suggestion_candidates = []

    for benefit_name, benefit_info in benefits.items():
        if benefit_info["unused_value"] <= 0:
            continue

        if benefit_info["type"] == "credit":
            suggestion_text = (
                f"You have ${benefit_info['unused_value']:.0f} left in {benefit_name} — use it before it resets."
            )
        elif benefit_info["type"] == "visit":
            remaining_uses = benefit_info["limit"] - benefit_info["used"]
            suggestion_text = (
                f"You have {remaining_uses} unused {benefit_name} visit(s), "
                f"worth ${benefit_info['unused_value']:.0f}."
            )
        elif benefit_info["type"] == "protection":
            suggestion_text = (
                f"A recent purchase is eligible for {benefit_name} — "
                f"up to ${benefit_info['unused_value']:.0f} in coverage you haven't claimed."
            )
        else:
            continue

        suggestion_candidates.append(
            {
                "benefit_name": benefit_name,
                "text": suggestion_text,
                "unused_value": benefit_info["unused_value"],
            }
        )

    suggestion_candidates.sort(key=lambda candidate: candidate["unused_value"], reverse=True)
    return suggestion_candidates[:4]