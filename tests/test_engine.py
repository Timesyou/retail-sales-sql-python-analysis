import unittest
from datetime import date, timedelta
from decimal import Decimal

from shelfsense.engine import analyse_inventory
from shelfsense.models import Product, Sale


def product(sku="SKU-1", **changes):
    values = dict(
        sku=sku, name="Test product", category="Test", on_hand=2, on_order=0,
        backorders=0, lead_time_days=3, order_cost=Decimal("25"),
        annual_holding_cost=Decimal("2"), service_level=0.95,
        pack_size=6, min_order_qty=6,
    )
    values.update(changes)
    return Product(**values)


class InventoryEngineTests(unittest.TestCase):
    def test_zero_filled_calendar_and_reorder_logic(self):
        start = date(2026, 1, 1)
        sales = [
            Sale(start, "SKU-1", 4, Decimal("10"), Decimal("6"), 2),
            Sale(start + timedelta(days=2), "SKU-1", 4, Decimal("10"), Decimal("6"), 3),
        ]
        results, summary = analyse_inventory(sales, {"SKU-1": product()})
        result = results[0]
        self.assertEqual(summary["observed_days"], 3)
        self.assertEqual(result.units_sold, 8)
        self.assertEqual(result.revenue, Decimal("80"))
        self.assertEqual(result.cost_of_goods_sold, Decimal("48"))
        self.assertEqual(result.gross_profit, Decimal("32"))
        self.assertEqual(result.decision, "REORDER")
        self.assertEqual(result.recommended_order_qty % 6, 0)

    def test_empty_sales_sku_is_included_and_not_reordered(self):
        sales = [Sale(date(2026, 1, 1), "SKU-1", 1, Decimal("5"), Decimal("2"), 2)]
        products = {
            "SKU-1": product(on_hand=1000),
            "SKU-2": product("SKU-2", name="New product", on_hand=0),
        }
        results, _ = analyse_inventory(sales, products)
        by_sku = {row.sku: row for row in results}
        self.assertEqual(by_sku["SKU-2"].units_sold, 0)
        self.assertEqual(by_sku["SKU-2"].xyz_class, "N")
        self.assertEqual(by_sku["SKU-2"].decision, "HOLD")

    def test_unknown_sales_sku_is_rejected(self):
        sales = [Sale(date(2026, 1, 1), "MISSING", 1, Decimal("5"), Decimal("2"), 2)]
        with self.assertRaisesRegex(ValueError, "missing from inventory"):
            analyse_inventory(sales, {"SKU-1": product()})

    def test_forecast_window_must_be_positive(self):
        sales = [Sale(date(2026, 1, 1), "SKU-1", 1, Decimal("5"), Decimal("2"), 2)]
        with self.assertRaises(ValueError):
            analyse_inventory(sales, {"SKU-1": product()}, forecast_window_days=0)

    def test_annual_days_must_be_finite_and_positive(self):
        sales = [Sale(date(2026, 1, 1), "SKU-1", 1, Decimal("5"), Decimal("2"), 2)]
        for value in (0, -1, float("inf"), float("nan")):
            with self.subTest(annual_days=value), self.assertRaises(ValueError):
                analyse_inventory(sales, {"SKU-1": product()}, annual_days=value)

    def test_inventory_position_includes_open_orders_and_backorders(self):
        start = date(2026, 1, 1)
        sales = [Sale(start, "SKU-1", 3, Decimal("10"), Decimal("6"), 2)]
        stocked = product(on_hand=20, on_order=12, backorders=5)
        results, _ = analyse_inventory(sales, {"SKU-1": stocked})
        self.assertEqual(results[0].inventory_position, 27)

    def test_order_quantity_obeys_minimum_and_pack_multiple(self):
        start = date(2026, 1, 1)
        sales = [Sale(start, "SKU-1", 3, Decimal("10"), Decimal("6"), 2)]
        stocked = product(on_hand=0, pack_size=8, min_order_qty=20)
        results, _ = analyse_inventory(sales, {"SKU-1": stocked})
        self.assertEqual(results[0].decision, "REORDER")
        self.assertGreaterEqual(results[0].recommended_order_qty, 20)
        self.assertEqual(results[0].recommended_order_qty % 8, 0)

    def test_revenue_and_cost_totals_remain_decimal_exact(self):
        start = date(2026, 1, 1)
        sales = [
            Sale(start, "SKU-1", 3, Decimal("0.10"), Decimal("0.03"), 2),
            Sale(start, "SKU-1", 7, Decimal("0.20"), Decimal("0.07"), 3),
        ]
        results, summary = analyse_inventory(sales, {"SKU-1": product()})
        self.assertEqual(results[0].revenue, Decimal("1.70"))
        self.assertEqual(results[0].cost_of_goods_sold, Decimal("0.58"))
        self.assertEqual(results[0].gross_profit, Decimal("1.12"))
        self.assertEqual(summary["gross_profit"], "1.12")


if __name__ == "__main__":
    unittest.main()
