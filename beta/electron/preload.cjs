const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("brainstemBeta", {
  checkForUpdates: () => ipcRenderer.invoke("beta:check-for-updates"),
  getState: () => ipcRenderer.invoke("beta:get-state"),
  installUpdate: () => ipcRenderer.invoke("beta:install-update"),
  listAgentFiles: () => ipcRenderer.invoke("beta:list-agent-files"),
  readAgentFile: (filename, scope) => (
    ipcRenderer.invoke("beta:read-agent-file", filename, scope)
  ),
  surgeonReset: () => ipcRenderer.invoke("beta:surgeon-reset"),
  surgeonSend: (prompt) => ipcRenderer.invoke("beta:surgeon-send", prompt),
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
