import path from "node:path";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";

import {
  app,
  BrowserWindow,
  ipcMain,
  Menu,
  session,
  shell,
} from "electron";

import {
  resolveBrainstemConfig,
} from "./brainstem-process.mjs";
import { BrainSurgeon } from "./brain-surgeon.mjs";
import { CopilotStudioAuthManager } from "./copilot-studio-auth.mjs";
import { CopilotRuntime } from "./copilot-runtime.mjs";
import { BetaRouteManager } from "./route-manager.mjs";
import {
  allowsUiDriverMediaPermission,
  startUiDriverServer,
} from "./ui-driver-server.mjs";
import {
  checkForUpdates,
  consumeUpdateResult,
  prepareUpdate,
} from "./update-manager.mjs";
import {
  betaSourceFingerprint,
  runtimeDirectoryFingerprint,
} from "../scripts/walkthrough-provenance.mjs";

const dirname = path.dirname(fileURLToPath(import.meta.url));
const packageDir = path.resolve(dirname, "..");
const uiFile = path.join(dirname, "..", "ui", "index.html");
const uiUrl = pathToFileURL(uiFile).href;
const config = resolveBrainstemConfig();
const startupFingerprint = betaSourceFingerprint(path.resolve(packageDir, ".."));
const brainstemRuntimeFingerprint = runtimeDirectoryFingerprint(
  config.brainstemDir,
);
const BETA_FRAME_BRIDGE_SOURCE = `(() => {
  if (window.__rappBetaFrameBridge) return true;
  window.__rappBetaFrameBridge = true;
  const style = document.createElement("style");
  style.textContent = [
    ".beta-agent-icon-button{display:grid!important;place-items:center;",
    "width:32px;height:30px;padding:0!important}",
    ".beta-agent-icon-button svg{width:16px;height:16px;pointer-events:none}",
    ".beta-frame-menu{position:relative}",
    ".beta-frame-menu #beta-app-panel{display:none;position:absolute;",
    "top:calc(100% + 10px);right:0;width:min(340px,calc(100vw - 32px));",
    "padding:14px;border:1px solid #30363d;border-radius:10px;",
    "background:#161b22;box-shadow:0 16px 48px rgba(0,0,0,.5);z-index:80}",
    ".beta-frame-menu #beta-app-panel.open{display:block}",
    ".beta-frame-menu #beta-app-panel h3{margin:0 0 5px;font-size:14px}",
    ".beta-frame-menu .beta-app-copy{margin:0 0 12px;color:#8b949e;",
    "font-size:11px;line-height:1.45}",
    ".beta-frame-menu .beta-panel-btn{width:100%;padding:8px 10px;",
    "border:1px solid #30363d;border-radius:6px;background:#21262d;",
    "color:#e6edf3;cursor:pointer;font:inherit;font-size:12px;font-weight:700}",
    ".beta-frame-menu .beta-panel-btn:hover{border-color:#58a6ff;",
    "background:#30363d}",
    ".beta-frame-menu .beta-panel-btn.primary{margin-top:9px;",
    "border-color:#238636;background:#238636}",
    ".beta-frame-menu .beta-panel-btn[hidden]{display:none}",
    ".beta-frame-menu #beta-update-status{margin-top:10px;padding:9px;",
    "border:1px solid #30363d;border-radius:8px;background:#0d1117;",
    "color:#8b949e;font-size:11px;line-height:1.4;white-space:pre-wrap}",
    ".beta-frame-menu #beta-update-status[data-phase=checking],",
    ".beta-frame-menu #beta-update-status[data-phase=applying]",
    "{border-color:#9e6a03;color:#d29922}",
    ".beta-frame-menu #beta-update-status[data-phase=current],",
    ".beta-frame-menu #beta-update-status[data-phase=success]",
    "{border-color:#238636;color:#3fb950}",
    ".beta-frame-menu #beta-update-status[data-phase=available]",
    "{border-color:#1f6feb;color:#58a6ff}",
    ".beta-frame-menu #beta-update-status[data-phase=blocked],",
    ".beta-frame-menu #beta-update-status[data-phase=error]",
    "{border-color:#da3633;color:#ff7b72}",
  ].join("");
  document.head.appendChild(style);
  const downloadIcon = '<svg viewBox="0 0 24 24" fill="none" '
    + 'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    + 'stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/>'
    + '<path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>';
  const trashIcon = '<svg viewBox="0 0 24 24" fill="none" '
    + 'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    + 'stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18"/>'
    + '<path d="M8 6V4h8v2"/><path d="m19 6-1 15H6L5 6"/>'
    + '<path d="M10 11v6M14 11v6"/></svg>';
  function decorateAgentButtons(root = document) {
    root.querySelectorAll(".export-btn").forEach((button) => {
      const deleting = button.classList.contains("del-btn");
      const iconKind = deleting ? "delete" : "download";
      if (button.dataset.betaAgentIcon === iconKind) return;
      button.dataset.betaAgentIcon = iconKind;
      button.classList.add("beta-agent-icon-button");
      button.innerHTML = deleting ? trashIcon : downloadIcon;
      button.title = deleting ? "Delete agent" : "Download agent.py";
      button.setAttribute(
        "aria-label",
        deleting ? "Delete agent" : "Download agent.py",
      );
    });
  }
  decorateAgentButtons();
  const agentList = document.getElementById("agent-list-ul");
  if (agentList) {
    new MutationObserver(() => decorateAgentButtons(agentList)).observe(
      agentList,
      { childList: true, subtree: true },
    );
  }
  function setBetaMenuOpen(open) {
    const panel = document.getElementById("beta-app-panel");
    const button = document.getElementById("beta-app-btn");
    if (!panel || !button) return;
    panel.classList.toggle("open", Boolean(open));
    button.setAttribute("aria-expanded", String(Boolean(open)));
  }
  function renderBetaUpdate(update, openPanel = false) {
    if (!update) return;
    const phase = update.phase || "idle";
    const status = document.getElementById("beta-update-status");
    if (!status) return;
    status.dataset.phase = phase;
    const lines = [
      update.message || "Check GitHub for the latest RAPP Brainstem Beta.",
      update.detail,
      update.source ? "Source: " + update.source : "",
      update.guidance,
    ].filter(Boolean);
    const message = document.getElementById("beta-update-message");
    if (message) {
      message.textContent = lines[0] || "";
      const detail = document.getElementById("beta-update-detail");
      const source = document.getElementById("beta-update-source");
      const guidance = document.getElementById("beta-update-guidance");
      if (detail) detail.textContent = update.detail || "";
      if (source) source.textContent = update.source
        ? "Source: " + update.source
        : "";
      if (guidance) guidance.textContent = update.guidance || "";
    } else {
      status.textContent = lines.join("\\n");
    }
    const busy = phase === "checking" || phase === "applying";
    const checkButton = document.getElementById("beta-check-updates");
    if (checkButton) {
      checkButton.disabled = busy;
      checkButton.textContent = phase === "checking"
        ? "Checking GitHub..."
        : "Check for updates";
    }
    const installButton = document.getElementById("beta-install-update");
    if (installButton) {
      installButton.hidden = phase !== "available";
      installButton.disabled = busy;
    }
    if (openPanel) setBetaMenuOpen(true);
  }
  function installBetaMenu() {
    const brainLogo = document.querySelector("header .logo");
    if (brainLogo) {
      brainLogo.title = "we are above that";
      brainLogo.setAttribute("aria-label", "we are above that");
    }
    let wrapper = document.querySelector(".beta-app-wrapper");
    let button = document.getElementById("beta-app-btn");
    let panel = document.getElementById("beta-app-panel");
    if (!wrapper || !button || !panel) {
      const controls = document.querySelector("header .controls");
      if (!controls) return false;
      wrapper = document.createElement("div");
      wrapper.className = "beta-app-wrapper beta-frame-menu";
      wrapper.innerHTML = '<button class="icon-btn" id="beta-app-btn" '
        + 'type="button" title="RAPP Brainstem Beta menu" aria-haspopup="true" '
        + 'aria-expanded="false"><span class="icon"><svg viewBox="0 0 24 24" '
        + 'fill="currentColor" aria-hidden="true"><path d="M6 10a2 2 0 1 0 0 4 '
        + '2 2 0 0 0 0-4Zm6 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm6 0a2 2 0 1 0 '
        + '0 4 2 2 0 0 0 0-4Z"/></svg></span></button>'
        + '<div id="beta-app-panel"><h3>RAPP Brainstem Beta</h3>'
        + '<p class="beta-app-copy">Chat is the control surface. Agents can add '
        + 'capabilities and visibly operate this workspace while you watch.</p>'
        + '<button class="beta-panel-btn" id="beta-check-updates" type="button">'
        + 'Check for updates</button><div id="beta-update-status" '
        + 'data-phase="idle" role="status" aria-live="polite">Check GitHub for '
        + 'the latest RAPP Brainstem Beta.</div><button class="beta-panel-btn '
        + 'primary" id="beta-install-update" type="button" hidden>'
        + 'Update and Restart</button></div>';
      const vscode = document.getElementById("vscode-link");
      controls.insertBefore(wrapper, vscode || null);
      button = document.getElementById("beta-app-btn");
      panel = document.getElementById("beta-app-panel");
    }
    document.body.classList.add("beta-app");
    button.removeAttribute("onclick");
    const checkButton = document.getElementById("beta-check-updates");
    const installButton = document.getElementById("beta-install-update");
    checkButton?.removeAttribute("onclick");
    installButton?.removeAttribute("onclick");
    if (!button.dataset.betaFrameBridge) {
      button.dataset.betaFrameBridge = "1";
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        setBetaMenuOpen(!panel.classList.contains("open"));
      });
      checkButton?.addEventListener("click", (event) => {
        event.stopPropagation();
        renderBetaUpdate({
          phase: "checking",
          message: "Checking GitHub for updates...",
        }, true);
        window.parent.postMessage({ type: "rapp-beta:check-updates" }, "*");
      });
      installButton?.addEventListener("click", (event) => {
        event.stopPropagation();
        renderBetaUpdate({
          phase: "applying",
          message: "Preparing the update and restart...",
        }, true);
        window.parent.postMessage({ type: "rapp-beta:install-update" }, "*");
      });
      document.addEventListener("click", (event) => {
        if (!event.target.closest(".beta-app-wrapper")) setBetaMenuOpen(false);
      });
    }
    return true;
  }
  installBetaMenu();
  window.addEventListener("message", (event) => {
    if (event.source !== window.parent || !event.data) return;
    if (event.data.type === "rapp-beta:open-update") {
      setBetaMenuOpen(true);
    } else if (event.data.type === "rapp-beta:update-state") {
      renderBetaUpdate(event.data.update, event.data.openPanel);
    }
  });
  async function requestParent(type, filename) {
    const requestId = window.crypto.randomUUID();
    return new Promise((resolve, reject) => {
      const timeout = window.setTimeout(() => {
        window.removeEventListener("message", receive);
        reject(new Error("Beta agent action timed out."));
      }, 30000);
      function receive(message) {
        if (
          message.source !== window.parent
          || message.data?.type !== type + "-result"
          || message.data?.requestId !== requestId
        ) return;
        window.clearTimeout(timeout);
        window.removeEventListener("message", receive);
        resolve(message.data);
      }
      window.addEventListener("message", receive);
      window.parent.postMessage({ type, requestId, filename }, "*");
    });
  }
  document.addEventListener("click", async (event) => {
    const button = event.target.closest?.(".export-btn");
    if (!button) return;
    const deleting = button.classList.contains("del-btn");
    const filename = button.closest("li")
      ?.querySelector(".agent-name")?.getAttribute("title");
    if (!filename) return;
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
    if (
      deleting
      && !window.confirm(\`Are you sure you want to remove \${filename}?\`)
    ) return;
    const original = button.innerHTML;
    button.disabled = true;
    button.textContent = deleting ? "Deleting..." : "Exporting...";
    try {
      const type = deleting
        ? "rapp-beta-delete-agent"
        : "rapp-beta-export-agent";
      const response = await requestParent(type, filename);
      if (!response.ok) throw new Error(response.error || "Agent action failed.");
      if (deleting) {
        await loadAgentsList();
      } else if (!response.result?.canceled) {
        window.alert(\`Exported \${filename} to \${response.result.path}\`);
      }
    } catch (error) {
      window.alert(
        (deleting ? "Delete failed: " : "Export failed: ")
        + String(error?.message || error)
      );
    } finally {
      button.disabled = false;
      button.innerHTML = original;
    }
  }, true);
  return true;
})()`;
const copilot = new CopilotRuntime({
  tokenFile: path.join(config.brainstemDir, ".copilot_token"),
  workingDirectory: config.brainstemDir,
});
const copilotStudioAuth = new CopilotStudioAuthManager();
const betaHome = process.env.BRAINSTEM_BETA_HOME
  || path.join(config.brainstemHome, "beta-launcher");

