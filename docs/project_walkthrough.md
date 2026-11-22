# Project walkthrough

This note is a technical guide to the codebase. It is not a record of work performed for a real retailer.

## The problem

A shop may have transaction history and a stock count, but those files do not directly answer three operational questions: which products produce the most sales value, which products have regular or erratic demand, and which products have fallen to a level where replenishment should be reviewed?

ShelfSense joins those questions in one reproducible run. It deliberately stops before placing an order because supplier constraints and real purchase decisions need human review.

## Why the calculation sequence matters

Daily demand is built before forecasting so missing transaction dates become zero-demand days rather than disappearing from the average. That is important: averaging only days with a sale would overstate demand for intermittent products.

Revenue and cost are aggregated from transaction lines. ABC classification uses cumulative revenue contribution; XYZ classification uses the coefficient of variation of daily demand. The two labels measure different things: value contribution and demand regularity.

The replenishment stage uses inventory position rather than on-hand stock alone. A purchase order already in transit increases inventory position, while backorders reduce it. This avoids recommending stock that is already on its way or ignoring units promised to customers.

## Worked reorder example

Assume a SKU has a 5-day lead time, a forecast of 8.2 units per day, a daily-demand standard deviation of 2.0 units and a 95% target cycle-service level. The one-sided normal quantile is approximately 1.6449.

- Safety stock = ceil(1.6449 × 2.0 × √5) = ceil(7.36) = 8 units.
- Reorder point = ceil(8.2 × 5 + 8) = 49 units.
- If inventory position is 40, and EOQ is 60, the target gap is (49 + 60) − 40 = 69 units.
- With a minimum order of 12 and a pack size of 6, the final recommendation remains 72 units after rounding to the next pack multiple.

A result can be reproduced directly from the source values and the formulas in `methodology.md`.

## Interview discussion points

A reviewer may reasonably ask why the forecast is not seasonal, whether the normal approximation is appropriate for intermittent demand, how supplier lead-time variability changes safety stock, or why a new SKU is not automatically reordered. Those are real model limitations, not hidden features. Good next steps include rolling-origin forecast evaluation, a variable-lead-time safety-stock model and a review workflow for exceptions.
