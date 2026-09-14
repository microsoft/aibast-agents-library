import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_REPOSITORY,
  DownloadCenterError,
  RELEASE_MANIFEST_FENCE,
  RELEASE_MANIFEST_SCHEMA,
  analyzePackagedDownloads,
  applyReleaseSummary,
  buildBootstrapDownloads,
  buildReleaseTransaction,
  claimDownloadCenterInitialization,
  copyText,
  detectArchitecture,
  discoverRelease,
  fetchGitHubJson,
  formatBytes,
  goldenPathUrl,
  handleDownloadSubmit,
  initializeDownloadCenter,
  orderDownloadsForPlatform,
  parseReleaseManifest,
  platformRecommendation,
  presentBinaryUnavailable,
  presentReleaseFailure,
  releaseFileSummary,
  repositoryDocumentUrl,
  resolveDownloadContext,
  safeReleaseAssetUrl,
  selectRelease,
  setFunctionalLink,
  showDownloadDialog,
  verifyReleaseManifestAsset,
  windowsSupportLabel,
} from "../download-center.js";

const betaRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repository = "octo/frontier";
const tag = "brainstem-beta-v1.2.3";
const commit = "a".repeat(40);
const artifactSha = "b".repeat(64);

function asset(name, options = {}) {
  const size = Object.hasOwn(options, "size") ? options.size : 4_194_304;
  const state = Object.hasOwn(options, "state") ? options.state : "uploaded";
  const url = Object.hasOwn(options, "url")
    ? options.url
    : `https://github.com/${repository}/releases/download/${tag}/${encodeURIComponent(name)}`;
  const digest = Object.hasOwn(options, "digest")
    ? options.digest
    : `sha256:${artifactSha}`;
  return {
    name,
    size,
    state,
    digest,
    browser_download_url: url,
  };
}

function release(overrides = {}) {
  return {
    id: 20,
    tag_name: tag,
    draft: false,
    prerelease: true,
    immutable: true,
    published_at: "2026-09-04T20:00:00Z",
    assets: [],
    body: "",
    ...overrides,
  };
}

function manifestEntry(releaseAsset, overrides = {}) {
  const platform = /\.dmg$/i.test(releaseAsset.name) ? "macos" : "windows";
  const architecture = /arm64|aarch64/i.test(releaseAsset.name)
    ? "arm64"
    : /universal/i.test(releaseAsset.name)
      ? "universal"
      : "x64";
  const base = {
    filename: releaseAsset.name,
    platform,
    architecture,
    size: releaseAsset.size,
    sha256: artifactSha,
    signing: {
      status: "verified",
      identity: platform === "macos"
        ? "Developer ID Application: Contoso Corporation (ABCDE12345)"
        : "Contoso Corporation",
    },
    runtime: {
      compatible: true,
      version: "1.2.3",
      commit,
      node: ">=24.19.0 <26",
      electron: "43.0.0",
    },
    gate: {
      status: "passed",
      name: "package-gate",
      commit,
      run_url: `https://github.com/${repository}/actions/runs/123456`,
    },
  };
  return {
    ...base,
    ...overrides,
    signing: { ...base.signing, ...overrides.signing },
    runtime: { ...base.runtime, ...overrides.runtime },
    gate: { ...base.gate, ...overrides.gate },
  };
}

function manifestFor(releaseAssets, overrides = {}) {
  const base = {
    schema: RELEASE_MANIFEST_SCHEMA,
    release: {
      tag,
      commit,
      version: "1.2.3",
    },
    artifacts: releaseAssets.map((releaseAsset) => manifestEntry(releaseAsset)),
  };
  return {
    ...base,
    ...overrides,
    release: { ...base.release, ...overrides.release },
    artifacts: overrides.artifacts || base.artifacts,
  };
}

function manifestBody(manifest) {
  return [
    "Release notes.",
    "",
    `\`\`\`${RELEASE_MANIFEST_FENCE}`,
    JSON.stringify(manifest),
    "\`\`\`",
  ].join("\n");
}

function manifestAsset(manifest) {
  const contents = `${JSON.stringify(manifest)}\n`;
  const name =
    `RAPP-Brainstem-Frontier-${manifest.release.version}-binary-manifest.json`;
  return asset(name, {
    size: Buffer.byteLength(contents),
    digest:
      `sha256:${createHash("sha256").update(contents).digest("hex")}`,
    url:
      `https://github.com/${repository}/releases/download/`
      + `${manifest.release.tag}/${name}`,
  });
}

function manifestResponse(manifest) {
  return new Response(`${JSON.stringify(manifest)}\n`, {
    status: 200,
    headers: { "content-type": "application/json" },
  });
}

function analyze(releaseAssets, manifest = manifestFor(releaseAssets)) {
  return analyzePackagedDownloads(
    release({ assets: releaseAssets }),
    {
      repository,
      commit,
      version: "1.2.3",
      manifest,
    },
  );
}

function jsonResponse(value, { status = 200, headers = {} } = {}) {
  return new Response(JSON.stringify(value), { status, headers });
}

function copyFixture({ writeText, execCommand = () => false } = {}) {
  const timers = [];
  const textarea = {
    style: {},
    removed: false,
    selected: false,
    setAttribute() {},
    select() {
      this.selected = true;
    },
    remove() {
      this.removed = true;
    },
  };
  const attributes = new Map();
  return {
    context: {
      documentObject: {
        createElement: () => textarea,
        body: { appendChild() {} },
        execCommand,
      },
      navigatorObject: {
        clipboard: writeText ? { writeText } : undefined,
      },
      windowObject: {
        setTimeout(callback) {
          timers.push(callback);
        },
      },
    },
    button: {
      textContent: "Copy command",
      dataset: {},
      setAttribute(name, value) {
        attributes.set(name, value);
      },
      removeAttribute(name) {
        attributes.delete(name);
      },
    },
    status: { textContent: "" },
    textarea,
    timers,
    attributes,
  };
}

