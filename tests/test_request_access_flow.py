"""The access flow recipe keeps the one rule that makes it safe.

``automation/request-access-flow/`` describes a flow that grants SharePoint
access from a form submission. The form takes a typed email address, which
proves nothing, so the recipe grants against the directory lookup instead and
mails the directory address rather than the typed one.

That is the whole safety property, and it is exactly the detail a later
simplification would remove. These tests hold it in place:

* the recipe never decides anything by matching an email domain;
* the grant and the notification both follow the directory result;
* the failure path notifies a person and grants nothing;
* no tenant value is committed, and the local settings file stays ignored.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FLOW = ROOT / "automation" / "request-access-flow"
README = (FLOW / "README.md").read_text(encoding="utf-8")
# Prose wraps; assertions about it must not depend on where.
PROSE = re.sub(r"\s+", " ", README)
# Addresses written to illustrate the attack, not to name anyone.
ILLUSTRATIVE = ("someone@microsoft.com", "not-a-real-person@microsoft.com")
SETTINGS = json.loads((FLOW / "settings.example.json").read_text(encoding="utf-8"))
REQUEST_PAGE = (ROOT / "request-info.html").read_text(encoding="utf-8")


def test_the_recipe_never_decides_by_matching_a_domain():
    # The obvious wrong build: trust the typed address because it ends in the
    # right domain. If this ever appears as an instruction, the door is open.
    lowered = PROSE.lower()
    for pattern in (
        r"endswith\s*\(\s*[^)]*@",
        r"contains\s*\(\s*[^)]*'@microsoft\.com'",
        r"if the (typed |submitted )?(domain|address) (is|ends|matches)[^.]*grant",
    ):
        assert not re.search(pattern, lowered), f"the recipe grants on a domain match: {pattern}"


def test_the_grant_follows_the_directory_not_the_form():
    assert "@body('Resolve_in_the_directory')?['id']" in README, "the grant does not use the resolved object id"
    # The composed form answer may be used for the lookup, and for nothing else.
    grant_section = README[README.index('"Add user to group"') : README.index('"Send an email (V2)", named `Tell the employee`')]
    assert "Requested_address" not in grant_section, "the form answer reaches the grant"


def test_the_confirmation_goes_to_the_directory_address():
    assert "@body('Resolve_in_the_directory')?['mail']" in README
    assert "never `outputs('Requested_address')`" in PROSE
    assert "It does not email the submitted address. Ever." in PROSE


def test_the_failure_path_asks_a_person_and_grants_nothing():
    assert "Ask a human" in PROSE
    assert "No grant happens on this branch" in PROSE
    assert "ownerMailbox" in SETTINGS


def test_the_access_model_stays_read_only_and_revocable():
    lowered = PROSE.lower()
    assert "do not grant anything above read" in lowered
    assert "it does not remove access" in lowered, "removal must stay deliberate"
    assert "does not create the group" in lowered, "the flow must not invent an access boundary"


def test_the_recipe_tells_the_builder_to_verify_the_dangerous_case():
    # A flow can report success and have granted the wrong thing.
    assert "not-a-real-person@microsoft.com" in PROSE
    assert "not by reading the run history" in PROSE


def test_no_tenant_value_is_committed():
    for key, value in SETTINGS.items():
        if key in ("$comment", "schema", "notes"):
            continue
        assert value.startswith("PLACEHOLDER_"), f"{key} carries a real value"
    for blob, where in ((README, "README.md"), (json.dumps(SETTINGS), "settings.example.json")):
        assert "sharepoint.com" not in blob.lower(), f"{where} names a tenant site"
        for example in ILLUSTRATIVE:
            blob = blob.replace(example, "")
        assert not re.search(r"[\w.+-]+@microsoft\.com", blob), (
            f"{where} carries a real-looking internal address"
        )


def test_the_local_settings_file_is_ignored():
    ignored = subprocess.run(
        ["git", "check-ignore", "automation/request-access-flow/settings.local.json"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert ignored.returncode == 0, "settings.local.json would be committed"
    assert not (FLOW / "settings.local.json").exists(), "a local settings file is sitting in the tree"


def test_the_request_page_says_what_happens_next():
    assert "What happens after you submit." in REQUEST_PAGE
    assert "directory record" in REQUEST_PAGE
    assert "reviewed by a person" in REQUEST_PAGE
