"""Write portable CSV and JSON reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .dashboard import write_dashboard
from .models import SkuAnalysis


def write_reports(output_dir: str | Path, analyses: list[SkuAnalysis], summary: dict[str, object]) -> None:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    records = [analysis.as_record() for analysis in analyses]
    if records:
        with (destination / "sku_performance.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)

    reorder_records = [record for record in records if record["decision"] == "REORDER"]
    with (destination / "replenishment_plan.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["sku", "product_name", "category", "abc_class", "xyz_class", "inventory_position", "safety_stock", "reorder_point", "economic_order_quantity", "recommended_order_qty", "estimated_order_value"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{field: record[field] for field in fields} for record in reorder_records])

    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_dashboard(destination / "dashboard.html", analyses, summary)
