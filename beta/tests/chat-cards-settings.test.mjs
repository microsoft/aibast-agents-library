import assert from "node:assert/strict";
import {
  mkdtempSync,
  readFileSync,
  rmSync,
  statSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
  changeAprilFoolsSettings,
  composeChatCardsFrameBridgeSource,
  parseAprilFoolsCommand,
  readAprilFoolsSettings,
  writeAprilFoolsSettings,
} from "../electron/chat-cards.mjs";

test("April Fools settings default off and persist beside Chat Look", (t) => {
  const betaHome = mkdtempSync(path.join(tmpdir(), "rapp-chat-cards-"));
  t.after(() => rmSync(betaHome, { recursive: true, force: true }));

  assert.deepEqual(readAprilFoolsSettings({ betaHome, env: {} }), {
    aprilFools: { on: false, table: "poker", customTablePath: null },
    aprilFoolsOverridden: false,
    file: path.join(betaHome, "settings.json"),
    storedAprilFools: { on: false, table: "poker", customTablePath: null },
  });

  writeAprilFoolsSettings({
    betaHome,
    aprilFools: { on: true, table: "uno" },
  });
  const changed = changeAprilFoolsSettings({
    betaHome,
    aprilFools: { table: "mtg" },
    env: {},
  });
  assert.deepEqual(changed.aprilFools, {
    on: true,
    table: "mtg",
    customTablePath: null,
  });
  const file = path.join(betaHome, "settings.json");
  assert.deepEqual(JSON.parse(readFileSync(file, "utf8")), {
    aprilFools: {
      on: true,
      table: "mtg",
      customTablePath: null,
    },
  });
  if (process.platform !== "win32") {
    assert.equal(statSync(file).mode & 0o777, 0o600);
  }
});

test("RAPP_APRIL_FOOLS is authoritative without overwriting the stored flag", (t) => {
  const betaHome = mkdtempSync(path.join(tmpdir(), "rapp-chat-cards-env-"));
  t.after(() => rmSync(betaHome, { recursive: true, force: true }));
  writeAprilFoolsSettings({ betaHome, aprilFools: { on: false } });

  const forced = readAprilFoolsSettings({
    betaHome,
    env: { RAPP_APRIL_FOOLS: "1" },
  });
  assert.equal(forced.aprilFools.on, true);
  assert.equal(forced.storedAprilFools.on, false);
  assert.equal(forced.aprilFoolsOverridden, true);
  assert.equal(
    readAprilFoolsSettings({
      betaHome,
      env: { RAPP_APRIL_FOOLS: "0" },
    }).aprilFools.on,
    false,
  );
});

test("April Fools composer word is exact and trimmed", () => {
  assert.equal(parseAprilFoolsCommand("april fools")?.action, "toggle-april-fools");
  assert.equal(parseAprilFoolsCommand("  april fools \n")?.action, "toggle-april-fools");
  assert.equal(parseAprilFoolsCommand("April Fools"), null);
  assert.equal(parseAprilFoolsCommand("please enable april fools"), null);
});

test("mode-off bridge composition is byte-identical", (t) => {
  const checkpointSource = "checkpoint-frame-bridge\n\u0000bytes";
  const disabled = composeChatCardsFrameBridgeSource(checkpointSource, {
    on: false,
    table: "poker",
    customTablePath: null,
  });
  assert.equal(disabled, checkpointSource);
  assert.doesNotMatch(disabled, /AprilFools|chat.card|card table/i);
  t.diagnostic("mode-off bridge composition: byte-identical");
});

test("main, preload, and both menus expose the guarded toggle", () => {
  const main = readFileSync(
    new URL("../electron/main.mjs", import.meta.url),
    "utf8",
  );
  const preload = readFileSync(
    new URL("../electron/preload.cjs", import.meta.url),
    "utf8",
  );
  assert.match(main, /ipcMain\.handle\("beta:set-april-fools"/);
  assert.match(main, /id: "april-fools-card-table"/);
  assert.match(main, /label: "April Fools: Card Table"/);
  assert.match(main, /composeChatCardsFrameBridgeSource\(checkpointSource, aprilFools\)/);
  assert.match(preload, /setAprilFools:/);
});