test("Microsoft defaults and static links stay canonical while forks remain generic", () => {
  assert.equal(DEFAULT_REPOSITORY, "microsoft/aibast-agents-library");
  for (const location of [
    { hostname: "localhost", pathname: "/beta/" },
    { hostname: "microsoft.github.io", pathname: "/aibast-agents-library/beta/" },
  ]) {
    const context = resolveDownloadContext(location);
    assert.equal(context.repository, DEFAULT_REPOSITORY);
    assert.equal(context.trusted, true);
  }
  const page = readFileSync(path.join(betaRoot, "index.html"), "utf8");
  const repositoryLinks = [...page.matchAll(/href="https:\/\/github\.com\/([^"]+)"/g)];
  assert.ok(repositoryLinks.length > 0);
  for (const [, target] of repositoryLinks) {
    assert.ok(target.startsWith(`${DEFAULT_REPOSITORY}/`), target);
  }
});

test("public repository authority is origin-bound and localhost overrides are untrusted", () => {
  assert.deepEqual(
    resolveDownloadContext({
      search: "?tag=brainstem-beta-v9.1.0",
      hostname: "contoso.github.io",
      pathname: "/frontier-fork/beta/",
    }),
    {
      repository: "contoso/frontier-fork",
      requestedTag: "brainstem-beta-v9.1.0",
      trusted: true,
      authority: "github-pages-origin",
      warning: "",
    },
  );

  assert.deepEqual(
    resolveDownloadContext({
      search: "?repo=contoso/frontier-fork",
      hostname: "localhost",
      pathname: "/beta/",
    }),
    {
      repository: "contoso/frontier-fork",
      requestedTag: null,
      trusted: false,
      authority: "localhost-override",
      warning:
        "LOCAL TEST ONLY — UNTRUSTED REPOSITORY contoso/frontier-fork. "
        + "Do not redistribute commands or downloads from this page.",
    },
  );

  assert.throws(
    () => resolveDownloadContext({
      search: "?repo=attacker/payload",
      hostname: "microsoft.github.io",
      pathname: "/aibast-agents-library/beta/",
    }),
    (error) => error.code === "PUBLIC_REPOSITORY_OVERRIDE",
  );
  assert.throws(
    () => resolveDownloadContext({
      search: "",
      hostname: "downloads.example.com",
      pathname: "/beta/",
    }),
    (error) => error.code === "AMBIGUOUS_DEPLOYMENT_ORIGIN",
  );
  assert.throws(
    () => resolveDownloadContext({
      search: "",
      hostname: "contoso.github.io",
      pathname: "/beta/",
    }),
    (error) => error.code === "AMBIGUOUS_DEPLOYMENT_PATH",
  );
  assert.throws(
    () => resolveDownloadContext({
      search: "?tag=v9.1.0",
      hostname: "contoso.github.io",
      pathname: "/frontier-fork/beta/",
    }),
    (error) => error.code === "INVALID_RELEASE_TAG",
  );
  assert.throws(
    () => resolveDownloadContext({
      search: "?repo=../payload",
      hostname: "localhost",
      pathname: "/beta/",
    }),
    (error) => error.code === "INVALID_REPOSITORY",
  );
});

test("release selection is deterministic and an explicit tag wins", () => {
  const older = release({
    id: 10,
    tag_name: "brainstem-beta-v1.0.0",
    published_at: "2026-08-01T00:00:00Z",
  });
  const newest = release({
    id: 30,
    tag_name: "brainstem-beta-v1.3.0",
    published_at: "2026-09-03T00:00:00Z",
  });
  const draft = release({
    id: 40,
    tag_name: "brainstem-beta-v2.0.0",
    draft: true,
    published_at: "2026-09-04T00:00:00Z",
  });
  const unrelated = release({
    id: 50,
    tag_name: "v99.0.0",
    published_at: "2026-09-05T00:00:00Z",
  });

  assert.equal(
    selectRelease([older, draft, unrelated, newest]).tag_name,
    newest.tag_name,
  );
  assert.equal(
    selectRelease([newest, older], { requestedTag: older.tag_name }).tag_name,
    older.tag_name,
  );
  assert.equal(selectRelease([draft, unrelated]), null);
});

test("release discovery executes the real API selection and commit validation", async () => {
  const olderTag = "brainstem-beta-v1.0.0";
  const olderAsset = asset("Frontier-1.0.0-win-x64.exe", {
    url: `https://github.com/${repository}/releases/download/${olderTag}/Frontier-1.0.0-win-x64.exe`,
  });
  const olderManifest = manifestFor([olderAsset], {
    release: { tag: olderTag, version: "1.0.0" },
    artifacts: [
      manifestEntry(olderAsset, {
        runtime: { version: "1.0.0" },
      }),
    ],
  });
  const calls = [];
  const selectedRelease = release({
    id: 10,
    tag_name: olderTag,
    published_at: "2026-08-01T00:00:00Z",
    assets: [olderAsset, manifestAsset(olderManifest)],
    body: manifestBody(olderManifest),
  });
  const fetchImpl = async (url, options) => {
    calls.push({ url, options });
    if (calls.length === 1) return jsonResponse(selectedRelease);
    if (url.includes("-binary-manifest.json")) {
      return manifestResponse(olderManifest);
    }
    return jsonResponse({ sha: commit.toUpperCase() });
  };

  const result = await discoverRelease({
    repository,
    requestedTag: olderTag,
    fetchImpl,
  });

  assert.equal(result.tag, olderTag);
  assert.equal(result.version, "1.0.0");
  assert.equal(result.commit, commit);
  assert.equal(result.packagedDownloads.length, 1);
  assert.equal(result.binaryAvailability.available, true);
  assert.equal(
    result.goldenPathUrl,
    `https://github.com/${repository}/blob/${olderTag}/beta/GOLDEN_PATH.md`,
  );
  assert.equal(
    calls[0].url,
    `https://api.github.com/repos/${repository}/releases/tags/${olderTag}`,
  );
  assert.equal(
    calls[1].url,
    `https://api.github.com/repos/${repository}/commits/${olderTag}`,
  );
  assert.equal(
    calls[2].url,
    manifestAsset(olderManifest).browser_download_url,
  );
  assert.equal(calls[0].options.headers.Accept, "application/vnd.github+json");
});

