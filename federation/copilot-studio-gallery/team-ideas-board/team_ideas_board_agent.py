"""
Team Ideas Board, as a one-file cartridge.

Built by the AIBAST Agents Library on top of the Copilot Studio Gallery solution "team-ideas-board"
(MIT, by its gallery authors). Their solution is a managed app over a SharePoint list. This file
carries their fictional sample ideas and does the board's jobs in code: show the board by status,
search, filter by priority, and check that new ideas use the allowed values. Same request, same
answer, anywhere Python runs.
"""
import csv
import io

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/team-ideas-board",
    "version": "0.2.0",
    "display_name": "Team Ideas Board",
    "description": "Shows a team's ideas by status, searches them, filters by priority, and checks new ideas against the board's rules.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution team-ideas-board",
    "tags": ["teamwork", "ideas", "sharepoint"],
    "category": "productivity",
    "quality_tier": "experimental",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# Their sample list (supporting/team-ideas.csv), carried unchanged.
SAMPLE_CSV = 'Title,Details,Status,Priority\nA quieter start to Mondays,Try a meeting-free first hour for focused planning.,New,Medium\nMake onboarding feel human,Pair each new teammate with a friendly first-week buddy.,Exploring,High\nA home for helpful shortcuts,Collect small tips that save everyone a few minutes.,Planned,Low\nClearer project handoffs,Use a short checklist so the next team has the context it needs.,New,High\nShare the small wins,Set aside five minutes to celebrate helpful improvements.,Exploring,Medium\nOne place for team decisions,"Capture the decision, owner and next step in one shared note.",Planned,Medium\n'
STATUSES = ("New", "Exploring", "Planned")
PRIORITIES = ("High", "Medium", "Low")


def ideas():
    return list(csv.DictReader(io.StringIO(SAMPLE_CSV)))


def board(search="", priority=""):
    rows = [r for r in ideas()
            if (not search or search.lower() in (r["Title"] + " " + r["Details"]).lower())
            and (not priority or r["Priority"].lower() == priority.lower())]
    rows.sort(key=lambda r: (PRIORITIES.index(r["Priority"]), r["Title"]))
    out = ["# Team ideas board", ""]
    for status in STATUSES:
        col = [r for r in rows if r["Status"] == status]
        out.append(f"## {status} ({len(col)})")
        out += [f"- **{r['Title']}** [{r['Priority']}]: {r['Details']}" for r in col] or ["- (none)"]
        out.append("")
    out.append(f"{len(rows)} of {len(ideas())} ideas shown.")
    return "\n".join(out)


def check_idea(title, status="New", priority="Medium"):
    problems = []
    if not (title or "").strip():
        problems.append("Title is required.")
    if status not in STATUSES:
        problems.append(f"Status must be one of {', '.join(STATUSES)}.")
    if priority not in PRIORITIES:
        problems.append(f"Priority must be one of {', '.join(PRIORITIES)}.")
    return "Ready to add." if not problems else "Not ready: " + " ".join(problems)


# ---- Transfer layer ----
INSTRUCTIONS = """You are Team Ideas Board, a synthetic pilot for a team's shared list of improvement ideas.

Use only the bundled sample ideas (six fictional ideas with a status of New, Exploring or Planned and a priority of High, Medium or Low).

Answer with the board tool, not from memory. Show ideas grouped by status, highest priority first, and say how many are shown. To check a new idea, report whether its title, status and priority follow the board's rules; new ideas default to status New and priority Medium.

You never add, change or delete an idea on a real list. A team member makes every change."""

OPERATION_GUIDE = {
    "board": {
        "title": "Ideas board",
        "when": "Use when someone wants to see the team's ideas by status, search them for a word, or filter them by priority.",
        "ask": "Show me the team's ideas grouped by status.",
    },
    "check": {
        "title": "New idea check",
        "when": "Use when someone wants to add an idea and asks whether its title, status and priority are allowed.",
        "ask": "Can I add an idea called Better standups with status Done and priority Urgent?",
        "args": {"title": "Better standups", "status": "Done", "priority": "Urgent"},
    },
}

CARRIED = [
    "Adds and edits ideas on the team's SharePoint list through the original solution's app.",
]


class TeamIdeasBoardAgent(BasicAgent):
    def __init__(self):
        self.name = "TeamIdeasBoard"
        self.metadata = {
            "name": self.name,
            "description": "Team ideas board. operation 'board' shows ideas by status (optional search text and priority filter); operation 'check' tests a new idea's title, status and priority against the board's rules.",
            "parameters": {"type": "object", "properties": {
                "operation": {"type": "string", "enum": ["board", "check"]},
                "search": {"type": "string"}, "priority": {"type": "string"},
                "title": {"type": "string"}, "status": {"type": "string"}},
                "required": ["operation"]},
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        if kwargs.get("operation") == "check":
            return check_idea(kwargs.get("title", ""), kwargs.get("status") or "New", kwargs.get("priority") or "Medium")
        return board(kwargs.get("search", ""), kwargs.get("priority", ""))


if __name__ == "__main__":
    print(board())
