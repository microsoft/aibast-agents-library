import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { EventEmitter, once } from "node:events";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import net from "node:net";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { BROWSER_STARTUP_TIMEOUT_MS, CDP_COMMAND_TIMEOUT_MS, CdpConnection, closeResources, launchBrowser, startStaticServer } from "./helpers/download-center-browser.mjs";

const testDirectory = path.dirname(fileURLToPath(import.meta.url));
const auditRoot = path.resolve(testDirectory, "../..");
const betaRoot = path.resolve(auditRoot, "../beta");
const fixture = path.join(testDirectory, "fixtures", "download-center-lifecycle.mjs");
const cache = path.join(auditRoot, "node_modules", ".cache");

function connection(t, options) {
  const session = new EventEmitter();
  session.send = () => new Promise(() => {});
  const cdp = new CdpConnection(session, options);
  t.after(() => cdp.close());
  return { session, cdp };
}

function killOwnedProcess(pid, group = false) {
  if (!Number.isInteger(pid) || pid <= 0) return;
  try {
    process.kill(group && process.platform !== "win32" ? -pid : pid, "SIGKILL");
  } catch (error) {
    if (error.code !== "ESRCH") throw error;
  }
}

function assertExited(pid) {
  assert.throws(
    () => process.kill(pid, 0),
    (error) => error.code === "ESRCH",
    `Browser process ${pid} must not survive the failed fixture`,
  );
}

test("cold browser startup has its own budget without relaxing command deadlines", async (t) => {
  assert.equal(BROWSER_STARTUP_TIMEOUT_MS, 30000);
  assert.equal(CDP_COMMAND_TIMEOUT_MS, 5000);
  const { cdp } = connection(t);
  assert.equal(cdp.timeoutMs, CDP_COMMAND_TIMEOUT_MS);
});

test("Playwright CDP results, protocol errors and events are forwarded without a custom wire", async (t) => {
  const { cdp, session } = connection(t);
  session.send = async (method, params) => {
    if (method === "Invalid.command") throw new Error("Unknown protocol command");
    return params;
  };
  assert.deepEqual(await cdp.send("Runtime.evaluate", { expression: "1" }), { expression: "1" });
  await assert.rejects(cdp.send("Invalid.command"), /Unknown protocol command/);
  const events = [
    cdp.waitFor("Page.loadEventFired"),
    cdp.waitFor("Runtime.executionContextCreated"),
  ];
  session.emit("Page.loadEventFired", { ready: 1 });
  session.emit("Runtime.executionContextCreated", { ready: 2 });
  assert.deepEqual(await Promise.all(events), [{ ready: 1 }, { ready: 2 }]);
  assert.equal(cdp.pending.size, 0);
  assert.equal(session.eventNames().length, 0);
});

test("CDP command and event timeouts remove pending work", async (t) => {
  const { cdp, session } = connection(t, { timeoutMs: 30 });
  await Promise.all([
    assert.rejects(cdp.send("Runtime.evaluate"), /Timed out.*Runtime.evaluate/),
    assert.rejects(cdp.waitFor("Page.loadEventFired", "session", 30), /Timed out.*Page.loadEventFired/),
  ]);
  assert.equal(cdp.pending.size, 0);
  assert.equal(session.eventNames().length, 0);
});

test("browser disconnect and cancellation reject every pending CDP wait", async (t) => {
  for (const failure of ["disconnect", "abort"]) {
    const controller = new AbortController();
    const { cdp, session } = connection(t, { signal: controller.signal });
    const pending = [
      cdp.send("Runtime.evaluate"),
      cdp.waitFor("Page.loadEventFired", "session"),
    ];
    const settled = Promise.allSettled(pending);
    if (failure === "disconnect") cdp.close(new Error("Playwright browser disconnected"));
    if (failure === "abort") controller.abort(new Error("Deliberate test cancellation"));
    const results = await settled;
    assert.ok(results.every((result) => result.status === "rejected"));
    const expected = failure === "disconnect" ? /browser disconnected/ : /Deliberate test cancellation/;
    for (const result of results) assert.match(result.reason.message, expected);
    assert.equal(cdp.pending.size, 0);
    assert.equal(session.eventNames().length, 0);
    await assert.rejects(cdp.send("Page.enable"), expected);
  }
});

