#!/usr/bin/env python3
"""
Example: Scan Airflow task logs from S3 (curated zone) and match known issues.

Realistic naming used:
  Bucket:  data-platform-curated-zone-logs
  Prefix:  airflow/logs/
  DAG:     etl_sales_curated_daily
  Task:    load_curated_sales
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.known_issues import KnownIssuesStore
from src.log_reader import list_s3_logs, read_s3_log
from src.matcher import analyze_failure

# --- Config (change to your real bucket if needed) ---
S3_BUCKET = "data-platform-curated-zone-logs"
S3_PREFIX = "airflow/logs/"
AWS_REGION = "ap-south-1"
HOURS_BACK = 24

# Optional: only one DAG
# S3_PREFIX = "airflow/logs/etl_sales_curated_daily/"


def main():
    store = KnownIssuesStore(
        str(Path(__file__).resolve().parents[1] / "known_issues.json")
    )

    print(f"Listing logs in s3://{S3_BUCKET}/{S3_PREFIX} (last {HOURS_BACK}h)...\n")

    try:
        logs = list_s3_logs(
            bucket=S3_BUCKET,
            prefix=S3_PREFIX,
            region=AWS_REGION,
            hours_back=HOURS_BACK,
            max_keys=30,
        )
    except Exception as e:
        print(f"Could not list S3 objects: {e}")
        print("Check AWS credentials and bucket name.")
        return

    if not logs:
        print("No recent log objects found.")
        return

    for item in logs:
        # Example key:
        # airflow/logs/etl_sales_curated_daily/load_curated_sales/
        #   scheduled__2026-03-15T02:00:00+00:00/1.log
        key = item["key"]
        text = read_s3_log(item["bucket"], key, region=AWS_REGION)
        decision = analyze_failure(text, store)

        print("=" * 60)
        print(f"Log:      {key}")
        print(f"Status:   {decision['status']}")
        print(f"Issue:    {decision.get('issue_id') or '—'}")
        print(f"Category: {decision.get('category')}")
        print(f"Action:   {decision.get('action_taken')}")
        print()


if __name__ == "__main__":
    main()
