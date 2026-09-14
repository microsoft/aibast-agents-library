export const TAG_PREFIX = "brainstem-beta-v";
export const DEFAULT_REPOSITORY = "microsoft/aibast-agents-library";
export const RELEASE_MANIFEST_SCHEMA =
  "rapp-brainstem-frontier-release-manifest/v1";
export const RELEASE_MANIFEST_FENCE = "rapp-frontier-release-manifest";

const MAX_RELEASE_MANIFEST_BYTES = 128 * 1024;
const SHA256_PATTERN = /^[0-9a-f]{64}$/;
const COMMIT_SHA_PATTERN = /^[0-9a-f]{40}$/i;
const RELEASE_TAG_PATTERN = /^brainstem-beta-v[0-9A-Za-z][0-9A-Za-z._-]*$/;

const PLATFORM_LABELS = Object.freeze({
  windows: "Windows 11 x64",
  macos: "macOS",
  linux: "Linux",
});

const ARCHITECTURE_LABELS = Object.freeze({
  x64: "x64",
  arm64: "ARM64",
  universal: "universal",
  unknown: "architecture not specified",
});

const PLATFORM_ORDER = Object.freeze({
  windows: 0,
  macos: 1,
  linux: 2,
});

const ARCHITECTURE_ORDER = Object.freeze({
  universal: 0,
  x64: 1,
  arm64: 2,
  unknown: 3,
});

const FILE_NAME_COLLATOR = new Intl.Collator("en", {
  numeric: true,
  sensitivity: "base",
});

export class DownloadCenterError extends Error {
  constructor(message, {
    code = "DOWNLOAD_CENTER_ERROR",
    status = null,
    retryAt = null,
    cause,
  } = {}) {
    super(message, cause === undefined ? undefined : { cause });
    this.name = "DownloadCenterError";
    this.code = code;
    this.status = status;
    this.retryAt = retryAt;
  }
}

export function validRepository(value) {
  if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(value || "")) return false;
  return String(value).split("/").every((part) => part !== "." && part !== "..");
}

function normalizeRequestedTag(value) {
  if (value === null || value === undefined) return null;
  const tag = String(value).trim();
  if (!tag) return null;
  if (!RELEASE_TAG_PATTERN.test(tag)) {
    throw new DownloadCenterError(
      `The requested tag must match ${TAG_PREFIX}<version>.`,
      {
        code: "INVALID_RELEASE_TAG",
      },
    );
  }
  return tag;
}

function isLoopbackHostname(hostname) {
  return ["localhost", "127.0.0.1", "::1", "[::1]"].includes(hostname);
}

export function resolveDownloadContext(locationLike = {}) {
  const params = new URLSearchParams(String(locationLike.search || ""));
  const hasOverride = params.has("repo");
  const override = params.get("repo");
  const hostname = String(locationLike.hostname || "").toLowerCase();
  const requestedTag = normalizeRequestedTag(params.get("tag"));

  if (isLoopbackHostname(hostname)) {
    if (hasOverride && !validRepository(override)) {
      throw new DownloadCenterError("The localhost repository override is invalid.", {
        code: "INVALID_REPOSITORY",
      });
    }
    const untrustedOverride = hasOverride && override !== DEFAULT_REPOSITORY;
    return {
      repository: hasOverride ? override : DEFAULT_REPOSITORY,
      requestedTag,
      trusted: !untrustedOverride,
      authority: untrustedOverride ? "localhost-override" : "canonical-default",
      warning: untrustedOverride
        ? `LOCAL TEST ONLY — UNTRUSTED REPOSITORY ${override}. `
          + "Do not redistribute commands or downloads from this page."
        : "",
    };
  }

  if (hasOverride) {
    throw new DownloadCenterError(
      "Public repository overrides are disabled. Use the repository that owns this Pages deployment.",
      { code: "PUBLIC_REPOSITORY_OVERRIDE" },
    );
  }
  if (!hostname.endsWith(".github.io")) {
    throw new DownloadCenterError(
      "This download page cannot determine a trusted repository from this deployment origin.",
      { code: "AMBIGUOUS_DEPLOYMENT_ORIGIN" },
    );
  }

  const owner = hostname.slice(0, -".github.io".length);
  const pathSegments = String(locationLike.pathname || "").split("/").filter(Boolean);
  if (pathSegments.length < 2 || pathSegments[1] !== "beta") {
    throw new DownloadCenterError(
      "This Pages path does not unambiguously identify a beta repository deployment.",
      { code: "AMBIGUOUS_DEPLOYMENT_PATH" },
    );
  }
  const repository = `${owner}/${pathSegments[0]}`;
  if (!validRepository(repository)) {
    throw new DownloadCenterError("The Pages deployment repository is invalid.", {
      code: "INVALID_REPOSITORY",
    });
  }
  return {
    repository,
    requestedTag,
    trusted: true,
    authority: "github-pages-origin",
    warning: "",
  };
}

function readHeader(headers, name) {
  try {
    return headers && typeof headers.get === "function" ? headers.get(name) : null;
  } catch {
    return null;
  }
}

function parseRateLimitReset(headers) {
  const raw = readHeader(headers, "x-ratelimit-reset");
  if (raw === null || raw === "") return null;
  const seconds = Number(raw);
  if (!Number.isFinite(seconds) || seconds <= 0) return null;
  const retryAt = new Date(seconds * 1000);
  return Number.isFinite(retryAt.getTime()) ? retryAt : null;
}

export async function fetchGitHubJson(url, {
  fetchImpl = globalThis.fetch,
  operation = "checking releases",
} = {}) {
  if (typeof fetchImpl !== "function") {
    throw new DownloadCenterError("GitHub release discovery is unavailable in this browser.", {
      code: "FETCH_UNAVAILABLE",
    });
  }

  let response;
  try {
    response = await fetchImpl(url, {
      headers: { Accept: "application/vnd.github+json" },
    });
  } catch (cause) {
    throw new DownloadCenterError(
      `Could not reach the GitHub API while ${operation}.`,
      { code: "GITHUB_NETWORK_ERROR", cause },
    );
  }

  const status = Number(response?.status);
  if (
    !response
    || typeof response.ok !== "boolean"
    || !Number.isInteger(status)
    || status < 100
    || status > 599
  ) {
    throw new DownloadCenterError(
      `GitHub returned an invalid response while ${operation}.`,
      { code: "INVALID_GITHUB_RESPONSE" },
    );
  }

  if (!response.ok) {
    const remaining = readHeader(response.headers, "x-ratelimit-remaining");
    const rateLimited = status === 429 || (status === 403 && remaining === "0");
    const retryAt = rateLimited ? parseRateLimitReset(response.headers) : null;
    const retryMessage = retryAt ? ` Try again after ${retryAt.toISOString()}.` : "";
    const message = rateLimited
      ? `GitHub API rate limit reached (HTTP ${status}) while ${operation}.${retryMessage}`
      : `GitHub API request failed (HTTP ${status}) while ${operation}.`;
    throw new DownloadCenterError(message, {
      code: rateLimited ? "GITHUB_RATE_LIMIT" : "GITHUB_HTTP_ERROR",
      status,
      retryAt,
    });
  }

  try {
    return await response.json();
  } catch (cause) {
    throw new DownloadCenterError(
      `GitHub returned invalid JSON while ${operation}.`,
      { code: "INVALID_GITHUB_JSON", status, cause },
    );
  }
}

function releaseTimestamp(release) {
  const timestamp = Date.parse(String(release?.published_at || ""));
  return Number.isFinite(timestamp) ? timestamp : null;
}

function compareReleases(left, right) {
  const leftTimestamp = releaseTimestamp(left);
  const rightTimestamp = releaseTimestamp(right);
  if (leftTimestamp !== rightTimestamp) {
    if (leftTimestamp === null) return 1;
    if (rightTimestamp === null) return -1;
    return rightTimestamp - leftTimestamp;
  }

  const leftId = Number(left?.id);
  const rightId = Number(right?.id);
  if (Number.isSafeInteger(leftId) && Number.isSafeInteger(rightId) && leftId !== rightId) {
    return rightId - leftId;
  }

  return FILE_NAME_COLLATOR.compare(
    String(right?.tag_name || ""),
    String(left?.tag_name || ""),
  );
}

export function selectRelease(releases, {
  requestedTag = null,
  tagPrefix = TAG_PREFIX,
} = {}) {
  if (!Array.isArray(releases)) {
    throw new DownloadCenterError("GitHub release metadata was not an array.", {
      code: "INVALID_RELEASE_LIST",
    });
  }

  const exactTag = normalizeRequestedTag(requestedTag);
  return releases
    .filter((candidate) => {
      if (!candidate || typeof candidate !== "object" || candidate.draft === true) {
        return false;
      }
      const tag = candidate.tag_name;
      if (typeof tag !== "string" || !tag) return false;
      return exactTag ? tag === exactTag : tag.startsWith(tagPrefix);
    })
    .sort(compareReleases)[0] || null;
}

function tokenPattern(token) {
  return new RegExp(`(?:^|[^a-z0-9])(?:${token})(?=$|[^a-z0-9])`, "i");
}

const UNIVERSAL_ASSET_PATTERN = tokenPattern("universal(?:2)?");
const ARM64_ASSET_PATTERN = tokenPattern("arm64|aarch64|armv8(?:\\.\\d+)?");
const X64_ASSET_PATTERN = tokenPattern("x64|amd64|x86[_-]64");
const X86_ASSET_PATTERN = tokenPattern("ia32|x86|win32");

