const frame = document.getElementById("brainstem");
const splash = document.getElementById("splash");
const error = document.getElementById("error");
const intro = document.getElementById("intro");
const introStorageKey = "rapp-brainstem-beta-intro-v1";
const surgeon = document.getElementById("surgeon");
const surgeonLog = document.getElementById("surgeon-log");
const surgeonInput = document.getElementById("surgeon-input");
const surgeonSend = document.getElementById("surgeon-send");
const surgeonHistoryKey = "rapp-brainstem-beta-surgeon-history-v1";
const surgeonOpenKey = "rapp-brainstem-beta-surgeon-open-v1";
const explorer = document.getElementById("explorer");
const agentTree = document.getElementById("agent-tree");
const agentSource = document.getElementById("agent-source");
const agentViewerEmpty = document.getElementById("agent-viewer-empty");
const agentViewerTab = document.getElementById("agent-viewer-tab");
const explorerStatus = document.getElementById("explorer-status");
const explorerOpenKey = "rapp-brainstem-beta-explorer-open-v1";
let loadedUrl = null;
let brainstemNavigationCount = 0;
window.__brainstemBetaNavigationCount = 0;
let latestState = null;
let surgeonBusy = false;
let surgeonCurrentAssistant = null;
let surgeonThinking = null;
let surgeonHistory = [];
const surgeonTools = [];
let currentAgentFile = null;
let currentAgentScope = "global";
let currentAgentRevision = null;
let agentTreeSignature = null;
let agentRefreshPromise = null;
let openBetaMenuOnNextSync = false;

frame.addEventListener("load", () => {
  brainstemNavigationCount += 1;
  window.__brainstemBetaNavigationCount = brainstemNavigationCount;
  void window.brainstemBeta.installFrameBridge().then(() => {
    syncBetaUpdate(latestState?.update, openBetaMenuOnNextSync);
    syncExplorerState();
    openBetaMenuOnNextSync = false;
  });
});
window.addEventListener("message", async (event) => {
  const type = event.data?.type;
  if (event.source !== frame.contentWindow) return;
  if (type === "rapp-beta:check-updates") {
    await window.brainstemBeta.checkForUpdates();
    return;
  }
  if (type === "rapp-beta:install-update") {
    await window.brainstemBeta.installUpdate();
    return;
  }
  if (type === "rapp-beta:toggle-explorer") {
    setExplorerOpen(!explorer.classList.contains("open"));
    return;
  }
  if (!["rapp-beta-delete-agent", "rapp-beta-export-agent"].includes(type)) return;
  const requestId = String(event.data.requestId || "");
  try {
    const filename = String(event.data.filename || "");
    const result = type === "rapp-beta-delete-agent"
      ? await window.brainstemBeta.deleteAgent(filename)
      : await window.brainstemBeta.exportAgent(filename);
    event.source.postMessage({
      type: `${type}-result`,
      requestId,
      ok: true,
      result,
    }, "*");
    agentTreeSignature = null;
    await refreshAgentExplorer();
  } catch (cause) {
    event.source.postMessage({
      type: `${type}-result`,
      requestId,
      ok: false,
      error: String(cause?.message || cause),
    }, "*");
  }
});

function setExplorerOpen(open) {
  if (open && window.innerWidth < 820) setSurgeonOpen(false);
  explorer.classList.toggle("open", open);
  document.body.classList.toggle("explorer-open", open);
  localStorage.setItem(explorerOpenKey, open ? "open" : "closed");
  syncExplorerState();
  if (open) void refreshAgentExplorer();
}

function syncExplorerState() {
  frame.contentWindow?.postMessage({
    type: "rapp-beta:explorer-state",
    open: explorer.classList.contains("open"),
  }, "*");
}

function setSurgeonOpen(open) {
  if (open && window.innerWidth < 820) setExplorerOpen(false);
  surgeon.classList.toggle("open", open);
  document.body.classList.toggle("surgeon-open", open);
  localStorage.setItem(surgeonOpenKey, open ? "open" : "closed");
  if (open) setTimeout(() => surgeonInput.focus(), 300);
}

function shortIdentifier(value, length = 24) {
  const text = String(value || "");
  return text.length > length ? `${text.slice(0, length)}…` : text;
}

