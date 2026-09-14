import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { BROWSER_STARTUP_TIMEOUT_MS, closeResources, launchBrowser, startStaticServer } from "./helpers/download-center-browser.mjs";

const betaRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../beta");

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
  await Promise.all([loaded, cdp.send("Page.navigate", { url }, sessionId)]);
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
  assert.equal(
    result.exceptionDetails,
    undefined,
    result.exceptionDetails?.exception?.description || result.exceptionDetails?.text,
  );
  return result.result.value;
}

async function waitForPageState(cdp, sessionId, condition, label) {
  await evaluate(cdp, sessionId, `(async () => {
    const deadline = performance.now() + 3000;
    while (!(${condition})) {
      if (performance.now() >= deadline) {
        throw new Error("Timed out waiting for " + ${JSON.stringify(label)}
          + ": " + document.querySelector("#release-status")?.textContent
          + "; " + document.querySelector("#load-error")?.textContent);
      }
      await new Promise((resolve) => setTimeout(resolve, 20));
    }
  })()`);
}

test("Download Center works without JavaScript and stays narrow under stress", {
  timeout: BROWSER_STARTUP_TIMEOUT_MS + 30000,
}, async (t) => {
  const site = await startStaticServer(betaRoot);
  let browser;
  t.after(() => closeResources([browser, site]));
  try {
    browser = await launchBrowser({ signal: t.signal });
    t.diagnostic(`Download Center browser: ${browser.executablePath} (${browser.version}); ${process.platform}/${process.arch}`);
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

    await browser.cdp.send("Page.addScriptToEvaluateOnNewDocument", {
      source: `(() => {
        const original = navigator.userAgentData;
        Object.defineProperty(navigator, "userAgentData", {
          configurable: true,
          value: {
            platform: original?.platform || navigator.platform,
            async getHighEntropyValues(hints) {
              await new Promise((resolve) => setTimeout(resolve, 350));
              return original?.getHighEntropyValues ? original.getHighEntropyValues(hints) : {};
            },
          },
        });
      })();`,
    }, browser.sessionId);

    for (const width of [320, 640]) {
      await navigate(
        browser.cdp,
        browser.sessionId,
        `${site.pageUrl}?scoutTheme=dark&scripts=${width}`,
        { width, height: 800, scripts: true },
      );
      await waitForPageState(
        browser.cdp, browser.sessionId,
        'document.querySelector("#release-status").textContent === "Release check unavailable"',
        "release recovery initialization",
      );
      const enhanced = await evaluate(
        browser.cdp,
        browser.sessionId,
        `(async () => {
          document.querySelector("#expand-all").click();
          const notice = document.querySelector("#load-error");
          notice.hidden = false;
          notice.textContent =
            "GitHub returned 403 for https://api.github.com/repos/microsoft/aibast-agents-library/releases?per_page=100";
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
      await waitForPageState(
        browser.cdp, browser.sessionId,
        'document.querySelector("#release-status").textContent.includes("unavailable")',
        `release failure for ${query}`,
      );
      const failedRelease = await evaluate(
        browser.cdp,
        browser.sessionId,
        `(async () => {
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
          const releaseGate = new Promise((resolve) => {
            window.resolveDownloadCenterFixture = resolve;
          });
          window.fetch = async (input, init) => {
            const url = String(input);
            if (url.includes("api.github.com") && url.includes("/releases?")) {
              window.downloadCenterFixtureRequested = true;
              await releaseGate;
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
    await waitForPageState(
      browser.cdp, browser.sessionId,
      "window.downloadCenterFixtureRequested === true",
      "pending release request",
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

    await evaluate(browser.cdp, browser.sessionId, "window.resolveDownloadCenterFixture()");
    await waitForPageState(
      browser.cdp, browser.sessionId,
      '!document.querySelector("#download-button").disabled',
      "resolved source release",
    );
    const sourceOnly = await evaluate(
      browser.cdp,
      browser.sessionId,
      `(async () => {
        document.querySelector("#download-button").click();
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
    // The test hook also runs on cancellation; both closers are idempotent.
    await closeResources([browser, site]);
  }
});
