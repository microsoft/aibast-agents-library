// Molt Lineage — the on-device, rappid-keyed, append-only ring store with
// environment-scoped HEADs. See beta/docs/MOLT-LINEAGE-PROTOCOL.md (molt-lineage/1.0).
//
// This is the layer that lets a Brainstem grow (molt overlays over a pristine Grail
// baseline) while staying resilient (always reconcilable to baseline) — WITHOUT
// touching the Grail kernel. It is PASSTHROUGH-FIRST and FAIL-SAFE by construction:
// every public resolver returns null (meaning "use the pristine baseline") on the
// slightest doubt — kill-switch off, store missing, ancestor unknown, HEAD unset,
// ring unverified, or any thrown error. It can only ever substitute an agent's
// bytes, never subtract from what Grail would have loaded.

import { createHash } from "node:crypto";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import os from "node:os";
import path from "node:path";
import { lineageStoreInternals } from "./lineage-store.mjs";

const STORE_SCHEMA = "molt-lineage/1.0";
const DEFAULT_ENV = "default";
const JOURNAL_CORRUPT_REASON =
  "promotion journal is corrupt (unreadable or not a JSON array) — refusing to trust or extend it";

const { sourceSha256 } = lineageStoreInternals;

function sha256Hex(str) {
  return createHash("sha256").update(String(str), "utf8").digest("hex");
}

function hexOf(rappid) {
  // rappid:@owner/slug:<64hex> -> the 64-hex identity (filesystem-safe key)
  const m = /:([0-9a-f]{64})$/i.exec(String(rappid || ""));
  return m ? m[1] : null;
}

// Identity is UNIFIED with the live routed store: both derivations below delegate
// to the exact rapp/1 functions lineage-store.mjs mints with, so the same molt
// bytes mint the same rappid here and in the running app — the protocol's "the
// same molt has the same rappid in every environment" invariant holds across
// BOTH modules, not just within one.

// Ancestor rappid (ring 0): a stable identity for a baseline agent, derived from
// its filename + pristine bytes, so the SAME Grail agent has the SAME ancestor
// rappid on every device and in every environment (the "same species" key).
export function ancestorRappidFor(filename, baselineSource) {
  return lineageStoreInternals.ancestorRappidFor(filename, baselineSource);
}

// Ring rappid: hash-chained to its parent and its bytes, so a ring cannot forge
// its place in the lineage and the same molt has the same rappid everywhere.
export function ringRappidFor(ancestorRappid, parentRappid, source, filename) {
  return lineageStoreInternals.ringRappidFor(ancestorRappid, parentRappid, source, filename);
}

function readJsonSafe(file) {
  try {
    return JSON.parse(readFileSync(file, "utf8"));
  } catch {
    return null;
  }
}

function writeJsonAtomic(file, value) {
  const tmp = `${file}.tmp-${process.pid}`;
  writeFileSync(tmp, JSON.stringify(value, null, 2), "utf8");
  renameSync(tmp, file);
}

export class MoltLineageStore {
  // enabled=false is the kill-switch: every resolver returns null (pure Grail
  // passthrough) regardless of what is on disk.
  constructor({ root, enabled = true } = {}) {
    this.root = root || path.join(os.homedir(), ".rapp", "lineage");
    this.enabled = enabled !== false;
  }

  _ancestorDir(ancestorRappid) {
    const key = hexOf(ancestorRappid);
    return key ? path.join(this.root, key) : null;
  }

  _indexFile() {
    return path.join(this.root, "filenames.json"); // filename -> ancestorRappid
  }

  _loadIndex() {
    return readJsonSafe(this._indexFile()) || {};
  }

  // Register (or look up) a baseline agent as ring 0. Idempotent: the ancestor
  // rappid is a pure function of the pristine bytes, so re-registering an unchanged
  // baseline is a no-op. Returns the ancestor rappid, or null on any failure.
  registerAncestor(filename, baselineSource) {
    try {
      const ancestorRappid = ancestorRappidFor(filename, baselineSource);
      const dir = this._ancestorDir(ancestorRappid);
      if (!dir) return null;
      mkdirSync(path.join(dir, "rings"), { recursive: true });
      mkdirSync(path.join(dir, "heads"), { recursive: true });
      const manifest = path.join(dir, "ancestor.json");
      if (!existsSync(manifest)) {
        writeJsonAtomic(manifest, {
          schema: STORE_SCHEMA,
          ancestor_rappid: ancestorRappid,
          filename,
          baseline_sha256: sourceSha256(baselineSource),
        });
      }
      const index = this._loadIndex();
      if (index[filename] !== ancestorRappid) {
        mkdirSync(this.root, { recursive: true });
        index[filename] = ancestorRappid;
        writeJsonAtomic(this._indexFile(), index);
      }
      return ancestorRappid;
    } catch {
      return null;
    }
  }