export function assetArchitecture(name) {
  const value = String(name || "");
  if (UNIVERSAL_ASSET_PATTERN.test(value)) return "universal";

  const arm64 = ARM64_ASSET_PATTERN.test(value);
  const x64 = X64_ASSET_PATTERN.test(value);
  if (arm64 && x64) return "ambiguous";
  if (arm64) return "arm64";
  if (x64) return "x64";
  if (X86_ASSET_PATTERN.test(value)) return "x86";
  return "unknown";
}

function normalizeArchitecture(architecture, bitness = "") {
  const value = String(architecture || "").toLowerCase();
  const bits = String(bitness || "");
  if (/arm64|aarch64|armv8/.test(value)) return "arm64";
  if (value === "arm" && bits === "64") return "arm64";
  if (/x64|amd64|x86_64|x86-64/.test(value)) return "x64";
  if ((value === "x86" || value === "ia32") && bits === "64") return "x64";
  return null;
}

export async function detectArchitecture(navigatorLike = {}) {
  const userAgentData = navigatorLike?.userAgentData;
  let entropy = null;
  if (userAgentData && typeof userAgentData.getHighEntropyValues === "function") {
    try {
      entropy = await userAgentData.getHighEntropyValues(["architecture", "bitness"]);
    } catch {
      entropy = null;
    }
  }

  const detected = normalizeArchitecture(
    entropy?.architecture || userAgentData?.architecture,
    entropy?.bitness || userAgentData?.bitness,
  );
  if (detected) return detected;

  const userAgent = `${navigatorLike?.platform || ""} ${navigatorLike?.userAgent || ""}`;
  if (/arm64|aarch64|armv8/i.test(userAgent)) return "arm64";
  if (/win64|x86[_-]64|amd64|\bx64\b/i.test(userAgent)) return "x64";
  return null;
}

export function detectPlatform(navigatorLike = {}) {
  const platform =
    navigatorLike?.userAgentData?.platform
    || navigatorLike?.platform
    || navigatorLike?.userAgent
    || "";
  if (/win/i.test(platform)) return "windows";
  if (/mac/i.test(platform)) return "macos";
  if (/linux|x11/i.test(platform)) return "linux";
  return "windows";
}

export function formatBytes(value) {
  if (!Number.isSafeInteger(value) || value <= 0) {
    throw new DownloadCenterError("Asset size must be a positive integer.", {
      code: "INVALID_ASSET_SIZE",
    });
  }
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function platformForAssetName(name) {
  if (/\.exe$/i.test(name)) return "windows";
  if (/\.dmg$/i.test(name)) return "macos";
  return null;
}

export function safeReleaseAssetUrl(value, repository, tag = null, fileName = null) {
  if (!validRepository(repository)) return null;
  try {
    const url = new URL(String(value || ""));
    const expectedPath = tag
      ? `/${repository}/releases/download/${encodeURIComponent(tag)}/`.toLowerCase()
      : `/${repository}/releases/download/`.toLowerCase();
    if (
      url.protocol !== "https:"
      || url.username
      || url.password
      || url.hostname.toLowerCase() !== "github.com"
      || !url.pathname.toLowerCase().startsWith(expectedPath)
    ) {
      return null;
    }
    if (fileName) {
      const encodedName = url.pathname.split("/").pop() || "";
      if (decodeURIComponent(encodedName) !== fileName) return null;
    }
    return url.href;
  } catch {
    return null;
  }
}

function comparePackagedDownloads(left, right) {
  const platformOrder =
    (PLATFORM_ORDER[left.platform] ?? 99) - (PLATFORM_ORDER[right.platform] ?? 99);
  if (platformOrder) return platformOrder;

  const architectureOrder =
    (ARCHITECTURE_ORDER[left.architecture] ?? 99)
    - (ARCHITECTURE_ORDER[right.architecture] ?? 99);
  if (architectureOrder) return architectureOrder;

  const nameOrder = FILE_NAME_COLLATOR.compare(left.fileName, right.fileName);
  if (nameOrder) return nameOrder;
  return left.href.localeCompare(right.href);
}

function platformArchitectureLabel(platform, architecture) {
  if (platform === "windows") return "Windows 11 x64";
  return `${PLATFORM_LABELS[platform]} ${ARCHITECTURE_LABELS[architecture]}`;
}

function binaryDescription(platform, architecture) {
  return `${platformArchitectureLabel(platform, architecture)} manifest-checked installer`;
}

function manifestError(message, code = "INVALID_RELEASE_MANIFEST") {
  return new DownloadCenterError(message, { code });
}

export function parseReleaseManifestBlock(body) {
  if (typeof body !== "string" || !body.trim()) {
    throw manifestError(
      "This release does not publish the required binary provenance manifest.",
      "MISSING_RELEASE_MANIFEST",
    );
  }

  const fence = RELEASE_MANIFEST_FENCE.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const pattern = "```" + fence + "[ \\t]*\\r?\\n([\\s\\S]*?)\\r?\\n```";
  const blocks = [
    ...body.matchAll(new RegExp(pattern, "g")),
  ];
  if (blocks.length === 0) {
    throw manifestError(
      "This release does not publish the required binary provenance manifest.",
      "MISSING_RELEASE_MANIFEST",
    );
  }
  if (blocks.length !== 1) {
    throw manifestError("The release contains multiple binary provenance manifests.");
  }

  const source = blocks[0][1];
  if (
    source !== source.trim()
    || !source
    || new TextEncoder().encode(source).byteLength > MAX_RELEASE_MANIFEST_BYTES
  ) {
    throw manifestError("The binary provenance manifest is empty or too large.");
  }

  let manifest;
  try {
    manifest = JSON.parse(source);
  } catch {
    throw manifestError("The binary provenance manifest is not valid JSON.");
  }
  if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) {
    throw manifestError("The binary provenance manifest must be a JSON object.");
  }
  return { manifest, source };
}

export function parseReleaseManifest(body) {
  return parseReleaseManifestBlock(body).manifest;
}

function manifestAssetName(version) {
  return `RAPP-Brainstem-Frontier-${version}-binary-manifest.json`;
}

async function sha256Hex(bytes, cryptoImpl = globalThis.crypto) {
  if (!cryptoImpl?.subtle || typeof cryptoImpl.subtle.digest !== "function") {
    throw manifestError("This browser cannot verify the release manifest digest.");
  }
  let digest;
  try {
    digest = await cryptoImpl.subtle.digest("SHA-256", bytes);
  } catch (cause) {
    throw new DownloadCenterError(
      "The release manifest digest could not be verified.",
      { code: "INVALID_RELEASE_MANIFEST", cause },
    );
  }
  return [...new Uint8Array(digest)]
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

export async function verifyReleaseManifestAsset(release, {
  repository,
  version,
  fetchImpl = globalThis.fetch,
  cryptoImpl = globalThis.crypto,
} = {}) {
  const block = parseReleaseManifestBlock(release?.body);
  if (release?.immutable !== true) {
    throw manifestError(
      "Packaged installers require an immutable GitHub release.",
    );
  }
  const expectedName = manifestAssetName(version);
  const matches = release.assets.filter((entry) => entry?.name === expectedName);
  if (matches.length !== 1) {
    throw manifestError(
      `Release manifest asset ${expectedName} must exist exactly once.`,
    );
  }
  const asset = matches[0];
  if (
    asset.state !== "uploaded"
    || !Number.isSafeInteger(asset.size)
    || asset.size <= 0
    || !/^sha256:[0-9a-f]{64}$/i.test(asset.digest || "")
  ) {
    throw manifestError("Release manifest asset metadata is incomplete.");
  }
  const href = safeReleaseAssetUrl(
    asset.browser_download_url,
    repository,
    release.tag_name,
    expectedName,
  );
  if (!href || typeof fetchImpl !== "function") {
    throw manifestError("Release manifest asset URL cannot be verified.");
  }

  let response;
  try {
    response = await fetchImpl(href, {
      headers: { Accept: "application/json" },
    });
  } catch (cause) {
    throw new DownloadCenterError(
      "The allowlisted release manifest asset could not be downloaded.",
      { code: "INVALID_RELEASE_MANIFEST", cause },
    );
  }
  const status = Number(response?.status);
  if (
    !response
    || response.ok !== true
    || !Number.isInteger(status)
    || typeof response.arrayBuffer !== "function"
  ) {
    throw manifestError(
      `Release manifest asset download failed (HTTP ${
        Number.isInteger(status) ? status : "unknown"
      }).`,
    );
  }
  let bytes;
  try {
    bytes = new Uint8Array(await response.arrayBuffer());
  } catch (cause) {
    throw new DownloadCenterError(
      "The allowlisted release manifest asset could not be read.",
      { code: "INVALID_RELEASE_MANIFEST", cause },
    );
  }
  const expectedBytes = new TextEncoder().encode(`${block.source}\n`);
  if (
    bytes.byteLength !== asset.size
    || bytes.byteLength !== expectedBytes.byteLength
    || bytes.some((value, index) => value !== expectedBytes[index])
  ) {
    throw manifestError(
      "The fenced release manifest and attached manifest asset differ.",
    );
  }
  const digest = await sha256Hex(bytes, cryptoImpl);
  if (`sha256:${digest}` !== String(asset.digest).toLowerCase()) {
    throw manifestError(
      "The attached release manifest does not match its GitHub SHA-256 digest.",
    );
  }
  return block.manifest;
}

function manifestText(value, label, maximum = 500) {
  if (
    typeof value !== "string"
    || !value.trim()
    || value !== value.trim()
    || value.length > maximum
    || /[\u0000-\u001f\u007f]/.test(value)
  ) {
    throw manifestError(`Manifest ${label} is invalid.`);
  }
  return value;
}

function packageFileName(value) {
  const fileName = manifestText(value, "filename", 255);
  if (!/^[A-Za-z0-9][A-Za-z0-9 ._()+-]*\.(?:exe|dmg)$/i.test(fileName)) {
    throw manifestError(`Manifest filename ${fileName} is unsafe.`);
  }
  const stem = fileName.replace(/\.(?:exe|dmg)$/i, "");
  if (
    /[ .]$/.test(stem)
    || /\.(?:exe|dmg)(?:$|[ ._()+-])/i.test(stem)
    || /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])$/i.test(stem)
    || /(?:^|[ ._()+-])(?:uninstall(?:er)?[0-9]*|unins[0-9]*|remove)(?=$|[ ._()+-])/i.test(stem)
  ) {
    throw manifestError(`Manifest filename ${fileName} uses a deceptive extension.`);
  }
  return fileName;
}

