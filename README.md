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