test("default discovery requests 100 releases and orders by published_at", async () => {
  const releases = Array.from({ length: 40 }, (_, index) => release({
    id: index + 1,
    tag_name: `brainstem-beta-v1.0.${index}`,
    published_at: new Date(Date.UTC(2026, 0, index + 1)).toISOString(),
  })).reverse();
  const expected = releases.at(-1);
  expected.published_at = "2027-01-01T00:00:00Z";
  const calls = [];
  const result = await discoverRelease({
    repository,
    fetchImpl: async (url) => {
      calls.push(url);
      return url.includes("/releases?")
        ? jsonResponse(releases)
        : jsonResponse({ sha: commit });
    },
  });

  assert.equal(result.tag, expected.tag_name);
  assert.equal(
    calls[0],
    `https://api.github.com/repos/${repository}/releases?per_page=100`,
  );
});

test("resolved fork packages and pinned identity reach the DOM transaction", async () => {
  const releaseAsset = asset("Frontier-win-x64.exe");
  const manifest = manifestFor([releaseAsset]);
  const selectedRelease = release({
    assets: [releaseAsset, manifestAsset(manifest)],
    body: manifestBody(manifest),
  });
  const context = resolveDownloadContext({
    search: `?tag=${tag}`,
    hostname: "octo.github.io",
    pathname: "/frontier/beta/",
  });
  const resolved = await discoverRelease({
    repository: context.repository,
    requestedTag: context.requestedTag,
    fetchImpl: async (url) => {
      if (url.includes("/releases/tags/")) return jsonResponse(selectedRelease);
      if (url.includes("-binary-manifest.json")) {
        return manifestResponse(manifest);
      }
      return jsonResponse({ sha: commit.toUpperCase() });
    },
  });
  const transaction = buildReleaseTransaction({
    context,
    release: resolved,
    locale: "en-US",
  });

  assert.equal(transaction.downloadItems[0].fileName, releaseAsset.name);
  const windowsSource = transaction.downloadItems.find(
    (item) => item.id === "source-windows",
  );
  assert.match(windowsSource.command, new RegExp(commit));
  assert.match(windowsSource.command, new RegExp(tag));
  assert.match(windowsSource.command, new RegExp(repository));

  const elements = Object.fromEntries(
    [
      "sourceLink",
      "guideLink",
      "goldenPathLink",
      "securityLink",
      "licenseLink",
      "releaseLinkTop",
      "releaseLinkBottom",
      "version",
      "date",
      "commit",
      "resolvedDate",
      "status",
      "statusDot",
      "error",
      "sourceStatus",
      "recoveryPanel",
    ].map((name) => [name, {
      textContent: "",
      href: "",
      title: "",
      className: "",
      hidden: true,
      setAttribute() {},
      removeAttribute() {},
    }]),
  );
  applyReleaseSummary(elements, transaction);
  assert.equal(elements.commit.textContent, commit.slice(0, 12));
  assert.match(elements.resolvedDate.textContent, new RegExp(repository));
  assert.match(elements.guideLink.href, new RegExp(`/blob/${tag}/beta/README\\.md$`));
  assert.match(elements.securityLink.href, new RegExp(`/blob/${tag}/SECURITY\\.md$`));
  assert.match(elements.licenseLink.href, new RegExp(`/blob/${tag}/LICENSE$`));
  assert.equal(elements.status.textContent, "Prerelease ready");
  assert.equal(elements.error.hidden, true);

  const localContext = resolveDownloadContext({
    search: `?repo=${repository}&tag=${tag}`,
    hostname: "localhost",
    pathname: "/beta/",
  });
  applyReleaseSummary(
    elements,
    buildReleaseTransaction({ context: localContext, release: resolved, locale: "en-US" }),
  );
  assert.equal(elements.status.textContent, "LOCAL TEST · UNTRUSTED REPOSITORY");
  assert.equal(elements.statusDot.className, "status-dot error");
  assert.match(elements.error.textContent, /LOCAL TEST ONLY — UNTRUSTED REPOSITORY/);

  assert.throws(
    () => buildReleaseTransaction({
      context,
      release: { ...resolved, commit: "not-a-commit" },
      locale: "en-US",
    }),
    (error) => error.code === "INVALID_RELEASE_TRANSACTION",
  );
});

