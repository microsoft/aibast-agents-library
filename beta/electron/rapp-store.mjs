// RAPP Store client — the source of RAPPlications a twin hatches from.
//
// The store publishes a single catalog (index.json, schema "rapp-store/1.0")
// whose `rapplications[]` each name a **sha256-pinned single-file agent.py**
// (`singleton_url`) plus an optional sha256-pinned state `.egg` (`egg_url`).
// This module fetches the catalog, resolves an id to its entry, and downloads a
// singleton **verifying the pinned hash before it is ever run**. Gated
// (`access: "private"`) entries live in a private repo and 404 on an
// unauthenticated fetch — the client surfaces that as a clear auth-needed error
// instead of a silent miss.
//
// No Electron, no native deps: pure Node (global fetch + node:crypto/node:fs),
// and the fetch impl is injectable so it is unit-testable offline.
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

import { compareBetaVersions } from "./update-manager.mjs";

export const DEFAULT_STORE_URL = "https://kody-w.github.io/RAPP_Store/index.json";
export const AIBAST_REGISTRY_URL = "https://microsoft.github.io/aibast-agents-library/registry.json";
export const STORE_SCHEMA = "rapp-store/1.0";
export const AIBAST_REGISTRY_SCHEMA = "rapp-agent/1.0";
export const AIBAST_RAW_BASE = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/";

// The three RAR library sources the Frontier browser can point at. AIBAST is
// the default; "custom" is any user-supplied RAR-compliant catalog URL
// (either the rapp-store/1.0 index shape or an AIBAST-style registry.json).
export const FRONTIER_STORE_URL = "https://microsoft.github.io/aibast-agents-library/beta/frontier/store/index.json";
export const STORE_SOURCES = {
  aibast: { key: "aibast", label: "AIBAST RAR", url: AIBAST_REGISTRY_URL },
  frontier: { key: "frontier", label: "Frontier Store", url: FRONTIER_STORE_URL },
  public: { key: "public", label: "Public RAR", url: DEFAULT_STORE_URL },
};

export function isAllowedStoreSourceUrl(url) {
  if (typeof url !== "string" || /\s/.test(url)) return false;
  return /^https:\/\/.+$/.test(url)
    || /^http:\/\/(127\.0\.0\.1|localhost)(:\d+)?\/.*$/.test(url);
}

