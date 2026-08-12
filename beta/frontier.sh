#!/usr/bin/env bash
set -euo pipefail

repo="${RAPP_FRONTIER_REPO:-microsoft/aibast-agents-library}"
case "$repo" in
    *[!A-Za-z0-9_.\/-]*|*/*/*|/*|*/|"")
        echo "Invalid RAPP_FRONTIER_REPO: $repo" >&2
        exit 2
        ;;
esac

api="https://api.github.com/repos/$repo"
tag=$(
    curl -fsSL -H "Accept: application/vnd.github+json" "$api/releases?per_page=30" \
        | sed -n 's/^[[:space:]]*"tag_name":[[:space:]]*"\(brainstem-beta-v[^"]*\)".*/\1/p' \
        | head -n 1
)
[ -n "$tag" ] || {
    echo "No published RAPP Brainstem Frontier release was found in $repo." >&2
    exit 3
}

commit=$(
    curl -fsSL -H "Accept: application/vnd.github+json" "$api/commits/$tag" \
        | sed -n 's/^[[:space:]]*"sha":[[:space:]]*"\([0-9a-fA-F]\{40\}\)".*/\1/p' \
        | head -n 1 \
        | tr 'A-F' 'a-f'
)
case "$commit" in
    *[!0-9a-f]*|"")
        echo "The Frontier release did not resolve to a full commit SHA." >&2
        exit 4
        ;;
esac
[ "${#commit}" -eq 40 ] || {
    echo "The Frontier release did not resolve to a full commit SHA." >&2
    exit 4
}

if [ "${RAPP_FRONTIER_RESOLVE_ONLY:-0}" = "1" ]; then
    printf '%s %s %s\n' "$repo" "$tag" "$commit"
    exit 0
fi

curl -fsSL "https://raw.githubusercontent.com/$repo/$commit/beta/install.sh" \
    | BRAINSTEM_BETA_REPO_URL="https://github.com/$repo.git" \
      BRAINSTEM_BETA_COMMIT="$commit" bash
