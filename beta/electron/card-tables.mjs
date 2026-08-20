export const CARD_TABLE_NAMES = Object.freeze([
  "poker",
  "yugioh",
  "pokemon",
  "mtg",
  "uno",
  "custom",
]);

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
