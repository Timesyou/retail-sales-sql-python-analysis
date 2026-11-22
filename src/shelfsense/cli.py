"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from .database import write_database
from .engine import analyse_inventory
from .ingest import DataValidationError, load_products, load_sales
from .reporting import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shelfsense",
        description="Turn retail sales and stock files into performance and replenishment reports.",
    )
    parser.add_argument("--sales", required=True, help="Path to the sales transaction CSV")
    parser.add_argument("--inventory", required=True, help="Path to the product and stock CSV")
    parser.add_argument("--output", default="reports", help="Output directory (default: reports)")
    parser.add_argument("--forecast-window", type=int, default=28, help="Recent calendar days used by the weighted forecast")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        sales = load_sales(args.sales)
        products = load_products(args.inventory)
        analyses, summary = analyse_inventory(sales, products, forecast_window_days=args.forecast_window)
        output_dir = Path(args.output)
        write_reports(output_dir, analyses, summary)
        write_database(output_dir / "shelfsense.sqlite", products, sales, analyses)
    except (DataValidationError, ValueError, OSError, sqlite3.Error) as exc:
        print(f"ShelfSense: {exc}", file=sys.stderr)
        return 2

    print(json.dumps({"status": "ok", "output_directory": str(output_dir), **summary}, indent=2))
    return 0
