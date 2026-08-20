import assert from "node:assert/strict";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
  LineageStore,
  baselineAncestors,
  configureLineageStore,
  lineageStoreInternals,
} from "../electron/lineage-store.mjs";


function fixture(t) {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-lineage-store-"));
  const brainstemDir = path.join(root, "brainstem");
  const agentsDirectory = path.join(brainstemDir, "agents");
  mkdirSync(agentsDirectory, { recursive: true });
  const sources = {
    "alpha_agent.py": "ALPHA = 'baseline'\n",
    "basic_agent.py": "class BasicAgent: pass\n",
    "context_memory_agent.py": "CONTEXT = 'baseline'\n",
  };
  for (const [filename, source] of Object.entries(sources)) {
    writeFileSync(path.join(agentsDirectory, filename), source);
  }
  let tick = 0;
  const store = new LineageStore({
    brainstemDir,
    root: path.join(root, "lineage"),
    now: () => `2026-01-01T00:00:0${tick++}.000Z`,
  });
  t.after(() => rmSync(root, { recursive: true, force: true }));
  return { root, store, sources };
}

function ringDirectory(store, ancestorRappid, ringRappid) {
  return path.join(
    store.root,
    lineageStoreInternals.filesystemSegment(ancestorRappid),
    "rings",
    lineageStoreInternals.filesystemSegment(ringRappid),
  );
}

test("lineage-store hash-chains deterministic rings and detects tampering", (t) => {
  const { store, sources } = fixture(t);
  const ancestors = store.baselineAncestors();
  configureLineageStore(store);
  assert.deepEqual(baselineAncestors(), ancestors);
  const alpha = ancestors.find((item) => item.filename === "alpha_agent.py");
  assert.ok(alpha);
  assert.equal(
    alpha.ancestorRappid,
    lineageStoreInternals.ancestorRappidFor(
      "alpha_agent.py",
      sources["alpha_agent.py"],
    ),
  );

  const source = "ALPHA = 'ring one'\n";
  const ringRappid = store.appendRing(alpha.ancestorRappid, {
    source,
    parentRappid: alpha.ancestorRappid,
    verified: true,
    meta: { author: "test", policy: "mutable" },
  });
  assert.equal(
    ringRappid,
    lineageStoreInternals.ringRappidFor(
      alpha.ancestorRappid,
      alpha.ancestorRappid,
      source,
      alpha.filename,
    ),
  );
  assert.equal(
    store.appendRing(alpha.ancestorRappid, {
      source,
      parentRappid: alpha.ancestorRappid,
      verified: true,
      meta: { author: "test" },
    }),
    ringRappid,
    "the same parent/source/ancestor frame must mint the same ring RAPPID",
  );
  assert.equal(store.listRings(alpha.ancestorRappid).length, 2);
  assert.equal(store.verifyChain(alpha.ancestorRappid), true);

  store.setHead(alpha.ancestorRappid, ringRappid);
  assert.deepEqual(store.resolveLive(alpha.ancestorRappid), {
    ringRappid,
    source,
    isBaseline: false,
  });

  writeFileSync(
    path.join(ringDirectory(store, alpha.ancestorRappid, ringRappid), "source.py"),
    "ALPHA = 'tampered'\n",
  );
  assert.equal(store.verifyChain(alpha.ancestorRappid), false);
  assert.deepEqual(store.resolveLive(alpha.ancestorRappid), {
    ringRappid: alpha.ancestorRappid,
    source: sources["alpha_agent.py"],
    isBaseline: true,
  });
  store.rollbackToBaseline(alpha.ancestorRappid);
  assert.throws(
    () => store.setHead(alpha.ancestorRappid, ringRappid),
    /invalid or unverified molt ring/,
  );
  assert.equal(store.getHead(alpha.ancestorRappid), alpha.ancestorRappid);
});

