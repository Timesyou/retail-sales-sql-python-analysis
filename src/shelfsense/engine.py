"""Core sales analysis, demand segmentation and replenishment calculations."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_CEILING

from .math_utils import abc_classes, population_stddev, round_up_to_multiple, service_level_z, weighted_moving_average, xyz_class
from .models import Product, Sale, SkuAnalysis


ZERO = Decimal("0")


def _ceil_decimal(value: float) -> int:
    return int(Decimal(str(max(0.0, value))).to_integral_value(rounding=ROUND_CEILING))


def analyse_inventory(
    sales: list[Sale],
    products: dict[str, Product],
    *,
    forecast_window_days: int = 28,
    annual_days: float = 365.25,
) -> tuple[list[SkuAnalysis], dict[str, object]]:
    """Calculate SKU-level performance and replenishment recommendations.

    Daily demand is zero-filled across the complete observed sales date range.
    Forecasting uses a linearly weighted moving average over the latest
    ``forecast_window_days``. Reorder points use a normal approximation for
    lead-time demand and the product's stated cycle-service level.
    """
    if not sales:
        raise ValueError("At least one sale is required")
    if forecast_window_days < 1:
        raise ValueError("forecast_window_days must be at least 1")
    if not math.isfinite(annual_days) or annual_days <= 0:
        raise ValueError("annual_days must be a finite number greater than zero")
    unknown = sorted({sale.sku for sale in sales} - set(products))
    if unknown:
        raise ValueError(f"Sales contain SKUs missing from inventory: {', '.join(unknown)}")

    first_day = min(sale.sale_date for sale in sales)
    last_day = max(sale.sale_date for sale in sales)
    observed_days = (last_day - first_day).days + 1
    daily_units: dict[str, dict[date, int]] = {sku: defaultdict(int) for sku in products}
    units: dict[str, int] = defaultdict(int)
    revenue: dict[str, Decimal] = defaultdict(lambda: ZERO)
    cogs: dict[str, Decimal] = defaultdict(lambda: ZERO)

    for sale in sales:
        daily_units[sale.sku][sale.sale_date] += sale.units
        units[sale.sku] += sale.units
        revenue[sale.sku] += sale.unit_price * sale.units
        cogs[sale.sku] += sale.unit_cost * sale.units

    abc = abc_classes({sku: revenue[sku] for sku in products})
    results: list[SkuAnalysis] = []

    for sku, product in products.items():
        series = [daily_units[sku].get(first_day + timedelta(days=offset), 0) for offset in range(observed_days)]
        recent = series[-forecast_window_days:]
        average = sum(series) / observed_days
        sigma = population_stddev(series)
        forecast = weighted_moving_average(recent)
        cv = sigma / average if average > 0 else None
        xyz = xyz_class(cv)

        sku_revenue = revenue[sku]
        sku_cogs = cogs[sku]
        gross_profit = sku_revenue - sku_cogs
        margin = float(gross_profit / sku_revenue * 100) if sku_revenue > ZERO else 0.0

        z_score = service_level_z(product.service_level)
        safety_stock = _ceil_decimal(z_score * sigma * math.sqrt(product.lead_time_days))
        reorder_point = _ceil_decimal(forecast * product.lead_time_days + safety_stock)
        annual_demand = units[sku] * annual_days / observed_days
        holding_cost = float(product.annual_holding_cost)
        ordering_cost = float(product.order_cost)
        eoq = _ceil_decimal(math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)) if holding_cost > 0 and ordering_cost > 0 and annual_demand > 0 else 0

        inventory_position = product.on_hand + product.on_order - product.backorders
        stock_cover = max(0, inventory_position) / forecast if forecast > 0 else None
        if units[sku] > 0 and inventory_position <= reorder_point:
            target_gap = max(0, reorder_point + eoq - inventory_position)
            base_quantity = max(target_gap, product.min_order_qty)
            recommended = round_up_to_multiple(base_quantity, product.pack_size)
            decision = "REORDER"
        else:
            recommended = 0
            decision = "HOLD"

        average_unit_cost = sku_cogs / units[sku] if units[sku] > 0 else ZERO
        order_value = average_unit_cost * recommended
        results.append(SkuAnalysis(
            sku=sku,
            name=product.name,
            category=product.category,
            units_sold=units[sku],
            revenue=sku_revenue,
            cost_of_goods_sold=sku_cogs,
            gross_profit=gross_profit,
            gross_margin_pct=margin,
            average_daily_demand=average,
            daily_demand_stddev=sigma,
            demand_cv=cv,
            forecast_daily_demand=forecast,
            abc_class=abc[sku],
            xyz_class=xyz,
            safety_stock=safety_stock,
            reorder_point=reorder_point,
            economic_order_quantity=eoq,
            inventory_position=inventory_position,
            stock_cover_days=stock_cover,
            decision=decision,
            recommended_order_qty=recommended,
            estimated_order_value=order_value,
        ))

    results.sort(key=lambda item: (-item.revenue, item.sku))
    total_revenue = sum(revenue.values(), ZERO)
    total_cogs = sum(cogs.values(), ZERO)
    reorder_rows = [item for item in results if item.decision == "REORDER"]
    summary: dict[str, object] = {
        "period_start": first_day.isoformat(),
        "period_end": last_day.isoformat(),
        "observed_days": observed_days,
        "sku_count": len(products),
        "transaction_lines": len(sales),
        "units_sold": sum(units.values()),
        "revenue": str(total_revenue.quantize(Decimal("0.01"))),
        "cost_of_goods_sold": str(total_cogs.quantize(Decimal("0.01"))),
        "gross_profit": str((total_revenue - total_cogs).quantize(Decimal("0.01"))),
        "gross_margin_pct": round(float((total_revenue - total_cogs) / total_revenue * 100), 2) if total_revenue > ZERO else 0.0,
        "skus_to_reorder": len(reorder_rows),
        "recommended_order_units": sum(item.recommended_order_qty for item in reorder_rows),
        "estimated_replenishment_value": str(sum((item.estimated_order_value for item in reorder_rows), ZERO).quantize(Decimal("0.01"))),
        "forecast_method": f"Weighted moving average over the latest {forecast_window_days} observed calendar days",
    }
    return results, summary
