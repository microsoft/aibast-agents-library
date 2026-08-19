import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import {
  executeLineageCommand,
  lineageControlReplies,
  parseLineageCommand,
} from "../electron/lineage-control.mjs";


const betaRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function managerFixture() {
  const calls = [];
  return {
    calls,
    manager: {
      rollbackLineage: () => calls.push("baseline"),
      restoreLineage: () => calls.push("restore"),
      startDefault: async () => {
        calls.push("materialize");
        return {
          compositionHash: "composed",
          url: "http://127.0.0.1:7001",
        };
      },
    },
  };
}

test("safe-word interceptor matches only the exact trimmed word", async () => {
  assert.equal(parseLineageCommand("talk about baseline"), null);
  assert.equal(parseLineageCommand("baseline please"), null);
  assert.equal(parseLineageCommand("BASELINE"), null);
  assert.deepEqual(parseLineageCommand("  baseline \n"), {
    action: "baseline",
    original: "  baseline \n",
    word: "baseline",
  });

  const { calls, manager } = managerFixture();
  const ordinary = "please keep the baseline behavior in this answer";
  assert.deepEqual(
    await executeLineageCommand({ message: ordinary, routeManager: manager }),
    { intercepted: false, message: ordinary },
  );
  assert.deepEqual(calls, [], "normal chat must pass without any lineage action");

  const reverted = await executeLineageCommand({
    message: "baseline",
    routeManager: manager,
  });
  assert.equal(reverted.intercepted, true);
  assert.equal(reverted.reply, lineageControlReplies.baseline);
  assert.deepEqual(calls, ["baseline", "materialize"]);
});

test("safe-word interceptor honors custom baseline and restore words", async () => {
  const env = {
    RAPP_BASELINE_SAFEWORD: "factory settings",
    RAPP_RESTORE_WORD: "grow again",
  };
  assert.equal(parseLineageCommand("baseline", env), null);
  assert.equal(
    parseLineageCommand(" factory settings ", env).action,
    "baseline",
  );
  assert.equal(parseLineageCommand("grow again", env).action, "restore");

  const { calls, manager } = managerFixture();
  const restored = await executeLineageCommand({
    message: "grow again",
    routeManager: manager,
    env,
  });
  assert.equal(restored.reply, lineageControlReplies.restore);
  assert.deepEqual(calls, ["restore", "materialize"]);
});

test("renderer intercepts before Grail chat and main exposes the lineage IPC", () => {
  const renderer = readFileSync(path.join(betaRoot, "ui", "renderer.js"), "utf8");
  const main = readFileSync(path.join(betaRoot, "electron", "main.mjs"), "utf8");
  const preload = readFileSync(path.join(betaRoot, "electron", "preload.cjs"), "utf8");
  assert.match(renderer, /type === "rapp-beta:lineage-chat"/);
  assert.match(renderer, /brainstemBeta\.lineageCommand/);
  assert.match(main, /beta:lineage-command/);
  assert.match(main, /target\.pathname === "\/chat\/stream"/);
  assert.match(preload, /lineageCommand:/);
});
