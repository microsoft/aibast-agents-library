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
});

test("lineage-store HEAD, unverified fallback, rollback, and restore are reversible", (t) => {
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
  store.setHead(alpha.ancestorRappid, unverified);
  assert.equal(store.getHead(alpha.ancestorRappid), unverified);
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