function agentTreeRow(item, depth = 1) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `agent-tree-file${
    item.filename === currentAgentFile && item.scope === currentAgentScope
      ? " active"
      : ""
  }`;
  button.setAttribute("role", "treeitem");
  button.title = item.filename;
  button.style.paddingLeft = `${22 + (depth * 16)}px`;
  const icon = document.createElement("span");
  icon.textContent = "🐍";
  const name = document.createElement("span");
  name.className = "name";
  name.textContent = item.filename;
  const count = document.createElement("span");
  count.className = "count";
  count.textContent = String(item.scope || "").startsWith("stack:")
    ? "role"
    : (item.loadable ? "hot-load" : "support");
  button.append(icon, name, count);
  button.addEventListener(
    "click",
    () => void openAgentFile(item.filename, item.revision, item.scope),
  );
  return button;
}

function appendStackNode(node, filesByStack, depth = 0) {
  const row = document.createElement("div");
  row.className = `agent-tree-stack${
    node.active ? " active" : (node.overlay_order ? " overlay" : "")
  }`;
  row.setAttribute("role", "treeitem");
  row.style.paddingLeft = `${20 + (depth * 16)}px`;
  row.title = node.rappid;
  const state = node.active
    ? "selected"
    : (node.overlay_order ? `overlay ${node.overlay_order}` : `${node.agent_count} agents`);
  row.textContent = `${
    node.children?.length ? "▾" : "•"
  } ${node.name} · ${state} · ${shortIdentifier(node.rappid, 18)}`;
  agentTree.appendChild(row);
  for (const item of filesByStack.get(node.rappid) || []) {
    agentTree.appendChild(agentTreeRow(item, depth + 2));
  }
  for (const child of node.children || []) {
    appendStackNode(child, filesByStack, depth + 1);
  }
}

async function refreshAgentExplorer() {
  if (agentRefreshPromise) return agentRefreshPromise;
  if (!explorer.classList.contains("open") || latestState?.brainstem?.phase !== "ready") {
    return;
  }
  agentRefreshPromise = (async () => {
    try {
      const payload = await window.brainstemBeta.listAgentFiles();
      const files = [...(payload.files || [])]
        .filter((item) => (
          typeof item.filename === "string" && item.filename.endsWith(".py")
        ))
        .sort((left, right) => left.filename.localeCompare(right.filename));
      const stackTree = Array.isArray(payload.stack_tree)
        ? payload.stack_tree
        : [];
      const signature = JSON.stringify({
        caller: payload.caller_rappid,
        memory: payload.memory_guid,
        active: payload.active_stack_rappid,
        overlays: payload.overlay_stack_rappids,
        stackTree,
        files,
      });
      if (signature !== agentTreeSignature) {
        agentTreeSignature = signature;
        agentTree.replaceChildren();
        const root = document.createElement("div");
        root.className = "agent-tree-root";
        root.textContent = "▾ RAPP/1 ORGANISM";
        agentTree.append(root);

        for (const [label, value] of [
          ["caller", payload.caller_rappid],
          ["memory", payload.memory_guid],
          ["composition", payload.composition_hash],
        ]) {
          const identityRow = document.createElement("div");
          identityRow.className = "agent-tree-identity";
          identityRow.title = String(value || "");
          identityRow.textContent = `${label}: ${shortIdentifier(value, 28)}`;
          agentTree.appendChild(identityRow);
        }

        const globalFiles = files.filter(
          (item) => !String(item.scope || "").startsWith("stack:"),
        );
        const stackFiles = files.filter(
          (item) => String(item.scope || "").startsWith("stack:"),
        );
        const globalFolder = document.createElement("div");
        globalFolder.className = "agent-tree-folder";
        globalFolder.textContent = "▾ 📁 agents/ · shared + memory";
        agentTree.appendChild(globalFolder);
        for (const item of globalFiles) {
          agentTree.appendChild(agentTreeRow(item));
        }

        const stackFolder = document.createElement("div");
        stackFolder.className = "agent-tree-folder";
        stackFolder.textContent = "▾ 🌳 stack RAPPIDs";
        agentTree.appendChild(stackFolder);
        const filesByStack = new Map();
        for (const item of stackFiles) {
          const rappid = item.scope.slice("stack:".length);
          if (!filesByStack.has(rappid)) filesByStack.set(rappid, []);
          filesByStack.get(rappid).push(item);
        }
        for (const stack of stackTree) {
          appendStackNode(stack, filesByStack);
        }
        if (!files.length) {
          const empty = document.createElement("div");
          empty.className = "agent-tree-file";
          empty.textContent = "No Python files in the active composition";
          agentTree.appendChild(empty);
        }
        if (
          currentAgentFile
          && !files.some((item) => (
            item.filename === currentAgentFile
            && item.scope === currentAgentScope
          ))
        ) {
          currentAgentFile = null;
          currentAgentScope = "global";
          currentAgentRevision = null;
          agentSource.hidden = true;
          agentViewerEmpty.hidden = false;
          agentViewerTab.textContent = "No agent selected";
        }
      }
      const selected = files.find((item) => (
        item.filename === currentAgentFile
        && item.scope === currentAgentScope
      ));
      if (selected && selected.revision !== currentAgentRevision) {
        const result = await window.brainstemBeta.readAgentFile(
          selected.filename,
          selected.scope,
        );
        currentAgentRevision = selected.revision;
        agentViewerTab.textContent = `🐍 ${
          String(selected.scope).startsWith("stack:") ? "agent_stacks" : "agents"
        }/${result.filename} · read-only`;
        agentSource.textContent = result.content;
        agentSource.hidden = false;
        agentViewerEmpty.hidden = true;
      }
      explorerStatus.textContent = `${files.length} files · memory ${
        shortIdentifier(payload.memory_guid, 8)
      } · ${(payload.overlay_stack_rappids || []).length} overlays · live`;
    } catch (cause) {
      explorerStatus.textContent = `Explorer unavailable: ${String(cause?.message || cause)}`;
    } finally {
      agentRefreshPromise = null;
    }
  })();
  return agentRefreshPromise;
}