  ancestorForFilename(filename) {
    try {
      return this._loadIndex()[filename] || null;
    } catch {
      return null;
    }
  }

  // Append a molt as a new ring (a frame). verified MUST be established by the
  // fertility/compile gate BEFORE calling this; an unverified ring is stored but
  // will never be resolved live. Returns the ring rappid, or null on failure.
  appendRing(ancestorRappid, { source, parentRappid = null, verified = false, meta = {} } = {}) {
    try {
      const dir = this._ancestorDir(ancestorRappid);
      if (!dir || typeof source !== "string" || !source) return null;
      const ancestor = readJsonSafe(path.join(dir, "ancestor.json"));
      if (!ancestor) return null;
      const filename = ancestor.filename;
      // First rings descend from the ancestor itself — the same parent convention
      // the live routed store uses, so a first molt of the same bytes mints the
      // same ring rappid in both modules.
      const parent = parentRappid || ancestorRappid;
      const ringRappid = ringRappidFor(ancestorRappid, parent, source, filename);
      const key = hexOf(ringRappid);
      if (!key) return null;
      const ringFile = path.join(dir, "rings", `${key}.json`);
      if (!existsSync(ringFile)) {
        mkdirSync(path.join(dir, "rings"), { recursive: true });
        writeJsonAtomic(ringFile, {
          schema: STORE_SCHEMA,
          ring_rappid: ringRappid,
          ancestor_rappid: ancestorRappid,
          parent_rappid: parent,
          filename,
          sha256: sourceSha256(source),
          verified: verified === true,
          source,
          meta: meta && typeof meta === "object" ? meta : {},
        });
      }
      return ringRappid;
    } catch {
      return null;
    }
  }

  getRing(ancestorRappid, ringRappid) {
    try {
      const dir = this._ancestorDir(ancestorRappid);
      const key = hexOf(ringRappid);
      if (!dir || !key) return null;
      const ring = readJsonSafe(path.join(dir, "rings", `${key}.json`));
      // Integrity: the stored source must match the ring's recorded sha, and the
      // ring rappid must re-derive from (parent, source, ancestor) — a tampered
      // ring fails to verify and is treated as absent (=> baseline).
      if (!ring || typeof ring.source !== "string") return null;
      if (sourceSha256(ring.source) !== ring.sha256) return null;
      const expected = ringRappidFor(
        ancestorRappid, ring.parent_rappid, ring.source, ring.filename);
      if (expected !== ringRappid) return null;
      return ring;
    } catch {
      return null;
    }
  }

  _headFile(ancestorRappid, env) {
    const dir = this._ancestorDir(ancestorRappid);
    if (!dir) return null;
    const safeEnv = String(env || DEFAULT_ENV).toLowerCase().replace(/[^a-z0-9._-]/g, "-") || DEFAULT_ENV;
    return path.join(dir, "heads", `${safeEnv}.json`);
  }

  head(ancestorRappid, env = DEFAULT_ENV) {
    try {
      const file = this._headFile(ancestorRappid, env);
      if (!file) return null;
      const rec = readJsonSafe(file);
      return rec && rec.ring_rappid ? rec.ring_rappid : null;
    } catch {
      return null;
    }
  }

  // Move an environment's HEAD to a ring (Benjamin Button / promotion target move).
  // A HEAD may only point at a VERIFIED ring that exists; anything else is refused
  // so a bad ring can never be made live.
  setHead(ancestorRappid, ringRappid, env = DEFAULT_ENV) {
    try {
      const ring = this.getRing(ancestorRappid, ringRappid);
      if (!ring || ring.verified !== true) return false;
      const file = this._headFile(ancestorRappid, env);
      if (!file) return false;
      mkdirSync(path.dirname(file), { recursive: true });
      writeJsonAtomic(file, { schema: STORE_SCHEMA, ring_rappid: ringRappid, env });
      return true;
    } catch {
      return false;
    }
  }