let mainWindow = null;
let shutdownStarted = false;
let shutdownComplete = false;
let updateCheckInFlight = false;
let updateMenuItem = null;
let availableUpdate = null;
let uiDriver = null;
let brainSurgeon = null;

const state = {
  brainstem: { phase: "starting", message: "Starting shared Brainstem..." },
  copilot: { phase: "starting", message: "Connecting bundled Copilot CLI..." },
  surgeon: {
    phase: "starting",
    message: "Preparing GitHub Copilot Agent mode...",
  },
  uiDriver: { phase: "starting", message: "Preparing visible AI controls..." },
  update: {
    phase: "idle",
    message: "Check GitHub for the latest RAPP Brainstem Beta.",
  },
  url: config.url,
};
const routeManager = new BetaRouteManager({
  betaHome,
  brainstemConfig: config,
  onActivate: async (route) => {
    state.url = route.url;
    state.brainstem = {
      phase: "ready",
      message: `Routed Brainstem v${route.health.version}`,
      callerRappid: route.callerRappid,
      memoryGuid: route.memoryGuid,
      stackRappid: route.stackRappid,
      compositionHash: route.transientCompositionHash || route.compositionHash,
    };
    emitState();
  },
});

function emitState() {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("beta:state", structuredClone(state));
  }
}

