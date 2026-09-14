import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createReadStream, existsSync, mkdirSync, rmSync, statSync } from "node:fs";
import { createServer } from "node:http";
import net from "node:net";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const betaRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

async function startStaticServer() {
  const server = createServer((request, response) => {
    const requestUrl = new URL(request.url || "/", "http://127.0.0.1");
    const relative = decodeURIComponent(requestUrl.pathname).replace(/^\/+/, "") || "index.html";
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
    createReadStream(filePath).pipe(response);
  });
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  return {
    pageUrl: `http://127.0.0.1:${address.port}/index.html`,
    close: () => new Promise((resolve) => server.close(resolve)),
  };
}

function findChrome() {
  const candidates = [
    process.env.CHROME_PATH,
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    process.env.PROGRAMFILES &&
      path.join(process.env.PROGRAMFILES, "Google", "Chrome", "Application", "chrome.exe"),
    process.env["PROGRAMFILES(X86)"] &&
      path.join(
        process.env["PROGRAMFILES(X86)"],
        "Google",
        "Chrome",
        "Application",
        "chrome.exe",
      ),
    process.env.LOCALAPPDATA &&
      path.join(
        process.env.LOCALAPPDATA,
        "Google",
        "Chrome",
        "Application",
        "chrome.exe",
      ),
  ].filter(Boolean);
  return candidates.find((candidate) => existsSync(candidate));
}

async function reservePort() {
  const server = net.createServer();
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });
  const address = server.address();
  await new Promise((resolve) => server.close(resolve));
  return address.port;
}

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

