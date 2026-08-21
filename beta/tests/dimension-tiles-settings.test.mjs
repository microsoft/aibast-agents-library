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
  changeTableViewSettings,
  composeDimensionTilesFrameBridgeSource,
  parseTableViewCommand,
  readTableViewSettings,
  writeTableViewSettings,
} from "../electron/dimension-tiles.mjs";

test("Table view settings default off and persist beside Chat Look", (t) => {
  const betaHome = mkdtempSync(path.join(tmpdir(), "rapp-dimension-tiles-"));
  t.after(() => rmSync(betaHome, { recursive: true, force: true }));

  assert.deepEqual(readTableViewSettings({ betaHome, env: {} }), {
    tableView: { on: false, layout: "table", customLayoutPath: null },
    tableViewOverridden: false,
    file: path.join(betaHome, "settings.json"),
    storedTableView: { on: false, layout: "table", customLayoutPath: null },
  });

  writeTableViewSettings({
    betaHome,
    tableView: { on: true, layout: "hand" },
  });
  const changed = changeTableViewSettings({
    betaHome,
    tableView: { layout: "battlefield" },
    env: {},
  });
  assert.deepEqual(changed.tableView, {
    on: true,
    layout: "battlefield",
    customLayoutPath: null,
  });
  const file = path.join(betaHome, "settings.json");
  assert.deepEqual(JSON.parse(readFileSync(file, "utf8")), {
    tableView: {
      on: true,
      layout: "battlefield",
      customLayoutPath: null,
    },
  });
  if (process.platform !== "win32") {
    assert.equal(statSync(file).mode & 0o777, 0o600);
  }
});

test("RAPP_TABLE_VIEW is authoritative without overwriting the stored flag", (t) => {
  const betaHome = mkdtempSync(path.join(tmpdir(), "rapp-dimension-tiles-env-"));
  t.after(() => rmSync(betaHome, { recursive: true, force: true }));
  writeTableViewSettings({ betaHome, tableView: { on: false } });

  const forced = readTableViewSettings({
    betaHome,
    env: { RAPP_TABLE_VIEW: "1" },
  });
  assert.equal(forced.tableView.on, true);
  assert.equal(forced.storedTableView.on, false);
  assert.equal(forced.tableViewOverridden, true);
  assert.equal(
    readTableViewSettings({
      betaHome,
      env: { RAPP_TABLE_VIEW: "0" },
    }).tableView.on,
    false,
  );
});

test("Table view composer word is exact and trimmed", () => {
  assert.equal(parseTableViewCommand("table view")?.action, "toggle-table-view");
  assert.equal(parseTableViewCommand("  table view \n")?.action, "toggle-table-view");
  assert.equal(parseTableViewCommand("Table view"), null);
  assert.equal(parseTableViewCommand("please enable table view"), null);
});

test("mode-off bridge composition is byte-identical", (t) => {
  const checkpointSource = "checkpoint-frame-bridge\n\u0000bytes";
  const disabled = composeDimensionTilesFrameBridgeSource(checkpointSource, {
    on: false,
    layout: "table",
    customLayoutPath: null,
  });
  assert.equal(disabled, checkpointSource);
  assert.doesNotMatch(disabled, /TableView|dimension.tile|table view/i);
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
  assert.match(main, /ipcMain\.handle\("beta:set-table-view"/);
  assert.match(main, /id: "table-view"/);
  assert.match(main, /label: "Table view"/);
  assert.match(main, /composeDimensionTilesFrameBridgeSource\(checkpointSource, tableView\)/);
  assert.match(preload, /setTableView:/);
});
