# Inventory Rebalancing Pilot — Facility & SKU Synthetic Snapshot

> SYNTHETIC PILOT DATA. Every warehouse, SKU, quantity, forecast, and reorder
> point below is fictional. No live ERP or warehouse-management system was
> queried to produce this snapshot; treat it strictly as a fixed reference
> data set for the pilot.

## Facility snapshot

| Facility ID | Facility name | Region | Capacity (pallets) | Used (pallets) | Utilization |
|---|---|---|---|---|---|
| WH-ATL | Atlanta Distribution Center | Southeast | 12,000 | 10,450 | 87.1% |
| WH-ORD | Chicago Regional Hub | Midwest | 18,000 | 9,200 | 51.1% |
| WH-DFW | Dallas Fulfillment Center | South Central | 15,000 | 14,100 | 94.0% |
| WH-SEA | Seattle West Coast Depot | Pacific Northwest | 10,000 | 4,300 | 43.0% |

Facilities above 90% synthetic utilization (currently WH-DFW, Dallas
Fulfillment Center) represent the highest facility-pressure review priority.
Facilities with available capacity (WH-ORD, WH-SEA) are candidate receiving
locations for inbound transfers.

## SKU on-hand levels by facility

| SKU | Description | WH-ATL | WH-ORD | WH-DFW | WH-SEA | Reorder point |
|---|---|---|---|---|---|---|
| SKU-4401 | Brushless DC Motor 48V | 3,200 | 1,800 | 4,100 | 600 | 1,200 |
| SKU-4402 | Planetary Gearbox PG-20 | 750 | 2,400 | 300 | 1,100 | 500 |
| SKU-4403 | Linear Actuator LA-150 | 1,900 | 500 | 2,600 | 200 | 600 |
| SKU-4404 | Servo Controller SC-800 | 400 | 1,200 | 950 | 1,800 | 350 |
| SKU-4405 | Encoder Module EM-512 | 5,000 | 3,100 | 4,800 | 900 | 2,000 |
| SKU-4406 | Harmonic Drive HD-25 | 180 | 620 | 90 | 340 | 150 |

`SKU-4406` (Harmonic Drive HD-25) has a fixed synthetic reorder point of
150 units. On-hand at WH-DFW (90 units) is below this reorder point and
should be reviewed first; on-hand at WH-ATL (180), WH-ORD (620), and WH-SEA
(340) remain above the reorder point. Apply this same below-reorder-point
check to every SKU and facility in the table above.

## Demand forecast by facility (synthetic, forecast period unspecified)

| SKU | WH-ATL | WH-ORD | WH-DFW | WH-SEA |
|---|---|---|---|---|
| SKU-4401 | 2,800 | 2,600 | 3,000 | 1,500 |
| SKU-4402 | 1,100 | 900 | 1,200 | 800 |
| SKU-4403 | 800 | 1,400 | 1,100 | 900 |
| SKU-4404 | 700 | 600 | 800 | 500 |
| SKU-4405 | 3,500 | 4,200 | 3,800 | 2,300 |
| SKU-4406 | 300 | 250 | 400 | 280 |

Compare on-hand minus forecast to identify a forecast-relative surplus
(positive delta) or shortage (negative delta). Treat any delta beyond ±200
units as material; treat deltas within ±200 units as balanced within
tolerance. This delta is a planning signal, not a live available-to-promise
value.

## Synthetic portfolio classification

| SKU | Velocity | Strategic value | Lifecycle risk |
|---|---|---|---|
| SKU-4401 | MEDIUM | CORE | LOW |
| SKU-4402 | SLOW-MOVING | HIGH | LOW |
| SKU-4403 | SLOW-MOVING | STANDARD | ELEVATED |
| SKU-4404 | MEDIUM | HIGH | LOW |
| SKU-4405 | FAST | CORE | LOW |
| SKU-4406 | SLOW-MOVING | CRITICAL | ELEVATED |

`SKU-4402`, `SKU-4403`, and `SKU-4406` are classified SLOW-MOVING in this
fixed pilot profile. `SKU-4403` and `SKU-4406` also carry ELEVATED synthetic
lifecycle risk. A lifecycle-risk signal is a review flag, not an
obsolescence declaration — vendor return, controlled disposition, or any
portfolio-policy change requires source-system evidence and authorized
review.

All facility names, SKU identifiers, quantities, forecasts, reorder points,
and classifications above are synthetic pilot evidence, not production data.
