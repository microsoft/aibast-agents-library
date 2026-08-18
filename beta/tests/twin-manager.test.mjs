import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import { TwinManager, twinManagerInternals } from "../electron/twin-manager.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (r) => readFileSync(path.join(root, r), "utf8");

test("twinSlug makes a safe agent-filename stem", () => {
  assert.equal(twinManagerInternals.twinSlug("JSON Doctor!"), "json-doctor");
  assert.equal(twinManagerInternals.twinSlug(""), "twin");
});

test("TwinManager requires a store client and brainstem config", () => {
  assert.throws(() => new TwinManager({ betaHome: "/x", storeClient: {} }), /brainstemConfig/);
  assert.throws(() => new TwinManager({ betaHome: "/x", brainstemConfig: {} }), /Store client/);
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

test("the herd renders twin tiles bound to the worker port", () => {
  const renderer = read("ui/renderer.js");
  const ui = read("ui/index.html");
  assert.match(renderer, /function twinTileFor/);
  assert.match(renderer, /handleTwinEvent/);
  assert.match(renderer, /twinClose/);
  assert.match(renderer, /\$\{twin\.url\}\/\?beta=1/);   // iframe of the twin's own port
  assert.match(ui, /herd-tile\.twin/);
  assert.match(ui, /frame-src http:\/\/127\.0\.0\.1/);   // CSP allows the twin iframe
});
