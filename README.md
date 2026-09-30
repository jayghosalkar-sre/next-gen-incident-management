# Next-Gen Incident Management

Lightweight **pure-Python** tool that matches **EMR / Spark** and **Airflow** failure logs against a JSON knowledge base of previously seen issues and recommends the exact action that was taken before.

Works with logs stored locally or in **S3**. No ML models and no paid APIs required for recurring problems.

## Features

- One knowledge base for both **EMR** and **Airflow** known issues
- Keyword + text-similarity matching (fast, transparent, offline)
- Local sample logs included for demo
- Optional S3 support (same reader for EMR and Airflow remote logs)
- Returns: category, specialist needed, auto-retry flag, recommended action
- Easy to extend — just add entries to `known_issues.json`

## Quick Start

```bash
git clone https://github.com/jayghosalkar-sre/next-gen-incident-management.git
cd next-gen-incident-management

pip install -r requirements.txt

# Run against all sample logs (EMR + Airflow)
python main.py

## Analyze a Specific Log

# EMR sample
python main.py --log sample_logs/oom_error.log

# Airflow sample
python main.py --log sample_logs/airflow_task_timeout.log



## How It Works

Failure Log (local file or S3 object)
        ↓
Match against known_issues.json
   (keywords + text similarity)
        ↓
┌─────────────────────────────────┐
│ Found match?                    │
│  Yes → Return known action      │
│  No  → Escalate as "unknown"    │
└─────────────────────────────────┘


## Supported Sources

Source       Example S3 path
EMR / Spark  s3://data-platform-raw-zone-emr-logs/elasticmapreduce/j-3ABCDEF12GHIJ/
Airflow      s3://data-platform-curated-zone-logs/airflow/logs/etl_sales_curated_daily/


## Knowledge Base Format

{
  "id": "af-timeout-001",
  "source": "airflow",
  "error_signature": "Task exceeded timeout or execution_timeout",
  "keywords": ["Timeout", "execution_timeout", "AirflowTaskTimeout"],
  "category": "timeout",
  "specialist_needed": "none",
  "can_auto_retry": true,
  "action_taken": "Increase task execution_timeout or optimize the task. Clear and retry.",
  "urgency": 2
}


## Sample Known Issues Included

EMR / Spark: OOM, connection refused, NullPointer, disk full, shuffle fetch, S3 SlowDown
Airflow: task timeout, sensor timeout, upstream failed, DAG import error, metadata DB failure, S3 AccessDenied, K8s OOMKilled, missing connection


## Project Structure

next-gen-incident-management/
├── main.py
├── known_issues.json
├── sample_logs/
├── src/
│   ├── known_issues.py
│   ├── log_reader.py
│   └── matcher.py
├── examples/
├── requirements.txt
└── README.md
