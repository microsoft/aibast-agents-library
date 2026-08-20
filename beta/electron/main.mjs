import path from "node:path";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";

import {
  app,
  BrowserWindow,
  ipcMain,
  Menu,
  nativeImage,
  net,
  Notification,
  session,
  shell,
} from "electron";

import {
  resolveBrainstemConfig,
} from "./brainstem-process.mjs";
import { humanizeAgentName } from "./agent-display.mjs";
import { BrainSurgeon } from "./brain-surgeon.mjs";
import { CopilotStudioAuthManager } from "./copilot-studio-auth.mjs";
import { CopilotRuntime } from "./copilot-runtime.mjs";
import { executeLineageCommand } from "./lineage-control.mjs";
import {
  createExportRedactionScript,
  redactSensitiveValue,
} from "./log-redaction.mjs";
import { BetaRouteManager } from "./route-manager.mjs";
import { isAllowedStoreSourceUrl, RappStoreClient, STORE_SOURCES } from "./rapp-store.mjs";
import { TwinManager } from "./twin-manager.mjs";
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
// The blue-brain app icon (build/icon.png), used for the window, the dock, and
// the taskbar so the running app never shows the default Electron icon. Packaged
// builds pick up build/icon.icns / .ico / icons/ via package.json.
const appIconFile = path.join(packageDir, "build", "icon.png");
const appIcon = existsSync(appIconFile) ? nativeImage.createFromPath(appIconFile) : null;
const uiFile = path.join(dirname, "..", "ui", "index.html");
const uiUrl = pathToFileURL(uiFile).href;
const config = resolveBrainstemConfig();
const startupFingerprint = betaSourceFingerprint(path.resolve(packageDir, ".."));
const brainstemRuntimeFingerprint = runtimeDirectoryFingerprint(
  config.brainstemDir,
);
const exportRedactionSource = createExportRedactionScript({
  roots: [
    config.brainstemDir,
    config.brainstemHome,
    homedir(),
    tmpdir(),
  ],
});
const BETA_FRAME_BRIDGE_SOURCE = `(() => {
  if (window.__rappBetaFrameBridge) return true;
  window.__rappBetaFrameBridge = true;
  ${exportRedactionSource}
  const humanizeAgentName = ${humanizeAgentName.toString()};
  const style = document.createElement("style");
  style.textContent = [
    ".beta-agent-icon-button{display:grid!important;place-items:center;",
    "width:32px;height:30px;padding:0!important}",
    ".beta-agent-icon-button svg{width:16px;height:16px;pointer-events:none}",
    "header .logo[data-beta-explorer-toggle]{cursor:pointer}",
    "header .logo[data-beta-explorer-toggle]:focus-visible{outline:2px solid #58a6ff;",
    "outline-offset:3px}",
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
  function decorateAgentRows(root = document) {
    root.querySelectorAll(".agent-title").forEach((title) => {
      if (title.dataset.betaAgentDisplay) return;
      title.dataset.betaAgentDisplay = "1";
      title.textContent = humanizeAgentName(title.textContent);
    });
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
  decorateAgentRows();
  const agentList = document.getElementById("agent-list-ul");
  if (agentList) {
    new MutationObserver(() => decorateAgentRows(agentList)).observe(
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
      update.message || "Check GitHub for the latest RAPP Brainstem Frontier.",
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
      brainLogo.setAttribute(
        "aria-label",
        "we are above that — toggle live agents",
      );
      brainLogo.setAttribute("role", "button");
      brainLogo.setAttribute("aria-expanded", "false");
      brainLogo.tabIndex = 0;
      if (!brainLogo.dataset.betaExplorerToggle) {
        brainLogo.dataset.betaExplorerToggle = "1";
        const toggleExplorer = () => {
          window.parent.postMessage({ type: "rapp-beta:toggle-explorer" }, "*");
        };
        brainLogo.addEventListener("click", toggleExplorer);
        brainLogo.addEventListener("keydown", (event) => {
          if (!["Enter", " "].includes(event.key)) return;
          event.preventDefault();
          toggleExplorer();
        });
      }
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
        + 'type="button" title="RAPP Brainstem Frontier menu" aria-haspopup="true" '
        + 'aria-expanded="false"><span class="icon"><svg viewBox="0 0 24 24" '
        + 'fill="currentColor" aria-hidden="true"><path d="M6 10a2 2 0 1 0 0 4 '
        + '2 2 0 0 0 0-4Zm6 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm6 0a2 2 0 1 0 '
        + '0 4 2 2 0 0 0 0-4Z"/></svg></span></button>'
        + '<div id="beta-app-panel"><h3>RAPP Brainstem Frontier</h3>'
        + '<p class="beta-app-copy">Chat is the control surface. Agents can add '
        + 'capabilities and visibly operate this workspace while you watch.</p>'
        + '<button class="beta-panel-btn" id="beta-check-updates" type="button">'
        + 'Check for updates</button><div id="beta-update-status" '
        + 'data-phase="idle" role="status" aria-live="polite">Check GitHub for '
        + 'the latest RAPP Brainstem Frontier.</div><button class="beta-panel-btn '
        + 'primary" id="beta-install-update" type="button" hidden>'
        + 'Update and Restart</button></div>';
      const vscode = document.getElementById("vscode-link");
      controls.insertBefore(wrapper, vscode || null);
      button = document.getElementById("beta-app-btn");
      panel = document.getElementById("beta-app-panel");
    }
    button.title = "RAPP Brainstem Frontier menu";
    button.setAttribute("aria-label", "RAPP Brainstem Frontier menu");
    const menuHeading = panel.querySelector("h3");
    if (menuHeading) menuHeading.textContent = "RAPP Brainstem Frontier";
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
    } else if (event.data.type === "rapp-beta:explorer-state") {
      document.querySelector("header .logo")
        ?.setAttribute("aria-expanded", String(Boolean(event.data.open)));
    } else if (event.data.type === "rapp-beta:lineage-confirmation") {
      const reply = String(event.data.reply || "");
      let rendered = false;
      if (reply && typeof appendMsg === "function") {
        appendMsg("assistant", reply);
        rendered = true;
      } else if (reply) {
        const chat = document.getElementById("chat");
        if (chat) {
          const wrap = document.createElement("div");
          wrap.className = "msg assistant";
          const bubble = document.createElement("div");
          bubble.className = "bubble";
          bubble.textContent = reply;
          wrap.appendChild(bubble);
          chat.appendChild(wrap);
          chat.classList.add("has-messages");
          chat.scrollTop = chat.scrollHeight;
          rendered = true;
        }
      }
      if (rendered) {
        window.parent.postMessage({
          type: "rapp-beta:lineage-confirmation-ack",
          confirmationId: event.data.confirmationId,
        }, "*");
      }
    }
  });
  const nativeFetch = window.fetch.bind(window);
  async function requestLineageCommand(message) {
    const requestId = window.crypto.randomUUID();
    return new Promise((resolve, reject) => {
      const timeout = window.setTimeout(() => {
        window.removeEventListener("message", receive);
        reject(new Error("Molt Lineage control timed out."));
      }, 120000);
      function receive(event) {
        if (
          event.source !== window.parent
          || event.data?.type !== "rapp-beta:lineage-chat-result"
          || event.data?.requestId !== requestId
        ) return;
        window.clearTimeout(timeout);
        window.removeEventListener("message", receive);
        if (event.data.ok) resolve(event.data.result);
        else reject(new Error(event.data.error || "Molt Lineage control failed."));
      }
      window.addEventListener("message", receive);
      window.parent.postMessage({
        type: "rapp-beta:lineage-chat",
        requestId,
        message,
      }, "*");
    });
  }
  window.fetch = async function frontierFetch(resource, options = {}) {
    let target;
    try {
      const raw = resource instanceof Request ? resource.url : String(resource);
      target = new URL(raw, window.location.href);
    } catch {
      return nativeFetch(resource, options);
    }
    const isChat = options.method === "POST"
      && (target.pathname === "/chat" || target.pathname === "/chat/stream");
    if (!isChat || typeof options.body !== "string") {
      return nativeFetch(resource, options);
    }
    let body;
    try {
      body = JSON.parse(options.body);
    } catch {
      return nativeFetch(resource, options);
    }
    if (typeof body.user_input !== "string") {
      return nativeFetch(resource, options);
    }
    // Fail OPEN, always. This interceptor sits in front of every chat message,
    // so a lineage-control failure (main busy, handler throw, window teardown,
    // timeout) must never take the user's ordinary chat down with it — the layer
    // may substitute, never subtract. On any error we fall through to Grail.
    let result;
    try {
      result = await requestLineageCommand(body.user_input);
    } catch {
      return nativeFetch(resource, options);
    }
    if (!result?.intercepted) {
      return nativeFetch(resource, options);
    }
    if (target.pathname === "/chat/stream") {
      const frame = "data: " + JSON.stringify({
        type: "done",
        response: result.reply,
        agent_logs: "",
        streamed: false,
      }) + "\\n\\n";
      return new Response(frame, {
        status: 200,
        headers: { "Content-Type": "text/event-stream; charset=utf-8" },
      });
    }
    return new Response(JSON.stringify({
      response: result.reply,
      agent_logs: "",
    }), {
      status: 200,
      headers: { "Content-Type": "application/json; charset=utf-8" },
    });
  };
  async function requestParent(type, filename) {
    const requestId = window.crypto.randomUUID();
    return new Promise((resolve, reject) => {
      const timeout = window.setTimeout(() => {
        window.removeEventListener("message", receive);
        reject(new Error("Frontier agent action timed out."));
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
let e2eStopTimer = null;
// One GitHub Copilot Brain Surgeon SDK session per chat tab, keyed by the id the
// renderer assigns. All share one runtime, one route manager, and one visible
// Brainstem — "several agents, one brainstem" — and every event they emit is
// tagged with its sessionId so the renderer routes it to the right tab/tile.
const brainSurgeons = new Map();
const chatLeaseRegistry = new Set();
const MAX_BRAIN_SURGEONS = 12;

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
    message: "Check GitHub for the latest RAPP Brainstem Frontier.",
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

// RAPPlication twins — specialized rapplications hatched from the RAPP Store as
// concurrent long-lived workers on their own loopback ports, beside the
// Brainstem chats in the herd. Kernel unchanged; driven only over /chat.
// RAR library source selection: AIBAST (default) / public RAR / a custom
// RAR-compliant catalog URL. Persisted per install; the active client backs
// BOTH the store browser and twin hatching. `rappStore` is a stable facade so
// everything that holds a reference follows the toggle.
const storeSourceFile = path.join(betaHome, "store-source.json");
function loadStoreSource() {
  try {
    const saved = JSON.parse(readFileSync(storeSourceFile, "utf8"));
    if (saved && isAllowedStoreSourceUrl(saved.url)) return saved;
  } catch { /* first run */ }
  return { key: "aibast", url: STORE_SOURCES.aibast.url };
}
let storeSource = loadStoreSource();
// Chromium's network stack (net.fetch) honors the system / enterprise proxy
// configuration the way the rest of the desktop does; Node's global fetch
// does not read HTTP(S)_PROXY at all, which made Store browsing, acquisition,
// and hatching fail on proxy-only networks where the installer had succeeded.
const storeFetch = typeof net?.fetch === "function"
  ? (url, init) => net.fetch(url, init)
  : globalThis.fetch;
let activeStoreClient = new RappStoreClient({ url: storeSource.url, fetchImpl: storeFetch });
function setStoreSource({ key, url }) {
  const target = STORE_SOURCES[key]?.url || url;
  // https everywhere — with a loopback exception so a local-first / air-gapped
  // RAR served on this machine works (never plain http to another host).
  if (!isAllowedStoreSourceUrl(target)) {
    throw new Error("A RAR source must be an https catalog URL (or http on this machine's loopback).");
  }
  storeSource = { key: STORE_SOURCES[key] ? key : "custom", url: target };
  activeStoreClient = new RappStoreClient({ url: target, fetchImpl: storeFetch });
  try { writeFileSync(storeSourceFile, JSON.stringify(storeSource, null, 2), { mode: 0o600 }); } catch { /* best effort */ }
  return { ...storeSource };
}
const rappStore = {
  list: (...a) => activeStoreClient.list(...a),
  load: (...a) => activeStoreClient.load(...a),
  resolve: (...a) => activeStoreClient.resolve(...a),
  download: (...a) => activeStoreClient.download(...a),
};

// Install a sha-verified agent.py through the routed composition gate. The
// candidate must dry-load before the stack changes, then startDefault swaps the
// worker atomically so a rejected store artifact never lands in AGENTS_PATH.
async function installAgentToBrainstem(storeId) {
  const cartridge = await rappStore.download(storeId);   // fail-closed sha256
  const filename = cartridge.filename && cartridge.filename.endsWith(".py")
    ? cartridge.filename
    : `${String(storeId).replace(/[^a-z0-9_]+/gi, "_")}_agent.py`;
  const installed = await routeManager.installScopedAgent({
    filename,
    source: cartridge.source,
  });
  const route = await routeManager.startDefault();
  const savedName = installed.agent.filename;
  return {
    ok: true,
    filename: savedName,
    requested: filename,
    agent: savedName,
    sha256: cartridge.sha256,
    persisted: "active stack (scoped install)",
    active_route: route,
  };
}
const twinManager = new TwinManager({
  brainstemConfig: config,
  betaHome,
  routeManager,
  storeClient: rappStore,
  // The Brainstem that plans a two-brain loop is whichever one is live now
  // (config URL, or a routed Brainstem once a route activates).
  brainstemUrl: () => state.url,
  onEvent: (event) => {
    if (event.type === "twin-needs-auth") notifyTwinNeedsAuth(event);
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send(
        "beta:twin-event",
        structuredClone(redactSensitiveValue(event)),
      );
    }
  },
});

// Twins pause at the one user-owned auth step (e.g. PAC device login). If the
// user is multitasking off the window they must still know a twin needs them —
// so we raise a native OS notification, and clicking it focuses the window and
// pops open the auth page in the user's own browser (identity auth is completed
// in their real session; the app never captures credentials).
const twinAuthPrompts = new Map();   // twinId -> { url, code, note }

function parseAuthPrompt(message) {
  const text = String(message || "");
  const url = (text.match(/https?:\/\/[^\s"')]+/) || [])[0]
    || (/devicelogin|device code|microsoft/i.test(text) ? "https://microsoft.com/devicelogin" : null);
  const code = (text.match(/\b[A-Z0-9]{4,5}-[A-Z0-9]{4,5}\b/) || [])[0] || null;
  return { url, code };
}

function openExternalUrl(url) {
  const value = String(url || "");
  if (!/^https?:\/\//i.test(value)) throw new Error("Refusing to open a non-http(s) URL.");
  return shell.openExternal(value);
}

function notifyTwinNeedsAuth(event) {
  const twin = twinManager.list().find((t) => t.id === event.id);
  const name = twin?.name || event.id || "A RAPPlication twin";
  const { url, code } = parseAuthPrompt(event.message);
  twinAuthPrompts.set(event.id, { url, code, note: event.message });
  if (!Notification.isSupported()) return;
  const notification = new Notification({
    title: "A RAPP twin needs you to sign in",
    body: `${name} paused for authentication${code ? ` — code ${code}` : ""}. Click to continue.`,
    silent: false,
  });
  notification.on("click", () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
      mainWindow.webContents.send("beta:twin-focus", { id: event.id });
    }
    if (url) openExternalUrl(url).catch(() => {});
  });
  notification.show();
}

// Pop a twin's own UI out into a phone-sized window — "mobile-first" literally —
// so a RAPPlication is comfortable to use at a real small-screen size.
// Walk the main window's frame tree to find the iframe hosting a twin's UI
// (loaded from the twin's own loopback origin).
function findTwinFrame(twinUrl) {
  if (!mainWindow || mainWindow.isDestroyed() || !twinUrl) return null;
  const prefix = String(twinUrl).replace(/\/+$/, "");
  const walk = (frame) => {
    const url = String(frame.url || "");
    if (url === prefix || url.startsWith(prefix + "/") || url.startsWith(prefix + "?")) return frame;
    for (const child of frame.frames || []) {
      const found = walk(child);
      if (found) return found;
    }
    return null;
  };
  return walk(mainWindow.webContents.mainFrame);
}

// Wipe the Grail chat in a twin's iframe and inject the rapplication's own
// static UI in its place. The iframe is loaded from the twin's own origin, so
// the injected UI's relative /chat hits the twin directly — no server, no proxy.
// A tiny force-mode marker woven into every injected rapplication UI. Because
// WE write the HTML into the frame, we can make any rapplication UI drivable /
// "force-mode capable" — the AI drives it in-frame with the ui-driver's cursor,
// and this flag lets the UI (or us) know it is under AI control. A rapplication
// may also ship its own force-mode affordances; this never overrides them.
const FORCE_MODE_BOOTSTRAP = "<script>window.__rappForceModeCapable=true;"
  + "try{document.documentElement.setAttribute('data-rapp-force-mode','ready');}catch(e){}</script>";

function instrumentRappUi(html) {
  const marker = FORCE_MODE_BOOTSTRAP;
  // Inject right after <head> when present, else prepend.
  return /<head[^>]*>/i.test(html)
    ? html.replace(/<head[^>]*>/i, (m) => m + marker)
    : marker + html;
}

const injectedFrames = new WeakSet();   // avoid re-injecting the same frame

async function injectFrameUi(frame, twinId) {
  if (injectedFrames.has(frame)) return { ok: true, already: true };
  const raw = twinManager.uiHtml(twinId);
  if (!raw) return { ok: false, reason: "no custom UI" };
  const html = instrumentRappUi(raw);
  injectedFrames.add(frame);
  await frame.executeJavaScript(
    `(() => { const html = ${JSON.stringify(html)}; document.open(); document.write(html); document.close(); return true; })()`,
    true,
  );
  return { ok: true, instrumented: true };
}

async function injectTwinUi(twinId) {
  const twin = twinManager.list().find((t) => t.id === twinId);
  if (!twin?.url) throw new Error(`No twin ${twinId}.`);
  const frame = findTwinFrame(twin.url);
  if (!frame) throw new Error(`Twin ${twinId} UI frame is not loaded yet.`);
  return injectFrameUi(frame, twinId);
}

// A small host-injected view toggle (declared): the pop-out opens with the full
// desktop real estate by default (a rapplication with a lot of UI shouldn't be
// mashed into a phone column), and the user can flip it to a centered mobile
// column any time. A rapplication may declare preferred_view:"mobile" to start
// narrow. This is the ONLY thing the host adds to the popped-out frame.
const VIEW_TOGGLE = (startMobile) => `
<style id="__rappViewStyle">
  html[data-rapp-view="mobile"] body { max-width: 480px !important; margin: 0 auto !important;
    box-shadow: 0 0 0 100vmax rgba(0,0,0,.25); }
  #__rappViewToggle { position: fixed; top: 8px; right: 8px; z-index: 2147483647;
    font: 600 11px Inter,system-ui,sans-serif; background: rgba(22,27,34,.9); color: #c8c9cc;
    border: 1px solid #30363d; border-radius: 7px; padding: 4px 9px; cursor: pointer; }
  #__rappViewToggle:hover { color: #e6edf3; border-color: #58a6ff; }
