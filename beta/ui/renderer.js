const frame = document.getElementById("brainstem");
const splash = document.getElementById("splash");
const error = document.getElementById("error");
const brainstemStatus = document.getElementById("brainstem-status");
const copilotStatus = document.getElementById("copilot-status");
const intro = document.getElementById("intro");
const introStorageKey = "rapp-brainstem-beta-intro-v1";

let loadedUrl = null;

function setPill(element, status) {
  element.className = `pill ${status.phase || ""}`;
  element.textContent = status.message || status.phase || "Unknown";
}

function render(state) {
  setPill(brainstemStatus, state.brainstem);
  setPill(copilotStatus, state.copilot);

  if (state.brainstem.phase === "ready") {
    if (loadedUrl !== state.url) {
      loadedUrl = state.url;
      frame.src = state.url;
    }
    frame.classList.add("ready");
    splash.classList.add("hidden");
    error.textContent = "";
    return;
  }

  frame.classList.remove("ready");
  splash.classList.remove("hidden");
  error.textContent = state.brainstem.phase === "error"
    ? state.brainstem.message
    : "";
}

document.getElementById("browser").addEventListener("click", () => {
  void window.brainstemBeta.openBrowser();
});
document.getElementById("vscode").addEventListener("click", () => {
  void window.brainstemBeta.openVscode();
});
document.getElementById("restart").addEventListener("click", () => {
  void window.brainstemBeta.restart();
});
document.getElementById("guide").addEventListener("click", () => {
  intro.classList.remove("hidden");
});
document.getElementById("enter").addEventListener("click", () => {
  localStorage.setItem(introStorageKey, "seen");
  intro.classList.add("hidden");
});

if (localStorage.getItem(introStorageKey) === "seen") {
  intro.classList.add("hidden");
}

window.brainstemBeta.onState(render);
window.brainstemBeta.getState().then(render);
