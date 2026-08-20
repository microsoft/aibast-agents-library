// The twins root under the beta home is shared state. A new TwinManager used
// to wipe it wholesale on construction, taking another live launcher's twins
// (and a grown capability the Molter had installed) with it while status still
// said "live". Now only directories whose owner process is gone are reaped.
import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import { TwinManager } from "../electron/twin-manager.mjs";

function twinDir(root, id, owner) {
  const dir = path.join(root, "twins", id);
  mkdirSync(path.join(dir, "agents"), { recursive: true });
  writeFileSync(path.join(dir, "agents", "demo_agent.py"), "# twin\n");
  if (owner !== undefined) {
    writeFileSync(path.join(dir, "owner.json"), JSON.stringify(owner));
  }
  return dir;
}

test("a new TwinManager reaps only twin directories whose owner is gone", (t) => {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-twin-ownership-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const liveOwner = spawn(process.execPath, ["-e", "setTimeout(() => {}, 30000)"], { stdio: "ignore" });
  t.after(() => liveOwner.kill());
  const deadPid = spawnSync("sh", ["-c", "exit 0"]).pid;

  const foreign = twinDir(root, "foreign-1", { pid: liveOwner.pid, startedAt: "2026-08-20T00:00:00Z" });
  const crashed = twinDir(root, "crashed-2", { pid: deadPid, startedAt: "2026-08-20T00:00:00Z" });
  const legacy = twinDir(root, "legacy-3", undefined);
  const corrupt = twinDir(root, "corrupt-4", "not json at all");
  writeFileSync(path.join(root, "twins", "stray-file.txt"), "keep me");

  const events = [];
  const manager = new TwinManager({
    betaHome: root,
    brainstemConfig: { url: "http://127.0.0.1:1" },
    storeClient: {},
    onEvent: (event) => events.push(event),
  });

  assert.ok(existsSync(foreign), "a directory owned by another live process is kept");
  assert.ok(!existsSync(crashed), "a directory whose owner died is reaped");
  assert.ok(!existsSync(legacy), "a directory with no ownership record is reaped (pre-ownership layout)");
  assert.ok(!existsSync(corrupt), "an unreadable ownership record counts as unowned");
  assert.ok(existsSync(path.join(root, "twins", "stray-file.txt")), "only directories are considered");
  assert.deepEqual(
    events.filter((event) => event.type === "twin-dir-kept").map((event) => event.id),
    ["foreign-1"],
  );
  assert.deepEqual(manager.reapStaleTwinDirectories(), { removed: [], kept: [{ id: "foreign-1", pid: liveOwner.pid }] });
});

test("a directory owned by THIS process is treated as stale on construction", (t) => {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-twin-ownership-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const self = twinDir(root, "self-1", { pid: process.pid, startedAt: "2026-08-20T00:00:00Z" });
  new TwinManager({ betaHome: root, brainstemConfig: { url: "http://127.0.0.1:1" }, storeClient: {} });
  assert.ok(!existsSync(self), "a fresh manager in the same process starts its own bookkeeping clean");
});

test("a missing twins root is not an error", () => {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-twin-ownership-"));
  const manager = new TwinManager({ betaHome: root, brainstemConfig: { url: "http://127.0.0.1:1" }, storeClient: {} });
  assert.deepEqual(manager.reapStaleTwinDirectories(), { removed: [], kept: [] });
  rmSync(root, { recursive: true, force: true });
});
