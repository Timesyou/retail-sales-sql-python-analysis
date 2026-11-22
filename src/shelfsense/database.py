"""Persist an auditable SQLite snapshot for ad-hoc SQL analysis."""

from __future__ import annotations

import sqlite3
from importlib.resources import files
from pathlib import Path

from .models import Product, Sale, SkuAnalysis


def write_database(
    path: str | Path,
    products: dict[str, Product],
    sales: list[Sale],
    analyses: list[SkuAnalysis],
) -> None:
    """Create a fresh SQLite database with source rows and calculated results."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    schema = files("shelfsense").joinpath("schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(destination) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema)
        connection.executemany(
            """INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [(
                p.sku, p.name, p.category, p.on_hand, p.on_order, p.backorders,
                p.lead_time_days, str(p.order_cost), str(p.annual_holding_cost),
                p.service_level, p.pack_size, p.min_order_qty,
            ) for p in products.values()],
        )
        connection.executemany(
            "INSERT INTO sales (sale_date, sku, units, unit_price, unit_cost) VALUES (?, ?, ?, ?, ?)",
            [(s.sale_date.isoformat(), s.sku, s.units, str(s.unit_price), str(s.unit_cost)) for s in sales],
        )
        connection.executemany(
            """INSERT INTO sku_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [(
                a.sku, a.units_sold, str(a.revenue), str(a.cost_of_goods_sold),
                str(a.gross_profit), a.gross_margin_pct, a.average_daily_demand,
                a.daily_demand_stddev, a.demand_cv, a.forecast_daily_demand,
                a.abc_class, a.xyz_class, a.safety_stock, a.reorder_point,
                a.economic_order_quantity, a.inventory_position, a.stock_cover_days,
            ) for a in analyses],
        )
        connection.executemany(
            "INSERT INTO recommendations VALUES (?, ?, ?, ?)",
            [(a.sku, a.decision, a.recommended_order_qty, str(a.estimated_order_value)) for a in analyses],
        )
