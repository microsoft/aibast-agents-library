// RAPP Store client — the source of RAPPlications a twin hatches from.
//
// The store publishes a single catalog (index.json, schema "rapp-store/1.0")
// whose `rapplications[]` each name a **sha256-pinned single-file agent.py**
// (`singleton_url`) plus an optional pre-populated state `.egg` (`egg_url`).
// This module fetches the catalog, resolves an id to its entry, and downloads a
// singleton **verifying the pinned hash before it is ever run**. Gated
// (`access: "private"`) entries live in a private repo and 404 on an
// unauthenticated fetch — the client surfaces that as a clear auth-needed error
// instead of a silent miss.
//
// No Electron, no native deps: pure Node (global fetch + node:crypto), and the
// fetch impl is injectable so it is unit-testable offline.
import { createHash } from "node:crypto";

export const DEFAULT_STORE_URL = "https://kody-w.github.io/RAPP_Store/index.json";
export const STORE_SCHEMA = "rapp-store/1.0";

function sha256Hex(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
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
    publisher: entry.publisher || "",
    qualityTier: entry.quality_tier || "",
    // Per-repo terms vary (MIT, source-available ARR, PolyForm-NC …) — surface
    // the entry's own license so a twin/consumer honors it, never assume MIT.
    license: entry.license || null,
    // A RAPPlication is specialized agents PLUS a specialized UI for its use
    // case; the twin tile renders this UI, bound to the twin's worker port.
    uiUrl: entry.ui_url || null,
    uiFilename: entry.ui_filename || null,
    gated: isGatedEntry(entry),
    raw: entry,
  };
}

export class RappStoreClient {
  constructor({ url = DEFAULT_STORE_URL, fetchImpl = globalThis.fetch, timeoutMs = 15000 } = {}) {
    if (typeof fetchImpl !== "function") {
      throw new Error("RappStoreClient needs a fetch implementation.");
    }
    this.url = url;
    this.fetchImpl = fetchImpl;
    this.timeoutMs = timeoutMs;
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
    if (!data || data.schema !== STORE_SCHEMA) {
      throw new Error(`Unexpected RAPP Store schema: ${data?.schema || "(none)"} (want ${STORE_SCHEMA}).`);
    }
    if (!Array.isArray(data.rapplications)) {
      throw new Error("RAPP Store catalog has no rapplications array.");
    }
    this.catalog = {
      schema: data.schema,
      generatedAt: data.generated_at || null,
      gatedNote: data.gated_rapplications_note || null,
      rapplications: data.rapplications.map(normalizeEntry),
    };
    return this.catalog;
  }

  async list() {
    return (await this.load()).rapplications;
  }

  async resolve(id) {
    const wanted = String(id || "").trim().toLowerCase();
    const entry = (await this.list()).find((e) => e.id.toLowerCase() === wanted);
    if (!entry) throw new Error(`No RAPPlication "${id}" in the RAPP Store.`);
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
      entry,
    };
    if (entry.eggUrl) {
      result.egg = await this.#fetch(entry.eggUrl, { asBytes: true });
    }
    return result;
  }
}

export const rappStoreInternals = { sha256Hex, normalizeEntry, isGatedEntry };
