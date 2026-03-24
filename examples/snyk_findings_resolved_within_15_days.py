#!/usr/bin/env python3
"""
Find critical Snyk findings linked to resolved issues where the issue
was resolved (updatedOn) within 15 days of being opened (createdOn).

J1QL cannot perform property-to-property arithmetic in WHERE clauses,
so we retrieve both timestamps and filter in Python.

Usage:
    export JUPITERONE_ACCOUNT_ID="<your-account-id>"
    export JUPITERONE_API_TOKEN="<your-api-token>"
    python snyk_findings_resolved_within_15_days.py [--csv output.csv]
"""

import os
import sys
import csv
import argparse
from datetime import datetime, timezone

from jupiterone import JupiterOneClient

FIFTEEN_DAYS_MS = 15 * 24 * 60 * 60 * 1000

J1QL_QUERY = """\
FIND snyk_finding WITH severity = 'critical' AS finding
  THAT RELATES TO snyk_issue WITH status = 'resolved' AS issue
RETURN
  finding.displayName  AS findingName,
  finding._key         AS findingKey,
  finding.severity     AS severity,
  issue.displayName    AS issueName,
  issue._key           AS issueKey,
  issue.status         AS issueStatus,
  issue.createdOn      AS createdOn,
  issue.updatedOn      AS updatedOn
LIMIT 250\
"""


def ms_to_iso(epoch_ms):
    """Convert epoch milliseconds to a human-readable ISO-8601 string."""
    if epoch_ms is None:
        return "N/A"
    try:
        return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    except (TypeError, ValueError, OSError):
        return str(epoch_ms)


def main():
    parser = argparse.ArgumentParser(
        description="Find critical Snyk findings resolved within 15 days."
    )
    parser.add_argument(
        "--csv",
        metavar="FILE",
        help="Write results to a CSV file instead of stdout.",
    )
    args = parser.parse_args()

    account = os.getenv("JUPITERONE_ACCOUNT_ID")
    token = os.getenv("JUPITERONE_API_TOKEN")
    if not account or not token:
        sys.exit(
            "Error: JUPITERONE_ACCOUNT_ID and JUPITERONE_API_TOKEN "
            "environment variables are required."
        )

    j1 = JupiterOneClient(
        account=account,
        token=token,
        url=os.getenv("JUPITERONE_URL", "https://graphql.us.jupiterone.io"),
        sync_url=os.getenv("JUPITERONE_SYNC_URL", "https://api.us.jupiterone.io"),
    )

    print(f"Executing J1QL query ...\n{J1QL_QUERY}\n")
    result = j1.query_v1(query=J1QL_QUERY)
    rows = result.get("data", [])
    print(f"Total rows returned: {len(rows)}")

    filtered = []
    skipped_missing_dates = 0

    for row in rows:
        props = row.get("properties", row)
        created_on = props.get("createdOn")
        updated_on = props.get("updatedOn")

        if created_on is None or updated_on is None:
            skipped_missing_dates += 1
            continue

        delta_ms = updated_on - created_on
        if delta_ms <= FIFTEEN_DAYS_MS:
            filtered.append(
                {
                    "findingName": props.get("findingName", ""),
                    "findingKey": props.get("findingKey", ""),
                    "severity": props.get("severity", ""),
                    "issueName": props.get("issueName", ""),
                    "issueKey": props.get("issueKey", ""),
                    "issueStatus": props.get("issueStatus", ""),
                    "createdOn": created_on,
                    "updatedOn": updated_on,
                    "createdOnHuman": ms_to_iso(created_on),
                    "updatedOnHuman": ms_to_iso(updated_on),
                    "daysToResolve": round(delta_ms / (24 * 60 * 60 * 1000), 2),
                }
            )

    print(f"Rows matching <=15-day window: {len(filtered)}")
    if skipped_missing_dates:
        print(f"Rows skipped (missing createdOn/updatedOn): {skipped_missing_dates}")

    if not filtered:
        print("No matching results.")
        return

    if args.csv:
        fieldnames = list(filtered[0].keys())
        with open(args.csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered)
        print(f"\nResults written to {args.csv}")
    else:
        print(f"\n{'Finding':<40} {'Issue':<40} {'Created':<24} {'Updated':<24} {'Days':>6}")
        print("-" * 138)
        for r in filtered:
            print(
                f"{r['findingName']:<40} "
                f"{r['issueName']:<40} "
                f"{r['createdOnHuman']:<24} "
                f"{r['updatedOnHuman']:<24} "
                f"{r['daysToResolve']:>6}"
            )


if __name__ == "__main__":
    main()
