import json
from pathlib import Path
import subprocess
import textwrap


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/workshop-feedback.yml"
METRICS_WORKFLOW = ROOT / ".github/workflows/metrics.yml"


def run_signal_classifier(body="", labels=()):
    workflow = WORKFLOW.read_text(encoding="utf-8")
    script = workflow.split("script: |", 1)[1].split(
        "\n\n      - name: Dispatch metrics compilation", 1
    )[0]
    harness = f"""
const calls = [];
const context = {{
  payload: {{ issue: {{ body: {json.dumps(body)}, labels: {json.dumps(list(labels))} }} }},
  repo: {{ owner: "owner", repo: "repo" }},
  issue: {{ number: 42 }}
}};
const github = {{
  rest: {{
    issues: {{
      getLabel: async (args) => calls.push(["getLabel", args]),
      createLabel: async (args) => calls.push(["createLabel", args]),
      removeLabel: async (args) => calls.push(["removeLabel", args]),
      addLabels: async (args) => calls.push(["addLabels", args])
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
    assert "types: [opened, edited, closed, reopened]" in text
    assert "actions: write" in text
    assert "issues: write" in text
    assert "<!-- aibast-workshop-feedback:v1 -->" in text
    assert "<!-- aibast-agi-progress:v1 -->" in text
    assert "<!-- aibast-agent-upvote:v1 -->" not in text
    assert "aibast-agi-achievement" not in text
    assert "||" in text
    assert "workshop-feedback" in text
    assert "needs-triage" in text
    assert "agent-upvote" not in text
    assert "agi-progress" in text
    assert "createLabel" in text
    assert "addLabels" in text
    assert "removeLabel" in text
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
    assert 'const isWorkshopFeedback = body.includes("<!-- aibast-workshop-feedback:v1 -->")' in text
    assert "const hasCurrentMarker = isWorkshopFeedback || isAgiProgress;" in text
    assert "const hasManagedLabel = currentNames.some((name) => managedNames.has(name));" in text
    assert "if (!hasCurrentMarker && !hasManagedLabel)" in text
    assert "return false;" in text
    assert ": [];" in text
    assert "if (labels.length)" in text
    assert "return true;" in text
    assert "if: steps.process-signal.outputs.result == 'true'" in text


def test_signal_classifier_behavior_is_fail_closed_and_removal_safe():
    unrelated = run_signal_classifier(body="ordinary issue", labels=("bug",))
    assert unrelated == {"result": False, "calls": []}

    stale = run_signal_classifier(
        body="marker removed",
        labels=({"name": "agi-progress"}, {"name": "bug"}),
    )
    assert stale["result"] is True
    assert [call[0] for call in stale["calls"]] == ["removeLabel"]
    assert stale["calls"][0][1]["name"] == "agi-progress"

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


def test_marker_removal_clears_stale_managed_labels_before_dispatch():
    text = WORKFLOW.read_text(encoding="utf-8")

    remove_position = text.index("await github.rest.issues.removeLabel")
    success_position = text.index("return true;")
    dispatch_position = text.index("await github.rest.actions.createWorkflowDispatch")
    assert remove_position < success_position < dispatch_position
    assert "if (!managedNames.has(name) || selectedNames.includes(name)) continue;" in text


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

    assert 'const isAgiProgress = body.includes("<!-- aibast-agi-progress:v1 -->")' in text
    assert '? ["agi-progress"]' in text
    assert '? ["workshop-feedback", "needs-triage"]' in text
    assert "Structured feedback submitted from an AIBAST workshop." in text
    assert "Opt-in public workshop achievement progress sync." in text
    assert "agent-upvote" not in text
    assert "AIBAST Beta workshop" not in text


def test_agi_progress_gets_only_agi_label_without_changing_other_signal_labels():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "const selectedNames = isAgiProgress" in text
    assert '? ["agi-progress"]' in text
    assert '? ["workshop-feedback", "needs-triage"]' in text
    assert 'const managedNames = new Set(Object.keys(definitions));' in text


def test_metrics_workflow_reads_issues_and_verifies_agi_profiles_and_scoring():
    text = METRICS_WORKFLOW.read_text(encoding="utf-8")

    assert "issues: read" in text
    assert "snapshot.get('agi', {})" in text
    assert "agi.get('schema') != 'aibast-agi/2.0'" in text
    assert "agi.get('profiles', [])" in text
    assert "agi.get('workshops', [])" in text
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
    assert "aibast-agi/1.0" not in text


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
