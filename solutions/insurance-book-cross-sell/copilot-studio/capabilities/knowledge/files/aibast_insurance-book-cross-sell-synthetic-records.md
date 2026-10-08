# Book of Business Cross-Sell Agent — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Northwind Mutual, its five underwriting units and their contacts, Fabrikam Insurance Brokers, Priya Natarajan, and the seven accounts are fictional. Every class code, premium, expiration date, appetite rule and reply is invented. Never match them to a real organization, person or live system.

## Complete synthetic records

Each section below is the exact output of one operation over the fixed snapshot (demo defaults). Together they contain every record, figure and rule the pilot may cite.

### Book of business summary (`book_summary`)

**Book of Business: Fabrikam Insurance Brokers (as of 2026-10-05)**

| Line | Account | State | Line of Business | Current Carrier | Expires | Premium |
|---|---|---|---|---|---|---|
| BK-01 | Alder Creek Framing | CO | General Liability | Other market | 2026-12-15 | $48,000 |
| BK-02 | Alder Creek Framing | CO | Workers Compensation | Other market | 2026-12-15 | $62,000 |
| BK-03 | Bluebird Bakery Co | OR | Property | Northwind Mutual | 2027-01-10 | $21,000 |
| BK-04 | Cedar Point Logistics | TX | Commercial Auto | Other market | 2026-11-30 | $95,000 |
| BK-05 | Cedar Point Logistics | TX | Inland Marine | Other market | 2026-11-30 | $18,000 |
| BK-06 | Driftwood Dental Group | WA | Professional Liability | Other market | 2027-02-01 | $14,000 |
| BK-07 | Elmstone Paving | AZ | General Liability | Northwind Mutual | 2026-12-31 | $41,000 |
| BK-08 | Elmstone Paving | AZ | Surety Bond | Other market | 2026-12-31 | $30,000 |
| BK-09 | Foxglove Studio | CA | General Liability | Other market | 2027-01-15 | $7,000 |
| BK-10 | Granite Ridge Storage | NV | Property | Other market | 2027-01-20 | $27,000 |

**Book at a glance:** 7 accounts, 10 policy lines, $363,000 total premium. 2 lines are already with Northwind Mutual; 8 lines ($301,000) sit with other markets.

**Next step:** classify every line so it can be checked against unit appetite.

### Industry class resolution (`classify_lines`)

**Industry Class Resolution: 7 accounts**

| Account | Description on Book | Industry Class | Basis |
|---|---|---|---|
| Alder Creek Framing | Framing contractor | IC-2381 Framing and structural contractors | Explicit class on the book |
| Bluebird Bakery Co | Wholesale bakery | IC-3118 Commercial bakeries | Legacy code L-2051 crosswalk |
| Cedar Point Logistics | Regional trucking fleet | IC-4841 General freight trucking | Keyword 'trucking' in description |
| Driftwood Dental Group | Dental group practice | IC-6212 Dental practices | Explicit class on the book |
| Elmstone Paving | Asphalt paving contractor | IC-2373 Paving and road contractors | Keyword 'paving' in description |
| Foxglove Studio | Creative services | Unresolved | Unresolved: ask the broker |
| Granite Ridge Storage | Self storage facilities | IC-4931 Warehousing and storage | Legacy code L-4225 crosswalk |

**Resolved 6 of 7 accounts:** 2 explicit, 2 by legacy crosswalk, 2 by keyword rule.
**Needs the broker:** Foxglove Studio (class not guessed; held from matching).

### Appetite and white-space match (`appetite_match`)

**Appetite Match: Fabrikam Insurance Brokers book**

| Account | Class | Already With Us | Competing-Market Lines | White Space (new lines) |
|---|---|---|---|---|
| Alder Creek Framing | IC-2381 | - | General Liability -> Northwind Casualty; Workers Compensation -> Northwind Casualty | Surety Bond -> Northwind Surety |
| Bluebird Bakery Co | IC-3118 | Property | - | General Liability -> Northwind Casualty |
| Cedar Point Logistics | IC-4841 | - | Commercial Auto -> Northwind Casualty; Inland Marine -> Northwind Inland Marine | - |
| Driftwood Dental Group | IC-6212 | - | Professional Liability -> Northwind Professional | Property -> Northwind Property |
| Elmstone Paving | IC-2373 | General Liability | Surety Bond -> Northwind Surety | Workers Compensation -> Northwind Casualty |
| Foxglove Studio | Unresolved | - | - | Held: Needs class from broker |
| Granite Ridge Storage | IC-4931 | - | Property -> Northwind Property | General Liability -> Northwind Casualty |