  // Benjamin Button to birth: drop the HEAD so materialization falls back to the
  // pristine Grail baseline. Non-destructive — every ring is retained.
  rollbackToBaseline(ancestorRappid, env = DEFAULT_ENV) {
    try {
      const file = this._headFile(ancestorRappid, env);
      if (file && existsSync(file)) rmSync(file);
      return true;
    } catch {
      return false;
    }
  }

  // THE materialization seam. Given an agent filename, return the live molt source
  // to overlay, or null to use the pristine Grail baseline. Fail-safe: null on the
  // slightest doubt. This is the whole passthrough contract in one method.
  resolveLive(filename, env = DEFAULT_ENV) {
    if (!this.enabled) return null; // kill-switch
    try {
      const ancestorRappid = this.ancestorForFilename(filename);
      if (!ancestorRappid) return null; // unknown agent -> passthrough
      const ringRappid = this.head(ancestorRappid, env);
      if (!ringRappid) return null; // no live molt -> baseline
      const ring = this.getRing(ancestorRappid, ringRappid);
      if (!ring || ring.verified !== true || typeof ring.source !== "string") return null;
      return { source: ring.source, ringRappid, ancestorRappid };
    } catch {
      return null; // any error -> baseline
    }
  }

  // Trace from a ring back to birth (baseline) following parent links. Returns the
  // chain [oldest..ring]; used for Benjamin-Button navigation and merge bases.
  walk(ancestorRappid, ringRappid) {
    const chain = [];
    let cur = ringRappid;
    const guard = new Set();
    while (cur && !guard.has(cur)) {
      guard.add(cur);
      const ring = this.getRing(ancestorRappid, cur);
      if (!ring) break;
      chain.unshift(cur);
      cur = ring.parent_rappid;
    }
    return chain;
  }

  listRings(ancestorRappid) {
    try {
      const dir = this._ancestorDir(ancestorRappid);
      if (!dir) return [];
      const ringsDir = path.join(dir, "rings");
      if (!existsSync(ringsDir)) return [];
      return readdirSync(ringsDir)
        .filter((f) => f.endsWith(".json"))
        .map((f) => readJsonSafe(path.join(ringsDir, f)))
        .filter((r) => r && r.ring_rappid);
    } catch {
      return [];
    }
  }

  // Append-only promotion journal (one file per ancestor). Each entry commits
  // to the previous digest, detecting edits and reordering within the present
  // log. Detecting full deletion or truncation requires an external anchor.
  _promotionsFile(ancestorRappid) {
    const dir = this._ancestorDir(ancestorRappid);
    return dir ? path.join(dir, "promotions.json") : null;
  }

  // Journal state, distinguishing a MISSING journal (empty history — fine) from a
  // CORRUPT one (present but unreadable / not a JSON array). Corruption is never
  // repaired or overwritten here — the corrupt bytes are the evidence §5 exists
  // to surface, so they are refused, not clobbered.
  _promotionJournal(ancestorRappid) {
    const file = this._promotionsFile(ancestorRappid);
    if (!file) return { file: null, log: [], corrupt: false };
    if (!existsSync(file)) return { file, log: [], corrupt: false };
    const parsed = readJsonSafe(file);
    if (!Array.isArray(parsed)) return { file, log: null, corrupt: true };
    return { file, log: parsed, corrupt: false };
  }

  _recordPromotion(ancestorRappid, entry) {
    try {
      const { file, log, corrupt } = this._promotionJournal(ancestorRappid);
      if (!file || corrupt) return null;
      const prev = log.length ? log[log.length - 1].entry_sha256 : null;
      const record = { schema: STORE_SCHEMA, ...entry, prev_entry_sha256: prev };
      record.entry_sha256 = sha256Hex(JSON.stringify(record));
      log.push(record);
      mkdirSync(path.dirname(file), { recursive: true });
      writeJsonAtomic(file, log);
      return record;
    } catch {
      return null;
    }
  }

  listPromotions(ancestorRappid) {
    try {
      const { log } = this._promotionJournal(ancestorRappid);
      return log || [];
    } catch {
      return [];
    }
  }

