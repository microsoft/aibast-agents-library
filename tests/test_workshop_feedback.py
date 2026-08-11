import json
from pathlib import Path
import subprocess
import textwrap


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/workshop-feedback.yml"
METRICS_WORKFLOW = ROOT / ".github/workflows/metrics.yml"


def run_signal_classifier(
    body="",
    labels=(),
    *,
    action="opened",
    state="open",
):
    workflow = WORKFLOW.read_text(encoding="utf-8")
    script = workflow.split("script: |", 1)[1].split(
        "\n\n      - name: Dispatch metrics compilation", 1
    )[0]
    harness = f"""
const calls = [];
const context = {{
  payload: {{
    action: {json.dumps(action)},
    issue: {{
      body: {json.dumps(body)},
      labels: {json.dumps(list(labels))},
      state: {json.dumps(state)}
    }}
  }},
  repo: {{ owner: "owner", repo: "repo" }},
  issue: {{ number: 42 }}
}};
const github = {{
  rest: {{
    issues: {{
      getLabel: async (args) => calls.push(["getLabel", args]),
      createLabel: async (args) => calls.push(["createLabel", args]),
      removeLabel: async (args) => calls.push(["removeLabel", args]),
      addLabels: async (args) => calls.push(["addLabels", args]),
      createComment: async (args) => calls.push(["createComment", args]),
      update: async (args) => calls.push(["update", args])
    }}
  }}
}};
(async () => {{
  const result = await (async () => {{
{textwrap.indent(textwrap.dedent(script), "    ")}
  }})();
  console.log(JSON.stringify({{ result, calls }}));
}})().catch((error) => {{
  console.error(error);
  process.exit(1);
}});
"""
    result = subprocess.run(
        ["node"],
        input=harness,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_workshop_feedback_workflow_detects_structured_signal():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "issues:" in text
    assert "types: [opened, edited, closed, reopened, labeled, unlabeled]" in text
    assert "actions: write" in text
    assert "issues: write" in text
    assert "<!-- aibast-workshop-feedback:v1 -->" in text
    assert "<!-- aibast-achievement-progress:v1 -->" in text
    assert "<!-- aibast-workshop-cohort:v1 -->" in text
    assert "<!-- aibast-badge-qualification:v1 -->" in text
    assert "<!-- aibast-agent-upvote:v1 -->" not in text
    assert "aibast-achievements-achievement" not in text
    assert "||" in text
    assert "workshop-feedback" in text
    assert "needs-triage" in text
    assert "agent-upvote" not in text
    assert "achievement-progress" in text
    assert "workshop-cohort" in text
    assert "badge-qualification" in text
    assert "needs-private-review" in text
    assert "cohort-verified" in text
    assert "badge-qualified" in text
    assert "createLabel" in text
    assert "addLabels" in text
    assert "removeLabel" in text
    assert "createComment" in text
    assert 'state: "closed"' in text
    job_header = text.split("jobs:", 1)[1].split("runs-on:", 1)[0]
    assert "if:" not in job_header


def test_structured_signal_dispatches_metrics_on_repository_default_branch():
    text = WORKFLOW.read_text(encoding="utf-8")

    label_position = text.index("await github.rest.issues.addLabels")
    dispatch_position = text.index("await github.rest.actions.createWorkflowDispatch")
    assert dispatch_position > label_position
    assert "const defaultBranch = context.payload.repository.default_branch;" in text
    assert 'workflow_id: "metrics.yml"' in text
    assert "ref: defaultBranch" in text
    assert 'ref: "main"' not in text
    assert "if: steps.process-signal.outputs.result == 'true'" in text


def test_signal_classification_fails_closed_and_reconciles_removed_markers():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert 'id: process-signal' in text
    assert 'const isWorkshopFeedback = body.startsWith("<!-- aibast-workshop-feedback:v1 -->")' in text
    assert "const markerCount = [" in text
    assert "const hasCurrentMarker = markerCount > 0;" in text
    assert "automaticallyManagedNames.has(name)" in text
    assert "if (!hasCurrentMarker && !hasManagedLabel)" in text
    assert "return false;" in text
    assert "? []" in text
    assert "if (labels.length)" in text
    assert "return true;" in text
    assert "if: steps.process-signal.outputs.result == 'true'" in text


def test_signal_classifier_behavior_is_fail_closed_and_removal_safe():
    unrelated = run_signal_classifier(body="ordinary issue", labels=("bug",))
    assert unrelated == {"result": False, "calls": []}

    stale = run_signal_classifier(
        body="marker removed",
        labels=({"name": "achievement-progress"}, {"name": "bug"}),
    )
    assert stale["result"] is True
    assert [call[0] for call in stale["calls"]] == ["removeLabel"]
    assert stale["calls"][0][1]["name"] == "achievement-progress"

    current = run_signal_classifier(
        body="<!-- aibast-workshop-feedback:v1 -->",
        labels=(),
    )
    assert current["result"] is True
    assert [call[0] for call in current["calls"]] == [
        "getLabel",
        "getLabel",
        "addLabels",
    ]
    assert current["calls"][-1][1]["labels"] == [
        "workshop-feedback",
        "needs-triage",
    ]


def test_valid_achievement_signal_is_acknowledged_and_closed():
    body = """<!-- aibast-achievement-progress:v1 -->
## Workshop achievement progress

- Schema: `aibast-achievement-progress/1.0`
- Workshop: `account-intelligence`
- Agent: `@aibast-agents-library/account-intelligence`
- Achievements: started
- Source: https://example.test/quest.html
"""
    result = run_signal_classifier(body=body)
    assert result["result"] is True
    assert [call[0] for call in result["calls"]] == [
        "getLabel",
        "addLabels",
        "createComment",
        "update",
    ]
    assert result["calls"][1][1]["labels"] == ["achievement-progress"]
    assert result["calls"][-1][1]["state"] == "closed"


def test_placeholder_cohort_signal_stays_open_for_correction():
    body = """<!-- aibast-workshop-cohort:v1 -->
## Public workshop cohort trigger

- Schema: `aibast-workshop-cohort/1.0`
- Workshop: `account-intelligence`
- Agent: `@aibast-agents-library/account-intelligence`
- Cohort code: `REPLACE-WITH-PUBLIC-CODE`
- Session date: `YYYY-MM-DD`
- Attendee count: `REPLACE-WITH-NUMBER`
- Private facilitator form submitted: `yes`
- Public progress consent: `yes`
"""
    result = run_signal_classifier(body=body)
    assert [call[0] for call in result["calls"]] == [
        "getLabel",
        "addLabels",
        "createComment",
    ]
    assert result["calls"][1][1]["labels"] == ["needs-triage"]


def test_valid_cohort_signal_gets_private_review_gate_and_closes():
    body = """<!-- aibast-workshop-cohort:v1 -->
## Public workshop cohort trigger

- Schema: `aibast-workshop-cohort/1.0`
- Workshop: `account-intelligence`
- Agent: `@aibast-agents-library/account-intelligence`
- Cohort code: `AIBAST-20260811-DEMO`
- Session date: `2026-08-11`
- Attendee count: `24`
- Private facilitator form submitted: `yes`
- Public progress consent: `yes`
"""
    result = run_signal_classifier(body=body)
    assert result["calls"][2][0] == "addLabels"
    assert result["calls"][2][1]["labels"] == [
        "workshop-cohort",
        "needs-private-review",
    ]
    assert result["calls"][-1][0] == "update"
    assert result["calls"][-1][1]["state"] == "closed"


def test_private_field_in_public_issue_is_rejected_and_left_open():
    body = """<!-- aibast-workshop-cohort:v1 -->
## Public workshop cohort trigger

- Schema: `aibast-workshop-cohort/1.0`
- Workshop: `account-intelligence`
- Agent: `@aibast-agents-library/account-intelligence`
- Cohort code: `AIBAST-20260811-DEMO`
- Session date: `2026-08-11`
- Attendee count: `24`
- Private facilitator form submitted: `yes`
- Public progress consent: `yes`
- MSIX: `123456`
"""
    result = run_signal_classifier(body=body)
    assert result["calls"][1][0] == "addLabels"
    assert result["calls"][1][1]["labels"] == ["needs-triage"]
    assert all(call[0] != "update" for call in result["calls"])


def test_unbulleted_private_field_and_unknown_workshop_are_not_closed():
    valid = """<!-- aibast-workshop-cohort:v1 -->
## Public workshop cohort trigger

- Schema: `aibast-workshop-cohort/1.0`
- Workshop: `account-intelligence`
- Agent: `@aibast-agents-library/account-intelligence`
- Cohort code: `AIBAST-20260811-DEMO`
- Session date: `2026-08-11`
- Attendee count: `24`
- Private facilitator form submitted: `yes`
- Public progress consent: `yes`
"""
    for body in (
        valid + "Email: person@example.test\n",
        valid + "* Email: person@example.test\n",
        valid + "+ MSIX: 123456\n",
        valid + "1. Token: secret\n",
        valid + "> Email: person@example.test\n",
        valid + "• Customer: Contoso\n",
        valid + "Email:person@example.test\n",
        valid + "* MSIX:123456\n",
        valid + "**Email**: person@example.test\n",
        valid + "`MSIX`: 123456\n",
        valid + "<strong>Customer</strong>: Contoso\n",
        valid + "&bull; Email: person@example.test\n",
        valid + "&lt;strong&gt;Email&lt;/strong&gt;: person@example.test\n",
        valid + "&#8226; MSIX: 123456\n",
        valid + "&#x2022; Token: secret\n",
        valid + "Email&colon; person@example.test\n",
        valid + "F\u200Boo: hidden\n",
        valid + "<!-- Email: person@example.test -->\n",
        valid.replace(
            "- Workshop: `account-intelligence`",
            "- Workshop: `not-a-workshop`",
        ),
    ):
        result = run_signal_classifier(body=body)
        assert all(call[0] != "update" for call in result["calls"])
        labels = [
            call[1]["labels"]
            for call in result["calls"]
            if call[0] == "addLabels"
        ]
        assert labels == [["needs-triage"]]


def test_reviewer_labels_are_never_automatically_removed():
    body = """<!-- aibast-badge-qualification:v1 -->
## Public badge qualification trigger

- Schema: `aibast-badge-qualification/1.0`
- Workshop: `account-intelligence`
- Agent: `@aibast-agents-library/account-intelligence`
- Cohort code: `AIBAST-20260811-DEMO`
- Achievement progress issue: `https://github.com/microsoft/aibast-agents-library/issues/123`
- Private qualification form submitted: `yes`
- Public profile consent: `yes`
"""
    result = run_signal_classifier(
        body=body,
        labels=(
            {"name": "badge-qualification"},
            {"name": "needs-private-review"},
            {"name": "badge-qualified"},
        ),
        action="labeled",
        state="closed",
    )
    removed = [
        call[1]["name"]
        for call in result["calls"]
        if call[0] == "removeLabel"
    ]
    assert "badge-qualified" not in removed


def test_marker_removal_clears_stale_managed_labels_before_dispatch():
    text = WORKFLOW.read_text(encoding="utf-8")

    remove_position = text.index("await github.rest.issues.removeLabel")
    success_position = text.index("return true;")
    dispatch_position = text.index("await github.rest.actions.createWorkflowDispatch")
    assert remove_position < success_position < dispatch_position
    assert "!automaticallyManagedNames.has(name)" in text
    assert "selectedNames.includes(name)" in text


def test_metrics_dispatch_cannot_retrigger_from_snapshot_state_commits():
    text = METRICS_WORKFLOW.read_text(encoding="utf-8")
    push_paths = text.split("paths:", 1)[1].split("permissions:", 1)[0]

    assert "concurrency:" in text
    assert "group: metrics-snapshot" in text
    assert "state/" not in push_paths
    assert "state/metrics.json" not in push_paths
    assert "state/metrics_history.json" not in push_paths


def test_metrics_workflow_compiles_issues_from_its_own_repository():
    text = METRICS_WORKFLOW.read_text(encoding="utf-8")
    collect_step = text.split("- name: Collect public metrics", 1)[1].split(
        "- name: Report traffic source", 1
    )[0]

    assert "METRICS_OWNER: ${{ github.repository_owner }}" in collect_step
    assert "METRICS_REPO: ${{ github.event.repository.name }}" in collect_step
    assert "run: python scripts/build_metrics.py" in collect_step
    assert "METRICS_OWNER: microsoft" not in collect_step
    assert "DISCUSSIONS_TOKEN: ${{ secrets.GITHUB_TOKEN }}" in text
    assert "discussions: write" in text
    assert "python scripts/sync_agent_discussions.py" in text


def test_workflow_applies_signal_specific_labels_and_descriptions():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert 'const isAchievementProgress = body.startsWith("<!-- aibast-achievement-progress:v1 -->")' in text
    assert '? ["achievement-progress"]' in text
    assert ': ["workshop-feedback", "needs-triage"];' in text
    assert "Structured feedback submitted from an AIBAST workshop." in text
    assert "Opt-in public workshop achievement progress sync." in text
    assert "agent-upvote" not in text
    assert "AIBAST Beta workshop" not in text


def test_achievement_progress_gets_only_achievement_label_without_changing_other_signal_labels():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert ": isAchievementProgress" in text
    assert '? ["achievement-progress"]' in text
    assert ': ["workshop-feedback", "needs-triage"];' in text
    assert "const automaticallyManagedNames = new Set([" in text
    assert '"cohort-verified"' not in text.split(
        "const automaticallyManagedNames = new Set([", 1
    )[1].split("]);", 1)[0]
    assert '"badge-qualified"' not in text.split(
        "const automaticallyManagedNames = new Set([", 1
    )[1].split("]);", 1)[0]


def test_metrics_workflow_reads_issues_and_verifies_achievement_profiles_and_scoring():
    text = METRICS_WORKFLOW.read_text(encoding="utf-8")

    assert "issues: read" in text
    assert "snapshot.get('achievements', {})" in text
    assert "achievements.get('schema') != 'aibast-achievements/2.0'" in text
    assert "achievements.get('profiles', [])" in text
    assert "achievements.get('workshops', [])" in text
    assert "allowed_profile_keys" in text
    assert "'workshop_completions', 'hard_completions', 'badges'" in text
    assert "'achievement_ids', 'completed_workshops'" in text
    assert "'hard-mode-completed': 50" in text
    assert "profile['points'] > profile['starts'] * 150" in text
    assert "Achievement profile contains logically impossible progress" in text
    assert "Achievement rollups do not reconcile" in text
    assert "Achievement completion rates do not reconcile" in text
    assert "Achievement profiles contain unexpected or privacy-unsafe fields" in text
    assert "Achievement point total does not reconcile" in text
    assert "snapshot.get('workshop_certification', {})" in text
    assert "aibast-workshop-certification/1.0" in text
    assert "Facilitator certification profiles contain unsafe fields" in text
    assert "Candidate certification profiles contain unsafe fields" in text
    assert '"cohort_code"' in text
    assert '"achievement_issue_url"' in text
    assert "aibast-achievements/1.0" not in text


def test_generated_workshops_expose_contextual_beta_reports():
    quest = (
        ROOT / "solutions/time-entry-billing/quest.html"
    ).read_text(encoding="utf-8")
    manual = (
        ROOT / "solutions/time-entry-billing/manual-tutorial.html"
    ).read_text(encoding="utf-8")

    for document in (quest, manual):
        assert "Report an issue" in document
        assert "Workshop feedback" in document
        assert "Beta workshop" not in document
        assert "<!-- aibast-workshop-feedback:v1 -->" in document
        assert "aibast-workshop-feedback/1.0" in document
        assert "issues/new" in document
        assert "does not submit" in document

    manual_reports = manual.count('data-report-location=')
    assert manual_reports == 20
    assert quest.count('data-report-location=') == 12 + manual_reports