function safeGateRunUrl(value, repository) {
  try {
    const url = new URL(String(value || ""));
    const [owner, project] = repository.toLowerCase().split("/");
    const segments = url.pathname.split("/").filter(Boolean);
    if (
      url.protocol !== "https:"
      || url.username
      || url.password
      || url.hostname.toLowerCase() !== "github.com"
      || segments[0]?.toLowerCase() !== owner
      || segments[1]?.toLowerCase() !== project
      || segments[2]?.toLowerCase() !== "actions"
      || segments[3]?.toLowerCase() !== "runs"
      || !/^[0-9]+$/.test(segments[4] || "")
    ) {
      return null;
    }
    return url.href;
  } catch {
    return null;
  }
}

function validateReleaseBinding(manifest, { release, commit, version }) {
  if (manifest.schema !== RELEASE_MANIFEST_SCHEMA) {
    throw manifestError(`Manifest schema must be ${RELEASE_MANIFEST_SCHEMA}.`);
  }
  if (!manifest.release || typeof manifest.release !== "object") {
    throw manifestError("Manifest release binding is missing.");
  }
  if (manifest.release.tag !== release.tag_name) {
    throw manifestError("Manifest release tag does not match the selected release.");
  }
  if (String(manifest.release.commit || "").toLowerCase() !== commit) {
    throw manifestError("Manifest release commit does not match the resolved tag.");
  }
  if (manifest.release.version !== version) {
    throw manifestError("Manifest runtime version does not match the selected release.");
  }
  if (
    !Array.isArray(manifest.artifacts)
    || manifest.artifacts.length === 0
    || manifest.artifacts.length > 100
  ) {
    throw manifestError("Manifest artifacts must be a non-empty bounded array.");
  }
}

export function analyzePackagedDownloads(
  release,
  { repository, commit, version, manifest } = {},
) {
  if (!validRepository(repository)) {
    throw new DownloadCenterError("A valid repository is required to verify release assets.", {
      code: "INVALID_REPOSITORY",
    });
  }
  if (!release || typeof release !== "object" || !Array.isArray(release.assets)) {
    throw new DownloadCenterError("GitHub release asset metadata was not an array.", {
      code: "INVALID_RELEASE_ASSETS",
    });
  }
  if (release.immutable !== true) {
    throw manifestError(
      "Packaged installers require an immutable GitHub release.",
    );
  }
  if (!/^[0-9a-f]{40}$/.test(commit || "") || typeof version !== "string" || !version) {
    throw manifestError("Verified release identity is required before evaluating binaries.");
  }
  if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) {
    throw manifestError("The binary provenance manifest is missing.");
  }

  validateReleaseBinding(manifest, { release, commit, version });
  const assetsByName = new Map();
  for (const asset of release.assets) {
    if (typeof asset?.name !== "string") continue;
    const matches = assetsByName.get(asset.name) || [];
    matches.push(asset);
    assetsByName.set(asset.name, matches);
  }

  const candidates = [];
  const allowlistedNames = new Set();
  const allowlistedKeys = new Set();
  const allowlistedTuples = new Set();
  for (const entry of manifest.artifacts) {
    if (!entry || typeof entry !== "object" || Array.isArray(entry)) {
      throw manifestError("Every manifest artifact must be an object.");
    }

    const fileName = packageFileName(entry.filename);
    const fileNameKey = fileName.toLowerCase();
    if (allowlistedKeys.has(fileNameKey)) {
      throw manifestError(`Manifest filename ${fileName} is duplicated.`);
    }
    allowlistedNames.add(fileName);
    allowlistedKeys.add(fileNameKey);

    const matches = assetsByName.get(fileName) || [];
    if (matches.length !== 1) {
      throw manifestError(
        `Manifest filename ${fileName} must match exactly one release asset.`,
      );
    }
    const asset = matches[0];
    const platform = platformForAssetName(fileName);
    if (entry.platform !== platform) {
      throw manifestError(`Manifest platform does not match ${fileName}.`);
    }

    const architecture = entry.architecture;
    if (
      !["x64", "arm64", "universal"].includes(architecture)
      || (platform === "windows" && architecture !== "x64")
    ) {
      throw manifestError(`Manifest architecture is invalid for ${fileName}.`);
    }
    const tuple = `${platform}:${architecture}`;
    if (allowlistedTuples.has(tuple)) {
      throw manifestError(`Manifest platform/architecture tuple ${tuple} is duplicated.`);
    }
    allowlistedTuples.add(tuple);
    const nameArchitecture = assetArchitecture(fileName);
    if (
      nameArchitecture === "ambiguous"
      || nameArchitecture === "x86"
      || (nameArchitecture !== "unknown" && nameArchitecture !== architecture)
    ) {
      throw manifestError(`Manifest architecture does not match ${fileName}.`);
    }

    if (
      !Number.isSafeInteger(entry.size)
      || entry.size <= 0
      || entry.size !== asset.size
    ) {
      throw manifestError(`Manifest size does not match ${fileName}.`);
    }
    const size = formatBytes(entry.size);
    if (asset.state !== "uploaded") {
      throw manifestError(`Release asset ${fileName} is not uploaded.`);
    }

    const href = safeReleaseAssetUrl(
      asset.browser_download_url,
      repository,
      release.tag_name,
      fileName,
    );
    if (!href) {
      throw manifestError(`Release asset URL is invalid for ${fileName}.`);
    }

    const sha256 = String(entry.sha256 || "").toLowerCase();
    if (!SHA256_PATTERN.test(sha256)) {
      throw manifestError(`Manifest SHA-256 is invalid for ${fileName}.`);
    }
    if (String(asset.digest || "").toLowerCase() !== `sha256:${sha256}`) {
      throw manifestError(`GitHub digest does not match the manifest for ${fileName}.`);
    }

    if (
      !entry.signing
      || entry.signing.status !== "verified"
    ) {
      throw manifestError(`Verified signing status is required for ${fileName}.`);
    }
    const signingIdentity = manifestText(
      entry.signing.identity,
      `signing identity for ${fileName}`,
    );
    if (/^(?:unknown|none|unsigned|n\/a)$/i.test(signingIdentity)) {
      throw manifestError(`Signing identity is not trustworthy for ${fileName}.`);
    }

    if (
      !entry.runtime
      || entry.runtime.compatible !== true
      || entry.runtime.version !== version
      || String(entry.runtime.commit || "").toLowerCase() !== commit
    ) {
      throw manifestError(`Runtime compatibility does not match ${fileName}.`);
    }
    const nodeCompatibility = manifestText(
      entry.runtime.node,
      `Node compatibility for ${fileName}`,
      100,
    );
    const electronCompatibility = manifestText(
      entry.runtime.electron,
      `Electron compatibility for ${fileName}`,
      100,
    );
    if (
      !/\d+\.\d+\.\d+/.test(nodeCompatibility)
      || !/\d+\.\d+\.\d+/.test(electronCompatibility)
    ) {
      throw manifestError(`Runtime compatibility ranges are invalid for ${fileName}.`);
    }

    if (
      !entry.gate
      || entry.gate.status !== "passed"
      || String(entry.gate.commit || "").toLowerCase() !== commit
    ) {
      throw manifestError(`Successful package gate evidence is required for ${fileName}.`);
    }
    const gateName = manifestText(entry.gate.name, `gate name for ${fileName}`, 200);
    if (!/gate/i.test(gateName)) {
      throw manifestError(`Package gate name is invalid for ${fileName}.`);
    }
    const gateUrl = safeGateRunUrl(entry.gate.run_url, repository);
    if (!gateUrl) {
      throw manifestError(`Package gate URL is invalid for ${fileName}.`);
    }

    candidates.push({
      platform,
      architecture,
      fileName,
      description: binaryDescription(platform, architecture),
      size,
      sizeBytes: entry.size,
      href,
      downloadName: fileName,
      command: "",
      kind: "binary",
      sha256,
      signingIdentity,
      runtimeCompatibility: {
        node: nodeCompatibility,
        electron: electronCompatibility,
      },
      gate: { name: gateName, url: gateUrl },
    });
  }

  candidates.sort(comparePackagedDownloads);
  const downloads = candidates.map((candidate, index) => ({
    ...candidate,
    id: `release-${candidate.platform}-${candidate.architecture}-${index + 1}`,
    platforms: [candidate.platform],
  }));
  const ignored = release.assets
    .filter((asset) => {
      const name = typeof asset?.name === "string" ? asset.name : "";
      return platformForAssetName(name) && !allowlistedNames.has(name);
    })
    .map((asset) => ({
      fileName: asset.name,
      reason: "not allowlisted by the provenance manifest",
    }));

  return { downloads, ignored };
}