  // Verify the promotion journal's hash chain end-to-end. A rewritten, reordered, or
  // edited entry breaks the chain and is reported with its index; a journal that is
  // not even a readable array is reported as corrupt, never as ok.
  verifyPromotions(ancestorRappid) {
    let journal;
    try {
      journal = this._promotionJournal(ancestorRappid);
    } catch {
      return { ok: false, corrupt: true, reason: JOURNAL_CORRUPT_REASON };
    }
    if (journal.corrupt) {
      return { ok: false, corrupt: true, reason: JOURNAL_CORRUPT_REASON };
    }
    const log = journal.log;
    let prev = null;
    for (let i = 0; i < log.length; i++) {
      const { entry_sha256, ...rest } = log[i] || {};
      if (rest.prev_entry_sha256 !== prev) return { ok: false, broken_at: i };
      if (sha256Hex(JSON.stringify(rest)) !== entry_sha256) return { ok: false, broken_at: i };
      prev = entry_sha256;
    }
    return { ok: true, entries: log.length };
  }

  // ── Enterprise ALM: gated three-way promotion between environments ──
  // Advance toEnv's HEAD toward fromEnv's, but only as a fast-forward. If toEnv has
  // diverged (holds a ring not on fromEnv's path — a production-only molt the
  // promotion did not build on) it is a CONFLICT and is refused, never overwritten.
  // Every attempt — fast-forward, refusal, or failure — lands in the tamper-evident
  // promotion journal (from/to ring rappids, envs, actor, UTC). The one exception is
  // fail-closed by construction: a CORRUPT journal refuses the promotion outright
  // (no HEAD moves, `journal_corrupt: true`) and preserves the corrupt bytes as
  // evidence instead of appending over them.
  promote(ancestorRappid, { fromEnv, toEnv, actor = null, utc = null } = {}) {
    const record = (outcome) => {
      this._recordPromotion(ancestorRappid, {
        from_env: fromEnv ?? null,
        to_env: toEnv ?? null,
        actor,
        utc: utc || new Date().toISOString(),
        ...outcome,
      });
      return outcome;
    };
    try {
      // §5 fail-closed: a corrupt journal cannot record this attempt, so no HEAD
      // may move — a promotion the audit trail cannot witness must not happen.
      // The refusal is NOT journaled (appending would clobber the evidence).
      if (this._promotionJournal(ancestorRappid).corrupt) {
        return {
          ok: false,
          journal_corrupt: true,
          reason: JOURNAL_CORRUPT_REASON,
        };
      }
      const fromHead = this.head(ancestorRappid, fromEnv);
      const toHead = this.head(ancestorRappid, toEnv);
      if (!fromHead) return record({ ok: false, reason: "source environment has no live ring to promote" });
      if (fromHead === toHead) return record({ ok: true, reason: "already in sync", noop: true });
      const fromChain = this.walk(ancestorRappid, fromHead);
      // Fast-forward is safe iff the target's current HEAD lies on the source's path
      // to baseline (target has NOT diverged). Baseline (no toHead) is trivially on it.
      const targetOnPath = !toHead || fromChain.includes(toHead);
      if (!targetOnPath) {
        const toChain = this.walk(ancestorRappid, toHead);
        const base = [...fromChain].reverse().find((r) => toChain.includes(r)) || null;
        return record({
          ok: false,
          conflict: true,
          reason: "target environment has diverged (a conflicting molt the promotion did not build on)",
          target_head: toHead,
          source_head: fromHead,
          common_ancestor: base,
        });
      }
      const moved = this.setHead(ancestorRappid, fromHead, toEnv);
      return record(
        moved
          ? { ok: true, reason: "fast-forward", target_head: fromHead, source_head: fromHead }
          : { ok: false, reason: "source HEAD is not a verified ring", source_head: fromHead },
      );
    } catch (e) {
      return record({ ok: false, reason: `promotion failed: ${e && e.message ? e.message : e}` });
    }
  }

  // Drift: does the target environment's live HEAD match what a promotion expects
  // as its base? Any mismatch is drift, surfaced BEFORE a promotion, not at runtime.
  detectDrift(ancestorRappid, env, expectedBaseRing) {
    const actual = this.head(ancestorRappid, env);
    const expected = expectedBaseRing || null;
    return { drifted: (actual || null) !== expected, actual: actual || null, expected };
  }
}

export { STORE_SCHEMA };