test("only manifest-allowlisted packaged assets are promoted deterministically", () => {
  const validAssets = [
    asset("Frontier-2.0.0-mac-arm64.dmg"),
    asset("Frontier-2.0.0-win-x64.exe"),
    asset("Frontier-2.0.0-mac-x64.dmg"),
  ];
  const hostileAssets = [
    asset("Calculator-win-x64.exe"),
    asset("Frontier-2.0.0-mac-arm64.dmg.exe"),
    asset("Frontier-2.0.0-win-x64\u202Ecod.exe"),
    asset("Frontier-2.0.0-win-x64.exe.blockmap"),
  ];

  const first = analyze(
    [...validAssets, ...hostileAssets],
    manifestFor(validAssets),
  );
  const second = analyze(
    [...hostileAssets].reverse().concat([...validAssets].reverse()),
    manifestFor(validAssets, {
      artifacts: validAssets.map((item) => manifestEntry(item)).reverse(),
    }),
  );

  const expectedNames = [
    "Frontier-2.0.0-win-x64.exe",
    "Frontier-2.0.0-mac-x64.dmg",
    "Frontier-2.0.0-mac-arm64.dmg",
  ];
  assert.deepEqual(first.downloads.map((item) => item.fileName), expectedNames);
  assert.deepEqual(second.downloads.map((item) => item.fileName), expectedNames);
  assert.deepEqual(
    first.ignored.map((item) => item.fileName),
    hostileAssets.slice(0, 3).map((item) => item.name),
  );
  assert.deepEqual(
    second.ignored.map((item) => item.fileName).sort(),
    hostileAssets.slice(0, 3).map((item) => item.name).sort(),
  );
  assert.ok(first.downloads.every((item) => item.size === "4.0 MB"));
  assert.ok(first.downloads.every((item) => item.href.startsWith("https://github.com/")));
  assert.ok(first.downloads.every((item) => item.sha256 === artifactSha));
  assert.ok(first.downloads.every((item) => item.signingIdentity.includes("Contoso")));
});

test("hostile package names cannot enter the manifest allowlist", async (t) => {
  for (const fileName of [
    "../Frontier-win-x64.exe",
    "Frontier-mac-arm64.dmg.exe",
    "Frontier-win-x64\u202Ecod.exe",
    "CON.exe",
    "Frontier-uninstaller-x64.exe",
    "Frontier-unins000-x64.exe",
  ]) {
    await t.test(fileName, () => {
      const releaseAsset = asset(fileName);
      assert.throws(
        () => analyze([releaseAsset], manifestFor([releaseAsset])),
        (error) => error instanceof DownloadCenterError
          && error.code === "INVALID_RELEASE_MANIFEST"
          && /filename/.test(error.message),
      );
    });
  }

  const releaseAsset = asset("Frontier-win-x64.exe");
  const mismatchedCase = manifestFor([releaseAsset], {
    artifacts: [
      manifestEntry(releaseAsset, { filename: "frontier-win-x64.exe" }),
    ],
  });
  assert.throws(
    () => analyze([releaseAsset], mismatchedCase),
    /must match exactly one release asset/,
  );

  const redirectedName = asset("Frontier-win-x64.exe", {
    url: `https://github.com/${repository}/releases/download/${tag}/Other.exe`,
  });
  assert.throws(
    () => analyze([redirectedName], manifestFor([redirectedName])),
    /asset URL is invalid/,
  );

  const missingDigest = asset("Frontier-win-x64.exe", { digest: null });
  assert.throws(
    () => analyze([missingDigest], manifestFor([missingDigest])),
    /GitHub digest does not match/,
  );
});

test("every provenance binding fails closed on manifest mismatch", async (t) => {
  const releaseAsset = asset("Frontier-win-x64.exe");
  const cases = [
    ["release tag", (value) => { value.release.tag = "brainstem-beta-v9.9.9"; }],
    ["release commit", (value) => { value.release.commit = "c".repeat(40); }],
    ["release version", (value) => { value.release.version = "9.9.9"; }],
    ["platform", (value) => { value.artifacts[0].platform = "macos"; }],
    ["architecture", (value) => { value.artifacts[0].architecture = "arm64"; }],
    ["size", (value) => { value.artifacts[0].size += 1; }],
    ["SHA-256", (value) => { value.artifacts[0].sha256 = "c".repeat(64); }],
    ["signing status", (value) => { value.artifacts[0].signing.status = "unsigned"; }],
    ["signing identity", (value) => { value.artifacts[0].signing.identity = "unknown"; }],
    ["runtime flag", (value) => { value.artifacts[0].runtime.compatible = false; }],
    ["runtime version", (value) => { value.artifacts[0].runtime.version = "9.9.9"; }],
    ["runtime commit", (value) => { value.artifacts[0].runtime.commit = "c".repeat(40); }],
    ["runtime details", (value) => { value.artifacts[0].runtime.node = ""; }],
    ["runtime range", (value) => { value.artifacts[0].runtime.electron = "latest"; }],
    ["gate status", (value) => { value.artifacts[0].gate.status = "failed"; }],
    ["gate commit", (value) => { value.artifacts[0].gate.commit = "c".repeat(40); }],
    ["gate name", (value) => { value.artifacts[0].gate.name = "smoke"; }],
    ["gate URL", (value) => { value.artifacts[0].gate.run_url = "https://evil.example/run/1"; }],
  ];

  for (const [name, mutate] of cases) {
    await t.test(name, () => {
      const candidate = structuredClone(manifestFor([releaseAsset]));
      mutate(candidate);
      assert.throws(
        () => analyze([releaseAsset], candidate),
        (error) => error instanceof DownloadCenterError
          && error.code === "INVALID_RELEASE_MANIFEST",
      );
    });
  }

  const duplicateTupleAssets = [
    asset("Frontier-win-x64.exe"),
    asset("Frontier-portable-win-x64.exe"),
  ];
  assert.throws(
    () => analyze(duplicateTupleAssets),
    /platform\/architecture tuple windows:x64 is duplicated/,
  );
});

