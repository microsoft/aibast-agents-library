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

## Portfolio optimization scenario (the demo default)

A consumer-goods manufacturer's warehouse portfolio. This scenario is the default for the agent's portfolio
operations; the facility and SKU tables above are a separate distribution-network detail view.

| Measure | Value |
|---|---|
| Total inventory | $5.0M |
| Slow-moving (30%) | $1.5M tied up |
| Warehouse utilization | 95% (critical) |
| Annual holding cost | $675K (13.5% of inventory value) |
| Cost of capital | 8% |

### Slow-moving breakdown

| Category | Value | Recommended action |
|---|---|---|
| Obsolete | $450K | liquidate immediately |
| Seasonal | $300K | store or pre-sell |
| Excess safety stock | $375K | right-size |
| Dead stock | $125K | write off |
| Other slow movers | $250K | consignment |
| Total slow-moving | $1.5M | |

### 90-day recovery plan (recommendation)

| Phase | Action | Cash / capital |
|---|---|---|
| Phase 1: Immediate Actions (Week 1-2) | Flash sale: 50% off obsolete items ($450K inventory) | $225K |
| Phase 1 | Vendor returns: $200K (restocking fees: $20K) | $180K net |
| Phase 1 | Write-offs: $125K dead stock (tax benefit: $31K) | $31K |
| Phase 2: Strategic Moves (Week 3-6) | Pre-season sale: $300K seasonal (80% recovery) | $240K |
| Phase 2 | Consignment agreements: $180K slow movers | $180K |
| Phase 2 | Safety stock reduction: $375K -> $150K freed | $150K |
| Phase 3: Optimization (Week 7-12) | Reorder point adjustments across 240 SKUs | $194K |
| Phase 3 | JIT agreements with 3 key suppliers; ABC analysis implementation | - |

Total Cash Recovery: $1.2M in 90 days (phase totals $436K, $570K, $194K).

### Warehouse impact

| Category | Current | After Optimization | Freed |
|---|---|---|---|
| Obsolete items | 12% | 1% | 11% |
| Excess safety | 18% | 8% | 10% |
| Seasonal storage | 15% | 11% | 4% |
| Dead stock | 5% | 0% | 5% |

Current Utilization 95% (Critical - operations impaired) -> New Utilization: 65% (Optimal operational range).
Benefits: improved picking efficiency +35%; reduced handling damage -40%; faster order fulfillment -2 days avg;
cycle count accuracy 94% -> 98%; staff safety (reduced congestion hazards). Capacity for Growth: room for $2.8M
additional inventory.

### Financial impact

- Cash freed: $1.2M (24% of total inventory); cost of capital 8% = $96K annual benefit.

| Category | Annual Savings |
|---|---|
| Holding costs reduced | $202K |
| Warehouse rent (avoid expansion) | $180K |
| Obsolescence write-offs | $135K |
| Handling efficiency | $78K |
| Insurance premiums | $45K |
| Total Annual Savings | $640K |

3-Year Value: $1.92M + $1.2M working capital = $3.12M. Implementation Cost: $42K (software + consulting).
Net ROI: 7,329% over 3 years.

### 90-day execution timeline

| Window | Actions | Cash in window |
|---|---|---|
| Week 1-2: Crisis Actions | Launch flash sale; process vendor returns (3 suppliers); tag and segregate dead stock | Expected cash: $307K (flash sale $225K + first vendor-return credits $82K) |
| Week 3-6: Strategic Liquidation | Pre-season promotional campaign; negotiate consignment deals; implement dynamic pricing | Expected recovery: $465K (vendor credits $98K + pre-season sale $240K + consignment $127K) |
| Week 7-12: System Optimization | AI-powered reorder points; JIT supplier agreements; ABC classification rollout; team training 40 staff hours | $428K (consignment $53K + tax benefit $31K + safety stock $150K + reorder points $194K) |

Milestones: Day 14: $300K cash recovered; Day 45: Warehouse at 75% utilization; Day 90: $1.2M working capital freed.
The timeline is prepared for the manager to share in Microsoft Teams; the agent does not post it.

### Continuous optimization (monitoring plan)

- Real-Time Dashboards: inventory velocity by SKU; days-on-hand trending; slow-moving item alerts (>90 days);
  working capital efficiency.
- Automated Actions (proposed policy; each needs an approved tool and owner): auto-flag items at 60 days no
  movement; price optimization for aging inventory; reorder point adjustments weekly; excess stock alerts to procurement.
- Monthly Reviews: ABC analysis updates; obsolescence risk assessment; supplier performance scoring; warehouse
  utilization trends.
- Success Metrics: Inventory turns 4.2 -> 7.8 (target); working capital ratio improved 35%; obsolescence rate
  6% -> <2%; perfect order rate +12%.

### Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| IR-01 | Supply Chain Manager | `inventory_snapshot` | Which distribution centers are tight on space, and which SKU positions should my team review first? | Dallas Fulfillment Center; SKU-4406 |
| IR-02 | Inventory Manager | `rebalance_recommendation` | Where do we have forecast-relative shortages or excess that deserve a rebalancing review? | SKU-4402; SLOW-MOVING |
| IR-03 | Supply Chain Manager | `transfer_plan` | Show me the proposed warehouse moves, but do not move or reserve anything. | SKU-4401; No inventory has been reserved |
| IR-04 | Procurement Manager | `cost_analysis` | Where is inventory exposure concentrated, and what trade-offs should I take to the planning meeting? | Total annual holding cost; synthetic planning estimates |
| IR-05 | Supply Chain Manager | `portfolio_analysis` | We have $5M inventory, 30% slow-moving, warehouse 95% full. Need optimization plan. | $1.5M tied up; $675K; Excess safety stock |
| IR-06 | Supply Chain Manager | `recovery_plan` | Yes, show me a phased plan to recover cash from the slow-moving stock. | Phase 1: Immediate Actions; $225K; $1.2M in 90 days |
| IR-07 | Inventory Manager | `warehouse_impact` | What would that plan do to our warehouse space and operations? | New Utilization; 65%; $2.8M |
| IR-08 | Procurement Manager | `financial_impact` | What are the savings and the ROI if we do this? | $640K; $3.12M; 7,329% |
| IR-09 | Supply Chain Manager | `execution_timeline` | Lay out the 90-day rollout with milestones I can share with stakeholders. | $307K; $465K; Day 45 |
| IR-10 | Inventory Manager | `monitoring_plan` | How do we keep inventory optimized after the 90 days? | 60 days no movement; Inventory turns; Success Metrics |