async function openAgentFile(filename, revision = null, scope = "global") {
  try {
    const result = await window.brainstemBeta.readAgentFile(
      filename,
      scope,
    );
    currentAgentFile = result.filename;
    currentAgentScope = scope;
    currentAgentRevision = revision;
    agentViewerTab.textContent = `🐍 ${
      String(scope).startsWith("stack:") ? "agent_stacks" : "agents"
    }/${result.filename} · read-only`;
    agentSource.textContent = result.content;
    agentSource.hidden = false;
    agentViewerEmpty.hidden = true;
    agentTreeSignature = null;
    await refreshAgentExplorer();
  } catch (cause) {
    explorerStatus.textContent = `Could not read ${filename}: ${String(cause?.message || cause)}`;
  }
}

function saveSurgeonHistory() {
  localStorage.setItem(
    surgeonHistoryKey,
    JSON.stringify(surgeonHistory.slice(-80)),
  );
}

function addSurgeonBubble(role, text, persist = true) {
  const bubble = document.createElement("div");
  bubble.className = `surgeon-message ${role}`;
  bubble.textContent = text || "";
  surgeonLog.appendChild(bubble);
  surgeonLog.scrollTop = surgeonLog.scrollHeight;
  if (persist && ["user", "assistant"].includes(role)) {
    surgeonHistory.push({ role, content: text || "" });
    saveSurgeonHistory();
  }
  return bubble;
}

