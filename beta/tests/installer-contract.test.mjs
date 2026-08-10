import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const unix = readFileSync(path.join(root, "install.sh"), "utf8");
const windows = readFileSync(path.join(root, "install.cmd"), "utf8");
const main = readFileSync(path.join(root, "electron", "main.mjs"), "utf8");
const preload = readFileSync(path.join(root, "electron", "preload.cjs"), "utf8");
const ui = readFileSync(path.join(root, "ui", "index.html"), "utf8");

test("beta installers use AIBAST as the canonical source", () => {
  for (const installer of [unix, windows]) {
    assert.match(installer, /microsoft\/aibast-agents-library/);
    assert.doesNotMatch(installer, /kody-w\/rapp-installer/);
  }
});

test("beta installers exclude the solution library", () => {
  assert.match(unix, /--filter=blob:none --sparse --depth 1/);
  assert.match(unix, /sparse-checkout set beta/);
  assert.match(windows, /--filter=blob:none --sparse --depth 1/);
  assert.match(windows, /sparse-checkout set beta/);
  assert.match(unix, /--no-launch/);
  assert.match(windows, /--no-launch/);
});

test("beta launcher reuses the global Brainstem and preserves VS Code pop-out", () => {
  assert.match(main, /resolveBrainstemConfig/);
  assert.match(main, /beta:open-vscode/);
  assert.match(main, /vscode:\/\/file/);
  assert.match(preload, /openVscode/);
});

test("Electron renderer is isolated from Node", () => {
  assert.match(main, /contextIsolation: true/);
  assert.match(main, /nodeIntegration: false/);
  assert.match(main, /sandbox: true/);
  assert.match(main, /BRAINSTEM_BETA_HEADLESS/);
  assert.match(main, /BRAINSTEM_BETA_SMOKE_EXIT_MS/);
});

test("first-run guide explains the customer rapid-use-case loop", () => {
  assert.match(ui, /Can AI do this\?/);
  assert.match(ui, /When should I reach for it\?/);
  assert.match(ui, /Scout/);
  assert.match(ui, /Copilot Studio \/ Foundry/);
  assert.match(ui, /Do not call the prototype production-ready/);
});
