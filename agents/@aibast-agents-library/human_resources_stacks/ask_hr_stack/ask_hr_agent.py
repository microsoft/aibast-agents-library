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
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/ask-hr",
    "version": "1.0.0",
    "display_name": "Ask HR",
    "description": "AI-powered HR assistant for time-off requests, benefits inquiries, parental leave, and policy lookups.",
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
        "parental_eligible": True,
        "remote_eligible": True,
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
        "parental_eligible": False,
        "remote_eligible": True,
    },
    "sarah": {
        "id": "emp-1003", "name": "Sarah Williams", "title": "Engineering Lead",
        "department": "Engineering", "manager": "Alex Rivera", "tenure_years": 5.0,
        "email": "sarah.williams@contoso.com",
        "leave_balance": {
            "vacation": 22.0, "sick": 10.0, "personal": 3.0,
            "accrual_rate": 1.5,
        },
        "health_plan": {
            "plan": "PPO Family Plan", "monthly_premium": 450,
            "deductible_individual": 500, "deductible_family": 1500,
            "oop_max_individual": 3000, "oop_max_family": 6000,
            "dependents": ["Spouse", "Child (age 4)"],
        },
        "parental_eligible": True,
        "remote_eligible": True,
    },
}

_COMPANY_HOLIDAYS = [
    {"name": "Memorial Day", "date": "May 26"},
    {"name": "Independence Day", "date": "Jul 4"},
    {"name": "Labor Day", "date": "Sep 1"},
    {"name": "Thanksgiving", "date": "Nov 27-28"},
    {"name": "Year-End", "date": "Dec 24-25, Dec 31-Jan 1"},
]

