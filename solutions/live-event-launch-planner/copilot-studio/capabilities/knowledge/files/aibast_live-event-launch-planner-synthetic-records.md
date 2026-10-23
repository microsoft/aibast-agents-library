# Live Event Launch Planner — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. The game studio and every seasonal event, milestone, plan, task, owner, launch pack, announcement brief, and draft are invented. Never match them to a real organization, person, or live record.

## Complete synthetic records

Every value the agent uses, exactly as bundled in the portable agent source.

### Events

```json
{
 "frostveil-festival": {
  "name": "Frostveil Festival",
  "plan": "PLN-FVF Launch",
  "launch_pack": "SP-FVF-LaunchPack-Approved",
  "launch_day": "In 12 days",
  "missing": "No",
  "milestones": [
   [
    "In 2 days",
    "Launch communications approval"
   ],
   [
    "In 7 days",
    "Readiness review"
   ],
   [
    "In 9 days",
    "Player announcement scheduling"
   ],
   [
    "In 12 days",
    "Launch day"
   ]
  ],
  "latest_update": "Yesterday: Live operations confirmed server-event configuration is on track."
 },
 "emberline-expedition": {
  "name": "Emberline Expedition",
  "plan": "PLN-EE Launch",
  "launch_pack": "SP-EE-LaunchPack-Approved",
  "launch_day": "In 8 days",
  "missing": "No",
  "milestones": [
   [
    "Tomorrow",
    "Final event rewards sign-off"
   ],
   [
    "In 6 days",
    "Readiness review"
   ],
   [
    "In 8 days",
    "Launch day"
   ]
  ],
  "latest_update": "2 days ago: Marketing confirmed key art delivery."
 },
 "moonlit-market": {
  "name": "Moonlit Market",
  "plan": "PLN-MM Launch",
  "launch_pack": "SP-MM-LaunchPack-Draft",
  "launch_day": "In 11 days",
  "missing": "Yes - approved player announcement brief",
  "milestones": [
   [
    "In 3 days",
    "Community moderation coverage confirmation"
   ],
   [
    "In 8 days",
    "Readiness review"
   ],
   [
    "In 11 days",
    "Launch day"
   ]
  ],
  "latest_update": "Yesterday: Community team still needs the approved announcement brief."
 },
 "cindercrest-trials": {
  "name": "Cindercrest Trials",
  "plan": "PLN-CT Launch",
  "launch_pack": "SP-CT-LaunchPack-Approved",
  "launch_day": "In 14 days",
  "missing": "No",
  "milestones": [
   [
    "In 4 days",
    "Localization handoff"
   ],
   [
    "In 9 days",
    "Readiness review"
   ],
   [
    "In 14 days",
    "Launch day"
   ]
  ],
  "latest_update": "Today: All launch dependencies have owners."
 }
}
```

### Tasks

```json
[
 {
  "id": "TSK-101",
  "event": "frostveil-festival",
  "task": "Confirm server-event configuration",
  "team": "Live operations",
  "owner": "Elena Voss",
  "status": "Complete",
  "reminder": "No",
  "source": "Planner"
 },
 {
  "id": "TSK-102",
  "event": "frostveil-festival",
  "task": "Confirm community moderation coverage",
  "team": "Community",
  "owner": "Priya Nair",
  "status": "Blocked",
  "reminder": "Yes",
  "source": "Planner"
 },
 {
  "id": "TSK-103",
  "event": "frostveil-festival",
  "task": "Submit final store assets",
  "team": "Marketing",
  "owner": "Mateo Silva",
  "status": "Late",
  "reminder": "Yes",
  "source": "Planner"
 },
 {
  "id": "TSK-104",
  "event": "frostveil-festival",
  "task": "Review launch communications",
  "team": "Community",
  "owner": "Jon Bell",
  "status": "In progress",
  "reminder": "No",
  "source": "Teams"
 },
 {
  "id": "TSK-201",
  "event": "emberline-expedition",
  "task": "Approve event reward table",
  "team": "Live operations",
  "owner": "Hana Cho",
  "status": "In progress",
  "reminder": "Yes",
  "source": "Planner"
 },
 {
  "id": "TSK-301",
  "event": "moonlit-market",
  "task": "Provide approved player announcement brief",
  "team": "Marketing",
  "owner": "Quinn Harper",
  "status": "Missing",
  "reminder": "Yes",
  "source": "SharePoint"
 },
 {
  "id": "TSK-401",
  "event": "cindercrest-trials",
  "task": "Complete localization handoff",
  "team": "Live operations",
  "owner": "Ravi Mehta",
  "status": "In progress",
  "reminder": "No",
  "source": "Planner"
 },
 {
  "id": "TSK-402",
  "event": "cindercrest-trials",
  "task": "Approve player announcement brief",
  "team": "Marketing",
  "owner": "Quinn Harper",
  "status": "In progress",
  "reminder": "Yes",
  "source": "SharePoint"
 }
]
```

### Announcements

```json
{
 "frostveil-festival": {
  "messaging": "Join the Frostveil Festival from launch day for limited-time quests, rewards, and community challenges.",
  "approval": "Approved",
  "permission": "Not granted - marketing lead sign-off required",
  "brief": "SP-FVF-AnnouncementBrief-Approved",
  "missing": "Publishing sign-off"
 },
 "emberline-expedition": {
  "messaging": "Emberline Expedition arrives on launch day with new expedition rewards and timed objectives.",
  "approval": "Approved",
  "permission": "Granted",
  "brief": "SP-EE-AnnouncementBrief-Approved",
  "missing": "Nothing missing"
 },
 "moonlit-market": {
  "messaging": "Moonlit Market returns with rotating vendor rewards.",
  "approval": "Pending review",
  "permission": "Not granted",
  "brief": "SP-MM-AnnouncementBrief-Draft",
  "missing": "Approved player announcement brief"
 },
 "cindercrest-trials": {
  "messaging": "Cindercrest Trials opens on launch day with competitive trials and seasonal rewards.",
  "approval": "Missing approval",
  "permission": "Not granted",
  "brief": "SP-CT-AnnouncementBrief-Review",
  "missing": "Messaging approval"
 }
}
```

