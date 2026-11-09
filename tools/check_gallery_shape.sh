#!/usr/bin/env bash
# Outbound compatibility gate: run the Copilot Studio Gallery's OWN submission checker (pinned in
# tools/gallery_contract.json) against this repository's submissions/ tree. Read-only toward the
# gallery: it clones, never pushes. Exit 0 = every submission would be accepted by their checker.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONTRACT="$ROOT/tools/gallery_contract.json"
REPO=$(python3 -c "import json;print(json.load(open('$CONTRACT'))['repository'])")
COMMIT=$(python3 -c "import json;print(json.load(open('$CONTRACT'))['commit'])")
WORK="${GALLERY_CHECKER_DIR:-$(mktemp -d)}"
if [ ! -d "$WORK/.git" ]; then
  git clone --quiet --filter=blob:none "$REPO" "$WORK"
fi
git -C "$WORK" fetch --quiet origin "$COMMIT" 2>/dev/null || true
git -C "$WORK" checkout --quiet "$COMMIT"
( cd "$WORK" && npm ci --silent --ignore-scripts )
cat > "$WORK/.aibast-check.mts" <<JS
import { importSubmissions } from "./scripts/import-submissions.ts";
const report: any = await importSubmissions({ root: process.env.AIBAST_ROOT, check: true });
const errors = Object.entries(report.errors || {});
console.log(\`gallery checker \${process.env.GALLERY_COMMIT.slice(0, 8)}: \${report.imported.length} submissions accepted, \${errors.length} with errors\`);
for (const [slug, list] of errors) console.log(\`::error::\${slug}: \${JSON.stringify(list)}\`);
process.exit(errors.length ? 1 : 0);
JS
( cd "$WORK" && AIBAST_ROOT="$ROOT" GALLERY_COMMIT="$COMMIT" npx tsx .aibast-check.mts )
