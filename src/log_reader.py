"""
Log Reader - supports local sample files and S3 (EMR + Airflow logs).
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta


def read_local_log(filepath: str) -> str:
    """Read a local log file and return its content."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {filepath}")
    return path.read_text(encoding="utf-8", errors="replace")


def list_sample_logs(sample_dir: str = "sample_logs") -> List[Dict]:
    """List all .log files in the sample_logs directory."""
    directory = Path(sample_dir)
    if not directory.exists():
        return []

    results = []
    for f in sorted(directory.glob("*.log")):
        results.append(
            {
                "source": "local",
                "path": str(f),
                "name": f.name,
            }
        )
    return results


def read_s3_log(
    bucket: str,
    key: str,
    region: str = "ap-south-1",
    max_bytes: int = 400_000,
) -> str:
    """
    Read a log file from S3 (works for EMR and Airflow logs).
    Requires boto3 and valid AWS credentials.
    """
    try:
        import boto3
    except ImportError:
        raise ImportError(
            "boto3 is required for S3 support. Install with: pip install boto3"
        )

    s3 = boto3.client("s3", region_name=region)

    head = s3.head_object(Bucket=bucket, Key=key)
    size = head["ContentLength"]
    start = max(0, size - max_bytes)

    params = {"Bucket": bucket, "Key": key}
    if start > 0:
        params["Range"] = f"bytes={start}-{size - 1}"

    response = s3.get_object(**params)
    return response["Body"].read().decode("utf-8", errors="replace")


def list_s3_logs(
    bucket: str,
    prefix: str,
    region: str = "ap-south-1",
    hours_back: int = 24,
    max_keys: int = 50,
) -> List[Dict]:
    """
    List recent log objects under an S3 prefix.

    Typical prefixes:
      - EMR:     elasticmapreduce/j-3ABCDEF12GHIJ/
      - Airflow: airflow/logs/etl_sales_curated_daily/
    """
    try:
        import boto3
    except ImportError:
        raise ImportError(
            "boto3 is required for S3 support. Install with: pip install boto3"
        )

    s3 = boto3.client("s3", region_name=region)
    cutoff = datetime.utcnow() - timedelta(hours=hours_back)
    prefix = prefix.rstrip("/") + "/"

    results = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if obj["LastModified"].replace(tzinfo=None) < cutoff:
                continue
            key = obj["Key"]
            # Skip folder markers and very small objects
            if key.endswith("/") or obj["Size"] < 50:
                continue
            results.append(
                {
                    "source": "s3",
                    "bucket": bucket,
                    "key": key,
                    "name": key.split("/")[-1],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"].isoformat(),
                }
            )
            if len(results) >= max_keys:
                return results

    return results
