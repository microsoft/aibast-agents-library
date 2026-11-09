# Supplier Claim Engagement — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Fabrikam Grocers and every supplier, purchase order, item, cost, evidence reference, deadline, and response are invented. The fixed demo clock is Apr 14, 2026 10:00. Never match them to a real organization, person, or live record.

## Complete synthetic records

Every value the agent uses, exactly as bundled in the portable agent source.

### Retailer

```json
"Fabrikam Grocers"
```

### Now

```json
[
 2026,
 4,
 14,
 10
]
```

### Now Label

```json
"Apr 14, 2026 10:00"
```

### Terms

```json
{
 "Quality": {
  "severity": "P1 - Critical",
  "response_h": 8,
  "resolve_bd": 3
 },
 "Damage": {
  "severity": "P2 - High",
  "response_h": 24,
  "resolve_bd": 5
 },
 "Shortage": {
  "severity": "P3 - Medium",
  "response_h": 36,
  "resolve_bd": 7
 },
 "Pricing": {
  "severity": "P4 - Low",
  "response_h": 60,
  "resolve_bd": 10
 }
}
```

### Required Evidence

```json
{
 "Damage": [
  "Damage photos (2 or more)",
  "Receiving inspection report",
  "Delivery note signed with exception"
 ],
 "Shortage": [
  "Delivery note signed with exception",
  "Receiving count sheet"
 ],
 "Quality": [
  "Temperature log",
  "Receiving inspection report",
  "Product photos (2 or more)"
 ],
 "Pricing": [
  "Purchase order price",
  "Supplier invoice",
  "Agreed price list"
 ]
}
```

### Claims

```json
{
 "CLM-5201": {
  "id": "CLM-5201",
  "type": "Damage",
  "supplier": "Northwind Packaging",
  "po": "PO-77310",
  "store": "Distribution Center 2",
  "delivered": "Apr 10, 2026",
  "status": "Ready to draft",
  "lines": [
   [
    "Sparkling water 12-pack",
    18,
    21.5
   ],
   [
    "Pasta sauce glass jars, case of 12",
    6,
    34.0
   ]
  ],
  "evidence": {
   "Damage photos (2 or more)": "3 photos",
   "Receiving inspection report": "RIR-4471",
   "Delivery note signed with exception": "DN-90318"
  },
  "sent_hour": null,
  "response": null
 },
 "CLM-5202": {
  "id": "CLM-5202",
  "type": "Shortage",
  "supplier": "Tailspin Freight",
  "po": "PO-77288",
  "store": "Distribution Center 1",
  "delivered": "Apr 9, 2026",
  "status": "Sent, awaiting response",
  "lines": [
   [
    "Whole-grain cereal, case of 10",
    12,
    28.75
   ]
  ],
  "evidence": {
   "Delivery note signed with exception": "DN-90207",
   "Receiving count sheet": "RC-2215"
  },
  "sent_hour": -38,
  "response": null
 },
 "CLM-5203": {
  "id": "CLM-5203",
  "type": "Quality",
  "supplier": "Alpine Dairy Co-op",
  "po": "PO-77295",
  "store": "Distribution Center 2",
  "delivered": "Apr 13, 2026",
  "status": "Sent, awaiting response",
  "lines": [
   [
    "Greek yogurt cups, case of 24",
    32,
    19.4
   ]
  ],
  "evidence": {
   "Temperature log": "TL-0412",
   "Receiving inspection report": "RIR-4466",
   "Product photos (2 or more)": "4 photos"
  },
  "sent_hour": -7,
  "response": null
 },
 "CLM-5204": {
  "id": "CLM-5204",
  "type": "Pricing",
  "supplier": "Litware Snacks",
  "po": "PO-77251",
  "store": "All stores",
  "delivered": "Apr 6, 2026",
  "status": "Supplier responded",
  "lines": [
   [
    "Kettle chips, case of 24 (invoiced 16.90 vs agreed 15.40)",
    50,
    1.5
   ]
  ],
  "evidence": {
   "Purchase order price": "PO-77251",
   "Supplier invoice": "INV-L-6620",
   "Agreed price list": "Price list effective Jan 5, 2026"
  },
  "sent_hour": -68,
  "response": {
   "received": "Apr 13, 2026 09:00",
   "hours_to_respond": 43,
   "position": "Partial acceptance",
   "accepted_units": 30,
   "reason": "Supplier says 20 cases shipped before the new price list took effect"
  }
 },
 "CLM-5205": {
  "id": "CLM-5205",
  "type": "Damage",
  "supplier": "Northwind Packaging",
  "po": "PO-77104",
  "store": "Distribution Center 1",
  "delivered": "Mar 27, 2026",
  "status": "Closed - credit received",
  "lines": [
   [
    "Olive oil bottles, case of 6",
    10,
    41.0
   ]
  ],
  "evidence": {
   "Damage photos (2 or more)": "2 photos",
   "Receiving inspection report": "RIR-4398",
   "Delivery note signed with exception": "DN-89955"
  },
  "sent_hour": null,
  "response": null,
  "recovered": 410.0
 }
}
```

