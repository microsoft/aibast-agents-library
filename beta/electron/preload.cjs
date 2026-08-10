const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("brainstemBeta", {
  getState: () => ipcRenderer.invoke("beta:get-state"),
  onState: (listener) => {
    const wrapped = (_event, state) => listener(state);
    ipcRenderer.on("beta:state", wrapped);
    return () => ipcRenderer.removeListener("beta:state", wrapped);
  },
});
