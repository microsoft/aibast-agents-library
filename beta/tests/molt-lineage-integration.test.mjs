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
// Installed launcher checkouts are sparse (beta + tools/rapp1 only); the Grail
// lives in the shared Brainstem checkout the installer points at.
const grailDirectory = process.env.BRAINSTEM_BETA_RUNTIME_DIR
  || path.join(repositoryRoot, "rapp_brainstem");
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
    path.join(homedir(), ".brainstem", "venv", "Scripts", "python.exe"),
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
    "other_agent.py": "OTHER = 'baseline'\n",
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

test("a named environment pinned to baseline composes byte-for-byte identically", (t) => {
  const fixture = minimalFixture(t);
  for (const baseline of fixture.store.baselineAncestors()) {
    assert.equal(
      fixture.store.setHead(
        baseline.ancestorRappid,
        baseline.ancestorRappid,
        { env: "prod" },
      ),
      true,
    );
  }
  const defaultManager = new BetaRouteManager({
    ...fixture.managerOptions,
    lineageEnv: "default",
  });
  const prodManager = new BetaRouteManager({
    ...fixture.managerOptions,
    lineageEnv: "prod",
  });
  const defaultDescriptor = defaultManager.compositionDescriptor();
  const prodDescriptor = prodManager.compositionDescriptor();
  assert.equal(prodDescriptor.compositionHash, defaultDescriptor.compositionHash);
  assert.deepEqual(entryShape(prodDescriptor), entryShape(defaultDescriptor));
  assert.deepEqual(prodDescriptor.lineageOverlays, []);
});

