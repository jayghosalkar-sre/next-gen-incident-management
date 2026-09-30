"""
Main matching logic: take error text → find known issue → return decision.
"""

from typing import Dict
from .known_issues import KnownIssuesStore


def analyze_failure(
    error_text: str,
    store: KnownIssuesStore,
    threshold: float = 0.35,
) -> Dict:
    """
    Analyze a failure log/error text against known issues.

    Returns a structured decision dictionary.
    """
    match = store.find_best_match(error_text, threshold=threshold)

    if match:
        return {
            "status": "known_issue",
            "issue_id": match["id"],
            "category": match["category"],
            "specialist_needed": match["specialist_needed"],
            "can_auto_retry": match["can_auto_retry"],
            "action_taken": match["action_taken"],
            "urgency": match["urgency"],
            "match_score": match["match_score"],
            "message": f"Matched known issue '{match['id']}' with score {match['match_score']}",
        }

    return {
        "status": "unknown",
        "issue_id": None,
        "category": "unknown",
        "specialist_needed": "data_engineer",
        "can_auto_retry": False,
        "action_taken": "No matching known issue found. Please investigate manually.",
        "urgency": 3,
        "match_score": 0.0,
        "message": "No known issue matched. Escalating to specialist.",
    }
