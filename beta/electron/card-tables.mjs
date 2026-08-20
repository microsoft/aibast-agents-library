import {
  readFileSync,
  statSync,
} from "node:fs";
import path from "node:path";

export const CARD_TABLE_NAMES = Object.freeze([
  "poker",
  "yugioh",
  "pokemon",
  "mtg",
  "uno",
  "custom",
]);

export const MAX_CUSTOM_TABLE_BYTES = 64 * 1024;
export const CARD_TABLE_THEMES = Object.freeze({
  poker: Object.freeze({
    label: "Poker",
    layout: "oval seats",
    cardLook: "plain frame",
  }),
  yugioh: Object.freeze({
    label: "Duel zones",
    layout: "five zones and a discard row",
    cardLook: "tall bronze frame",
  }),
  pokemon: Object.freeze({
    label: "Active bench",
    layout: "one active seat over a bench of five",
    cardLook: "rounded pip frame",
  }),
  mtg: Object.freeze({
    label: "Battlefield",
    layout: "two battlefield rows",
    cardLook: "title banner and art window",
  }),
  uno: Object.freeze({
    label: "Color hand",
    layout: "draw pile, discard pile, and fan",
    cardLook: "bold model color and turn number",
  }),
  custom: Object.freeze({
    label: "Custom local table",
    layout: "validated local JSON",
    cardLook: "validated local JSON",
  }),
});

export const DEFAULT_APRIL_FOOLS = Object.freeze({
  on: false,
  table: "poker",
  customTablePath: null,
});

export function validCardTable(value) {
  const normalized = String(value || "").toLowerCase();
  return CARD_TABLE_NAMES.includes(normalized) ? normalized : null;
}

export function normalizeAprilFoolsSettings(value = {}) {
  const input = value && typeof value === "object" && !Array.isArray(value)
    ? value
    : {};
  return {
    on: input.on === true,
    table: validCardTable(input.table) || DEFAULT_APRIL_FOOLS.table,
    customTablePath: typeof input.customTablePath === "string"
      && input.customTablePath.trim()
      ? input.customTablePath
      : null,
  };
}

function finiteNumber(value, label, minimum, maximum) {
  const number = Number(value);
  if (!Number.isFinite(number) || number < minimum || number > maximum) {
    throw new Error(
      `${label} must be a number from ${minimum} through ${maximum}.`,
    );
  }
  return number;
}

export function validateCustomTable(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("A custom card table must be a JSON object.");
  }
  const allowed = new Set([
    "name",
    "feltColor",
    "seatPositions",
    "cardSize",
    "dealPattern",
    "faceDownRule",
  ]);
  const unexpected = Object.keys(value).filter((key) => !allowed.has(key));
  if (unexpected.length) {
    throw new Error(
      `Custom card table contains unsupported fields: ${unexpected.join(", ")}.`,
    );
  }
  if (!/^#[0-9a-f]{6}$/i.test(String(value.feltColor || ""))) {
    throw new Error("Custom feltColor must be a six-digit hexadecimal color.");
  }
  if (
    !Array.isArray(value.seatPositions)
    || value.seatPositions.length < 1
    || value.seatPositions.length > 12
  ) {
    throw new Error("Custom seatPositions must contain 1 through 12 seats.");
  }
  const seatPositions = value.seatPositions.map((seat, index) => {
    if (!seat || typeof seat !== "object" || Array.isArray(seat)) {
      throw new Error(`Custom seat ${index + 1} must be an object.`);
    }
    return {
      x: finiteNumber(seat.x, `Custom seat ${index + 1} x`, 0, 100),
      y: finiteNumber(seat.y, `Custom seat ${index + 1} y`, 0, 100),
      rotation: finiteNumber(
        seat.rotation ?? 0,
        `Custom seat ${index + 1} rotation`,
        -180,
        180,
      ),
    };
  });
  if (
    !value.cardSize
    || typeof value.cardSize !== "object"
    || Array.isArray(value.cardSize)
  ) {
    throw new Error("Custom cardSize must be an object.");
  }
  const dealPatterns = new Set([
    "clockwise",
    "counterclockwise",
    "fan",
    "rows",
    "stack",
  ]);
  if (!dealPatterns.has(value.dealPattern)) {
    throw new Error(
      "Custom dealPattern must be clockwise, counterclockwise, fan, rows, or stack.",
    );
  }
  const faceDownRules = new Set(["never", "folded", "all", "alternate"]);
  if (!faceDownRules.has(value.faceDownRule)) {
    throw new Error(
      "Custom faceDownRule must be never, folded, all, or alternate.",
    );
  }
  const name = String(value.name || "Custom table").trim();
  if (!name || [...name].length > 60) {
    throw new Error("Custom table name must contain at most 60 characters.");
  }
  return {
    name,
    feltColor: value.feltColor.toLowerCase(),
    seatPositions,
    cardSize: {
      width: finiteNumber(value.cardSize.width, "Custom card width", 120, 320),
      height: finiteNumber(value.cardSize.height, "Custom card height", 160, 440),
    },
    dealPattern: value.dealPattern,
    faceDownRule: value.faceDownRule,
  };
}

export function readCustomTable(filePath) {
  const requested = String(filePath || "");
  if (!requested || /^[a-z][a-z0-9+.-]*:\/\//i.test(requested)) {
    throw new Error("A custom card table must be a local JSON file.");
  }
  const absolute = path.resolve(requested);
  const size = statSync(absolute).size;
  if (size > MAX_CUSTOM_TABLE_BYTES) {
    throw new Error(
      `Custom card tables are limited to ${MAX_CUSTOM_TABLE_BYTES} bytes.`,
    );
  }
  let value;
  try {
    value = JSON.parse(readFileSync(absolute, "utf8"));
  } catch (error) {
    throw new Error(`Invalid custom card table at ${absolute}: ${error.message}`);
  }
  return {
    file: absolute,
    table: validateCustomTable(value),
  };
}
