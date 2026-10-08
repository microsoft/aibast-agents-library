# Briefing Pack Builder — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. The City of Contoso, its Budget Office briefing team, the Elm Street Bridge Replacement, the Central Library Renovation, documents DOC-01 to DOC-08, change order CO-7 and every figure, date and comment count are fictional. Never match them to a real organization,
> person, product or market, and never treat them as live data.

## Complete synthetic records

## Content set

| Field | Value |
|---|---|
| Organization | City of Contoso (fictional) |
| Team | Budget Office briefing team |
| Indexed | 2026-04-06 |
| Documents | 8 |
| Passages | 10 |
| Topics | elm_street_bridge = Elm Street Bridge Replacement (default); library_renovation = Central Library Renovation |

## Documents

| ID | Title |
|---|---|
| DOC-01 | FY27 Adopted Capital Budget - Transportation |
| DOC-02 | Elm Street Bridge Project Fact Sheet (January) |
| DOC-03 | Quarterly Capital Status Report (Q2 FY27) |
| DOC-04 | Public Works Staffing Workbook |
| DOC-05 | Council Meeting Transcript (February 10) |
| DOC-06 | Community Engagement Summary - Elm Street Bridge |
| DOC-07 | Central Library Renovation Scope Note |
| DOC-08 | Briefing Approval Route Guide |

## Passages (complete)

| Doc | Topic | Sections tagged | Text |
|---|---|---|---|
| DOC-01 | Elm Street Bridge | Summary; Context; Why this brief; Situation; Decision sought | The Elm Street Bridge Replacement replaces the 1962 two-lane bridge with a four-lane structure and a shared path. |
| DOC-01 | Elm Street Bridge | Key figures; Budget status; Cost picture; Facts to cite | Approved budget $48.6 million; $19.2 million expended to date; completion forecast Q3 FY28. |
| DOC-02 | Elm Street Bridge | Key figures; Progress; Where things stand | Approved budget $48.6 million. Foundations complete; deck works 40 percent complete. |
| DOC-03 | Elm Street Bridge | Budget status; Cost change explanation; Recent changes; Cost picture; Issues to weigh; Follow-up lines | Revised approved budget $51.3 million after change order CO-7; $21.7 million expended to date. The $2.7 million increase reflects steel price escalation and utility relocation. |
| DOC-03 | Elm Street Bridge | Risks; Issues to weigh; Follow-up lines | Utility relocation is two months behind schedule; the Q3 FY28 completion date is at risk if it slips further. |
| DOC-04 | Elm Street Bridge | Staffing | Project team establishment 16 FTE; 14 FTE filled after 2 engineer vacancies in December. |
| DOC-05 | Elm Street Bridge | Likely questions; Likely question | Council members asked how long the Elm Street detour will last and whether the project will exceed its budget. |
| DOC-06 | Elm Street Bridge | Public and press interest; Risks | 312 public comments received; detour length was the top concern, raised in 141 comments. |
| DOC-07 | Central Library | Summary; Context; Why this brief; Situation; Decision sought | The Central Library Renovation refurbishes the 1978 building and adds a children's learning floor. |
| DOC-07 | Central Library | Key figures; Budget status; Cost picture; Facts to cite | Approved budget $12.4 million; design phase complete; construction tender planned for July. |

Elm Street Bridge Replacement: 8 passages on topic across 6 documents (DOC-01 2, DOC-02 1, DOC-03 2, DOC-04 1, DOC-05 1, DOC-06 1).

## Figure register

| Topic | Measure | Values (documents) | Status |
|---|---|---|---|
| Elm Street Bridge | Approved budget | $48.6 million (DOC-01, DOC-02); $51.3 million (DOC-03) | Conflict - confirm before use |
| Elm Street Bridge | Expended to date | $19.2 million (DOC-01); $21.7 million (DOC-03) | Conflict - confirm before use |
| Elm Street Bridge | Completion forecast | Q3 FY28 (DOC-01, DOC-03) | Consistent |
| Central Library | Approved budget | $12.4 million (DOC-07) | Consistent |

## Briefing templates and approval routes

| Key | Format | Audience | Sections | Reviewer | Approver | Working days |
|---|---|---|---|---|---|---|
| budget_hearing | Budget Hearing Brief | Mayor and council members, for the annual budget hearing | Summary; Key figures; Budget status; Cost change explanation; Staffing; Talking points; Likely questions; Risks | Deputy City Manager | City Manager | 8 |
| council_question | Council Question Brief | Mayor, for a council question session | Likely question; Proposed answer; Facts to cite; Follow-up lines | Department Director | Mayor's Office | 2 |
| rapid_response | Rapid Response Brief | Mayor and City Manager | Situation; Where things stand; Recent changes; Public and press interest; Suggested lines | City Manager | Mayor's Office | 1 |
| executive | Executive Brief | City Manager | Why this brief; Context; Progress; Cost picture; Recommended action | Deputy City Manager | City Manager | 4 |
| decision_memo | Council Decision Memo | City Council | Decision sought; Context; Issues to weigh; Cost picture; Recommended action; Sign-off | City Manager | City Council | 6 |

