# Generate Demo Skill

Generate realistic static demo endpoints for simulating APIs like CRM, support tickets, etc.

## Usage

```
/generate-demo <scenario> [description]
```

**Examples:**
```
/generate-demo crm
/generate-demo crm "enterprise software sales with 5 active deals"
/generate-demo support "IT helpdesk with mixed priority tickets"
/generate-demo inventory "warehouse with low stock alerts"
```

## Supported Scenarios

| Scenario | Description |
|----------|-------------|
| `crm` | Sales CRM with deals, contacts, pipeline stages |
| `support` | Help desk with tickets, priorities, agents |
| `inventory` | Product inventory with stock levels |
| `calendar` | Meeting scheduler with appointments |
| `custom` | Describe your own scenario |

## Execution

### Step 1: Parse Input

```
scenario = first argument (crm, support, inventory, calendar, custom)
description = remaining text (optional context for generation)
```

### Step 2: Generate Demo Data

Based on scenario type, generate realistic JSON data:

**CRM Schema:**
```json
{
  "assistant_response": "## Your Sales Pipeline\n\n| Deal | Company | Value | Stage | Close Date |\n|------|---------|-------|-------|------------|\n...",
  "voice_response": "You have X active deals worth $Y total.",
  "agent_logs": "[Demo Mode] CRM Agent - Retrieved pipeline data",
  "user_guid": "demo-user-crm",
  "mode": "demo",
  "data": {
    "deals": [
      {
        "id": "deal_001",
        "name": "Enterprise License",
        "company": "Acme Corp",
        "value": 50000,
        "stage": "negotiation",
        "probability": 75,
        "close_date": "2025-02-15",
        "contact": "Jane Smith",
        "notes": "Final pricing review scheduled"
      }
    ],
    "summary": {
      "total_deals": 5,
      "total_value": 185000,
      "weighted_value": 125000,
      "stages": {
        "prospecting": 1,
        "qualification": 1,
        "proposal": 1,
        "negotiation": 2
      }
    }
  }
}
```

**Support Schema:**
```json
{
  "assistant_response": "## Open Tickets\n\n| ID | Subject | Priority | Status | Assigned |\n|----|---------|----------|--------|----------|\n...",
  "voice_response": "You have X open tickets, Y are high priority.",
  "agent_logs": "[Demo Mode] Support Agent - Retrieved ticket queue",
  "user_guid": "demo-user-support",
  "mode": "demo",
  "data": {
    "tickets": [
      {
        "id": "TKT-1234",
        "subject": "Login issue after password reset",
        "priority": "high",
        "status": "open",
        "created": "2025-01-30T10:30:00Z",
        "customer": "john.doe@company.com",
        "assigned_to": "Agent Sarah",
        "category": "authentication"
      }
    ],
    "summary": {
      "total_open": 12,
      "high_priority": 3,
      "avg_response_time": "2.5 hours"
    }
  }
}
```

**Inventory Schema:**
```json
{
  "assistant_response": "## Inventory Status\n\n| SKU | Product | Stock | Status | Reorder |\n|-----|---------|-------|--------|----------|\n...",
  "voice_response": "X items are low on stock and need reordering.",
  "agent_logs": "[Demo Mode] Inventory Agent - Retrieved stock levels",
  "user_guid": "demo-user-inventory",
  "mode": "demo",
  "data": {
    "products": [
      {
        "sku": "WIDGET-001",
        "name": "Premium Widget",
        "stock": 15,
        "min_stock": 50,
        "status": "low",
        "reorder_qty": 100,
        "supplier": "WidgetCo",
        "last_restock": "2025-01-15"
      }
    ],
    "summary": {
      "total_products": 150,
      "low_stock": 8,
      "out_of_stock": 2
    }
  }
}
```

### Step 3: Create Response Files

Generate multiple response files for the scenario:

```
api-demo/scenarios/<scenario>/
├── overview.json      # Dashboard/summary view
├── list.json          # List all items
├── detail.json        # Single item detail
├── create.json        # Response after creating item
├── update.json        # Response after updating item
└── search.json        # Search results
```

### Step 4: Update Active Scenario

Create/update the main endpoint that apps fetch:

```bash
# Copy overview as the default response
cp api-demo/scenarios/<scenario>/overview.json api-demo/responses/<scenario>.json
```

### Step 5: Commit and Push

```bash
cd /Users/kodywildfeuer/Documents/GitHub/CommunityRAPP
git add api-demo/
git commit -m "Generate: <scenario> demo data - <description>"
git push origin main
```

### Step 6: Output Results

```
✅ Demo scenario generated: <scenario>

📁 Files created:
- api-demo/scenarios/<scenario>/overview.json
- api-demo/scenarios/<scenario>/list.json
- api-demo/scenarios/<scenario>/detail.json
- api-demo/responses/<scenario>.json

🔗 Test endpoints:
- Overview: https://raw.githubusercontent.com/kody-w/CommunityRAPP/main/api-demo/responses/<scenario>.json
- List: https://raw.githubusercontent.com/kody-w/CommunityRAPP/main/api-demo/scenarios/<scenario>/list.json

💡 Use in your app:
fetch('https://raw.githubusercontent.com/kody-w/CommunityRAPP/main/api-demo/responses/<scenario>.json')
```

## Tips

- Generated data uses realistic names, dates, and values
- Each run creates fresh data (previous scenario preserved in scenarios/)
- Use description to customize: `/generate-demo crm "struggling startup with 2 deals"`
- Chain scenarios: generate CRM, then support for same "company"

## Triggering from Apps

Apps can simulate different states by fetching different scenario files:

```javascript
// Fetch based on user action
const scenario = userAction === 'view_pipeline' ? 'overview' : 'list';
const url = `https://raw.githubusercontent.com/kody-w/CommunityRAPP/main/api-demo/scenarios/crm/${scenario}.json`;
const response = await fetch(url);
```
