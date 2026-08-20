import {
  chmodSync,
  existsSync,
  mkdirSync,
  readFileSync,
  renameSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";

import {
  DEFAULT_APRIL_FOOLS,
  normalizeAprilFoolsSettings,
} from "./card-tables.mjs";

function settingsPath(betaHome) {
  if (!betaHome) throw new Error("A beta home is required for chat card settings.");
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

function environmentOverride(env) {
  if (env.RAPP_APRIL_FOOLS === "1") return true;
  if (env.RAPP_APRIL_FOOLS === "0") return false;
  return null;
}

export function readAprilFoolsSettings({
  betaHome,
  env = process.env,
} = {}) {
  const settings = readSettings(betaHome);
  const storedAprilFools = normalizeAprilFoolsSettings(
    settings.aprilFools || DEFAULT_APRIL_FOOLS,
  );
  const override = environmentOverride(env);
  const aprilFools = {
    ...storedAprilFools,
    on: override === null ? storedAprilFools.on : override,
  };
  return {
    aprilFools,
    aprilFoolsOverridden: override !== null,
    file: settingsPath(betaHome),
    storedAprilFools,
  };
}

export function writeAprilFoolsSettings({
  aprilFools,
  betaHome,
} = {}) {
  const settings = readSettings(betaHome);
  settings.aprilFools = normalizeAprilFoolsSettings({
    ...DEFAULT_APRIL_FOOLS,
    ...(settings.aprilFools || {}),
    ...(aprilFools || {}),
  });
  const file = writeSettings(betaHome, settings);
  return { aprilFools: settings.aprilFools, file };
}

export function changeAprilFoolsSettings({
  apply,
  aprilFools,
  betaHome,
  env = process.env,
} = {}) {
  writeAprilFoolsSettings({ aprilFools, betaHome });
  const effective = readAprilFoolsSettings({ betaHome, env });
  apply?.(effective);
  return effective;
}

export function parseAprilFoolsCommand(message) {
  return typeof message === "string" && message.trim() === "april fools"
    ? { action: "toggle-april-fools", original: message }
    : null;
}

function installAprilFoolsFrameToggle(settings) {
  const prior = window.__rappBetaAprilFoolsBridge;
  if (prior) {
    prior.update(settings);
    return true;
  }

  let current = settings;
  function removeToggle() {
    document.getElementById("beta-april-fools-toggle")?.remove();
  }
  function renderToggle() {
    const panel = document.getElementById("beta-app-panel");
    if (!panel) return false;
    let button = document.getElementById("beta-april-fools-toggle");
    if (!button) {
      button = document.createElement("button");
      button.id = "beta-april-fools-toggle";
      button.className = "beta-panel-btn";
      button.type = "button";
      button.textContent = "April Fools: Card Table";
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        window.parent.postMessage({
          type: "rapp-beta:set-april-fools",
          aprilFools: { on: !current.on },
        }, "*");
      });
      const updateButton = document.getElementById("beta-check-updates");
      panel.insertBefore(button, updateButton || null);
    }
    button.setAttribute("aria-pressed", String(Boolean(current.on)));
    button.textContent = `April Fools: Card Table ${current.on ? "✓" : ""}`.trim();
    return true;
  }
  function receive(event) {
    if (
      event.source === window.parent
      && event.data?.type === "rapp-beta:april-fools-state"
    ) {
      current = event.data.aprilFools || current;
      if (!current.on) {
        removeToggle();
        window.removeEventListener("message", receive);
        delete window.__rappBetaAprilFoolsBridge;
      } else {
        renderToggle();
      }
    }
  }
  const bridge = {
    update(next) {
      current = next;
      renderToggle();
    },
  };
  window.__rappBetaAprilFoolsBridge = bridge;
  window.addEventListener("message", receive);
  renderToggle();
  return true;
}

export function composeChatCardsFrameBridgeSource(checkpointSource, aprilFools) {
  const source = String(checkpointSource || "");
  if (!aprilFools?.on) return source;
  return `${source}\n;(${installAprilFoolsFrameToggle.toString()})(${
    JSON.stringify(normalizeAprilFoolsSettings(aprilFools))
  });`;
}