function showSurgeonEmpty() {
  if (surgeonHistory.length || surgeonLog.childElementCount) return;
  const empty = document.createElement("div");
  empty.className = "surgeon-empty";
  empty.innerHTML = `
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2c-2.3 0-3.6.9-4.3 2.1-.5-.1-1-.1-1.5-.1C3.4 4 2 5.6 2 8.2v.3C1 9 .5 9.9.5 11.2v2.1c0 2 1 3.4 2.8 4.2C5.1 18.9 8.2 20 12 20s6.9-1.1 8.7-2.5c1.8-.8 2.8-2.2 2.8-4.2v-2.1c0-1.3-.5-2.2-1.5-2.7v-.3C22 5.6 20.6 4 17.8 4c-.5 0-1 0-1.5.1C15.6 2.9 14.3 2 12 2Z"/>
    </svg>
    <h2>GitHub Copilot, in your Brainstem</h2>
    The full Copilot agent loop: files, shell, tests, one-chat capability
    injection, visible UI control, screenshots, and recorded demos.
    <div class="surgeon-caps">
      <span>run commands</span><span>read/write files</span><span>test Brainstem</span>
    </div>
    <div class="surgeon-starters"></div>
  `;
  const starters = [
    { label: "Build and test an agent for this customer use case" },
    { label: "Inspect this Brainstem and tell me what it can do" },
    { label: "Check for beta updates while I watch" },
    { label: "Record a short autopilot demo of the current workflow" },
    {
      label: "Deploy loaded agents to Copilot Studio",
      className: "deploy-copilot-studio",
      prompt: [
        "Run the beta one-click Copilot Studio deployment loop.",
        "First call ensure_copilot_studio_deploy_agents,",
        "copilot_studio_deployment_defaults, copilot_studio_auth_status,",
        "and list_active_agent_files.",
        "Record the protected parity_cases_path and industry_matrix_path",
        "returned by ensure_copilot_studio_deploy_agents.",
        "Present a concise numbered list of",
        "currently loaded business/industry agents that can be selected.",
        "Exclude BasicAgent, memory, RAR, UI-driver, Factory, Parity Deploy,",
        "and other infrastructure-only agents from the general list. Also offer",
        "a clearly labeled hello-world parity preset: HackerNews + ContextMemory",
        "+ ManageMemory. The memory pair is allowed only for that preset and its",
        "storage/infrastructure requirements must remain explicit. Ask me in this Brain Surgeon",
        "chat which agents I want, the Copilot Studio display name, publisher",
        "prefix, and target environment/profile. Do not continue until I answer.",
        "If the selected user PAC profile is not authenticated to that exact",
        "environment, call start_copilot_studio_login and show me the device",
        "login instructions; poll only after I say sign-in is complete. Never",
        "read, return, or use a client secret from local.settings.json.",
        "After selection and login, use the visible Brainstem chat to drive",
        "RappCopilotStudioFactoryBeta and CopilotStudioDeployBeta through",
        "doctor, plan, build/deploy and provision. Copy the protected",
        "parity_cases_path to",
        "the deployment run as parity-cases.json before parity, then run",
        "parity and finalize. Keep working autonomously and visibly until the",
        "Draft is proven.",
        "As soon as AgentId and EnvironmentId are known, call",
        "show_copilot_studio_agent_link so this chat contains a clickable",
        "Copilot Studio card for the exact agent. The beta is Draft-only:",
        "never call release or publish. Show the exact AgentId, environment,",
        "Draft parity evidence, and warning that live publication is a manual",
        "user action in the linked Copilot Studio UI. Record the evidence and",
        "return the Copilot Studio agent ID and URL. Do not stop at",
        "instructions or hand work to VS Code.",
      ].join(" "),
    },
  ];
  const list = empty.querySelector(".surgeon-starters");
  for (const starter of starters) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = starter.label;
    if (starter.className) button.classList.add(starter.className);
    button.addEventListener("click", () => {
      surgeonInput.value = starter.prompt || starter.label;
      void submitSurgeon();
    });
    list.appendChild(button);
  }
  surgeonLog.appendChild(empty);
}

function removeSurgeonEmpty() {
  surgeonLog.querySelector(".surgeon-empty")?.remove();
}

function showSurgeonThinking() {
  if (surgeonThinking) return;
  surgeonThinking = document.createElement("div");
  surgeonThinking.className = "surgeon-thinking";
  surgeonThinking.innerHTML = `
    <span class="surgeon-dots"><span></span><span></span><span></span></span>
    <span>Copilot is working</span>
  `;
  surgeonLog.appendChild(surgeonThinking);
  surgeonLog.scrollTop = surgeonLog.scrollHeight;
}

function hideSurgeonThinking() {
  surgeonThinking?.remove();
  surgeonThinking = null;
}

function addSurgeonTool(toolName, toolCallId) {
  const tool = document.createElement("div");
  tool.className = "surgeon-tool";
  tool.dataset.toolName = toolName;
  if (toolCallId) tool.dataset.toolCallId = toolCallId;
  tool.dataset.active = "true";
  const head = document.createElement("div");
  head.className = "surgeon-tool-head";
  const name = document.createElement("strong");
  name.textContent = toolName;
  const status = document.createElement("span");
  status.className = "surgeon-tool-status";
  status.textContent = "running";
  head.append("⚙", name, status);
  tool.appendChild(head);
  surgeonLog.appendChild(tool);
  surgeonTools.push(tool);
  surgeonLog.scrollTop = surgeonLog.scrollHeight;
}