test("missing or invalid provenance falls back visibly to source bootstraps", async () => {
  const releaseAsset = asset("Frontier-win-x64.exe");
  const invalidManifest = manifestFor([releaseAsset]);
  invalidManifest.artifacts[0].gate.status = "failed";
  const candidates = [
    [release({ assets: [], body: "" }), "SOURCE_ONLY_RELEASE"],
    [release({ assets: [releaseAsset], body: "" }), "MISSING_RELEASE_MANIFEST"],
    [release({ assets: [releaseAsset], body: manifestBody(invalidManifest) }), "INVALID_RELEASE_MANIFEST"],
    [release({
      assets: [releaseAsset],
      body: `\`\`\`${RELEASE_MANIFEST_FENCE}\n{not json}\n\`\`\``,
    }), "INVALID_RELEASE_MANIFEST"],
  ];

  for (const [candidate, expectedCode] of candidates) {
    const result = await discoverRelease({
      repository,
      fetchImpl: async (url) => url.includes("/releases?")
        ? jsonResponse([candidate])
        : jsonResponse({ sha: commit }),
    });
    assert.equal(result.packagedDownloads.length, 0);
    assert.equal(result.binaryAvailability.available, false);
    assert.equal(result.binaryAvailability.code, expectedCode);
    const transaction = buildReleaseTransaction({
      context: {
        repository,
        trusted: true,
        warning: "",
      },
      release: result,
      locale: "en-US",
    });
    const sourceFallback = transaction.downloadItems;
    assert.deepEqual(
      orderDownloadsForPlatform(
        sourceFallback,
        "windows",
        "x64",
      ).map((item) => item.fileName),
      ["install.cmd"],
    );

    const windowsSource = sourceFallback.find((item) => item.id === "source-windows");
    assert.equal(windowsSource.downloadable, true);
    assert.match(windowsSource.downloadHref, /^data:text\/plain;charset=utf-8,/);
    assert.match(decodeURIComponent(windowsSource.downloadHref), new RegExp(commit));

    const elements = {
      error: { textContent: "", hidden: true },
      sourceStatus: { textContent: "", hidden: true },
    };
    presentBinaryUnavailable(elements, result.binaryAvailability);
    if (expectedCode === "SOURCE_ONLY_RELEASE") {
      assert.equal(elements.error.hidden, true);
      assert.equal(elements.sourceStatus.hidden, false);
      assert.match(elements.sourceStatus.textContent, /source-only/i);
      assert.doesNotMatch(elements.sourceStatus.textContent, /provenance manifest/i);
    } else {
      assert.equal(elements.error.hidden, false);
      assert.match(elements.error.textContent, /Packaged installers are unavailable/);
    }
  }

  assert.throws(
    () => parseReleaseManifest(
      `\`\`\`${RELEASE_MANIFEST_FENCE}\n{not json}\n\`\`\``,
    ),
    (error) => error.code === "INVALID_RELEASE_MANIFEST",
  );
});

test("binary trust requires immutable release and byte-identical manifest asset", async () => {
  const binary = asset("Frontier-win-x64.exe");
  const manifest = manifestFor([binary]);
  const attachedManifest = manifestAsset(manifest);
  const candidate = release({
    assets: [binary, attachedManifest],
    body: manifestBody(manifest),
  });

  assert.deepEqual(
    await verifyReleaseManifestAsset(candidate, {
      repository,
      version: "1.2.3",
      fetchImpl: async () => manifestResponse(manifest),
    }),
    manifest,
  );
  assert.throws(
    () => analyzePackagedDownloads(
      { ...candidate, immutable: false },
      { repository, commit, version: "1.2.3", manifest },
    ),
    /immutable GitHub release/,
  );
  await assert.rejects(
    () => verifyReleaseManifestAsset(
      { ...candidate, immutable: false },
      {
        repository,
        version: "1.2.3",
        fetchImpl: async () => manifestResponse(manifest),
      },
    ),
    /immutable GitHub release/,
  );
  await assert.rejects(
    () => verifyReleaseManifestAsset(candidate, {
      repository,
      version: "1.2.3",
      fetchImpl: async () => new Response(
        `${JSON.stringify(manifest, null, 2)}\n`,
        { status: 200 },
      ),
    }),
    /fenced release manifest and attached manifest asset differ/,
  );
  await assert.rejects(
    () => verifyReleaseManifestAsset({
      ...candidate,
      assets: [
        binary,
        { ...attachedManifest, digest: `sha256:${"0".repeat(64)}` },
      ],
    }, {
      repository,
      version: "1.2.3",
      fetchImpl: async () => manifestResponse(manifest),
    }),
    /does not match its GitHub SHA-256 digest/,
  );
});

test("mutable packaged releases fall back to source-only discovery", async () => {
  const binary = asset("Frontier-win-x64.exe");
  const manifest = manifestFor([binary]);
  const candidate = release({
    immutable: false,
    assets: [binary, manifestAsset(manifest)],
    body: manifestBody(manifest),
  });
  const result = await discoverRelease({
    repository,
    fetchImpl: async (url) => url.includes("/releases?")
      ? jsonResponse([candidate])
      : jsonResponse({ sha: commit }),
  });
  assert.equal(result.packagedDownloads.length, 0);
  assert.equal(result.binaryAvailability.available, false);
  assert.equal(result.binaryAvailability.code, "INVALID_RELEASE_MANIFEST");
  assert.match(result.binaryAvailability.detail, /immutable GitHub release/);
});

