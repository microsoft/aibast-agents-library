$ErrorActionPreference = "Stop"

$repo = if ($env:RAPP_FRONTIER_REPO) {
    $env:RAPP_FRONTIER_REPO
} else {
    "microsoft/aibast-agents-library"
}
if ($repo -notmatch "^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$") {
    throw "Invalid RAPP_FRONTIER_REPO: $repo"
}

$api = "https://api.github.com/repos/$repo"
$headers = @{ Accept = "application/vnd.github+json" }
$releases = Invoke-RestMethod -Headers $headers -Uri "$api/releases?per_page=30"
$release = @(
    $releases | Where-Object {
        -not $_.draft -and $_.tag_name.StartsWith("brainstem-beta-v")
    }
)[0]
if (-not $release) {
    throw "No published RAPP Brainstem Frontier release was found in $repo."
}

$tag = $release.tag_name
$commit = (
    Invoke-RestMethod -Headers $headers -Uri "$api/commits/$([uri]::EscapeDataString($tag))"
).sha.ToLowerInvariant()
if ($commit -notmatch "^[0-9a-f]{40}$") {
    throw "The Frontier release did not resolve to a full commit SHA."
}

if ($env:RAPP_FRONTIER_RESOLVE_ONLY -eq "1") {
    Write-Output "$repo $tag $commit"
    return
}

$env:BRAINSTEM_BETA_REPO_URL = "https://github.com/$repo.git"
$env:BRAINSTEM_BETA_RELEASE_TAG = $tag
$env:BRAINSTEM_BETA_RUNTIME_VERSION_URL =
    "https://raw.githubusercontent.com/$repo/$commit/rapp_brainstem/VERSION"
$env:BRAINSTEM_BETA_COMMIT = $commit
$env:BRAINSTEM_BETA_BOOTSTRAP_URL =
    "https://raw.githubusercontent.com/$repo/$commit/install.ps1"
$installer = Join-Path $env:TEMP "rapp-frontier-$commit.cmd"
try {
    Invoke-WebRequest `
        "https://raw.githubusercontent.com/$repo/$commit/beta/install.cmd" `
        -OutFile $installer `
        -UseBasicParsing
    & $installer
    if ($LASTEXITCODE -ne 0) {
        throw "Frontier installer exited with code $LASTEXITCODE."
    }
} finally {
    Remove-Item $installer -Force -ErrorAction SilentlyContinue
}
