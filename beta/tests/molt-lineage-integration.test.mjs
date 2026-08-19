import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { homedir, tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import { LineageStore } from "../electron/lineage-store.mjs";
import {
  BetaRouteManager,
  routeManagerInternals,
} from "../electron/route-manager.mjs";


const betaRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = path.resolve(betaRoot, "..");
const grailDirectory = path.join(repositoryRoot, "rapp_brainstem");
const grailContextPath = path.join(
  grailDirectory,
  "agents",
  "context_memory_agent.py",
);
const ring1Path = path.join(
  betaRoot,
  "electron",
  "rings",
  "context_memory_agent.ring1.py",
);

function integrationPython() {
  const candidates = [
    process.env.BRAINSTEM_BETA_PYTHON,
    path.join(homedir(), ".brainstem", "venv", "bin", "python"),
    path.join(grailDirectory, ".venv", "bin", "python"),
    "/usr/bin/python3",
  ].filter(Boolean);
  const selected = candidates.find((candidate) => existsSync(candidate));
  assert.ok(selected, "a Python interpreter is required for Grail dry-load tests");
  return selected;
}

function minimalFixture(t, { validator = () => true } = {}) {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-molt-integration-"));
  const brainstemDir = path.join(root, "brainstem");
  const agentsDirectory = path.join(brainstemDir, "agents");
  mkdirSync(agentsDirectory, { recursive: true });
  const sources = {
    "basic_agent.py": "class BasicAgent: pass\n",
    "context_memory_agent.py": "class ContextMemoryAgent: pass\n",
    "global_agent.py": "GLOBAL = 'baseline'\n",
    "manage_memory_agent.py": "class ManageMemoryAgent: pass\n",
  };
  for (const [filename, source] of Object.entries(sources)) {
    writeFileSync(path.join(agentsDirectory, filename), source);
  }
  const lineageRoot = path.join(root, "lineage");
  const store = new LineageStore({ brainstemDir, root: lineageRoot });
  const managerOptions = {
    betaHome: path.join(root, "beta-home"),
    brainstemConfig: { brainstemDir, python: "/tmp/python" },
    lineageRoot,
    lineageStore: store,
    seedLineageDefaults: false,
    compositionValidator: validator,
  };
  t.after(() => rmSync(root, { recursive: true, force: true }));
  return { root, sources, store, managerOptions };
}

function entryShape(descriptor) {
  return descriptor.entries.map((entry) => ({
    filename: entry.filename,
    address: entry.address,
    objectPath: entry.objectPath,
    scope: entry.scope,
    bytes: Buffer.from(entry.bytes || []),
  }));
}

function scanBrokenAgents(python, agentDirectory) {
  const source = [
    "import importlib.util",
    "import os",
    "import sys",
    "brainstem_dir, agents_dir = sys.argv[1:3]",
    "sys.path.insert(0, brainstem_dir)",
    "spec = importlib.util.spec_from_file_location('_scan_brainstem', os.path.join(brainstem_dir, 'brainstem.py'))",
    "brainstem = importlib.util.module_from_spec(spec)",
    "spec.loader.exec_module(brainstem)",
    "brainstem._register_shims()",
    "spec = importlib.util.spec_from_file_location('_routed_context', os.path.join(agents_dir, 'context_memory_agent.py'))",
    "context = importlib.util.module_from_spec(spec)",
    "spec.loader.exec_module(context)",
    "broken = context.scan_broken_agents(agents_dir)",
    "if broken:",
    "    sys.stderr.write(repr(broken))",
    "    raise SystemExit(1)",
  ].join("\n");
  return spawnSync(
    python,
    ["-c", source, grailDirectory, agentDirectory],
    {
      cwd: grailDirectory,
      encoding: "utf8",
      env: {
        ...process.env,
        PYTHONDONTWRITEBYTECODE: "1",
        PYTHONUTF8: "1",
      },
    },
  );
}

test("HARD 1 — zero molts compose byte-for-byte identically to legacy passthrough", (t) => {
  const { managerOptions } = minimalFixture(t);
  const legacy = new BetaRouteManager({
    ...managerOptions,
    lineageEnabled: false,
  });
  const enabled = new BetaRouteManager({
    ...managerOptions,
    lineageEnabled: true,
  });
  const legacyDescriptor = legacy.compositionDescriptor();
  const enabledDescriptor = enabled.compositionDescriptor();
  assert.equal(enabledDescriptor.compositionHash, legacyDescriptor.compositionHash);
  assert.deepEqual(entryShape(enabledDescriptor), entryShape(legacyDescriptor));
  assert.deepEqual(enabledDescriptor.lineageOverlays, []);

  const legacyMaterialized = legacy.materializeComposition(legacyDescriptor);
  const enabledMaterialized = enabled.materializeComposition(enabledDescriptor);
  assert.equal(
    enabledMaterialized.compositionDirectory,
    legacyMaterialized.compositionDirectory,
  );
  for (const entry of legacyDescriptor.entries) {
    assert.deepEqual(
      readFileSync(path.join(enabledMaterialized.agentDirectory, entry.filename)),
      readFileSync(path.join(legacyMaterialized.agentDirectory, entry.filename)),
    );
  }
});

test("HARD 2 — Grail remains blind to Molt Lineage", () => {
  const brainstem = readFileSync(
    path.join(grailDirectory, "brainstem.py"),
    "utf8",
  );
  assert.doesNotMatch(
    brainstem,
    /RAPP_MOLT_LINEAGE|lineage-store|rollbackToBaseline|molt-lineage/,
  );
});

test("HARD 3 — raw Grail stays pristine while ContextMemory ring 1 composes", (t) => {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-context-ring1-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const pristineBefore = readFileSync(grailContextPath, "utf8");
  const ring1 = readFileSync(ring1Path, "utf8");
  assert.doesNotMatch(pristineBefore, /^import ast$|^import glob$/m);
  assert.doesNotMatch(pristineBefore, /scan_broken_agents|_self_status_block/);
  assert.match(pristineBefore, /"""Inject stored memories into the system prompt each turn\."""/);

  const manager = new BetaRouteManager({
    betaHome: path.join(root, "beta-home"),
    brainstemConfig: {
      brainstemDir: grailDirectory,
      python: integrationPython(),
    },
    lineageRoot: path.join(root, "lineage"),
  });
  const ringDescriptor = manager.compositionDescriptor();
  const contextEntry = ringDescriptor.entries.find(
    (entry) => entry.filename === "context_memory_agent.py",
  );
  assert.ok(contextEntry.lineage, "Frontier should seed ContextMemory HEAD at ring 1");
  const routedRing1 = Buffer.from(contextEntry.bytes).toString("utf8");
  assert.match(routedRing1, /def scan_broken_agents/);
  assert.match(routedRing1, /def _self_status_block/);
  assert.match(routedRing1, /def _operating_context_block/);
  assert.match(routedRing1, /class _ContextMemoryRing1\(BasicAgent\):/);
  assert.match(
    routedRing1,
    /class RoutedContextMemoryAgent\(_ContextMemoryRing1\):/,
  );
  assert.doesNotMatch(
    routedRing1,
    /from agents\.context_memory_agent import ContextMemoryAgent/,
  );
  const materializedRing = manager.materializeComposition(ringDescriptor);
  assert.equal(
    readFileSync(
      path.join(materializedRing.agentDirectory, "context_memory_agent.py"),
      "utf8",
    ),
    routedRing1,
  );
  const scan = scanBrokenAgents(
    manager.brainstemConfig.python,
    materializedRing.agentDirectory,
  );
  assert.equal(
    scan.status,
    0,
    scan.stderr || scan.stdout || "ring-1 self-state scan reported a healthy routed agent as broken",
  );

  const memoryMarker = "    def perform(self, **kwargs):";
  assert.equal(
    ring1.slice(ring1.indexOf(memoryMarker)),
    pristineBefore.slice(pristineBefore.indexOf(memoryMarker)),
    "ring 1 must preserve perform/recall memory behavior byte-for-byte",
  );
  assert.equal(readFileSync(grailContextPath, "utf8"), pristineBefore);

  manager.rollbackLineage();
  const baselineDescriptor = manager.compositionDescriptor();
  const baselineContext = baselineDescriptor.entries.find(
    (entry) => entry.filename === "context_memory_agent.py",
  );
  assert.equal(baselineContext.lineage, undefined);
  assert.match(
    readFileSync(baselineContext.objectPath, "utf8"),
    /from agents\.context_memory_agent import ContextMemoryAgent/,
  );
  assert.doesNotMatch(readFileSync(baselineContext.objectPath, "utf8"), /scan_broken_agents/);
  manager.materializeComposition(baselineDescriptor);

  manager.restoreLineage();
  assert.ok(
    manager.compositionDescriptor().entries.find(
      (entry) => entry.filename === "context_memory_agent.py",
    ).lineage,
  );
  assert.equal(readFileSync(grailContextPath, "utf8"), pristineBefore);
});

test("HARD 4 — invalid live composition falls back to loadable baseline", (t) => {
  const validationSources = [];
  const fixture = minimalFixture(t, {
    validator: (agentDirectory) => {
      const source = readFileSync(
        path.join(agentDirectory, "global_agent.py"),
        "utf8",
      );
      validationSources.push(source);
      return source.includes("BROKEN")
        ? { ok: false, error: "synthetic integration failure" }
        : { ok: true };
    },
  });
  const global = fixture.store.baselineAncestors().find(
    (item) => item.filename === "global_agent.py",
  );
  const unverified = fixture.store.appendRing(global.ancestorRappid, {
    source: "GLOBAL = 'unverified'\n",
    parentRappid: global.ancestorRappid,
    verified: false,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, unverified);
  const manager = new BetaRouteManager(fixture.managerOptions);
  assert.deepEqual(manager.compositionDescriptor().lineageOverlays, []);

  const broken = fixture.store.appendRing(global.ancestorRappid, {
    source: "BROKEN = True\n",
    parentRappid: global.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, broken);
  const brokenDescriptor = manager.compositionDescriptor();
  assert.equal(brokenDescriptor.lineageOverlays.length, 1);
  const materialized = manager.materializeComposition(brokenDescriptor);
  assert.equal(materialized.fallbackFrom, brokenDescriptor.compositionHash);
  assert.equal(materialized.fallbackStrategy, "baseline");
  assert.equal(
    fixture.store.getHead(global.ancestorRappid),
    global.ancestorRappid,
  );
  assert.equal(
    readFileSync(
      path.join(materialized.agentDirectory, "global_agent.py"),
      "utf8",
    ),
    fixture.sources["global_agent.py"],
  );
  assert.ok(validationSources.some((source) => source.includes("BROKEN")));
  assert.equal(validationSources.at(-1), fixture.sources["global_agent.py"]);
});

test("fail-safe prefers the last-good parent ring before pristine baseline", (t) => {
  const fixture = minimalFixture(t, {
    validator: (agentDirectory) => {
      const source = readFileSync(
        path.join(agentDirectory, "global_agent.py"),
        "utf8",
      );
      return source.includes("ring two")
        ? { ok: false, error: "ring two conflicts with the composed set" }
        : { ok: true };
    },
  });
  const global = fixture.store.baselineAncestors().find(
    (item) => item.filename === "global_agent.py",
  );
  const ring1Source = "GLOBAL = 'ring one'\n";
  const ring1 = fixture.store.appendRing(global.ancestorRappid, {
    source: ring1Source,
    parentRappid: global.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, ring1);
  const manager = new BetaRouteManager(fixture.managerOptions);
  manager.materializeComposition(manager.compositionDescriptor());

  const ring2 = fixture.store.appendRing(global.ancestorRappid, {
    source: "GLOBAL = 'ring two'\n",
    parentRappid: ring1,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, ring2);
  const failed = manager.compositionDescriptor();
  const materialized = manager.materializeComposition(failed);
  assert.equal(materialized.fallbackStrategy, "last-good");
  assert.equal(fixture.store.getHead(global.ancestorRappid), ring1);
  assert.equal(
    readFileSync(
      path.join(materialized.agentDirectory, "global_agent.py"),
      "utf8",
    ),
    ring1Source,
  );
});

test("an unrelated invalid scoped agent does not reset healthy lineage HEADs", async (t) => {
  const fixture = minimalFixture(t, {
    validator: (agentDirectory) => {
      const broken = readdirSync(agentDirectory)
        .filter((filename) => filename.endsWith(".py"))
        .some((filename) => (
          readFileSync(path.join(agentDirectory, filename), "utf8")
            .includes("BROKEN_SCOPED")
        ));
      return broken
        ? { ok: false, error: "unrelated scoped agent failed" }
        : { ok: true };
    },
  });
  const global = fixture.store.baselineAncestors().find(
    (item) => item.filename === "global_agent.py",
  );
  const ring = fixture.store.appendRing(global.ancestorRappid, {
    source: "GLOBAL = 'healthy molt'\n",
    parentRappid: global.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, ring);
  const manager = new BetaRouteManager(fixture.managerOptions);
  manager.materializeComposition(manager.compositionDescriptor());
  await manager.installScopedAgent({
    filename: "broken_scoped_agent.py",
    source: "BROKEN_SCOPED = True\n",
  });

  const fallback = manager.materializeComposition(manager.compositionDescriptor());
  assert.equal(fallback.fallbackStrategy, "last-good");
  assert.equal(fixture.store.getHead(global.ancestorRappid), ring);
});

test("HARD 5 — RAPP_MOLT_LINEAGE=0 forces pure baseline composition", (t) => {
  const fixture = minimalFixture(t);
  const global = fixture.store.baselineAncestors().find(
    (item) => item.filename === "global_agent.py",
  );
  const ring = fixture.store.appendRing(global.ancestorRappid, {
    source: "GLOBAL = 'molted'\n",
    parentRappid: global.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, ring);
  const previous = process.env.RAPP_MOLT_LINEAGE;
  process.env.RAPP_MOLT_LINEAGE = "0";
  try {
    const manager = new BetaRouteManager(fixture.managerOptions);
    const descriptor = manager.compositionDescriptor();
    assert.deepEqual(descriptor.lineageOverlays, []);
    const entry = descriptor.entries.find(
      (candidate) => candidate.filename === "global_agent.py",
    );
    assert.equal(
      readFileSync(entry.objectPath, "utf8"),
      fixture.sources["global_agent.py"],
    );
  } finally {
    if (previous === undefined) delete process.env.RAPP_MOLT_LINEAGE;
    else process.env.RAPP_MOLT_LINEAGE = previous;
  }
});

test("HARD 6 — composition validates in staging before one atomic publication", (t) => {
  let targetDirectory = null;
  let validations = 0;
  const fixture = minimalFixture(t, {
    validator: (agentDirectory) => {
      validations += 1;
      assert.match(agentDirectory, /\.stage\/agents$/);
      assert.equal(existsSync(targetDirectory), false);
      return { ok: true };
    },
  });
  const manager = new BetaRouteManager(fixture.managerOptions);
  const descriptor = manager.compositionDescriptor();
  targetDirectory = path.join(
    manager.compositionRoot,
    descriptor.compositionHash,
  );
  const materialized = manager.materializeComposition(descriptor);
  assert.equal(validations, 1);
  assert.equal(materialized.compositionDirectory, targetDirectory);
  assert.equal(existsSync(path.join(targetDirectory, "complete.json")), true);
  assert.equal(
    readdirSync(manager.compositionRoot).some((name) => name.endsWith(".stage")),
    false,
  );
  assert.equal(
    existsSync(path.join(materialized.agentDirectory, "__pycache__")),
    false,
  );
});

test("independent twin AGENTS_PATH composition receives the same verified overlay", (t) => {
  const fixture = minimalFixture(t);
  const global = fixture.store.baselineAncestors().find(
    (item) => item.filename === "global_agent.py",
  );
  const source = "GLOBAL = 'twin molt'\n";
  const ring = fixture.store.appendRing(global.ancestorRappid, {
    source,
    parentRappid: global.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, ring);
  const manager = new BetaRouteManager(fixture.managerOptions);
  const agentDirectory = path.join(fixture.root, "twin", "agents");
  mkdirSync(path.dirname(agentDirectory), { recursive: true });
  const materialized = manager.materializeExternalAgentSet([
    {
      filename: "global_agent.py",
      source: fixture.sources["global_agent.py"],
    },
  ], agentDirectory);
  assert.equal(materialized[0].source, source);
  assert.equal(
    readFileSync(path.join(agentDirectory, "global_agent.py"), "utf8"),
    source,
  );
});

test("a twin-specific overlay failure falls back locally without moving shared HEAD", (t) => {
  const fixture = minimalFixture(t, {
    validator: (agentDirectory) => {
      const source = readFileSync(
        path.join(agentDirectory, "global_agent.py"),
        "utf8",
      );
      return source.includes("twin-only conflict")
        ? { ok: false, error: "twin-only conflict" }
        : { ok: true };
    },
  });
  const global = fixture.store.baselineAncestors().find(
    (item) => item.filename === "global_agent.py",
  );
  const ring = fixture.store.appendRing(global.ancestorRappid, {
    source: "GLOBAL = 'twin-only conflict'\n",
    parentRappid: global.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, ring);
  const manager = new BetaRouteManager(fixture.managerOptions);
  const agentDirectory = path.join(fixture.root, "twin-fallback", "agents");
  mkdirSync(path.dirname(agentDirectory), { recursive: true });
  manager.materializeExternalAgentSet([
    {
      filename: "global_agent.py",
      source: fixture.sources["global_agent.py"],
    },
  ], agentDirectory);
  assert.equal(
    readFileSync(path.join(agentDirectory, "global_agent.py"), "utf8"),
    fixture.sources["global_agent.py"],
  );
  assert.equal(fixture.store.getHead(global.ancestorRappid), ring);
});

test("packaged Frontier exposes the Molter gate outside app.asar", () => {
  const packageJson = JSON.parse(readFileSync(
    path.join(betaRoot, "package.json"),
    "utf8",
  ));
  assert.ok(
    packageJson.build.asarUnpack.includes(
      "frontier/rapplications/molter/agents/molter_agent.py",
    ),
  );
  assert.equal(
    routeManagerInternals.unpackedAsarPath(
      path.join("/Applications", "Frontier", "app.asar", "frontier", "molter.py"),
    ),
    path.join(
      "/Applications",
      "Frontier",
      "app.asar.unpacked",
      "frontier",
      "molter.py",
    ),
  );
});