_POLICIES = {
    "time_off": {
        "min_notice_5plus_days": "2 weeks",
        "holiday_period": "Dec 15 - Jan 5 requires manager pre-approval",
        "rollover_max": 5,
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
}

_PENDING_REQUESTS = []


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_employee(query):
    if not query:
        return "jordan"
    q = query.lower().strip()
    for key in _EMPLOYEES:
        if key in q or q in _EMPLOYEES[key]["name"].lower():
            return key
    return "jordan"


def _benefits_value(emp):
    pol = _POLICIES
    values = {}
    if emp["parental_eligible"]:
        weeks = pol["parental_leave"]["paternity_weeks"]
        # Rough salary estimate from title
        weekly_salary = 2500
        values["parental_leave"] = weeks * weekly_salary
        values["family_stipend"] = pol["parental_leave"]["stipend"]
        values["childcare_benefit"] = 3000
    values["equipment_stipend"] = pol["remote_work"]["equipment_stipend"]
    total = sum(values.values())
    return values, total


def _submit_time_off(emp_key, start_date, end_date, days):
    emp = _EMPLOYEES[emp_key]
    remaining = emp["leave_balance"]["vacation"] - days
    request = {
        "employee": emp["name"], "dates": f"{start_date} to {end_date}",
        "days": days, "status": "Pending Manager Approval",
        "manager": emp["manager"], "balance_after": remaining,
    }
    _PENDING_REQUESTS.append(request)
    return request


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class AskHRAgent(BasicAgent):
    """
    Employee self-service HR assistant.

    Operations:
        leave_balance     - check vacation, sick, personal day balances
        submit_time_off   - request time off for given dates
        parental_leave    - parental leave eligibility and benefits
        health_insurance  - health plan details and dependent enrollment
        remote_work       - remote work policy and new-parent flexibility
        benefits_summary  - comprehensive benefits package overview
    """

    def __init__(self):
        self.name = "AskHRAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "leave_balance", "submit_time_off",
                            "parental_leave", "health_insurance",
                            "remote_work", "benefits_summary",
                        ],
                        "description": "The HR inquiry to handle",
                    },
                    "employee_name": {
                        "type": "string",
                        "description": "Employee name (e.g. 'Jordan Chen')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "leave_balance")
        key = _resolve_employee(kwargs.get("employee_name", ""))
        dispatch = {
            "leave_balance": self._leave_balance,
            "submit_time_off": self._submit_time_off,
            "parental_leave": self._parental_leave,
            "health_insurance": self._health_insurance,
            "remote_work": self._remote_work,
            "benefits_summary": self._benefits_summary,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
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
            f"| Vacation | {lb['vacation']} days |\n"
            f"| Sick Leave | {lb['sick']} days |\n"
            f"| Personal Days | {lb['personal']} days |\n"
            f"| Accrual Rate | {lb['accrual_rate']} days/month |\n\n"
            f"**Upcoming Company Holidays:**\n{holidays}\n\n"
            f"**Time Off Guidelines:**\n"
            f"- 5+ days: Requires {pol['min_notice_5plus_days']} notice\n"
            f"- {pol['holiday_period']}\n"
            f"- Rollover policy: Max {pol['rollover_max']} days carry to next year\n\n"
            f"Source: [Workday + HR Portal]\nAgents: AskHRAgent"
        )

    # ── submit_time_off ───────────────────────────────────────
    def _submit_time_off(self, key):
        emp = _EMPLOYEES[key]
        start = (datetime.now() + timedelta(days=30)).strftime("%b %d")
        end = (datetime.now() + timedelta(days=34)).strftime("%b %d")
        req = _submit_time_off(key, start, end, 5)
        return (
            f"**Time Off Request Submitted**\n\n"
            f"| Detail | Information |\n|---|---|\n"
            f"| Employee | {emp['name']} |\n"
            f"| Dates | {req['dates']} (5 days) |\n"
            f"| Status | {req['status']} |\n"
            f"| Manager | {req['manager']} |\n"
            f"| Balance After | {req['balance_after']} days remaining |\n\n"
            f"Your manager will be notified automatically.\n\n"
            f"Source: [Workday]\nAgents: AskHRAgent"
        )

    # ── parental_leave ────────────────────────────────────────
    def _parental_leave(self, key):
        emp = _EMPLOYEES[key]
        pol = _POLICIES["parental_leave"]
        eligible = emp["parental_eligible"]
        status = "Qualified" if eligible else "Not yet eligible (requires 1+ year tenure)"
        return (
            f"**Parental Leave Benefits: {emp['name']}**\n\n"
            f"| Benefit | Details |\n|---|---|\n"
            f"| Paternity Leave | {pol['paternity_weeks']} weeks fully paid |\n"
            f"| Maternity Leave | {pol['maternity_weeks']} weeks fully paid |\n"
            f"| Your Eligibility | {status} |\n"
            f"| Family Care Stipend | ${pol['stipend']:,} one-time |\n"
            f"| Backup Childcare | {pol['backup_childcare_months']} months included |\n\n"
            f"**Additional Support:**\n"
            f"- Flexible return-to-work schedule available\n"
            f"- Parent Employee Resource Group\n"
            f"- Lactation room access\n\n"
            f"**Next Step:** Submit parental leave form 30 days before due date.\n\n"
            f"Source: [Benefits Portal]\nAgents: AskHRAgent"
        )

    # ── health_insurance ──────────────────────────────────────
    def _health_insurance(self, key):
        emp = _EMPLOYEES[key]
        hp = emp["health_plan"]
        pol = _POLICIES["health_insurance"]
        deps = ", ".join(hp["dependents"]) if hp["dependents"] else "None"
        return (
            f"**Health Insurance: {emp['name']}**\n\n"
            f"| Coverage | Detail |\n|---|---|\n"
            f"| Plan | {hp['plan']} |\n"
            f"| Monthly Premium | ${hp['monthly_premium']:,} (your contribution) |\n"
            f"| Deductible (Individual) | ${hp['deductible_individual']:,} |\n"
            f"| Out-of-Pocket Max | ${hp['oop_max_individual']:,} |\n"
            f"| Current Dependents | {deps} |\n\n"
            f"**Adding a Dependent:**\n"
            f"- Enrollment window: {pol['enrollment_window_days']} days from qualifying event\n"
            f"- Premium increase: +${pol['dependent_premium_increase']}/month\n"
            f"- Coverage effective: Date of qualifying event\n\n"
            f"**New Baby Benefits (100% Covered):**\n"
            f"- Well-baby care visits\n"
            f"- All immunizations\n"
            f"- Pediatric visits: ${pol['pediatric_copay']} copay\n"
            f"- Dependent life insurance: ${pol['dependent_life_insurance']:,} automatic\n\n"
            f"Source: [Benefits Portal + Insurance Carrier]\nAgents: AskHRAgent"
        )

    # ── remote_work ───────────────────────────────────────────
    def _remote_work(self, key):
        emp = _EMPLOYEES[key]
        pol = _POLICIES["remote_work"]
        eligible = emp["remote_eligible"]
        total_days = pol["standard_days_per_week"]
        parent_note = ""
        if emp["parental_eligible"]:
            total_days += pol["new_parent_bonus_days"]
            parent_note = (
                f"\n**New Parent Options:**\n"
                f"- Additional {pol['new_parent_bonus_days']} remote days/week for {pol['new_parent_bonus_months']} months\n"
                f"- Gradual return: Part-time for 4 weeks\n"
                f"- Emergency childcare: 10 days/year included\n"
            )
        return (
            f"**Remote Work Policy: {emp['name']}**\n\n"
            f"| Benefit | Your Eligibility |\n|---|---|\n"
            f"| Standard Allowance | {pol['standard_days_per_week']} days/week remote |\n"
            f"| Your Status | {'Eligible' if eligible else 'Not eligible'} |\n"
            f"| Core Hours | {pol['core_hours']} |\n\n"
            f"**Home Office Support:**\n"
            f"- Equipment stipend: ${pol['equipment_stipend']:,} one-time\n"
            f"- Internet reimbursement: ${pol['internet_reimbursement']}/month\n"
            f"- Ergonomic assessment: Virtual consultation\n"
            f"- Same-day IT support available\n"
            f"{parent_note}\n"
            f"Source: [HR Policy Portal + Benefits]\nAgents: AskHRAgent"
        )

    # ── benefits_summary ──────────────────────────────────────
    def _benefits_summary(self, key):
        emp = _EMPLOYEES[key]
        lb = emp["leave_balance"]
        hp = emp["health_plan"]
        values, total = _benefits_value(emp)
        pol = _POLICIES

        items = []
        items.append(f"- Time Off: {lb['vacation']} vacation days + {lb['sick']} sick days")
        if emp["parental_eligible"]:
            items.append(f"- Parental Leave: {pol['parental_leave']['paternity_weeks']} weeks paid + ${pol['parental_leave']['stipend']:,} stipend")
        items.append(f"- Health Coverage: {hp['plan']} (${hp['monthly_premium']}/mo)")
        items.append(f"- Remote Work: {pol['remote_work']['standard_days_per_week']} days/week")
        items.append(f"- Equipment Stipend: ${pol['remote_work']['equipment_stipend']:,}")

        value_lines = "\n".join(f"- {k.replace('_', ' ').title()}: ${v:,}" for k, v in values.items())

        return (
            f"**Benefits Summary: {emp['name']}**\n"
            f"**{emp['title']}, {emp['department']}** ({emp['tenure_years']} years)\n\n"
            f"**Your Benefits Package:**\n"
            + "\n".join(items) + "\n\n"
            f"**Financial Value:**\n{value_lines}\n"
            f"**Total estimated value: ${total:,}**\n\n"
            f"**Next Steps:**\n"
            f"1. Review parental leave form (submit 30 days before due date)\n"
            f"2. Benefits enrollment changes within 30 days of qualifying event\n"
            f"3. Discuss remote schedule with {emp['manager']}\n\n"
            f"Source: [All HR Systems]\nAgents: AskHRAgent"
        )


if __name__ == "__main__":
    agent = AskHRAgent()
    for op in ["leave_balance", "submit_time_off", "parental_leave",
               "health_insurance", "remote_work", "benefits_summary"]:
        print("=" * 60)
        print(agent.perform(operation=op, employee_name="Jordan Chen"))
        print()
