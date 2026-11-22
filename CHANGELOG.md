# Changelog

## 1.1.0

- Tightened CSV header validation and rejected blank column names.
- Used compensated floating-point summation for demand statistics.
- Validated the annualisation basis before calculating EOQ demand.
- Kept the highest-revenue SKU in ABC class A when one item alone exceeds the 80% target.
- Expanded coverage for financial arithmetic, replenishment constraints, malformed inputs and SQL outputs.

## 1.0.0

- Initial ShelfSense release.
- Added validated CSV ingestion, retail metrics, ABC–XYZ segmentation and replenishment calculations.
- Added CSV/JSON exports, a self-contained HTML dashboard and SQLite analysis views.
- Added deterministic sample data, a reproducible data generator, tests and GitHub Actions CI.
