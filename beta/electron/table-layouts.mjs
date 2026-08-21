import {
  readFileSync,
  statSync,
} from "node:fs";
import path from "node:path";

export const TABLE_LAYOUT_NAMES = Object.freeze([
  "table",
  "duel",
  "bench",
  "battlefield",
  "hand",
  "custom",
]);

export const MAX_CUSTOM_LAYOUT_BYTES = 64 * 1024;
export const TABLE_LAYOUTS = Object.freeze({
  table: Object.freeze({
    label: "Table",
    layout: "oval seats",
    tileLook: "plain frame",
  }),
  duel: Object.freeze({
    label: "Duel zones",
    layout: "five zones and a discard row",
    tileLook: "tall bronze frame",
  }),
  bench: Object.freeze({
    label: "Bench",
    layout: "one active seat over a bench of five",
    tileLook: "rounded pip frame",
  }),
  battlefield: Object.freeze({
    label: "Battlefield",
    layout: "two battlefield rows",
    tileLook: "title banner and art window",
  }),
  hand: Object.freeze({
    label: "Hand",
    layout: "draw pile, discard pile, and fan",
    tileLook: "bold model color and turn number",
  }),
  custom: Object.freeze({
    label: "Custom…",
    layout: "validated local JSON",
    tileLook: "validated local JSON",
  }),
});

export const DEFAULT_TABLE_VIEW = Object.freeze({
  on: false,
  layout: "table",
  customLayoutPath: null,
});

export function validTableLayout(value) {
  const normalized = String(value || "").toLowerCase();
  return TABLE_LAYOUT_NAMES.includes(normalized) ? normalized : null;
}

export function normalizeTableViewSettings(value = {}) {
  const input = value && typeof value === "object" && !Array.isArray(value)
    ? value
    : {};
  return {
    on: input.on === true,
    layout: validTableLayout(input.layout) || DEFAULT_TABLE_VIEW.layout,
    customLayoutPath: typeof input.customLayoutPath === "string"
      && input.customLayoutPath.trim()
      ? input.customLayoutPath
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

export function validateCustomLayout(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("A custom table layout must be a JSON object.");
  }
  const allowed = new Set([
    "name",
    "surfaceColor",
    "seatPositions",
    "tileSize",
    "dealPattern",
    "faceDownRule",
  ]);
  const unexpected = Object.keys(value).filter((key) => !allowed.has(key));
  if (unexpected.length) {
    throw new Error(
      `Custom table layout contains unsupported fields: ${unexpected.join(", ")}.`,
    );
  }
  if (!/^#[0-9a-f]{6}$/i.test(String(value.surfaceColor || ""))) {
    throw new Error("Custom surfaceColor must be a six-digit hexadecimal color.");
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
    !value.tileSize
    || typeof value.tileSize !== "object"
    || Array.isArray(value.tileSize)
  ) {
    throw new Error("Custom tileSize must be an object.");
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
    surfaceColor: value.surfaceColor.toLowerCase(),
    seatPositions,
    tileSize: {
      width: finiteNumber(value.tileSize.width, "Custom tile width", 120, 320),
      height: finiteNumber(value.tileSize.height, "Custom tile height", 160, 440),
    },
    dealPattern: value.dealPattern,
    faceDownRule: value.faceDownRule,
  };
}

export function readCustomLayout(filePath) {
  const requested = String(filePath || "");
  if (!requested || /^[a-z][a-z0-9+.-]*:\/\//i.test(requested)) {
    throw new Error("A custom table layout must be a local JSON file.");
  }
  const absolute = path.resolve(requested);
  const size = statSync(absolute).size;
  if (size > MAX_CUSTOM_LAYOUT_BYTES) {
    throw new Error(
      `Custom table layouts are limited to ${MAX_CUSTOM_LAYOUT_BYTES} bytes.`,
    );
  }
  let value;
  try {
    value = JSON.parse(readFileSync(absolute, "utf8"));
  } catch (error) {
    throw new Error(`Invalid custom table layout at ${absolute}: ${error.message}`);
  }
  return {
    file: absolute,
    layout: validateCustomLayout(value),
  };
}

export function resolveCustomLayout(settings, {
  read = readCustomLayout,
} = {}) {
  if (
    !settings?.on
    || settings.layout !== "custom"
    || !settings.customLayoutPath
  ) {
    return { error: null, layout: null };
  }
  try {
    return {
      error: null,
      layout: read(settings.customLayoutPath).layout,
    };
  } catch (error) {
    return {
      error: `Could not load custom table layout: ${String(
        error?.message || error,
      )}`,
      layout: null,
    };
  }
}
