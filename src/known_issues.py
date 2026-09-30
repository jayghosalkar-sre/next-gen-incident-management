"""
Known Issues Store - loads and matches against a JSON knowledge base.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from difflib import SequenceMatcher


class KnownIssuesStore:
    def __init__(self, filepath: str = "known_issues.json"):
        self.filepath = Path(filepath)
        self.issues: List[Dict] = []
        self.load()

    def load(self) -> None:
        """Load known issues from JSON file."""
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.issues = json.load(f)
            print(f"Loaded {len(self.issues)} known issues from {self.filepath}")
        else:
            print(f"Warning: {self.filepath} not found. Starting with empty list.")
            self.issues = []

    def save(self) -> None:
        """Save current issues back to JSON (useful when adding new ones)."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.issues, f, indent=2, ensure_ascii=False)

    def add_issue(self, issue: Dict) -> None:
        """Add a new known issue and save."""
        self.issues.append(issue)
        self.save()
        print(f"Added new issue: {issue.get('id')}")

    def find_best_match(
        self, error_text: str, threshold: float = 0.35
    ) -> Optional[Dict]:
        """
        Find the best matching known issue for the given error text.

        Scoring logic:
        - Strong boost if any keyword is found
        - Extra weight when multiple keywords match
        - Light text similarity against the error_signature
        """
        if not error_text or not self.issues:
            return None

        error_lower = error_text.lower()
        best_score = 0.0
        best_issue = None

        for issue in self.issues:
            score = 0.0
            keywords = issue.get("keywords", [])

            if keywords:
                hits = [kw for kw in keywords if kw.lower() in error_lower]
                hit_count = len(hits)

                if hit_count > 0:
                    # Base score for having at least one keyword hit
                    score += 0.40
                    # Additional score for more keyword hits
                    score += min(hit_count / len(keywords), 1.0) * 0.45

            # Light similarity against the short error signature
            signature = issue.get("error_signature", "")
            if signature:
                # Compare against a shortened version of the log for better ratio
                short_error = error_lower[:800]
                similarity = SequenceMatcher(
                    None, short_error, signature.lower()
                ).ratio()
                score += similarity * 0.20

            if score > best_score:
                best_score = score
                best_issue = issue

        if best_issue and best_score >= threshold:
            result = dict(best_issue)
            result["match_score"] = round(best_score, 3)
            return result

        return None