**Opportunity:** 7 competing-market lines worth $294,000 at renewal, plus 5 white-space lines with no current policy; 2 lines are already with us.
**State filter:** Elmstone Paving: Inland Marine (Northwind Inland Marine unavailable in AZ).
**Next step:** ask each underwriting unit to confirm appetite before anything is routed.

### Unit appetite confirmation drafts (`unit_confirmation`)

**Unit Appetite Confirmation Drafts - Not Sent**

**Northwind Property** (2 opportunities, contact Marcus Lee)

| Account | Opportunity | Expires | Premium |
|---|---|---|---|
| Driftwood Dental Group | Property (new line) | 2027-02-01 | New line |
| Granite Ridge Storage | Property at renewal | 2027-01-20 | $27,000 |

> Draft note to Marcus Lee: "From the Fabrikam Insurance Brokers book, these accounts look like a fit for Northwind Property: Driftwood Dental Group, Granite Ridge Storage. Can you confirm appetite, or tell us which to pass on, by Oct 12?"

**Northwind Casualty** (6 opportunities, contact Elena Ruiz)

| Account | Opportunity | Expires | Premium |
|---|---|---|---|
| Alder Creek Framing | General Liability at renewal | 2026-12-15 | $48,000 |
| Alder Creek Framing | Workers Compensation at renewal | 2026-12-15 | $62,000 |
| Bluebird Bakery Co | General Liability (new line) | 2027-01-10 | New line |
| Cedar Point Logistics | Commercial Auto at renewal | 2026-11-30 | $95,000 |
| Elmstone Paving | Workers Compensation (new line) | 2026-12-31 | New line |
| Granite Ridge Storage | General Liability (new line) | 2027-01-20 | New line |

> Draft note to Elena Ruiz: "From the Fabrikam Insurance Brokers book, these accounts look like a fit for Northwind Casualty: Alder Creek Framing, Bluebird Bakery Co, Cedar Point Logistics, Elmstone Paving, Granite Ridge Storage. Can you confirm appetite, or tell us which to pass on, by Oct 12?"

**Northwind Surety** (2 opportunities, contact Tom Becker)

| Account | Opportunity | Expires | Premium |
|---|---|---|---|
| Alder Creek Framing | Surety Bond (new line) | 2026-12-15 | New line |
| Elmstone Paving | Surety Bond at renewal | 2026-12-31 | $30,000 |

> Draft note to Tom Becker: "From the Fabrikam Insurance Brokers book, these accounts look like a fit for Northwind Surety: Alder Creek Framing, Elmstone Paving. Can you confirm appetite, or tell us which to pass on, by Oct 12?"

**Northwind Professional** (1 opportunity, contact Grace Okafor)

| Account | Opportunity | Expires | Premium |
|---|---|---|---|
| Driftwood Dental Group | Professional Liability at renewal | 2027-02-01 | $14,000 |

> Draft note to Grace Okafor: "From the Fabrikam Insurance Brokers book, these accounts look like a fit for Northwind Professional: Driftwood Dental Group. Can you confirm appetite, or tell us which to pass on, by Oct 12?"

**Northwind Inland Marine** (1 opportunity, contact Sam Patel)

| Account | Opportunity | Expires | Premium |
|---|---|---|---|
| Cedar Point Logistics | Inland Marine at renewal | 2026-11-30 | $18,000 |

> Draft note to Sam Patel: "From the Fabrikam Insurance Brokers book, these accounts look like a fit for Northwind Inland Marine: Cedar Point Logistics. Can you confirm appetite, or tell us which to pass on, by Oct 12?"

**Shortlist:** 12 opportunities across 5 units. Status: Draft for your review; nothing is routed until the units reply.

### Broker confirmation draft (`broker_confirmation`)

**Broker Confirmation Draft - Not Sent**

| Shortlisted Account | Lines on the Book |
|---|---|
| Alder Creek Framing | General Liability, Workers Compensation |
| Bluebird Bakery Co | Property |
| Cedar Point Logistics | Commercial Auto, Inland Marine |
| Driftwood Dental Group | Professional Liability |
| Elmstone Paving | General Liability, Surety Bond |
| Granite Ridge Storage | Property |

