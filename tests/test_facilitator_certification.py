"""Facilitator-only enrollment, certification, and Brainstem guide contract."""

import html
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from scripts import build_metrics

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
WORKSHOPS = build_metrics.build_workshop_catalog(REGISTRY)
FORM_DIR = ROOT / "solutions" / "_shared"
FACILITATOR_FORM = FORM_DIR / "AIBAST-Facilitator-Cohort-Registration.docx"
QUALIFICATION_FORM = FORM_DIR / "AIBAST-Badge-Qualification.docx"
WORKFLOW = ROOT / ".github/workflows/workshop-feedback.yml"


def cohort_body(**overrides):
    values = {
        "Schema": build_metrics.WORKSHOP_COHORT_SCHEMA,
        "Workshop": "account-intelligence",
        "Agent": "@aibast-agents-library/account-intelligence",
        "Cohort code": "AIBAST-20260811-DEMO",
        "Session date": "2026-08-11",
        "Attendee count": "24",
        "Private facilitator form submitted": "yes",
        "Public progress consent": "yes",
    }
    values.update(overrides)
    fields = "\n".join(
        f"- {name}: `{value}`" for name, value in values.items()
    )
    return (
        f"{build_metrics.WORKSHOP_COHORT_MARKER}\n"
        "## Public workshop cohort trigger\n\n"
        f"{fields}\n"
    )


def qualification_body(**overrides):
    values = {
        "Schema": build_metrics.BADGE_QUALIFICATION_SCHEMA,
        "Workshop": "account-intelligence",
        "Agent": "@aibast-agents-library/account-intelligence",
        "Cohort code": "AIBAST-20260811-DEMO",
        "Achievement progress issue": (
            "https://github.com/microsoft/aibast-agents-library/issues/123"
        ),
        "Private qualification form submitted": "yes",
        "Public profile consent": "yes",
    }
    values.update(overrides)
    fields = "\n".join(
        f"- {name}: `{value}`" for name, value in values.items()
    )
    return (
        f"{build_metrics.BADGE_QUALIFICATION_MARKER}\n"
        "## Public badge qualification trigger\n\n"
        f"{fields}\n"
    )


def docx_text(path):
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml").decode("utf-8")
    return " ".join(
        html.unescape(value)
        for value in re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml)
    )


def issue_bodies_from_field_guide(page):
    urls = re.findall(
        r'href="(https://github\.com/microsoft/'
        r'aibast-agents-library/issues/new\?[^"]+)"',
        page,
    )
    return [
        parse_qs(urlparse(html.unescape(url)).query)["body"][0]
        for url in urls
    ]


def test_every_canonical_field_guide_contains_the_gated_flow():
    assert len(WORKSHOPS) == 51
    for row in WORKSHOPS:
        package = ROOT / "solutions" / row["slug"]
        markdown = (package / "FIELD-GUIDE.md").read_text(encoding="utf-8")
        page = (package / "field-guide.html").read_text(encoding="utf-8")
        for token in (
            "aibast-facilitator-certification:v1",
            "Optional badge certification onboarding",
            "Facilitator crash course",
            "AIBAST-Facilitator-Cohort-Registration.docx",
            "AIBAST-Badge-Qualification.docx",
        ):
            assert token in markdown, f"{row['slug']} markdown missing {token}"
            assert token in page, f"{row['slug']} HTML missing {token}"
        canonical_installer = (
            "microsoft.github.io/aibast-agents-library/install.sh"
        )
        assert canonical_installer in markdown
        assert canonical_installer in page
        assert "kody-w.github.io/rapp-installer" not in markdown
        assert "raw.githubusercontent.com/kody-w/rapp-installer" not in markdown
        assert "claim -> test -> verify" in markdown
        assert "claim -&gt; test -&gt; verify" in page


def test_certification_content_does_not_leak_into_workshops_or_public_entry_pages():
    forbidden = (
        "aibast-facilitator-certification:v1",
        "aibast-workshop-cohort:v1",
        "aibast-badge-qualification:v1",
        "AIBAST-Facilitator-Cohort-Registration.docx",
        "AIBAST-Badge-Qualification.docx",
    )
    public_entry_pages = (
        ROOT / "index.html",
        ROOT / "library.html",
        ROOT / "achievements.html",
    )
    for path in public_entry_pages:
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{path}: leaked {token}"
    for row in WORKSHOPS:
        package = ROOT / "solutions" / row["slug"]
        for filename in ("quest.html", "manual-tutorial.html"):
            text = (package / filename).read_text(encoding="utf-8")
            for token in forbidden:
                assert token not in text, (
                    f"{row['slug']}/{filename}: leaked {token}"
                )