class CdpConnection {
  constructor(socket) {
    this.socket = socket;
    this.nextId = 1;
    this.pending = new Map();
    this.waiters = new Map();
    socket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (message.id) {
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        if (message.error) {
          pending.reject(new Error(message.error.message));
        } else {
          pending.resolve(message.result);
        }
        return;
      }

      const key = `${message.sessionId || ""}:${message.method}`;
      const waiters = this.waiters.get(key) || [];
      this.waiters.delete(key);
      for (const waiter of waiters) waiter.resolve(message.params);
    });
  }

  static async connect(url) {
    const socket = new WebSocket(url);
    await new Promise((resolve, reject) => {
      socket.addEventListener("open", resolve, { once: true });
      socket.addEventListener("error", reject, { once: true });
    });
    return new CdpConnection(socket);
  }

  send(method, params = {}, sessionId) {
    const id = this.nextId;
    this.nextId += 1;
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    this.socket.send(JSON.stringify(payload));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
    });
  }

  waitFor(method, sessionId, timeout = 10000) {
    const key = `${sessionId || ""}:${method}`;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Timed out waiting for ${method}`));
      }, timeout);
      const waiters = this.waiters.get(key) || [];
      waiters.push({
        resolve: (value) => {
          clearTimeout(timer);
          resolve(value);
        },
      });
      this.waiters.set(key, waiters);
    });
  }

  close() {
    this.socket.close();
  }
}

async function launchBrowser() {
  const executable = findChrome();
  assert.ok(executable, "Chrome or Chromium is required for Download Center browser tests");
  const port = await reservePort();
  const profile = path.join(
    betaRoot,
    "node_modules",
    ".cache",
    `download-center-browser-${process.pid}-${Date.now()}`,
  );
  mkdirSync(profile, { recursive: true });
  const child = spawn(
    executable,
    [
      "--headless=new",
      "--disable-gpu",
      "--disable-background-networking",
      "--no-default-browser-check",
      "--no-first-run",
      "--no-sandbox",
      `--remote-debugging-port=${port}`,
      `--user-data-dir=${profile}`,
      "about:blank",
    ],
    { stdio: ["ignore", "ignore", "pipe"] },
  );
  child.stderr.resume();

  let browserMetadata;
  for (let attempt = 0; attempt < 100; attempt += 1) {
    if (child.exitCode !== null) break;
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (response.ok) {
        browserMetadata = await response.json();
        break;
      }
    } catch {
      await delay(50);
    }
  }
  assert.ok(browserMetadata?.webSocketDebuggerUrl, "Chrome DevTools endpoint did not start");

  const cdp = await CdpConnection.connect(browserMetadata.webSocketDebuggerUrl);
  const { targetId } = await cdp.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await cdp.send("Target.attachToTarget", {
    targetId,
    flatten: true,
  });
  await cdp.send("Page.enable", {}, sessionId);
  await cdp.send("Runtime.enable", {}, sessionId);
  await cdp.send("Network.enable", {}, sessionId);
  await cdp.send(
    "Network.setBlockedURLs",
    { urls: ["https://api.github.com/*"] },
    sessionId,
  );

  return {
    cdp,
    sessionId,
    async close() {
      cdp.close();
      if (child.exitCode === null) {
        child.kill("SIGTERM");
        await Promise.race([
          new Promise((resolve) => child.once("exit", resolve)),
          delay(2000).then(() => {
            if (child.exitCode === null) child.kill("SIGKILL");
          }),
        ]);
      }
      rmSync(profile, { recursive: true, force: true });
    },
  };
}

async function navigate(cdp, sessionId, url, { width, height, scripts }) {
  await cdp.send(
    "Emulation.setDeviceMetricsOverride",
    { width, height, deviceScaleFactor: 1, mobile: true },
    sessionId,
  );
  await cdp.send(
    "Emulation.setScriptExecutionDisabled",
    { value: !scripts },
    sessionId,
  );
  const loaded = cdp.waitFor("Page.loadEventFired", sessionId);
  await cdp.send("Page.navigate", { url }, sessionId);
  await loaded;
  if (!scripts) {
    await cdp.send(
      "Emulation.setScriptExecutionDisabled",
      { value: false },
      sessionId,
    );
  }
}

async function evaluate(cdp, sessionId, expression) {
  const result = await cdp.send(
    "Runtime.evaluate",
    { expression, awaitPromise: true, returnByValue: true },
    sessionId,
  );
  assert.equal(result.exceptionDetails, undefined, result.exceptionDetails?.text);
  return result.result.value;
}

test("Download Center works without JavaScript and stays narrow under stress", {
  timeout: 30000,
}, async () => {
  const site = await startStaticServer();
  let browser;
  try {
    browser = await launchBrowser();
    for (const width of [320, 640]) {
      await navigate(browser.cdp, browser.sessionId, `${site.pageUrl}?no-js=${width}`, {
        width,
        height: 800,
        scripts: false,
      });
      const noJs = await evaluate(
        browser.cdp,
        browser.sessionId,
        `(() => ({
          viewport: innerWidth,
          overflow: document.documentElement.scrollWidth - innerWidth,
          fallbackVisible: document.querySelector("#no-js-download").getClientRects().length > 0,
          formVisible: document.querySelector("#download-form").getClientRects().length > 0,
          triggerVisible: document.querySelector("#trigger-install").getClientRects().length > 0,
          panelsVisible: [...document.querySelectorAll(".accordion-panel")]
            .every((panel) => panel.getClientRects().length > 0),
          downloads: [...document.querySelectorAll("#no-js-download a[download]")]
            .map((link) => ({ href: link.href, download: link.download })),
          source: document.querySelector("#source-link").href,
          release: document.querySelector("#release-link-top").href,
          goldenPath: document.querySelector("#golden-path-link").href,
        }))()`,
      );
      assert.equal(noJs.viewport, width);
      assert.equal(noJs.overflow, 0);
      assert.equal(noJs.fallbackVisible, true);
      assert.equal(noJs.formVisible, false);
      assert.equal(noJs.triggerVisible, false);
      assert.equal(noJs.panelsVisible, true);
      assert.equal(noJs.downloads.length, 2);
      assert.ok(noJs.downloads.every((download) => download.download));
      assert.match(noJs.downloads[0].href, /frontier\.ps1$/);
      assert.match(noJs.downloads[1].href, /frontier\.sh$/);
      assert.match(noJs.source, /github\.com\/microsoft\/aibast-agents-library\/tree\/main\/beta$/);
      assert.match(noJs.release, /github\.com\/microsoft\/aibast-agents-library\/releases$/);
      assert.match(
        noJs.goldenPath,
        /github\.com\/microsoft\/aibast-agents-library\/blob\/main\/beta\/GOLDEN_PATH\.md$/,
      );
    }

    for (const width of [320, 640]) {
      await navigate(
        browser.cdp,
        browser.sessionId,
        `${site.pageUrl}?scoutTheme=dark&scripts=${width}`,
        { width, height: 800, scripts: true },
      );
      const enhanced = await evaluate(
        browser.cdp,
        browser.sessionId,
        `(async () => {
          await new Promise((resolve) => setTimeout(resolve, 100));
          document.querySelector("#expand-all").click();
          const notice = document.querySelector("#load-error");
          notice.hidden = false;
          notice.textContent =
            "GitHub returned 403 for https://api.github.com/repos/microsoft/aibast-agents-library/releases?per_page=100";
          await new Promise((resolve) => setTimeout(resolve, 50));
          return {
            viewport: innerWidth,
            overflow: document.documentElement.scrollWidth - innerWidth,
            expanded: document.querySelectorAll(
              '.accordion-trigger[aria-expanded="true"]',
            ).length,
            noJsFallbackPresent: Boolean(document.querySelector("#no-js-download")),
            releaseClaim: document.querySelector(".product-mark strong").textContent.trim(),
            requirements: document.querySelector("#panel-requirements").innerText,
            recoveryVisible:
              document.querySelector("#recovery-panel").getClientRects().length > 0,
            recoveryDownloads: [
              ...document.querySelectorAll("#recovery-panel a[download]"),
            ].map((link) => link.getAttribute("href")),
            recoveryCommands: [
              document.querySelector("#recovery-windows-command").textContent.trim(),
              document.querySelector("#recovery-unix-command").textContent.trim(),
            ],
            platformHelp: document.querySelector("#platform-help").textContent.trim(),
          };
        })()`,
      );
      assert.equal(enhanced.viewport, width);
      assert.equal(enhanced.overflow, 0);
      assert.equal(enhanced.expanded, 4);
      assert.equal(enhanced.noJsFallbackPresent, false);
      assert.equal(enhanced.releaseClaim, "Commit-pinned source bootstraps");
      assert.equal(enhanced.recoveryVisible, true);
      assert.equal(enhanced.recoveryDownloads.length, 2);
      assert.match(enhanced.recoveryDownloads[0], /frontier\.ps1$/);
      assert.match(enhanced.recoveryDownloads[1], /frontier\.sh$/);
      assert.match(enhanced.recoveryCommands[0], /powershell/i);
      assert.match(enhanced.recoveryCommands[0], /RAPP_FRONTIER_REPO="microsoft\/aibast-agents-library"/);
      assert.match(enhanced.recoveryCommands[1], /^RAPP_FRONTIER_REPO="microsoft\/aibast-agents-library" bash /);
      assert.match(enhanced.platformHelp, /source recovery options below/);
      assert.match(
        enhanced.requirements,
        /Application signature and native installation verification are not claimed/,
      );
      assert.match(enhanced.requirements, /SmartScreen warnings may still appear/);
      assert.match(enhanced.requirements, /does not suppress or remove those warnings/);
    }

    for (const query of [
      "?tag=brainstem-beta-v9.9.9",
      "?repo=contoso/frontier-fork",
      "?repo=../payload",
    ]) {
      await navigate(browser.cdp, browser.sessionId, `${site.pageUrl}${query}`, {
        width: 640,
        height: 900,
        scripts: true,
      });
      const failedRelease = await evaluate(
        browser.cdp,
        browser.sessionId,
        `(async () => {
          for (let attempt = 0; attempt < 100; attempt += 1) {
            if (document.querySelector("#release-status").textContent.includes("unavailable")) break;
            await new Promise((resolve) => setTimeout(resolve, 20));
          }
          return {
            recoveryHidden: document.querySelector("#recovery-panel").hidden,
            scriptLinks: ["#windows-script", "#unix-script"].map(
              (selector) => document.querySelector(selector).getAttribute("href"),
            ),
            recoveryCommands: ["#recovery-windows-command", "#recovery-unix-command"].map(
              (selector) => document.querySelector(selector).textContent,
            ),
            notice: document.querySelector("#load-error").textContent,
          };
        })()`,
      );
      if (query.startsWith("?tag=")) {
        assert.equal(failedRelease.recoveryHidden, true);
        assert.deepEqual(failedRelease.scriptLinks, [null, null]);
        assert.match(failedRelease.notice, /No alternate release has been selected/);
      } else if (query === "?repo=../payload") {
        assert.equal(failedRelease.recoveryHidden, true);
        assert.deepEqual(failedRelease.scriptLinks, [null, null]);
        assert.match(failedRelease.notice, /No download has been selected/);
      } else {
        assert.equal(failedRelease.recoveryHidden, false);
        assert.ok(failedRelease.recoveryCommands.every(
          (command) => command.includes('RAPP_FRONTIER_REPO="contoso/frontier-fork"'),
        ));
        assert.match(failedRelease.notice, /UNTRUSTED REPOSITORY/);
      }
    }

    const sourceOnlyRelease = {
      id: 1,
      tag_name: "brainstem-beta-v0.1.0-beta.6",
      draft: false,
      prerelease: true,
      published_at: "2026-08-18T23:03:14Z",
      assets: [],
      body: "",
    };
    const sourceOnlyCommit = "985693ee9399e737e17f75b6c02a227fdb628551";
    await browser.cdp.send(
      "Page.addScriptToEvaluateOnNewDocument",
      {
        source: `(() => {
          const originalFetch = window.fetch.bind(window);
          const release = ${JSON.stringify(sourceOnlyRelease)};
          window.fetch = async (input, init) => {
            const url = String(input);
            if (url.includes("api.github.com") && url.includes("/releases?")) {
              await new Promise((resolve) => setTimeout(resolve, 250));
              return new Response(JSON.stringify([release]), {
                status: 200,
                headers: { "content-type": "application/json" },
              });
            }
            if (url.includes("api.github.com") && url.includes("/commits/")) {
              return new Response(JSON.stringify({ sha: "${sourceOnlyCommit}" }), {
                status: 200,
                headers: { "content-type": "application/json" },
              });
            }
            return originalFetch(input, init);
          };
        })();`,
      },
      browser.sessionId,
    );
    await navigate(
      browser.cdp,
      browser.sessionId,
      `${site.pageUrl}?source-only=beta.6`,
      { width: 640, height: 900, scripts: true },
    );
    const loading = await evaluate(
      browser.cdp,
      browser.sessionId,
      `({
        status: document.querySelector("#release-status").textContent.trim(),
        disabled: document.querySelector("#download-button").disabled,
        version: document.querySelector("#release-version").textContent.trim(),
        help: document.querySelector("#platform-help").textContent.trim(),
      })`,
    );
    assert.equal(loading.status, "Checking Frontier release");
    assert.equal(loading.disabled, true);
    assert.equal(loading.version, "Resolving");
    assert.match(loading.help, /Checking the release/);

    const sourceOnly = await evaluate(
      browser.cdp,
      browser.sessionId,
      `(async () => {
        for (let attempt = 0; attempt < 100; attempt += 1) {
          if (!document.querySelector("#download-button").disabled) break;
          await new Promise((resolve) => setTimeout(resolve, 20));
        }
        document.querySelector("#download-button").click();
        await new Promise((resolve) => setTimeout(resolve, 20));
        const download = document.querySelector("#download-selected");
        return {
          status: document.querySelector("#release-status").textContent.trim(),
          sourceStatus: document.querySelector("#source-status").textContent.trim(),
          warningHidden: document.querySelector("#load-error").hidden,
          dialogOpen: document.querySelector("#download-dialog").open,
          copyVisible: document.querySelector("#copy-selected").getClientRects().length > 0,
          downloadVisible: download.getClientRects().length > 0,
          downloadHref: download.getAttribute("href"),
          downloadName: download.getAttribute("download"),
          downloadText: download.textContent.trim(),
          guide: document.querySelector("#frontier-guide-link").href,
          security: document.querySelector("#security-link").href,
          license: document.querySelector("#license-link").href,
        };
      })()`,
    );
    assert.equal(sourceOnly.status, "Source prerelease ready");
    assert.match(sourceOnly.sourceStatus, /source-only/i);
    assert.equal(sourceOnly.warningHidden, true);
    assert.equal(sourceOnly.dialogOpen, true);
    assert.equal(sourceOnly.copyVisible, true);
    assert.equal(sourceOnly.downloadVisible, true);
    assert.match(sourceOnly.downloadHref, /^data:text\/plain;charset=utf-8,/);
    assert.match(sourceOnly.downloadName, /RAPP-Brainstem-Frontier/);
    assert.equal(sourceOnly.downloadText, "Download bootstrap");
    assert.match(sourceOnly.guide, /blob\/brainstem-beta-v0\.1\.0-beta\.6\/beta\/README\.md$/);
    assert.match(sourceOnly.security, /blob\/brainstem-beta-v0\.1\.0-beta\.6\/SECURITY\.md$/);
    assert.match(sourceOnly.license, /blob\/brainstem-beta-v0\.1\.0-beta\.6\/LICENSE$/);

    await browser.cdp.send(
      "Emulation.setEmulatedMedia",
      {
        features: [{ name: "prefers-reduced-motion", value: "reduce" }],
      },
      browser.sessionId,
    );
    const reducedMotion = await evaluate(
      browser.cdp,
      browser.sessionId,
      'getComputedStyle(document.documentElement).scrollBehavior',
    );
    assert.equal(reducedMotion, "auto");
  } finally {
    await browser?.close();
    await site.close();
  }
});
