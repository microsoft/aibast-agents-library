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
  CARD_TABLE_NAMES,
  CARD_TABLE_THEMES,
  MAX_CUSTOM_TABLE_BYTES,
  readCustomTable,
  validateCustomTable,
} from "../electron/card-tables.mjs";

function customFixture() {
  return {
    name: "Moonlit tiles",
    feltColor: "#123456",
    seatPositions: [
      { x: 50, y: 8, rotation: 0 },
      { x: 86, y: 50, rotation: 90 },
      { x: 50, y: 92, rotation: 180 },
      { x: 14, y: 50, rotation: -90 },
    ],
    cardSize: { width: 180, height: 260 },
    dealPattern: "clockwise",
    faceDownRule: "folded",
  };
}

test("built-in card tables all use original layout metadata", () => {
  assert.deepEqual(Object.keys(CARD_TABLE_THEMES), [...CARD_TABLE_NAMES]);
  for (const theme of Object.values(CARD_TABLE_THEMES)) {
    assert.equal(typeof theme.label, "string");
    assert.equal(typeof theme.layout, "string");
    assert.equal(typeof theme.cardLook, "string");
  }
});

test("custom table validator bounds local visual primitives", () => {
  assert.deepEqual(validateCustomTable(customFixture()), customFixture());
  assert.throws(
    () => validateCustomTable({ ...customFixture(), feltColor: "url(https://x)" }),
    /six-digit hexadecimal/,
  );
  assert.throws(
    () => validateCustomTable({
      ...customFixture(),
      seatPositions: [{ x: 101, y: 0 }],
    }),
    /seat 1 x/,
  );
  assert.throws(
    () => validateCustomTable({ ...customFixture(), logo: "https://example.com/a.png" }),
    /unsupported fields: logo/,
  );
  assert.throws(
    () => validateCustomTable({ ...customFixture(), faceDownRule: "remote" }),
    /faceDownRule/,
  );
});

test("custom table loader accepts only size-bounded local JSON", (t) => {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-card-table-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const file = path.join(root, "table.json");
  writeFileSync(file, JSON.stringify(customFixture()), { mode: 0o600 });
  assert.deepEqual(readCustomTable(file), {
    file,
    table: customFixture(),
  });
  assert.throws(
    () => readCustomTable("https://example.com/table.json"),
    /local JSON file/,
  );
  const large = path.join(root, "large.json");
  writeFileSync(large, " ".repeat(MAX_CUSTOM_TABLE_BYTES + 1));
  assert.throws(() => readCustomTable(large), /limited to 65536 bytes/);
});