### Escalation Role

```json
"Category manager, pantry and beverages"
```

### Default Claim

```json
{
 "triage_claim": "CLM-5201",
 "evidence_pack": "CLM-5201",
 "draft_supplier_claim": "CLM-5201",
 "supplier_response": "CLM-5204",
 "escalation_brief": "CLM-5202"
}
```

## Exact responses for every locked case

### SC-01 — Supplier claims queue

Prompt: "Show me our open supplier claims and what needs attention today."

Operation: `claims_queue`; arguments: `{"operation": "claims_queue"}`

**Supplier Claims Queue: Fabrikam Grocers, Apr 14, 2026 10:00**

| Claim | Type | Supplier | Value | Severity | Status |
|---|---|---|---|---|---|
| CLM-5201 | Damage | Northwind Packaging | $591.00 | P2 - High | Ready to draft |
| CLM-5202 | Shortage | Tailspin Freight | $345.00 | P3 - Medium | Sent, awaiting response |
| CLM-5203 | Quality | Alpine Dairy Co-op | $620.80 | P1 - Critical | Sent, awaiting response |
| CLM-5204 | Pricing | Litware Snacks | $75.00 | P4 - Low | Supplier responded |
| CLM-5205 | Damage | Northwind Packaging | $410.00 | P2 - High | Closed - credit received |

| Measure | Value |
|---|---|
| Open claims | 4 |
| Open claim value | $1,631.80 |
| Recovered this month | $410.00 |

**Next step:** CLM-5201 is new and ready to draft; CLM-5202 is past its response window.

Synthetic claims evidence only. This agent does not send a claim, contact a supplier, accept or reject a credit, escalate, or change a case; an authorized claims coordinator reviews every draft.

Source: [Synthetic Fabrikam Grocers Claims Snapshot]
Agents: SupplierClaimEngagementAgent

### SC-02 — Claim triage

Prompt: "Triage the new damage claim CLM-5201. Who is responsible and what are the terms?"

Operation: `triage_claim`; arguments: `{"operation": "triage_claim", "claim_id": "CLM-5201"}`

**Claim Triage: CLM-5201**

| Detail | Value |
|---|---|
| Claim type | Damage |
| Severity | P2 - High |
| Responsible supplier | Northwind Packaging |
| Purchase order | PO-77310 |
| Received at | Distribution Center 2, delivered Apr 10, 2026 |
| Claim value | $591.00 |
| Supplier response window | 24 hours |
| Resolution window | 5 business days |
| Routing | Supplier claims coordinator, then Northwind Packaging claims desk |

**Next step:** check the evidence pack, then draft the supplier claim notice.