test("lineage-store HEAD rejects unverified rings; rollback and restore are reversible", (t) => {
  const { store, sources } = fixture(t);
  const [alpha, context] = ["alpha_agent.py", "context_memory_agent.py"].map(
    (filename) => store.baselineAncestors().find(
      (item) => item.filename === filename,
    ),
  );

  const unverified = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'unverified'\n",
    parentRappid: alpha.ancestorRappid,
    verified: false,
    meta: { author: "test" },
  });
  assert.throws(
    () => store.setHead(alpha.ancestorRappid, unverified),
    /invalid or unverified molt ring/,
  );
  assert.equal(store.getHead(alpha.ancestorRappid), alpha.ancestorRappid);
  assert.deepEqual(store.resolveLive(alpha.ancestorRappid), {
    ringRappid: alpha.ancestorRappid,
    source: sources["alpha_agent.py"],
    isBaseline: true,
  });
  assert.throws(
    () => store.appendRing(alpha.ancestorRappid, {
      source: "ALPHA = 'invalid child'\n",
      parentRappid: unverified,
      verified: true,
      meta: { author: "test" },
    }),
    /valid parent/,
  );

  const first = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'verified one'\n",
    parentRappid: alpha.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  const second = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'verified two'\n",
    parentRappid: first,
    verified: true,
    meta: { author: "test" },
  });
  const contextRing = store.appendRing(context.ancestorRappid, {
    source: "CONTEXT = 'verified'\n",
    parentRappid: context.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  store.setHead(alpha.ancestorRappid, second);
  store.setHead(context.ancestorRappid, contextRing);

  store.rollbackToBaseline(null);
  assert.equal(store.getHead(alpha.ancestorRappid), alpha.ancestorRappid);
  assert.equal(store.getHead(context.ancestorRappid), context.ancestorRappid);
  store.restore(null);
  assert.equal(store.getHead(alpha.ancestorRappid), second);
  assert.equal(store.getHead(context.ancestorRappid), contextRing);

  const locus = JSON.parse(readFileSync(path.join(
    store.root,
    lineageStoreInternals.filesystemSegment(alpha.ancestorRappid),
    "locus.json",
  )));
  assert.equal(locus.policy, "mutable");
  assert.equal(
    existsSync(path.join(
      ringDirectory(store, alpha.ancestorRappid, second),
      "meta.json",
    )),
    true,
  );
});

test("re-appending an existing ring can promote it to verified", (t) => {
  const { store } = fixture(t);
  const alpha = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  const frame = {
    source: "ALPHA = 'candidate'\n",
    parentRappid: alpha.ancestorRappid,
    verified: false,
    meta: { author: "test" },
  };
  const ring = store.appendRing(alpha.ancestorRappid, frame);
  assert.equal(
    store.listRings(alpha.ancestorRappid)
      .find((candidate) => candidate.ringRappid === ring).verified,
    false,
  );

  assert.equal(
    store.appendRing(alpha.ancestorRappid, {
      ...frame,
      verified: true,
      meta: { verifiedBy: "molter._verify" },
    }),
    ring,
  );
  const promoted = store.listRings(alpha.ancestorRappid)
    .find((candidate) => candidate.ringRappid === ring);
  assert.equal(promoted.verified, true);
  assert.deepEqual(promoted.meta, {
    author: "test",
    verifiedBy: "molter._verify",
  });
  assert.doesNotThrow(() => store.setHead(alpha.ancestorRappid, ring));
  assert.equal(store.resolveLive(alpha.ancestorRappid).ringRappid, ring);
});

test("a corrupt ring meta.json is skipped: restore and resolve stay fail-safe", (t) => {
  const { store, sources } = fixture(t);
  const alpha = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  const firstSource = "ALPHA = 'verified one'\n";
  const first = store.appendRing(alpha.ancestorRappid, {
    source: firstSource,
    parentRappid: alpha.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  const second = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'verified two'\n",
    parentRappid: first,
    verified: true,
    meta: { author: "test" },
  });
  store.setHead(alpha.ancestorRappid, second);

  writeFileSync(
    path.join(ringDirectory(store, alpha.ancestorRappid, second), "meta.json"),
    "{ truncated",
  );
  assert.deepEqual(
    store.listRings(alpha.ancestorRappid).map((ring) => ring.ringRappid),
    [alpha.ancestorRappid, first],
    "a corrupt ring must be treated as absent, never thrown",
  );
  assert.deepEqual(store.resolveLive(alpha.ancestorRappid), {
    ringRappid: alpha.ancestorRappid,
    source: sources["alpha_agent.py"],
    isBaseline: true,
  });
  assert.doesNotThrow(() => store.restore(null));
  assert.equal(store.getHead(alpha.ancestorRappid), first);
  assert.deepEqual(store.resolveLive(alpha.ancestorRappid), {
    ringRappid: first,
    source: firstSource,
    isBaseline: false,
  });
  assert.equal(
    store.verifyChain(alpha.ancestorRappid),
    true,
    "the corrupt ring is absent, so the surviving chain still verifies",
  );

  writeFileSync(
    path.join(ringDirectory(store, alpha.ancestorRappid, first), "meta.json"),
    "{ truncated",
  );
  assert.doesNotThrow(() => store.restore(null));
  assert.equal(store.getHead(alpha.ancestorRappid), alpha.ancestorRappid);
  assert.deepEqual(store.resolveLive(alpha.ancestorRappid), {
    ringRappid: alpha.ancestorRappid,
    source: sources["alpha_agent.py"],
    isBaseline: true,
  });
});