Budget Hearing Brief on the Elm Street Bridge Replacement: 7 sections covered, 1 gap (Talking points); "1 of 8 sections need input"; missing content is requested from Communications and the project director. Gap text: "Not covered by the content set - input needed from the owning department."

## Locked-case evidence contract

Each locked case below calls exactly one operation. The agent output must contain every listed evidence string.

| Case | Persona | Operation | Prompt | Must include |
|---|---|---|---|---|
| BPB-01 | Briefing Coordinator | list_templates | What briefing formats can you build for us? | Budget Hearing Brief; Council Question Brief; 8 documents indexed |
| BPB-02 | Budget Analyst | content_scan | What do we hold on the Elm Street Bridge Replacement? | 8 passages on topic; Quarterly Capital Status Report; Measures with conflicting values |
| BPB-03 | Budget Analyst | figure_check | Before I draft anything, do any of the figures disagree? | $51.3 million; Conflict - confirm before use; does not choose between them |
| BPB-04 | Briefing Coordinator | draft_brief | Draft the budget hearing brief on the Elm Street bridge. | DRAFT - not approved; Figures needing confirmation; Talking points |
| BPB-05 | Briefing Coordinator | gap_report | Which sections of that brief still need input? | 1 of 8 sections need input; Gap - needs input; Communications and the project director |
| BPB-06 | Department Director | approval_route | Who signs this brief off, and how long does it take? | Deputy City Manager; 8 working days; No brief was sent for approval |

## Reference outputs (exact agent output for each locked case)

### BPB-01 — Briefing formats (`{"operation": "list_templates"}`)

````markdown
**Briefing Templates: City of Contoso Budget Office briefing team**

| Key | Format | Audience | Sections |
|---|---|---|---|
| budget_hearing | Budget Hearing Brief | Mayor and council members, for the annual budget hearing | 8: Summary, Key figures, Budget status, Cost change explanation, Staffing, Talking points, Likely questions, Risks |
| council_question | Council Question Brief | Mayor, for a council question session | 4: Likely question, Proposed answer, Facts to cite, Follow-up lines |
| rapid_response | Rapid Response Brief | Mayor and City Manager | 5: Situation, Where things stand, Recent changes, Public and press interest, Suggested lines |
| executive | Executive Brief | City Manager | 5: Why this brief, Context, Progress, Cost picture, Recommended action |
| decision_memo | Council Decision Memo | City Council | 6: Decision sought, Context, Issues to weigh, Cost picture, Recommended action, Sign-off |

Each format is a template entry, so adding a format needs no code change. Content set: 8 documents indexed 2026-04-06.

**Next step:** name a topic and I will show what the content set holds on it.

Synthetic content set only. This agent drafts; it does not approve, file, send or publish a brief. Responsible officers verify every figure and route the brief for sign-off.

Source: [Synthetic Briefing Content Set, indexed 2026-04-06]
Agents: BriefingPackBuilderAgent
````

### BPB-02 — Content scan (`{"operation": "content_scan", "topic": "elm_street_bridge"}`)

````markdown
**Content Scan: Elm Street Bridge Replacement**

Searched 8 indexed documents (10 passages); 8 passages on topic across 6 documents.

| Document | Title | Passages on topic |
|---|---|---|
| DOC-01 | FY27 Adopted Capital Budget - Transportation | 2 |
| DOC-02 | Elm Street Bridge Project Fact Sheet (January) | 1 |
| DOC-03 | Quarterly Capital Status Report (Q2 FY27) | 2 |
| DOC-04 | Public Works Staffing Workbook | 1 |
| DOC-05 | Council Meeting Transcript (February 10) | 1 |
| DOC-06 | Community Engagement Summary - Elm Street Bridge | 1 |

**Measures with conflicting values:** 2. Run a figure check before drafting.

Synthetic content set only. This agent drafts; it does not approve, file, send or publish a brief. Responsible officers verify every figure and route the brief for sign-off.

Source: [Synthetic Briefing Content Set, indexed 2026-04-06]
Agents: BriefingPackBuilderAgent
````

### BPB-03 — Figure check (`{"operation": "figure_check", "topic": "elm_street_bridge"}`)

````markdown
**Figure Check: Elm Street Bridge Replacement**

| Measure | Values found (documents) | Status |
|---|---|---|
| Approved budget | $48.6 million (DOC-01, DOC-02); $51.3 million (DOC-03) | Conflict - confirm before use |
| Expended to date | $19.2 million (DOC-01); $21.7 million (DOC-03) | Conflict - confirm before use |
| Completion forecast | Q3 FY28 (DOC-01, DOC-03) | Consistent |

2 conflicting measures.

**Figures needing confirmation:** the content set carries two values for these measures. The later status report reflects change order CO-7, but the brief owner must confirm which is current; this agent does not choose between them.

Synthetic content set only. This agent drafts; it does not approve, file, send or publish a brief. Responsible officers verify every figure and route the brief for sign-off.

Source: [Synthetic Briefing Content Set, indexed 2026-04-06]
Agents: BriefingPackBuilderAgent
````

