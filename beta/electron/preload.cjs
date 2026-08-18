const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("brainstemBeta", {
  checkForUpdates: () => ipcRenderer.invoke("beta:check-for-updates"),
  getState: () => ipcRenderer.invoke("beta:get-state"),
  installUpdate: () => ipcRenderer.invoke("beta:install-update"),
  deleteAgent: (filename) => ipcRenderer.invoke("beta:delete-agent", filename),
  exportAgent: (filename) => ipcRenderer.invoke("beta:export-agent", filename),
  installFrameBridge: () => (
    ipcRenderer.invoke("beta:install-frame-bridge")
  ),
  listAgentFiles: () => ipcRenderer.invoke("beta:list-agent-files"),
  readAgentFile: (filename, scope) => (
    ipcRenderer.invoke("beta:read-agent-file", filename, scope)
  ),
  surgeonReset: (sessionId = 1) => ipcRenderer.invoke("beta:surgeon-reset", sessionId),
  surgeonSend: (sessionId, prompt) => ipcRenderer.invoke("beta:surgeon-send", sessionId, prompt),
  surgeonClose: (sessionId) => ipcRenderer.invoke("beta:surgeon-close", sessionId),
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