function releaseWebUrl(repository, tag) {
  return `https://github.com/${repository}/releases/tag/${encodeURIComponent(tag)}`;
}

function sourceTreeUrl(repository, ref = "main") {
  return `https://github.com/${repository}/tree/${encodeURIComponent(ref)}/beta`;
}

export function repositoryDocumentUrl(repository, ref, filePath) {
  if (
    !validRepository(repository)
    || typeof ref !== "string"
    || !ref
    || !/^[A-Za-z0-9_./-]+$/.test(filePath || "")
    || String(filePath).includes("..")
  ) {
    throw new DownloadCenterError("The repository document URL is invalid.", {
      code: "INVALID_REPOSITORY_DOCUMENT",
    });
  }
  return `https://github.com/${repository}/blob/${encodeURIComponent(ref)}/${filePath}`;
}

export function goldenPathUrl(repository, ref = "main") {
  return repositoryDocumentUrl(repository, ref, "beta/GOLDEN_PATH.md");
}

function releaseListUrl(repository) {
  return `https://github.com/${repository}/releases`;
}

function normalizeReleaseMetadata(release, { repository, requestedTag }) {
  const tag = typeof release?.tag_name === "string" ? release.tag_name : "";
  if (!tag || (requestedTag && tag !== requestedTag)) {
    throw new DownloadCenterError("GitHub returned invalid release tag metadata.", {
      code: "INVALID_RELEASE_METADATA",
    });
  }

  const publishedTimestamp = releaseTimestamp(release);
  if (publishedTimestamp === null) {
    throw new DownloadCenterError(`Release ${tag} does not have a valid published date.`, {
      code: "INVALID_RELEASE_DATE",
    });
  }
  if (!Array.isArray(release.assets)) {
    throw new DownloadCenterError("GitHub release asset metadata was not an array.", {
      code: "INVALID_RELEASE_ASSETS",
    });
  }

  return {
    tag,
    version: tag.startsWith(TAG_PREFIX) ? tag.slice(TAG_PREFIX.length) : tag,
    prerelease: release.prerelease === true,
    publishedAt: new Date(publishedTimestamp),
    releaseUrl: releaseWebUrl(repository, tag),
    sourceUrl: sourceTreeUrl(repository, tag),
    goldenPathUrl: goldenPathUrl(repository, tag),
    guideUrl: repositoryDocumentUrl(repository, tag, "beta/README.md"),
    securityUrl: repositoryDocumentUrl(repository, tag, "SECURITY.md"),
    licenseUrl: repositoryDocumentUrl(repository, tag, "LICENSE"),
  };
}

function normalizeCommit(commitData) {
  const rawCommit = typeof commitData?.sha === "string" ? commitData.sha.trim() : "";
  if (!COMMIT_SHA_PATTERN.test(rawCommit)) {
    throw new DownloadCenterError(
      "The Frontier release did not resolve to a full commit SHA.",
      { code: "INVALID_RELEASE_COMMIT" },
    );
  }
  return rawCommit.toLowerCase();
}

export async function discoverRelease({
  repository,
  requestedTag = null,
  fetchImpl = globalThis.fetch,
} = {}) {
  if (!validRepository(repository)) {
    throw new DownloadCenterError("The release repository is invalid.", {
      code: "INVALID_REPOSITORY",
    });
  }

  let release;
  if (requestedTag) {
    release = await fetchGitHubJson(
      `https://api.github.com/repos/${repository}/releases/tags/${encodeURIComponent(requestedTag)}`,
      { fetchImpl, operation: `checking ${requestedTag} in ${repository}` },
    );
    if (
      !release
      || typeof release !== "object"
      || release.draft === true
      || release.tag_name !== requestedTag
    ) {
      throw new DownloadCenterError(
        `Release ${requestedTag} was not found in ${repository}.`,
        { code: "RELEASE_NOT_FOUND" },
      );
    }
  } else {
    const releases = await fetchGitHubJson(
      `https://api.github.com/repos/${repository}/releases?per_page=100`,
      { fetchImpl, operation: `checking releases for ${repository}` },
    );
    release = selectRelease(releases);
  }
  if (!release) {
    throw new DownloadCenterError(
      `No published ${TAG_PREFIX} release was found in ${repository}.`,
      { code: "RELEASE_NOT_FOUND" },
    );
  }

  const metadata = normalizeReleaseMetadata(release, { repository, requestedTag });
  const commitData = await fetchGitHubJson(
    `https://api.github.com/repos/${repository}/commits/${encodeURIComponent(metadata.tag)}`,
    { fetchImpl, operation: `resolving ${metadata.tag} to a commit` },
  );
  const commit = normalizeCommit(commitData);
  let packagedDownloads = [];
  let rejectedAssets = [];
  let binaryAvailability;
  try {
    const manifest = await verifyReleaseManifestAsset(release, {
      repository,
      version: metadata.version,
      fetchImpl,
    });
    const analysis = analyzePackagedDownloads(release, {
      repository,
      commit,
      version: metadata.version,
      manifest,
    });
    packagedDownloads = analysis.downloads;
    rejectedAssets = analysis.ignored;
    binaryAvailability = {
      available: true,
      code: "VERIFIED_PACKAGES_AVAILABLE",
      message:
        `${packagedDownloads.length} manifest-checked packaged installer`
        + `${packagedDownloads.length === 1 ? "" : "s"} available.`,
    };
  } catch (error) {
    if (
      !(error instanceof DownloadCenterError)
      || !["MISSING_RELEASE_MANIFEST", "INVALID_RELEASE_MANIFEST"].includes(error.code)
    ) {
      throw error;
    }
    const hasPackagedAssets = release.assets.some(
      (asset) => platformForAssetName(String(asset?.name || "")),
    );
    binaryAvailability = error.code === "MISSING_RELEASE_MANIFEST" && !hasPackagedAssets
      ? {
        available: false,
        code: "SOURCE_ONLY_RELEASE",
        message: "This release publishes source bootstraps only.",
      }
      : {
        available: false,
        code: error.code,
        message: "Packaged installers were withheld because their manifest is missing or invalid.",
        detail: error.message,
      };
  }

  return {
    ...metadata,
    repository,
    commit,
    packagedDownloads,
    rejectedAssets,
    binaryAvailability,
  };
}

function bootstrapUrl(fileName, baseUrl) {
  try {
    return new URL(fileName, baseUrl).href;
  } catch (cause) {
    throw new DownloadCenterError("The bootstrap download URL is invalid.", {
      code: "INVALID_BOOTSTRAP_URL",
      cause,
    });
  }
}

function rawRepositoryUrl(repository, commit, filePath) {
  return `https://raw.githubusercontent.com/${repository}/${commit}/${filePath}`;
}

function repositoryFileUrl(repository, ref, filePath) {
  return `https://github.com/${repository}/blob/${encodeURIComponent(ref)}/${filePath}`;
}