### BPB-04 — Cited draft brief (`{"operation": "draft_brief", "template": "budget_hearing", "topic": "elm_street_bridge"}`)

````markdown
**Budget Hearing Brief - Elm Street Bridge Replacement** (DRAFT - not approved)

Audience: Mayor and council members, for the annual budget hearing. Drafted from 8 indexed documents (8 passages on topic).

### Summary
The Elm Street Bridge Replacement replaces the 1962 two-lane bridge with a four-lane structure and a shared path. [DOC-01]

### Key figures
Approved budget $48.6 million; $19.2 million expended to date; completion forecast Q3 FY28. [DOC-01] Approved budget $48.6 million. Foundations complete; deck works 40 percent complete. [DOC-02]

### Budget status
Approved budget $48.6 million; $19.2 million expended to date; completion forecast Q3 FY28. [DOC-01] Revised approved budget $51.3 million after change order CO-7; $21.7 million expended to date. The $2.7 million increase reflects steel price escalation and utility relocation. [DOC-03]

### Cost change explanation
Revised approved budget $51.3 million after change order CO-7; $21.7 million expended to date. The $2.7 million increase reflects steel price escalation and utility relocation. [DOC-03]

### Staffing
Project team establishment 16 FTE; 14 FTE filled after 2 engineer vacancies in December. [DOC-04]

### Talking points
Not covered by the content set - input needed from the owning department.

### Likely questions
Council members asked how long the Elm Street detour will last and whether the project will exceed its budget. [DOC-05]

### Risks
Utility relocation is two months behind schedule; the Q3 FY28 completion date is at risk if it slips further. [DOC-03] 312 public comments received; detour length was the top concern, raised in 141 comments. [DOC-06]

### Figures needing confirmation
- Approved budget: $48.6 million (DOC-01, DOC-02) vs $51.3 million (DOC-03)
- Expended to date: $19.2 million (DOC-01) vs $21.7 million (DOC-03)

**Sources:** DOC-01 FY27 Adopted Capital Budget - Transportation; DOC-02 Elm Street Bridge Project Fact Sheet (January); DOC-03 Quarterly Capital Status Report (Q2 FY27); DOC-04 Public Works Staffing Workbook; DOC-05 Council Meeting Transcript (February 10); DOC-06 Community Engagement Summary - Elm Street Bridge

**Gaps:** 1 (Talking points).
**Approval route:** Deputy City Manager reviews, City Manager approves, 8 working days.

Status: Draft for officer review - not approved, filed or sent.

Synthetic content set only. This agent drafts; it does not approve, file, send or publish a brief. Responsible officers verify every figure and route the brief for sign-off.

Source: [Synthetic Briefing Content Set, indexed 2026-04-06]
Agents: BriefingPackBuilderAgent
````

### BPB-05 — Gap report (`{"operation": "gap_report", "template": "budget_hearing", "topic": "elm_street_bridge"}`)

````markdown
**Gap Report: Budget Hearing Brief - Elm Street Bridge Replacement**

| Section | Cited passages | Status |
|---|---|---|
| Summary | 1 | Covered |
| Key figures | 2 | Covered |
| Budget status | 2 | Covered |
| Cost change explanation | 1 | Covered |
| Staffing | 1 | Covered |
| Talking points | 0 | Gap - needs input |
| Likely questions | 1 | Covered |
| Risks | 2 | Covered |

**1 of 8 sections need input.** Gap sections are left as "Not covered by the content set - input needed from the owning department." and are never filled from general knowledge.

**Next step:** request the missing content from Communications and the project director before the brief goes for review.

Synthetic content set only. This agent drafts; it does not approve, file, send or publish a brief. Responsible officers verify every figure and route the brief for sign-off.

Source: [Synthetic Briefing Content Set, indexed 2026-04-06]
Agents: BriefingPackBuilderAgent
````

### BPB-06 — Approval route (`{"operation": "approval_route", "template": "budget_hearing"}`)

````markdown
**Approval Route: Budget Hearing Brief**

| Step | Owner |
|---|---|
| 1. Draft and cite | Budget Office briefing team (this agent prepares the draft) |
| 2. Verify figures and fill gaps | Owning department |
| 3. Review | Deputy City Manager |
| 4. Approve | City Manager |

**Turnaround:** 8 working days from a complete draft.

| Format | Reviewer | Approver | Working days |
|---|---|---|---|
| Budget Hearing Brief | Deputy City Manager | City Manager | 8 |
| Council Question Brief | Department Director | Mayor's Office | 2 |
| Rapid Response Brief | City Manager | Mayor's Office | 1 |
| Executive Brief | Deputy City Manager | City Manager | 4 |
| Council Decision Memo | City Manager | City Council | 6 |

Sign-off stays with people: the agent never marks a draft as approved, and the briefing log stays the record of status. No brief was sent for approval.

Synthetic content set only. This agent drafts; it does not approve, file, send or publish a brief. Responsible officers verify every figure and route the brief for sign-off.

Source: [Synthetic Briefing Content Set, indexed 2026-04-06]
Agents: BriefingPackBuilderAgent
````
