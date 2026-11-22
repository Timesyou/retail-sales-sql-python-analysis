# Quality checks and reproducibility

This document records the checks that can be repeated locally. It is intentionally separate from claims about a live retailer or production deployment.

## Run the checks

From the project root:

```bash
python -m pip install --editable .
python -m unittest discover -s tests -v
python -m compileall -q src tests
python -m shelfsense --sales data/sales.csv --inventory data/inventory.csv --output reports
```

The test suite includes checks for exact decimal aggregation, demand-series construction, statistical boundaries, annualisation inputs, stock-position arithmetic, pack and minimum-quantity rules, malformed CSVs, dashboard escaping, and SQLite report contents.

## Sample-data run

The bundled inputs are synthetic. A run over those inputs should report:

| Measure | Result |
| --- | ---: |
| Observation window | 2026-01-01 to 2026-03-31 (90 days) |
| Transaction lines | 652 |
| Products | 9 |
| Units sold | 6,375 |
| Revenue | 21,766.85 |
| Cost of goods sold | 12,500.43 |
| Gross profit | 9,266.42 |
| Gross margin | 42.57% |
| SKUs at reorder point | 3 |

The figures are deterministic outputs from the included sample CSVs, not independent market benchmarks or real business results. Because all monetary fields are supplied without a currency code, the figures are in the sample's notional currency units.

## Database inspection

After running the CLI, these checks can be performed with Python:

```python
import sqlite3

connection = sqlite3.connect("reports/shelfsense.sqlite")
print(connection.execute("PRAGMA integrity_check").fetchone()[0])
print(connection.execute("SELECT COUNT(*) FROM sales").fetchone()[0])
print(connection.execute("SELECT COUNT(*) FROM sku_metrics").fetchone()[0])
print(connection.execute("SELECT COUNT(*) FROM v_replenishment_queue").fetchone()[0])
connection.close()
```

The integrity check should return `ok`. Table and view names are defined in `src/shelfsense/schema.sql`.

## Known limits

- There is no seasonal, holiday, promotion or price-response model.
- Safety stock assumes fixed lead time and approximately normal, independent daily demand.
- New products without observed sales are retained but not automatically reordered.
- The estimated purchase value uses observed weighted-average unit cost, not a supplier quotation.
- The generated dashboard is a local report, not a live inventory connection.