export function buildBootstrapDownloads({
  repository,
  baseUrl,
  tag = null,
  commit = null,
} = {}) {
  if (!validRepository(repository)) {
    throw new DownloadCenterError("The bootstrap repository is invalid.", {
      code: "INVALID_REPOSITORY",
    });
  }

  const pinned = tag !== null || commit !== null;
  if (
    pinned
    && (!RELEASE_TAG_PATTERN.test(tag || "") || !COMMIT_SHA_PATTERN.test(commit || ""))
  ) {
    throw new DownloadCenterError(
      "A valid Frontier tag and full commit are required for pinned source commands.",
      { code: "INVALID_RELEASE_IDENTITY" },
    );
  }

  const normalizedCommit = pinned ? commit.toLowerCase() : null;
  const repositoryUrl = `https://github.com/${repository}.git`;
  const runtimeVersionUrl = pinned
    ? rawRepositoryUrl(repository, normalizedCommit, "rapp_brainstem/VERSION")
    : "";
  const windowsInstallerUrl = pinned
    ? rawRepositoryUrl(repository, normalizedCommit, "beta/install.cmd")
    : "";
  const unixInstallerUrl = pinned
    ? rawRepositoryUrl(repository, normalizedCommit, "beta/install.sh")
    : "";
  const brainstemBootstrapUrl = pinned
    ? rawRepositoryUrl(repository, normalizedCommit, "install.ps1")
    : "";
  const windowsHref = pinned
    ? repositoryFileUrl(repository, normalizedCommit, "beta/install.cmd")
    : bootstrapUrl("frontier.ps1", baseUrl);
  const unixHref = pinned
    ? repositoryFileUrl(repository, normalizedCommit, "beta/install.sh")
    : bootstrapUrl("frontier.sh", baseUrl);
  const windowsCommand = pinned
    ? [
      `$env:BRAINSTEM_BETA_REPO_URL="${repositoryUrl}"`,
      `$env:BRAINSTEM_BETA_RELEASE_TAG="${tag}"`,
      `$env:BRAINSTEM_BETA_RUNTIME_VERSION_URL="${runtimeVersionUrl}"`,
      `$env:BRAINSTEM_BETA_COMMIT="${normalizedCommit}"`,
      `$env:BRAINSTEM_BETA_BOOTSTRAP_URL="${brainstemBootstrapUrl}"`,
      `$installer=Join-Path $env:TEMP "rapp-frontier-${normalizedCommit}.cmd"`,
      `try { Invoke-WebRequest "${windowsInstallerUrl}" -OutFile $installer `
        + "-UseBasicParsing; & $installer; if ($LASTEXITCODE -ne 0) "
        + "{ throw \"Frontier installer failed with exit code $LASTEXITCODE.\" } } "
        + "finally { Remove-Item $installer -Force -ErrorAction SilentlyContinue }",
    ].join(";")
    : "";
  const unixCommand = pinned
    ? `curl -fsSL "${unixInstallerUrl}" | `
      + `BRAINSTEM_BETA_REPO_URL="${repositoryUrl}" `
      + `BRAINSTEM_BETA_RELEASE_TAG="${tag}" `
      + `BRAINSTEM_BETA_RUNTIME_VERSION_URL="${runtimeVersionUrl}" `
      + `BRAINSTEM_BETA_COMMIT="${normalizedCommit}" bash`
    : "";
  const windowsDownloadHref = pinned
    ? `data:text/plain;charset=utf-8,${encodeURIComponent(
      `$ErrorActionPreference = "Stop"\r\n${windowsCommand}\r\n`,
    )}`
    : "";
  const unixDownloadHref = pinned
    ? `data:text/plain;charset=utf-8,${encodeURIComponent(
      `#!/usr/bin/env bash\nset -euo pipefail\n${unixCommand}\n`,
    )}`
    : "";

  return [
    {
      id: "source-windows",
      platforms: ["windows"],
      platform: "windows",
      architecture: "source",
      architectures: ["x64"],
      fileName: pinned ? "install.cmd" : "frontier.ps1",
      description: pinned
        ? "Windows 11 x64 exact-commit source install"
        : "Inspect the Windows 11 x64 source bootstrap",
      size: pinned ? "Pinned source" : "Source",
      command: windowsCommand,
      href: windowsHref,
      downloadHref: windowsDownloadHref,
      downloadName: "RAPP-Brainstem-Frontier-Windows.ps1",
      kind: "bootstrap",
      ready: pinned,
      downloadable: pinned,
    },
    {
      id: "source-unix",
      platforms: ["macos", "linux"],
      platform: "unix",
      architecture: "source",
      architectures: ["x64", "arm64"],
      fileName: pinned ? "install.sh" : "frontier.sh",
      description: pinned
        ? "macOS or Linux exact-commit source install"
        : "Inspect the macOS or Linux source bootstrap",
      size: pinned ? "Pinned source" : "Source",
      command: unixCommand,
      href: unixHref,
      downloadHref: unixDownloadHref,
      downloadName: "RAPP-Brainstem-Frontier-macOS-Linux.sh",
      kind: "bootstrap",
      ready: pinned,
      downloadable: pinned,
    },
  ];
}

function itemSupportsArchitecture(item, architecture) {
  if (item.kind === "binary") {
    return item.architecture === architecture || item.architecture === "universal";
  }
  return Array.isArray(item.architectures) && item.architectures.includes(architecture);
}

export function orderDownloadsForPlatform(items, platform, architecture) {
  if (!Array.isArray(items)) {
    throw new DownloadCenterError("The download catalog was not an array.", {
      code: "INVALID_DOWNLOAD_CATALOG",
    });
  }
  if (!Object.hasOwn(PLATFORM_LABELS, platform)) {
    throw new DownloadCenterError(`Unsupported download platform: ${platform}`, {
      code: "INVALID_PLATFORM",
    });
  }
  if (!["x64", "arm64"].includes(architecture)) {
    throw new DownloadCenterError("Choose an explicit x64 or ARM64 architecture.", {
      code: "INVALID_ARCHITECTURE",
    });
  }

  return items
    .filter(
      (item) => Array.isArray(item?.platforms)
        && item.platforms.includes(platform)
        && itemSupportsArchitecture(item, architecture),
    )
    .sort((left, right) => {
      const kindOrder =
        (left.kind === "binary" ? 0 : 1) - (right.kind === "binary" ? 0 : 1);
      if (kindOrder) return kindOrder;

      if (left.kind === "binary" && right.kind === "binary") {
        const compatibilityOrder =
          (left.architecture === architecture ? 0 : 1)
          - (right.architecture === architecture ? 0 : 1);
        if (compatibilityOrder) return compatibilityOrder;
        const architectureOrder =
          (ARCHITECTURE_ORDER[left.architecture] ?? 99)
          - (ARCHITECTURE_ORDER[right.architecture] ?? 99);
        if (architectureOrder) return architectureOrder;
      }

      const name = FILE_NAME_COLLATOR.compare(
        String(left.fileName || ""),
        String(right.fileName || ""),
      );
      if (name) return name;
      return String(left.id || "").localeCompare(String(right.id || ""));
    });
}

function architectureSummary(downloads) {
  const architectures = [];
  for (const architecture of ["universal", "x64", "arm64", "unknown"]) {
    if (downloads.some((item) => item.architecture === architecture)) {
      architectures.push(ARCHITECTURE_LABELS[architecture]);
    }
  }
  return architectures.join(", ");
}

export function platformRecommendation(items, platform, architecture) {
  if (platform === "windows" && architecture === "arm64") {
    return "Windows ARM64 is not supported until its native dependencies pass the package gate.";
  }

  const selectionLabel = platformArchitectureLabel(platform, architecture);
  const available = orderDownloadsForPlatform(items, platform, architecture);
  const binaries = available.filter((item) => item.kind === "binary");
  const sourceAvailable = available.some(
    (item) => item.kind === "bootstrap" && item.ready === true,
  );
  if (!binaries.length && !sourceAvailable) {
    return `No validated download is available for ${selectionLabel}.`;
  }
  if (!binaries.length) {
    return `Download the bootstrap or copy the exact-commit command for ${selectionLabel}.`;
  }

  const packagedLabel = `Packaged installer${binaries.length === 1 ? "" : "s"}`
    + `${binaries.length > 1 ? ` (${architectureSummary(binaries)})` : ""}`;
  return packagedLabel
    + `${sourceAvailable ? " and exact-commit source install" : ""} available for `
    + `${selectionLabel}.`;
}

export function windowsSupportLabel(items) {
  const windowsBinaries = Array.isArray(items)
    ? items.filter(
      (item) => item?.kind === "binary" && item?.platforms?.includes("windows"),
    )
    : [];
  return windowsBinaries.some((item) => item.architecture === "x64")
    ? "Windows 11 x64"
    : "Windows 11 x64 source install";
}

export function claimDownloadCenterInitialization(rootElement) {
  if (!rootElement || !rootElement.dataset) {
    throw new DownloadCenterError("The download page root element is unavailable.", {
      code: "INVALID_DOCUMENT",
    });
  }
  if (rootElement.dataset.downloadCenterInitialized === "true") return false;
  rootElement.dataset.downloadCenterInitialized = "true";
  return true;
}

function requireElement(documentObject, id) {
  const element = documentObject.getElementById(id);
  if (!element) {
    throw new DownloadCenterError(`The download page is missing #${id}.`, {
      code: "MISSING_PAGE_ELEMENT",
    });
  }
  return element;
}

function collectElements(documentObject) {
  return {
    error: requireElement(documentObject, "load-error"),
    sourceStatus: requireElement(documentObject, "source-status"),
    recoveryPanel: requireElement(documentObject, "recovery-panel"),
    recoveryMessage: requireElement(documentObject, "recovery-message"),
    recoveryWindowsLink: requireElement(documentObject, "recovery-windows-link"),
    recoveryUnixLink: requireElement(documentObject, "recovery-unix-link"),
    recoveryWindowsCommand: requireElement(documentObject, "recovery-windows-command"),
    recoveryUnixCommand: requireElement(documentObject, "recovery-unix-command"),
    copyStatus: requireElement(documentObject, "copy-status"),
    status: requireElement(documentObject, "release-status"),
    statusDot: requireElement(documentObject, "status-dot"),
    version: requireElement(documentObject, "release-version"),
    date: requireElement(documentObject, "release-date"),
    files: requireElement(documentObject, "release-files"),
    commit: requireElement(documentObject, "release-commit"),
    resolvedDate: requireElement(documentObject, "resolved-date"),
    platformSelect: requireElement(documentObject, "platform-select"),
    architectureSelect: requireElement(documentObject, "architecture-select"),
    platformHelp: requireElement(documentObject, "platform-help"),
    downloadForm: requireElement(documentObject, "download-form"),
    downloadButton: requireElement(documentObject, "download-button"),
    dialog: requireElement(documentObject, "download-dialog"),
    downloadOptionList: requireElement(documentObject, "download-option-list"),
    selectedCommandPanel: requireElement(documentObject, "selected-command-panel"),
    selectedCommand: requireElement(documentObject, "selected-command"),
    copySelected: requireElement(documentObject, "copy-selected"),
    downloadSelected: requireElement(documentObject, "download-selected"),
    unixCommand: requireElement(documentObject, "unix-command"),
    windowsCommand: requireElement(documentObject, "windows-command"),
    copyUnix: requireElement(documentObject, "copy-unix"),
    copyWindows: requireElement(documentObject, "copy-windows"),
    unixScript: requireElement(documentObject, "unix-script"),
    windowsScript: requireElement(documentObject, "windows-script"),
    sourceLink: requireElement(documentObject, "source-link"),
    guideLink: requireElement(documentObject, "frontier-guide-link"),
    goldenPathLink: requireElement(documentObject, "golden-path-link"),
    securityLink: requireElement(documentObject, "security-link"),
    licenseLink: requireElement(documentObject, "license-link"),
    releaseLinkTop: requireElement(documentObject, "release-link-top"),
    releaseLinkBottom: requireElement(documentObject, "release-link-bottom"),
    expandAll: requireElement(documentObject, "expand-all"),
    windowsCard: requireElement(documentObject, "windows-card"),
    unixCard: requireElement(documentObject, "unix-card"),
    windowsSupport: requireElement(documentObject, "windows-support"),
  };
}

