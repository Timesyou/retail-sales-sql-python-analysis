# Calculation methodology

ShelfSense is a transparent planning baseline, not a demand-planning service that claims to know future sales. Every result is derived from the supplied transaction and inventory files.

## Sales and margin

For each SKU:

- Revenue = Σ(units × unit selling price).
- Cost of goods sold = Σ(units × unit cost).
- Gross profit = revenue − cost of goods sold.
- Gross margin (%) = gross profit ÷ revenue × 100. It is reported as zero when revenue is zero because a margin ratio is undefined in that case.

Financial source values are parsed as `Decimal`; CSV reports retain two decimal places. The chosen currency is not inferred. All monetary columns must use the same currency and tax treatment.

## Daily demand and baseline forecast

The observation window runs from the earliest to the latest transaction date, inclusive. Each SKU receives one observation per calendar day; dates without sales are filled with zero. Average daily demand and population standard deviation are calculated over this series.

The forecast is a linearly weighted moving average over the most recent `forecast_window` calendar days. The newest day receives weight *n*, the prior day *n − 1*, and so on. This makes the forecast responsive to recent changes, but it does not model holidays, promotions, price changes or weekly seasonality. It should be back-tested before operational use.

The coefficient of variation is daily-demand standard deviation divided by average daily demand. XYZ classes are X (CV ≤ 0.50), Y (0.50 < CV ≤ 1.00), and Z (CV > 1.00). A SKU with no observed demand receives N.

## ABC classification

SKUs are sorted by descending observed revenue, with SKU as a deterministic tie-breaker. A targets the first 80% of revenue, B the next band up to 95%, and C the remainder. The highest-revenue SKU is always class A, even when it contributes more than 80% by itself; subsequent SKUs use the cumulative cutoffs. This avoids the counterintuitive result of having no A-class product in a highly concentrated assortment. These are configurable business conventions, not universal laws. Zero-revenue SKUs are class C.

## Replenishment calculations

- Annualized demand = observed units × 365.25 ÷ observed calendar days.
- Safety stock = ceil(z × daily-demand standard deviation × √lead time).
- Reorder point = ceil(forecast daily demand × lead time + safety stock).
- EOQ = ceil(√(2 × annual demand × order cost ÷ annual holding cost per unit)). EOQ is set to zero when annual demand, ordering cost or holding cost is zero; the reorder threshold still applies.
- Inventory position = on hand + on order − backorders.
- A SKU is marked REORDER when inventory position is at or below its reorder point. The target is reorder point + EOQ. The recommended quantity is rounded up to the greater of the target gap and minimum order quantity, then rounded to a pack-size multiple.

The `annual_days` parameter must be finite and greater than zero; its default is 365.25. The service-level z value is the one-sided standard-normal quantile for the requested cycle-service probability. This calculation assumes independent, approximately normally distributed daily demand and a fixed lead time. It does not account for lead-time variability, supplier constraints, order calendars, shelf life, or correlated demand. For intermittent or highly skewed demand, the normal approximation can be poor.

## Operational use

Review the generated plan with a buyer before placing orders. Confirm supplier minimums, pack rules, open purchase orders, returns, promotions, stock reservations and product lifecycle status. The estimate of replenishment value uses the SKU's observed weighted-average unit cost and is not a supplier quote.
