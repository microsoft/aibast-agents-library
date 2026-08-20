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

function managerFixture({ changed = 1, unchanged = 0, failed = [] } = {}) {
  const calls = [];
  // The real route manager returns a report saying what actually moved. A double
  // that returns nothing makes every command look like a no-op, which is exactly
  // the state the honest-reporting rules are meant to detect — so it has to
  // model a real move by default.
  const report = () => ({
    disabled: false,
    changed: Array.from({ length: changed }, (_, i) => `rappid:@grail/a${i}:x`),
    unchanged: Array.from({ length: unchanged }, (_, i) => `rappid:@grail/u${i}:x`),
    failed,
  });
  return {
    calls,
    manager: {
      rollbackLineage: () => { calls.push("baseline"); return report(); },
      restoreLineage: () => { calls.push("restore"); return report(); },
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

test("lineage commands round-trip the full wire result shape", async () => {
  // The frame bridge forwards this result verbatim over postMessage and
  // fabricates the /chat and /chat/stream responses from result.reply, so the
  // exact shape IS the wire protocol.
  const baselineRun = managerFixture();
  const baseline = await executeLineageCommand({
    message: "baseline",
    routeManager: baselineRun.manager,
  });
  assert.deepEqual(baseline, {
    intercepted: true,
    action: "baseline",
    fallback: null,
    reply: lineageControlReplies.baseline,
    compositionHash: "composed",
    restored: undefined,
    // changed/unchanged are part of the wire shape: they are what lets a caller
    // tell a real restore from one that moved nothing.
    changed: 1,
    unchanged: 0,
    url: "http://127.0.0.1:7001",
  });
  assert.deepEqual(baselineRun.calls, ["baseline", "materialize"]);

  const restoreRun = managerFixture();
  const restored = await executeLineageCommand({
    message: "restore",
    routeManager: restoreRun.manager,
  });
  assert.equal(restored.intercepted, true);
  assert.equal(restored.action, "restore");
  assert.equal(restored.reply, lineageControlReplies.restore);
  assert.equal(restored.restored, true);
  assert.equal(restored.compositionHash, "composed");
  assert.equal(restored.url, "http://127.0.0.1:7001");
  assert.deepEqual(restoreRun.calls, ["restore", "materialize"]);
});

test("default safe words pass through untouched when custom words are configured", async () => {
  const env = {
    RAPP_BASELINE_SAFEWORD: "factory settings",
    RAPP_RESTORE_WORD: "grow again",
  };
  const { calls, manager } = managerFixture();
  const passed = await executeLineageCommand({
    message: "restore",
    routeManager: manager,
    env,
  });
  assert.deepEqual(passed, { intercepted: false, message: "restore" });
  assert.deepEqual(calls, [], "the default word must reach Grail untouched");

  const reset = await executeLineageCommand({
    message: " factory settings ",
    routeManager: manager,
    env,
  });
  assert.equal(reset.action, "baseline");
  assert.equal(reset.reply, lineageControlReplies.baseline);
  assert.deepEqual(calls, ["baseline", "materialize"]);
});

test("a partially compatible restore reports the kept-last-good compromise", async () => {
  const { calls, manager } = managerFixture();
  manager.lastLineageFallback = {
    accepted: ["rappid:@frontier/good-ring:cafef00d"],
    rejected: ["rappid:@frontier/bad-ring:deadbeef"],
    strategy: "last-good",
  };
  const result = await executeLineageCommand({
    message: "restore",
    routeManager: manager,
  });
  assert.equal(result.intercepted, true);
  assert.equal(result.restored, false);
  assert.notEqual(result.reply, lineageControlReplies.restore);
  assert.match(result.reply, /compatible verified molts.*incompatible rings/i);
  assert.deepEqual(result.fallback, manager.lastLineageFallback);
  assert.deepEqual(calls, ["restore", "materialize"]);
});

test("baseline never reports a partial restore even with fallback state", async () => {
  const { manager } = managerFixture();
  manager.lastLineageFallback = {
    accepted: [],
    rejected: ["rappid:@frontier/bad-ring:deadbeef"],
    strategy: "last-good",
  };
  const result = await executeLineageCommand({
    message: "baseline",
    routeManager: manager,
  });
  assert.equal(result.reply, lineageControlReplies.baseline);
  assert.equal(result.restored, undefined);
});

test("a safe word without the route manager is an error, not a silent pass", async () => {
  await assert.rejects(
    executeLineageCommand({ message: "restore" }),
    /Frontier route manager/,
  );
});

test("restore reports a refused composition instead of claiming success", async () => {
  const { manager } = managerFixture();
  manager.lastLineageFallback = {
    accepted: [],
    rejected: ["rappid:@frontier/bad-ring:deadbeef"],
    strategy: "last-good",
  };
  const result = await executeLineageCommand({
    message: "restore",
    routeManager: manager,
  });
  assert.equal(result.restored, false);
  assert.notEqual(result.reply, lineageControlReplies.restore);
  assert.match(result.reply, /could not activate.*last-good/i);
});

test("renderer intercepts before Grail chat and main exposes the lineage IPC", () => {
  const renderer = readFileSync(path.join(betaRoot, "ui", "renderer.js"), "utf8");
  const main = readFileSync(path.join(betaRoot, "electron", "main.mjs"), "utf8");
  const preload = readFileSync(path.join(betaRoot, "electron", "preload.cjs"), "utf8");
  assert.match(renderer, /type === "rapp-beta:lineage-chat"/);
  assert.match(renderer, /rapp-beta:lineage-confirmation-ack/);
  assert.match(renderer, /pendingLineageReply\.url !== loadedFrameUrl/);
  assert.match(renderer, /brainstemBeta\.lineageCommand/);
  assert.match(main, /beta:lineage-command/);
  assert.match(main, /rapp-beta:lineage-confirmation-ack/);
  assert.match(main, /target\.pathname === "\/chat\/stream"/);
  assert.match(preload, /lineageCommand:/);
  // The synthetic /chat/stream done-frame the bridge fabricates must keep the
  // DOUBLE-escaped separator: the bridge lives inside a template literal, so
  // only \\n\\n in main.mjs source puts the \n\n escape into the injected
  // script and a real blank-line separator on the wire. A single-escaped
  // newline breaks Grail's SSE parser ("stream ended without done").
  assert.match(
    main,
    /const frame = "data: " \+ JSON\.stringify\(\{\s+type: "done",\s+response: result\.reply,\s+agent_logs: "",\s+streamed: false,\s+\}\) \+ "\\\\n\\\\n";/,
  );
  assert.match(main, /text\/event-stream/);
});
