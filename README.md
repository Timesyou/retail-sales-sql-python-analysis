# ShelfSense

**Retail sales analytics and inventory replenishment, built as a small, auditable Python application.**

ShelfSense turns transaction lines and a stock file into SKU-level commercial metrics, ABC–XYZ segments, a transparent demand baseline, reorder points, safety stock, EOQ-based order quantities, CSV reports and a queryable SQLite snapshot.

It uses the Python standard library only. There are no API keys, paid services, external data downloads or hidden dependencies.

## What it does

- Validates sales and inventory CSV files before doing any calculations.
- Calculates units sold, revenue, cost of goods sold, gross profit and gross margin using `Decimal` for financial arithmetic.
- Builds a complete daily demand series, including days with zero sales.
- Produces a recency-weighted moving-average demand baseline.
- Segments products by revenue contribution (ABC) and demand variability (XYZ).
- Calculates service-level-based safety stock, reorder points and economic order quantities.
- Accounts for on-hand units, open purchase orders, backorders, minimum order quantities and pack-size multiples.
- Exports a self-contained `dashboard.html`, `sku_performance.csv`, `replenishment_plan.csv`, `summary.json` and `shelfsense.sqlite`.
- Includes SQL views, 30 unit tests and a GitHub Actions test workflow.

## Quick start

Python 3.10 or later is required.

```bash
python -m venv .venv
```

Activate the environment, then install the project:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -e .

# macOS / Linux
source .venv/bin/activate
python -m pip install -e .
```

Run the included demonstration data:

```bash
python -m shelfsense --sales data/sales.csv --inventory data/inventory.csv --output reports
```

Or, after installation:

```bash
shelfsense --sales data/sales.csv --inventory data/inventory.csv --output reports
```

On Windows, `scripts\run_demo.ps1` installs the local package in editable mode, regenerates the sample reports and opens the dashboard in your browser.

The command exits with code `0` when reports are created and `2` for invalid inputs or a processing error. The generated `reports/` directory is intentionally excluded from version control.


## Publish to your GitHub repository

From the extracted project folder, run this in PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\clone_and_publish.ps1
```

It clones `Timesyou/retail-sales-sql-python-analysis` into `%USERPROFILE%\source\retail-sales-sql-python-analysis` if the folder does not exist, then runs the guarded publisher. To use an existing clean clone instead:

```powershell
.\scripts\publish_to_github.ps1 -RepositoryPath "C:\path\to\retail-sales-sql-python-analysis"
```

The publisher verifies the repository URL, requires the `main` branch and a clean working tree, copies the project, creates a commit on a new `feature/shelfsense-publish-*` branch, and pushes only that branch. It never pushes directly to `main` or force-pushes. Review the printed GitHub compare link and open a pull request. GitHub authentication must be configured locally; pushing workflow files may require the credential to have the `workflow` permission. Never paste an access token into the script or a chat.

## Included demonstration

The `demo-output/` folder contains reports generated from the bundled synthetic CSV files, including a SQLite snapshot that can be opened with DB Browser for SQLite. Open `demo-output/dashboard.html` to see the dashboard without installing anything.

## Output files

| File | Contents |
| --- | --- |
| `sku_performance.csv` | Sales, margin, demand, segmentation and stock metrics for every SKU |
| `replenishment_plan.csv` | Only SKUs at or below their reorder point, with proposed quantities |
| `summary.json` | Reporting window, sales totals and replenishment summary |
| `dashboard.html` | Responsive, self-contained dashboard; opens locally in a browser |
| `shelfsense.sqlite` | Source products and transactions, calculated metrics, recommendations and SQL views |

Useful SQLite views are `v_replenishment_queue` and `v_category_performance`. Example queries are in [`sql_examples.sql`](sql_examples.sql).

## Input files

The expected headers and validation rules are documented in [`docs/data_dictionary.md`](docs/data_dictionary.md). A short example is supplied in `data/`. The sample records are synthetic and exist only to make the project runnable immediately.

Money fields must use one consistent currency and tax convention. ShelfSense does not guess the currency, tax treatment or supplier terms.

## Calculation notes

The formulas, choices and limitations are described in [`docs/methodology.md`](docs/methodology.md). The core policy is:

- `inventory_position = on_hand + on_order - backorders`
- `safety_stock = ceil(z × daily_demand_stddev × √lead_time_days)`
- `reorder_point = ceil(forecast_daily_demand × lead_time_days + safety_stock)`
- `EOQ = ceil(√(2 × annual_demand × order_cost / annual_holding_cost_per_unit))`
- The order target is `reorder_point + EOQ`, rounded up to satisfy minimum quantity and pack size.

This is a baseline decision-support model, not an autonomous purchasing system. Its normal-demand safety-stock approximation assumes fixed lead time and approximately independent, normally distributed daily demand. It does not model promotions, holidays, lead-time variation, expiry, supplier calendars or stock reservations. Validate the outputs and back-test the forecast before using business data for live purchasing.

## Tests

Run the test suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests cover statistical formulas, service-level quantiles, exact decimal aggregation, input validation, zero-demand products, replenishment constraints, dashboard escaping and SQLite output. GitHub Actions installs the package, runs the archive-security and application suites, compiles the source, and exercises the installed CLI on Python 3.10, 3.11, 3.12 and 3.13.

## Project layout

```text
src/shelfsense/   Application, ingestion, calculations, database, dashboard and reporting
sql_examples.sql Example SQL analysis queries
data/             Synthetic 90-day input files
scripts/          Demo runner, data generator and guarded GitHub publishing scripts
docs/             Data contract and calculation methodology
tests/            Standard-library unit tests
.github/workflows Continuous-integration test workflow
```

## License

MIT. See [`LICENSE`](LICENSE).
