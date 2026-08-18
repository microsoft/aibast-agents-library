const frame = document.getElementById("brainstem");
const splash = document.getElementById("splash");
const error = document.getElementById("error");
const intro = document.getElementById("intro");
const introStorageKey = "rapp-brainstem-beta-intro-v1";
const surgeon = document.getElementById("surgeon");
const surgeonLog = document.getElementById("surgeon-log");
const surgeonInput = document.getElementById("surgeon-input");
const surgeonSend = document.getElementById("surgeon-send");
const surgeonTabs = document.getElementById("surgeon-tabs");
const surgeonHerdBtn = document.getElementById("surgeon-herd-btn");
let surgeonHerdEl = null;
let surgeonGridEl = null;
const surgeonHistoryKey = "rapp-brainstem-beta-surgeon-sessions-v1";
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
// Multi-chat Brain Surgeon state (several independent Copilot chats).
let surgeonSessions = [];
let surgeonActiveId = 0;
let surgeonSeq = 0;
let surgeonHerd = false;
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

const SURGEON_STARTERS = [
  { label: "Build and test an agent for this customer use case" },
  { label: "Inspect this Brainstem and tell me what it can do" },
  { label: "Check for beta updates while I watch" },
  { label: "Record a short autopilot demo of the current workflow" },
  { label: "Show Mode: click-through preview", className: "show-mode-preview", tour: true },
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

// ── Multi-chat Brain Surgeon ─────────────────────────────────────────────
// Several independent GitHub Copilot conversations over the one visible
// Brainstem: a tab per chat plus a herd grid to see them at once. Each session
// owns its transcript node (.surgeon-session); in the dock only the active one
// shows, in the herd each node is moved into its tile — it renders identically
// either way. Every main-process event carries a sessionId so it lands in the
// right chat. Ported from the vBrainstem Brain Surgeon (surgeon.js).

function saveSurgeonSessions() {
  try {
    const data = surgeonSessions.map((s) => ({
      id: s.id,
      title: s.title,
      history: (s.history || []).slice(-80),
    }));
    localStorage.setItem(
      surgeonHistoryKey,
      JSON.stringify({ active: surgeonActiveId, sessions: data }),
    );
  } catch {
    // Over quota — keep the last few chats, trimmed.
    try {
      const data = surgeonSessions.slice(-4).map((s) => ({
        id: s.id,
        title: s.title,
        history: (s.history || []).slice(-24),
      }));
      localStorage.setItem(
        surgeonHistoryKey,
        JSON.stringify({ active: surgeonActiveId, sessions: data }),
      );
    } catch {
      // give up silently
    }
  }
}

function activeSurgeon() {
  return surgeonSessions.find((s) => s.id === surgeonActiveId) || null;
}

// ── per-session transcript rendering (scoped to session.logEl) ──
function surgeonPlace(session, node) {
  if (session.thinkEl && session.thinkEl.parentNode === session.logEl) {
    session.logEl.insertBefore(node, session.thinkEl);
  } else {
    session.logEl.appendChild(node);
  }
  scrollSurgeon(session);
}

function scrollSurgeon(session) {
  const scroller = session.logEl.closest(".htrans") || surgeonLog;
  if (session.id === surgeonActiveId || session.tileEl) {
    scroller.scrollTop = scroller.scrollHeight;
  }
}

function addSurgeonBubble(session, role, text, persist = true) {
  removeSurgeonEmpty(session);
  const bubble = document.createElement("div");
  bubble.className = `surgeon-message ${role}`;
  bubble.textContent = text || "";
  surgeonPlace(session, bubble);
  if (persist && ["user", "assistant"].includes(role)) {
    session.history.push({ role, content: text || "" });
    saveSurgeonSessions();
  }
  return bubble;
}

function showSurgeonThinking(session) {
  if (session.thinkEl) return;
  const think = document.createElement("div");
  think.className = "surgeon-thinking";
  think.innerHTML = `
    <span class="surgeon-dots"><span></span><span></span><span></span></span>
    <span>Copilot is working</span>
  `;
  session.logEl.appendChild(think);
  session.thinkEl = think;
  scrollSurgeon(session);
}

function hideSurgeonThinking(session) {
  session.thinkEl?.remove();
  session.thinkEl = null;
}

function addSurgeonTool(session, toolName, toolCallId) {
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
  surgeonPlace(session, tool);
  session.tools.push(tool);
}

function finishSurgeonTool(session, toolName, toolCallId, success) {
  const tool = [...session.tools].reverse().find(
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

function addSurgeonArtifact(session, artifact) {
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
  surgeonPlace(session, card);
}

// ── empty-state + starters (per session) ──
function removeSurgeonEmpty(session) {
  session.logEl.querySelector(".surgeon-empty")?.remove();
}

function renderSurgeonEmpty(session) {
  if (session.history.length || session.logEl.querySelector(".surgeon-message, .surgeon-tool")) return;
  const empty = document.createElement("div");
  empty.className = "surgeon-empty";
  empty.innerHTML = `
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2c-2.3 0-3.6.9-4.3 2.1-.5-.1-1-.1-1.5-.1C3.4 4 2 5.6 2 8.2v.3C1 9 .5 9.9.5 11.2v2.1c0 2 1 3.4 2.8 4.2C5.1 18.9 8.2 20 12 20s6.9-1.1 8.7-2.5c1.8-.8 2.8-2.2 2.8-4.2v-2.1c0-1.3-.5-2.2-1.5-2.7v-.3C22 5.6 20.6 4 17.8 4c-.5 0-1 0-1.5.1C15.6 2.9 14.3 2 12 2Z"/>
    </svg>
    <h2>GitHub Copilot, in your Brainstem</h2>
    The full Copilot agent loop: files, shell, tests, one-chat capability
    injection, visible UI control, screenshots, and recorded demos. Open more
    chats with <b>+</b> to build several agents at once on the same Brainstem.
    <div class="surgeon-caps">
      <span>run commands</span><span>read/write files</span><span>test Brainstem</span>
    </div>
    <div class="surgeon-starters"></div>
  `;
  const list = empty.querySelector(".surgeon-starters");
  for (const starter of SURGEON_STARTERS) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = starter.label;
    if (starter.className) button.classList.add(starter.className);
    if (starter.tour) button.dataset.showModeTour = "true";
    button.addEventListener("click", () => {
      if (starter.tour) {
        window.dispatchEvent(new CustomEvent("rapp-beta:show-mode-tour"));
        return;
      }
      runSurgeon(session, starter.prompt || starter.label);
    });
    list.appendChild(button);
  }
  session.logEl.appendChild(empty);
}

// ── session lifecycle ──
function newSurgeonSession(activate = true) {
  const id = ++surgeonSeq;
  const log = document.createElement("div");
  log.className = "surgeon-session";
  surgeonLog.appendChild(log);
  const session = {
    id,
    defaultTitle: "New chat",
    title: "New chat",
    history: [],
    running: false,
    logEl: log,
    tileEl: null,
    streamEl: null,
    thinkEl: null,
    tools: [],
  };
  surgeonSessions.push(session);
  renderSurgeonEmpty(session);
  if (surgeonHerd) {
    addSurgeonTile(session);
    renderSurgeonTabs();
  } else if (activate) {
    setActiveSurgeon(id);
    surgeonInput?.focus();
  }
  saveSurgeonSessions();
  return session;
}

function restoreSurgeonSession(data) {
  const log = document.createElement("div");
  log.className = "surgeon-session";
  surgeonLog.appendChild(log);
  const session = {
    id: data.id,
    defaultTitle: "New chat",
    title: data.title || "New chat",
    history: Array.isArray(data.history) ? data.history : [],
    running: false,
    logEl: log,
    tileEl: null,
    streamEl: null,
    thinkEl: null,
    tools: [],
  };
  surgeonSessions.push(session);
  if (surgeonSeq < session.id) surgeonSeq = session.id;
  for (const message of session.history) {
    if (["user", "assistant"].includes(message.role)) {
      const bubble = document.createElement("div");
      bubble.className = `surgeon-message ${message.role}`;
      bubble.textContent = String(message.content || "");
      log.appendChild(bubble);
    }
  }
  if (!session.history.length) renderSurgeonEmpty(session);
  return session;
}

function setActiveSurgeon(id) {
  surgeonActiveId = id;
  for (const s of surgeonSessions) {
    s.logEl.style.display = s.id === id ? "" : "none";
  }
  renderSurgeonTabs();
  syncSurgeonComposer();
  const active = activeSurgeon();
  if (active) scrollSurgeon(active);
}

function closeSurgeonSession(id) {
  const index = surgeonSessions.findIndex((s) => s.id === id);
  if (index < 0) return;
  const session = surgeonSessions[index];
  session.tileEl?.remove();
  session.logEl.remove();
  surgeonSessions.splice(index, 1);
  void window.brainstemBeta.surgeonClose(id);
  if (!surgeonSessions.length) {
    newSurgeonSession();
    return;
  }
  const fallback = surgeonSessions[Math.max(0, index - 1)].id;
  if (surgeonHerd) {
    if (surgeonActiveId === id) surgeonActiveId = fallback;
    renderSurgeonTabs();
  } else if (surgeonActiveId === id) {
    setActiveSurgeon(fallback);
  } else {
    renderSurgeonTabs();
  }
  saveSurgeonSessions();
}

function refreshSurgeon(session) {
  renderSurgeonTabs();
  updateSurgeonTile(session);
  if (session.id === surgeonActiveId) syncSurgeonComposer();
  saveSurgeonSessions();
}

function renderSurgeonTabs() {
  if (!surgeonTabs) return;
  surgeonTabs.replaceChildren();
  for (const s of surgeonSessions) {
    const tab = document.createElement("button");
    tab.type = "button";
    tab.className = `surgeon-tab${s.id === surgeonActiveId ? " active" : ""}`;
    const title = s.title.length > 22 ? `${s.title.slice(0, 22)}…` : s.title;
    tab.innerHTML = (s.running ? '<span class="sp"></span>' : "")
      + `<span class="tt">${escapeHtml(title)}</span>`
      + (surgeonSessions.length > 1 ? '<span class="cl" title="Close chat">×</span>' : "");
    tab.addEventListener("click", (event) => {
      if (event.target.classList.contains("cl")) {
        event.stopPropagation();
        closeSurgeonSession(s.id);
      } else {
        setActiveSurgeon(s.id);
      }
    });
    surgeonTabs.appendChild(tab);
  }
  const add = document.createElement("button");
  add.type = "button";
  add.className = "surgeon-new";
  add.textContent = "+";
  add.title = "New Copilot chat (same Brainstem)";
  add.addEventListener("click", () => newSurgeonSession());
  surgeonTabs.appendChild(add);
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value == null ? "" : String(value);
  return div.innerHTML;
}

// ── herd view: every session as a live tile in a grid ──
function ensureSurgeonHerdDom() {
  if (surgeonHerdEl) return;
  const herd = document.createElement("aside");
  herd.id = "surgeon-herd";
  herd.setAttribute("aria-label", "GitHub Copilot herd — several chats at once");
  herd.innerHTML = `
    <div class="hbar">
      <span class="surgeon-badge">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
          <path d="M12 2c-2.3 0-3.6.9-4.3 2.1-.5-.1-1-.1-1.5-.1C3.4 4 2 5.6 2 8.2v.3C1 9 .5 9.9.5 11.2v2.1c0 2 1 3.4 2.8 4.2C5.1 18.9 8.2 20 12 20s6.9-1.1 8.7-2.5c1.8-.8 2.8-2.2 2.8-4.2v-2.1c0-1.3-.5-2.2-1.5-2.7v-.3C22 5.6 20.6 4 17.8 4c-.5 0-1 0-1.5.1C15.6 2.9 14.3 2 12 2Z"/>
        </svg>
      </span>
      <span class="t">GitHub Copilot · Herd</span>
      <span class="sub">several agents, one Brainstem</span>
      <button class="hnew" type="button">+ New chat</button>
      <button class="hclose" type="button">Dock ▸</button>
    </div>
    <div class="herd-grid"></div>
  `;
  document.body.appendChild(herd);
  surgeonHerdEl = herd;
  surgeonGridEl = herd.querySelector(".herd-grid");
  herd.querySelector(".hnew").addEventListener("click", () => newSurgeonSession());
  herd.querySelector(".hclose").addEventListener("click", exitSurgeonHerd);
}

function surgeonTileFor(session) {
  const tile = document.createElement("div");
  tile.className = "herd-tile";
  tile.innerHTML = `
    <div class="hh">
      <span class="tt"></span>
      <span class="hst">ready</span>
      <span class="cl" title="Close chat">×</span>
    </div>
    <div class="htrans"></div>
    <div class="hcomp">
      <textarea rows="1" placeholder="Message this Copilot…"></textarea>
      <button type="button" title="Send">➤</button>
    </div>
  `;
  tile.querySelector(".htrans").appendChild(session.logEl);
  session.logEl.style.display = "";
  const textarea = tile.querySelector(".hcomp textarea");
  const button = tile.querySelector(".hcomp button");
  const send = () => {
    const text = textarea.value.trim();
    if (!text || session.running) return;
    textarea.value = "";
    textarea.style.height = "auto";
    runSurgeon(session, text);
  };
  button.addEventListener("click", send);
  textarea.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      send();
    }
  });
  textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 90)}px`;
  });
  tile.querySelector(".cl").addEventListener("click", () => closeSurgeonSession(session.id));
  session.tileEl = tile;
  updateSurgeonTile(session);
  return tile;
}

function updateSurgeonTile(session) {
  if (!session.tileEl) return;
  session.tileEl.querySelector(".tt").textContent = session.title;
  const status = session.tileEl.querySelector(".hst");
  const state = session.running ? "working" : (session.history.length ? "done" : "ready");
  status.textContent = state;
  status.className = `hst ${state}`;
  const button = session.tileEl.querySelector(".hcomp button");
  if (button) button.disabled = session.running;
}

function addSurgeonTile(session) {
  ensureSurgeonHerdDom();
  surgeonGridEl.appendChild(surgeonTileFor(session));
}

function enterSurgeonHerd() {
  ensureSurgeonHerdDom();
  surgeonGridEl.replaceChildren();
  for (const s of surgeonSessions) {
    s.tileEl = null;
    surgeonGridEl.appendChild(surgeonTileFor(s));
  }
  surgeonHerdEl.classList.add("open");
  document.body.classList.add("surgeon-herd-open");
  surgeonHerd = true;
  surgeonHerdBtn?.classList.add("on");
}

function exitSurgeonHerd() {
  surgeonHerd = false;
  surgeonHerdEl?.classList.remove("open");
  document.body.classList.remove("surgeon-herd-open");
  surgeonHerdBtn?.classList.remove("on");
  for (const s of surgeonSessions) {
    s.tileEl = null;
    surgeonLog.appendChild(s.logEl);
  }
  setActiveSurgeon(surgeonActiveId);
}

function toggleSurgeonHerd() {
  if (surgeonHerd) exitSurgeonHerd();
  else enterSurgeonHerd();
}

// ── running a turn (per session, parallel across sessions) ──
async function runSurgeon(session, prompt) {
  const text = String(prompt || "").trim();
  if (!text || session.running) return;
  removeSurgeonEmpty(session);
  if (session.title === session.defaultTitle) session.title = text.slice(0, 40);
  session.running = true;
  session.streamEl = null;
  addSurgeonBubble(session, "user", text);
  showSurgeonThinking(session);
  refreshSurgeon(session);
  try {
    await window.brainstemBeta.surgeonSend(session.id, text);
  } catch (cause) {
    hideSurgeonThinking(session);
    if (!session.streamEl) {
      addSurgeonBubble(session, "error", String(cause?.message || cause || "Brain Surgeon failed."), false);
    }
  } finally {
    session.running = false;
    session.streamEl = null;
    refreshSurgeon(session);
  }
}

function submitSurgeon() {
  const prompt = surgeonInput.value.trim();
  if (!prompt) return;
  const session = activeSurgeon() || newSurgeonSession();
  if (session.running) return;   // this chat is busy — open a new tab (+) to run in parallel
  surgeonInput.value = "";
  surgeonInput.style.height = "auto";
  runSurgeon(session, prompt);
}

function syncSurgeonComposer() {
  const session = activeSurgeon();
  const busy = !!(session && session.running);
  if (surgeonSend) {
    surgeonSend.disabled = busy;
    surgeonSend.textContent = busy ? "Working" : "Build";
  }
}

// Reset the ACTIVE chat's transcript and its main-process session.
function clearSurgeonUi() {
  const session = activeSurgeon();
  if (!session) return;
  hideSurgeonThinking(session);
  session.logEl.replaceChildren();
  session.history = [];
  session.title = session.defaultTitle;
  session.streamEl = null;
  session.tools = [];
  session.running = false;
  surgeonInput.value = "";
  surgeonInput.style.height = "auto";
  renderSurgeonEmpty(session);
  refreshSurgeon(session);
}

function handleSurgeonEvent(event) {
  if (!event) return;
  const session = surgeonSessions.find((s) => s.id === event.sessionId)
    || surgeonSessions.find((s) => s.id === surgeonActiveId);
  if (!session) return;
  if (event.type === "response-start") {
    showSurgeonThinking(session);
  } else if (event.type === "delta") {
    hideSurgeonThinking(session);
    if (!session.streamEl) session.streamEl = addSurgeonBubble(session, "assistant", "", false);
    session.streamEl.textContent += event.text || "";
    scrollSurgeon(session);
  } else if (event.type === "tool-start") {
    hideSurgeonThinking(session);
    addSurgeonTool(session, event.toolName || "tool", event.toolCallId);
    showSurgeonThinking(session);
  } else if (event.type === "tool-complete") {
    finishSurgeonTool(session, event.toolName || "tool", event.toolCallId, event.success !== false);
    void refreshAgentExplorer();
  } else if (event.type === "artifact") {
    addSurgeonArtifact(session, event.artifact);
  } else if (event.type === "lease") {
    addSurgeonBubble(session, "assistant", event.message || "Temporary capability leased.", false);
  } else if (event.type === "done") {
    hideSurgeonThinking(session);
    const finalText = String(event.content || "").trim();
    if (!session.streamEl) {
      session.streamEl = addSurgeonBubble(session, "assistant", finalText || "(done)", false);
    } else if (finalText) {
      session.streamEl.textContent = finalText;
    }
    session.history.push({ role: "assistant", content: session.streamEl.textContent });
    session.streamEl = null;
    saveSurgeonSessions();
  } else if (event.type === "error") {
    hideSurgeonThinking(session);
    addSurgeonBubble(session, "error", event.message || "Brain Surgeon failed.", false);
  } else if (event.type === "reset") {
    // A main-process reset for this session — already cleared in clearSurgeonUi.
  }
}

function initSurgeonSessions() {
  let saved = null;
  try {
    saved = JSON.parse(localStorage.getItem(surgeonHistoryKey) || "null");
  } catch {
    saved = null;
  }
  if (saved && Array.isArray(saved.sessions) && saved.sessions.length) {
    saved.sessions.forEach(restoreSurgeonSession);
    const active = surgeonSessions.some((s) => s.id === saved.active) ? saved.active : surgeonSessions[0].id;
    setActiveSurgeon(active);
  } else {
    newSurgeonSession();
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
  const session = activeSurgeon();
  clearSurgeonUi();
  try {
    await window.brainstemBeta.surgeonReset(session ? session.id : 1);
  } catch (cause) {
    if (session) {
      addSurgeonBubble(
        session,
        "error",
        `Could not reset Brain Surgeon: ${String(cause?.message || cause)}`,
        false,
      );
    }
  }
});
surgeonHerdBtn.addEventListener("click", toggleSurgeonHerd);
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

initSurgeonSessions();
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
