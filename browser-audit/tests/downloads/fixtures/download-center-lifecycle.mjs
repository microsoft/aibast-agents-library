import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const filename = fileURLToPath(import.meta.url);
const betaRoot = path.resolve(path.dirname(filename), "../../../../beta");

if (process.argv.includes("--fake-chrome")) {
  const resourceFile = process.env.DOWNLOAD_CENTER_RESOURCE_FILE;
  writeFileSync(resourceFile, JSON.stringify({
    ...JSON.parse(readFileSync(resourceFile, "utf8")),
    pid: process.pid,
  }));
  process.stderr.write("Synthetic Chrome startup failure: no DevTools response.\n");
  process.on("SIGTERM", () => {});
  setInterval(() => {}, 1000);
} else {
  const { BROWSER_STARTUP_TIMEOUT_MS, closeResources, launchBrowser, startStaticServer } = await import("../helpers/download-center-browser.mjs");
  const mode = process.env.DOWNLOAD_CENTER_FAILURE_CASE;
  test(`deliberately failing browser fixture: ${mode}`, {
    timeout: mode === "test-timeout" ? 1000 : BROWSER_STARTUP_TIMEOUT_MS + 10000,
  }, async (t) => {
    const site = await startStaticServer(betaRoot);
    writeFileSync(process.env.DOWNLOAD_CENTER_RESOURCE_FILE, JSON.stringify({
      pageUrl: site.pageUrl,
    }));
    let browser;
    t.after(() => closeResources([browser, site]));
    const fake = mode === "startup-failure" || mode === "test-timeout";
    browser = await launchBrowser({
      signal: t.signal,
      ...(fake ? {
        executable: process.execPath,
        executableArgs: [filename, "--fake-chrome"],
        startupTimeoutMs: mode === "test-timeout" ? 5000 : 1000,
      } : {}),
      onLaunch: (resource) => {
        writeFileSync(process.env.DOWNLOAD_CENTER_RESOURCE_FILE, JSON.stringify({
          ...resource,
          pageUrl: site.pageUrl,
        }));
      },
    });
    assert.equal(mode, "ready-assertion");
    assert.fail("Deliberate assertion after real Chrome startup");
  });
}