test("ring directory segments stay under Windows MAX_PATH on a realistic beta home", (t) => {
  const { store } = fixture(t);
  const alpha = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  const ring = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'ring one'\n",
    parentRappid: alpha.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  const segment = lineageStoreInternals.filesystemSegment(ring);
  assert.match(segment, /^[0-9a-f]{32}$/);
  assert.equal(
    segment,
    lineageStoreInternals.filesystemSegment(ring),
    "the same rappid must always map to the same on-disk segment",
  );

  // Only the directory name shortens — full rappids stay inside the metadata.
  const meta = JSON.parse(readFileSync(
    path.join(ringDirectory(store, alpha.ancestorRappid, ring), "meta.json"),
    "utf8",
  ));
  assert.equal(meta.ringRappid, ring);
  assert.equal(meta.ancestorRappid, alpha.ancestorRappid);
  const locus = JSON.parse(readFileSync(path.join(
    store.root,
    lineageStoreInternals.filesystemSegment(alpha.ancestorRappid),
    "locus.json",
  )));
  assert.equal(locus.ancestorRappid, alpha.ancestorRappid);

  // Deepest on-disk path (staging meta.json) for a realistic Windows beta
  // home must clear stock MAX_PATH (260) with headroom — target < 200.
  const realisticRoot =
    "C:\\Users\\kodywildfeuer\\.brainstem\\beta-launcher\\lineage";
  const deepest = [
    realisticRoot,
    lineageStoreInternals.filesystemSegment(alpha.ancestorRappid),
    "rings",
    `.${segment}.9999999.${Date.now()}.stage`,
    "meta.json",
  ].join("\\");
  assert.ok(
    deepest.length < 200,
    `deepest store path must stay under 200 chars, got ${deepest.length}`,
  );
});

