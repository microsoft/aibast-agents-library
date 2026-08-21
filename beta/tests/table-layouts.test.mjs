import assert from "node:assert/strict";
import {
  mkdtempSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
  MAX_CUSTOM_LAYOUT_BYTES,
  TABLE_LAYOUT_NAMES,
  TABLE_LAYOUTS,
  readCustomLayout,
  resolveCustomLayout,
  validateCustomLayout,
} from "../electron/table-layouts.mjs";

function customFixture() {
  return {
    name: "Moonlit tiles",
    surfaceColor: "#123456",
    seatPositions: [
      { x: 50, y: 8, rotation: 0 },
      { x: 86, y: 50, rotation: 90 },
      { x: 50, y: 92, rotation: 180 },
      { x: 14, y: 50, rotation: -90 },
    ],
    tileSize: { width: 180, height: 260 },
    dealPattern: "clockwise",
    faceDownRule: "folded",
  };
}

test("built-in table layouts all use original layout metadata", () => {
  assert.deepEqual(Object.keys(TABLE_LAYOUTS), [...TABLE_LAYOUT_NAMES]);
  for (const layout of Object.values(TABLE_LAYOUTS)) {
    assert.equal(typeof layout.label, "string");
    assert.equal(typeof layout.layout, "string");
    assert.equal(typeof layout.tileLook, "string");
  }
});

test("custom layout validator bounds local visual primitives", () => {
  assert.deepEqual(validateCustomLayout(customFixture()), customFixture());
  assert.throws(
    () => validateCustomLayout({
      ...customFixture(),
      surfaceColor: "url(https://x)",
    }),
    /six-digit hexadecimal/,
  );
  assert.throws(
    () => validateCustomLayout({
      ...customFixture(),
      seatPositions: [{ x: 101, y: 0 }],
    }),
    /seat 1 x/,
  );
  assert.throws(
    () => validateCustomLayout({
      ...customFixture(),
      logo: "https://example.com/a.png",
    }),
    /unsupported fields: logo/,
  );
  assert.throws(
    () => validateCustomLayout({ ...customFixture(), faceDownRule: "remote" }),
    /faceDownRule/,
  );
});

test("custom layout loader accepts only size-bounded local JSON", (t) => {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-table-layout-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const file = path.join(root, "table.json");
  writeFileSync(file, JSON.stringify(customFixture()), { mode: 0o600 });
  assert.deepEqual(readCustomLayout(file), {
    file,
    layout: customFixture(),
  });
  assert.throws(
    () => readCustomLayout("https://example.com/table.json"),
    /local JSON file/,
  );
  const large = path.join(root, "large.json");
  writeFileSync(large, " ".repeat(MAX_CUSTOM_LAYOUT_BYTES + 1));
  assert.throws(() => readCustomLayout(large), /limited to 65536 bytes/);
});

test("a stale custom layout cannot break disabled mode", () => {
  let reads = 0;
  const disabled = resolveCustomLayout({
    on: false,
    layout: "custom",
    customLayoutPath: "/deleted/table.json",
  }, {
    read() {
      reads += 1;
      throw new Error("should not read");
    },
  });
  assert.deepEqual(disabled, { error: null, layout: null });
  assert.equal(reads, 0);

  const enabled = resolveCustomLayout({
    on: true,
    layout: "custom",
    customLayoutPath: "/deleted/table.json",
  }, {
    read() {
      throw new Error("file is gone");
    },
  });
  assert.equal(enabled.layout, null);
  assert.match(enabled.error, /file is gone/);
});
