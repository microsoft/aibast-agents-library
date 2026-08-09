from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/workshop-feedback.yml"


def test_workshop_feedback_workflow_detects_structured_signal():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "issues:" in text
    assert "types: [opened, edited, reopened]" in text
    assert "issues: write" in text
    assert "<!-- aibast-workshop-feedback:v1 -->" in text
    assert "<!-- aibast-agent-upvote:v1 -->" in text
    assert "||" in text
    assert "workshop-feedback" in text
    assert "needs-triage" in text
    assert "agent-upvote" in text
    assert "createLabel" in text
    assert "addLabels" in text
    assert "removeLabel" in text


def test_workflow_applies_signal_specific_labels_and_descriptions():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert 'const isAgentUpvote = body.includes("<!-- aibast-agent-upvote:v1 -->")' in text
    assert '? ["agent-upvote"]' in text
    assert ': ["workshop-feedback", "needs-triage"]' in text
    assert "Structured feedback submitted from an AIBAST workshop." in text
    assert "Public community preference signal for an AIBAST library agent." in text
    assert "AIBAST Beta workshop" not in text


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

    assert quest.count('data-report-location=') == 12
    assert manual.count('data-report-location=') == 20