function emitSurgeonEvent(event) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("beta:surgeon-event", structuredClone(event));
  }
}

async function executeUiCommand(command) {
  if (!uiDriver?.metadataPath) {
    throw new Error("The visible Brainstem control bridge is not ready.");
  }
  const metadata = JSON.parse(readFileSync(uiDriver.metadataPath, "utf8"));
  const response = await fetch(
    `http://${metadata.host}:${metadata.port}/v1/command`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${metadata.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(command),
    },
  );
  const payload = await response.json();
  if (!response.ok || !payload.ok) {
    throw new Error(payload.error || `Visible UI command failed with HTTP ${response.status}.`);
  }
  return payload.result;
}

function ensureBrainSurgeon() {
  if (!brainSurgeon) {
    brainSurgeon = new BrainSurgeon({
      runtime: copilot,
      brainstemUrl: config.url,
      checkForUpdates: () => handleCheckForUpdates({ openPanel: true }),
      copilotStudioAuth,
      routeManager,
      uiCommand: executeUiCommand,
      onEvent: emitSurgeonEvent,
    });
  }
  return brainSurgeon;
}

function loopbackUrl(raw) {
  try {
    const url = new URL(raw);
    const allowedHost = ["127.0.0.1", "localhost"].includes(url.hostname);
    const active = new URL(state.url);
    return (
      allowedHost
      && url.protocol === active.protocol
      && url.hostname === active.hostname
      && Number(url.port || 80) === Number(active.port || 80)
    );
  } catch {
    return false;
  }
}

