// Pins the molt-lineage/1.0 store contract (beta/docs/MOLT-LINEAGE-PROTOCOL.md):
// deterministic content-addressed rappids, env-scoped HEADs over one shared ring
// store, fail-safe passthrough resolution, gated fast-forward-only promotion with
// named conflicts, drift detection, and the tamper-evident promotion journal.
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { lineageStoreInternals } from "../electron/lineage-store.mjs";
import {
  ancestorRappidFor,
  MoltLineageStore,
  ringRappidFor,
} from "../electron/molt-lineage.mjs";

const BASELINE = "from agents.basic_agent import BasicAgent\n\nclass EchoAgent(BasicAgent):\n    def perform(self, **kwargs):\n        return 'baseline'\n";
const MOLT_1 = BASELINE.replace("'baseline'", "'ring one'");
const MOLT_2 = BASELINE.replace("'baseline'", "'ring two'");
const MOLT_PROD_ONLY = BASELINE.replace("'baseline'", "'prod hotfix'");

function freshStore(opts = {}) {
  const root = mkdtempSync(path.join(os.tmpdir(), "molt-lineage-test-"));
  const store = new MoltLineageStore({ root, ...opts });
  return { store, root, cleanup: () => rmSync(root, { recursive: true, force: true }) };
}

test("rappids are deterministic: same molt has the same identity everywhere", () => {
  const a1 = ancestorRappidFor("echo_agent.py", BASELINE);
  const a2 = ancestorRappidFor("echo_agent.py", BASELINE);
  assert.equal(a1, a2);
  const r1 = ringRappidFor(a1, null, MOLT_1, "echo_agent.py");
  const r2 = ringRappidFor(a1, null, MOLT_1, "echo_agent.py");
  assert.equal(r1, r2);
  // Different bytes, different parent, or different ancestor => different ring rappid.
  assert.notEqual(r1, ringRappidFor(a1, null, MOLT_2, "echo_agent.py"));
  assert.notEqual(r1, ringRappidFor(a1, r1, MOLT_1, "echo_agent.py"));
});

test("identity is unified with the wired lineage-store: same molt bytes, same rappid in both modules", () => {
  // The ALM layer delegates to the exact derivations the live routed store
  // mints with — the protocol's cross-environment identity invariant holds
  // ACROSS modules, not just within one.
  const ancestor = ancestorRappidFor("echo_agent.py", BASELINE);
  assert.equal(
    ancestor,
    lineageStoreInternals.ancestorRappidFor("echo_agent.py", BASELINE),
  );
  const ring = ringRappidFor(ancestor, ancestor, MOLT_1, "echo_agent.py");
  assert.equal(
    ring,
    lineageStoreInternals.ringRappidFor(ancestor, ancestor, MOLT_1, "echo_agent.py"),
  );
  // A first ring appended with no explicit parent descends from the ancestor —
  // the live store's parent convention — so the stored ring carries the same
  // rappid the running app would mint for the same first molt.
  const { store, cleanup } = freshStore();
  try {
    const registered = store.registerAncestor("echo_agent.py", BASELINE);
    assert.equal(registered, ancestor);
    assert.equal(store.appendRing(ancestor, { source: MOLT_1, verified: true }), ring);
  } finally {
    cleanup();
  }
});

test("passthrough by default: unknown agent, no HEAD, and kill-switch all resolve to baseline", () => {
  const { store, cleanup } = freshStore();
  try {
    assert.equal(store.resolveLive("never_registered_agent.py"), null);
    const ancestor = store.registerAncestor("echo_agent.py", BASELINE);
    assert.ok(ancestor);
    // Registered but no live molt -> still baseline.
    assert.equal(store.resolveLive("echo_agent.py"), null);
    const ring = store.appendRing(ancestor, { source: MOLT_1, verified: true });
    assert.ok(store.setHead(ancestor, ring));
    assert.equal(store.resolveLive("echo_agent.py").source, MOLT_1);
    // Kill-switch forces pure Grail passthrough even with a live verified molt.
    const killed = new MoltLineageStore({ root: store.root, enabled: false });
    assert.equal(killed.resolveLive("echo_agent.py"), null);
  } finally {
    cleanup();
  }
});

