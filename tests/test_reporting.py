import csv
import json
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from shelfsense.engine import analyse_inventory
from shelfsense.models import Product, Sale
from shelfsense.reporting import write_reports


class ReportingTests(unittest.TestCase):
    def test_all_user_facing_reports_are_written(self):
        sales = [Sale(date(2026, 1, 1), "A", 2, Decimal("5"), Decimal("2"), 2)]
        products = {"A": Product("A", "Widget", "General", 0, 0, 0, 3, Decimal("4"), Decimal("1"), 0.95, 1, 1)}
        analyses, summary = analyse_inventory(sales, products)
        with tempfile.TemporaryDirectory() as folder:
            write_reports(folder, analyses, summary)
            root = Path(folder)
            self.assertTrue((root / "sku_performance.csv").is_file())
            self.assertTrue((root / "replenishment_plan.csv").is_file())
            self.assertTrue((root / "dashboard.html").is_file())
            self.assertTrue((root / "summary.json").is_file())
            self.assertEqual(json.loads((root / "summary.json").read_text())["units_sold"], 2)
            with (root / "sku_performance.csv").open() as handle:
                self.assertEqual(next(csv.DictReader(handle))["sku"], "A")
            self.assertIn("ShelfSense", (root / "dashboard.html").read_text())

    def test_dashboard_escapes_product_names(self):
        sales = [Sale(date(2026, 1, 1), "A", 2, Decimal("5"), Decimal("2"), 2)]
        products = {"A": Product("A", "<img src=x onerror=alert(1)>", "General", 0, 0, 0, 3, Decimal("4"), Decimal("1"), 0.95, 1, 1)}
        analyses, summary = analyse_inventory(sales, products)
        with tempfile.TemporaryDirectory() as folder:
            write_reports(folder, analyses, summary)
            dashboard = (Path(folder) / "dashboard.html").read_text()
            self.assertIn("\\u003cimg src=x onerror=alert(1)\\u003e", dashboard)
            self.assertIn("escapeHtml(r.product_name)", dashboard)
            self.assertNotIn("<img src=x onerror=alert(1)>", dashboard)


if __name__ == "__main__":
    unittest.main()