> To Priya Natarajan, Fabrikam Insurance Brokers: "We reviewed your book and found 6 accounts we believe Northwind Mutual can help with. Before we involve our units, can you confirm none of them are out of business or already placed elsewhere? For Foxglove Studio, can you tell us the type of business so we can classify it?"

**Status:** Draft for your review. Broker replies remove accounts before routing.

### Cross-sell routing plan (`routing_plan`)

**Cross-Sell Routing Plan - Draft, Not Routed**

| Account | Opportunity | Unit | Seller | Expires | Follow-Up By |
|---|---|---|---|---|---|
| Cedar Point Logistics | Commercial Auto at renewal | Northwind Casualty | Elena Ruiz | 2026-11-30 | Now (window opened 2026-10-01) |
| Cedar Point Logistics | Inland Marine at renewal | Northwind Inland Marine | Sam Patel | 2026-11-30 | Now (window opened 2026-10-01) |
| Alder Creek Framing | General Liability at renewal | Northwind Casualty | Elena Ruiz | 2026-12-15 | 2026-10-16 |
| Alder Creek Framing | Workers Compensation at renewal | Northwind Casualty | Elena Ruiz | 2026-12-15 | 2026-10-16 |
| Alder Creek Framing | Surety Bond (new line) | Northwind Surety | Tom Becker | 2026-12-15 | 2026-10-16 |
| Elmstone Paving | Workers Compensation (new line) | Northwind Casualty | Elena Ruiz | 2026-12-31 | 2026-11-01 |
| Bluebird Bakery Co | General Liability (new line) | Northwind Casualty | Elena Ruiz | 2027-01-10 | 2026-11-11 |
| Driftwood Dental Group | Property (new line) | Northwind Property | Marcus Lee | 2027-02-01 | 2026-12-03 |
| Driftwood Dental Group | Professional Liability at renewal | Northwind Professional | Grace Okafor | 2027-02-01 | 2026-12-03 |

**Removed after replies:**

| Account | Opportunity | Reason |
|---|---|---|
| Granite Ridge Storage | Property at renewal | Broker: renewed early with its current market |
| Granite Ridge Storage | General Liability (new line) | Broker: renewed early with its current market |
| Elmstone Paving | Surety Bond at renewal | Northwind Surety passed: bond capacity for paving is full this quarter |

**Plan:** 9 opportunities ready to route ($237,000 competing-market premium plus new lines); follow-up is set 60 days before each expiration. Still held: Foxglove Studio (needs class from broker).
**Next step:** a person approves the plan and creates the pipeline records.

### `unit_confirmation` with unit = property

**Unit Appetite Confirmation Drafts - Not Sent**

**Northwind Property** (2 opportunities, contact Marcus Lee)

| Account | Opportunity | Expires | Premium |
|---|---|---|---|
| Driftwood Dental Group | Property (new line) | 2027-02-01 | New line |
| Granite Ridge Storage | Property at renewal | 2027-01-20 | $27,000 |

> Draft note to Marcus Lee: "From the Fabrikam Insurance Brokers book, these accounts look like a fit for Northwind Property: Driftwood Dental Group, Granite Ridge Storage. Can you confirm appetite, or tell us which to pass on, by Oct 12?"

**Shortlist:** 2 opportunities across 1 units. Status: Draft for your review; nothing is routed until the units reply.

### `unit_confirmation` with unit = casualty

**Unit Appetite Confirmation Drafts - Not Sent**

**Northwind Casualty** (6 opportunities, contact Elena Ruiz)

| Account | Opportunity | Expires | Premium |
|---|---|---|---|
| Alder Creek Framing | General Liability at renewal | 2026-12-15 | $48,000 |
| Alder Creek Framing | Workers Compensation at renewal | 2026-12-15 | $62,000 |
| Bluebird Bakery Co | General Liability (new line) | 2027-01-10 | New line |
| Cedar Point Logistics | Commercial Auto at renewal | 2026-11-30 | $95,000 |
| Elmstone Paving | Workers Compensation (new line) | 2026-12-31 | New line |
| Granite Ridge Storage | General Liability (new line) | 2027-01-20 | New line |

> Draft note to Elena Ruiz: "From the Fabrikam Insurance Brokers book, these accounts look like a fit for Northwind Casualty: Alder Creek Framing, Bluebird Bakery Co, Cedar Point Logistics, Elmstone Paving, Granite Ridge Storage. Can you confirm appetite, or tell us which to pass on, by Oct 12?"

