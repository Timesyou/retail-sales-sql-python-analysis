import sqlite3
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from shelfsense.database import write_database
from shelfsense.engine import analyse_inventory
from shelfsense.models import Product, Sale


class DatabaseTests(unittest.TestCase):
    def test_database_contains_source_and_analysis_views(self):
        sale = Sale(date(2026, 1, 1), "A", 3, Decimal("12"), Decimal("7"), 2)
        product = Product("A", "Widget", "General", 0, 0, 0, 4, Decimal("20"), Decimal("2"), 0.95, 1, 1)
        analyses, _ = analyse_inventory([sale], {"A": product})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "reports" / "snapshot.sqlite"
            write_database(path, {"A": product}, [sale], analyses)
            with sqlite3.connect(path) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM sales").fetchone()[0], 1)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM v_replenishment_queue").fetchone()[0], 1)
                self.assertEqual(connection.execute("SELECT units_sold FROM sku_metrics WHERE sku='A'").fetchone()[0], 3)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM products").fetchone()[0], 1)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0], 1)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM v_category_performance").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