test("architecture-aware ordering recommends a compatible package before source fallback", () => {
  const packagedAssets = [
    asset("Frontier-win-x64.exe"),
    asset("Frontier-mac-x64.dmg"),
    asset("Frontier-mac-arm64.dmg"),
    asset("Frontier-mac-universal.dmg"),
  ];
  const { downloads } = analyze(packagedAssets);
  const catalog = [
    ...downloads,
    ...buildBootstrapDownloads({
      repository,
      tag,
      commit,
    }),
  ];

  assert.deepEqual(
    orderDownloadsForPlatform(catalog, "windows", "arm64").map((item) => item.fileName),
    [],
  );
  assert.deepEqual(
    orderDownloadsForPlatform(catalog, "windows", "x64").map((item) => item.fileName),
    ["Frontier-win-x64.exe", "install.cmd"],
  );
  assert.doesNotMatch(
    platformRecommendation(catalog, "windows", "x64"),
    /Windows 11 x64 x64/,
  );
  assert.doesNotMatch(
    downloads.find((item) => item.platform === "windows").description,
    /Windows 11 x64 x64/,
  );
  assert.deepEqual(
    orderDownloadsForPlatform(catalog, "linux", "arm64").map((item) => item.fileName),
    ["install.sh"],
  );
  assert.deepEqual(
    orderDownloadsForPlatform(catalog, "macos", "arm64").map((item) => item.fileName),
    ["Frontier-mac-arm64.dmg", "Frontier-mac-universal.dmg", "install.sh"],
  );
  assert.deepEqual(
    orderDownloadsForPlatform(catalog, "macos", "x64").map((item) => item.fileName),
    ["Frontier-mac-x64.dmg", "Frontier-mac-universal.dmg", "install.sh"],
  );
  assert.throws(
    () => orderDownloadsForPlatform(catalog, "windows"),
    (error) => error.code === "INVALID_ARCHITECTURE",
  );
});

test("release summaries keep every filename paired with its size", () => {
  const packagedAssets = [
    asset("Frontier-win-x64.exe", { size: 5_242_880 }),
    asset("Frontier-mac-arm64.dmg", { size: 7_340_032 }),
  ];
  const manifest = manifestFor(packagedAssets, {
    artifacts: packagedAssets.map((item) => manifestEntry(item, { size: item.size })),
  });
  const downloads = analyze(packagedAssets, manifest).downloads;
  assert.deepEqual(releaseFileSummary(downloads), [
    { fileName: "Frontier-win-x64.exe", size: "5.0 MB" },
    { fileName: "Frontier-mac-arm64.dmg", size: "7.0 MB" },
  ]);
  assert.throws(
    () => releaseFileSummary([{ fileName: "missing-size.exe", size: "" }]),
    (error) => error.code === "INVALID_RELEASE_FILES",
  );
});

test("Windows ARM64 packages and claims remain disabled", () => {
  const x64Asset = asset("Frontier-win-x64.exe");
  const arm64Asset = asset("Frontier-win-arm64.exe");
  const x64Only = analyze([x64Asset]).downloads;

  assert.equal(windowsSupportLabel(x64Only), "Windows 11 x64");
  assert.doesNotMatch(windowsSupportLabel(x64Only), /ARM64/);
  assert.throws(
    () => analyze([arm64Asset]),
    /architecture is invalid/,
  );
  assert.match(
    platformRecommendation(x64Only, "windows", "arm64"),
    /Windows ARM64 is not supported/,
  );
  const pageSource = readFileSync(path.join(betaRoot, "index.html"), "utf8");
  assert.doesNotMatch(pageSource, /Windows 11 x64 or ARM64/);
  assert.match(pageSource, /<option value="arm64">ARM64<\/option>/);
  assert.match(pageSource, /\.download-controls\s*\{[^}]*min-width:\s*0;/s);
  assert.match(pageSource, /select\s*\{[^}]*min-width:\s*0;/s);
});

test("missing and invalid size measurements fail instead of being skipped", () => {
  for (const invalid of [undefined, null, Number.NaN, -1, 0, 1.5, "4096"]) {
    assert.throws(
      () => formatBytes(invalid),
      (error) => error instanceof DownloadCenterError
        && error.code === "INVALID_ASSET_SIZE",
    );
  }

  const unmeasuredAsset = asset("Frontier-win-x64.exe", { size: undefined });
  assert.throws(
    () => analyze(
      [unmeasuredAsset],
      manifestFor([unmeasuredAsset]),
    ),
    (error) => error instanceof DownloadCenterError
      && error.code === "INVALID_RELEASE_MANIFEST"
      && /size does not match/.test(error.message),
  );
});

test("GitHub rate limits and malformed commit data surface actionable failures", async () => {
  const reset = 1_800_000_000;
  await assert.rejects(
    () => fetchGitHubJson("https://api.github.com/example", {
      operation: "checking a test release",
      fetchImpl: async () => jsonResponse(
        { message: "rate limited" },
        {
          status: 403,
          headers: {
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": String(reset),
          },
        },
      ),
    }),
    (error) => {
      assert.equal(error.code, "GITHUB_RATE_LIMIT");
      assert.equal(error.status, 403);
      assert.equal(error.retryAt.toISOString(), new Date(reset * 1000).toISOString());
      assert.match(error.message, /rate limit reached/);
      return true;
    },
  );

  await assert.rejects(
    () => discoverRelease({
      repository,
      fetchImpl: async (url) => url.includes("/releases?")
        ? jsonResponse([release()])
        : jsonResponse({ sha: "short" }),
    }),
    (error) => error instanceof DownloadCenterError
      && error.code === "INVALID_RELEASE_COMMIT",
  );
});

test("an unpublished requested release never selects a different release or repository", async () => {
  const calls = [];
  await assert.rejects(
    () => discoverRelease({
      repository,
      requestedTag: tag,
      fetchImpl: async (url) => {
        calls.push(url);
        return jsonResponse({ message: "Not Found" }, { status: 404 });
      },
    }),
    (error) => error.code === "GITHUB_HTTP_ERROR" && error.status === 404,
  );
  assert.deepEqual(calls, [
    `https://api.github.com/repos/${repository}/releases/tags/${tag}`,
  ]);
});