test("static server shutdown closes unfinished client requests and is idempotent", async (t) => {
  const site = await startStaticServer(betaRoot);
  t.after(() => site.close());
  const { port, hostname } = new URL(site.pageUrl);
  const socket = net.connect(Number(port), hostname);
  t.after(() => socket.destroy());
  await once(socket, "connect");
  socket.on("error", (error) => assert.equal(error.code, "ECONNRESET"));
  socket.write("GET /index.html HTTP/1.1\r\nHost: localhost\r\n");
  const closed = new Promise((resolve) => socket.once("close", resolve));
  await Promise.all([site.close(), site.close(), closed]);
  assert.equal(socket.destroyed, true);
});

test("Playwright reports missing executables without selecting another browser", async () => {
  await assert.rejects(launchBrowser({
    executable: path.join(cache, "missing-chrome"),
  }), /[Ee]xecutable.*(?:exist|missing)|ENOENT/);
});

test("a failing closer cannot prevent another resource from being closed", async () => {
  const calls = [];
  await assert.rejects(closeResources([
    { close() { calls.push("browser"); throw new Error("Deliberate cleanup failure"); } },
    { async close() { calls.push("server"); } },
  ]), (error) => error instanceof AggregateError
    && error.errors[0].message === "Deliberate cleanup failure");
  assert.deepEqual(calls, ["browser", "server"]);
});

test("failed browser startup, assertions and test deadlines exit without leaked resources", {
  timeout: BROWSER_STARTUP_TIMEOUT_MS + 40000,
}, async (t) => {
  for (const mode of ["startup-failure", "ready-assertion", "test-timeout"]) {
    await t.test(mode, async () => {
      mkdirSync(cache, { recursive: true });
      const directory = mkdtempSync(path.join(cache, "download-center-watchdog-"));
      const resourceFile = path.join(directory, "resource.json");
      let resource;
      let output = "";
      let watchdog;
      const started = Date.now();
      const watchdogMs = mode === "ready-assertion" ? BROWSER_STARTUP_TIMEOUT_MS + 10000 : 12000;
      const env = {
        ...process.env,
        DOWNLOAD_CENTER_FAILURE_CASE: mode,
        DOWNLOAD_CENTER_RESOURCE_FILE: resourceFile,
      };
      // This is an independent test runner, not another worker of the current runner.
      delete env.NODE_TEST_CONTEXT;
      const child = spawn(process.execPath, ["--test", "--test-reporter=tap", fixture], {
        cwd: testDirectory,
        detached: process.platform !== "win32",
        stdio: ["ignore", "pipe", "pipe"],
        env,
      });
      child.stdout.setEncoding("utf8").on("data", (chunk) => { output += chunk; });
      child.stderr.setEncoding("utf8").on("data", (chunk) => { output += chunk; });
      try {
        const result = await Promise.race([
          new Promise((resolve, reject) => {
            child.once("error", reject);
            child.once("close", (code, signal) => resolve({ code, signal }));
          }),
          new Promise((_, reject) => {
            watchdog = setTimeout(() => {
              killOwnedProcess(child.pid, true);
              child.stdout.destroy();
              child.stderr.destroy();
              reject(new Error(`Failed ${mode} fixture did not exit within ${watchdogMs}ms:\n${output}`));
            }, watchdogMs);
          }),
        ]);
        assert.equal(result.code, 1, output);
        assert.equal(result.signal, null, output);
        assert.ok(Date.now() - started < watchdogMs, output);
        assert.ok(existsSync(resourceFile), output);
        resource = JSON.parse(readFileSync(resourceFile, "utf8"));
        assertExited(resource.pid);
        assert.match(output, mode === "ready-assertion"
          ? /Deliberate assertion after real Chrome startup/
          : mode === "test-timeout" ? /testTimeoutFailure/
            : /Synthetic Chrome startup failure: no DevTools response/);
        await assert.rejects(fetch(resource.pageUrl, { signal: AbortSignal.timeout(1000) }));
      } finally {
        clearTimeout(watchdog);
        killOwnedProcess(child.pid, true);
        resource ||= existsSync(resourceFile) && JSON.parse(readFileSync(resourceFile, "utf8"));
        if (resource) {
          killOwnedProcess(resource.pid, true);
        }
        child.stdout.destroy();
        child.stderr.destroy();
        child.unref();
        rmSync(directory, { recursive: true, force: true });
      }
    });
  }
});