</style>
<script>
  (function(){
    document.documentElement.dataset.rappView = ${startMobile ? '"mobile"' : '"full"'};
    var b = document.createElement("button");
    b.id = "__rappViewToggle";
    function label(){ b.textContent = document.documentElement.dataset.rappView === "mobile" ? "⤢ Full width" : "▭ Mobile view"; }
    b.addEventListener("click", function(){
      document.documentElement.dataset.rappView = document.documentElement.dataset.rappView === "mobile" ? "full" : "mobile";
      label();
    });
    label();
    (document.body || document.documentElement).appendChild(b);
  })();
</script>`;

function popOutTwin(id) {
  const twin = twinManager.list().find((t) => t.id === id);
  if (!twin?.url) throw new Error(`No twin ${id}.`);
  const startMobile = twin.preferredView === "mobile";
  const win = new BrowserWindow({
    // Use the real estate by default; resizable back down to a phone column.
    width: startMobile ? 460 : 1180,
    height: 860,
    minWidth: 380,
    minHeight: 480,
    title: twin.name || "RAPPlication",
    backgroundColor: "#0d1117",
    parent: mainWindow || undefined,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true },
  });
  win.setMenuBarVisibility(false);
  const raw = twinManager.uiHtml(id);
  const html = raw ? instrumentRappUi(raw) + VIEW_TOGGLE(startMobile) : null;
  win.webContents.on("did-finish-load", () => {
    if (html) {
      win.webContents.executeJavaScript(
        `(() => { const h = ${JSON.stringify(html)}; document.open(); document.write(h); document.close(); return true; })()`,
        true,
      ).catch(() => {});
    }
  });
  win.loadURL(`${twin.url}/?beta=1`);
  return { ok: true };
}

// P2: hatch the Copilot Studio Factory + Deploy pipeline onto its OWN twin, and
// kick its deploy loop asynchronously. The Brain Surgeon (and the main Brainstem
// chat) stays free for other work while this twin drives PAC / Factory / Deploy
// on its own port — the deploy engine is unchanged, only WHERE it runs and WHO
// drives it (a twin loop, not the visible Brainstem). Draft-only; the one
// visible step is the user-owned PAC device login, which the twin surfaces.
const COPILOT_STUDIO_TWIN_AGENTS = [
  "rar_kody_w_factory_agent.py",
  "rar_kody_w_copilot_studio_parity_deploy_agent.py",
];
const COPILOT_STUDIO_TWIN_RESOURCES = [
  "hacker-news-memory-parity-cases.json",
  "industry-agent-matrix.json",
];

function readCopilotStudioResource(name) {
  const file = path.join(import.meta.dirname, "..", "resources", "copilot-studio", name);
  if (!existsSync(file)) throw new Error(`Bundled Copilot Studio resource is missing: ${file}`);
  return file;
}

async function hatchCopilotStudioTwin({ displayName = "Copilot Studio Draft", environment = null, agents = [] } = {}) {
  const agentSources = [];
  for (const filename of COPILOT_STUDIO_TWIN_AGENTS) {
    agentSources.push({ filename, source: readFileSync(readCopilotStudioResource(filename), "utf8") });
  }
  // Include the selected business/industry agents to deploy (from the active
  // composition), so the twin can build and parity-test them Draft-only.
  const active = routeManager.activeAgentFiles();
  for (const wanted of Array.isArray(agents) ? agents : []) {
    const match = active.find((a) => a.filename === wanted);
    if (match) {
      try {
        agentSources.push({ filename: match.filename, source: routeManager.readActiveAgent(match.filename) });
      } catch {
        // skip unreadable agent
      }
    }
  }
  const resources = COPILOT_STUDIO_TWIN_RESOURCES.map((name) => ({
    name,
    bytes: readFileSync(readCopilotStudioResource(name)),
  }));
  const parityCases = "hacker-news-memory-parity-cases.json";
  const instruction = [
    "You are a Copilot Studio deploy twin running on your own Brainstem worker.",
    "Deploy the loaded business/industry agent(s) to a Draft in Microsoft Copilot Studio",
    "using RappCopilotStudioFactoryBeta and CopilotStudioDeployBeta.",
    `Target display name: ${displayName}.`,
    environment ? `Target environment: ${environment}.` : "Ask which environment only if none is authenticated.",
    "Run doctor, then plan and build. If PAC is NOT authenticated to that environment,",
    "reply with exactly what PAC device login is required and STOP — do not guess credentials.",
    "Otherwise provision, push as DRAFT, run parity against the parity cases",
    `(${parityCases} in your working dir), and finalize.`,
    "DRAFT-ONLY: never call release or publish; publishing is the user's manual action.",
    "Never read or echo any client secret. Report the AgentId, environment, and the Copilot Studio Draft link.",
    "Say DONE when the Draft is ready.",
  ].join(" ");
  // Non-blocking: hatch + kick the loop; return immediately so the Surgeon is free.
  return twinManager.hatchLocal(
    {
      id: "copilot-studio-deploy",
      name: `Copilot Studio Deploy · ${displayName}`,
      agentSources,
      resources,
      license: "beta-bundled",
    },
    { instruction },
  );
}

// Actions that actually DRIVE the one visible Brainstem (move the cursor, type,
// hold the center chat, record, run the click-through). With several Brain
// Surgeon chats live at once they share this single window, so these are
// serialized through one "stage" so two chats never fight over it. Read-only
// and quick-state actions (inspect, read, screenshot, telemetry, lease, force
// mode) pass straight through — a background chat keeps doing its own file,
// shell, build, and test work while another chat holds the stage.
const UI_STAGE_ACTIONS = new Set([
  "announce", "chat", "click", "press", "run",
  "start_recording", "stop_recording", "surgeon_chat", "tour", "type",
]);
let uiStageChain = Promise.resolve();

function executeUiCommand(command) {
  const action = String(command?.action || "").toLowerCase();
  if (!UI_STAGE_ACTIONS.has(action)) return rawUiCommand(command);
  const run = () => rawUiCommand(command);
  const result = uiStageChain.then(run, run);
  // Keep the queue moving even if one driving command fails.
  uiStageChain = result.then(() => {}, () => {});
  return result;
}

async function rawUiCommand(command) {
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

function normalizeSurgeonId(sessionId) {
  const id = Number.parseInt(sessionId, 10);
  return Number.isFinite(id) && id > 0 ? id : 1;
}

function ensureBrainSurgeon(sessionId = 1) {
  const id = normalizeSurgeonId(sessionId);
  let surgeon = brainSurgeons.get(id);
  if (!surgeon) {
    if (brainSurgeons.size >= MAX_BRAIN_SURGEONS) {
      throw new Error(
        `You have ${MAX_BRAIN_SURGEONS} Copilot chats open — close one before opening another.`,
      );
    }
    surgeon = new BrainSurgeon({
      runtime: copilot,
      brainstemUrl: config.url,
      chatLeaseRegistry,
      checkForUpdates: () => handleCheckForUpdates({ openPanel: true }),
      copilotStudioAuth,
      routeManager,
      uiCommand: executeUiCommand,
      twins: {
        hatch: (storeId, instruction) => twinManager.hatch(storeId, { instruction: instruction || null }),
        list: () => twinManager.list(),
        list_store: () => rappStore.list(),
        loop: (id, goal) => { twinManager.loop(id, goal).catch(() => {}); return { ok: true, looping: id }; },
        deploy_copilot_studio: (opts) => hatchCopilotStudioTwin(opts || {}),
        open_auth: (opts) => {
          const url = opts?.url || (opts?.id && twinAuthPrompts.get(opts.id)?.url);
          if (!url) throw new Error("No auth URL to open.");
          return openExternalUrl(url).then(() => ({ ok: true, opened: url }));
        },
      },
      onEvent: (event) => emitSurgeonEvent({ ...event, sessionId: id }),
    });
    brainSurgeons.set(id, surgeon);
  }
  return surgeon;
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

// A twin runs its own Brainstem worker on its own loopback port, and its UI is
// shown in a herd-tile iframe — so twin worker URLs are allowed to load in
// (sub)frames, alongside the active Brainstem. Both are loopback-only.
function isTwinFrameUrl(raw) {
  // Twin workers each run on their own loopback port and are shown in herd-tile
  // iframes. The kernel trust boundary and the page CSP already confine
  // everything to loopback, so any 127.0.0.1/localhost subframe is allowed
  // (this covers every twin worker without racing tile creation).
  try {
    const url = new URL(raw);
    return ["http:", "https:"].includes(url.protocol)
      && ["127.0.0.1", "localhost"].includes(url.hostname);
  } catch {
    return false;
  }
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
  if (loopbackUrl(raw) || isTwinFrameUrl(raw)) return;   // active Brainstem OR a twin worker
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
    title: "RAPP Brainstem Frontier",
    backgroundColor: "#0d1117",
    ...(appIcon ? { icon: appIcon } : {}),
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
        message: `No RAPP Brainstem Frontier update is published on ${update.updateRef} yet.`,
        detail: `This source build remains on ${update.currentVersion} `
          + `(${shortCommit(update.currentCommit)}). The latest repository commit `
          + `(${shortCommit(update.latestCommit)}) has no beta/VERSION manifest.`,
        source: `${update.repository}@${update.updateRef}`,
      });
    }
    if (!update.available) {
      if (update.channelBehind) {
        return setUpdateState({
          phase: "current",
          message: "This build is ahead of its update channel.",
          detail: `Installed ${update.currentVersion} (${shortCommit(update.currentCommit)}); `
            + `the channel serves ${update.latestVersion} (${shortCommit(update.latestCommit)}). `
            + "Nothing to install.",
          source: `${update.repository}@${update.updateRef}`,
        });
      }
      if (!update.releasePublished) {
        return setUpdateState({
          phase: "current",
          message: `RAPP Brainstem Frontier ${update.latestVersion} is staged on ${update.updateRef} but not released.`,
          detail: `${update.releaseProblem}\n`
            + `Installed ${update.currentVersion} (${shortCommit(update.currentCommit)}); `
            + `channel head ${shortCommit(update.channelCommit)}.`,
          source: `${update.repository}@${update.updateRef}`,
          guidance: "Only the commit behind the annotated release tag is ever installed "
            + "(RELEASING.md §2). Nothing to do until the release is tagged.",
        });
      }
      return setUpdateState({
        phase: "current",
        message: "RAPP Brainstem Frontier is up to date.",
        detail: `Version ${update.currentVersion} (${shortCommit(update.currentCommit)}), `
          + `the released commit behind ${update.releaseTag}.`,
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
      message: update.sameVersion
        ? `RAPP Brainstem Frontier ${update.latestVersion} can be re-aligned to its released commit.`
        : `RAPP Brainstem Frontier ${update.latestVersion} is available.`,
      detail: `Installed ${update.currentVersion} (${shortCommit(update.currentCommit)}); `
        + `released ${update.latestVersion} (${shortCommit(update.latestCommit)}, ${update.releaseTag}).`,
      source: `${update.repository}@${update.updateRef}`,
      guidance: "Update and Restart refreshes the launcher and shared Brainstem "
        + "from the release tag's exact commit. If the install fails, the "
        + "previous version is restored automatically.",
    });
  } catch (error) {
    return setUpdateState({
      phase: "error",
      message: "RAPP Brainstem Frontier could not check for updates.",
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
    message: `Installing RAPP Brainstem Frontier ${update.latestVersion}...`,
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
      message: "RAPP Brainstem Frontier could not start the update.",
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
      message: `RAPP Brainstem Frontier updated to ${result.latestVersion}.`,
      detail: `Installed commit: ${shortCommit(result.commit)}\n`
        + "The launcher and shared Brainstem source were refreshed.",
    };
    return;
  }

  const rollback = result.rollback || null;
  const restored = Boolean(rollback?.success);
  let rollbackDetail = "No rollback was possible.";
  if (restored) {
    rollbackDetail = `Restored the previous version at ${shortCommit(rollback.commit)}.`;
  } else if (rollback?.attempted) {
    rollbackDetail = `Rolling back to ${shortCommit(rollback.commit)} also failed: ${
      rollback.error || "unknown error"
    }`;
  } else if (rollback?.error) {
    rollbackDetail = rollback.error;
  }
  state.update = {
    phase: "error",
    message: restored
      ? "The update failed; the previous version was restored."
      : "RAPP Brainstem Frontier could not finish the update.",
    detail: `${result.error || "Unknown updater error."}\n\n${rollbackDetail}\n\nLog: ${
      result.logPath || "unavailable"
    }`,
    ...(restored
      ? {}
      : { guidance: "Re-run the Frontier installer to repair this install." }),
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
  ipcMain.handle("beta:lineage-command", async (event, message) => {
    assertTrustedIpc(event);
    return executeLineageCommand({
      message,
      routeManager,
      env: process.env,
    });
  });
  ipcMain.handle("beta:lineage-environments", (event) => {
    assertTrustedIpc(event);
    return routeManager.lineageEnvironments();
  });
  ipcMain.handle("beta:lineage-promote", (event, options) => {
    assertTrustedIpc(event);
    return routeManager.promoteLineage(options || {});
  });
  ipcMain.handle("beta:lineage-drift", (event, env) => {
    assertTrustedIpc(event);
    return routeManager.lineageDrift(env);
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
  ipcMain.handle("beta:surgeon-send", async (event, sessionId, prompt) => {
    assertTrustedIpc(event);
    return ensureBrainSurgeon(sessionId).send(prompt);
  });
  ipcMain.handle("beta:surgeon-reset", async (event, sessionId) => {
    assertTrustedIpc(event);
    const surgeon = brainSurgeons.get(normalizeSurgeonId(sessionId));
    if (surgeon) await surgeon.reset();
    return { ok: true };
  });
  ipcMain.handle("beta:surgeon-close", async (event, sessionId) => {
    assertTrustedIpc(event);
    const id = normalizeSurgeonId(sessionId);
    const surgeon = brainSurgeons.get(id);
    if (surgeon) {
      brainSurgeons.delete(id);
      await surgeon.stop().catch(() => {});
    }
    return { ok: true };
  });
  ipcMain.handle("beta:store-source", async (event, next) => {
    assertTrustedIpc(event);
    if (next) return setStoreSource(next);
    return { ...storeSource, sources: Object.values(STORE_SOURCES).map((s) => ({ key: s.key, label: s.label, url: s.url })) };
  });
  ipcMain.handle("beta:store-install-agent", async (event, storeId) => {
    assertTrustedIpc(event);
    return installAgentToBrainstem(storeId);
  });
  ipcMain.handle("beta:store-list", async (event) => {
    assertTrustedIpc(event);
    return rappStore.list();
  });
  ipcMain.handle("beta:twin-list", async (event) => {
    assertTrustedIpc(event);
    return twinManager.list();
  });
  ipcMain.handle("beta:twin-hatch-egg", async (event, payload) => {
    assertTrustedIpc(event);
    const bytes = payload?.bytes instanceof Uint8Array ? payload.bytes : new Uint8Array(payload?.bytes || []);
    return twinManager.hatchEgg(
      { bytes, filename: String(payload?.filename || "dropped.egg") },
      { instruction: payload?.instruction || null },
    );
  });
  ipcMain.handle("beta:twin-hatch", async (event, storeId, instruction) => {
    assertTrustedIpc(event);
    return twinManager.hatch(storeId, { instruction: instruction || null });
  });
  ipcMain.handle("beta:twin-chat", async (event, id, prompt) => {
    assertTrustedIpc(event);
    return twinManager.chat(id, prompt, { author: "You" });
  });
  ipcMain.handle("beta:twin-run", async (event, id, instruction) => {
    assertTrustedIpc(event);
    return twinManager.run(id, instruction);
  });
  // The visible Brainstem loops with the twin autonomously (two-brain: Brainstem
  // plans each turn, twin executes). Non-blocking — returns once kicked off; the
  // exchange streams into the twin's tile so the user can watch and interject.
  ipcMain.handle("beta:twin-loop", async (event, id, goal) => {
    assertTrustedIpc(event);
    twinManager.loop(id, goal).catch(() => {});   // errors surface as a twin-message in the room
    return { ok: true, looping: id };
  });
  ipcMain.handle("beta:twin-close", async (event, id) => {
    assertTrustedIpc(event);
    return twinManager.close(id);
  });
  ipcMain.handle("beta:twin-deploy-copilot-studio", async (event, options) => {
    assertTrustedIpc(event);
    return hatchCopilotStudioTwin(options || {});
  });
  ipcMain.handle("beta:twin-popout", async (event, id) => {
    assertTrustedIpc(event);
    return popOutTwin(id);
  });
  ipcMain.handle("beta:twin-inject-ui", async (event, id) => {
    assertTrustedIpc(event);
    return injectTwinUi(id);
  });
  ipcMain.handle("beta:open-auth", async (event, options) => {
    assertTrustedIpc(event);
    const { url, id } = options || {};
    const target = url || (id && twinAuthPrompts.get(id)?.url);
    if (!target) throw new Error("No auth URL to open.");
    await openExternalUrl(target);
    return { ok: true, opened: target };
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
          message: "GitHub Copilot Agent mode is ready inside Frontier.",
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
    // Blue-brain dock icon in dev too (packaged builds get it from the bundle).
    if (appIcon && !appIcon.isEmpty() && process.platform === "darwin" && app.dock) {
      app.dock.setIcon(appIcon);
    }
    session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
      callback(allowsUiDriverMediaPermission(webContents, permission));
    });
    registerIpc();
    installApplicationMenu();
    loadPendingUpdateResult();
    mainWindow = createWindow();
    startUiDriverServer({
      resolveTwinUrls: (id) => {
        const twin = twinManager.list().find((t) => t.id === id);
        return twin ? [twin.url].filter(Boolean) : [];
      },
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
    const e2eStopFile = process.env.BRAINSTEM_BETA_E2E_STOP_FILE;
    if (e2eStopFile) {
      e2eStopTimer = setInterval(() => {
        if (!existsSync(e2eStopFile)) return;
        clearInterval(e2eStopTimer);
        e2eStopTimer = null;
        app.quit();
      }, 100);
      e2eStopTimer.unref?.();
    }
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
    if (e2eStopTimer) {
      clearInterval(e2eStopTimer);
      e2eStopTimer = null;
    }
    Promise.allSettled([
      ...Array.from(brainSurgeons.values(), (surgeon) => surgeon.stop()),
      twinManager.stopAll(),
      copilot.stop(),
      routeManager.stop(),
      uiDriver?.stop(),
    ]).finally(() => {
      shutdownComplete = true;
      app.quit();
    });
  });
}