function finishSurgeonTool(toolName, toolCallId, success) {
  const tool = [...surgeonTools].reverse().find(
    (candidate) => (
      candidate.dataset.active === "true"
      && (
        (toolCallId && candidate.dataset.toolCallId === toolCallId)
        || (!toolCallId && candidate.dataset.toolName === toolName)
      )
    ),
  );
  if (!tool) return;
  tool.dataset.active = "false";
  const status = tool.querySelector(".surgeon-tool-status");
  status.textContent = success ? "done" : "failed";
  status.style.color = success ? "#5cc271" : "#ff7b72";
}

function addSurgeonArtifact(artifact) {
  if (!artifact?.url) return;
  const card = document.createElement("div");
  card.className = "surgeon-artifact";
  if (artifact.kind === "link") {
    card.classList.add("link");
  } else if (artifact.kind === "video") {
    const video = document.createElement("video");
    video.src = artifact.url;
    video.controls = true;
    video.preload = "metadata";
    card.appendChild(video);
  } else {
    const image = document.createElement("img");
    image.src = artifact.url;
    image.alt = artifact.alt || "Brain Surgeon result";
    card.appendChild(image);
  }
  const link = document.createElement("a");
  link.href = artifact.url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = artifact.alt || "Open artifact";
  card.appendChild(link);
  surgeonLog.appendChild(card);
  surgeonLog.scrollTop = surgeonLog.scrollHeight;
}

function restoreSurgeonHistory() {
  try {
    const parsed = JSON.parse(localStorage.getItem(surgeonHistoryKey) || "[]");
    surgeonHistory = Array.isArray(parsed) ? parsed.slice(-80) : [];
  } catch {
    surgeonHistory = [];
  }
  for (const message of surgeonHistory) {
    if (["user", "assistant"].includes(message.role)) {
      addSurgeonBubble(message.role, String(message.content || ""), false);
    }
  }
  showSurgeonEmpty();
}

function clearSurgeonUi() {
  hideSurgeonThinking();
  surgeonLog.replaceChildren();
  surgeonHistory = [];
  surgeonCurrentAssistant = null;
  surgeonBusy = false;
  surgeonInput.value = "";
  surgeonInput.style.height = "auto";
  surgeonSend.disabled = false;
  surgeonSend.textContent = "Build";
  saveSurgeonHistory();
  showSurgeonEmpty();
}

async function submitSurgeon() {
  const prompt = surgeonInput.value.trim();
  if (!prompt || surgeonBusy) return;
  removeSurgeonEmpty();
  addSurgeonBubble("user", prompt);
  surgeonInput.value = "";
  surgeonInput.style.height = "auto";
  surgeonBusy = true;
  surgeonSend.disabled = true;
  surgeonSend.textContent = "Working";
  surgeonCurrentAssistant = null;
  showSurgeonThinking();
  try {
    await window.brainstemBeta.surgeonSend(prompt);
  } catch (cause) {
    hideSurgeonThinking();
    if (!surgeonCurrentAssistant) {
      addSurgeonBubble(
        "error",
        String(cause?.message || cause || "Brain Surgeon failed."),
        false,
      );
    }
  } finally {
    surgeonBusy = false;
    surgeonSend.disabled = false;
    surgeonSend.textContent = "Build";
  }
}