def test_import_ready_forms_exist_and_contain_only_the_expected_questions():
    for path in (FACILITATOR_FORM, QUALIFICATION_FORM):
        assert path.exists()
        assert path.read_bytes().startswith(b"PK")
        assert path.stat().st_size < 10 * 1024 * 1024
    facilitator = docx_text(FACILITATOR_FORM)
    qualification = docx_text(QUALIFICATION_FORM)
    for token in (
        "Microsoft corporate alias",
        "MSIX ID",
        "GitHub username used to run and report the workshop",
        "Public non-identifying cohort code",
        "Candidate GitHub usernames supplied for reviewer matching",
    ):
        assert token in facilitator
    for token in (
        "GitHub username",
        "Public GitHub achievement-progress issue URL",
        "Which locked case IDs did you complete",
        "What determines whether a locked workshop case passes",
        "Candidate attestation",
    ):
        assert token in qualification
    assert "Open text response" not in facilitator
    assert "Open text response" not in qualification


def test_every_source_bundle_contains_the_linked_forms_templates():
    expected = {
        "solutions/_shared/AIBAST-Facilitator-Cohort-Registration.docx",
        "solutions/_shared/AIBAST-Badge-Qualification.docx",
    }
    for row in WORKSHOPS:
        package = ROOT / "solutions" / row["slug"]
        manifest = json.loads(
            (package / "export-manifest.json").read_text(encoding="utf-8")
        )
        manifest_paths = {item["path"] for item in manifest["files"]}
        assert expected <= manifest_paths
        bundle = ROOT / manifest["bundle"]["path"]
        with zipfile.ZipFile(bundle) as archive:
            assert expected <= set(archive.namelist())


def test_generated_issue_triggers_are_public_safe_and_strictly_shaped():
    page = (
        ROOT / "solutions/account-intelligence/field-guide.html"
    ).read_text(encoding="utf-8")
    bodies = issue_bodies_from_field_guide(page)
    assert len(bodies) == 2
    cohort = next(
        body for body in bodies
        if body.startswith(build_metrics.WORKSHOP_COHORT_MARKER)
    )
    qualification = next(
        body for body in bodies
        if body.startswith(build_metrics.BADGE_QUALIFICATION_MARKER)
    )
    for body in bodies:
        for private_field in (
            "- MSIX:",
            "- Microsoft alias:",
            "- Email:",
            "- Customer:",
            "- Organization:",
            "- Roster:",
            "- Test answer:",
            "- Token:",
        ):
            assert private_field not in body
    assert "REPLACE-WITH-PUBLIC-CODE" in cohort
    assert "REPLACE-WITH-PUBLIC-CODE" in qualification


def test_strict_parsers_accept_valid_public_safe_claims():
    catalog = WORKSHOPS
    cohort = build_metrics.parse_workshop_cohort_claim(
        cohort_body(),
        catalog,
    )
    qualification = build_metrics.parse_badge_qualification_claim(
        qualification_body(),
        catalog,
    )
    assert cohort == {
        "workshop": "account-intelligence",
        "agent": "@aibast-agents-library/account-intelligence",
        "cohort_code": "AIBAST-20260811-DEMO",
        "session_date": "2026-08-11",
        "attendee_count": 24,
    }
    assert qualification == {
        "workshop": "account-intelligence",
        "agent": "@aibast-agents-library/account-intelligence",
        "cohort_code": "AIBAST-20260811-DEMO",
        "achievement_issue_url": (
            "https://github.com/microsoft/aibast-agents-library/issues/123"
        ),
    }


