#!/usr/bin/env bash
# Retheme the whole library from the one palette source.
#
#   1. edit tools/design_tokens.py (add or pick a palette with PALETTE = "...")
#   2. bash scripts/retheme.sh
#   3. open docs/design-system.html and a few real pages, then open a PR to staging
#
# Everything downstream of the tokens is regenerated here so nothing has to be
# edited by hand: the stamped block on every published page (which also removes
# any page-local palette copy), the design-system preview, the metrics page
# contract, the impact report and the library API's page hashes. The audits and
# token tests run last. Solution source bundles are release assets built by CI.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export PYTHONPATH="${PYTHONPATH:-}:."

echo "== palette"; "$PY" tools/design_tokens.py --list
echo "== stamp every published page"; "$PY" scripts/apply_design_tokens.py
echo "== design-system preview"; "$PY" tools/design_tokens.py --preview
"$PY" scripts/apply_design_tokens.py >/dev/null   # the preview is a page too
echo "== metrics page contract"; "$PY" tools/audit_metrics_page.py --write-contract >/dev/null
echo "== impact report"; "$PY" scripts/build_impact_report.py --skip-pdf --no-record >/dev/null
echo "== library API (page hashes)"; "$PY" tools/build_library_api.py | tail -1
# Solution source bundles are release assets built by CI from these pages; they
# are never written into the tree (tests expect them absent), so nothing to do here.
echo "== audits"
"$PY" tools/audit_metrics_page.py | tail -3
"$PY" tools/audit_rapp_guide.py | tail -1
echo "== tests"
"$PY" -m pytest -q -p no:cacheprovider tests/test_design_tokens.py tests/test_metrics_page_theme.py tests/test_rapp_guide_theme.py tests/test_metrics_admin_setup.py tests/test_impact_report.py | tail -1
"$PY" scripts/apply_design_tokens.py --check
echo "Retheme complete. Review docs/design-system.html, then open a pull request to staging."
