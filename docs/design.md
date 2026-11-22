# Design and implementation notes

## Data flow

1. `ingest.py` reads both CSV files and validates the complete input contract. It fails early instead of silently dropping unrecognized SKUs or coercing malformed quantities.
2. `models.py` defines immutable records shared by the application layers.
3. `engine.py` aggregates transaction lines, constructs daily SKU demand series and calculates commercial and replenishment metrics.
4. `reporting.py` writes flat CSV exports and a JSON summary; `dashboard.py` creates a local, self-contained HTML view.
5. `database.py` writes source rows and calculated metrics to SQLite. The database includes indexed sales rows and two views for common analysis questions.
6. `cli.py` coordinates the pipeline and returns a non-zero exit code when validation or output generation fails.

## Important invariants

- Every sales SKU must exist in the inventory master. Inventory-only SKUs are allowed and stay visible in the result.
- Units, stock counts, lead time and order multiples are whole numbers. Financial source amounts use decimal arithmetic.
- Inventory position includes stock already on order and subtracts backorders.
- A product with no observed demand is kept in the output but is not automatically reordered. A new product needs an explicit demand or launch-plan input before an automated replenishment model can sensibly size it.
- Recommended order quantities always satisfy the minimum order quantity and pack-size multiple.
- The application creates recommendations only. It has no supplier credentials, purchase-order integration or autonomous ordering capability.

## Deliberate trade-offs

The project uses only the Python standard library to make the example easy to run on a fresh machine and to keep financial rules visible. `Decimal` is used for currency arithmetic; statistical calculations use floating point because the normal quantile and square-root formulas are statistical approximations. SQLite stores money values as text so that the exact decimal representation remains available; example SQL casts those values to `REAL` only for approximate ordering and charting.

The 28-day weighted moving average is a transparent baseline rather than a claim of best-in-class forecasting. A production deployment should compare it against seasonal-naive and other candidates using rolling-origin back-tests, report forecast error by SKU, account for lead-time variability and evaluate the cost of stockouts versus carrying stock.
