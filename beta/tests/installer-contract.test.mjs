import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const unix = readFileSync(path.join(root, "install.sh"), "utf8");
const windows = readFileSync(path.join(root, "install.cmd"), "utf8");
const installerPage = readFileSync(path.join(root, "index.html"), "utf8");
const main = readFileSync(path.join(root, "electron", "main.mjs"), "utf8");
const preload = readFileSync(path.join(root, "electron", "preload.cjs"), "utf8");
const ui = readFileSync(path.join(root, "ui", "index.html"), "utf8");
const renderer = readFileSync(path.join(root, "ui", "renderer.js"), "utf8");

test("beta installers use AIBAST as the canonical source", () => {
  for (const installer of [unix, windows]) {
    assert.match(installer, /microsoft\/aibast-agents-library/);
    assert.doesNotMatch(installer, /kody-w\/rapp-installer/);
  }
});

test("beta installers exclude the solution library", () => {
  assert.match(unix, /fetch --progress --filter=blob:none --depth 1 origin "\$REPO_REF"/);
  assert.match(unix, /sparse-checkout set beta/);
  assert.match(windows, /fetch --progress --filter=blob:none --depth 1 origin "%REPO_REF%"/);
  assert.match(windows, /sparse-checkout set beta/);
  assert.match(unix, /--no-launch/);
  assert.match(windows, /--no-launch/);
});

test("released beta installs can pin the launcher and runtime to one commit", () => {
  for (const installer of [unix, windows]) {
    assert.match(installer, /BRAINSTEM_BETA_COMMIT/);
    assert.match(installer, /40-character commit SHA/);
    assert.match(installer, /reset --hard FETCH_HEAD/);
  }
  assert.match(unix, /--version "\$REPO_COMMIT"/);
  assert.match(unix, /GIT_CONFIG_KEY_/);
  assert.match(windows, /--version "%REPO_COMMIT%"/);
  assert.match(windows, /GIT_CONFIG_KEY_0/);
});

test("dedicated beta page resolves fork releases without changing main install", () => {
  assert.match(installerPage, /brainstem-beta-v/);
  assert.match(installerPage, /api\.github\.com\/repos/);
  assert.match(installerPage, /BRAINSTEM_BETA_COMMIT/);
  assert.match(installerPage, /beta\/install\.sh/);
  assert.match(installerPage, /beta\/install\.cmd/);
  assert.match(installerPage, /The production installer is unchanged/);
  assert.match(installerPage, /--cp-bg/);
  assert.match(installerPage, /data-theme/);
});

test("dedicated beta page scripts parse", () => {
  const scripts = [...installerPage.matchAll(/<script>([\s\S]*?)<\/script>/g)];
  assert.ok(scripts.length >= 2);
  for (const [, source] of scripts) {
    assert.doesNotThrow(() => new Function(source));
  }
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

test("desktop chrome omits redundant runtime status pills", () => {
  assert.doesNotMatch(ui, /brainstem-status|copilot-status/);
  assert.doesNotMatch(renderer, /brainstemStatus|copilotStatus|setPill/);
});