test("a CRLF checkout mints the same identity as its LF form", (t) => {
  const { store, sources } = fixture(t);
  const lfAlpha = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  const crlfRoot = mkdtempSync(path.join(tmpdir(), "rapp-lineage-crlf-"));
  t.after(() => rmSync(crlfRoot, { recursive: true, force: true }));
  const crlfBrainstem = path.join(crlfRoot, "brainstem");
  mkdirSync(path.join(crlfBrainstem, "agents"), { recursive: true });
  writeFileSync(
    path.join(crlfBrainstem, "agents", "alpha_agent.py"),
    sources["alpha_agent.py"].replaceAll("\n", "\r\n"),
  );
  const crlfStore = new LineageStore({
    brainstemDir: crlfBrainstem,
    root: path.join(crlfRoot, "lineage"),
  });
  const crlfAlpha = crlfStore.baselineAncestors()[0];
  assert.equal(
    crlfAlpha.ancestorRappid,
    lfAlpha.ancestorRappid,
    "git autocrlf must not fork the ancestor identity",
  );
  assert.equal(crlfAlpha.sha256, lfAlpha.sha256);
  assert.equal(
    lineageStoreInternals.sourceSha256("A = 1\r\nB = 2\r\n"),
    lineageStoreInternals.sourceSha256("A = 1\nB = 2\n"),
  );

  const ringFrame = (source) => ({
    source,
    parentRappid: lfAlpha.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  const lfRing = store.appendRing(
    lfAlpha.ancestorRappid,
    ringFrame("ALPHA = 'ring one'\n"),
  );
  const crlfRing = crlfStore.appendRing(
    crlfAlpha.ancestorRappid,
    ringFrame("ALPHA = 'ring one'\r\n"),
  );
  assert.equal(
    crlfRing,
    lfRing,
    "the same molt must have the same ring rappid on every platform",
  );
});

test("kill switch gates HEAD WRITES too: safe words cannot silently move rings", (t) => {
  const { store } = fixture(t);
  const alpha = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  const ring = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'molt'\n",
    parentRappid: alpha.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  store.setHead(alpha.ancestorRappid, ring);

  // Operator flips the kill switch. `baseline`/`restore` must NOT write HEAD —
  // otherwise the moved HEADs survive and silently activate molts once the flag
  // is cleared again.
  const previous = process.env.RAPP_MOLT_LINEAGE;
  process.env.RAPP_MOLT_LINEAGE = "0";
  t.after(() => {
    if (previous === undefined) delete process.env.RAPP_MOLT_LINEAGE;
    else process.env.RAPP_MOLT_LINEAGE = previous;
  });

  const rollback = store.rollbackToBaseline(null);
  assert.equal(rollback.disabled, true, "rollback reports the layer is off");
  assert.deepEqual(rollback.changed, [], "no HEAD was moved");
  const restored = store.restore(null);
  assert.equal(restored.disabled, true, "restore reports the layer is off");
  assert.deepEqual(restored.changed, [], "no HEAD was moved");

  // HEAD is untouched, so clearing the flag restores the operator's real state.
  assert.equal(store.getHead(alpha.ancestorRappid), ring);
  delete process.env.RAPP_MOLT_LINEAGE;
  assert.equal(store.resolveLive(alpha.ancestorRappid).ringRappid, ring);
});

test("a failing locus never aborts a fleet-wide rollback", (t) => {
  const { store } = fixture(t);
  const ancestors = store.baselineAncestors();
  assert.ok(ancestors.length >= 2, "fixture needs multiple loci");
  const failing = ancestors[0].ancestorRappid;

  // One locus cannot have its HEAD written. The safe word must still land every
  // other agent on baseline instead of throwing out mid-fleet and leaving them molted.
  const realSetHead = store.setHead.bind(store);
  store.setHead = (ancestorRappid, ringRappid) => {
    if (ancestorRappid === failing) throw new Error("simulated HEAD write failure");
    return realSetHead(ancestorRappid, ringRappid);
  };

  let report;
  assert.doesNotThrow(() => { report = store.rollbackToBaseline(null); });
  assert.equal(report.failed.length, 1, "the failing locus is reported, not hidden");
  assert.equal(report.failed[0].ancestorRappid, failing);
  // A locus already sitting at baseline is reported as unchanged rather than
  // changed — that split is what lets `restore` tell a real recovery from a
  // no-op. Either way every healthy locus ended up at baseline.
  assert.equal(
    report.changed.length + report.unchanged.length,
    ancestors.length - 1,
    "every healthy locus still ended at baseline",
  );
});

test("inspectLineage surfaces on-disk corruption that verifyChain does not answer for", (t) => {
  const { store } = fixture(t);
  const alpha = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  const first = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'one'\n",
    parentRappid: alpha.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  const second = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'two'\n",
    parentRappid: first,
    verified: true,
    meta: { author: "test" },
  });
  store.setHead(alpha.ancestorRappid, first);
  assert.equal(store.inspectLineage(alpha.ancestorRappid).healthy, true);

  writeFileSync(
    path.join(ringDirectory(store, alpha.ancestorRappid, second), "meta.json"),
    "{ truncated",
  );
  const report = store.inspectLineage(alpha.ancestorRappid);
  assert.equal(report.corruptRings, 1, "corruption is counted, not silently dropped");
  assert.equal(report.healthy, false, "the locus is reported unhealthy");
  // Composition stays fail-safe regardless: the reachable chain still verifies.
  assert.equal(report.chainOk, true);
  assert.equal(store.resolveLive(alpha.ancestorRappid).ringRappid, first);
});

