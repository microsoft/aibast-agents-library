import { spawn } from "node:child_process";
import { createReadStream, existsSync, mkdirSync, mkdtempSync, rmSync, statSync } from "node:fs";
import { createServer } from "node:http";
import path from "node:path";

const COMMAND_TIMEOUT_MS = 5000;
const EXIT_TIMEOUT_MS = 2000;
const STDERR_LIMIT = 16 * 1024;
const MESSAGE_LIMIT = 16 * 1024 * 1024;

function operation(label, timeoutMs, onSettled) {
  let resolvePromise;
  let rejectPromise;
  let settled = false;
  const promise = new Promise((resolve, reject) => {
    resolvePromise = resolve;
    rejectPromise = reject;
  });
  const settle = (callback, value) => {
    if (settled) return;
    settled = true;
    clearTimeout(timer);
    onSettled();
    callback(value);
  };
  const result = {
    promise,
    resolve: (value) => settle(resolvePromise, value),
    reject: (error) => settle(rejectPromise, error),
  };
  const timer = setTimeout(() => {
    result.reject(new Error(`Timed out after ${timeoutMs}ms waiting for ${label}`));
  }, timeoutMs);
  return result;
}

async function settlesWithin(promise, timeoutMs) {
  let timer;
  try {
    return await Promise.race([
      promise.then(() => true),
      new Promise((resolve) => {
        timer = setTimeout(() => resolve(false), timeoutMs);
      }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}

export async function closeResources(resources) {
  const results = await Promise.allSettled(resources.filter(Boolean).map(
    (resource) => Promise.resolve().then(() => resource.close()),
  ));
  const errors = results.filter((result) => result.status === "rejected")
    .map((result) => result.reason);
  if (errors.length) throw new AggregateError(errors, "Browser test cleanup failed");
}

export class CdpConnection {
  constructor(readable, writable, { signal, timeoutMs = COMMAND_TIMEOUT_MS } = {}) {
    this.readable = readable;
    this.writable = writable;
    this.timeoutMs = timeoutMs;
    this.nextId = 1;
    this.pending = new Map();
    this.waiters = new Map();
    this.buffer = "";
    this.closed = false;
    this.signal = signal;
    this.onAbort = () => this.close(signal.reason);
    readable.setEncoding("utf8");
    readable.on("data", (chunk) => this.receive(chunk));
    readable.on("error", (error) => this.close(error));
    readable.on("end", () => this.close(new Error("Chrome DevTools pipe ended")));
    readable.on("close", () => this.close(new Error("Chrome DevTools pipe closed")));
    writable.on("error", (error) => this.close(error));
    signal?.addEventListener("abort", this.onAbort, { once: true });
    if (signal?.aborted) this.onAbort();
  }

  receive(chunk) {
    if (this.closed) return;
    this.buffer += chunk;
    if (Buffer.byteLength(this.buffer) > MESSAGE_LIMIT) {
      this.close(new Error("Chrome DevTools message exceeded the size limit"));
      return;
    }
    let boundary;
    while ((boundary = this.buffer.indexOf("\0")) !== -1) {
      const source = this.buffer.slice(0, boundary);
      this.buffer = this.buffer.slice(boundary + 1);
      let message;
      try {
        message = JSON.parse(source);
        if (!message || typeof message !== "object" || Array.isArray(message)) {
          throw new Error("Expected a DevTools message object");
        }
      } catch (cause) {
        this.close(new Error("Chrome returned invalid DevTools JSON", { cause }));
        return;
      }
      if (message.id !== undefined) {
        const pending = this.pending.get(message.id);
        if (message.error) {
          pending?.reject(new Error(message.error.message || "Chrome DevTools command failed"));
        } else {
          pending?.resolve(message.result);
        }
      } else {
        const key = `${message.sessionId || ""}:${message.method}`;
        for (const waiter of this.waiters.get(key) || []) waiter.resolve(message.params);
      }
    }
  }

  send(method, params = {}, sessionId) {
    if (this.closed) return Promise.reject(this.closeReason);
    const id = this.nextId++;
    const request = operation(method, this.timeoutMs, () => this.pending.delete(id));
    this.pending.set(id, request);
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    try {
      this.writable.write(`${JSON.stringify(payload)}\0`, (error) => {
        if (error) this.close(error);
      });
    } catch (error) {
      this.close(error);
    }
    return request.promise;
  }

  waitFor(method, sessionId, timeoutMs = 10000) {
    if (this.closed) return Promise.reject(this.closeReason);
    const key = `${sessionId || ""}:${method}`;
    const waiters = this.waiters.get(key) || new Set();
    const waiter = operation(method, timeoutMs, () => {
      waiters.delete(waiter);
      if (!waiters.size) this.waiters.delete(key);
    });
    waiters.add(waiter);
    this.waiters.set(key, waiters);
    return waiter.promise;
  }

  close(reason = new Error("Chrome DevTools connection closed")) {
    if (this.closed) return;
    this.closed = true;
    this.closeReason = reason;
    this.signal?.removeEventListener("abort", this.onAbort);
    for (const request of this.pending.values()) request.reject(reason);
    for (const waiters of this.waiters.values()) {
      for (const waiter of waiters) waiter.reject(reason);
    }
    this.buffer = "";
    this.readable.destroy();
    this.writable.destroy();
  }
}

export async function startStaticServer(betaRoot) {
  const sockets = new Set();
  const server = createServer((request, response) => {
    let relative;
    try {
      const url = new URL(request.url || "/", "http://127.0.0.1");
      relative = decodeURIComponent(url.pathname).replace(/^\/+/, "") || "index.html";
    } catch {
      response.writeHead(400).end("Invalid request path");
      return;
    }
    const filePath = path.resolve(betaRoot, relative);
    if (
      !filePath.startsWith(`${betaRoot}${path.sep}`)
      || !existsSync(filePath)
      || !statSync(filePath).isFile()
    ) {
      response.writeHead(404).end("Not found");
      return;
    }
    const contentTypes = {
      ".html": "text/html; charset=utf-8",
      ".js": "text/javascript; charset=utf-8",
      ".svg": "image/svg+xml",
      ".ps1": "text/plain; charset=utf-8",
      ".sh": "text/plain; charset=utf-8",
    };
    response.setHeader("Content-Type", contentTypes[path.extname(filePath)] || "application/octet-stream");
    const stream = createReadStream(filePath);
    stream.on("error", () => {
      if (!response.headersSent) response.writeHead(500);
      response.end("Could not read the requested file");
    });
    response.once("close", () => stream.destroy());
    stream.pipe(response);
  });
  server.on("connection", (socket) => {
    sockets.add(socket);
    socket.once("close", () => sockets.delete(socket));
  });
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  let closing;
  return {
    pageUrl: `http://127.0.0.1:${address.port}/index.html`,
    close() {
      closing ||= (async () => {
        const closed = new Promise((resolve, reject) => {
          server.close((error) => error ? reject(error) : resolve());
        });
        server.closeAllConnections();
        for (const socket of sockets) socket.destroy();
        try {
          if (!await settlesWithin(closed, EXIT_TIMEOUT_MS)) {
            throw new Error("Timed out closing the Download Center test server");
          }
        } finally {
          server.unref();
        }
      })();
      return closing;
    },
  };
}

function findChrome() {
  if (process.env.CHROME_PATH) {
    if (!existsSync(process.env.CHROME_PATH)) {
      throw new Error(`Configured Chrome executable does not exist: ${process.env.CHROME_PATH}`);
    }
    return process.env.CHROME_PATH;
  }
  const candidates = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ...["PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"].map((name) =>
      process.env[name] && path.join(
        process.env[name], "Google", "Chrome", "Application", "chrome.exe",
      ),
    ),
  ].filter(Boolean);
  const executable = candidates.find((candidate) => existsSync(candidate));
  if (!executable) {
    throw new Error("Chrome or Chromium is required for Download Center browser tests");
  }
  return executable;
}

function signalBrowser(child, signal) {
  if (!child.pid) return;
  try {
    if (process.platform === "win32") {
      if (child.exitCode === null && child.signalCode === null) child.kill(signal);
    } else {
      process.kill(-child.pid, signal);
    }
  } catch (error) {
    if (error.code !== "ESRCH") throw error;
  }
}

export async function launchBrowser({
  betaRoot,
  signal,
  executable = findChrome(),
  executableArgs = [],
  timeoutMs = COMMAND_TIMEOUT_MS,
  onSpawn = () => {},
} = {}) {
  signal?.throwIfAborted();
  const cache = path.join(betaRoot, "node_modules", ".cache");
  mkdirSync(cache, { recursive: true });
  const profile = mkdtempSync(path.join(cache, "download-center-browser-"));
  let child;
  let cdp;
  let stderr = "";
  let closing;
  let exited;
  const close = () => {
    closing ||= (async () => {
      cdp?.close();
      try {
        if (child) {
          signalBrowser(child, "SIGTERM");
          child.stderr?.destroy();
          if (!await settlesWithin(exited, EXIT_TIMEOUT_MS)) {
            signalBrowser(child, "SIGKILL");
            if (!await settlesWithin(exited, EXIT_TIMEOUT_MS)) {
              throw new Error(`Chrome process ${child.pid} did not exit after SIGKILL`);
            }
          }
          // The Linux Chrome wrapper can leave helpers after its main process exits.
          if (process.platform !== "win32") signalBrowser(child, "SIGKILL");
        }
      } finally {
        for (const stream of child?.stdio || []) stream?.destroy();
        child?.unref();
        rmSync(profile, { recursive: true, force: true, maxRetries: 2, retryDelay: 100 });
      }
    })();
    return closing;
  };
  try {
    child = spawn(executable, [
      ...executableArgs,
      "--headless=new",
      "--disable-gpu",
      "--disable-background-networking",
      "--no-default-browser-check",
      "--no-first-run",
      "--no-sandbox",
      "--remote-debugging-pipe",
      `--user-data-dir=${profile}`,
      "about:blank",
    ], {
      // Keep the child referenced; the new process group is only for scoped teardown.
      detached: process.platform !== "win32",
      stdio: ["ignore", "ignore", "pipe", "pipe", "pipe"],
    });
    exited = new Promise((resolve) => {
      child.once("exit", resolve);
      child.once("error", resolve);
    });
    child.stderr.setEncoding("utf8");
    child.stderr.on("data", (chunk) => {
      stderr = (stderr + chunk).slice(-STDERR_LIMIT);
    });
    cdp = new CdpConnection(child.stdio[4], child.stdio[3], { signal, timeoutMs });
    child.once("error", (error) => cdp.close(error));
    child.once("exit", (code, exitSignal) => {
      cdp.close(new Error(`Chrome exited (code ${code}, signal ${exitSignal})`));
    });
    onSpawn({ pid: child.pid, profile });
    await cdp.send("Browser.getVersion");
    const { targetId } = await cdp.send("Target.createTarget", { url: "about:blank" });
    const { sessionId } = await cdp.send("Target.attachToTarget", { targetId, flatten: true });
    await cdp.send("Page.enable", {}, sessionId);
    await cdp.send("Runtime.enable", {}, sessionId);
    await cdp.send("Network.enable", {}, sessionId);
    await cdp.send("Network.setBlockedURLs", { urls: ["https://api.github.com/*"] }, sessionId);
    return { cdp, sessionId, pid: child.pid, profile, close };
  } catch (cause) {
    const failure = new Error(
      `Chrome DevTools startup failed (${executable}, pid ${child?.pid ?? "not spawned"}): `
      + `${cause.message}\nChrome stderr (last ${STDERR_LIMIT} characters):\n`
      + (stderr || "(no stderr received)"),
      { cause },
    );
    try {
      await close();
    } catch (cleanupError) {
      throw new AggregateError([failure, cleanupError], "Chrome startup and cleanup failed");
    }
    throw failure;
  }
}
