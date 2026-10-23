# Campaign Delivery Optimizer — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. The media company and every advertiser campaign, reach figure, placement, inventory record, sales lead, and recommendation draft are invented. Never match them to a real organization, person, or live record.

## Complete synthetic records

Every value the agent uses, exactly as bundled in the portable agent source.

### Campaigns

```json
{
 "harborlight": {
  "name": "Harborlight Streaming Campaign",
  "id": "CMP-2041",
  "sales_lead": "Maya Chen",
  "planned_weekly_reach": "235,000",
  "delivered_reach": "192,700",
  "variance": "18% below plan",
  "at_risk": "Yes",
  "delivery_status": "At risk",
  "missing": "No",
  "reason": "Delivered reach is 18% below planned weekly reach as of this week's delivery read."
 },
 "northfield": {
  "name": "Northfield Culture Campaign",
  "id": "CMP-2038",
  "sales_lead": "Jon Bell",
  "planned_weekly_reach": "120,000",
  "delivered_reach": "124,800",
  "variance": "4% above plan",
  "at_risk": "No",
  "delivery_status": "On track",
  "missing": "No",
  "reason": "Delivered reach is tracking 4% above planned weekly reach as of this week's delivery read."
 },
 "cedar-view": {
  "name": "Cedar View Campaign",
  "id": "CMP-2045",
  "sales_lead": "Priya Nair",
  "planned_weekly_reach": "80,000",
  "delivered_reach": "Incomplete",
  "variance": "Cannot be compared",
  "at_risk": "Yes",
  "delivery_status": "Pending review",
  "missing": "Yes - current-week delivery data",
  "reason": "Delivery data for the current week is incomplete; planned weekly reach cannot be fully compared."
 },
 "ridgeway-audio": {
  "name": "Ridgeway Audio Campaign",
  "id": "CMP-2033",
  "sales_lead": "Elena Ruiz",
  "planned_weekly_reach": "150,000",
  "delivered_reach": "147,000",
  "variance": "2% below plan",
  "at_risk": "No",
  "delivery_status": "On track",
  "missing": "No",
  "reason": "Delivered reach is within 2% of planned weekly reach as of this week's delivery read."
 }
}
```

### Placements

```json
[
 {
  "id": "INV-501",
  "campaign": "harborlight",
  "placement": "Streaming Home Screen Takeover",
  "extra_reach": "42,000",
  "status": "Available"
 },
 {
  "id": "INV-502",
  "campaign": "harborlight",
  "placement": "Weekend Premium Video Pre-roll",
  "extra_reach": "0",
  "status": "Sold out"
 },
 {
  "id": "INV-511",
  "campaign": "northfield",
  "placement": "Culture Newsletter Sponsorship",
  "extra_reach": "15,500",
  "status": "Available"
 },
 {
  "id": "INV-520",
  "campaign": "cedar-view",
  "placement": "Local News Mid-roll",
  "extra_reach": "8,200",
  "status": "Pending confirmation"
 },
 {
  "id": "INV-531",
  "campaign": "ridgeway-audio",
  "placement": "Podcast Network Host-read",
  "extra_reach": "27,000",
  "status": "Available"
 }
]
```

### Recommendations

```json
{
 "harborlight": {
  "draft": "Propose Streaming Home Screen Takeover for an estimated 42,000 additional reach this week to address the 18% weekly reach gap.",
  "approval_status": "Pending sales lead approval",
  "missing": "Nothing missing"
 },
 "northfield": {
  "draft": "No additional reach recommendation is needed because delivery is on track.",
  "approval_status": "Approved",
  "missing": "Nothing missing"
 },
 "cedar-view": {
  "draft": "Recommendation cannot be finalized until current-week delivery data is provided.",
  "approval_status": "Blocked - missing delivery data",
  "missing": "Current-week delivery data"
 },
 "ridgeway-audio": {
  "draft": "Keep the current placement mix because delivery is within the planned weekly range.",
  "approval_status": "Pending sales lead approval",
  "missing": "Nothing missing"
 }
}
```

## Exact responses for every locked case

### CDO-01 — Campaign risk check

Prompt: "Is the Harborlight Streaming campaign falling behind this week, and by how much?"

Operation: `campaign_risk`; arguments: `{"operation": "campaign_risk", "campaign": "Harborlight Streaming Campaign"}`

**Campaign Risk - Harborlight Streaming Campaign**

**Campaign:** CMP-2041 | **Sales lead:** Maya Chen | **Delivery status:** At risk | **At risk this week:** Yes

| Planned weekly reach | Delivered reach | Variance |
|----------------------|-----------------|----------|
| 235,000 | 192,700 | 18% below plan |

**Why:** Delivered reach is 18% below planned weekly reach as of this week's delivery read.
**Anything missing:** No
**Across all 4 active campaigns:** 2 at risk this week.

> Read-only synthetic snapshot. No inventory was booked, no campaign or placement was changed and nothing was shared with an advertiser; every recommendation is a draft for the sales lead to approve.

Source: [Synthetic Campaign Delivery Snapshot]
Agents: CampaignDeliveryOptimizerAgent

### CDO-02 — Available reach

Prompt: "Where can we find extra reach this week to close the Harborlight gap?"

Operation: `available_reach`; arguments: `{"operation": "available_reach", "campaign": "Harborlight Streaming Campaign"}`

**Available Reach - Harborlight Streaming Campaign**

**Delivery gap:** 18% below plan | **Delivery status:** At risk

| Inventory | Placement | Extra reach this week | Inventory status |
|-----------|-----------|-----------------------|------------------|
| INV-501 | Streaming Home Screen Takeover | 42,000 | Available |
| INV-502 | Weekend Premium Video Pre-roll | 0 | Sold out |

> Read-only synthetic snapshot. No inventory was booked, no campaign or placement was changed and nothing was shared with an advertiser; every recommendation is a draft for the sales lead to approve.

Source: [Synthetic Campaign Delivery Snapshot]
Agents: CampaignDeliveryOptimizerAgent

### CDO-03 — Recommendation draft for approval

Prompt: "Draft the make-good for Harborlight so Maya can review it. Don't send anything to the advertiser yet."

Operation: `approval_recommendation`; arguments: `{"operation": "approval_recommendation", "campaign": "Harborlight Streaming Campaign"}`

**Approval Recommendation - Harborlight Streaming Campaign**

**Sales lead:** Maya Chen | **Approval status:** Pending sales lead approval
**Anything missing:** Nothing missing

**Draft recommendation**
- Propose Streaming Home Screen Takeover for an estimated 42,000 additional reach this week to address the 18% weekly reach gap.
- Basis: Delivered reach is 18% below planned weekly reach as of this week's delivery read.

> Draft only: nothing was booked or shared with the advertiser. Read-only synthetic snapshot. No inventory was booked, no campaign or placement was changed and nothing was shared with an advertiser; every recommendation is a draft for the sales lead to approve.

Source: [Synthetic Campaign Delivery Snapshot]
Agents: CampaignDeliveryOptimizerAgent

## Locked-case evidence contract

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| CDO-01 | Ad Operations Manager | Is the Harborlight Streaming campaign falling behind this week, and by how much? | `campaign_risk` | Campaign Risk; 18% below plan; 235,000 |
| CDO-02 | Campaign Manager | Where can we find extra reach this week to close the Harborlight gap? | `available_reach` | Available Reach; Streaming Home Screen Takeover; 42,000 |
| CDO-03 | Ad Sales Lead | Draft the make-good for Harborlight so Maya can review it. Don't send anything to the advertiser yet. | `approval_recommendation` | Approval Recommendation; Pending sales lead approval; Draft only |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