test("release failures are visible while source fallback remains inspectable", () => {
  const elements = Object.fromEntries(
    ["status", "statusDot", "version", "date", "commit", "resolvedDate", "error"]
      .map((name) => [name, { textContent: "", className: "", hidden: true }]),
  );
  presentReleaseFailure(
    elements,
    new DownloadCenterError("GitHub API request failed (HTTP 500)."),
  );
  assert.equal(elements.status.textContent, "Release check unavailable");
  assert.equal(elements.statusDot.className, "status-dot error");
  assert.equal(elements.error.hidden, false);
  assert.match(elements.error.textContent, /HTTP 500/);
  assert.match(elements.error.textContent, /inspectable source bootstraps remain available/);

  const fallback = buildBootstrapDownloads({
    repository,
    baseUrl: "https://contoso.github.io/frontier/beta/",
  });
  assert.deepEqual(
    fallback.map((item) => item.href),
    [
      "https://contoso.github.io/frontier/beta/frontier.ps1",
      "https://contoso.github.io/frontier/beta/frontier.sh",
    ],
  );
  assert.ok(fallback.every((item) => item.command === "" && item.ready === false));

  const pinned = buildBootstrapDownloads({ repository, tag, commit });
  assert.ok(pinned.every((item) => item.command.includes(commit)));
  assert.ok(pinned.every((item) => item.command.includes(tag)));
  assert.ok(pinned.every((item) => item.command.includes(`https://github.com/${repository}.git`)));
  assert.ok(pinned.every((item) => item.command.includes("BRAINSTEM_BETA_RELEASE_TAG")));
  assert.ok(pinned.every((item) => item.command.includes("BRAINSTEM_BETA_COMMIT")));
  assert.ok(pinned.every((item) => !/RAPP_FRONTIER_REPO/.test(item.command)));
  assert.ok(pinned.every((item) => !/beta\/frontier\.(?:ps1|sh)/.test(item.command)));
  assert.ok(pinned.every((item) => item.href.includes(`/blob/${commit}/beta/install.`)));
  assert.ok(pinned.every((item) => item.downloadable === true));
  assert.ok(
    pinned.every((item) => item.downloadHref.startsWith("data:text/plain;charset=utf-8,")),
  );
  assert.ok(
    pinned.every((item) => decodeURIComponent(item.downloadHref).includes(commit)),
  );
  assert.match(pinned[0].command, /BRAINSTEM_BETA_BOOTSTRAP_URL/);
  assert.ok(
    pinned[0].command.includes(
      `https://raw.githubusercontent.com/${repository}/${commit}/beta/install.cmd`,
    ),
  );
  assert.ok(
    pinned[1].command.includes(
      `https://raw.githubusercontent.com/${repository}/${commit}/beta/install.sh`,
    ),
  );
});

test("copy feedback reports Clipboard API, fallback, and total failure truthfully", async () => {
  const clipboard = copyFixture({ writeText: async () => {} });
  const clipboardResult = await copyText(
    clipboard.context,
    clipboard.button,
    "exact command",
    clipboard.status,
  );
  assert.deepEqual(clipboardResult, { ok: true, method: "clipboard" });
  assert.equal(clipboard.button.textContent, "Copied");
  assert.match(clipboard.status.textContent, /Clipboard API/);
  assert.equal(clipboard.textarea.selected, false);
  clipboard.timers[0]();
  assert.equal(clipboard.button.textContent, "Copy command");

  const fallback = copyFixture({
    writeText: async () => {
      throw new Error("permission denied");
    },
    execCommand: () => true,
  });
  const fallbackResult = await copyText(
    fallback.context,
    fallback.button,
    "exact command",
    fallback.status,
  );
  assert.deepEqual(fallbackResult, { ok: true, method: "fallback" });
  assert.equal(fallback.textarea.selected, true);
  assert.equal(fallback.textarea.removed, true);
  assert.match(fallback.status.textContent, /browser fallback/);

  const failed = copyFixture({
    writeText: async () => {
      throw new Error("permission denied");
    },
    execCommand: () => false,
  });
  const failedResult = await copyText(
    failed.context,
    failed.button,
    "exact command",
    failed.status,
  );
  assert.equal(failedResult.ok, false);
  assert.match(failedResult.clipboardError.message, /permission denied/);
  assert.match(failedResult.fallbackError.message, /fallback failed/);
  assert.equal(failed.button.textContent, "Copy failed");
  assert.equal(failed.attributes.get("aria-invalid"), "true");
  assert.equal(failed.button.dataset.copyState, "failed");
  assert.match(failed.status.textContent, /Clipboard API and browser fallback could not copy/);
  assert.equal(failed.textarea.removed, true);
});

test("submit and dialog behavior stays disabled until a validated release is ready", () => {
  let prevented = 0;
  let opened = 0;
  const event = { preventDefault: () => { prevented += 1; } };

  assert.equal(
    handleDownloadSubmit(event, { disabled: true, openDialog: () => { opened += 1; } }),
    false,
  );
  assert.equal(prevented, 1);
  assert.equal(opened, 0);
  assert.equal(
    handleDownloadSubmit(event, { disabled: false, openDialog: () => { opened += 1; } }),
    true,
  );
  assert.equal(prevented, 2);
  assert.equal(opened, 1);

  const nativeDialog = {
    open: false,
    calls: 0,
    hasAttribute: () => false,
    showModal() {
      this.calls += 1;
      this.open = true;
    },
  };
  assert.equal(showDownloadDialog(nativeDialog), true);
  assert.equal(showDownloadDialog(nativeDialog), false);
  assert.equal(nativeDialog.calls, 1);

  const attributes = new Set();
  const fallbackDialog = {
    open: false,
    hasAttribute: (name) => attributes.has(name),
    setAttribute: (name) => attributes.add(name),
  };
  assert.equal(showDownloadDialog(fallbackDialog), true);
  assert.equal(attributes.has("open"), true);
  assert.equal(showDownloadDialog(fallbackDialog), false);
});