export async function copyText(
  { documentObject, navigatorObject, windowObject },
  button,
  value,
  statusElement,
) {
  const original = button.dataset?.copyOriginalLabel || button.textContent;
  if (button.dataset && !button.dataset.copyOriginalLabel) {
    button.dataset.copyOriginalLabel = original;
  }

  let clipboardFailure = null;
  let method = "clipboard";
  try {
    if (!value) throw new Error("No command is available to copy.");
    if (typeof navigatorObject?.clipboard?.writeText !== "function") {
      throw new Error("Clipboard API unavailable.");
    }
    await navigatorObject.clipboard.writeText(value);
  } catch (error) {
    clipboardFailure = error;
    method = "fallback";
  }

  if (clipboardFailure) {
    let textarea = null;
    try {
      if (!value) throw clipboardFailure;
      textarea = documentObject.createElement("textarea");
      textarea.value = value;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      documentObject.body.appendChild(textarea);
      textarea.select();
      if (
        typeof documentObject.execCommand !== "function"
        || documentObject.execCommand("copy") !== true
      ) {
        throw new Error("Browser copy fallback failed.");
      }
    } catch (fallbackFailure) {
      button.textContent = "Copy failed";
      button.setAttribute("aria-invalid", "true");
      if (button.dataset) button.dataset.copyState = "failed";
      statusElement.textContent =
        "Copy failed. The Clipboard API and browser fallback could not copy the command. "
        + "Select the command text and copy it manually.";
      return {
        ok: false,
        clipboardError: clipboardFailure,
        fallbackError: fallbackFailure,
      };
    } finally {
      textarea?.remove();
    }
  }

  button.textContent = "Copied";
  button.removeAttribute("aria-invalid");
  if (button.dataset) button.dataset.copyState = "copied";
  statusElement.textContent =
    `Install command copied using the ${method === "clipboard" ? "Clipboard API" : "browser fallback"}.`;
  windowObject.setTimeout(() => {
    button.textContent = original;
    if (button.dataset) button.dataset.copyState = "idle";
  }, 1600);
  return { ok: true, method };
}

export function setFunctionalLink(link, url) {
  try {
    const parsed = new URL(String(url || ""));
    if (!["https:", "http:"].includes(parsed.protocol)) throw new Error("Invalid protocol");
    link.href = parsed.href;
    link.removeAttribute("aria-disabled");
    link.removeAttribute("tabindex");
    return true;
  } catch {
    link.removeAttribute("href");
    link.setAttribute("aria-disabled", "true");
    link.setAttribute("tabindex", "-1");
    return false;
  }
}

function setReleaseLinks(elements, url) {
  for (const link of [elements.releaseLinkTop, elements.releaseLinkBottom]) {
    setFunctionalLink(link, url);
  }
}

export function releaseFileSummary(items) {
  if (!Array.isArray(items) || !items.length) {
    throw new DownloadCenterError("Release files are unavailable.", {
      code: "INVALID_RELEASE_FILES",
    });
  }
  return items.map((item) => {
    if (
      typeof item?.fileName !== "string"
      || !item.fileName
      || typeof item?.size !== "string"
      || !item.size
    ) {
      throw new DownloadCenterError("Release file metadata is incomplete.", {
        code: "INVALID_RELEASE_FILES",
      });
    }
    return { fileName: item.fileName, size: item.size };
  });
}

function setFileNames(documentObject, elements, items) {
  const fragment = documentObject.createDocumentFragment();
  for (const item of releaseFileSummary(items)) {
    const entry = documentObject.createElement("span");
    entry.className = "release-file-entry";
    const code = documentObject.createElement("code");
    code.textContent = item.fileName;
    const size = documentObject.createElement("span");
    size.textContent = item.size;
    entry.append(code, size);
    fragment.append(entry);
  }
  elements.files.replaceChildren(fragment);
}

function setAccordionState(documentObject, button, open) {
  const panel = requireElement(documentObject, button.getAttribute("aria-controls"));
  button.setAttribute("aria-expanded", String(open));
  const icon = button.querySelector(".accordion-icon");
  if (!icon) {
    throw new DownloadCenterError("An accordion icon is missing.", {
      code: "MISSING_PAGE_ELEMENT",
    });
  }
  icon.textContent = open ? "−" : "+";
  panel.hidden = !open;
}

function syncExpandAllState(elements, triggers) {
  const allOpen = triggers.every(
    (trigger) => trigger.getAttribute("aria-expanded") === "true",
  );
  elements.expandAll.textContent = allOpen ? "Collapse all" : "Expand all";
  elements.expandAll.setAttribute("aria-expanded", String(allOpen));
}

function setupAccordions(documentObject, elements) {
  const triggers = [...documentObject.querySelectorAll(".accordion-trigger")];
  if (!triggers.length) {
    throw new DownloadCenterError("The download page has no accordion controls.", {
      code: "MISSING_PAGE_ELEMENT",
    });
  }

  for (const trigger of triggers) {
    setAccordionState(
      documentObject,
      trigger,
      trigger.getAttribute("aria-expanded") === "true",
    );
    trigger.addEventListener("click", () => {
      setAccordionState(
        documentObject,
        trigger,
        trigger.getAttribute("aria-expanded") !== "true",
      );
      syncExpandAllState(elements, triggers);
    });

    trigger.addEventListener("keydown", (event) => {
      const currentIndex = triggers.indexOf(trigger);
      let nextIndex;
      switch (event.key) {
        case "ArrowDown":
          nextIndex = (currentIndex + 1) % triggers.length;
          break;
        case "ArrowUp":
          nextIndex = (currentIndex - 1 + triggers.length) % triggers.length;
          break;
        case "Home":
          nextIndex = 0;
          break;
        case "End":
          nextIndex = triggers.length - 1;
          break;
        default:
          return;
      }
      event.preventDefault();
      triggers[nextIndex].focus();
    });
  }

  elements.expandAll.addEventListener("click", () => {
    const shouldOpen = triggers.some(
      (trigger) => trigger.getAttribute("aria-expanded") !== "true",
    );
    for (const trigger of triggers) {
      setAccordionState(documentObject, trigger, shouldOpen);
    }
    syncExpandAllState(elements, triggers);
  });
  syncExpandAllState(elements, triggers);
}

function updateDialogSelection(documentObject, elements, state) {
  const selected = elements.downloadOptionList.querySelector(
    'input[name="download-file"]:checked',
  );
  if (!selected) {
    elements.selectedCommandPanel.hidden = true;
    elements.copySelected.hidden = true;
    elements.downloadSelected.hidden = true;
    elements.downloadSelected.removeAttribute("href");
    elements.downloadSelected.removeAttribute("download");
    return;
  }

  const file = state.downloadItems.find((candidate) => candidate.id === selected.value);
  if (!file) {
    throw new DownloadCenterError("The selected download is no longer available.", {
      code: "INVALID_DOWNLOAD_SELECTION",
    });
  }

  const hasCommand = Boolean(file.command);
  elements.selectedCommandPanel.hidden = !hasCommand;
  elements.copySelected.hidden = !hasCommand;
  elements.selectedCommand.textContent = file.command;
  const downloadable = file.downloadable !== false
    && (file.kind === "binary" || Boolean(file.downloadHref));
  elements.downloadSelected.hidden = !downloadable;
  if (downloadable) {
    if (file.kind === "binary") {
      setFunctionalLink(elements.downloadSelected, file.href);
    } else if (
      typeof file.downloadHref === "string"
      && file.downloadHref.startsWith("data:text/plain;charset=utf-8,")
    ) {
      elements.downloadSelected.href = file.downloadHref;
      elements.downloadSelected.removeAttribute("aria-disabled");
      elements.downloadSelected.removeAttribute("tabindex");
    } else {
      throw new DownloadCenterError("The generated bootstrap download is invalid.", {
        code: "INVALID_BOOTSTRAP_DOWNLOAD",
      });
    }
    elements.downloadSelected.setAttribute("download", file.downloadName);
    elements.downloadSelected.textContent = file.kind === "binary"
      ? "Download installer"
      : "Download bootstrap";
  } else {
    elements.downloadSelected.removeAttribute("href");
    elements.downloadSelected.removeAttribute("download");
  }
}

