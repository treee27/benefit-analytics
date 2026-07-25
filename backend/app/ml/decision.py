"""Expected-value nudge decision.

Turns the raw engagement probability into a business decision: a nudge
is only worth sending when the expected recovered benefit value
(P(user acts) x unclaimed dollar value) clears a threshold. This keeps
low-value / low-engagement nudges from spamming the cardmember.

Plain Python, no FastAPI/DB dependency. Sits downstream of the
rule-based nudge engine, per its docstring: rules generate candidate
nudges, this filters them.
"""

EV_THRESHOLD_DOLLARS = 10.0


def decide_nudge(engagement_score: float, unused_value: float,
                 threshold: float = EV_THRESHOLD_DOLLARS) -> dict:
    """
    expected_value = engagement_score x unused_value (dollars we expect
    the cardmember to actually recover if we send this nudge now).
    """
    expected_value = round(engagement_score * unused_value, 2)
    return {
        "engagement_score": round(engagement_score, 4),
        "unused_value": unused_value,
        "expected_value": expected_value,
        "send": expected_value >= threshold,
        "threshold": threshold,
    }