## Exact responses for every locked case

### LEL-01 — Launch timeline

Prompt: "Lay out the Frostveil Festival plan from comms approval to launch day. What comes first?"

Operation: `launch_timeline`; arguments: `{"operation": "launch_timeline", "event": "Frostveil Festival"}`

**Launch Timeline - Frostveil Festival**

**Launch day:** In 12 days | **Plan:** PLN-FVF Launch | **Launch pack:** SP-FVF-LaunchPack-Approved
**First milestone:** Launch communications approval - in 2 days

| When | Milestone |
|------|-----------|
| In 2 days | Launch communications approval |
| In 7 days | Readiness review |
| In 9 days | Player announcement scheduling |
| In 12 days | Launch day |

**Latest team update:** Yesterday: Live operations confirmed server-event configuration is on track.
**Anything missing:** No

> Read-only synthetic snapshot. No announcement was published, no task or event was changed and no reminder was sent; every announcement and reminder is a draft for the event owners to approve.

Source: [Synthetic Seasonal Event Launch Snapshot]
Agents: LiveEventLaunchPlannerAgent

### LEL-02 — Cross-team readiness checklist

Prompt: "Who owns each task across live ops, community and marketing for Frostveil, and where does each one stand?"

Operation: `readiness_checklist`; arguments: `{"operation": "readiness_checklist", "event": "Frostveil Festival"}`

**Readiness Checklist - Frostveil Festival**

**Launch day:** In 12 days | **Tasks complete:** 1 of 4

| Task | Team | Owner | Status | Reminder needed | Source |
|------|------|-------|--------|-----------------|--------|
| TSK-101 Confirm server-event configuration | Live operations | Elena Voss | Complete | No | Planner |
| TSK-102 Confirm community moderation coverage | Community | Priya Nair | Blocked | Yes | Planner |
| TSK-103 Submit final store assets | Marketing | Mateo Silva | Late | Yes | Planner |
| TSK-104 Review launch communications | Community | Jon Bell | In progress | No | Teams |

> Read-only synthetic snapshot. No announcement was published, no task or event was changed and no reminder was sent; every announcement and reminder is a draft for the event owners to approve.

Source: [Synthetic Seasonal Event Launch Snapshot]
Agents: LiveEventLaunchPlannerAgent

### LEL-03 — Player announcement check

Prompt: "Can we post the Frostveil player announcement yet? Show me the copy but hold it."

Operation: `announcement_check`; arguments: `{"operation": "announcement_check", "event": "Frostveil Festival"}`

**Announcement Check - Frostveil Festival**

**Messaging approval:** Approved | **Publish permission:** Not granted - marketing lead sign-off required
**Ready to publish:** No - hold
**Announcement brief:** SP-FVF-AnnouncementBrief-Approved | **Anything missing:** Publishing sign-off

**Draft player announcement**
> Join the Frostveil Festival from launch day for limited-time quests, rewards, and community challenges.

> Draft only: the announcement was not published. Read-only synthetic snapshot. No announcement was published, no task or event was changed and no reminder was sent; every announcement and reminder is a draft for the event owners to approve.

Source: [Synthetic Seasonal Event Launch Snapshot]
Agents: LiveEventLaunchPlannerAgent

### LEL-04 — Launch status summary

Prompt: "What's late or blocked for Frostveil, and who needs a nudge? Don't message anyone yet."

Operation: `launch_summary`; arguments: `{"operation": "launch_summary", "event": "Frostveil Festival"}`

**Launch Summary - Frostveil Festival**

**Launch day:** In 12 days | **Late:** 1 | **Missing:** 0 | **Blocked:** 1
**Announcement:** Approved; publish permission not granted - marketing lead sign-off required

**Needs attention**
| Task | Owner | Status |
|------|-------|--------|
| Confirm community moderation coverage | Priya Nair (Community) | Blocked |
| Submit final store assets | Mateo Silva (Marketing) | Late |

**Draft reminders**
- To Priya Nair: "Confirm community moderation coverage" is blocked for Frostveil Festival; launch day is in 12 days.
- To Mateo Silva: "Submit final store assets" is late for Frostveil Festival; launch day is in 12 days.

> Draft only: no reminder was sent. Read-only synthetic snapshot. No announcement was published, no task or event was changed and no reminder was sent; every announcement and reminder is a draft for the event owners to approve.

Source: [Synthetic Seasonal Event Launch Snapshot]
Agents: LiveEventLaunchPlannerAgent

## Locked-case evidence contract

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| LEL-01 | Live Operations Manager | Lay out the Frostveil Festival plan from comms approval to launch day. What comes first? | `launch_timeline` | Launch Timeline; Launch communications approval; In 12 days |
| LEL-02 | Live Operations Manager | Who owns each task across live ops, community and marketing for Frostveil, and where does each one stand? | `readiness_checklist` | Readiness Checklist; Mateo Silva; 1 of 4 |
| LEL-03 | Community Manager | Can we post the Frostveil player announcement yet? Show me the copy but hold it. | `announcement_check` | Announcement Check; Not granted; marketing lead sign-off required |
| LEL-04 | Marketing Lead | What's late or blocked for Frostveil, and who needs a nudge? Don't message anyone yet. | `launch_summary` | Launch Summary; Submit final store assets; no reminder was sent |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
