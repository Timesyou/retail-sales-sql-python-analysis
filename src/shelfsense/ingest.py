"""CSV ingestion and row-level validation."""

from __future__ import annotations

import csv
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import Product, Sale


class DataValidationError(ValueError):
    """Raised when an input file violates the documented data contract."""


SALES_COLUMNS = {"date", "sku", "units", "unit_price", "unit_cost"}
PRODUCT_COLUMNS = {
    "sku", "name", "category", "on_hand", "on_order", "backorders",
    "lead_time_days", "order_cost", "annual_holding_cost", "service_level",
    "pack_size", "min_order_qty",
}


def _read_dict_rows(path: Path, required: set[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise DataValidationError(f"File does not exist: {path}")
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise DataValidationError(f"{path}: missing CSV header")
            normalized_headers = [header.strip() if header is not None else "" for header in reader.fieldnames]
            if any(not header for header in normalized_headers):
                raise DataValidationError(f"{path}: column names cannot be blank")
            if len(normalized_headers) != len(set(normalized_headers)):
                raise DataValidationError(f"{path}: duplicate column names are not allowed")
            headers = set(normalized_headers)
            missing = sorted(required - headers)
            if missing:
                raise DataValidationError(f"{path}: missing required columns: {', '.join(missing)}")
            rows = []
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise DataValidationError(f"{path}: row {row_number} has more values than the header")
                if not row or all(value is None or not value.strip() for value in row.values()):
                    continue
                rows.append({key.strip(): (value or "").strip() for key, value in row.items() if key})
            return rows
    except UnicodeDecodeError as exc:
        raise DataValidationError(f"{path}: expected UTF-8 encoded CSV") from exc


def _integer(value: str, field: str, row_number: int, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise DataValidationError(f"Row {row_number}: {field} must be a whole number") from exc
    if str(parsed) != value.strip() and value.strip() not in {f"+{parsed}"}:
        raise DataValidationError(f"Row {row_number}: {field} must be a whole number")
    if parsed < minimum:
        raise DataValidationError(f"Row {row_number}: {field} must be at least {minimum}")
    return parsed


def _decimal(value: str, field: str, row_number: int, *, minimum: Decimal = Decimal("0")) -> Decimal:
    try:
        parsed = Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise DataValidationError(f"Row {row_number}: {field} must be numeric") from exc
    if not parsed.is_finite() or parsed < minimum:
        raise DataValidationError(f"Row {row_number}: {field} must be finite and at least {minimum}")
    return parsed


def load_sales(path: str | Path) -> list[Sale]:
    rows = _read_dict_rows(Path(path), SALES_COLUMNS)
    sales: list[Sale] = []
    for row_number, row in enumerate(rows, start=2):
        date_text = row["date"]
        if not re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", date_text):
            raise DataValidationError(f"Row {row_number}: date must use YYYY-MM-DD")
        try:
            sale_date = date.fromisoformat(date_text)
        except ValueError as exc:
            raise DataValidationError(f"Row {row_number}: date must be a valid calendar date") from exc
        sku = row["sku"].strip()
        if not sku:
            raise DataValidationError(f"Row {row_number}: sku cannot be empty")
        units = _integer(row["units"], "units", row_number, minimum=1)
        unit_price = _decimal(row["unit_price"], "unit_price", row_number)
        unit_cost = _decimal(row["unit_cost"], "unit_cost", row_number)
        sales.append(Sale(sale_date, sku, units, unit_price, unit_cost, row_number))
    if not sales:
        raise DataValidationError("Sales file contains no transaction rows")
    return sales


def load_products(path: str | Path) -> dict[str, Product]:
    rows = _read_dict_rows(Path(path), PRODUCT_COLUMNS)
    products: dict[str, Product] = {}
    for row_number, row in enumerate(rows, start=2):
        sku = row["sku"].strip()
        if not sku:
            raise DataValidationError(f"Row {row_number}: sku cannot be empty")
        if sku in products:
            raise DataValidationError(f"Row {row_number}: duplicate product sku {sku!r}")
        name = row["name"].strip()
        if not name:
            raise DataValidationError(f"Row {row_number}: name cannot be empty")
        service_level = float(_decimal(row["service_level"], "service_level", row_number, minimum=Decimal("0")))
        if not 0.0 < service_level < 1.0:
            raise DataValidationError(f"Row {row_number}: service_level must be strictly between 0 and 1")
        products[sku] = Product(
            sku=sku,
            name=name,
            category=row["category"].strip() or "Uncategorized",
            on_hand=_integer(row["on_hand"], "on_hand", row_number),
            on_order=_integer(row["on_order"], "on_order", row_number),
            backorders=_integer(row["backorders"], "backorders", row_number),
            lead_time_days=_integer(row["lead_time_days"], "lead_time_days", row_number, minimum=1),
            order_cost=_decimal(row["order_cost"], "order_cost", row_number),
            annual_holding_cost=_decimal(row["annual_holding_cost"], "annual_holding_cost", row_number),
            service_level=service_level,
            pack_size=_integer(row["pack_size"], "pack_size", row_number, minimum=1),
            min_order_qty=_integer(row["min_order_qty"], "min_order_qty", row_number, minimum=1),
        )
    if not products:
        raise DataValidationError("Inventory file contains no product rows")
    return products
