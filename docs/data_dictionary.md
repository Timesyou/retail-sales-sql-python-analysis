# Input data contract

Both inputs are UTF-8 CSV files. Headers are case-sensitive and must match the names below. Blank lines are ignored. Dates use ISO `YYYY-MM-DD` format. No external data is downloaded.

## `sales.csv`

| Column | Type | Rule |
| --- | --- | --- |
| `date` | date | Transaction date, `YYYY-MM-DD` |
| `sku` | text | Non-empty product key |
| `units` | integer | Positive whole number |
| `unit_price` | decimal | Non-negative selling price per unit |
| `unit_cost` | decimal | Non-negative cost per unit |

Each row is a transaction line. Multiple rows for the same SKU and date are aggregated.

## `inventory.csv`

| Column | Type | Rule |
| --- | --- | --- |
| `sku` | text | Unique product key; must match sales SKUs |
| `name` | text | Non-empty product name |
| `category` | text | Optional label; blank becomes `Uncategorized` |
| `on_hand` | integer | Non-negative physical stock |
| `on_order` | integer | Non-negative open purchase-order quantity |
| `backorders` | integer | Non-negative committed but unfilled quantity |
| `lead_time_days` | integer | Positive fixed lead time |
| `order_cost` | decimal | Non-negative cost per replenishment order |
| `annual_holding_cost` | decimal | Non-negative annual holding cost per unit |
| `service_level` | decimal | Strictly between 0 and 1, e.g. `0.95` |
| `pack_size` | integer | Positive order multiple |
| `min_order_qty` | integer | Positive minimum order quantity |

Products with no sales during the observed window are retained and classified N. Products with sales but no inventory master row cause validation to fail rather than being silently dropped.

## Sample data

The files in `data/` are deterministic, synthetic examples created for testing and demonstration. They do not represent a real retailer, customer, supplier, or business outcome. Replace them with properly authorized business data before using the tool for decisions.
