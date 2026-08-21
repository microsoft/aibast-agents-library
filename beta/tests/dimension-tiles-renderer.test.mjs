import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const renderer = readFileSync(
  new URL("../ui/renderer.js", import.meta.url),
  "utf8",
);
const tilesSource = readFileSync(
  new URL("../ui/dimension-tiles.js", import.meta.url),
  "utf8",
);
const tilesCss = readFileSync(
  new URL("../ui/dimension-tiles.css", import.meta.url),
  "utf8",
);
const shell = readFileSync(
  new URL("../ui/index.html", import.meta.url),
  "utf8",
);

test("mode off loads no tile script, stylesheet, DOM, or listeners", async (t) => {
  assert.doesNotMatch(shell, /dimension-tiles\.(?:js|css)/);
  assert.match(
    renderer,
    /if \(state\.tableView\?\.on\) \{[\s\S]*syncDimensionTiles\(state, tilesGeneration\)/,
  );
  assert.match(
    renderer,
    /else if \([\s\S]*tilesWereRequested[\s\S]*dimensionTilesLoader[\s\S]*window\.RappDimensionTiles/,
  );
  assert.match(tilesSource, /__rappDimensionTilesScript/);
  assert.match(renderer, /generation !== dimensionTilesGeneration/);

  delete globalThis.RappDimensionTiles;
  await import(`../ui/dimension-tiles.js?mode-off=${Date.now()}`);
  assert.equal(globalThis.RappDimensionTiles.enabled(), false);
  globalThis.RappDimensionTiles.disable();
  assert.equal(globalThis.RappDimensionTiles.enabled(), false);
  t.diagnostic("mode-off renderer: 0 tile DOM, 0 tile listeners, 0 tile CSS");
});

test("every tile move and the Brainstem grab control has a drive handle", () => {
  assert.match(tilesSource, /dataset\.drive = "brainstem\.grab"/);
  assert.match(tilesSource, /herd\.tile\[\$\{id\}\]/);
  for (const move of ["wake", "fold", "race"]) {
    assert.match(tilesSource, new RegExp(`driveTile\\(tile\\.id, "${move}"\\)`));
  }
  assert.match(tilesSource, /tableView\.arrange/);
  assert.match(tilesSource, /tableView\.layout/);
  assert.match(tilesSource, /tableView\.raceTarget/);
  assert.match(tilesSource, /\.api\.twinChat/);
});

test("tiles support drag, threshold swipes, buttons, and keyboard paths", () => {
  assert.match(tilesSource, /application\/x-rapp-brainstem-chat/);
  assert.match(tilesSource, /application\/x-rapp-dimension-tile/);
  assert.match(tilesSource, /movement >= 72/);
  assert.match(tilesSource, /movement <= -72/);
  assert.match(tilesSource, /pointermove/);
  assert.match(tilesCss, /touch-action:\s*pan-y/);
  assert.match(tilesSource, /event\.key === "ArrowRight"/);
  assert.match(tilesSource, /event\.key === "ArrowLeft"/);
  assert.match(tilesSource, /event\.key\.toLowerCase\(\) === "r"/);
});

test("table UI includes all layouts and four arrange moves", () => {
  for (const layout of ["table", "row", "focus", "grid", "stack", "custom"]) {
    assert.match(tilesSource, new RegExp(`${layout}:`));
  }
  for (const deal of ["reorder", "fan", "distribute", "open-one"]) {
    assert.match(tilesSource, new RegExp(`"${deal}"`));
  }
  assert.match(tilesSource, /renderOverflow\(surface, active\.slice\(12\)\)/);
  assert.doesNotMatch(tilesSource, /folded\.slice\(/);
  assert.match(tilesSource, /if \(!SCRIPT_STATE\.enabled\) return null/);
});