def test_strict_parsers_reject_placeholders_private_fields_and_bad_shapes():
    catalog = WORKSHOPS
    assert build_metrics.parse_workshop_cohort_claim(
        cohort_body(**{"Cohort code": "REPLACE-WITH-PUBLIC-CODE"}),
        catalog,
    ) is None
    assert build_metrics.parse_workshop_cohort_claim(
        cohort_body(**{"Attendee count": "zero"}),
        catalog,
    ) is None
    assert build_metrics.parse_badge_qualification_claim(
        qualification_body(
            **{
                "Achievement progress issue":
                    "https://github.com/other/repo/issues/1",
            }
        ),
        catalog,
    ) is None
    for leaked_field in (
        "- MSIX: `123456`\n",
        "* Email: `person@example.test`\n",
        "+ Token: `secret`\n",
        "1. Customer: `Contoso`\n",
        "> Email: `person@example.test`\n",
        "• Organization: `Contoso`\n",
        "Email:person@example.test\n",
        "* MSIX:123456\n",
        "**Email**: person@example.test\n",
        "`MSIX`: 123456\n",
        "<strong>Customer</strong>: Contoso\n",
        "&bull; Email: person@example.test\n",
        "&lt;strong&gt;Email&lt;/strong&gt;: person@example.test\n",
        "&#8226; MSIX: 123456\n",
        "&#x2022; Token: secret\n",
        "Email&colon; person@example.test\n",
        "F\u200Boo: hidden\n",
        "<!-- Email: person@example.test -->\n",
    ):
        leaked = cohort_body() + leaked_field
        assert build_metrics.parse_workshop_cohort_claim(
            leaked,
            catalog,
        ) is None


def test_aggregation_counts_only_human_verified_labels_and_stays_public_safe():
    issues = [
        {
            "number": 1,
            "body": cohort_body(),
            "user": {"login": "Facilitator-One"},
            "labels": [{"name": build_metrics.WORKSHOP_COHORT_LABEL}],
        },
        {
            "number": 2,
            "body": cohort_body(**{"Cohort code": "AIBAST-20260812-DEMO"}),
            "user": {"login": "Facilitator-One"},
            "labels": [
                {"name": build_metrics.WORKSHOP_COHORT_LABEL},
                {"name": build_metrics.COHORT_VERIFIED_LABEL},
            ],
        },
        {
            "number": 3,
            "body": qualification_body(),
            "user": {"login": "Candidate-One"},
            "labels": [{"name": build_metrics.BADGE_QUALIFICATION_LABEL}],
        },
        {
            "number": 4,
            "body": qualification_body(
                **{"Cohort code": "AIBAST-20260812-DEMO"}
            ),
            "user": {"login": "Candidate-One"},
            "labels": [
                {"name": build_metrics.BADGE_QUALIFICATION_LABEL},
                {"name": build_metrics.BADGE_QUALIFIED_LABEL},
            ],
        },
        {
            "number": 5,
            "body": qualification_body(
                **{"Cohort code": "AIBAST-20260813-DEMO"}
            ),
            "user": {"login": "Candidate-One"},
            "labels": [
                {"name": build_metrics.BADGE_QUALIFICATION_LABEL},
                {"name": build_metrics.BADGE_QUALIFIED_LABEL},
            ],
        },
    ]
    result = build_metrics.group_workshop_certification(
        issues,
        WORKSHOPS,
        as_of="2026-08-11T16:00:00Z",
    )
    assert result["totals"] == {
        "cohort_submissions": 2,
        "verified_cohorts": 1,
        "facilitators": 1,
        "attendees_reported": 24,
        "qualification_submissions": 3,
        "qualified_modules": 1,
        "qualified_profiles": 1,
    }
    assert result["facilitators"] == [
        {
            "login": "Facilitator-One",
            "verified_cohorts": 1,
            "attendees_reported": 24,
            "workshops": ["account-intelligence"],
        }
    ]
    assert result["candidates"] == [
        {
            "login": "Candidate-One",
            "qualified_modules": 1,
            "workshops": ["account-intelligence"],
        }
    ]
    assert result["coverage"]["diagnostics"]["duplicate_submissions"] == 1
    serialized = json.dumps(result)
    for private_value in (
        "customer name",
        "private@example",
        "AIBAST-20260812-DEMO",
        "/issues/123",
    ):
        assert private_value not in serialized


def test_workflow_stamps_closes_and_preserves_manual_review_gates():
    text = WORKFLOW.read_text(encoding="utf-8")
    for token in (
        "aibast-workshop-cohort:v1",
        "aibast-badge-qualification:v1",
        "workshop-cohort",
        "badge-qualification",
        "needs-private-review",
        "cohort-verified",
        "badge-qualified",
        "createComment",
        'state: "closed"',
        'state_reason: "completed"',
        "Closed issues remain in the public, state=all aggregation ledger.",
    ):
        assert token in text
    assert "automaticallyManagedNames" in text
    assert 'types: [opened, edited, closed, reopened, labeled, unlabeled]' in text
