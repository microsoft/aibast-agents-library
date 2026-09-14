import { accessSync, constants, createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import path from "node:path";
import { stripVTControlCharacters } from "node:util";
import { chromium } from "playwright";

export const BROWSER_STARTUP_TIMEOUT_MS = 30000;
export const CDP_COMMAND_TIMEOUT_MS = 5000;
const EXIT_TIMEOUT_MS = 2000;

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

function bounded(promise, label, timeoutMs, signal) {
  const onAbort = () => request.reject(signal.reason);
  const request = operation(label, timeoutMs, () => {
    signal?.removeEventListener("abort", onAbort);
  });
  signal?.addEventListener("abort", onAbort, { once: true });
  if (signal?.aborted) onAbort();
  Promise.resolve(promise).then(request.resolve, request.reject);
  return request.promise;
}

async function terminateBrowser(pid) {
  if (!Number.isInteger(pid) || pid <= 0) {
    throw new Error("Playwright did not report an owned browser process to terminate");
  }
  try {
    process.kill(pid, "SIGKILL");
  } catch (error) {
    if (error.code !== "ESRCH") throw error;
    return;
  }
  const deadline = Date.now() + EXIT_TIMEOUT_MS;
  while (Date.now() < deadline) {
    try {
      process.kill(pid, 0);
    } catch (error) {
      if (error.code !== "ESRCH") throw error;
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
  throw new Error(`Playwright browser process ${pid} did not exit after SIGKILL`);
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
  constructor(session, { signal, timeoutMs = CDP_COMMAND_TIMEOUT_MS } = {}) {
    this.session = session;
    this.timeoutMs = timeoutMs;
    this.pending = new Set();
    this.closed = false;
    this.signal = signal;
    this.onAbort = () => this.close(signal.reason);
    signal?.addEventListener("abort", this.onAbort, { once: true });
    if (signal?.aborted) this.onAbort();
  }

  request(label, run, timeoutMs = this.timeoutMs) {
    if (this.closed) return Promise.reject(this.closeReason);
    const request = operation(label, timeoutMs, () => this.pending.delete(request));
    this.pending.add(request);
    try {
      Promise.resolve(run()).then(request.resolve, request.reject);
    } catch (error) {
      request.reject(error);
    }
    return request.promise;
  }

  send(method, params = {}) {
    return this.request(method, () => this.session.send(method, params));
  }

  waitFor(method, _sessionId, timeoutMs = 10000) {
    let receive;
    return this.request(method, () => new Promise((resolve) => {
      receive = resolve;
      this.session.on(method, receive);
    }), timeoutMs).finally(() => {
      if (receive) this.session.off(method, receive);
    });
  }

  close(reason = new Error("Chrome DevTools connection closed")) {
    if (this.closed) return;
    this.closed = true;
    this.closeReason = reason;
    this.signal?.removeEventListener("abort", this.onAbort);
    for (const request of this.pending) request.reject(reason);
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
  const override = process.env.CHROME_PATH || process.env.AIBAST_CHROME_PATH;
  if (override) {
    accessSync(override, constants.X_OK);
    return override;
  }
  // Match the proven academy-course-audit.mjs discovery order and Playwright version.
  const candidates = [
    chromium.executablePath(),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    ...["PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"].map((name) =>
      process.env[name] && path.join(
        process.env[name], "Google", "Chrome", "Application", "chrome.exe",
      ),
    ),
  ].filter(Boolean);
  const executable = candidates.find((candidate) => {
    try {
      accessSync(candidate, constants.X_OK);
      return true;
    } catch (error) {
      if (!["ENOENT", "EACCES"].includes(error.code)) throw error;
      return false;
    }
  });
  if (!executable) {
    throw new Error("Chrome or Chromium is required for Download Center browser tests");
  }
  return executable;
}

export async function launchBrowser({
  signal,
  executable = findChrome(),
  executableArgs = [],
  startupTimeoutMs = BROWSER_STARTUP_TIMEOUT_MS,
  commandTimeoutMs = CDP_COMMAND_TIMEOUT_MS,
  onLaunch = () => {},
} = {}) {
  signal?.throwIfAborted();
  let browser;
  let pid;
  let cdp;
  let closing;
  const close = () => {
    closing ||= (async () => {
      cdp?.close();
      if (browser) {
        let gracefulError;
        try {
          await bounded(browser.close(), "Playwright browser shutdown", EXIT_TIMEOUT_MS);
          return;
        } catch (error) {
          gracefulError = error;
        }
        try {
          await terminateBrowser(pid);
          await bounded(browser.close(), "Playwright browser termination", EXIT_TIMEOUT_MS);
        } catch (error) {
          throw new AggregateError([gracefulError, error], "Playwright browser cleanup failed");
        }
      } else if (pid) {
        await terminateBrowser(pid);
      }
    })();
    return closing;
  };
  try {
    browser = await chromium.launch({
      executablePath: executable,
      headless: true,
      timeout: startupTimeoutMs,
      ...(executableArgs.length ? { args: executableArgs, ignoreDefaultArgs: true } : {}),
    });
    signal?.throwIfAborted();
    const browserSession = await bounded(
      browser.newBrowserCDPSession(), "Playwright browser session", commandTimeoutMs, signal,
    );
    const processes = await bounded(
      browserSession.send("SystemInfo.getProcessInfo"), "Chrome process identity", commandTimeoutMs, signal,
    );
    pid = processes.processInfo.find((entry) => entry.type === "browser")?.id;
    if (!Number.isInteger(pid) || pid <= 0) throw new Error("Chrome did not report its browser process ID");
    onLaunch({ pid });
    await bounded(browserSession.detach(), "Chrome process session detach", commandTimeoutMs, signal);
    const page = await bounded(
      browser.newPage({ viewport: null }), "Playwright test page", commandTimeoutMs, signal,
    );
    const session = await bounded(
      page.context().newCDPSession(page), "Playwright CDP session", commandTimeoutMs, signal,
    );
    cdp = new CdpConnection(session, { signal, timeoutMs: commandTimeoutMs });
    browser.on("disconnected", () => {
      cdp.close(new Error("Playwright browser disconnected"));
    });
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Network.enable");
    await cdp.send("Network.setBlockedURLs", { urls: ["https://api.github.com/*"] });
    return { cdp, pid, executablePath: executable, version: browser.version(), close };
  } catch (cause) {
    // A launch timeout can reject while Playwright is still attempting graceful
    // shutdown. Its pinned-version call log identifies the process it spawned.
    if (!pid) {
      const launched = /^\s*- <launched> pid=(\d+)\s*$/m.exec(
        stripVTControlCharacters(cause.message || ""),
      );
      if (launched) pid = Number(launched[1]);
    }
    const failure = new Error(
      `Playwright Chromium startup failed (${executable}): ${cause.message}`,
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