function externalUrl(raw) {
  try {
    const url = new URL(raw);
    return ["https:", "vscode:"].includes(url.protocol);
  } catch {
    return false;
  }
}

function routeMainNavigation(event, raw) {
  if (!raw || raw === "about:blank" || raw === uiUrl) return;
  event.preventDefault();
  if (externalUrl(raw)) void shell.openExternal(raw);
}

function routeFrameNavigation(details) {
  const raw = details?.url;
  if (!raw || raw === "about:blank") return;
  if (details.isMainFrame) {
    if (raw !== uiUrl) {
      details.preventDefault();
      if (externalUrl(raw)) void shell.openExternal(raw);
    }
    return;
  }
  if (loopbackUrl(raw)) return;
  details.preventDefault();
  if (externalUrl(raw)) void shell.openExternal(raw);
}

function assertTrustedIpc(event) {
  if (
    !mainWindow
    || event.sender !== mainWindow.webContents
    || event.senderFrame !== mainWindow.webContents.mainFrame
    || event.senderFrame.url !== uiUrl
  ) {
    throw new Error("Rejected IPC from an untrusted frame.");
  }
}

function createWindow() {
  const win = new BrowserWindow({
    show: process.env.BRAINSTEM_BETA_HEADLESS !== "1",
    width: 1280,
    height: 860,
    minWidth: 900,
    minHeight: 620,
    title: "RAPP Brainstem Beta",
    backgroundColor: "#0d1117",
    webPreferences: {
      preload: path.join(dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  win.webContents.setWindowOpenHandler(({ url }) => {
    if (externalUrl(url)) void shell.openExternal(url);
    return { action: "deny" };
  });
  win.webContents.on("will-navigate", routeMainNavigation);
  win.webContents.on("will-frame-navigate", routeFrameNavigation);
  win.on("closed", () => {
    mainWindow = null;
  });
  void win.loadFile(uiFile);
  return win;
}

function shortCommit(commit) {
  return commit.slice(0, 8);
}

function openUpdatePanel() {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("beta:open-update");
  }
}

function setUpdateState(update) {
  state.update = update;
  emitState();
  return structuredClone(update);
}

async function handleCheckForUpdates({ openPanel = false } = {}) {
  if (openPanel) openUpdatePanel();
  if (updateCheckInFlight) return structuredClone(state.update);
  updateCheckInFlight = true;
  if (updateMenuItem) updateMenuItem.enabled = false;
  availableUpdate = null;
  setUpdateState({
    phase: "checking",
    message: "Checking GitHub for updates...",
  });

  try {
    const update = await checkForUpdates({
      packageDir,
      env: process.env,
    });
    if (!update.published) {
      return setUpdateState({
        phase: "current",
        message: `No RAPP Brainstem Beta update is published on ${update.updateRef} yet.`,
        detail: `This source build remains on ${update.currentVersion} `
          + `(${shortCommit(update.currentCommit)}). The latest repository commit `
          + `(${shortCommit(update.latestCommit)}) has no beta/VERSION manifest.`,
        source: `${update.repository}@${update.updateRef}`,
      });
    }
    if (!update.available) {
      return setUpdateState({
        phase: "current",
        message: "RAPP Brainstem Beta is up to date.",
        detail: `Version ${update.currentVersion} (${shortCommit(update.currentCommit)})`,
        source: `${update.repository}@${update.updateRef}`,
      });
    }

    if (update.dirty) {
      return setUpdateState({
        phase: "blocked",
        message: "An update is available, but local launcher changes block it.",
        detail: `Installed ${update.currentVersion} (${shortCommit(update.currentCommit)}); `
          + `available ${update.latestVersion} (${shortCommit(update.latestCommit)}).`,
        source: `${update.repository}@${update.updateRef}`,
        guidance: `Preserve or discard the changes in ${update.repoRoot}, then check again.`,
      });
    }

    availableUpdate = update;
    return setUpdateState({
      phase: "available",
      message: `RAPP Brainstem Beta ${update.latestVersion} is available.`,
      detail: `Installed ${update.currentVersion} (${shortCommit(update.currentCommit)}); `
        + `latest ${update.latestVersion} (${shortCommit(update.latestCommit)}).`,
      source: `${update.repository}@${update.updateRef}`,
      guidance: "Update and Restart refreshes the launcher and shared Brainstem "
        + "from this exact GitHub commit.",
    });
  } catch (error) {
    return setUpdateState({
      phase: "error",
      message: "RAPP Brainstem Beta could not check for updates.",
      detail: String(error.message || error),
    });
  } finally {
    updateCheckInFlight = false;
    if (updateMenuItem && !shutdownStarted) updateMenuItem.enabled = true;
  }
}

async function handleInstallUpdate() {
  if (!availableUpdate) {
    return setUpdateState({
      phase: "error",
      message: "No ready update is available.",
      detail: "Check for updates again before installing.",
    });
  }
  const update = availableUpdate;
  setUpdateState({
    phase: "applying",
    message: `Installing RAPP Brainstem Beta ${update.latestVersion}...`,
    detail: "The app will close, run the pinned installer, and reopen.",
  });
  try {
    await prepareUpdate({
      update,
      brainstemHome: config.brainstemHome,
      env: process.env,
    });
    app.quit();
    return structuredClone(state.update);
  } catch (error) {
    return setUpdateState({
      phase: "error",
      message: "RAPP Brainstem Beta could not start the update.",
      detail: String(error.message || error),
    });
  }
}

function installApplicationMenu() {
  const checkForUpdatesItem = {
    id: "check-for-updates",
    label: "Check for Updates...",
    accelerator: "CmdOrCtrl+Shift+U",
    click: () => void handleCheckForUpdates({ openPanel: true }),
  };
  const editMenu = {
    label: "Edit",
    submenu: [
      { role: "undo" },
      { role: "redo" },
      { type: "separator" },
      { role: "cut" },
      { role: "copy" },
      { role: "paste" },
      { role: "selectAll" },
    ],
  };
  const viewMenu = {
    label: "View",
    submenu: [
      { role: "reload" },
      { role: "forceReload" },
      { role: "toggleDevTools" },
      { type: "separator" },
      { role: "resetZoom" },
      { role: "zoomIn" },
      { role: "zoomOut" },
      { type: "separator" },
      { role: "togglefullscreen" },
    ],
  };
  const template = process.platform === "darwin"
    ? [
        {
          label: app.name,
          submenu: [
            { role: "about" },
            { type: "separator" },
            checkForUpdatesItem,
            { type: "separator" },
            { role: "services" },
            { type: "separator" },
            { role: "hide" },
            { role: "hideOthers" },
            { role: "unhide" },
            { type: "separator" },
            { role: "quit" },
          ],
        },
        editMenu,
        viewMenu,
        { role: "windowMenu" },
      ]
    : [
        { label: "File", submenu: [{ role: "quit" }] },
        editMenu,
        viewMenu,
        { role: "windowMenu" },
        { label: "Help", submenu: [checkForUpdatesItem] },
      ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
  updateMenuItem = Menu.getApplicationMenu()?.getMenuItemById(
    "check-for-updates",
  );
}

function loadPendingUpdateResult() {
  let result;
  try {
    result = consumeUpdateResult({ packageDir, env: process.env });
  } catch (error) {
    result = {
      success: false,
      error: `The update result could not be read: ${String(error.message || error)}`,
    };
  }
  if (!result) return;

  if (result.success) {
    state.update = {
      phase: "success",
      message: `RAPP Brainstem Beta updated to ${result.latestVersion}.`,
      detail: `Installed commit: ${shortCommit(result.commit)}\n`
        + "The launcher and shared Brainstem source were refreshed.",
    };
    return;
  }

  state.update = {
    phase: "error",
    message: "RAPP Brainstem Beta could not finish the update.",
    detail: `${result.error || "Unknown updater error."}\n\nLog: ${
      result.logPath || "unavailable"
    }`,
  };
}

function registerIpc() {
  ipcMain.handle("beta:get-state", (event) => {
    assertTrustedIpc(event);
    return structuredClone(state);
  });
  ipcMain.handle("beta:list-agent-files", async (event) => {
    assertTrustedIpc(event);
    const identity = routeManager.identity();
    const route = routeManager.activeRoute;
    return {
      caller_rappid: identity.caller_rappid,
      memory_guid: identity.memory_guid,
      active_stack_rappid: route?.stackRappid || identity.active_stack_rappid,
      overlay_stack_rappids: route?.overlayStackRappids
        || identity.overlay_stack_rappids,
      stack_lineage: route?.stackLineage || [],
      stack_tree: routeManager.stackTree(),
      composition_hash: route?.transientCompositionHash
        || route?.compositionHash
        || null,
      files: routeManager.activeAgentFiles().map((agent) => ({
        filename: agent.filename,
        agents: [],
        loadable: true,
        revision: agent.address || agent.filename,
        scope: agent.scope,
      })),
    };
  });
  ipcMain.handle("beta:read-agent-file", async (
    event,
    filename,
    scope,
  ) => {
    assertTrustedIpc(event);
    const safeName = String(filename || "");
    if (
      !/^[A-Za-z0-9_.-]+\.py$/.test(safeName)
      || safeName.startsWith(".")
    ) {
      throw new Error("A safe Python agent filename is required.");
    }
    return {
      filename: safeName,
      scope: String(scope || "global"),
      content: routeManager.readActiveAgent(safeName),
    };
  });
  ipcMain.handle("beta:delete-agent", async (event, filename) => {
    assertTrustedIpc(event);
    const removed = await routeManager.removeActiveAgent({ filename });
    const route = await routeManager.startDefault();
    return { ...removed, active_route: route };
  });
  ipcMain.handle("beta:export-agent", async (event, filename) => {
    assertTrustedIpc(event);
    const safeName = path.basename(String(filename || ""));
    const source = routeManager.readActiveAgent(safeName);
    const downloads = app.getPath("downloads");
    const extension = path.extname(safeName);
    const stem = path.basename(safeName, extension);
    let filePath = path.join(downloads, safeName);
    let suffix = 1;
    while (existsSync(filePath)) {
      filePath = path.join(downloads, `${stem} (${suffix})${extension}`);
      suffix += 1;
    }
    writeFileSync(filePath, source, { mode: 0o600 });
    return {
      canceled: false,
      filename: safeName,
      path: filePath,
    };
  });
  ipcMain.handle("beta:install-frame-bridge", async (event) => {
    assertTrustedIpc(event);
    const frame = mainWindow?.webContents.mainFrame.framesInSubtree.find(
      (candidate) => loopbackUrl(candidate.url),
    );
    if (!frame) return { installed: false };
    await frame.executeJavaScript(BETA_FRAME_BRIDGE_SOURCE, true);
    return { installed: true };
  });
  ipcMain.handle(
    "beta:check-for-updates",
    (event) => {
      assertTrustedIpc(event);
      return handleCheckForUpdates();
    },
  );
  ipcMain.handle(
    "beta:install-update",
    (event) => {
      assertTrustedIpc(event);
      return handleInstallUpdate();
    },
  );
  ipcMain.handle("beta:surgeon-send", async (event, prompt) => {
    assertTrustedIpc(event);
    return ensureBrainSurgeon().send(prompt);
  });
  ipcMain.handle("beta:surgeon-reset", async (event) => {
    assertTrustedIpc(event);
    if (brainSurgeon) await brainSurgeon.reset();
    return { ok: true };
  });
}

async function startServices() {
  const brainstemTask = routeManager.startDefault().then((route) => {
    state.url = route.url;
    emitState();
  }).catch((error) => {
    state.brainstem = { phase: "error", message: String(error.message || error) };
    emitState();
  });

  const copilotTask = copilot.start().then((result) => {
    state.copilot = result.authenticated
      ? {
          phase: "ready",
          message: result.login
            ? `Copilot CLI signed in as ${result.login}`
            : "Copilot CLI signed in",
        }
      : {
          phase: "signed-out",
          message: "Copilot CLI is bundled; sign in through Brainstem chat.",
        };
    state.surgeon = result.authenticated
      ? {
          phase: "ready",
          message: "GitHub Copilot Agent mode is ready inside the beta client.",
        }
      : {
          phase: "signed-out",
          message: "Sign in to GitHub Copilot before using Brain Surgeon.",
        };
    emitState();
  }).catch((error) => {
    state.copilot = {
      phase: "warning",
      message: `Copilot CLI status unavailable: ${String(error.message || error)}`,
    };
    state.surgeon = {
      phase: "error",
      message: state.copilot.message,
    };
    emitState();
  });

  await Promise.allSettled([brainstemTask, copilotTask]);
}

const hasLock = app.requestSingleInstanceLock();
if (!hasLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (!mainWindow || mainWindow.isDestroyed()) mainWindow = createWindow();
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.show();
    mainWindow.focus();
  });

  app.whenReady().then(() => {
    session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
      callback(allowsUiDriverMediaPermission(webContents, permission));
    });
    registerIpc();
    installApplicationMenu();
    loadPendingUpdateResult();
    mainWindow = createWindow();
    startUiDriverServer({
      window: mainWindow,
      brainstemHome: config.brainstemHome,
      loopbackUrl,
      env: process.env,
      routeTelemetry: () => routeManager.telemetrySnapshot(),
      brainstemRuntimeFingerprint,
      runtimeFingerprint: startupFingerprint,
    }).then((driver) => {
      uiDriver = driver;
      state.uiDriver = {
        phase: "ready",
        message: "Chat agents can visibly operate this Brainstem.",
      };
      emitState();
    }).catch((error) => {
      state.uiDriver = {
        phase: "error",
        message: `Visible AI controls unavailable: ${String(error.message || error)}`,
      };
      console.error(state.uiDriver.message);
      emitState();
    });
    void startServices();
    const smokeExitMs = Number.parseInt(
      process.env.BRAINSTEM_BETA_SMOKE_EXIT_MS || "0",
      10,
    );
    if (Number.isInteger(smokeExitMs) && smokeExitMs > 0) {
      setTimeout(() => app.quit(), smokeExitMs);
    }
  });

  app.on("activate", () => {
    if (!mainWindow || mainWindow.isDestroyed()) mainWindow = createWindow();
    mainWindow.show();
  });

  app.on("window-all-closed", () => {
    if (process.platform !== "darwin") app.quit();
  });

  app.on("before-quit", (event) => {
    if (shutdownComplete) return;
    event.preventDefault();
    if (shutdownStarted) return;
    shutdownStarted = true;
    Promise.allSettled([
      brainSurgeon?.stop(),
      copilot.stop(),
      routeManager.stop(),
      uiDriver?.stop(),
    ]).finally(() => {
      shutdownComplete = true;
      app.quit();
    });
  });
}