test("an unverified ring can never go live, and a tampered ring resolves to baseline", () => {
  const { store, root, cleanup } = freshStore();
  try {
    const ancestor = store.registerAncestor("echo_agent.py", BASELINE);
    const unverified = store.appendRing(ancestor, { source: MOLT_1, verified: false });
    assert.equal(store.setHead(ancestor, unverified), false);
    assert.equal(store.resolveLive("echo_agent.py"), null);

    const ring = store.appendRing(ancestor, { source: MOLT_2, verified: true });
    assert.ok(store.setHead(ancestor, ring));
    // Tamper with the stored source bytes on disk: getRing must refuse the ring
    // (sha + rappid re-derivation fail) and resolution falls back to baseline.
    const key = /:([0-9a-f]{64})$/.exec(ring)[1];
    const ringFile = path.join(root, /:([0-9a-f]{64})$/.exec(ancestor)[1], "rings", `${key}.json`);
    const rec = JSON.parse(readFileSync(ringFile, "utf8"));
    rec.source = rec.source.replace("ring two", "evil payload");
    writeFileSync(ringFile, JSON.stringify(rec));
    assert.equal(store.getRing(ancestor, ring), null);
    assert.equal(store.resolveLive("echo_agent.py"), null);
  } finally {
    cleanup();
  }
});

test("Benjamin Button: HEAD walks back to any ring or to baseline, non-destructively", () => {
  const { store, cleanup } = freshStore();
  try {
    const ancestor = store.registerAncestor("echo_agent.py", BASELINE);
    const r1 = store.appendRing(ancestor, { source: MOLT_1, verified: true });
    const r2 = store.appendRing(ancestor, { source: MOLT_2, parentRappid: r1, verified: true });
    assert.ok(store.setHead(ancestor, r2));
    assert.deepEqual(store.walk(ancestor, r2), [r1, r2]);
    // Back one ring, then to birth; every ring is retained throughout.
    assert.ok(store.setHead(ancestor, r1));
    assert.equal(store.resolveLive("echo_agent.py").source, MOLT_1);
    assert.ok(store.rollbackToBaseline(ancestor));
    assert.equal(store.resolveLive("echo_agent.py"), null);
    assert.equal(store.listRings(ancestor).length, 2);
    // Grow up again: HEAD forward to the retained later ring.
    assert.ok(store.setHead(ancestor, r2));
    assert.equal(store.resolveLive("echo_agent.py").source, MOLT_2);
  } finally {
    cleanup();
  }
});

test("environments are HEADs, not copies: dev and prod pin into one shared ring store", () => {
  const { store, cleanup } = freshStore();
  try {
    const ancestor = store.registerAncestor("echo_agent.py", BASELINE);
    const r1 = store.appendRing(ancestor, { source: MOLT_1, verified: true });
    assert.ok(store.setHead(ancestor, r1, "dev"));
    assert.equal(store.resolveLive("echo_agent.py", "dev").ringRappid, r1);
    // prod is untouched by dev's HEAD move — same store, independent pointer.
    assert.equal(store.resolveLive("echo_agent.py", "prod"), null);
    assert.equal(store.head(ancestor, "prod"), null);
  } finally {
    cleanup();
  }
});

test("promotion fast-forwards when the target has not diverged", () => {
  const { store, cleanup } = freshStore();
  try {
    const ancestor = store.registerAncestor("echo_agent.py", BASELINE);
    const r1 = store.appendRing(ancestor, { source: MOLT_1, verified: true });
    const r2 = store.appendRing(ancestor, { source: MOLT_2, parentRappid: r1, verified: true });
    store.setHead(ancestor, r2, "dev");
    // prod at baseline -> trivial fast-forward.
    let res = store.promote(ancestor, { fromEnv: "dev", toEnv: "prod", actor: "alice" });
    assert.equal(res.ok, true);
    assert.equal(res.reason, "fast-forward");
    assert.equal(store.head(ancestor, "prod"), r2);
    // Re-promoting in-sync envs is a recorded no-op, not an error.
    res = store.promote(ancestor, { fromEnv: "dev", toEnv: "prod", actor: "alice" });
    assert.equal(res.ok, true);
    assert.equal(res.noop, true);
    // prod behind on the same path (at r1) also fast-forwards.
    store.setHead(ancestor, r1, "prod");
    res = store.promote(ancestor, { fromEnv: "dev", toEnv: "prod", actor: "alice" });
    assert.equal(res.ok, true);
    assert.equal(store.head(ancestor, "prod"), r2);
  } finally {
    cleanup();
  }
});

