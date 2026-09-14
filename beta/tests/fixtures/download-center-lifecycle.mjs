import assert from "node:assert/strict";
import { writeFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const filename = fileURLToPath(import.meta.url);
const betaRoot = path.resolve(path.dirname(filename), "../..");

if (process.argv.includes("--fake-chrome")) {
  process.stderr.write("Synthetic Chrome startup failure: no DevTools response.\n");
  process.on("SIGTERM", () => {});
  setInterval(() => {}, 1000);
} else {
  const { closeResources, launchBrowser, startStaticServer } = await import("../helpers/download-center-browser.mjs");
  const mode = process.env.DOWNLOAD_CENTER_FAILURE_CASE;
  test(`deliberately failing browser fixture: ${mode}`, {
    timeout: mode === "test-timeout" ? 1000 : 10000,
  }, async (t) => {
    const site = await startStaticServer(betaRoot);
    let browser;
    t.after(() => closeResources([browser, site]));
    const fake = mode === "startup-failure" || mode === "test-timeout";
    browser = await launchBrowser({
      betaRoot,
      signal: t.signal,
      ...(fake ? {
        executable: process.execPath,
        executableArgs: [filename, "--fake-chrome"],
        timeoutMs: mode === "test-timeout" ? 5000 : 1000,
      } : {}),
      onSpawn: (resource) => {
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
