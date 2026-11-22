import tempfile
import unittest
from pathlib import Path

from shelfsense.ingest import DataValidationError, load_products, load_sales


class CsvIngestionTests(unittest.TestCase):
    def test_loads_valid_sales_and_products(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sales_path = root / "sales.csv"
            inventory_path = root / "inventory.csv"
            sales_path.write_text("date,sku,units,unit_price,unit_cost\n2026-01-01,A,2,10.25,6.10\n", encoding="utf-8")
            inventory_path.write_text(
                "sku,name,category,on_hand,on_order,backorders,lead_time_days,order_cost,annual_holding_cost,service_level,pack_size,min_order_qty\n"
                "A,Widget,General,12,4,0,5,20,2,0.95,6,6\n", encoding="utf-8"
            )
            self.assertEqual(load_sales(sales_path)[0].units, 2)
            self.assertEqual(load_products(inventory_path)["A"].pack_size, 6)

    def test_rejects_duplicate_skus(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "inventory.csv"
            path.write_text(
                "sku,name,category,on_hand,on_order,backorders,lead_time_days,order_cost,annual_holding_cost,service_level,pack_size,min_order_qty\n"
                "A,One,General,1,0,0,5,20,2,0.95,1,1\n"
                "A,Two,General,1,0,0,5,20,2,0.95,1,1\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(DataValidationError, "duplicate"):
                load_products(path)

    def test_rejects_invalid_service_level(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "inventory.csv"
            path.write_text(
                "sku,name,category,on_hand,on_order,backorders,lead_time_days,order_cost,annual_holding_cost,service_level,pack_size,min_order_qty\n"
                "A,One,General,1,0,0,5,20,2,1.0,1,1\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(DataValidationError, "service_level"):
                load_products(path)

    def test_rejects_extra_values_without_a_header(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sales.csv"
            path.write_text(
                "date,sku,units,unit_price,unit_cost\n2026-01-01,A,1,5,2,unexpected\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(DataValidationError, "more values than the header"):
                load_sales(path)

    def test_rejects_duplicate_headers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sales.csv"
            path.write_text(
                "date,sku,units,unit_price,unit_cost,sku\n2026-01-01,A,1,5,2,A\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(DataValidationError, "duplicate column names"):
                load_sales(path)

    def test_rejects_blank_header_names(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sales.csv"
            path.write_text("date,sku,units,unit_price,unit_cost,  \n2026-01-01,A,1,5,2,extra\n", encoding="utf-8")
            with self.assertRaisesRegex(DataValidationError, "column names cannot be blank"):
                load_sales(path)

    def test_rejects_missing_required_columns(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sales.csv"
            path.write_text("date,sku,units\n2026-01-01,A,1\n", encoding="utf-8")
            with self.assertRaisesRegex(DataValidationError, "missing required columns"):
                load_sales(path)

    def test_rejects_noncanonical_iso_date_format(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sales.csv"
            path.write_text(
                "date,sku,units,unit_price,unit_cost\\n20260101,SKU-1,1,2.00,1.00\\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(DataValidationError, "YYYY-MM-DD"):
                load_sales(path)

    def test_rejects_non_finite_money_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sales.csv"
            path.write_text(
                "date,sku,units,unit_price,unit_cost\n2026-01-01,A,1,NaN,2\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(DataValidationError, "unit_price must be finite"):
                load_sales(path)

    def test_ignores_blank_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sales.csv"
            path.write_text(
                "date,sku,units,unit_price,unit_cost\n\n2026-01-01,A,1,5,2\n\n", encoding="utf-8"
            )
            self.assertEqual(len(load_sales(path)), 1)


if __name__ == "__main__":
    unittest.main()
