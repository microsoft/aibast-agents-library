import assert from "node:assert/strict";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
  copilotPackageName,
  readGitHubTokenFile,
  withTimeout,
} from "../electron/copilot-runtime.mjs";

test("Copilot package selection follows platform and architecture", () => {
  assert.equal(
    copilotPackageName("darwin", "arm64"),
    "@github/copilot-darwin-arm64",
  );
  assert.equal(
    copilotPackageName("win32", "x64"),
    "@github/copilot-win32-x64",
  );
  assert.equal(
    copilotPackageName("linux", "x64"),
    "@github/copilot-linux-x64",
  );
});

test("Copilot startup timeout rejects a hung runtime", async () => {
  await assert.rejects(
    withTimeout(new Promise(() => {}), "test runtime", 5),
    /test runtime did not start within 5ms/,
  );
});

test("Copilot startup timeout preserves successful results", async () => {
  assert.equal(await withTimeout(Promise.resolve("ready"), "test runtime", 50), "ready");
});

test("Copilot runtime reads the protected Brainstem device token", () => {
  const directory = mkdtempSync(path.join(tmpdir(), "brainstem-token-"));
  const tokenFile = path.join(directory, ".copilot_token");
  try {
    writeFileSync(tokenFile, JSON.stringify({
      access_token: "ghu_example",
      refresh_token: "hidden",
    }));
    assert.equal(readGitHubTokenFile(tokenFile), "ghu_example");
    writeFileSync(tokenFile, "{not json");
    assert.equal(readGitHubTokenFile(tokenFile), null);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