test("a pinned locus never molts while its siblings molt freely", (t) => {
  const { store, sources } = fixture(t);
  const ancestors = store.baselineAncestors();
  const memory = ancestors.find(
    (item) => item.filename === "context_memory_agent.py",
  );
  const news = ancestors.find((item) => item.filename === "alpha_agent.py");

  // Pin memory at its Grail baseline; leave the other locus mutable.
  assert.equal(store.setLocusPolicy(memory.ancestorRappid, "pinned"), "pinned");
  assert.equal(store.locusPolicy(memory.ancestorRappid), "pinned");
  assert.equal(store.locusPolicy(news.ancestorRappid), "mutable");

  // A ring may still be recorded for the pinned locus (history is append-only),
  // but it can never be made live.
  const memoryRing = store.appendRing(memory.ancestorRappid, {
    source: "CONTEXT = 'molted'\n",
    parentRappid: memory.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  assert.throws(
    () => store.setHead(memory.ancestorRappid, memoryRing),
    /pinned/,
    "a pinned locus refuses to move HEAD off baseline",
  );
  assert.deepEqual(store.resolveLive(memory.ancestorRappid), {
    ringRappid: memory.ancestorRappid,
    source: sources["context_memory_agent.py"],
    isBaseline: true,
  });

  // The sibling locus molts normally on its own timeline.
  const newsRing = store.appendRing(news.ancestorRappid, {
    source: "ALPHA = 'today'\n",
    parentRappid: news.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  store.setHead(news.ancestorRappid, newsRing);
  assert.equal(store.resolveLive(news.ancestorRappid).isBaseline, false);

  // A fleet-wide restore must not fight the pin, and must not report it failed.
  const report = store.restore(null);
  assert.deepEqual(report.failed, [], "pinning is honored, not an error");
  assert.equal(
    store.resolveLive(memory.ancestorRappid).isBaseline,
    true,
    "memory stayed at baseline through a fleet restore",
  );
  assert.equal(store.resolveLive(news.ancestorRappid).ringRappid, newsRing);
});

test("restore returns to where you were, not to whatever is newest", (t) => {
  const { store } = fixture(t);
  const alpha = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  const first = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'one'\n",
    parentRappid: alpha.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  const second = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'two'\n",
    parentRappid: first,
    verified: true,
    meta: { author: "test" },
  });

  // The user deliberately parks on the OLDER generation.
  store.setHead(alpha.ancestorRappid, first);
  assert.equal(store.getHead(alpha.ancestorRappid), first);

  // Safe word: back to factory.
  store.rollbackToBaseline(alpha.ancestorRappid);
  assert.equal(store.resolveLive(alpha.ancestorRappid).isBaseline, true);

  // Restore must bring them back to where they actually were — fast-forwarding
  // to `second` would silently discard a deliberate choice.
  store.restore(alpha.ancestorRappid);
  assert.equal(
    store.getHead(alpha.ancestorRappid),
    first,
    "restore is the inverse of baseline, not a fast-forward",
  );
  assert.notEqual(store.getHead(alpha.ancestorRappid), second);
});

test("restore still fast-forwards when there is no displaced generation", (t) => {
  const { store } = fixture(t);
  const alpha = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  const ring = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'only'\n",
    parentRappid: alpha.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  // Never molted, never rolled back: restore adopts the newest verified ring.
  store.restore(alpha.ancestorRappid);
  assert.equal(store.getHead(alpha.ancestorRappid), ring);
});

test("a Grail upgrade does not orphan the user's lineage", (t) => {
  const { store, root } = fixture(t);
  const agentsDir = path.join(root, "brainstem", "agents");
  const before = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  const ring = store.appendRing(before.ancestorRappid, {
    source: "ALPHA = 'my tweak'\n",
    parentRappid: before.ancestorRappid,
    verified: true,
    meta: { author: "user" },
  });
  store.setHead(before.ancestorRappid, ring);
  assert.equal(store.resolveLive(before.ancestorRappid).isBaseline, false);

  // Grail ships a new version: the factory agent's bytes change. This is a
  // routine upgrade and it must not cost the user their molts.
  writeFileSync(path.join(agentsDir, "alpha_agent.py"), "ALPHA = 'baseline v2'\n");
  const after = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  assert.equal(
    after.ancestorRappid,
    before.ancestorRappid,
    "locus identity must survive a baseline update",
  );
  assert.notEqual(after.sha256, before.sha256, "the baseline really did change");
  assert.equal(
    store.getHead(after.ancestorRappid),
    ring,
    "HEAD still points at the user's molt",
  );
  assert.equal(store.resolveLive(after.ancestorRappid).isBaseline, false);
  assert.equal(store.listRings(after.ancestorRappid).length, 2, "history intact");

  // ...and reverting now lands on the NEW baseline, which is the point.
  store.rollbackToBaseline(after.ancestorRappid);
  assert.equal(
    store.resolveLive(after.ancestorRappid).source,
    "ALPHA = 'baseline v2'\n",
  );
});

test("a store written under the legacy content-derived id migrates, not orphans", (t) => {
  const { store, root } = fixture(t);
  const alpha = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  // Forge a legacy locus: same shape, but keyed by an id that is not current.
  const legacyAncestor = "rappid:@grail/alpha:" + "d".repeat(64);
  const legacyDir = path.join(
    store.root, lineageStoreInternals.filesystemSegment(legacyAncestor));
  const legacyRing = "rappid:@frontier/alpha-ring:" + "e".repeat(64);
  const ringDir = path.join(
    legacyDir, "rings", lineageStoreInternals.filesystemSegment(legacyRing));
  mkdirSync(ringDir, { recursive: true });
  writeFileSync(path.join(legacyDir, "locus.json"), JSON.stringify({
    schema: "molt-lineage/1.0",
    ancestorRappid: legacyAncestor,
    filename: "alpha_agent.py",
  }));
  writeFileSync(path.join(legacyDir, "HEAD"), legacyRing + "\n");
  writeFileSync(path.join(ringDir, "source.py"), "ALPHA = 'grown before the fix'\n");
  writeFileSync(path.join(ringDir, "meta.json"), JSON.stringify({
    ringRappid: legacyRing,
    parentRappid: legacyAncestor,
    ancestorRappid: legacyAncestor,
    verified: true,
    createdAt: "2026-01-01T00:00:00.000Z",
    meta: { author: "user" },
  }));

  // A fresh store must adopt that history rather than leave it stranded.
  const reopened = new LineageStore({
    brainstemDir: path.join(root, "brainstem"),
    root: store.root,
  });
  const current = reopened.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  assert.equal(current.ancestorRappid, alpha.ancestorRappid);
  const live = reopened.resolveLive(current.ancestorRappid);
  assert.equal(
    live.source,
    "ALPHA = 'grown before the fix'\n",
    "the pre-fix molt survived migration and is live again",
  );
  assert.equal(live.isBaseline, false);
  // Non-destructive: the legacy directory is set aside, never deleted.
  assert.equal(existsSync(legacyDir), false);
  assert.ok(existsSync(path.join(
    store.root,
    ".migrated-" + lineageStoreInternals.filesystemSegment(legacyAncestor))));
});

test("a restore that recovers nothing is not reported as a restore", (t) => {
  const { store } = fixture(t);
  const alpha = store.baselineAncestors().find(
    (item) => item.filename === "alpha_agent.py",
  );
  // No rings were ever grown: there is genuinely nothing to come back to.
  const report = store.restore(alpha.ancestorRappid);
  assert.deepEqual(report.changed, [], "a no-op must not be reported as a change");
  assert.equal(report.unchanged.length, 1, "it is reported as unchanged, not silently");
  assert.deepEqual(report.failed, []);

  // A real recovery still reports as one.
  const ring = store.appendRing(alpha.ancestorRappid, {
    source: "ALPHA = 'grown'\n",
    parentRappid: alpha.ancestorRappid,
    verified: true,
    meta: { author: "user" },
  });
  store.setHead(alpha.ancestorRappid, ring);
  store.rollbackToBaseline(alpha.ancestorRappid);
  const real = store.restore(alpha.ancestorRappid);
  assert.deepEqual(real.changed, [alpha.ancestorRappid], "a real restore is a change");
  assert.equal(store.getHead(alpha.ancestorRappid), ring);
});
