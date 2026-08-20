const { contextBridge, ipcRenderer } = require("electron");

const streamArgument = process.argv.find((value) => (
  value.startsWith("--rapp-chat-stream=")
));
const requestedStreamMode = streamArgument?.split("=", 2)[1];
const chatStreamMode = ["smooth", "raw", "hold"].includes(requestedStreamMode)
  ? requestedStreamMode
  : "smooth";

contextBridge.exposeInMainWorld("brainstemBeta", {
  chatStreamMode,
  checkForUpdates: () => ipcRenderer.invoke("beta:check-for-updates"),
  getState: () => ipcRenderer.invoke("beta:get-state"),
  installUpdate: () => ipcRenderer.invoke("beta:install-update"),
  deleteAgent: (filename) => ipcRenderer.invoke("beta:delete-agent", filename),
  exportAgent: (filename) => ipcRenderer.invoke("beta:export-agent", filename),
  installFrameBridge: () => (
    ipcRenderer.invoke("beta:install-frame-bridge")
  ),
  lineageCommand: (message) => (
    ipcRenderer.invoke("beta:lineage-command", message)
  ),
  lineageEnvironments: () => (
    ipcRenderer.invoke("beta:lineage-environments")
  ),
  lineagePromote: (options) => (
    ipcRenderer.invoke("beta:lineage-promote", options || {})
  ),
  lineageDrift: (env) => (
    ipcRenderer.invoke("beta:lineage-drift", env)
  ),
  listAgentFiles: () => ipcRenderer.invoke("beta:list-agent-files"),
  readAgentFile: (filename, scope) => (
    ipcRenderer.invoke("beta:read-agent-file", filename, scope)
  ),
  surgeonReset: (sessionId = 1) => ipcRenderer.invoke("beta:surgeon-reset", sessionId),
  surgeonSend: (sessionId, prompt) => ipcRenderer.invoke("beta:surgeon-send", sessionId, prompt),
  surgeonClose: (sessionId) => ipcRenderer.invoke("beta:surgeon-close", sessionId),
  storeList: () => ipcRenderer.invoke("beta:store-list"),
  storeSource: (next) => ipcRenderer.invoke("beta:store-source", next || null),
  storeInstallAgent: (id) => ipcRenderer.invoke("beta:store-install-agent", id),
  twinList: () => ipcRenderer.invoke("beta:twin-list"),
  twinHatch: (storeId, instruction) => ipcRenderer.invoke("beta:twin-hatch", storeId, instruction),
  twinHatchEgg: (payload) => ipcRenderer.invoke("beta:twin-hatch-egg", payload),
  twinChat: (id, prompt) => ipcRenderer.invoke("beta:twin-chat", id, prompt),
  twinRun: (id, instruction) => ipcRenderer.invoke("beta:twin-run", id, instruction),
  twinLoop: (id, goal) => ipcRenderer.invoke("beta:twin-loop", id, goal),
  twinClose: (id) => ipcRenderer.invoke("beta:twin-close", id),
  twinDeployCopilotStudio: (options) => ipcRenderer.invoke("beta:twin-deploy-copilot-studio", options),
  twinPopOut: (id) => ipcRenderer.invoke("beta:twin-popout", id),
  twinInjectUi: (id) => ipcRenderer.invoke("beta:twin-inject-ui", id),
  openAuth: (options) => ipcRenderer.invoke("beta:open-auth", options),
  onTwinFocus: (listener) => {
    const wrapped = (_event, payload) => listener(payload);
    ipcRenderer.on("beta:twin-focus", wrapped);
    return () => ipcRenderer.removeListener("beta:twin-focus", wrapped);
  },
  onTwinEvent: (listener) => {
    const wrapped = (_event, payload) => listener(payload);
    ipcRenderer.on("beta:twin-event", wrapped);
    return () => ipcRenderer.removeListener("beta:twin-event", wrapped);
  },
  onSurgeonEvent: (listener) => {
    const wrapped = (_event, payload) => listener(payload);
    ipcRenderer.on("beta:surgeon-event", wrapped);
    return () => ipcRenderer.removeListener("beta:surgeon-event", wrapped);
  },
  onOpenUpdate: (listener) => {
    const wrapped = () => listener();
    ipcRenderer.on("beta:open-update", wrapped);
    return () => ipcRenderer.removeListener("beta:open-update", wrapped);
  },
  onState: (listener) => {
    const wrapped = (_event, state) => listener(state);
    ipcRenderer.on("beta:state", wrapped);
    return () => ipcRenderer.removeListener("beta:state", wrapped);
  },
});
