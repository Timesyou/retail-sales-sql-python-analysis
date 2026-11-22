PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS v_replenishment_queue;
DROP VIEW IF EXISTS v_category_performance;
DROP TABLE IF EXISTS recommendations;
DROP TABLE IF EXISTS sku_metrics;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    on_hand INTEGER NOT NULL CHECK (on_hand >= 0),
    on_order INTEGER NOT NULL CHECK (on_order >= 0),
    backorders INTEGER NOT NULL CHECK (backorders >= 0),
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days > 0),
    order_cost TEXT NOT NULL,
    annual_holding_cost TEXT NOT NULL,
    service_level REAL NOT NULL CHECK (service_level > 0 AND service_level < 1),
    pack_size INTEGER NOT NULL CHECK (pack_size > 0),
    min_order_qty INTEGER NOT NULL CHECK (min_order_qty > 0)
);

CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    sale_date TEXT NOT NULL,
    sku TEXT NOT NULL REFERENCES products(sku),
    units INTEGER NOT NULL CHECK (units > 0),
    unit_price TEXT NOT NULL,
    unit_cost TEXT NOT NULL
);

CREATE INDEX idx_sales_sku_date ON sales(sku, sale_date);

CREATE TABLE sku_metrics (
    sku TEXT PRIMARY KEY REFERENCES products(sku),
    units_sold INTEGER NOT NULL,
    revenue TEXT NOT NULL,
    cost_of_goods_sold TEXT NOT NULL,
    gross_profit TEXT NOT NULL,
    gross_margin_pct REAL NOT NULL,
    average_daily_demand REAL NOT NULL,
    daily_demand_stddev REAL NOT NULL,
    demand_cv REAL,
    forecast_daily_demand REAL NOT NULL,
    abc_class TEXT NOT NULL,
    xyz_class TEXT NOT NULL,
    safety_stock INTEGER NOT NULL,
    reorder_point INTEGER NOT NULL,
    economic_order_quantity INTEGER NOT NULL,
    inventory_position INTEGER NOT NULL,
    stock_cover_days REAL
);

CREATE TABLE recommendations (
    sku TEXT PRIMARY KEY REFERENCES products(sku),
    decision TEXT NOT NULL CHECK (decision IN ('HOLD', 'REORDER')),
    recommended_order_qty INTEGER NOT NULL CHECK (recommended_order_qty >= 0),
    estimated_order_value TEXT NOT NULL
);

CREATE VIEW v_replenishment_queue AS
SELECT p.sku, p.name, p.category, r.recommended_order_qty,
       m.reorder_point, m.inventory_position, r.estimated_order_value
FROM recommendations AS r
JOIN products AS p USING (sku)
JOIN sku_metrics AS m USING (sku)
WHERE r.decision = 'REORDER'
ORDER BY m.abc_class, r.estimated_order_value DESC;

CREATE VIEW v_category_performance AS
SELECT p.category,
       SUM(m.units_sold) AS units_sold,
       SUM(CAST(m.revenue AS REAL)) AS revenue,
       SUM(CAST(m.gross_profit AS REAL)) AS gross_profit,
       COUNT(*) AS sku_count
FROM products AS p
JOIN sku_metrics AS m USING (sku)
GROUP BY p.category;
