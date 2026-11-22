-- Run these against reports/shelfsense.sqlite with the SQLite CLI or DB Browser.

-- 1. Highest-gross-profit SKUs (values are stored as decimal text to preserve
--    Python's Decimal output; cast only for approximate ranking in SQLite).
SELECT sku, units_sold, revenue, gross_profit, gross_margin_pct, abc_class, xyz_class
FROM sku_metrics
ORDER BY CAST(gross_profit AS REAL) DESC, sku
LIMIT 10;

-- 2. Actionable replenishment queue.
SELECT sku, name, category, inventory_position, reorder_point,
       recommended_order_qty, estimated_order_value
FROM v_replenishment_queue
ORDER BY CAST(estimated_order_value AS REAL) DESC;

-- 3. Category-level commercial performance.
SELECT category, sku_count, units_sold, ROUND(revenue, 2) AS revenue,
       ROUND(gross_profit, 2) AS gross_profit
FROM v_category_performance
ORDER BY revenue DESC;
