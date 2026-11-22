"""Small, dependency-free statistical helpers with explicit edge cases."""

from __future__ import annotations

import math
from decimal import Decimal
from statistics import NormalDist
from typing import Sequence


def weighted_moving_average(values: Sequence[int | float]) -> float:
    """Return a linear weighted mean; the newest observation gets the largest weight."""
    if not values:
        raise ValueError("At least one observation is required")
    denominator = len(values) * (len(values) + 1) / 2
    numerator = math.fsum((index + 1) * value for index, value in enumerate(values))
    return numerator / denominator


def population_stddev(values: Sequence[int | float]) -> float:
    """Population standard deviation; daily sales are treated as the observed population."""
    if not values:
        raise ValueError("At least one observation is required")
    average = math.fsum(values) / len(values)
    variance = math.fsum((value - average) ** 2 for value in values) / len(values)
    return math.sqrt(variance)


def service_level_z(service_level: float) -> float:
    """Convert a one-sided cycle-service probability to its standard-normal quantile."""
    if not 0.0 < service_level < 1.0:
        raise ValueError("service_level must be strictly between 0 and 1")
    return NormalDist().inv_cdf(service_level)


def round_up_to_multiple(quantity: int, multiple: int) -> int:
    """Round a non-negative quantity up to an integer pack multiple."""
    if quantity < 0:
        raise ValueError("quantity cannot be negative")
    if multiple < 1:
        raise ValueError("multiple must be at least 1")
    if quantity == 0:
        return 0
    return ((quantity + multiple - 1) // multiple) * multiple


def abc_classes(revenue_by_sku: dict[str, Decimal | int | float]) -> dict[str, str]:
    """Classify SKUs by cumulative revenue contribution (A: 80%, B: next 15%, C: rest)."""
    values = {sku: max(Decimal("0"), Decimal(str(value))) for sku, value in revenue_by_sku.items()}
    total = sum(values.values(), Decimal("0"))
    if total <= 0:
        return {sku: "C" for sku in values}

    result: dict[str, str] = {}
    cumulative = Decimal("0")
    ordered = sorted(values.items(), key=lambda item: (-item[1], item[0]))
    for index, (sku, revenue) in enumerate(ordered):
        cumulative += revenue
        share = cumulative / total
        # Keep the leading SKU in class A even when it alone exceeds 80%.
        if index == 0 or share <= Decimal("0.80"):
            result[sku] = "A"
        elif share <= Decimal("0.95"):
            result[sku] = "B"
        else:
            result[sku] = "C"
    return result


def xyz_class(cv: float | None) -> str:
    """Classify demand regularity; undefined CV is treated as non-moving (N)."""
    if cv is None:
        return "N"
    if cv <= 0.50:
        return "X"
    if cv <= 1.00:
        return "Y"
    return "Z"