**Shortlist:** 6 opportunities across 1 units. Status: Draft for your review; nothing is routed until the units reply.

### `unit_confirmation` with unit = surety

**Unit Appetite Confirmation Drafts - Not Sent**

**Northwind Surety** (2 opportunities, contact Tom Becker)

| Account | Opportunity | Expires | Premium |
|---|---|---|---|
| Alder Creek Framing | Surety Bond (new line) | 2026-12-15 | New line |
| Elmstone Paving | Surety Bond at renewal | 2026-12-31 | $30,000 |

> Draft note to Tom Becker: "From the Fabrikam Insurance Brokers book, these accounts look like a fit for Northwind Surety: Alder Creek Framing, Elmstone Paving. Can you confirm appetite, or tell us which to pass on, by Oct 12?"

**Shortlist:** 2 opportunities across 1 units. Status: Draft for your review; nothing is routed until the units reply.

### `unit_confirmation` with unit = professional

**Unit Appetite Confirmation Drafts - Not Sent**

**Northwind Professional** (1 opportunity, contact Grace Okafor)

| Account | Opportunity | Expires | Premium |
|---|---|---|---|
| Driftwood Dental Group | Professional Liability at renewal | 2027-02-01 | $14,000 |

> Draft note to Grace Okafor: "From the Fabrikam Insurance Brokers book, these accounts look like a fit for Northwind Professional: Driftwood Dental Group. Can you confirm appetite, or tell us which to pass on, by Oct 12?"

**Shortlist:** 1 opportunities across 1 units. Status: Draft for your review; nothing is routed until the units reply.

### `unit_confirmation` with unit = marine

**Unit Appetite Confirmation Drafts - Not Sent**

**Northwind Inland Marine** (1 opportunity, contact Sam Patel)

| Account | Opportunity | Expires | Premium |
|---|---|---|---|
| Cedar Point Logistics | Inland Marine at renewal | 2026-11-30 | $18,000 |

> Draft note to Sam Patel: "From the Fabrikam Insurance Brokers book, these accounts look like a fit for Northwind Inland Marine: Cedar Point Logistics. Can you confirm appetite, or tell us which to pass on, by Oct 12?"

**Shortlist:** 1 opportunities across 1 units. Status: Draft for your review; nothing is routed until the units reply.

## Record resolution rules

- The book belongs to Fabrikam Insurance Brokers and is fixed; every operation reads the same ten lines.
- `unit_confirmation` takes an optional `unit`: all (default), property, casualty, surety, professional or marine. Any other value returns "No synthetic underwriting unit matches".
- Industry class order: explicit class on the book, then the legacy crosswalk (L-2051, L-4225), then a keyword rule (trucking, paving). Anything else is unresolved and held.
- Follow-up dates are 60 days before each expiration; a window that opened before the 2026-10-05 snapshot shows as Now.

## Locked-case evidence contract

Each locked case below routes to one skill; a correct answer always contains every listed evidence string.

| Case | Persona | Prompt | Skill | Must include |
|---|---|---|---|---|
| XS-01 | Cross-Sell Manager | A broker just sent over their book of business. What's in it? | `book-summary` | `10 policy lines`; `$363,000 total premium`; `Fabrikam Insurance Brokers` |
| XS-02 | Cross-Sell Manager | Can you fill in the industry classes for those accounts and tell me which ones you couldn't figure out? | `classify-lines` | `Resolved 6 of 7 accounts`; `Foxglove Studio`; `Legacy code L-2051 crosswalk` |
| XS-03 | Cross-Sell Manager | Which of these accounts fit our appetite, and where's the white space? | `appetite-match` | `7 competing-market lines`; `5 white-space lines`; `unavailable in AZ` |
| XS-04 | Underwriting Unit Lead | Ask our underwriting units to confirm they want these before we route anything. | `unit-confirmation` | `Not Sent`; `12 opportunities across 5 units`; `Elena Ruiz` |
| XS-05 | Broker Relationship Manager | Now draft a note back to the broker to make sure none of these are dead or already placed. | `broker-confirmation` | `Broker Confirmation Draft`; `Priya Natarajan`; `out of business or already placed elsewhere` |
| XS-06 | Cross-Sell Manager | The replies are in. Route what's left to the right sellers with follow-up dates. | `routing-plan` | `9 opportunities ready to route`; `renewed early with its current market`; `Follow-Up By` |
