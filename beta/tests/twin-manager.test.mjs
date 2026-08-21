import assert from "node:assert/strict";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);

import { TwinManager, twinManagerInternals } from "../electron/twin-manager.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (r) => (
  readFileSync(path.join(root, r), "utf8").replaceAll("\r\n", "\n")
);

test("twinSlug makes a safe agent-filename stem", () => {
  assert.equal(twinManagerInternals.twinSlug("JSON Doctor!"), "json-doctor");
  assert.equal(twinManagerInternals.twinSlug(""), "twin");
});

test("TwinManager requires a store client and brainstem config", () => {
  assert.throws(() => new TwinManager({ betaHome: "/x", storeClient: {} }), /brainstemConfig/);
  assert.throws(() => new TwinManager({ betaHome: "/x", brainstemConfig: {} }), /Store client/);
});

test("store hatch refuses a traversal filename before it can escape the twin agents directory", async (t) => {
  const temporary = mkdtempSync(path.join(tmpdir(), "rapp-twin-hatch-"));
  const betaHome = path.join(temporary, "home");
  const escaped = path.join(temporary, "escaped_agent.py");
  mkdirSync(betaHome);
  t.after(() => rmSync(temporary, { recursive: true, force: true }));

  const manager = new TwinManager({
    betaHome,
    brainstemConfig: {},
    storeClient: {
      download: async () => ({
        id: "escape",
        filename: "../../../../escaped_agent.py",
        source: "VALUE = 'outside'\n",
        sha256: "0".repeat(64),
        entry: { name: "Escape" },
      }),
    },
  });

  await assert.rejects(() => manager.hatch("escape"), /safe \*_agent\.py basename/);
  assert.equal(existsSync(escaped), false);
});