function handleSurgeonEvent(event) {
  if (!event) return;
  if (event.type === "response-start") {
    showSurgeonThinking();
  } else if (event.type === "delta") {
    hideSurgeonThinking();
    if (!surgeonCurrentAssistant) {
      surgeonCurrentAssistant = addSurgeonBubble("assistant", "", false);
    }
    surgeonCurrentAssistant.textContent += event.text || "";
    surgeonLog.scrollTop = surgeonLog.scrollHeight;
  } else if (event.type === "tool-start") {
    hideSurgeonThinking();
    addSurgeonTool(event.toolName || "tool", event.toolCallId);
    showSurgeonThinking();
  } else if (event.type === "tool-complete") {
    finishSurgeonTool(
      event.toolName || "tool",
      event.toolCallId,
      event.success !== false,
    );
    void refreshAgentExplorer();
  } else if (event.type === "artifact") {
    addSurgeonArtifact(event.artifact);
  } else if (event.type === "lease") {
    addSurgeonBubble("assistant", event.message || "Temporary capability leased.", false);
  } else if (event.type === "done") {
    hideSurgeonThinking();
    const finalText = String(event.content || "").trim();
    if (!surgeonCurrentAssistant) {
      surgeonCurrentAssistant = addSurgeonBubble(
        "assistant",
        finalText || "(done)",
        false,
      );
    } else if (finalText) {
      surgeonCurrentAssistant.textContent = finalText;
    }
    surgeonHistory.push({
      role: "assistant",
      content: surgeonCurrentAssistant.textContent,
    });
    saveSurgeonHistory();
    surgeonCurrentAssistant = null;
  } else if (event.type === "error") {
    hideSurgeonThinking();
    addSurgeonBubble("error", event.message || "Brain Surgeon failed.", false);
  } else if (event.type === "reset") {
    clearSurgeonUi();
  }
}

function betaUrl(raw) {
  const url = new URL(raw);
  url.searchParams.set("beta", "1");
  return url.href;
}

function syncBetaUpdate(update, openPanel = false) {
  const value = update || {
    phase: "idle",
    message: "Check GitHub for the latest RAPP Brainstem Frontier.",
  };
  frame.contentWindow?.postMessage({
    type: "rapp-beta:update-state",
    update: value,
    openPanel,
  }, "*");
}

function render(state) {
  latestState = state;
  const surgeonState = state.surgeon || state.copilot;
  document.getElementById("surgeon-model").textContent =
    surgeonState?.phase === "ready" ? "Agent" : (surgeonState?.phase || "starting");
  if (state.brainstem.phase === "ready") {
    if (loadedUrl !== state.url) {
      loadedUrl = state.url;
      frame.src = betaUrl(state.url);
    }
    frame.classList.add("ready");
    splash.classList.add("hidden");
    error.textContent = "";
    syncBetaUpdate(state.update);
    void refreshAgentExplorer();
    return;
  }

  frame.classList.remove("ready");
  splash.classList.remove("hidden");
  error.textContent = state.brainstem.phase === "error"
    ? state.brainstem.message
    : "";
}

document.getElementById("enter").addEventListener("click", () => {
  localStorage.setItem(introStorageKey, "seen");
  intro.classList.add("hidden");
  setSurgeonOpen(true);
});

document.getElementById("surgeon-tab").addEventListener(
  "click",
  () => setSurgeonOpen(true),
);
document.getElementById("explorer-close").addEventListener(
  "click",
  () => setExplorerOpen(false),
);
document.getElementById("explorer-refresh").addEventListener(
  "click",
  () => {
    agentTreeSignature = null;
    void refreshAgentExplorer();
  },
);
document.getElementById("surgeon-close").addEventListener(
  "click",
  () => setSurgeonOpen(false),
);
document.getElementById("surgeon-new").addEventListener("click", async () => {
  clearSurgeonUi();
  try {
    await window.brainstemBeta.surgeonReset();
  } catch (cause) {
    addSurgeonBubble(
      "error",
      `Could not reset Brain Surgeon: ${String(cause?.message || cause)}`,
      false,
    );
  }
});
surgeonSend.addEventListener("click", () => void submitSurgeon());
surgeonInput.addEventListener("input", () => {
  surgeonInput.style.height = "auto";
  surgeonInput.style.height = `${Math.min(surgeonInput.scrollHeight, 150)}px`;
});
surgeonInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
    event.preventDefault();
    void submitSurgeon();
  }
});

if (localStorage.getItem(introStorageKey) === "seen") {
  intro.classList.add("hidden");
}

restoreSurgeonHistory();
setSurgeonOpen(localStorage.getItem(surgeonOpenKey) !== "closed");
setExplorerOpen(localStorage.getItem(explorerOpenKey) === "open");
setInterval(() => void refreshAgentExplorer(), 2000);
window.brainstemBeta.onSurgeonEvent(handleSurgeonEvent);
window.brainstemBeta.onOpenUpdate(() => {
  openBetaMenuOnNextSync = true;
  syncBetaUpdate(latestState?.update, true);
});
window.brainstemBeta.onState(render);
window.brainstemBeta.getState().then(render);