Synthetic claims evidence only. This agent does not send a claim, contact a supplier, accept or reject a credit, escalate, or change a case; an authorized claims coordinator reviews every draft.

Source: [Synthetic Fabrikam Grocers Claims Snapshot]
Agents: SupplierClaimEngagementAgent

### SC-03 — Evidence pack check

Prompt: "Is the evidence for CLM-5201 complete, and what is the claim worth?"

Operation: `evidence_pack`; arguments: `{"operation": "evidence_pack", "claim_id": "CLM-5201"}`

**Evidence Pack: CLM-5201 (Damage, Northwind Packaging)**

| Required Evidence | On File |
|---|---|
| Damage photos (2 or more) | 3 photos |
| Receiving inspection report | RIR-4471 |
| Delivery note signed with exception | DN-90318 |

**Evidence status:** Complete

| Affected Item | Units | Unit Cost | Line Value |
|---|---|---|---|
| Sparkling water 12-pack | 18 | $21.50 | $387.00 |
| Pasta sauce glass jars, case of 12 | 6 | $34.00 | $204.00 |
| **Total claim value** | | | **$591.00** |

Synthetic claims evidence only. This agent does not send a claim, contact a supplier, accept or reject a credit, escalate, or change a case; an authorized claims coordinator reviews every draft.

Source: [Synthetic Fabrikam Grocers Claims Snapshot]
Agents: SupplierClaimEngagementAgent

### SC-04 — Supplier claim notice draft

Prompt: "Draft the claim notice to the supplier for CLM-5201, but don't send it."

Operation: `draft_supplier_claim`; arguments: `{"operation": "draft_supplier_claim", "claim_id": "CLM-5201"}`

**Supplier Claim Notice - Draft, Not Sent**

| Field | Value |
|---|---|
| To | Northwind Packaging claims desk (synthetic) |
| Claim | CLM-5201 - Damage, P2 - High |
| Purchase order | PO-77310 delivered Apr 10, 2026 |
| Claim value | $591.00 |
| Evidence attached | 3 photos, RIR-4471, DN-90318 |
| Response due if sent now | Apr 15, 2026 10:00 (24 h) |
| Resolution due if sent now | Apr 21, 2026 (5 business days) |

**Message draft:** "Fabrikam Grocers is filing a damage claim on PO-77310. Affected items: 18 x Sparkling water 12-pack ($387.00); 6 x Pasta sauce glass jars, case of 12 ($204.00). Total $591.00. The evidence pack is attached. Please respond within 24 hours with a credit or replacement proposal."

Status: Draft for coordinator review. Nothing was sent and no deadline clock was started.

Synthetic claims evidence only. This agent does not send a claim, contact a supplier, accept or reject a credit, escalate, or change a case; an authorized claims coordinator reviews every draft.

Source: [Synthetic Fabrikam Grocers Claims Snapshot]
Agents: SupplierClaimEngagementAgent

### SC-05 — Response deadline tracker

Prompt: "Which supplier claims are at risk of missing their response deadline?"

Operation: `sla_tracker`; arguments: `{"operation": "sla_tracker"}`

**Supplier Response Deadlines: Apr 14, 2026 10:00**

| Claim | Supplier | Window | Elapsed | Status |
|---|---|---|---|---|
| CLM-5201 | Northwind Packaging | 24 h | - | Not sent |
| CLM-5202 | Tailspin Freight | 36 h | 38 h | Breached by 2 h |
| CLM-5203 | Alpine Dairy Co-op | 8 h | 7 h | At risk (1 h left) |
| CLM-5204 | Litware Snacks | 60 h | 43 h | Responded within window |

**Breached:** CLM-5202  
**At risk:** CLM-5203

**Next step:** prepare the escalation brief for CLM-5202 and a reminder draft for CLM-5203.

Synthetic claims evidence only. This agent does not send a claim, contact a supplier, accept or reject a credit, escalate, or change a case; an authorized claims coordinator reviews every draft.

