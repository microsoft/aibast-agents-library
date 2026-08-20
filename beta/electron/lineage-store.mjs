import {
  chmodSync,
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

import {
  H,
  Hb,
  mintRappid,
  rappidValid,
} from "./rapp-protocol.mjs";


const LINEAGE_SCHEMA = "molt-lineage/1.0";
const HEAD_FILE = "HEAD";
const LOCUS_FILE = "locus.json";
const RING_SOURCE_FILE = "source.py";
const RING_META_FILE = "meta.json";

function ensurePrivateDirectory(directory) {
  mkdirSync(directory, { recursive: true, mode: 0o700 });
  try {
    chmodSync(directory, 0o700);
  } catch {}
}

function atomicWrite(filePath, value) {
  ensurePrivateDirectory(path.dirname(filePath));
  const temporary = `${filePath}.${process.pid}.${Date.now()}.tmp`;
  writeFileSync(temporary, value, { mode: 0o600 });
  renameSync(temporary, filePath);
}

function atomicWriteJson(filePath, value) {
  atomicWrite(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

function readJsonSafe(filePath) {
  // A corrupt or unreadable JSON file is treated as absent: every lineage
  // error must degrade to a bootable composition, never propagate a throw.
  try {
    return JSON.parse(readFileSync(filePath, "utf8"));
  } catch {
    return null;
  }
}

function filesystemSegment(value) {
  // Directory names are a short, stable digest of the rappid — URI-encoding
  // the full rappid (~100 chars per segment) pushes ring paths past the
  // Windows MAX_PATH limit (260). Identity stays inside locus.json/meta.json;
  // only the directory name shortens (same rappid -> same segment).
  return Hb(
    "rapp/1:lineage-segment",
    Buffer.from(String(value), "utf8"),
  ).slice(0, 32);
}

function slugFromFilename(filename) {
  const slug = path.basename(String(filename || ""))
    .replace(/_agent\.py$/i, "")
    .replace(/\.py$/i, "")
    .replaceAll("_", "-")
    .toLowerCase()
    .replace(/[^a-z0-9-]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 94);
  return slug || "agent";
}

function uuidFromDigest(digest) {
  const compact = String(digest).slice(0, 32);
  if (!/^[0-9a-f]{32}$/.test(compact)) {
    throw new Error("A stable 128-bit digest is required for lineage minting.");
  }
  return [
    compact.slice(0, 8),
    compact.slice(8, 12),
    compact.slice(12, 16),
    compact.slice(16, 20),
    compact.slice(20),
  ].join("-");
}

function sourceSha256(source) {
  // The single identity chokepoint. CRLF canonicalizes to LF so a git
  // autocrlf checkout mints the same ancestor/ring rappids as an LF checkout
  // — the same molt has the same rappid everywhere.
  return Hb(
    "rapp/1:molt-source",
    Buffer.from(String(source).replaceAll("\r\n", "\n"), "utf8"),
  );
}

function ancestorRappidFor(filename, source) {
  const baselineSha = sourceSha256(source);
  const anchor = uuidFromDigest(H("rapp/1:molt-ancestor", {
    filename,
    sha256: baselineSha,
  }));
  return mintRappid("grail", slugFromFilename(filename), {
    uuidAnchor: anchor,
  }).rappid;
}

function ringRappidFor(ancestorRappid, parentRappid, source, filename) {
  const chainDigest = H("rapp/1:molt-ring", {
    ancestor: ancestorRappid,
    parent: parentRappid,
    src: sourceSha256(source),
  });
  return mintRappid(
    "frontier",
    `${slugFromFilename(filename)}-ring`,
    { uuidAnchor: uuidFromDigest(chainDigest) },
  ).rappid;
}

function newestFirst(left, right) {
  return String(right.createdAt || "").localeCompare(String(left.createdAt || ""))
    || right.ringRappid.localeCompare(left.ringRappid);
}

export class LineageStore {
  constructor({
    brainstemDir,
    root = path.join(os.homedir(), ".rapp", "lineage"),
    enabled = true,
    now = () => new Date().toISOString(),
  } = {}) {
    if (!brainstemDir) {
      throw new Error("LineageStore requires the pristine Brainstem directory.");
    }
    this.brainstemDir = path.resolve(brainstemDir);
    this.root = path.resolve(root);
    this.enabled = enabled !== false;
    this.now = now;
  }

  baselineAncestors() {
    const agentsDirectory = path.join(this.brainstemDir, "agents");
    return readdirSync(agentsDirectory, { withFileTypes: true })
      .filter((entry) => (
        entry.isFile()
        && entry.name.endsWith("_agent.py")
        && !entry.name.startsWith("__")
      ))
      .map((entry) => {
        const sourcePath = path.join(agentsDirectory, entry.name);
        const source = readFileSync(sourcePath, "utf8");
        return {
          ancestorRappid: ancestorRappidFor(entry.name, source),
          filename: entry.name,
          sha256: sourceSha256(source),
          sourcePath,
        };
      })
      .sort((left, right) => left.filename.localeCompare(right.filename));
  }

  _baseline(ancestorRappid) {
    return this.baselineAncestors().find(
      (candidate) => candidate.ancestorRappid === ancestorRappid,
    ) || null;
  }

  _locusDirectory(ancestorRappid) {
    return path.join(this.root, filesystemSegment(ancestorRappid));
  }

  _ringsDirectory(ancestorRappid) {
    return path.join(this._locusDirectory(ancestorRappid), "rings");
  }

  _ringDirectory(ancestorRappid, ringRappid) {
    return path.join(
      this._ringsDirectory(ancestorRappid),
      filesystemSegment(ringRappid),
    );
  }

  _headPath(ancestorRappid) {
    return path.join(this._locusDirectory(ancestorRappid), HEAD_FILE);
  }

  _ensureLocus(baseline, policy = "mutable") {
    const locusDirectory = this._locusDirectory(baseline.ancestorRappid);
    ensurePrivateDirectory(this._ringsDirectory(baseline.ancestorRappid));
    const locusPath = path.join(locusDirectory, LOCUS_FILE);
    if (!existsSync(locusPath)) {
      atomicWriteJson(locusPath, {
        schema: LINEAGE_SCHEMA,
        ancestorRappid: baseline.ancestorRappid,
        filename: baseline.filename,
        sha256: baseline.sha256,
        sourcePath: baseline.sourcePath,
        policy: policy === "pinned" ? "pinned" : "mutable",
      });
    }
  }

  _readRing(ancestorRappid, ringRappid) {
    const ringDirectory = this._ringDirectory(ancestorRappid, ringRappid);
    const sourcePath = path.join(ringDirectory, RING_SOURCE_FILE);
    const metaPath = path.join(ringDirectory, RING_META_FILE);
    if (!existsSync(sourcePath) || !existsSync(metaPath)) return null;
    const meta = readJsonSafe(metaPath);
    if (!meta || typeof meta !== "object") return null;
    try {
      return {
        ...meta,
        source: readFileSync(sourcePath, "utf8"),
      };
    } catch {
      return null;
    }
  }

  _ringIsValid(ancestorRappid, ringRappid, ring = null) {
    const candidate = ring || this._readRing(ancestorRappid, ringRappid);
    if (
      !candidate
      || candidate.ringRappid !== ringRappid
      || candidate.ancestorRappid !== ancestorRappid
      || typeof candidate.source !== "string"
      || candidate.sha256 !== sourceSha256(candidate.source)
    ) {
      return false;
    }
    const baseline = this._baseline(ancestorRappid);
    if (!baseline) return false;
    return ringRappidFor(
      ancestorRappid,
      candidate.parentRappid,
      candidate.source,
      baseline.filename,
    ) === ringRappid;
  }

  _pathIsValid(ancestorRappid, ringRappid, { requireVerified = false } = {}) {
    const seen = new Set();
    let current = ringRappid;
    while (current !== ancestorRappid) {
      if (!rappidValid(current) || seen.has(current)) return false;
      seen.add(current);
      const ring = this._readRing(ancestorRappid, current);
      if (!this._ringIsValid(ancestorRappid, current, ring)) return false;
      if (requireVerified && ring.verified !== true) return false;
      current = ring.parentRappid;
    }
    return true;
  }

  listRings(ancestorRappid) {
    const baseline = this._baseline(ancestorRappid);
    if (!baseline) return [];
    const baselineRing = {
      ringRappid: ancestorRappid,
      parentRappid: null,
      ancestorRappid,
      sha256: baseline.sha256,
      verified: true,
      meta: { ring: 0, policy: "pinned", sourcePath: baseline.sourcePath },
      createdAt: null,
    };
    const ringsDirectory = this._ringsDirectory(ancestorRappid);
    if (!existsSync(ringsDirectory)) return [baselineRing];
    const rings = readdirSync(ringsDirectory, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && !entry.name.startsWith("."))
      .map((entry) => readJsonSafe(
        path.join(ringsDirectory, entry.name, RING_META_FILE),
      ))
      .filter((meta) => meta && typeof meta.ringRappid === "string")
      .sort((left, right) => (
        String(left.createdAt || "").localeCompare(String(right.createdAt || ""))
        || left.ringRappid.localeCompare(right.ringRappid)
      ));
    return [baselineRing, ...rings];
  }

  appendRing(
    ancestorRappid,
    {
      source,
      parentRappid,
      verified,
      meta = {},
    } = {},
  ) {
    const baseline = this._baseline(ancestorRappid);
    if (!baseline) throw new Error(`Unknown Grail ancestor: ${ancestorRappid}`);
    if (typeof source !== "string" || !source.length) {
      throw new Error("A molt ring requires non-empty Python source.");
    }
    const parent = parentRappid || this.getHead(ancestorRappid);
    if (
      parent !== ancestorRappid
      && !this._pathIsValid(
        ancestorRappid,
        parent,
        { requireVerified: true },
      )
    ) {
      throw new Error("A molt ring must descend from an existing valid parent.");
    }
    const ringRappid = ringRappidFor(
      ancestorRappid,
      parent,
      source,
      baseline.filename,
    );
    const ringDirectory = this._ringDirectory(ancestorRappid, ringRappid);
    if (existsSync(ringDirectory)) {
      const existing = this._readRing(ancestorRappid, ringRappid);
      if (!this._ringIsValid(ancestorRappid, ringRappid, existing)) {
        throw new Error(`Existing ring is corrupt: ${ringRappid}`);
      }
      if (verified === true && existing.verified !== true) {
        const { source: _source, ...existingMeta } = existing;
        atomicWriteJson(path.join(ringDirectory, RING_META_FILE), {
          ...existingMeta,
          verified: true,
          meta: {
            ...(existing.meta && typeof existing.meta === "object"
              ? existing.meta
              : {}),
            ...(meta && typeof meta === "object" ? meta : {}),
          },
        });
      }
      return ringRappid;
    }

    this._ensureLocus(baseline, meta.policy);
    const stagingDirectory = path.join(
      this._ringsDirectory(ancestorRappid),
      `.${filesystemSegment(ringRappid)}.${process.pid}.${Date.now()}.stage`,
    );
    ensurePrivateDirectory(stagingDirectory);
    const ringMeta = {
      schema: LINEAGE_SCHEMA,
      ringRappid,
      parentRappid: parent,
      ancestorRappid,
      sha256: sourceSha256(source),
      verified: verified === true,
      meta: meta && typeof meta === "object" ? { ...meta } : {},
      createdAt: this.now(),
    };
    try {
      writeFileSync(
        path.join(stagingDirectory, RING_SOURCE_FILE),
        source,
        { mode: 0o600 },
      );
      writeFileSync(
        path.join(stagingDirectory, RING_META_FILE),
        `${JSON.stringify(ringMeta, null, 2)}\n`,
        { mode: 0o600 },
      );
      renameSync(stagingDirectory, ringDirectory);
    } catch (error) {
      rmSync(stagingDirectory, { recursive: true, force: true });
      if (
        existsSync(ringDirectory)
        && this._ringIsValid(ancestorRappid, ringRappid)
      ) {
        return ringRappid;
      }
      throw error;
    }
    return ringRappid;
  }

  getHead(ancestorRappid) {
    const baseline = this._baseline(ancestorRappid);
    if (!baseline) return null;
    const headPath = this._headPath(ancestorRappid);
    if (!existsSync(headPath)) return ancestorRappid;
    try {
      const head = readFileSync(headPath, "utf8").trim();
      return rappidValid(head) ? head : ancestorRappid;
    } catch {
      return ancestorRappid;
    }
  }

  setHead(ancestorRappid, ringRappid) {
    const baseline = this._baseline(ancestorRappid);
    if (!baseline) throw new Error(`Unknown Grail ancestor: ${ancestorRappid}`);
    if (
      ringRappid !== ancestorRappid
      && !this._pathIsValid(
        ancestorRappid,
        ringRappid,
        { requireVerified: true },
      )
    ) {
      throw new Error(`Refusing invalid or unverified molt ring: ${ringRappid}`);
    }
    this._ensureLocus(baseline);
    atomicWrite(this._headPath(ancestorRappid), `${ringRappid}\n`);
  }

  resolveRing(ancestorRappid, ringRappid) {
    const baseline = this._baseline(ancestorRappid);
    if (!baseline) return null;
    const baselineResult = () => ({
      ringRappid: ancestorRappid,
      source: readFileSync(baseline.sourcePath, "utf8"),
      isBaseline: true,
    });
    if (!this.enabled || process.env.RAPP_MOLT_LINEAGE === "0") {
      return baselineResult();
    }
    try {
      if (!ringRappid || ringRappid === ancestorRappid) return baselineResult();
      const ring = this._readRing(ancestorRappid, ringRappid);
      if (
        !ring
        || ring.verified !== true
        || !this._pathIsValid(
          ancestorRappid,
          ringRappid,
          { requireVerified: true },
        )
      ) {
        return baselineResult();
      }
      return {
        ringRappid,
        source: ring.source,
        isBaseline: false,
      };
    } catch {
      return baselineResult();
    }
  }

  resolveLive(ancestorRappid) {
    return this.resolveRing(
      ancestorRappid,
      this.getHead(ancestorRappid),
    );
  }

  /** True when the overlay may serve or move rings at all. The kill switch must
   *  gate WRITES as well as reads: otherwise HEADs move invisibly while the layer
   *  is off and silently activate on the next boot once the flag is cleared. */
  isEnabled() {
    return this.enabled && process.env.RAPP_MOLT_LINEAGE !== "0";
  }

  /** Resolve the loci a fleet-wide command applies to, without letting an
   *  unreadable Grail tree throw out of the command. */
  _commandTargets(ancestorRappid) {
    if (ancestorRappid) return [ancestorRappid];
    try {
      return this.baselineAncestors().map((baseline) => baseline.ancestorRappid);
    } catch {
      return [];
    }
  }

  /** Move HEAD across loci, isolating each one. A single failing locus must never
   *  abort the fleet and leave the rest molted — the whole point of the safe word
   *  is that it always lands somewhere safe. Returns a report, never throws. */
  _moveHeads(targets, pick) {
    const changed = [];
    const failed = [];
    for (const target of targets) {
      try {
        this.setHead(target, pick(target));
        changed.push(target);
      } catch (error) {
        failed.push({ ancestorRappid: target, error: String(error?.message || error) });
      }
    }
    return { disabled: false, changed, failed };
  }

  rollbackToBaseline(ancestorRappid = null) {
    if (!this.isEnabled()) return { disabled: true, changed: [], failed: [] };
    return this._moveHeads(this._commandTargets(ancestorRappid), (target) => target);
  }

  restore(ancestorRappid = null) {
    if (!this.isEnabled()) return { disabled: true, changed: [], failed: [] };
    return this._moveHeads(this._commandTargets(ancestorRappid), (target) => {
      const latest = this.listRings(target)
        .filter((ring) => (
          ring.ringRappid !== target
          && ring.verified === true
          && this._pathIsValid(
            target,
            ring.ringRappid,
            { requireVerified: true },
          )
        ))
        .sort(newestFirst)[0];
      return latest?.ringRappid || target;
    });
  }

  /** Count ring directories on disk whose metadata will not parse. listRings
   *  deliberately drops these so composition stays fail-safe, but an integrity
   *  check must not inherit that blindness — otherwise the audit surface hides
   *  exactly the corruption it exists to find. */
  _corruptRingCount(ancestorRappid) {
    const ringsDirectory = this._ringsDirectory(ancestorRappid);
    if (!existsSync(ringsDirectory)) return 0;
    return readdirSync(ringsDirectory, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && !entry.name.startsWith("."))
      .filter((entry) => {
        const meta = readJsonSafe(
          path.join(ringsDirectory, entry.name, RING_META_FILE),
        );
        return !meta || typeof meta.ringRappid !== "string";
      })
      .length;
  }

  /** Health report for a locus. verifyChain() answers only "does the reachable
   *  chain verify" — deliberately, so unreachable corruption never breaks
   *  composition. This surfaces the corruption that answer omits, so operators
   *  (and the proprioception layer) can see rot on disk instead of inferring
   *  health from a boolean that was never asked the question. */
  inspectLineage(ancestorRappid) {
    let corruptRings = 0;
    try {
      corruptRings = this._corruptRingCount(ancestorRappid);
    } catch {
      corruptRings = 0;
    }
    let chainOk = false;
    try {
      chainOk = this.verifyChain(ancestorRappid);
    } catch {
      chainOk = false;
    }
    let head = null;
    try {
      head = this.getHead(ancestorRappid);
    } catch {
      head = null;
    }
    return {
      ancestorRappid,
      chainOk,
      corruptRings,
      healthy: chainOk && corruptRings === 0,
      head,
    };
  }

  verifyChain(ancestorRappid) {
    const baseline = this._baseline(ancestorRappid);
    if (!baseline) return false;
    try {
      return this.listRings(ancestorRappid)
        .filter((ring) => ring.ringRappid !== ancestorRappid)
        .every((ring) => (
          this._ringIsValid(ancestorRappid, ring.ringRappid)
          && this._pathIsValid(ancestorRappid, ring.ringRappid)
        ));
    } catch {
      return false;
    }
  }
}

export const lineageStoreInternals = {
  ancestorRappidFor,
  filesystemSegment,
  ringRappidFor,
  sourceSha256,
};

let defaultStore = null;

export function configureLineageStore(options = {}) {
  defaultStore = options instanceof LineageStore
    ? options
    : new LineageStore({
        brainstemDir: process.env.BRAINSTEM_BETA_SOURCE_DIR
          || path.join(os.homedir(), ".brainstem", "src", "rapp_brainstem"),
        ...options,
      });
  return defaultStore;
}

function configuredStore() {
  return defaultStore || configureLineageStore();
}

export function baselineAncestors() {
  return configuredStore().baselineAncestors();
}

export function listRings(ancestorRappid) {
  return configuredStore().listRings(ancestorRappid);
}

export function appendRing(ancestorRappid, frame) {
  return configuredStore().appendRing(ancestorRappid, frame);
}

export function getHead(ancestorRappid) {
  return configuredStore().getHead(ancestorRappid);
}

export function setHead(ancestorRappid, ringRappid) {
  return configuredStore().setHead(ancestorRappid, ringRappid);
}

export function resolveLive(ancestorRappid) {
  return configuredStore().resolveLive(ancestorRappid);
}

export function rollbackToBaseline(ancestorRappid = null) {
  return configuredStore().rollbackToBaseline(ancestorRappid);
}

export function restore(ancestorRappid = null) {
  return configuredStore().restore(ancestorRappid);
}

export function verifyChain(ancestorRappid) {
  return configuredStore().verifyChain(ancestorRappid);
}

export function inspectLineage(ancestorRappid) {
  return configuredStore().inspectLineage(ancestorRappid);
}
