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

test("herd mode loads no tile script, stylesheet, DOM, or listeners", async (t) => {
  assert.doesNotMatch(shell, /dimension-tiles\.(?:js|css)/);
  assert.match(
    renderer,
    /dimensionTilesRequested = state\.viewMode\?\.mode === "arena"/,
  );
  assert.match(
    renderer,
    /if \(dimensionTilesRequested\) \{[\s\S]*syncDimensionTiles\(state, tilesGeneration\)/,
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
  t.diagnostic("herd-mode renderer: 0 tile DOM, 0 tile listeners, 0 tile CSS");
});

test("every tile move and the Brainstem grab control has a drive handle", () => {
  assert.match(tilesSource, /dataset\.drive = "brainstem\.grab"/);
  assert.match(tilesSource, /herd\.tile\[\$\{id\}\]/);
  for (const move of ["wake", "fold", "race"]) {
    assert.match(tilesSource, new RegExp(`driveTile\\(tile\\.id, "${move}"\\)`));
  }
  assert.match(tilesSource, /arena\.arrange/);
  assert.match(tilesSource, /arena\.layout/);
  assert.match(tilesSource, /arena\.raceTarget/);
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

test("Agent Arena includes all layouts and four arrange moves", () => {
  for (const layout of ["ring", "row", "focus", "grid", "stack", "custom"]) {
    assert.match(tilesSource, new RegExp(`${layout}:`));
  }
  for (const move of ["reorder", "spread", "distribute", "open-one"]) {
    assert.match(tilesSource, new RegExp(`"${move}"`));
  }
  assert.match(
    tilesSource,
    /Agent Arena — parked conversations compete side by side/,
  );
  assert.match(tilesSource, /renderOverflow\(surface, active\.slice\(12\)\)/);
  assert.doesNotMatch(tilesSource, /folded\.slice\(/);
  assert.match(tilesSource, /if \(!SCRIPT_STATE\.enabled\) return null/);
});
