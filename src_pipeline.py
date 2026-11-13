#!/usr/bin/env python3
"""Clean the March shop export and aggregate accepted sales by category.

Uses only Python's standard library. Rejected records are written to quarantine
with a reason; raw inputs are never modified.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "orders_2024_03.csv"
OUT = ROOT / "data" / "processed"
QUARANTINE = ROOT / "data" / "quarantine"
LOG = ROOT / "logs" / "run_log.txt"
MAX_QUANTITY = 100


def parse_date(value: str) -> date:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError("unparseable order_date")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    today = date.today()
    seen: set[str] = set()
    clean: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    reasons: dict[str, int] = defaultdict(int)
    with RAW.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        row = {k: (v or "").strip() for k, v in row.items()}
        reason = ""
        try:
            oid = row["order_id"]
            if not oid:
                reason = "missing order_id"
            elif oid in seen:
                reason = "duplicate order_id"
            else:
                order_date = parse_date(row["order_date"])
                if order_date > today:
                    reason = "custom check: order_date is in the future"
                else:
                    qty = int(row["quantity"])
                    if qty <= 0 or qty > MAX_QUANTITY:
                        reason = f"quantity outside allowed range 1..{MAX_QUANTITY}"
                    elif not row["unit_price"]:
                        reason = "missing unit_price"
                    else:
                        price = Decimal(row["unit_price"])
                        if price < 0:
                            reason = "unit_price must be non-negative"
                        elif row["currency"].replace("€", "EUR") != "EUR":
                            reason = "unsupported currency (EUR-only output)"
                        elif not row["category"]:
                            reason = "missing category"
                        else:
                            seen.add(oid)
                            row["order_date"] = order_date.isoformat()
                            row["currency"] = "EUR"
                            row["quantity"] = str(qty)
                            row["unit_price"] = f"{price:.2f}"
                            row["revenue"] = f"{(price * qty):.2f}"
                            clean.append(row)
        except (KeyError, ValueError, InvalidOperation) as exc:
            reason = str(exc) or "invalid row"
        if reason:
            row["rejection_reason"] = reason
            rejected.append(row)
            reasons[reason] += 1

    fields = list(rows[0].keys()) + ["revenue"] if rows else ["revenue"]
    with (OUT / "clean_orders.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(clean)
    qfields = list(rows[0].keys()) + ["rejection_reason"] if rows else ["rejection_reason"]
    with (QUARANTINE / "rejected_orders.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=qfields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rejected)

    totals: dict[str, Decimal] = defaultdict(Decimal)
    counts: dict[str, int] = defaultdict(int)
    for row in clean:
        totals[row["category"]] += Decimal(row["revenue"])
        counts[row["category"]] += 1
    with (OUT / "revenue_by_category.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "order_count", "revenue_eur"])
        writer.writeheader()
        for category in sorted(totals):
            writer.writerow({"category": category, "order_count": counts[category],
                             "revenue_eur": f"{totals[category]:.2f}"})

    lines = [f"Run date: {today.isoformat()}", f"Input: {RAW.relative_to(ROOT)}",
             f"Rows read: {len(rows)}", f"Accepted: {len(clean)}",
             f"Quarantined: {len(rejected)}"]
    lines.extend(f"  - {reason}: {count}" for reason, count in sorted(reasons.items()))
    lines.extend(["Outputs: data/processed/clean_orders.csv, data/processed/revenue_by_category.csv,",
                  "         data/quarantine/rejected_orders.csv"])
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
