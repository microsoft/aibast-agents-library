import {
  chmodSync,
  existsSync,
  mkdirSync,
  readFileSync,
  renameSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";

export const CHAT_LOOKS = Object.freeze(["messages", "business"]);

export function validChatLook(value) {
  const normalized = String(value || "").toLowerCase();
  return CHAT_LOOKS.includes(normalized) ? normalized : null;
}

function settingsPath(betaHome) {
  if (!betaHome) throw new Error("A beta home is required for chat look settings.");
  return path.join(betaHome, "settings.json");
}

function readSettings(betaHome) {
  const file = settingsPath(betaHome);
  if (!existsSync(file)) return {};
  let value;
  try {
    value = JSON.parse(readFileSync(file, "utf8"));
  } catch (error) {
    throw new Error(`Invalid Frontier settings at ${file}: ${error.message}`);
  }
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`Invalid Frontier settings at ${file}.`);
  }
  return value;
}

function writeSettings(betaHome, value) {
  const file = settingsPath(betaHome);
  mkdirSync(betaHome, { recursive: true, mode: 0o700 });
  try {
    chmodSync(betaHome, 0o700);
  } catch {
    // Windows does not expose POSIX directory modes.
  }
  const temporary = `${file}.${process.pid}.${Date.now()}.tmp`;
  writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, {
    mode: 0o600,
  });
  renameSync(temporary, file);
  try {
    chmodSync(file, 0o600);
  } catch {
    // Windows does not expose POSIX file modes.
  }
  return file;
}

export function resolveChatTypingEnabled(_chatLook, env = process.env) {
  if (env.RAPP_CHAT_TYPING === "1") return true;
  return String(env.RAPP_CHAT_STREAM || "").toLowerCase() === "hold";
}

export function readChatLookSettings({
  betaHome,
  env = process.env,
} = {}) {
  const settings = readSettings(betaHome);
  const storedChatLook = validChatLook(settings.chatLook) || "messages";
  const override = validChatLook(env.RAPP_CHAT_LOOK);
  const chatLook = override || storedChatLook;
  return {
    chatLook,
    chatLookOverridden: Boolean(override),
    chatTypingEnabled: resolveChatTypingEnabled(chatLook, env),
    file: settingsPath(betaHome),
    storedChatLook,
  };
}

export function writeChatLookSettings({
  betaHome,
  chatLook,
} = {}) {
  const normalized = validChatLook(chatLook);
  if (!normalized) {
    throw new Error('Chat look must be either "messages" or "business".');
  }
  const settings = readSettings(betaHome);
  settings.chatLook = normalized;
  const file = writeSettings(betaHome, settings);
  return { chatLook: normalized, file };
}

export function changeChatLook({
  apply,
  betaHome,
  chatLook,
  env = process.env,
} = {}) {
  writeChatLookSettings({ betaHome, chatLook });
  const effective = readChatLookSettings({ betaHome, env });
  apply?.(effective);
  return effective;
}