test("a twin is driven only over /chat — never a new route (canon)", () => {
  const src = read("electron/twin-manager.mjs");
  assert.match(src, /fetch\(`\$\{twin\.url\}\/chat`/);      // the wire is /chat
  assert.doesNotMatch(src, /fetch\([^)]*\/api\/agent/);        // never the legacy RCE route
  assert.match(src, /127\.0\.0\.1/);      // loopback-only
  assert.match(src, /sha256-verified|singleton_sha256|cartridge\.sha256/i);
});

test("main wires twins + store IPC and the Surgeon hatch tools", () => {
  const main = read("electron/main.mjs");
  const preload = read("electron/preload.cjs");
  const surgeon = read("electron/brain-surgeon.mjs");
  assert.match(main, /new TwinManager\(/);
  assert.match(main, /beta:twin-hatch/);
  assert.match(main, /beta:store-list/);
  assert.match(main, /twinManager\.stopAll\(\)/);
  assert.match(preload, /twinHatch:/);
  assert.match(preload, /onTwinEvent:/);
  assert.match(surgeon, /name: "hatch_rapplication"/);
  assert.match(surgeon, /name: "list_rapplications"/);
});

test("the herd renders a chat/work-log tile per twin", () => {
  const renderer = read("ui/renderer.js");
  const ui = read("ui/index.html");
  assert.match(renderer, /function twinTileFor/);
  assert.match(renderer, /handleTwinEvent/);
  assert.match(renderer, /twinClose/);
  assert.match(renderer, /function renderTwinChat/);      // the work-log/chat transcript
  assert.match(ui, /herd-tile\.twin/);
  assert.match(ui, /\.twin-chat/);
});

test("the Copilot Studio deploy twin is composed from the bundled Factory + Deploy agents (P2)", () => {
  const main = read("electron/main.mjs");
  const surgeon = read("electron/brain-surgeon.mjs");
  const src = read("electron/twin-manager.mjs");
  // hatchLocal composes a twin from local agent sources (not a store pull)
  assert.match(src, /async hatchLocal\(/);
  assert.match(src, /twin-needs-auth/);                 // pauses at the one user-owned auth step
  // main hatches the CS twin from the bundled deploy agents + resources
  assert.match(main, /rar_kody_w_factory_agent\.py/);
  assert.match(main, /rar_kody_w_copilot_studio_parity_deploy_agent\.py/);
  assert.match(main, /function hatchCopilotStudioTwin/);
  assert.match(main, /DRAFT-ONLY: never call release or publish/);
  // the Surgeon offloads to the twin instead of running it inline
  assert.match(surgeon, /name: "deploy_to_copilot_studio"/);
  assert.match(surgeon, /loops autonomously in the herd/);
});

test("small view = a chat/work-log over the twin's /chat; the full custom UI pops out (P3)", () => {
  const tm = read("electron/twin-manager.mjs");
  const main = read("electron/main.mjs");
  const renderer = read("ui/renderer.js");
  const ui = read("ui/index.html");
  const fs = require("node:fs");
  // the proxy is gone; the twin keeps the rapplication's static UI HTML
  assert.ok(!fs.existsSync(path.join(root, "electron/twin-ui-proxy.mjs")), "twin-ui-proxy.mjs should be removed");
  assert.doesNotMatch(tm, /startTwinUiProxy|uiProxyUrl/);
  // The pin law hardening: a twin's custom UI is never fetched unverified at
  // hatch time — it arrives sha-verified from the store client (cartridge
  // .uiHtml) or inside a verified egg. The old `twin.uiHtml = await fetch`
  // path must stay gone.
  assert.doesNotMatch(tm, /uiHtml = await fetch/);
  assert.match(tm, /spec\.uiHtml/);
  assert.match(tm, /cartridge\.uiHtml/);
  assert.match(tm, /uiHtml\(id\)/);
  assert.match(tm, /hasCustomUi/);
  assert.match(tm, /maxTwins/);
  // the tile is a chat log with a composer, NOT an inline custom-UI iframe
  assert.match(renderer, /function renderTwinChat/);
  assert.match(renderer, /function sendTwinMessage/);
  assert.match(renderer, /brainstemBeta\.twinChat\(id, text\)/);
  assert.doesNotMatch(renderer, /twin-frame|twin-ui-toggle/);
  assert.match(ui, /\.twin-chat/);
  assert.match(ui, /\.twin-comp/);
  // the full custom UI opens in the pop-out (which document.writes the UI)
  assert.match(renderer, /brainstemBeta\.twinPopOut/);
  assert.match(main, /function popOutTwin/);
  assert.match(main, /document\.open\(\); document\.write/);
});

test("the Brainstem loops with a twin autonomously — a genuine two-brain loop", () => {
  const tm = read("electron/twin-manager.mjs");
  const main = read("electron/main.mjs");
  const preload = read("electron/preload.cjs");
  const surgeon = read("electron/brain-surgeon.mjs");
  const renderer = read("ui/renderer.js");
  const ui = read("ui/index.html");
  // The loop plans over the visible Brainstem's /chat AND executes over the twin's /chat.
  assert.match(tm, /async loop\(id, goal/);
  assert.match(tm, /#brainstemPlan\(/);
  assert.match(tm, /\$\{base\}\/chat/);                 // plans over the Brainstem /chat
  assert.match(tm, /this\.chat\(id, instruction, \{ author: "Brainstem" \}\)/);  // twin executes; labeled Brainstem
  assert.match(tm, /brainstemUrl/);
  // main resolves the live Brainstem URL and exposes the loop over IPC + to the Surgeon.
  assert.match(main, /brainstemUrl: \(\) => state\.url/);
  assert.match(main, /beta:twin-loop/);
  assert.match(main, /loop: \(id, goal\) =>/);
  assert.match(preload, /twinLoop:/);
  assert.match(surgeon, /name: "loop_brainstem_with_twin"/);
  // the herd tile can start the loop, and it lights while looping.
  assert.match(renderer, /brainstemBeta\.twinLoop/);
  assert.match(renderer, /classList\.toggle\("looping"/);
  assert.match(ui, /\.tw-loop/);
});

test("the AI can drive a twin's own UI in-tile (P3c)", () => {
  const server = read("electron/ui-driver-server.mjs");
  const surgeon = read("electron/brain-surgeon.mjs");
  const main = read("electron/main.mjs");
  assert.match(server, /function twinFrame/);
  assert.match(server, /resolveTwinUrls/);
  assert.match(main, /resolveTwinUrls: \(id\) =>/);
  assert.match(surgeon, /name: "drive_twin"/);
  assert.match(surgeon, /action: "run",\s*twin: twinId/);
});

test("away-auth: notification + browser pop-out, never capturing credentials (P3d)", () => {
  const main = read("electron/main.mjs");
  const surgeon = read("electron/brain-surgeon.mjs");
  const preload = read("electron/preload.cjs");
  assert.match(main, /new Notification\(/);
  assert.match(main, /notifyTwinNeedsAuth/);
  assert.match(main, /shell\.openExternal/);          // identity auth opens the user's own browser
  assert.match(surgeon, /name: "open_auth_window"/);
  assert.match(surgeon, /never capture or type their credentials/i);
  assert.match(preload, /twinPopOut:/);
  assert.match(preload, /openAuth:/);
});

test("twin molt.json generations mirror once with their archived source", (t) => {
  const temporary = mkdtempSync(path.join(tmpdir(), "rapp-twin-molts-"));
  t.after(() => rmSync(temporary, { recursive: true, force: true }));
  const molterHome = path.join(temporary, "molter");
  const generation = path.join(
    molterHome,
    "molts",
    "weather",
    "gen-001",
  );
  mkdirSync(generation, { recursive: true });
  const source = [
    "class WeatherAgent:",
    "    def __init__(self):",
    "        self.name = \"WeatherAgent\"",
    "",
  ].join("\n");
  writeFileSync(path.join(generation, "agent.py"), source);
  writeFileSync(path.join(generation, "molt.json"), JSON.stringify({
    generation: 1,
    kind: "mutate",
    verdict: "verified",
    sha256: "recorded-by-molter",
    detail: { tool_name: "WeatherAgent" },
  }));
  const writes = [];
  const manager = Object.create(TwinManager.prototype);
  manager.ledger = {
    recordAgent: (row) => writes.push(row),
  };
  const twin = {
    dir: temporary,
    id: "weather-1",
    molterHome,
    rappid: "rappid:@microsoft/weather",
    seenMolts: new Set(),
  };

  const first = manager.mirrorMolts(twin);
  const second = manager.mirrorMolts(twin);
  assert.equal(first.length, 1);
  assert.equal(second.length, 0);
  assert.equal(writes.length, 1);
  assert.equal(writes[0].event, "molted");
  assert.equal(writes[0].filename, "weather_agent.py");
  assert.equal(writes[0].toolName, "WeatherAgent");
  assert.equal(writes[0].origin, "molter");
  assert.equal(writes[0].sourcePath, path.join(generation, "agent.py"));
  assert.match(writes[0].sha256, /^[a-f0-9]{64}$/);
  assert.equal(writes[0].detail.recorded_sha256, "recorded-by-molter");
});

test("twin hatches and chat completions are wired into the shared ledger", () => {
  const source = read("electron/twin-manager.mjs");
  assert.match(source, /event: "hatched"/);
  assert.match(source, /surface: `twin:\$\{id\}`/);
  assert.match(source, /MOLTER_HOME: molterHome/);
  assert.match(source, /path\.join\(\s*this\.betaHome,\s*"molts"/);
  assert.match(source, /this\.mirrorMolts\(twin\)/);
  assert.match(source, /recordCompletedTurn\(this\.ledger/);
  assert.match(source, /finally \{\s*this\.mirrorMolts\(twin\)/);
  assert.match(source, /if \(twin\) this\.mirrorMolts\(twin\)/);
  assert.match(source, /surface: "brainstem"/);
  assert.match(source, /sessionId: data\.session_id \|\| sessionId/);
});
