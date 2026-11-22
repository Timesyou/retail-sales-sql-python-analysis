"""Regenerate the deterministic, synthetic retail data shipped with ShelfSense."""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = date(2026, 1, 1)
DAYS = 90
RNG = random.Random(240319)

PRODUCTS = [
    ("TEA-01", "Assam Tea 250g", "Grocery", 55, 0, 0, 4, 10, 3.5, 0.95, 6, 12),
    ("COF-02", "Ground Coffee 200g", "Beverages", 34, 6, 0, 7, 12, 4.0, 0.97, 6, 6),
    ("RIC-03", "Premium Rice 1kg", "Grocery", 70, 0, 3, 5, 8, 3.0, 0.95, 10, 20),
    ("OIL-04", "Sunflower Oil 1L", "Grocery", 22, 0, 0, 6, 10, 4.0, 0.98, 6, 12),
    ("SNK-05", "Masala Snack Pack", "Snacks", 58, 12, 0, 3, 7, 1.5, 0.90, 12, 24),
    ("DET-06", "Laundry Detergent 1kg", "Home Care", 44, 0, 0, 8, 12, 4.5, 0.95, 6, 6),
    ("SOAP-07", "Bathing Soap 100g", "Personal Care", 28, 0, 2, 4, 7, 1.5, 0.95, 12, 24),
    ("BIS-08", "Butter Biscuits", "Bakery", 84, 0, 0, 2, 6, 1.2, 0.90, 12, 24),
    ("NEW-09", "New Seasonal Product", "Seasonal", 0, 0, 0, 10, 9, 2.0, 0.95, 6, 6),
]

# base daily units and unit selling/cost values. SKU DET-06 is intentionally
# intermittent; NEW-09 has no sales so the pipeline's zero-demand handling is visible.
DEMAND = {
    "TEA-01": (10, 4.50, 2.10),
    "COF-02": (5, 8.90, 4.30),
    "RIC-03": (11, 3.20, 2.35),
    "OIL-04": (6, 6.75, 5.10),
    "SNK-05": (12, 1.80, 0.85),
    "DET-06": (3, 5.40, 3.20),
    "SOAP-07": (7, 2.25, 1.20),
    "BIS-08": (15, 1.25, 0.62),
}


def main() -> None:
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    inventory_path = data_dir / "inventory.csv"
    with inventory_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "sku", "name", "category", "on_hand", "on_order", "backorders",
            "lead_time_days", "order_cost", "annual_holding_cost", "service_level",
            "pack_size", "min_order_qty",
        ])
        writer.writerows(PRODUCTS)

    sales_path = data_dir / "sales.csv"
    with sales_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "sku", "units", "unit_price", "unit_cost"])
        for day_index in range(DAYS):
            current_day = START + timedelta(days=day_index)
            for sku, (base, price, cost) in DEMAND.items():
                weekday_effect = (1, 0, 2, -1, 1, 3, -2)[current_day.weekday()]
                noise = RNG.randint(-2, 2)
                seasonal_lift = 2 if 35 <= day_index <= 44 and sku in {"TEA-01", "SNK-05"} else 0
                units = max(0, base + weekday_effect + noise + seasonal_lift)
                if sku == "DET-06" and day_index % 4 != 0:
                    units = 0
                if units:
                    writer.writerow([current_day.isoformat(), sku, units, f"{price:.2f}", f"{cost:.2f}"])


if __name__ == "__main__":
    main()
