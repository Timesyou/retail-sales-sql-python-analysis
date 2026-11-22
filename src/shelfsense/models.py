"""Typed records shared by the ingestion and analytics layers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Sale:
    sale_date: date
    sku: str
    units: int
    unit_price: Decimal
    unit_cost: Decimal
    source_row: int


@dataclass(frozen=True, slots=True)
class Product:
    sku: str
    name: str
    category: str
    on_hand: int
    on_order: int
    backorders: int
    lead_time_days: int
    order_cost: Decimal
    annual_holding_cost: Decimal
    service_level: float
    pack_size: int
    min_order_qty: int


@dataclass(frozen=True, slots=True)
class SkuAnalysis:
    sku: str
    name: str
    category: str
    units_sold: int
    revenue: Decimal
    cost_of_goods_sold: Decimal
    gross_profit: Decimal
    gross_margin_pct: float
    average_daily_demand: float
    daily_demand_stddev: float
    demand_cv: float | None
    forecast_daily_demand: float
    abc_class: str
    xyz_class: str
    safety_stock: int
    reorder_point: int
    economic_order_quantity: int
    inventory_position: int
    stock_cover_days: float | None
    decision: str
    recommended_order_qty: int
    estimated_order_value: Decimal

    def as_record(self) -> dict[str, object]:
        """Return a flat, CSV/JSON-friendly representation."""
        return {
            "sku": self.sku,
            "product_name": self.name,
            "category": self.category,
            "units_sold": self.units_sold,
            "revenue": str(self.revenue.quantize(Decimal("0.01"))),
            "cost_of_goods_sold": str(self.cost_of_goods_sold.quantize(Decimal("0.01"))),
            "gross_profit": str(self.gross_profit.quantize(Decimal("0.01"))),
            "gross_margin_pct": round(self.gross_margin_pct, 2),
            "average_daily_demand": round(self.average_daily_demand, 4),
            "daily_demand_stddev": round(self.daily_demand_stddev, 4),
            "demand_cv": None if self.demand_cv is None else round(self.demand_cv, 4),
            "forecast_daily_demand": round(self.forecast_daily_demand, 4),
            "abc_class": self.abc_class,
            "xyz_class": self.xyz_class,
            "safety_stock": self.safety_stock,
            "reorder_point": self.reorder_point,
            "economic_order_quantity": self.economic_order_quantity,
            "inventory_position": self.inventory_position,
            "stock_cover_days": None if self.stock_cover_days is None else round(self.stock_cover_days, 2),
            "decision": self.decision,
            "recommended_order_qty": self.recommended_order_qty,
            "estimated_order_value": str(self.estimated_order_value.quantize(Decimal("0.01"))),
        }
