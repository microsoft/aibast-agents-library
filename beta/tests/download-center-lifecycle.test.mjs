import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import net from "node:net";
import path from "node:path";
import { PassThrough } from "node:stream";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { CdpConnection, closeResources, launchBrowser, startStaticServer } from "./helpers/download-center-browser.mjs";

const betaRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const fixture = path.join(betaRoot, "tests", "fixtures", "download-center-lifecycle.mjs");
const cache = path.join(betaRoot, "node_modules", ".cache");

function connection(t, options) {
  const readable = new PassThrough();
  const writable = new PassThrough();
  const cdp = new CdpConnection(readable, writable, options);
  t.after(() => cdp.close());
  return { readable, writable, cdp };
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

test("CDP pipes handle fragmented UTF-8, multiple frames and immediate replies", async (t) => {
  const { cdp, readable, writable } = connection(t);
  writable.once("data", (chunk) => {
    const request = JSON.parse(chunk.toString().slice(0, -1));
    const bytes = Buffer.from(JSON.stringify({ id: request.id, result: { text: "café" } }) + "\0");
    const split = bytes.indexOf(Buffer.from("é")) + 1;
    readable.write(bytes.subarray(0, split));
    readable.write(bytes.subarray(split));
  });
  assert.deepEqual(await cdp.send("Browser.getVersion"), { text: "café" });
  const events = [
    cdp.waitFor("Page.loadEventFired", "one"),
    cdp.waitFor("Page.loadEventFired", "two"),
  ];
  readable.write(
    '{"method":"Page.loadEventFired","sessionId":"one","params":{"ready":1}}\0'
    + '{"method":"Page.loadEventFired","sessionId":"two","params":{"ready":2}}\0',
  );
  assert.deepEqual(await Promise.all(events), [{ ready: 1 }, { ready: 2 }]);
  assert.equal(cdp.pending.size, 0);
  assert.equal(cdp.waiters.size, 0);
});

test("CDP command and event timeouts remove pending work", async (t) => {
  const { cdp } = connection(t, { timeoutMs: 30 });
  await Promise.all([
    assert.rejects(cdp.send("Runtime.evaluate"), /Timed out.*Runtime.evaluate/),
    assert.rejects(cdp.waitFor("Page.loadEventFired", "session", 30), /Timed out.*Page.loadEventFired/),
  ]);
  assert.equal(cdp.pending.size, 0);
  assert.equal(cdp.waiters.size, 0);
});

test("CDP disconnect, malformed responses and cancellation reject every pending wait", async (t) => {
  for (const failure of ["disconnect", "malformed", "abort"]) {
    const controller = new AbortController();
    const { cdp, readable } = connection(t, { signal: controller.signal });
    const pending = [
      cdp.send("Runtime.evaluate"),
      cdp.waitFor("Page.loadEventFired", "session"),
    ];
    const settled = Promise.allSettled(pending);
    if (failure === "disconnect") readable.end();
    if (failure === "malformed") readable.write("{invalid}\0");
    if (failure === "abort") controller.abort(new Error("Deliberate test cancellation"));
    const results = await settled;
    assert.ok(results.every((result) => result.status === "rejected"));
    const expected = failure === "disconnect" ? /pipe ended/
      : failure === "malformed" ? /invalid DevTools JSON/ : /Deliberate test cancellation/;
    for (const result of results) assert.match(result.reason.message, expected);
    assert.equal(cdp.pending.size, 0);
    assert.equal(cdp.waiters.size, 0);
    assert.equal(cdp.readable.destroyed, true);
    assert.equal(cdp.writable.destroyed, true);
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

test("spawn failures remove the profile and report the executable error", async () => {
  let profile;
  await assert.rejects(launchBrowser({
    betaRoot,
    executable: path.join(betaRoot, "node_modules", ".cache", "missing-chrome"),
    onSpawn: (resource) => { profile = resource.profile; },
  }), /ENOENT/);
  assert.ok(profile);
  assert.equal(existsSync(profile), false);
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
  timeout: 40000,
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
      const env = {
        ...process.env,
        DOWNLOAD_CENTER_FAILURE_CASE: mode,
        DOWNLOAD_CENTER_RESOURCE_FILE: resourceFile,
      };
      // This is an independent test runner, not another worker of the current runner.
      delete env.NODE_TEST_CONTEXT;
      const child = spawn(process.execPath, ["--test", "--test-reporter=tap", fixture], {
        cwd: betaRoot,
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
              reject(new Error(`Failed ${mode} fixture did not exit within 12s:\n${output}`));
            }, 12000);
          }),
        ]);
        assert.equal(result.code, 1, output);
        assert.equal(result.signal, null, output);
        assert.ok(Date.now() - started < 12000, output);
        assert.ok(existsSync(resourceFile), output);
        resource = JSON.parse(readFileSync(resourceFile, "utf8"));
        assertExited(resource.pid);
        assert.equal(existsSync(resource.profile), false, output);
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
          assert.equal(path.dirname(resource.profile), cache);
          assert.ok(path.basename(resource.profile).startsWith("download-center-browser-"));
          rmSync(resource.profile, { recursive: true, force: true, maxRetries: 2 });
        }
        child.stdout.destroy();
        child.stderr.destroy();
        child.unref();
        rmSync(directory, { recursive: true, force: true });
      }
    });
  }
});