test("lineage telemetry names the active environment and default seeding precisely", (t) => {
  const fixture = minimalFixture(t);
  const manager = new BetaRouteManager({
    ...fixture.managerOptions,
    lineageEnv: "prod",
    seedLineageDefaults: true,
  });
  manager.lineageEnvironments();
  manager.rollbackLineage();
  const lineageEvents = manager.telemetry.filter(
    (event) => event.type.startsWith("lineage-"),
  );
  assert.ok(lineageEvents.length >= 3);
  assert.ok(
    lineageEvents.every((event) => typeof event.env === "string"),
    "every lineage telemetry event must carry an environment",
  );
  const seed = lineageEvents.find(
    (event) => event.type === "lineage-default-skipped",
  );
  assert.equal(seed.env, "default", "ring-1 seeding always targets default");
  assert.equal(
    lineageEvents.find((event) => event.type === "lineage-environments").env,
    "prod",
  );
  assert.equal(
    lineageEvents.find((event) => event.type === "lineage-rollback").env,
    "prod",
  );
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
  assert.ok(
    contextEntry.lineage,
    "Frontier should seed ContextMemory HEAD at ring 1; lineage telemetry: "
      + JSON.stringify(
        manager.telemetry.filter((event) => String(event.type).startsWith("lineage-")),
      ),
  );
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

  // Compare in canonical LF: the Grail checkout may be CRLF on Windows while
  // the ring is pinned -text. The marker must exist exactly once on each side
  // or the comparison would pass vacuously on two tails that start at -1.
  const memoryMarker = "    def perform(self, **kwargs):";
  const canonical = (text) => text.replaceAll("\r\n", "\n");
  const ring1Lf = canonical(ring1);
  const pristineLf = canonical(pristineBefore);
  for (const [label, text] of [["ring 1", ring1Lf], ["the Grail", pristineLf]]) {
    const first = text.indexOf(memoryMarker);
    assert.notEqual(first, -1, `${label} must define perform()`);
    assert.equal(text.indexOf(memoryMarker, first + 1), -1, `${label} must define perform() once`);
  }
  assert.equal(
    ring1Lf.slice(ring1Lf.indexOf(memoryMarker)),
    pristineLf.slice(pristineLf.indexOf(memoryMarker)),
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
  assert.throws(
    () => fixture.store.setHead(global.ancestorRappid, unverified),
    /invalid or unverified molt ring/,
  );
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
  assert.ok(validationSources.includes(fixture.sources["global_agent.py"]));
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

test("fail-safe isolates a broken locus without rewinding a healthy sibling", (t) => {
  const fixture = minimalFixture(t, {
    validator: (agentDirectory) => {
      const globalSource = readFileSync(
        path.join(agentDirectory, "global_agent.py"),
        "utf8",
      );
      return globalSource.includes("broken ring two")
        ? { ok: false, error: "global ring two is incompatible" }
        : { ok: true };
    },
  });
  const baselines = new Map(
    fixture.store.baselineAncestors().map(
      (item) => [item.filename, item],
    ),
  );
  const global = baselines.get("global_agent.py");
  const other = baselines.get("other_agent.py");
  const global1 = fixture.store.appendRing(global.ancestorRappid, {
    source: "GLOBAL = 'ring one'\n",
    parentRappid: global.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  const other1 = fixture.store.appendRing(other.ancestorRappid, {
    source: "OTHER = 'ring one'\n",
    parentRappid: other.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, global1);
  fixture.store.setHead(other.ancestorRappid, other1);
  const manager = new BetaRouteManager(fixture.managerOptions);
  manager.materializeComposition(manager.compositionDescriptor());

  const global2 = fixture.store.appendRing(global.ancestorRappid, {
    source: "GLOBAL = 'broken ring two'\n",
    parentRappid: global1,
    verified: true,
    meta: { author: "test" },
  });
  const other2Source = "OTHER = 'healthy ring two'\n";
  const other2 = fixture.store.appendRing(other.ancestorRappid, {
    source: other2Source,
    parentRappid: other1,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, global2);
  fixture.store.setHead(other.ancestorRappid, other2);

  const fallback = manager.materializeComposition(manager.compositionDescriptor());
  assert.equal(fallback.fallbackStrategy, "isolated");
  assert.deepEqual(fallback.lineageAccepted, [other2]);
  assert.deepEqual(fallback.lineageRejected, [global2]);
  assert.equal(fixture.store.getHead(global.ancestorRappid), global1);
  assert.equal(fixture.store.getHead(other.ancestorRappid), other2);
  assert.equal(
    readFileSync(
      path.join(fallback.agentDirectory, "other_agent.py"),
      "utf8",
    ),
    other2Source,
  );
});

test("an unrelated invalid scoped agent does not reset healthy lineage HEADs", (t) => {
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
  // Persisted broken content (written before the install gate existed) —
  // today's installScopedAgent refuses this source outright.
  const stack = manager.loadStack(manager.identity().active_stack_rappid);
  stack.agents = [manager.packageAgent({
    filename: "broken_scoped_agent.py",
    source: "BROKEN_SCOPED = True\n",
  })];
  manager.saveStack(stack);

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
      // Separator-agnostic: Windows materializes backslash paths.
      assert.match(agentDirectory, /\.dry-load-[^/\\]+[/\\]agents$/);
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

test("dry-load executes private copies and cannot rewrite publishable bytes", (t) => {
  const fixture = minimalFixture(t, {
    validator: (agentDirectory) => {
      writeFileSync(
        path.join(agentDirectory, "global_agent.py"),
        "GLOBAL = 'mutated during import'\n",
      );
      writeFileSync(path.join(agentDirectory, "unexpected_agent.py"), "BAD = True\n");
      return { ok: true };
    },
  });
  const manager = new BetaRouteManager(fixture.managerOptions);
  const descriptor = manager.compositionDescriptor();
  const globalEntry = descriptor.entries.find(
    (entry) => entry.filename === "global_agent.py",
  );
  const materialized = manager.materializeComposition(descriptor);
  assert.equal(
    readFileSync(
      path.join(materialized.agentDirectory, "global_agent.py"),
      "utf8",
    ),
    fixture.sources["global_agent.py"],
  );
  assert.equal(
    readFileSync(globalEntry.objectPath, "utf8"),
    fixture.sources["global_agent.py"],
  );
  assert.equal(
    existsSync(path.join(materialized.agentDirectory, "unexpected_agent.py")),
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

function brokenScopedValidator(agentDirectory) {
  // Mirrors the Grail dry-load contract: stderr names each failing file.
  const failures = readdirSync(agentDirectory)
    .filter((filename) => filename.endsWith(".py"))
    .filter((filename) => (
      readFileSync(path.join(agentDirectory, filename), "utf8")
        .includes("BROKEN_SCOPED")
    ))
    .map((filename) => `${filename} loaded no agents`);
  return failures.length
    ? { ok: false, error: failures.join("\n") }
    : { ok: true };
}

function fakeWorkerProcess() {
  return {
    start: async () => ({ health: { status: "ok" } }),
    stop: async () => {},
  };
}

test("the install gate refuses a scoped agent that fails the Grail dry-load", async (t) => {
  const fixture = minimalFixture(t, { validator: brokenScopedValidator });
  const manager = new BetaRouteManager(fixture.managerOptions);
  await assert.rejects(
    () => manager.installScopedAgent({
      filename: "broken_scoped_agent.py",
      source: "BROKEN_SCOPED = True\n",
    }),
    /Refusing to install broken_scoped_agent\.py: .*loaded no agents/,
  );
  assert.equal(
    manager.loadStack(manager.identity().active_stack_rappid).agents.length,
    0,
    "a refused install must persist nothing",
  );
  const refused = manager.telemetrySnapshot().events.find(
    (event) => event.type === "stack-agent-install-refused",
  );
  assert.equal(refused.filename, "broken_scoped_agent.py");
  assert.match(refused.lesson, /loaded no agents/);

  const installed = await manager.installScopedAgent({
    filename: "healthy_scoped_agent.py",
    source: "HEALTHY_SCOPED = True\n",
  });
  assert.equal(installed.agent.filename, "healthy_scoped_agent.py");
  const materialized = manager.materializeComposition(
    manager.compositionDescriptor(),
  );
  assert.equal(materialized.fallbackStrategy, undefined);
  assert.equal(
    existsSync(path.join(materialized.agentDirectory, "healthy_scoped_agent.py")),
    true,
  );
});

test("boot with a persisted broken scoped agent and no last-good quarantines and boots", async (t) => {
  const fixture = minimalFixture(t, { validator: brokenScopedValidator });
  const seeded = new BetaRouteManager(fixture.managerOptions);
  const stack = seeded.loadStack(seeded.identity().active_stack_rappid);
  stack.agents = [seeded.packageAgent({
    filename: "broken_scoped_agent.py",
    source: "BROKEN_SCOPED = True\n",
  })];
  seeded.saveStack(stack);

  // Fresh launch: no last-good descriptor, no lineage overlays, the pristine
  // composition itself refuses to dry-load — the beta must still boot.
  const manager = new BetaRouteManager(fixture.managerOptions);
  manager.createWorkerProcess = fakeWorkerProcess;
  const route = await manager.startDefault();
  assert.ok(route.url);
  assert.equal(manager.lastLineageFallback.strategy, "quarantine");
  const worker = manager.workers.get(route.compositionHash);
  assert.equal(
    existsSync(path.join(worker.agentDirectory, "broken_scoped_agent.py")),
    false,
    "the broken agent must be excluded from the booted composition",
  );
  assert.equal(
    existsSync(path.join(worker.agentDirectory, "global_agent.py")),
    true,
  );
  const event = manager.telemetrySnapshot().events.find(
    (candidate) => candidate.type === "composition-quarantine",
  );
  assert.deepEqual(
    event.excluded_files.map((excluded) => excluded.filename),
    ["broken_scoped_agent.py"],
  );
  assert.match(event.excluded_files[0].reason, /loaded no agents/);
  // The user's persisted source stays untouched on disk for later repair.
  const persisted = manager.loadStack(
    manager.identity().active_stack_rappid,
  ).agents;
  assert.equal(persisted[0].filename, "broken_scoped_agent.py");
  assert.equal(
    readFileSync(persisted[0].object_path, "utf8"),
    "BROKEN_SCOPED = True\n",
  );
  await manager.stop();
});

test("real Grail boot quarantines a persisted broken scoped agent and boots", async (t) => {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-boot-quarantine-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const managerOptions = {
    betaHome: path.join(root, "beta-home"),
    brainstemConfig: {
      brainstemDir: grailDirectory,
      python: integrationPython(),
    },
    lineageRoot: path.join(root, "lineage"),
    seedLineageDefaults: false,
  };
  const seeded = new BetaRouteManager(managerOptions);
  const stack = seeded.loadStack(seeded.identity().active_stack_rappid);
  stack.agents = [seeded.packageAgent({
    filename: "broken_scoped_agent.py",
    source: "raise RuntimeError('broken scoped agent import')\n",
  })];
  seeded.saveStack(stack);

  const manager = new BetaRouteManager(managerOptions);
  manager.createWorkerProcess = fakeWorkerProcess;
  const route = await manager.startDefault();
  assert.equal(manager.lastLineageFallback.strategy, "quarantine");
  const worker = manager.workers.get(route.compositionHash);
  assert.equal(
    existsSync(path.join(worker.agentDirectory, "broken_scoped_agent.py")),
    false,
  );
  const event = manager.telemetrySnapshot().events.find(
    (candidate) => candidate.type === "composition-quarantine",
  );
  assert.deepEqual(
    event.excluded_files.map((excluded) => excluded.filename),
    ["broken_scoped_agent.py"],
  );
  await manager.stop();
});

test("ephemeral + lineage fallback teardown retires the effective worker and its composition", async (t) => {
  const fixture = minimalFixture(t, {
    validator: (agentDirectory) => {
      const source = readFileSync(
        path.join(agentDirectory, "global_agent.py"),
        "utf8",
      );
      return source.includes("broken ring")
        ? { ok: false, error: "broken ring conflicts with the composed set" }
        : { ok: true };
    },
  });
  const global = fixture.store.baselineAncestors().find(
    (item) => item.filename === "global_agent.py",
  );
  const ring = fixture.store.appendRing(global.ancestorRappid, {
    source: "GLOBAL = 'broken ring'\n",
    parentRappid: global.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, ring);
  const manager = new BetaRouteManager(fixture.managerOptions);
  manager.createWorkerProcess = fakeWorkerProcess;

  let fallbackWorker = null;
  let fallbackDirectory = null;
  await manager.withRoute({
    ephemeralAgent: {
      filename: "oneshot_agent.py",
      source: "ONESHOT = True\n",
    },
  }, async (route) => {
    fallbackWorker = manager.workers.get(route.compositionHash);
    assert.ok(fallbackWorker, "the callback route must key the live worker");
    fallbackDirectory = fallbackWorker.compositionDirectory;
    assert.equal(
      existsSync(path.join(fallbackWorker.agentDirectory, "oneshot_agent.py")),
      true,
      "the pristine ephemeral fallback must still carry the one-shot tool",
    );
  });

  assert.equal(manager.lastLineageFallback.strategy, "baseline");
  assert.notEqual(
    manager.lastLineageFallback.effectiveCompositionHash,
    manager.lastLineageFallback.requestedCompositionHash,
  );
  assert.equal(
    existsSync(path.join(fallbackWorker.agentDirectory, "oneshot_agent.py")),
    false,
    "teardown must scrub the ephemeral tool from the effective worker",
  );
  assert.equal(fallbackWorker.retiredCompositionDirectory, fallbackDirectory);
  const retiredManifest = JSON.parse(readFileSync(
    path.join(fallbackDirectory, "complete.json"),
    "utf8",
  ));
  assert.equal(retiredManifest.retired_ephemeral, true);
  assert.ok(
    retiredManifest.agents.every((agent) => agent.scope !== "ephemeral"),
  );
  assert.equal(
    manager.activeRoute.compositionHash,
    manager.compositionDescriptor().compositionHash,
  );
  await manager.stop();
  assert.equal(
    existsSync(fallbackDirectory),
    false,
    "the fallback ephemeral composition directory must not persist",
  );
});

test("an explicit stack switch never resurrects the previous stack's last-good composition", async (t) => {
  const fixture = minimalFixture(t, {
    validator: (agentDirectory) => {
      const source = readFileSync(
        path.join(agentDirectory, "global_agent.py"),
        "utf8",
      );
      return source.includes("broken ring")
        ? { ok: false, error: "broken ring conflicts with the composed set" }
        : { ok: true };
    },
  });
  const manager = new BetaRouteManager(fixture.managerOptions);
  const identity = manager.identity();
  const stackA = await manager.createStack({
    name: "previous",
    parentRappid: identity.default_stack_rappid,
  });
  await manager.installScopedAgent({
    filename: "stack_a_marker_agent.py",
    source: "STACK_A_MARKER = True\n",
    stackRappid: stackA.rappid,
  });
  await manager.selectStack({ stackRappid: stackA.rappid, overlayRappids: [] });
  manager.materializeComposition(manager.compositionDescriptor());

  const stackB = await manager.createStack({
    name: "switched",
    parentRappid: identity.default_stack_rappid,
  });
  await manager.installScopedAgent({
    filename: "stack_b_marker_agent.py",
    source: "STACK_B_MARKER = True\n",
    stackRappid: stackB.rappid,
  });
  await manager.selectStack({ stackRappid: stackB.rappid, overlayRappids: [] });

  const global = fixture.store.baselineAncestors().find(
    (item) => item.filename === "global_agent.py",
  );
  const ring = fixture.store.appendRing(global.ancestorRappid, {
    source: "GLOBAL = 'broken ring'\n",
    parentRappid: global.ancestorRappid,
    verified: true,
    meta: { author: "test" },
  });
  fixture.store.setHead(global.ancestorRappid, ring);

  const fallback = manager.materializeComposition(
    manager.compositionDescriptor(),
  );
  assert.equal(fallback.fallbackStrategy, "baseline");
  assert.equal(fallback.descriptor.stack.rappid, stackB.rappid);
  assert.equal(
    existsSync(path.join(fallback.agentDirectory, "stack_a_marker_agent.py")),
    false,
    "the previous stack's last-good composition must not be resurrected",
  );
  assert.equal(
    existsSync(path.join(fallback.agentDirectory, "stack_b_marker_agent.py")),
    true,
    "the requested route's pristine baseline must be served",
  );
  assert.equal(
    readFileSync(path.join(fallback.agentDirectory, "global_agent.py"), "utf8"),
    fixture.sources["global_agent.py"],
  );
  assert.equal(
    fixture.store.getHead(global.ancestorRappid),
    global.ancestorRappid,
  );
});

function duplicateToolNameValidator(agentDirectory) {
  // Mirrors Grail's duplicate-tool-name failure, which names BOTH colliding
  // files on one line — the pristine baseline agent and the newcomer.
  const files = readdirSync(agentDirectory);
  const collider = files.find((filename) => (
    filename.endsWith(".py")
    && readFileSync(path.join(agentDirectory, filename), "utf8")
      .includes("COLLIDES_WITH_MEMORY")
  ));
  if (!collider) return { ok: true };
  return {
    ok: false,
    error: `duplicate agent name 'ManageMemory': ${collider} conflicts with `
      + "manage_memory_agent.py already registered",
  };
}

test("a colliding user agent never evicts the pristine baseline agent", async (t) => {
  const fixture = minimalFixture(t, { validator: duplicateToolNameValidator });
  const seeded = new BetaRouteManager(fixture.managerOptions);
  const stack = seeded.loadStack(seeded.identity().active_stack_rappid);
  stack.agents = [seeded.packageAgent({
    filename: "rogue_memory_agent.py",
    source: "COLLIDES_WITH_MEMORY = True\n",
  })];
  seeded.saveStack(stack);

  const manager = new BetaRouteManager(fixture.managerOptions);
  manager.createWorkerProcess = fakeWorkerProcess;
  const route = await manager.startDefault();
  assert.ok(route.url, "the beta still boots");
  const worker = manager.workers.get(route.compositionHash);

  // The survival floor is inviolable: quarantining the baseline here would
  // silently disable the user's memory — strictly worse than bare Grail.
  assert.equal(
    existsSync(path.join(worker.agentDirectory, "manage_memory_agent.py")),
    true,
    "the pristine baseline memory agent must survive the collision",
  );
  assert.equal(
    existsSync(path.join(worker.agentDirectory, "context_memory_agent.py")),
    true,
    "the other sacred memory agent is untouched",
  );
  assert.equal(
    existsSync(path.join(worker.agentDirectory, "rogue_memory_agent.py")),
    false,
    "the colliding newcomer is the one that goes",
  );
  const event = manager.telemetrySnapshot().events.find(
    (candidate) => candidate.type === "composition-quarantine",
  );
  assert.deepEqual(
    event.excluded_files.map((excluded) => excluded.filename),
    ["rogue_memory_agent.py"],
    "only the newcomer is recorded as quarantined",
  );
  await manager.stop();
});

test("a known-bad composition is not re-validated on every request", async (t) => {
  let validations = 0;
  const countingValidator = (agentDirectory) => {
    validations += 1;
    return brokenScopedValidator(agentDirectory);
  };
  const fixture = minimalFixture(t, { validator: countingValidator });
  const seeded = new BetaRouteManager(fixture.managerOptions);
  const stack = seeded.loadStack(seeded.identity().active_stack_rappid);
  stack.agents = [seeded.packageAgent({
    filename: "broken_scoped_agent.py",
    source: "BROKEN_SCOPED = True\n",
  })];
  seeded.saveStack(stack);

  const manager = new BetaRouteManager(fixture.managerOptions);
  manager.createWorkerProcess = fakeWorkerProcess;
  await manager.startDefault();
  const afterFirst = validations;
  assert.ok(afterFirst > 0, "the first boot validates");

  // Re-composing the same broken content must not spawn the dry-load again:
  // compositionHash is content-addressed, so the verdict cannot have changed.
  const descriptor = manager.compositionDescriptor({});
  for (let i = 0; i < 5; i += 1) {
    try {
      manager.materializeCompositionOnce(descriptor);
    } catch {}
  }
  assert.equal(
    validations,
    afterFirst,
    "a remembered failure short-circuits the expensive validator",
  );
  await manager.stop();
});

test("a CRLF ring source (Windows autocrlf checkout) still composes ring 1", (t) => {
  // Found on the windows-latest installer job: beta/electron/rings/ was not
  // pinned -text, the checkout handed the Frontier a CRLF ring-1, the LF-written
  // scanner match in routedContextMemoryMoltSource silently failed, and the
  // overlay was skipped — the user ran baseline while the seed said ring 1.
  const { managerOptions, store } = minimalFixture(t);
  const lf = readFileSync(ring1Path, "utf8");
  assert.doesNotMatch(lf, /\r/, "the repository ring-1 must be LF");
  const crlf = lf.replaceAll("\n", "\r\n");
  const { routedContextMemoryMoltSource } = routeManagerInternals;
  assert.equal(
    routedContextMemoryMoltSource(crlf, "guid-1"),
    routedContextMemoryMoltSource(lf, "guid-1"),
    "CRLF and LF ring sources must produce the same routed molt",
  );

  const manager = new BetaRouteManager({
    ...managerOptions,
    moltVerifier: () => true,
  });
  const baseline = manager.baselineAncestor("context_memory_agent.py");
  const ring = store.appendRing(baseline.ancestorRappid, {
    source: crlf,
    parentRappid: baseline.ancestorRappid,
    verified: true,
    meta: { author: "test", kind: "ambient-context/1.0", policy: "mutable", ring: 1 },
  });
  store.setHead(baseline.ancestorRappid, ring);

  const descriptor = manager.compositionDescriptor();
  const entry = descriptor.entries.find(
    (candidate) => candidate.filename === "context_memory_agent.py",
  );
  assert.ok(
    entry.lineage,
    "a CRLF ring must still overlay; telemetry: " + JSON.stringify(manager.telemetry),
  );
  const routed = Buffer.from(entry.bytes).toString("utf8");
  assert.match(routed, /class RoutedContextMemoryAgent\(_ContextMemoryRing1\):/);
  assert.doesNotMatch(routed, /\r/, "the composed molt is canonical LF");
  assert.deepEqual(
    manager.telemetry.filter((event) => event.type === "lineage-overlay-skipped"),
    [],
  );
});