test("nonfunctional links are disabled and no-JS source fallbacks stay usable", () => {
  const attributes = new Map([["href", "#"]]);
  const link = {
    href: "#",
    setAttribute(name, value) {
      attributes.set(name, value);
    },
    removeAttribute(name) {
      attributes.delete(name);
      if (name === "href") this.href = "";
    },
  };
  assert.equal(setFunctionalLink(link, "#"), false);
  assert.equal(link.href, "");
  assert.equal(attributes.get("aria-disabled"), "true");
  assert.equal(attributes.get("tabindex"), "-1");
  assert.equal(
    setFunctionalLink(link, "https://github.com/octo/frontier/releases"),
    true,
  );
  assert.equal(attributes.has("aria-disabled"), false);

  const pageSource = readFileSync(path.join(betaRoot, "index.html"), "utf8");
  assert.doesNotMatch(pageSource, /href="#"/);
  assert.match(pageSource, /id="release-status">Checking Frontier release</);
  assert.match(pageSource, /id="download-button" type="submit" disabled/);
  assert.match(pageSource, /id="release-version">Resolving</);
  assert.match(pageSource, /Checking the release and available downloads\./);
  assert.match(pageSource, /id="recovery-panel"[\s\S]*?id="recovery-windows-link"/);
  assert.match(pageSource, /id="recovery-panel"[\s\S]*?id="recovery-unix-link"/);
  assert.match(pageSource, /id="copy-status"[^>]*aria-live="polite"/);
  assert.match(pageSource, /<noscript>[\s\S]*href="frontier\.ps1"/);
  assert.match(pageSource, /<noscript>[\s\S]*href="frontier\.sh"/);
});

test("duplicate initialization exits before listener registration", async () => {
  const root = { dataset: {} };
  assert.equal(claimDownloadCenterInitialization(root), true);
  assert.equal(claimDownloadCenterInitialization(root), false);

  const result = await initializeDownloadCenter({
    documentObject: {
      documentElement: {
        dataset: { downloadCenterInitialized: "true" },
      },
    },
    windowObject: {},
  });
  assert.deepEqual(result, { initialized: false });
});

test("download URLs and DOM wiring reject executable injection surfaces", () => {
  assert.equal(safeReleaseAssetUrl("javascript:alert(1)", repository), null);
  assert.equal(
    safeReleaseAssetUrl(
      `https://evil.example/${repository}/releases/download/${tag}/Frontier.exe`,
      repository,
    ),
    null,
  );
  assert.equal(
    safeReleaseAssetUrl(
      `https://github.com/${repository}/releases/download/${tag}/Frontier.exe`,
      repository,
      tag,
      "Frontier.exe",
    ),
    `https://github.com/${repository}/releases/download/${tag}/Frontier.exe`,
  );
  assert.equal(
    safeReleaseAssetUrl(
      `https://github.com/${repository}/releases/download/other-tag/Frontier.exe`,
      repository,
      tag,
    ),
    null,
  );

  const moduleSource = readFileSync(path.join(betaRoot, "download-center.js"), "utf8");
  const pageSource = readFileSync(path.join(betaRoot, "index.html"), "utf8");
  assert.doesNotMatch(moduleSource, /\binnerHTML\b|insertAdjacentHTML|document\.write/);
  assert.match(pageSource, /<script type="module" src="download-center\.js"><\/script>/);
  assert.doesNotMatch(pageSource, /href="GOLDEN_PATH\.md"/);
  assert.match(pageSource, /id="golden-path-link"/);
  assert.equal(
    goldenPathUrl("contoso/frontier", "brainstem-beta-v2.0.0"),
    "https://github.com/contoso/frontier/blob/brainstem-beta-v2.0.0/beta/GOLDEN_PATH.md",
  );
  assert.equal(
    repositoryDocumentUrl("contoso/frontier", "brainstem-beta-v2.0.0", "beta/README.md"),
    "https://github.com/contoso/frontier/blob/brainstem-beta-v2.0.0/beta/README.md",
  );
  for (const id of ["frontier-guide-link", "security-link", "license-link"]) {
    const tag = pageSource.match(new RegExp(`<a(?=[^>]*id="${id}")[^>]*>`))?.[0];
    assert.ok(tag, `${id} is missing`);
    assert.match(tag, /https:\/\/github\.com\/microsoft\/aibast-agents-library\/blob\/main\//);
  }
  assert.equal(
    [...pageSource.matchAll(/src="download-center\.js"/g)].length,
    1,
  );
});

test("architecture detection uses explicit high-entropy data without guessing Apple Silicon", async () => {
  assert.equal(
    await detectArchitecture({
      userAgentData: {
        getHighEntropyValues: async () => ({ architecture: "arm", bitness: "64" }),
      },
    }),
    "arm64",
  );
  assert.equal(
    await detectArchitecture({
      userAgentData: {
        getHighEntropyValues: async () => ({ architecture: "x86", bitness: "64" }),
      },
    }),
    "x64",
  );
  assert.equal(
    await detectArchitecture({
      platform: "MacIntel",
      userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    }),
    null,
  );
});
