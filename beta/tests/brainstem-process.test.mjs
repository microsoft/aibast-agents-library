import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";

import {
  isBrainstemHealth,
  resolveBrainstemConfig,
  waitForHealth,
} from "../electron/brainstem-process.mjs";

test("beta launcher resolves the shared global Brainstem", () => {
  const config = resolveBrainstemConfig({
    env: {},
    platform: "linux",
    home: "/tmp/example-home",
  });
  assert.equal(config.brainstemHome, "/tmp/example-home/.brainstem");
  assert.equal(
    config.brainstemDir,
    path.posix.join("/tmp/example-home/.brainstem", "src", "rapp_brainstem"),
  );
  assert.equal(
    config.python,
    path.posix.join("/tmp/example-home/.brainstem", "venv", "bin", "python"),
  );
  assert.equal(config.port, 7071);
});

test("beta launcher resolves Windows Brainstem paths", () => {
  const config = resolveBrainstemConfig({
    env: {},
    platform: "win32",
    home: "C:\\Users\\Example",
  });
  assert.equal(config.brainstemHome, "C:\\Users\\Example\\.brainstem");
  assert.equal(
    config.python,
    "C:\\Users\\Example\\.brainstem\\venv\\Scripts\\python.exe",
  );
});

test("beta launcher accepts authenticated and unauthenticated health", () => {
  const base = { version: "0.6.16", agents: [] };
  assert.equal(isBrainstemHealth({ ...base, status: "ok" }), true);
  assert.equal(isBrainstemHealth({ ...base, status: "unauthenticated" }), true);
  assert.equal(isBrainstemHealth({ status: "ok", version: "0.6.16" }), false);
  assert.equal(isBrainstemHealth({ status: "other", ...base }), false);
});

test("health wait stops when the child exits", async () => {
  let calls = 0;
  const result = await waitForHealth("http://127.0.0.1:7071", {
    timeoutMs: 5_000,
    intervalMs: 1,
    probe: async () => {
      calls += 1;
      return null;
    },
    exited: () => calls >= 2,
  });
  assert.equal(result, null);
  assert.equal(calls, 2);
});

test("health wait returns the first valid response", async () => {
  const health = { status: "unauthenticated", version: "0.6.16", agents: [] };
  let calls = 0;
  const result = await waitForHealth("http://127.0.0.1:7071", {
    timeoutMs: 100,
    intervalMs: 1,
    probe: async () => {
      calls += 1;
      return calls === 2 ? health : null;
    },
  });
  assert.deepEqual(result, health);
});