function sha256Hex(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

// The running launcher's version, read from the app's own package.json (the same
// version electron-builder stamps on the artifacts). Null when unavailable — a
// library consumer without a launcher version skips min_app_version enforcement.
function defaultAppVersion() {
  try {
    const pkg = JSON.parse(
      readFileSync(new URL("../package.json", import.meta.url), "utf8"),
    );
    return typeof pkg.version === "string" && pkg.version ? pkg.version : null;
  } catch {
    return null;
  }
}

// A gated entry references a private source; treat an explicit access flag OR a
// "private" quality tier as gated so the caller can prompt for auth up front.
export function isGatedEntry(entry) {
  return entry?.access === "private" || entry?.quality_tier === "private";
}

function normalizeEntry(entry) {
  return {
    id: String(entry.id || ""),
    name: entry.name || entry.id || "",
    version: entry.version || "",
    summary: entry.summary || entry.tagline || "",
    category: entry.category || "",
    tags: Array.isArray(entry.tags) ? entry.tags : [],
    manifestName: entry.manifest_name || "",
    singletonFilename: entry.singleton_filename || "",
    singletonUrl: entry.singleton_url || "",
    singletonSha256: (entry.singleton_sha256 || "").toLowerCase(),
    singletonBytes: Number(entry.singleton_bytes) || null,
    eggUrl: entry.egg_url || null,
    eggSha256: (entry.egg_sha256 || "").toLowerCase(),
    publisher: entry.publisher || "",
    qualityTier: entry.quality_tier || "",
    // Per-repo terms vary (MIT, source-available ARR, PolyForm-NC …) — surface
    // the entry's own license so a twin/consumer honors it, never assume MIT.
    license: entry.license || null,
    // A RAPPlication is specialized agents PLUS a specialized UI for its use
    // case; the twin tile renders this UI, bound to the twin's worker port.
    uiUrl: entry.ui_url || null,
    uiSha256: (entry.ui_sha256 || "").toLowerCase(),
    // "full" (default) opens the pop-out with desktop real estate; "mobile"
    // starts it as a centered phone column. Either can be toggled at runtime.
    preferredView: entry.preferred_view === "mobile" ? "mobile" : "full",
    uiFilename: entry.ui_filename || null,
    gated: isGatedEntry(entry),
    // Release-control fields the client honors: yanked and deprecated entries
    // remain visible to list() for messaging but resolve/download refuse them
    // (each with its own named code), and a min_app_version newer than the
    // running launcher refuses to hatch until the app updates.
    yanked: Boolean(entry.yanked),
    deprecated: Boolean(entry.deprecated),
    minAppVersion: entry.min_app_version || null,
    raw: entry,
  };
}

export class RappStoreClient {
  constructor({
    url = DEFAULT_STORE_URL,
    fetchImpl = globalThis.fetch,
    timeoutMs = 15000,
    appVersion = defaultAppVersion(),
  } = {}) {
    if (typeof fetchImpl !== "function") {
      throw new Error("RappStoreClient needs a fetch implementation.");
    }
    this.url = url;
    this.fetchImpl = fetchImpl;
    this.timeoutMs = timeoutMs;
    this.appVersion = appVersion || null;
    this.catalog = null;
  }

  async #fetch(url, { asBytes = false } = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);
    let response;
    try {
      response = await this.fetchImpl(url, { cache: "no-store", signal: controller.signal });
    } finally {
      clearTimeout(timer);
    }
    if (!response.ok) {
      const error = new Error(`RAPP Store fetch failed: HTTP ${response.status} for ${url}`);
      error.status = response.status;
      throw error;
    }
    if (asBytes) return Buffer.from(await response.arrayBuffer());
    return response.json();
  }

  // Load and validate the catalog once (cached). Returns the parsed catalog.
  async load({ force = false } = {}) {
    if (this.catalog && !force) return this.catalog;
    const data = await this.#fetch(this.url);
    // Two RAR-compliant catalog shapes are accepted:
    //   * rapp-store/1.0 — rapplications[] with singleton_url + singleton_sha256
    //   * an AIBAST-style registry.json — agents[] with _file + _sha256, which
    //     we map onto the same pinned-singleton entry shape (fail-closed pins
    //     preserved; hatching and installing verify the same way).
    if (data && data.schema === STORE_SCHEMA && Array.isArray(data.rapplications)) {
      this.catalog = {
        schema: data.schema,
        generatedAt: data.generated_at || null,
        gatedNote: data.gated_rapplications_note || null,
        rapplications: data.rapplications.map(normalizeEntry),
      };
      return this.catalog;
    }
    if (data && Array.isArray(data.agents)) {
      const base = this.url.replace(/[^/]*$/, "");
      // Only the canonical Microsoft Pages registry maps to the git raw host;
      // any other catalog (a fork, a loopback mirror) resolves _file relative
      // to its OWN URL — a substring match would hijack those to microsoft's raw.
      const raw = this.url.startsWith("https://microsoft.github.io/aibast-agents-library/") ? AIBAST_RAW_BASE : base;
      this.catalog = {
        schema: data.schema || "registry",
        generatedAt: data.generated_at || null,
        gatedNote: null,
        rapplications: data.agents
          .filter((a) => a && a._file && a._sha256)
          .map((a) => normalizeEntry({
            id: String(a.name || "").split("/").pop() || a._install_prefix || a._file,
            name: a.display_name || a.name,
            version: a.version || "",
            summary: a.description || "",
            category: a.category || "",
            tags: a.tags || [],
            manifest_name: a.name || "",
            singleton_filename: a._install_filename || a._file.split("/").pop(),
            singleton_url: raw + a._file.split("/").map(encodeURIComponent).join("/"),
            singleton_sha256: a._sha256,
            singleton_bytes: a._size_kb ? Math.round(a._size_kb * 1024) : null,
            publisher: a.author || "",
            quality_tier: a.quality_tier || "",
            license: a.license || null,
            yanked: a.yanked,
            deprecated: a.deprecated,
            min_app_version: a.min_app_version,
          })),
      };
      return this.catalog;
    }
    throw new Error(`Unexpected RAR catalog schema: ${data?.schema || "(none)"} (want ${STORE_SCHEMA} or a registry with agents[]).`);
  }

  async list() {
    return (await this.load()).rapplications;
  }

  async resolve(id) {
    const wanted = String(id || "").trim().toLowerCase();
    const entry = (await this.list()).find((e) => e.id.toLowerCase() === wanted);
    if (!entry) throw new Error(`No RAPPlication "${id}" in the RAPP Store.`);
    if (entry.yanked) {
      const error = new Error(
        `RAPPlication "${entry.id}" has been yanked (recalled); refusing to resolve or download it.`,
      );
      error.code = "yanked";
      error.entry = entry;
      throw error;
    }
    if (entry.deprecated) {
      const error = new Error(
        `RAPPlication "${entry.id}" is deprecated by its publisher; `
        + "refusing to install or hatch it — pick its replacement from the store.",
      );
      error.code = "deprecated";
      error.entry = entry;
      throw error;
    }
    // min_app_version is a runtime-seam floor: an entry that needs a newer
    // launcher must never hatch on an older one and break at runtime.
    if (
      entry.minAppVersion
      && this.appVersion
      && compareBetaVersions(entry.minAppVersion, this.appVersion) === 1
    ) {
      const error = new Error(
        `RAPPlication "${entry.id}" needs app version ${entry.minAppVersion} or newer `
        + `(this launcher is ${this.appVersion}) — update the app, then hatch it.`,
      );
      error.code = "min_app_version";
      error.entry = entry;
      throw error;
    }
    return entry;
  }

  // Download the pinned singleton (and, if present, its egg), verifying the
  // sha256 before returning. Gated entries that 404 are reported as auth-needed.
  async download(id) {
    const entry = await this.resolve(id);
    if (!entry.singletonUrl) throw new Error(`RAPPlication "${entry.id}" has no singleton_url.`);
    let bytes;
    try {
      bytes = await this.#fetch(entry.singletonUrl, { asBytes: true });
    } catch (error) {
      if (error.status === 404 && entry.gated) {
        const gated = new Error(
          `RAPPlication "${entry.id}" is gated (access: private). `
          + "Sign in / provide a read-scoped token for its private repo to hatch it.",
        );
        gated.code = "gated";
        gated.entry = entry;
        throw gated;
      }
      throw error;
    }
    const digest = sha256Hex(bytes);
    // Fail CLOSED: never return an unpinned singleton for hatching. A gated 404
    // is already handled above; a body that downloads MUST carry a valid pin.
    if (!/^[0-9a-f]{64}$/.test(entry.singletonSha256 || "")) {
      throw new Error(`Refusing to hatch "${entry.id}": the store has no valid singleton_sha256 pin (fail-closed).`);
    }
    if (digest !== entry.singletonSha256) {
      throw new Error(
        `Refusing to hatch "${entry.id}": singleton sha256 mismatch `
        + `(store pins ${entry.singletonSha256}, downloaded ${digest}).`,
      );
    }
    const result = {
      id: entry.id,
      filename: entry.singletonFilename,
      source: bytes.toString("utf8"),
      sha256: digest,
      verified: Boolean(entry.singletonSha256),
      egg: null,
      eggNote: null,
      entry,
    };
    if (entry.eggUrl) {
      if (/^[0-9a-f]{64}$/.test(entry.eggSha256 || "")) {
        const eggBytes = await this.#fetch(entry.eggUrl, { asBytes: true });
        const eggDigest = sha256Hex(eggBytes);
        if (eggDigest !== entry.eggSha256) {
          throw new Error(
            `Refusing "${entry.id}" egg: sha256 mismatch `
            + `(expected ${entry.eggSha256.slice(0, 12)}…, got ${eggDigest.slice(0, 12)}…).`,
          );
        }
        result.egg = eggBytes;
      } else {
        result.eggNote = `Egg for "${entry.id}" carries no sha256 pin in the catalog — skipping unverified egg bytes.`;
      }
    }
    // The custom UI is executable content at the twin's origin — SAME pin law
    // as the singleton. A pinned UI must match its sha256; an unpinned ui_url
    // is never fetched: the twin falls back to the Grail chat rather than run
    // unverified markup.
    result.uiHtml = null;
    result.uiNote = null;
    if (entry.uiUrl) {
      if (/^[0-9a-f]{64}$/.test(entry.uiSha256 || "")) {
        let uiBytes;
        try {
          uiBytes = await this.#fetch(entry.uiUrl, { asBytes: true });
        } catch (error) {
          // The singleton is the agent; a UI that won't download must NOT sink
          // the whole hatch — degrade to the Grail chat with a note.
          result.uiNote = `UI for "${entry.id}" could not be fetched (${error.message}) — using the default Grail chat.`;
          return result;
        }
        const uiDigest = sha256Hex(uiBytes);
        if (uiDigest !== entry.uiSha256) {
          throw new Error(
            `Refusing "${entry.id}" UI: sha256 mismatch `
            + `(expected ${entry.uiSha256.slice(0, 12)}…, got ${uiDigest.slice(0, 12)}…).`,
          );
        }
        result.uiHtml = Buffer.from(uiBytes).toString("utf8");
      } else {
        result.uiNote = `UI for "${entry.id}" carries no sha256 pin in the catalog — using the default Grail chat instead of unverified markup.`;
      }
    }
    return result;
  }
}

export const rappStoreInternals = {
  sha256Hex,
  normalizeEntry,
  isGatedEntry,
  isAllowedStoreSourceUrl,
};