function renderDownloadOptions(documentObject, elements, state) {
  const available = orderDownloadsForPlatform(
    state.downloadItems,
    elements.platformSelect.value,
    elements.architectureSelect.value,
  );
  elements.downloadOptionList.replaceChildren();

  available.forEach((item, index) => {
    const label = documentObject.createElement("label");
    label.className = "file-option";

    const input = documentObject.createElement("input");
    input.type = "radio";
    input.name = "download-file";
    input.value = item.id;
    input.checked = index === 0;
    input.addEventListener(
      "change",
      () => updateDialogSelection(documentObject, elements, state),
    );

    const description = documentObject.createElement("span");
    const name = documentObject.createElement("span");
    name.className = "file-name";
    name.textContent = item.fileName;
    const platformLabel = documentObject.createElement("span");
    platformLabel.className = "file-platform";
    platformLabel.textContent = item.description;
    description.append(name, platformLabel);

    const size = documentObject.createElement("span");
    size.className = "file-size";
    size.textContent = item.size;

    label.append(input, description, size);
    elements.downloadOptionList.append(label);
  });

  updateDialogSelection(documentObject, elements, state);
}

function updatePlatformRecommendation(elements, state) {
  const platform = elements.platformSelect.value;
  const architecture = elements.architectureSelect.value;
  if (!state.releaseReady) {
    elements.platformHelp.textContent = "Checking the release and available downloads.";
    elements.downloadButton.disabled = true;
    elements.windowsCard.classList.toggle("recommended", platform === "windows");
    elements.unixCard.classList.toggle("recommended", platform !== "windows");
    return;
  }
  elements.platformHelp.textContent = platformRecommendation(
    state.downloadItems,
    platform,
    architecture,
  );
  elements.windowsSupport.textContent = windowsSupportLabel(state.downloadItems);
  elements.windowsCard.classList.toggle("recommended", platform === "windows");
  elements.unixCard.classList.toggle("recommended", platform !== "windows");
  elements.downloadButton.disabled = !state.releaseReady
    || orderDownloadsForPlatform(state.downloadItems, platform, architecture).length === 0;
}

export function showDownloadDialog(dialog) {
  if (dialog.open || dialog.hasAttribute("open")) return false;
  if (typeof dialog.showModal === "function") {
    dialog.showModal();
  } else {
    dialog.setAttribute("open", "");
  }
  return true;
}

function openDownloadDialog(documentObject, elements, state) {
  renderDownloadOptions(documentObject, elements, state);
  const selectedOption = elements.downloadOptionList.querySelector(
    'input[name="download-file"]:checked',
  );
  const opened = showDownloadDialog(elements.dialog);
  selectedOption?.focus();
  return opened;
}

export function handleDownloadSubmit(event, {
  disabled,
  openDialog,
} = {}) {
  event.preventDefault();
  if (disabled || typeof openDialog !== "function") return false;
  openDialog();
  return true;
}

function refreshOpenDownloadDialog(documentObject, elements, state) {
  if (elements.dialog.open || elements.dialog.hasAttribute("open")) {
    renderDownloadOptions(documentObject, elements, state);
  }
}

function sourceDownload(state, id) {
  return state.downloadItems.find((item) => item.id === id);
}

function applySourceLink(link, source) {
  setFunctionalLink(link, source.href);
  if (source.ready) {
    link.removeAttribute("download");
    link.setAttribute("target", "_blank");
    link.setAttribute("rel", "noreferrer");
    link.textContent = "Inspect pinned installer";
  } else {
    link.setAttribute("download", source.downloadName);
    link.removeAttribute("target");
    link.removeAttribute("rel");
    link.textContent = "Download bootstrap";
  }
}

function applySourceControls(elements, state) {
  const windowsSource = sourceDownload(state, "source-windows");
  const unixSource = sourceDownload(state, "source-unix");
  if (!windowsSource || !unixSource) {
    throw new DownloadCenterError("The source bootstrap fallback is incomplete.", {
      code: "MISSING_BOOTSTRAP",
    });
  }

  elements.windowsCommand.textContent =
    windowsSource.command || "Release verification required before this command is enabled.";
  elements.unixCommand.textContent =
    unixSource.command || "Release verification required before this command is enabled.";
  applySourceLink(elements.windowsScript, windowsSource);
  applySourceLink(elements.unixScript, unixSource);
  if (!state.releaseReady && state.allowRecovery === false) {
    for (const link of [elements.windowsScript, elements.unixScript]) {
      setFunctionalLink(link, null);
      link.removeAttribute("download");
      link.textContent = "Release verification required";
    }
  }
  elements.copyWindows.disabled = !windowsSource.command;
  elements.copyUnix.disabled = !unixSource.command;
}