Source: [Synthetic Fabrikam Grocers Claims Snapshot]
Agents: SupplierClaimEngagementAgent

### SC-06 — Supplier response evaluation

Prompt: "Litware Snacks replied on CLM-5204. What did they offer, and what's the gap?"

Operation: `supplier_response`; arguments: `{"operation": "supplier_response", "claim_id": "CLM-5204"}`

**Supplier Response: CLM-5204 (Litware Snacks)**

| Detail | Value |
|---|---|
| Received | Apr 13, 2026 09:00 (43 h, within the 60 h window) |
| Position | Partial acceptance |
| Supplier reason | Supplier says 20 cases shipped before the new price list took effect |
| Claimed | $75.00 (50 units) |
| Credit offered | $45.00 (30 units) |
| Unrecovered gap | $30.00 (20 units) |

**Suggested next step:** ask the supplier for ship dates on the disputed units and compare them with the agreed price list on file (Price list effective Jan 5, 2026). A coordinator decides whether to accept the $45.00 credit or counter for the $30.00 gap.

No credit was accepted or rejected.

Synthetic claims evidence only. This agent does not send a claim, contact a supplier, accept or reject a credit, escalate, or change a case; an authorized claims coordinator reviews every draft.

Source: [Synthetic Fabrikam Grocers Claims Snapshot]
Agents: SupplierClaimEngagementAgent

### SC-07 — Escalation brief draft

Prompt: "Prepare an escalation for the overdue shortage claim CLM-5202."

Operation: `escalation_brief`; arguments: `{"operation": "escalation_brief", "claim_id": "CLM-5202"}`

**Escalation Brief - Draft, Not Sent**

| Field | Value |
|---|---|
| Claim | CLM-5202 - Shortage, P3 - Medium |
| Supplier | Tailspin Freight |
| Claim value | $345.00 |
| Response window | 36 h |
| Elapsed without response | 38 h (Breached by 2 h) |
| Escalate to | Category manager, pantry and beverages |

**Draft:** "CLM-5202 with Tailspin Freight ($345.00) has had no response for 38 hours against a 36-hour window. Please raise it with the supplier's account contact and confirm a response date."

Status: Draft for coordinator approval. No escalation or message was sent.

Synthetic claims evidence only. This agent does not send a claim, contact a supplier, accept or reject a credit, escalate, or change a case; an authorized claims coordinator reviews every draft.

Source: [Synthetic Fabrikam Grocers Claims Snapshot]
Agents: SupplierClaimEngagementAgent

## Locked-case evidence contract

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| SC-01 | Supplier Claims Coordinator | Show me our open supplier claims and what needs attention today. | `claims_queue` | Open claim value; 1,631.80; CLM-5201 |
| SC-02 | Supplier Claims Coordinator | Triage the new damage claim CLM-5201. Who is responsible and what are the terms? | `triage_claim` | P2 - High; Northwind Packaging; 24 hours |
| SC-03 | Receiving Supervisor | Is the evidence for CLM-5201 complete, and what is the claim worth? | `evidence_pack` | Evidence status; RIR-4471; 591.00 |
| SC-04 | Supplier Claims Coordinator | Draft the claim notice to the supplier for CLM-5201, but don't send it. | `draft_supplier_claim` | Draft, Not Sent; Apr 15, 2026 10:00; Nothing was sent |
| SC-05 | Claims Team Lead | Which supplier claims are at risk of missing their response deadline? | `sla_tracker` | Breached by 2 h; CLM-5203; At risk |
| SC-06 | Supplier Claims Coordinator | Litware Snacks replied on CLM-5204. What did they offer, and what's the gap? | `supplier_response` | Partial acceptance; 45.00; Unrecovered gap |
| SC-07 | Claims Team Lead | Prepare an escalation for the overdue shortage claim CLM-5202. | `escalation_brief` | Escalation Brief; 38 h; No escalation or message was sent |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
