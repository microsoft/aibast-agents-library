import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import {
  app,
  BrowserWindow,
  ipcMain,
  session,
  shell,
} from "electron";

import {
  BrainstemProcess,
  resolveBrainstemConfig,
} from "./brainstem-process.mjs";
import { CopilotRuntime } from "./copilot-runtime.mjs";

const dirname = path.dirname(fileURLToPath(import.meta.url));
const uiFile = path.join(dirname, "..", "ui", "index.html");
const uiUrl = pathToFileURL(uiFile).href;
const config = resolveBrainstemConfig();
const brainstem = new BrainstemProcess(config);
const copilot = new CopilotRuntime();

let mainWindow = null;
let shutdownStarted = false;
let shutdownComplete = false;

const state = {
  brainstem: { phase: "starting", message: "Starting shared Brainstem..." },
  copilot: { phase: "starting", message: "Connecting bundled Copilot CLI..." },
  url: config.url,
};

function emitState() {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("beta:state", structuredClone(state));
  }
}

function loopbackUrl(raw) {
  try {
    const url = new URL(raw);
    const allowedHost = ["127.0.0.1", "localhost"].includes(url.hostname);
    return allowedHost && Number(url.port || 80) === config.port;
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

function routeNavigation(event, details) {
  const raw = typeof details === "string" ? details : details?.url;
  if (!raw || raw === "about:blank" || raw === uiUrl || loopbackUrl(raw)) {
    return;
  }
  event.preventDefault();
  if (externalUrl(raw)) void shell.openExternal(raw);
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
  win.webContents.on("will-navigate", routeNavigation);
  win.webContents.on("will-frame-navigate", routeNavigation);
  win.on("closed", () => {
    mainWindow = null;
  });
  void win.loadFile(uiFile);
  return win;
}

function registerIpc() {
  ipcMain.handle("beta:get-state", () => structuredClone(state));
}

async function startServices() {
  const brainstemTask = brainstem.start().then((result) => {
    state.brainstem = {
      phase: "ready",
      message: result.reused
        ? `Using shared Brainstem v${result.health.version}`
        : `Brainstem v${result.health.version} started`,
    };
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
    emitState();
  }).catch((error) => {
    state.copilot = {
      phase: "warning",
      message: `Copilot CLI status unavailable: ${String(error.message || error)}`,
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
    session.defaultSession.setPermissionRequestHandler((_webContents, _permission, callback) => {
      callback(false);
    });
    registerIpc();
    mainWindow = createWindow();
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
    Promise.allSettled([brainstem.stop(), copilot.stop()]).finally(() => {
      shutdownComplete = true;
      app.quit();
    });
  });
}
