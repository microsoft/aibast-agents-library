"""
Ask HR Agent

AI-powered HR assistant for employee self-service: time-off requests,
benefits inquiries, parental leave guidance, and policy lookups.

Where a real deployment would call Workday, Benefits Portal, or HR systems,
this agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/ask-hr",
    "version": "1.0.0",
    "display_name": "Ask HR Agent",
    "description": "Provide self-service HR inquiry handling that transforms the process from a manual ticket-based system to intelligent, automated resolutions.",
    "author": "AIBAST",
    "tags": ["hr", "human-resources", "benefits", "time-off", "employee-self-service"],
    "category": "human_resources",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_EMPLOYEES = {
    "jordan": {
        "id": "emp-1001", "name": "Jordan Chen", "title": "Senior Product Manager",
        "department": "Product", "manager": "Sarah Johnson", "tenure_years": 3.5,
        "email": "jordan.chen@contoso.com",
        "leave_balance": {
            "vacation": 15.5, "sick": 8.0, "personal": 3.0,
            "accrual_rate": 1.25,
        },
        "health_plan": {
            "plan": "PPO Family Plan", "monthly_premium": 450,
            "deductible_individual": 500, "deductible_family": 1500,
            "oop_max_individual": 3000, "oop_max_family": 6000,
            "dependents": ["Spouse"],
        },
    },
    "michael": {
        "id": "emp-1002", "name": "Michael Torres", "title": "Account Executive",
        "department": "Sales", "manager": "David Kim", "tenure_years": 1.2,
        "email": "michael.torres@contoso.com",
        "leave_balance": {
            "vacation": 10.0, "sick": 6.0, "personal": 2.0,
            "accrual_rate": 1.0,
        },
        "health_plan": {
            "plan": "HMO Individual", "monthly_premium": 220,
            "deductible_individual": 750, "deductible_family": None,
            "oop_max_individual": 4000, "oop_max_family": None,
            "dependents": [],
        },
    },
    "sarah": {
        "id": "emp-1003", "name": "Sarah Chen", "title": "Software Engineer",
        "department": "Engineering", "manager": "David Kim", "tenure_years": 2.7,
        "start_date": "March 2022", "benefits_tier": "Employee + Family",
        "email": "sarah.chen@contoso.com",
        "leave_balance": {
            "vacation": 14.0, "sick": 8.0, "personal": 2.0,
            "accrual_rate": 1.25,
        },
        "health_plan": {
            "plan": "PPO Gold", "monthly_premium": 485,
            "deductible_individual": 500, "deductible_family": 1000,
            "oop_max_individual": 3000, "oop_max_family": 6000,
            "primary_care_copay": 25,
            "dependents": ["Spouse", "Child"],
        },
        "dental_premium": 42, "vision_premium": 12,
        "retirement": {"plan": "401(k)", "contribution_pct": 8, "match_pct": 4},
    },
}

_COMPANY_HOLIDAYS = [
    {"name": "Memorial Day", "date": "May 26"},
    {"name": "Independence Day", "date": "Jul 4"},
    {"name": "Labor Day", "date": "Sep 1"},
    {"name": "Thanksgiving", "date": "Nov 27-28"},
    {"name": "Christmas Day", "date": "Dec 25"},
    {"name": "New Year's Day", "date": "Jan 1"},
]

_POLICIES = {
    "time_off": {
        "min_notice_5plus_days": "2 weeks",
        "holiday_period": "No blackout dates; year-end requests follow the standard manager approval",
        "rollover_max": 5,
        "approval_window": "1-2 business days",
        "auto_approve_hours": 48,
        "accrual_reset": "January 1",
        "open_enrollment": "November 1-15",
    },
    "parental_leave": {
        "paternity_weeks": 8, "maternity_weeks": 16,
        "min_tenure_years": 1, "stipend": 2000,
        "backup_childcare_months": 6,
    },
    "remote_work": {
        "standard_days_per_week": 3,
        "new_parent_bonus_days": 2,
        "new_parent_bonus_months": 6,
        "core_hours": "10 AM - 3 PM local",
        "equipment_stipend": 1000,
        "internet_reimbursement": 50,
    },
    "health_insurance": {
        "enrollment_window_days": 30,
        "dependent_premium_increase": 125,
        "well_baby_covered": True,
        "pediatric_copay": 20,
        "dependent_life_insurance": 10000,
    },
    "dependents": {
        "eligible": [
            ("Spouse / domestic partner", "Eligible"),
            ("Children under 26", "Eligible"),
            ("Parents", "Not typically eligible"),
        ],
        "parent_rule": (
            "Parents are covered only when they are your legal tax dependents "
            "(you provide more than 50% of their support)."
        ),
        "alternatives": [
            "Medicare (age 65+)",
            "Healthcare.gov marketplace plan",
            "COBRA continuation from a former employer plan",
        ],
        "reference": "Employee Handbook Section 4.2",
    },
}

# Fixed demo calendar: dates without a year are read in the synthetic 2024 plan year.
_DEMO_YEAR = 2024
_HOLIDAY_DATES = {(12, 25): "Christmas Day", (1, 1): "New Year's Day",
                  (7, 4): "Independence Day", (5, 26): "Memorial Day",
                  (9, 1): "Labor Day", (11, 27): "Thanksgiving", (11, 28): "Thanksgiving"}
_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

_HR_GATE = (
    "Synthetic policy guidance only. This agent does not determine eligibility, "
    "infer sensitive employee circumstances, submit a transaction, notify a "
    "manager, or make an HR decision."
)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_employee(query):
    """Profile key, full name or a unique name part; None when no profile matches (never another person)."""
    if not query:
        return "sarah"
    q = query.lower().strip()
    for key in _EMPLOYEES:
        if key in q or q in _EMPLOYEES[key]["name"].lower():
            return key
    return None


def _parse_date(text, default_year=_DEMO_YEAR):
    """'December 18', 'Dec 18, 2024' or '2024-12-18' -> datetime.date (None if unreadable)."""
    import datetime, re
    if not text:
        return None
    t = str(text).strip()
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", t)
    if m:
        return datetime.date(int(m[1]), int(m[2]), int(m[3]))
    m = re.match(r"^([A-Za-z]{3,})\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?$", t)
    if m and m[1][:3].lower() in _MONTHS:
        return datetime.date(int(m[3] or default_year), _MONTHS[m[1][:3].lower()], int(m[2]))
    return None


def _business_days(start, end):
    """Weekdays from start to end inclusive, skipping company holidays; also the return-to-work date."""
    import datetime
    days, holidays_in_range, d = 0, [], start
    while d <= end:
        name = _HOLIDAY_DATES.get((d.month, d.day))
        if d.weekday() < 5 and name:
            holidays_in_range.append(f"{name} ({d:%b} {d.day})")
        elif d.weekday() < 5:
            days += 1
        d += datetime.timedelta(days=1)
    back, skipped = end + datetime.timedelta(days=1), []
    while back.weekday() >= 5 or (back.month, back.day) in _HOLIDAY_DATES:
        if (back.month, back.day) in _HOLIDAY_DATES:
            skipped.append(f"{_HOLIDAY_DATES[(back.month, back.day)]} ({back:%b} {back.day})")
        back += datetime.timedelta(days=1)
    return days, back, holidays_in_range + skipped


def _submit_time_off(emp_key, start_date, end_date, days):
    """Deterministic draft: business days and return date computed from the dates when they parse."""
    emp = _EMPLOYEES[emp_key]
    start, end = _parse_date(start_date), _parse_date(end_date)
    if start and end and end >= start:
        days, back, holidays = _business_days(start, end)
        dates = f"{start:%b} {start.day} - {end:%b} {end.day}, {end.year}"
        year = start.year
    else:
        back, holidays, dates, year = None, [], f"{start_date} to {end_date}", _DEMO_YEAR
    remaining = emp["leave_balance"]["vacation"] - days
    return {
        "employee": emp["name"], "dates": dates, "days": days,
        "return": f"{back:%a %b} {back.day}" if back else "Confirm with HR",
        "holidays": holidays, "status": "Draft for employee review",
        "manager": emp["manager"], "balance_before": emp["leave_balance"]["vacation"],
        "balance_after": remaining, "request_id": f"PTO-{year}-8934",
    }


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = [
    "leave_balance", "submit_time_off", "parental_leave", "health_insurance",
    "remote_work", "benefits_summary", "time_off_check", "reminders",
]


class AskHRAgent(BasicAgent):
    """
    Employee self-service HR assistant.

    Operations:
        leave_balance     - check vacation, sick, personal day balances
        submit_time_off   - draft a time-off request for given dates (never submitted)
        parental_leave    - parental leave eligibility and benefits
        health_insurance  - health plan details and dependent eligibility
        remote_work       - remote work policy and new-parent flexibility
        benefits_summary  - profile, current benefits and leave balances
        time_off_check    - policy pre-check for a planned number of days off
        reminders         - open enrollment, accrual reset and carryover reminders
    """

    def __init__(self):
        self.name = "AskHRAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} Always use this tool for fictional "
                "leave balances, vacation or time-off previews, parental-leave "
                "guidance, health-plan and dependent questions, remote-work policy, "
                "benefits summaries, time-off policy checks, and HR reminders. The "
                "demo employee is Sarah Chen. When someone says they want N days off "
                "but gives no dates yet, call time_off_check right away (it needs no "
                "dates) instead of asking for dates. A request to preview or submit vacation "
                "dates, or to avoid submitting anything, must use submit_time_off; "
                "that operation returns a deterministic Not Submitted draft and sends "
                "no notification. Use fictional profiles and published policy "
                "examples only. Never infer a sensitive employee circumstance, "
                "decide eligibility, submit a transaction, or make an HR decision."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "benefits_summary for 'my benefits options' or an overall "
                            "package; health_insurance for plan details or adding "
                            "dependents (e.g. parents); time_off_check whenever someone "
                            "says they want to take N days off (even with no dates yet); "
                            "submit_time_off for "
                            "specific dates to preview or submit, including 'do not "
                            "submit' wording; reminders for 'anything else I should "
                            "know'; leave_balance for balances and notice rules; "
                            "parental_leave and remote_work for those policies."
                        ),
                    },
                    "employee_name": {
                        "type": "string",
                        "description": "Employee name (default 'Sarah Chen')",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Requested start date, e.g. 'December 18'",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Requested end date, e.g. 'December 24'",
                    },
                    "days": {
                        "type": "number",
                        "description": "Requested vacation days (time_off_check, or when no dates are given)",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "benefits_summary")
        dispatch = {
            "leave_balance": self._leave_balance,
            "submit_time_off": self._submit_time_off,
            "parental_leave": self._parental_leave,
            "health_insurance": self._health_insurance,
            "remote_work": self._remote_work,
            "benefits_summary": self._benefits_summary,
            "time_off_check": self._time_off_check,
            "reminders": self._reminders,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        key = _resolve_employee(kwargs.get("employee_name", ""))
        if key is None:
            names = ", ".join(e["name"] for e in _EMPLOYEES.values())
            return (
                f"No synthetic profile matches '{kwargs.get('employee_name')}'. "
                f"Fictional profiles: {names}.\n\n{_HR_GATE}\n\n"
                f"Source: [Synthetic HRIS Snapshot]\nAgents: AskHRAgent"
            )
        if op == "submit_time_off":
            return handler(
                key,
                kwargs.get("start_date") or "December 18",
                kwargs.get("end_date") or "December 24",
                kwargs.get("days", 5),
            )
        if op == "time_off_check":
            return handler(key, kwargs.get("days", 5))
        return handler(key)

    # ── leave_balance ─────────────────────────────────────────
    def _leave_balance(self, key):
        emp = _EMPLOYEES[key]
        lb = emp["leave_balance"]
        pol = _POLICIES["time_off"]
        holidays = "\n".join(f"- {h['name']}: {h['date']}" for h in _COMPANY_HOLIDAYS)
        return (
            f"**Leave Balance: {emp['name']}**\n\n"
            f"| Leave Type | Available |\n|---|---|\n"
            f"| Vacation (PTO) | {lb['vacation']:g} days |\n"
            f"| Sick Leave | {lb['sick']:g} days |\n"
            f"| Personal Days | {lb['personal']:g} days |\n"
            f"| Accrual Rate | {lb['accrual_rate']} days/month |\n\n"
            f"**Upcoming Company Holidays:**\n{holidays}\n\n"
            f"**Time Off Guidelines:**\n"
            f"- 5+ days: Requires {pol['min_notice_5plus_days']} notice\n"
            f"- {pol['holiday_period']}\n"
            f"- Rollover policy: Max {pol['rollover_max']} days carry to next year\n\n"
            f"{_HR_GATE}\n\n"
            f"Source: [Synthetic HRIS + Policy Snapshot]\nAgents: AskHRAgent"
        )

    # ── submit_time_off ───────────────────────────────────────
    def _submit_time_off(self, key, start_date, end_date, days):
        emp = _EMPLOYEES[key]
        try:
            days = float(days)
        except (TypeError, ValueError):
            days = 5
        req = _submit_time_off(key, start_date, end_date, days)
        pol = _POLICIES["time_off"]
        holiday_note = (
            f"| Holidays | {', '.join(req['holidays'])} - company holiday, not counted |\n"
            if req["holidays"] else ""
        )
        return (
            f"**Time Off Request Preview — Not Submitted**\n\n"
            f"| Detail | Information |\n|---|---|\n"
            f"| Draft Request ID | {req['request_id']} |\n"
            f"| Employee | {emp['name']} |\n"
            f"| Dates | {req['dates']} ({req['days']:g} business days) |\n"
            f"| Return to Work | {req['return']} |\n"
            f"{holiday_note}"
            f"| Status | {req['status']} |\n"
            f"| Approver | {req['manager']} (manager) |\n"
            f"| Balance Impact | {req['balance_before']:g} -> {req['balance_after']:g} days "
            f"(accrual +{emp['leave_balance']['accrual_rate']} days/month continues) |\n\n"
            f"**Approval path:** once you submit it in the HR system, {req['manager']} "
            f"receives the request; expected decision within {pol['auto_approve_hours']} "
            f"hours ({pol['approval_window']}).\n"
            f"**Optional:** add coverage notes for your team before you submit.\n\n"
            f"Review the dates, balance, local policy, and coverage with an "
            f"authorized HR or manager before submission. No notification was sent.\n\n"
            f"{_HR_GATE}\n\n"
            f"Source: [Synthetic HRIS Snapshot]\nAgents: AskHRAgent"
        )

    # ── time_off_check ────────────────────────────────────────
    def _time_off_check(self, key, days):
        emp = _EMPLOYEES[key]
        lb = emp["leave_balance"]
        pol = _POLICIES["time_off"]
        try:
            days = float(days)
        except (TypeError, ValueError):
            days = 5
        after = lb["vacation"] - days
        ok = "Pass" if after >= 0 else "Insufficient balance"
        return (
            f"**Time Off Check: {days:g} days for {emp['name']}**\n\n"
            f"| Balance | Days |\n|---|---|\n"
            f"| Available PTO | {lb['vacation']:g} |\n"
            f"| Requested | {days:g} |\n"
            f"| After Request | {after:g} |\n\n"
            f"**Approver:** {emp['manager']} (manager)\n\n"
            f"| Policy Requirement | Status |\n|---|---|\n"
            f"| Sufficient balance | {ok} |\n"
            f"| Advance notice ({pol['min_notice_5plus_days']} for 5+ days) | Pass if submitted today |\n"
            f"| Team conflicts | None found in the synthetic team calendar |\n"
            f"| Blackout dates | None in the next 30 days |\n\n"
            f"**Typical approval:** {pol['approval_window']}. Share the dates and I will "
            f"prepare the request draft for you to submit.\n\n"
            f"{_HR_GATE}\n\n"
            f"Source: [Synthetic HRIS + Policy Snapshot]\nAgents: AskHRAgent"
        )

    # ── reminders ─────────────────────────────────────────────
    def _reminders(self, key):
        emp = _EMPLOYEES[key]
        lb = emp["leave_balance"]
        pol = _POLICIES["time_off"]
        planned = 5
        year_end = round(lb["vacation"] - planned + lb["accrual_rate"])
        excess = max(0, year_end - pol["rollover_max"])
        return (
            f"**Things to Know: {emp['name']}**\n\n"
            f"- **Open enrollment ({pol['open_enrollment']}):** review medical, dental, "
            f"vision and 401(k) choices for next year.\n"
            f"- **PTO accrual reset ({pol['accrual_reset']}):** unused days above the "
            f"carryover limit are lost.\n"
            f"- **Carryover:** max {pol['rollover_max']} days. After the planned "
            f"{planned}-day trip you would have {lb['vacation'] - planned:g} days, plus "
            f"{lb['accrual_rate']} accrual = about {year_end} days at year-end, so "
            f"plan to use about {excess} more days before Dec 31.\n\n"
            f"**Resources:** benefits portal, HR help desk, Employee Handbook.\n\n"
            f"{_HR_GATE}\n\n"
            f"Source: [Synthetic HRIS + Policy Snapshot]\nAgents: AskHRAgent"
        )

    # ── parental_leave ────────────────────────────────────────
    def _parental_leave(self, key):
        emp = _EMPLOYEES[key]
        pol = _POLICIES["parental_leave"]
        return (
            f"**Parental Leave Policy Guidance: {emp['name']} (Synthetic Profile)**\n\n"
            f"| Benefit | Details |\n|---|---|\n"
            f"| Paternity Leave | {pol['paternity_weeks']} weeks fully paid |\n"
            f"| Maternity Leave | {pol['maternity_weeks']} weeks fully paid |\n"
            f"| Eligibility Rule | Verify tenure, location, leave type, and qualifying event with HR |\n"
            f"| Family Care Stipend | ${pol['stipend']:,} one-time |\n"
            f"| Backup Childcare | {pol['backup_childcare_months']} months included |\n\n"
            f"**Additional Support:**\n"
            f"- Flexible return-to-work schedule available\n"
            f"- Parent Employee Resource Group\n"
            f"- Lactation room access\n\n"
            f"**Next Step:** Ask an authorized HR reviewer to confirm the applicable "
            f"policy and submission timing. Do not disclose medical or family details here.\n\n"
            f"{_HR_GATE}\n\n"
            f"Source: [Synthetic Benefits Policy Snapshot]\nAgents: AskHRAgent"
        )

    # ── health_insurance ──────────────────────────────────────
    def _health_insurance(self, key):
        emp = _EMPLOYEES[key]
        hp = emp["health_plan"]
        pol = _POLICIES["health_insurance"]
        dep = _POLICIES["dependents"]
        deps = ", ".join(hp["dependents"]) if hp["dependents"] else "None"

        def pair(a, b):
            return f"${a:,} / ${b:,}" if b else f"${a:,}"
        copay = f"| Primary Care Copay | ${hp['primary_care_copay']} |\n" if hp.get("primary_care_copay") else ""
        eligible = "\n".join(f"| {who} | {status} |" for who, status in dep["eligible"])
        return (
            f"**Health Insurance: {emp['name']}**\n\n"
            f"| Coverage | Detail |\n|---|---|\n"
            f"| Plan | {hp['plan']} |\n"
            f"| Monthly Premium | ${hp['monthly_premium']:,} (your contribution) |\n"
            f"| Deductible (Individual / Family) | {pair(hp['deductible_individual'], hp['deductible_family'])} |\n"
            f"| Out-of-Pocket Max (Individual / Family) | {pair(hp['oop_max_individual'], hp['oop_max_family'])} |\n"
            f"{copay}"
            f"| Current Dependents | {deps} |\n\n"
            f"**Who Can Be Added as a Dependent:**\n\n"
            f"| Relationship | Plan Rule |\n|---|---|\n{eligible}\n\n"
            f"**Parents:** {dep['parent_rule']}\n"
            f"**Alternatives for parents:** {'; '.join(dep['alternatives'])}.\n"
            f"**Policy reference:** {dep['reference']}\n\n"
            f"**Adding a Dependent:**\n"
            f"- Enrollment window: {pol['enrollment_window_days']} days from qualifying event\n"
            f"- Premium increase: +${pol['dependent_premium_increase']}/month\n"
            f"- Coverage effective: Date of qualifying event\n\n"
            f"Verify plan rules and enrollment eligibility with the benefits "
            f"administrator before making a selection.\n\n"
            f"{_HR_GATE}\n\n"
            f"Source: [Synthetic Benefits Policy Snapshot]\nAgents: AskHRAgent"
        )

    # ── remote_work ───────────────────────────────────────────
    def _remote_work(self, key):
        emp = _EMPLOYEES[key]
        pol = _POLICIES["remote_work"]
        return (
            f"**Remote Work Policy Guidance: {emp['name']} (Synthetic Profile)**\n\n"
            f"| Benefit | Published Policy Example |\n|---|---|\n"
            f"| Standard Allowance | {pol['standard_days_per_week']} days/week remote |\n"
            f"| Eligibility | Requires role, location, and manager/HR review |\n"
            f"| Core Hours | {pol['core_hours']} |\n\n"
            f"**Home Office Support:**\n"
            f"- Equipment stipend: ${pol['equipment_stipend']:,} one-time\n"
            f"- Internet reimbursement: ${pol['internet_reimbursement']}/month\n"
            f"- Ergonomic assessment: Virtual consultation\n"
            f"- Same-day IT support available\n\n"
            f"Do not infer caregiver, disability, medical, or family status from "
            f"a request. Route exceptions to authorized HR review.\n\n"
            f"{_HR_GATE}\n\n"
            f"Source: [Synthetic HR Policy Snapshot]\nAgents: AskHRAgent"
        )

    # ── benefits_summary ──────────────────────────────────────
    def _benefits_summary(self, key):
        emp = _EMPLOYEES[key]
        lb = emp["leave_balance"]
        hp = emp["health_plan"]
        start = emp.get("start_date") or f"{emp['tenure_years']} years tenure"
        current = [f"{hp['plan']} medical (${hp['monthly_premium']}/mo)"]
        if emp.get("dental_premium"):
            current.append(f"Dental (${emp['dental_premium']}/mo)")
        if emp.get("vision_premium"):
            current.append(f"Vision (${emp['vision_premium']}/mo)")
        if emp.get("retirement"):
            r = emp["retirement"]
            current.append(f"{r['plan']} {r['contribution_pct']}% contribution "
                           f"({r['match_pct']}% company match)")
        return (
            f"**Benefits Summary: {emp['name']} (Synthetic Profile)**\n\n"
            f"| Profile | Detail |\n|---|---|\n"
            f"| Name | {emp['name']} |\n"
            f"| Department | {emp['department']} |\n"
            f"| Start Date | {start} |\n"
            f"| Benefits Tier | {emp.get('benefits_tier', 'See plan')} |\n\n"
            f"**Current Benefits:** {'; '.join(current)}\n\n"
            f"| Leave | Balance |\n|---|---|\n"
            f"| PTO | {lb['vacation']:g} days |\n"
            f"| Sick | {lb['sick']:g} days |\n"
            f"| Personal | {lb['personal']:g} days |\n\n"
            f"**How to request time off:** tell me the dates; I check the policy and "
            f"prepare a draft request for you to submit to {emp['manager']}.\n\n"
            f"No salary, medical, family-status, or total-compensation value is inferred.\n\n"
            f"{_HR_GATE}\n\n"
            f"Source: [Synthetic HR Policy Snapshot]\nAgents: AskHRAgent"
        )


if __name__ == "__main__":
    agent = AskHRAgent()
    for op in _OPERATIONS:
        print("=" * 60)
        print(agent.perform(operation=op, employee_name="Sarah Chen"))
        print()