test("the ALM scenario: a prod-only molt makes promotion a named CONFLICT, never a silent overwrite", () => {
  const { store, cleanup } = freshStore();
  try {
    const ancestor = store.registerAncestor("echo_agent.py", BASELINE);
    const r1 = store.appendRing(ancestor, { source: MOLT_1, verified: true });
    // Someone molts directly in prod off r1...
    const prodOnly = store.appendRing(ancestor, { source: MOLT_PROD_ONLY, parentRappid: r1, verified: true });
    store.setHead(ancestor, prodOnly, "prod");
    // ...while dev builds a different layer off the same base.
    const devRing = store.appendRing(ancestor, { source: MOLT_2, parentRappid: r1, verified: true });
    store.setHead(ancestor, devRing, "dev");
    const res = store.promote(ancestor, { fromEnv: "dev", toEnv: "prod", actor: "bob" });
    assert.equal(res.ok, false);
    assert.equal(res.conflict, true);
    // The refusal names both diverging rappids and their common ancestor.
    assert.equal(res.target_head, prodOnly);
    assert.equal(res.source_head, devRing);
    assert.equal(res.common_ancestor, r1);
    // Prod's HEAD is untouched — the break surfaced at promote time, not runtime.
    assert.equal(store.head(ancestor, "prod"), prodOnly);
    // Drift detection reports the same divergence before any promotion runs.
    const drift = store.detectDrift(ancestor, "prod", r1);
    assert.equal(drift.drifted, true);
    assert.equal(drift.actual, prodOnly);
  } finally {
    cleanup();
  }
});

test("every promotion attempt lands in an internally verified hash chain", () => {
  const { store, root, cleanup } = freshStore();
  try {
    const ancestor = store.registerAncestor("echo_agent.py", BASELINE);
    const r1 = store.appendRing(ancestor, { source: MOLT_1, verified: true });
    const prodOnly = store.appendRing(ancestor, { source: MOLT_PROD_ONLY, parentRappid: r1, verified: true });
    store.setHead(ancestor, r1, "dev");
    store.promote(ancestor, { fromEnv: "dev", toEnv: "prod", actor: "alice", utc: "2026-08-19T00:00:00Z" });
    store.setHead(ancestor, prodOnly, "prod");
    store.setHead(ancestor, r1, "dev");
    store.promote(ancestor, { fromEnv: "dev", toEnv: "prod", actor: "bob", utc: "2026-08-19T00:01:00Z" });

    const log = store.listPromotions(ancestor);
    assert.equal(log.length, 2);
    assert.equal(log[0].actor, "alice");
    assert.equal(log[0].ok, true);
    assert.equal(log[1].actor, "bob");
    assert.equal(log[1].conflict, true);
    assert.equal(log[1].prev_entry_sha256, log[0].entry_sha256);
    assert.deepEqual(store.verifyPromotions(ancestor), { ok: true, entries: 2 });

    // Rewriting history breaks the chain and is detected with the entry index.
    const file = path.join(root, /:([0-9a-f]{64})$/.exec(ancestor)[1], "promotions.json");
    const tampered = JSON.parse(readFileSync(file, "utf8"));
    tampered[0].actor = "mallory";
    writeFileSync(file, JSON.stringify(tampered));
    assert.deepEqual(store.verifyPromotions(ancestor), { ok: false, broken_at: 0 });
  } finally {
    cleanup();
  }
});

test("a corrupt promotion journal fails closed: promote refuses to move HEAD and verify reports the corruption", () => {
  const { store, root, cleanup } = freshStore();
  try {
    const ancestor = store.registerAncestor("echo_agent.py", BASELINE);
    const r1 = store.appendRing(ancestor, { source: MOLT_1, verified: true });
    assert.ok(store.setHead(ancestor, r1, "dev"));
    const file = path.join(root, /:([0-9a-f]{64})$/.exec(ancestor)[1], "promotions.json");

    // Truthy-non-array JSON ('{}') and truncated JSON are both corruption — the
    // exact shapes that used to slip through as an empty journal and verify ok.
    for (const corruptBytes of ["{}", "{ truncated"]) {
      writeFileSync(file, corruptBytes);
      const res = store.promote(ancestor, { fromEnv: "dev", toEnv: "prod", actor: "carol" });
      assert.equal(res.ok, false);
      assert.equal(res.journal_corrupt, true);
      assert.match(res.reason, /journal is corrupt/);
      // No HEAD moved: prod stays at baseline, the would-be fast-forward refused.
      assert.equal(store.head(ancestor, "prod"), null);
      assert.equal(store.resolveLive("echo_agent.py", "prod"), null);
      // The audit check flags the corruption instead of reporting ok...
      const verdict = store.verifyPromotions(ancestor);
      assert.equal(verdict.ok, false);
      assert.equal(verdict.corrupt, true);
      // ...and the corrupt bytes are preserved as evidence, never appended over.
      assert.equal(readFileSync(file, "utf8"), corruptBytes);
      assert.deepEqual(store.listPromotions(ancestor), []);
    }

    // Restoring a valid journal restores promotion — fail-closed, not bricked.
    rmSync(file);
    const recovered = store.promote(ancestor, { fromEnv: "dev", toEnv: "prod", actor: "carol" });
    assert.equal(recovered.ok, true);
    assert.equal(store.head(ancestor, "prod"), r1);
    assert.deepEqual(store.verifyPromotions(ancestor), { ok: true, entries: 1 });
  } finally {
    cleanup();
  }
});