function setupDownloadControls({
  documentObject,
  navigatorObject,
  windowObject,
  elements,
  state,
}) {
  applySourceControls(elements, state);

  const copyContext = { documentObject, navigatorObject, windowObject };
  elements.copyWindows.addEventListener(
    "click",
    () => copyText(
      copyContext,
      elements.copyWindows,
      sourceDownload(state, "source-windows")?.command || "",
      elements.copyStatus,
    ),
  );
  elements.copyUnix.addEventListener(
    "click",
    () => copyText(
      copyContext,
      elements.copyUnix,
      sourceDownload(state, "source-unix")?.command || "",
      elements.copyStatus,
    ),
  );
  elements.copySelected.addEventListener(
    "click",
    () => copyText(
      copyContext,
      elements.copySelected,
      elements.selectedCommand.textContent,
      elements.copyStatus,
    ),
  );
  const updateSelection = () => {
    updatePlatformRecommendation(elements, state);
    refreshOpenDownloadDialog(documentObject, elements, state);
  };
  elements.platformSelect.addEventListener("change", updateSelection);
  elements.architectureSelect.addEventListener("change", updateSelection);
  elements.downloadForm.addEventListener("submit", (event) => {
    handleDownloadSubmit(event, {
      disabled: elements.downloadButton.disabled,
      openDialog: () => openDownloadDialog(documentObject, elements, state),
    });
  });
  elements.dialog.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;
    const visibleControls = [
      ...elements.dialog.querySelectorAll(
        'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
      ),
    ].filter((control) => control.getClientRects().length > 0);
    if (!visibleControls.length) return;

    const first = visibleControls[0];
    const last = visibleControls[visibleControls.length - 1];
    if (!elements.dialog.contains(documentObject.activeElement)) {
      event.preventDefault();
      first.focus();
    } else if (event.shiftKey && documentObject.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && documentObject.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
  elements.dialog.addEventListener("click", (event) => {
    if (event.target !== elements.dialog) return;
    if (typeof elements.dialog.close === "function") {
      elements.dialog.close();
    } else {
      elements.dialog.removeAttribute("open");
    }
  });
}

function setSafetyNotice(elements, messages) {
  const notice = messages.filter(Boolean).join(" ");
  elements.error.textContent = notice;
  elements.error.hidden = !notice;
}

function setSourceStatus(elements, message = "") {
  if (!elements.sourceStatus) return;
  elements.sourceStatus.textContent = message;
  elements.sourceStatus.hidden = !message;
}

function hideRecoveryPanel(elements) {
  if (elements.recoveryPanel) elements.recoveryPanel.hidden = true;
}

function showRecoveryPanel(elements, inspectionDownloads) {
  const windowsSource = inspectionDownloads.find((item) => item.id === "source-windows");
  const unixSource = inspectionDownloads.find((item) => item.id === "source-unix");
  if (!windowsSource || !unixSource) {
    throw new DownloadCenterError("Source recovery downloads are unavailable.", {
      code: "MISSING_BOOTSTRAP",
    });
  }
  setFunctionalLink(elements.recoveryWindowsLink, windowsSource.href);
  setFunctionalLink(elements.recoveryUnixLink, unixSource.href);
  elements.recoveryWindowsLink.setAttribute("download", windowsSource.downloadName);
  elements.recoveryUnixLink.setAttribute("download", unixSource.downloadName);
  elements.recoveryMessage.textContent =
    "Live release details could not be refreshed. Download an inspectable source bootstrap "
    + "now; it resolves the published Frontier release before installing.";
  elements.recoveryPanel.hidden = false;
}

export function presentReleaseFailure(elements, error, authorityWarning = "", requestedTag = null) {
  const message = error instanceof Error ? error.message : "Unknown release discovery error.";
  elements.status.textContent = "Release check unavailable";
  elements.statusDot.className = "status-dot error";
  elements.version.textContent = "Unavailable";
  elements.date.textContent = "Unavailable";
  elements.commit.textContent = "Unavailable";
  elements.resolvedDate.textContent = "Release metadata could not be verified.";
  setSourceStatus(elements);
  setSafetyNotice(elements, [
    authorityWarning,
    requestedTag
      ? `${message} No alternate release has been selected. Verify ${requestedTag} `
        + "in this repository's release notes before retrying."
      : `${message} The inspectable source bootstraps remain available, but verify the `
        + "published release before installing.",
  ]);
}

export function presentBinaryUnavailable(elements, availability) {
  const reason = availability?.message || "Release provenance could not be verified.";
  if (availability?.code === "SOURCE_ONLY_RELEASE" && elements.sourceStatus) {
    setSourceStatus(
      elements,
      "This release is source-only. Download the bootstrap or copy the exact-commit command.",
    );
    setSafetyNotice(elements, []);
    return;
  }
  setSafetyNotice(elements, [
    `Packaged installers are unavailable: ${reason} `
      + "The exact-commit source install remains available.",
  ]);
}

function formatPublishedDate(date, locale) {
  if (!(date instanceof Date) || !Number.isFinite(date.getTime())) {
    throw new DownloadCenterError("The release date could not be measured.", {
      code: "INVALID_RELEASE_DATE",
    });
  }
  return new Intl.DateTimeFormat(locale || undefined, { dateStyle: "long" }).format(date);
}

export function buildReleaseTransaction({ context, release, locale } = {}) {
  if (
    !context
    || !validRepository(context.repository)
    || release?.repository !== context.repository
    || !RELEASE_TAG_PATTERN.test(release?.tag || "")
    || !COMMIT_SHA_PATTERN.test(release?.commit || "")
    || !Array.isArray(release?.packagedDownloads)
    || !release?.binaryAvailability
  ) {
    throw new DownloadCenterError("The resolved release transaction is invalid.", {
      code: "INVALID_RELEASE_TRANSACTION",
    });
  }

  const pinnedSourceDownloads = buildBootstrapDownloads({
    repository: context.repository,
    tag: release.tag,
    commit: release.commit,
  });
  return {
    context,
    release,
    publishedLabel: formatPublishedDate(release.publishedAt, locale),
    downloadItems: [...release.packagedDownloads, ...pinnedSourceDownloads],
  };
}

export function applyReleaseSummary(elements, transaction) {
  const { context, release, publishedLabel } = transaction;
  setFunctionalLink(elements.sourceLink, release.sourceUrl);
  setFunctionalLink(elements.guideLink, release.guideUrl);
  setFunctionalLink(elements.goldenPathLink, release.goldenPathUrl);
  setFunctionalLink(elements.securityLink, release.securityUrl);
  setFunctionalLink(elements.licenseLink, release.licenseUrl);
  setReleaseLinks(elements, release.releaseUrl);
  elements.version.textContent = release.version;
  elements.date.textContent = publishedLabel;
  elements.commit.textContent = release.commit.slice(0, 12);
  elements.commit.title = release.commit;
  elements.resolvedDate.textContent =
    `Published ${publishedLabel} from ${context.repository} at ${release.commit.slice(0, 12)}.`;

  const notices = [];
  if (context.warning) notices.push(context.warning);
  const sourceOnly = release.binaryAvailability.code === "SOURCE_ONLY_RELEASE";
  if (sourceOnly) {
    setSourceStatus(
      elements,
      "This release is source-only. Download the bootstrap or copy the exact commit-pinned "
      + "command for your platform.",
    );
  } else {
    setSourceStatus(elements);
  }
  if (!release.binaryAvailability.available && !sourceOnly) {
    notices.push(
      `Packaged installers are unavailable: ${release.binaryAvailability.message} `
      + `${release.binaryAvailability.detail || ""} `
      + "The exact-commit source install remains available.",
    );
  }
  setSafetyNotice(elements, notices);
  hideRecoveryPanel(elements);

  if (!context.trusted) {
    elements.status.textContent = "LOCAL TEST · UNTRUSTED REPOSITORY";
    elements.statusDot.className = "status-dot error";
  } else {
    elements.status.textContent = release.binaryAvailability.available
      ? (release.prerelease ? "Prerelease ready" : "Release ready")
      : (release.prerelease ? "Source prerelease ready" : "Source release ready");
    elements.statusDot.className = "status-dot ready";
  }
}

function applyReleaseTransaction({
  documentObject,
  elements,
  state,
  context,
  release,
  locale,
}) {
  const transaction = buildReleaseTransaction({ context, release, locale });
  const nextState = {
    downloadItems: transaction.downloadItems,
    releaseReady: true,
  };
  applyReleaseSummary(elements, transaction);
  setFileNames(
    documentObject,
    elements,
    transaction.downloadItems,
  );
  applySourceControls(elements, nextState);
  updatePlatformRecommendation(elements, nextState);
  refreshOpenDownloadDialog(documentObject, elements, nextState);
  state.downloadItems = nextState.downloadItems;
  state.releaseReady = nextState.releaseReady;
  return transaction;
}

function resetReleaseTransaction({
  documentObject,
  elements,
  state,
  inspectionDownloads,
  context,
  error,
}) {
  state.downloadItems = inspectionDownloads;
  state.releaseReady = false;
  setFunctionalLink(elements.sourceLink, sourceTreeUrl(context.repository));
  setFunctionalLink(
    elements.guideLink,
    repositoryDocumentUrl(context.repository, "main", "beta/README.md"),
  );
  setFunctionalLink(elements.goldenPathLink, goldenPathUrl(context.repository));
  setFunctionalLink(
    elements.securityLink,
    repositoryDocumentUrl(context.repository, "main", "SECURITY.md"),
  );
  setFunctionalLink(
    elements.licenseLink,
    repositoryDocumentUrl(context.repository, "main", "LICENSE"),
  );
  setReleaseLinks(elements, releaseListUrl(context.repository));
  setFileNames(
    documentObject,
    elements,
    inspectionDownloads,
  );
  applySourceControls(elements, state);
  updatePlatformRecommendation(elements, state);
  refreshOpenDownloadDialog(documentObject, elements, state);
  presentReleaseFailure(elements, error, context.warning, context.requestedTag);
  if (state.allowRecovery) {
    showRecoveryPanel(elements, inspectionDownloads);
    elements.platformHelp.textContent =
      "Live release details are unavailable. Use the source recovery options below.";
  } else {
    hideRecoveryPanel(elements);
    elements.platformHelp.textContent =
      "The requested release is unavailable. No alternate release has been selected.";
  }
}

export async function initializeDownloadCenter({
  windowObject = globalThis.window,
  documentObject = globalThis.document,
  fetchImpl,
} = {}) {
  if (!documentObject || !claimDownloadCenterInitialization(documentObject.documentElement)) {
    return { initialized: false };
  }

  const elements = collectElements(documentObject);
  const context = resolveDownloadContext(windowObject.location);
  const inspectionDownloads = buildBootstrapDownloads({
    repository: context.repository,
    baseUrl: windowObject.location.href,
  });
  const state = {
    downloadItems: inspectionDownloads,
    releaseReady: false,
    allowRecovery: !context.requestedTag,
  };
  elements.recoveryWindowsCommand.textContent =
    `$env:RAPP_FRONTIER_REPO="${context.repository}";`
    + 'powershell -ExecutionPolicy Bypass -File ".\\RAPP-Brainstem-Frontier-Windows.ps1"';
  elements.recoveryUnixCommand.textContent =
    `RAPP_FRONTIER_REPO="${context.repository}" `
    + 'bash "$HOME/Downloads/RAPP-Brainstem-Frontier-macOS-Linux.sh"';

  setFunctionalLink(elements.sourceLink, sourceTreeUrl(context.repository));
  setFunctionalLink(
    elements.guideLink,
    repositoryDocumentUrl(context.repository, "main", "beta/README.md"),
  );
  setFunctionalLink(elements.goldenPathLink, goldenPathUrl(context.repository));
  setFunctionalLink(
    elements.securityLink,
    repositoryDocumentUrl(context.repository, "main", "SECURITY.md"),
  );
  setFunctionalLink(
    elements.licenseLink,
    repositoryDocumentUrl(context.repository, "main", "LICENSE"),
  );
  setReleaseLinks(elements, releaseListUrl(context.repository));
  setFileNames(
    documentObject,
    elements,
    inspectionDownloads,
  );
  elements.platformSelect.value = detectPlatform(windowObject.navigator);
  elements.architectureSelect.value =
    await detectArchitecture(windowObject.navigator) || "x64";
  setupDownloadControls({
    documentObject,
    navigatorObject: windowObject.navigator,
    windowObject,
    elements,
    state,
  });
  setupAccordions(documentObject, elements);
  elements.status.textContent = "Checking Frontier release";
  elements.statusDot.className = "status-dot";
  elements.version.textContent = "Resolving";
  elements.date.textContent = "Resolving";
  elements.commit.textContent = "Resolving";
  elements.resolvedDate.textContent = "Checking the published Frontier release.";
  elements.platformHelp.textContent = "Checking the release and available downloads.";
  setSourceStatus(elements);
  hideRecoveryPanel(elements);
  updatePlatformRecommendation(elements, state);
  if (context.warning) {
    elements.status.textContent = "LOCAL TEST · UNTRUSTED REPOSITORY";
    elements.statusDot.className = "status-dot error";
    setSafetyNotice(elements, [context.warning]);
  }

  try {
    const release = await discoverRelease({
      repository: context.repository,
      requestedTag: context.requestedTag,
      fetchImpl: fetchImpl || windowObject.fetch?.bind(windowObject),
    });
    applyReleaseTransaction({
      documentObject,
      elements,
      state,
      context,
      release,
      locale: windowObject.navigator?.language,
    });
    return { initialized: true, release, downloadItems: state.downloadItems };
  } catch (error) {
    resetReleaseTransaction({
      documentObject,
      elements,
      state,
      inspectionDownloads,
      context,
      error,
    });
    return { initialized: true, error, downloadItems: state.downloadItems };
  }
}

if (typeof window !== "undefined" && typeof document !== "undefined") {
  void initializeDownloadCenter().catch((error) => {
    const errorElement = document.getElementById("load-error");
    if (errorElement) {
      errorElement.textContent =
        `${error instanceof Error ? error.message : "The download page could not start."} `
        + "No download has been selected. Open the deployment's Download Center without overrides.";
      errorElement.hidden = false;
    }
    const status = document.getElementById("release-status");
    const statusDot = document.getElementById("status-dot");
    if (status) status.textContent = "Download page unavailable";
    if (statusDot) statusDot.className = "status-dot error";
    for (const id of ["windows-script", "unix-script", "recovery-windows-link", "recovery-unix-link"]) {
      const link = document.getElementById(id);
      if (link) {
        setFunctionalLink(link, null);
        link.removeAttribute("download");
      }
    }
  });
}
