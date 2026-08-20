import {
  chmodSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  writeFileSync,
} from "node:fs";
import { randomUUID } from "node:crypto";
import path from "node:path";

import {
  DEFAULT_APRIL_FOOLS,
  normalizeAprilFoolsSettings,
} from "./card-tables.mjs";

export const CHAT_CARD_SCHEMA = "rapp-chat-card/1.0";
export const MAX_CHAT_CARD_TURNS = 200;
export const MAX_CHAT_CARD_BYTES = 256 * 1024;
export const CHAT_CARD_UNDO_MS = 10_000;
const CHAT_CARD_STATUSES = new Set([
  "parked",
  "racing",
  "primary",
  "folded",
]);
const CHAT_CARD_ID = /^card-[a-z0-9][a-z0-9-]{5,120}$/;

function settingsPath(betaHome) {
  if (!betaHome) throw new Error("A beta home is required for chat card settings.");
  return path.join(betaHome, "settings.json");
}

function readSettings(betaHome) {
  const file = settingsPath(betaHome);
  if (!existsSync(file)) return {};
  let value;
  try {
    value = JSON.parse(readFileSync(file, "utf8"));
  } catch (error) {
    throw new Error(`Invalid Frontier settings at ${file}: ${error.message}`);
  }
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`Invalid Frontier settings at ${file}.`);
  }
  return value;
}

function writeSettings(betaHome, value) {
  const file = settingsPath(betaHome);
  mkdirSync(betaHome, { recursive: true, mode: 0o700 });
  try {
    chmodSync(betaHome, 0o700);
  } catch {
    // Windows does not expose POSIX directory modes.
  }
  const temporary = `${file}.${process.pid}.${Date.now()}.tmp`;
  writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, {
    mode: 0o600,
  });
  renameSync(temporary, file);
  try {
    chmodSync(file, 0o600);
  } catch {
    // Windows does not expose POSIX file modes.
  }
  return file;
}

function environmentOverride(env) {
  if (env.RAPP_APRIL_FOOLS === "1") return true;
  if (env.RAPP_APRIL_FOOLS === "0") return false;
  return null;
}

export function readAprilFoolsSettings({
  betaHome,
  env = process.env,
} = {}) {
  const settings = readSettings(betaHome);
  const storedAprilFools = normalizeAprilFoolsSettings(
    settings.aprilFools || DEFAULT_APRIL_FOOLS,
  );
  const override = environmentOverride(env);
  const aprilFools = {
    ...storedAprilFools,
    on: override === null ? storedAprilFools.on : override,
  };
  return {
    aprilFools,
    aprilFoolsOverridden: override !== null,
    file: settingsPath(betaHome),
    storedAprilFools,
  };
}

export function writeAprilFoolsSettings({
  aprilFools,
  betaHome,
} = {}) {
  const settings = readSettings(betaHome);
  settings.aprilFools = normalizeAprilFoolsSettings({
    ...DEFAULT_APRIL_FOOLS,
    ...(settings.aprilFools || {}),
    ...(aprilFools || {}),
  });
  const file = writeSettings(betaHome, settings);
  return { aprilFools: settings.aprilFools, file };
}

export function changeAprilFoolsSettings({
  apply,
  aprilFools,
  betaHome,
  env = process.env,
} = {}) {
  writeAprilFoolsSettings({ aprilFools, betaHome });
  const effective = readAprilFoolsSettings({ betaHome, env });
  apply?.(effective);
  return effective;
}

export function parseAprilFoolsCommand(message) {
  return typeof message === "string" && message.trim() === "april fools"
    ? { action: "toggle-april-fools", original: message }
    : null;
}

function cardsPath(betaHome) {
  if (!betaHome) throw new Error("A beta home is required for chat cards.");
  return path.join(betaHome, "cards");
}

function safeCardId(value) {
  const id = String(value || "");
  if (!CHAT_CARD_ID.test(id)) {
    throw new Error("A valid chat card id is required.");
  }
  return id;
}

function cardPath(betaHome, id) {
  return path.join(cardsPath(betaHome), `${safeCardId(id)}.json`);
}

function timestamp(value, fallback) {
  const parsed = Date.parse(String(value || ""));
  return Number.isFinite(parsed) ? new Date(parsed).toISOString() : fallback;
}

function cardTitle(turns, value) {
  const requested = String(value || "").trim();
  const firstUser = turns.find((turn) => turn.role === "user")?.text || "";
  const title = requested || firstUser.split(/\r?\n/, 1)[0].trim() || "Parked chat";
  return [...title].slice(0, 60).join("");
}

function normalizeTurn(value, fallbackAt) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Every chat card turn must be an object.");
  }
  if (!["user", "assistant"].includes(value.role)) {
    throw new Error("Chat card turns must use the user or assistant role.");
  }
  return {
    role: value.role,
    text: String(value.text || ""),
    html: String(value.html || ""),
    at: timestamp(value.at, fallbackAt),
    ...(value.pending === true ? { pending: true } : {}),
  };
}

function normalizeHistoryMessage(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Every chat card history message must be an object.");
  }
  if (!["user", "assistant"].includes(value.role)) {
    throw new Error("Chat card history must use the user or assistant role.");
  }
  return {
    role: value.role,
    content: String(value.content || ""),
  };
}

function normalizeRoute(value) {
  const route = value && typeof value === "object" && !Array.isArray(value)
    ? value
    : {};
  return {
    url: String(route.url || ""),
    rappid: String(route.rappid || ""),
    compositionHash: String(route.compositionHash || ""),
    model: String(route.model || "auto"),
  };
}

function normalizeTable(value) {
  const table = value && typeof value === "object" && !Array.isArray(value)
    ? value
    : {};
  const seat = Number(table.seat);
  return {
    seat: Number.isInteger(seat) && seat >= 1 && seat <= 12 ? seat : null,
    faceUp: table.faceUp !== false,
  };
}

export function normalizeChatCard(value, {
  id,
  now = new Date().toISOString(),
} = {}) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("A chat card must be an object.");
  }
  const cardId = safeCardId(id || value.id);
  const turns = Array.isArray(value.turns)
    ? value.turns.map((turn) => normalizeTurn(turn, now))
    : [];
  if (turns.length > MAX_CHAT_CARD_TURNS) {
    throw new Error(
      `Chat cards are limited to ${MAX_CHAT_CARD_TURNS} transcript turns.`,
    );
  }
  const history = Array.isArray(value.history)
    ? value.history.map(normalizeHistoryMessage)
    : [];
  const status = CHAT_CARD_STATUSES.has(value.status)
    ? value.status
    : "parked";
  const createdAt = timestamp(value.createdAt, now);
  return {
    schema: CHAT_CARD_SCHEMA,
    id: cardId,
    title: cardTitle(turns, value.title),
    createdAt,
    parkedAt: timestamp(value.parkedAt, now),
    route: normalizeRoute(value.route),
    turns,
    history,
    status,
    table: normalizeTable(value.table),
  };
}

function serializeCard(card) {
  const serialized = `${JSON.stringify(card, null, 2)}\n`;
  const size = Buffer.byteLength(serialized);
  if (size > MAX_CHAT_CARD_BYTES) {
    throw new Error(
      `Chat cards are limited to ${MAX_CHAT_CARD_BYTES} bytes; this card is ${size} bytes.`,
    );
  }
  return serialized;
}

function atomicWriteCard(betaHome, card) {
  const directory = cardsPath(betaHome);
  mkdirSync(directory, { recursive: true, mode: 0o700 });
  try {
    chmodSync(directory, 0o700);
  } catch {
    // Windows does not expose POSIX directory modes.
  }
  const file = cardPath(betaHome, card.id);
  const temporary = `${file}.${process.pid}.${Date.now()}.tmp`;
  writeFileSync(temporary, serializeCard(card), { mode: 0o600 });
  renameSync(temporary, file);
  try {
    chmodSync(file, 0o600);
  } catch {
    // Windows does not expose POSIX file modes.
  }
  return file;
}

function lastQuestion(card) {
  const question = [...card.turns]
    .reverse()
    .find((turn) => turn.role === "user")
    ?.text
    .trim();
  return question?.endsWith("?") ? question : null;
}

export class ChatCardStore {
  constructor({
    betaHome,
    idFactory = () => (
      `card-${Date.now().toString(36)}-${randomUUID().slice(0, 8)}`
    ),
    now = () => new Date(),
  } = {}) {
    if (!betaHome) throw new Error("A beta home is required for chat cards.");
    this.betaHome = betaHome;
    this.idFactory = idFactory;
    this.now = now;
    this.undoEntries = new Map();
  }

  nowIso() {
    return this.now().toISOString();
  }

  list() {
    const directory = cardsPath(this.betaHome);
    if (!existsSync(directory)) return [];
    return readdirSync(directory)
      .filter((name) => /^card-[a-z0-9][a-z0-9-]{5,120}\.json$/.test(name))
      .map((name) => this.read(name.slice(0, -5)))
      .sort((left, right) => (
        right.parkedAt.localeCompare(left.parkedAt)
        || left.id.localeCompare(right.id)
      ));
  }

  read(id) {
    const file = cardPath(this.betaHome, id);
    if (!existsSync(file)) {
      throw new Error(`Chat card ${safeCardId(id)} was not found.`);
    }
    let value;
    try {
      value = JSON.parse(readFileSync(file, "utf8"));
    } catch (error) {
      throw new Error(`Chat card ${id} is invalid: ${error.message}`);
    }
    if (value?.schema !== CHAT_CARD_SCHEMA) {
      throw new Error(`Chat card ${id} does not use ${CHAT_CARD_SCHEMA}.`);
    }
    return normalizeChatCard(value, { id });
  }

  nextSeat(excludeId = null) {
    const occupied = new Set(this.list()
      .filter((card) => card.id !== excludeId && card.status !== "folded")
      .map((card) => card.table.seat)
      .filter(Boolean));
    for (let seat = 1; seat <= 12; seat += 1) {
      if (!occupied.has(seat)) return seat;
    }
    return null;
  }

  save(value) {
    const card = normalizeChatCard(value, {
      id: value.id,
      now: this.nowIso(),
    });
    atomicWriteCard(this.betaHome, card);
    return card;
  }

  park(value) {
    const now = this.nowIso();
    const id = value?.id || this.idFactory();
    const card = normalizeChatCard({
      ...value,
      id,
      createdAt: value?.createdAt || now,
      parkedAt: now,
      status: value?.status === "racing" ? "racing" : "parked",
      table: {
        ...(value?.table || {}),
        seat: value?.table?.seat || this.nextSeat(id),
      },
    }, { id, now });
    atomicWriteCard(this.betaHome, card);
    return card;
  }

  complete(id, {
    at,
    html = "",
    reply,
  } = {}) {
    const card = this.read(id);
    const completedAt = timestamp(at, this.nowIso());
    const pending = [...card.turns]
      .reverse()
      .find((turn) => turn.role === "assistant" && turn.pending);
    if (pending) {
      pending.text = String(reply || "");
      pending.html = String(html || "");
      pending.at = completedAt;
      delete pending.pending;
    } else {
      if (card.turns.length >= MAX_CHAT_CARD_TURNS) {
        throw new Error(
          `Chat cards are limited to ${MAX_CHAT_CARD_TURNS} transcript turns.`,
        );
      }
      card.turns.push({
        role: "assistant",
        text: String(reply || ""),
        html: String(html || ""),
        at: completedAt,
      });
    }
    card.history.push({
      role: "assistant",
      content: String(reply || ""),
    });
    return this.save(card);
  }

  fold(id) {
    const card = this.read(id);
    const undoUntil = this.now().getTime() + CHAT_CARD_UNDO_MS;
    this.undoEntries.set(card.id, {
      status: card.status,
      faceUp: card.table.faceUp,
      undoUntil,
    });
    card.status = "folded";
    card.table.faceUp = false;
    return {
      card: this.save(card),
      undoUntil: new Date(undoUntil).toISOString(),
    };
  }

  undo(id) {
    const cardId = safeCardId(id);
    const entry = this.undoEntries.get(cardId);
    if (!entry || this.now().getTime() > entry.undoUntil) {
      this.undoEntries.delete(cardId);
      throw new Error("The 10 second fold undo window has expired.");
    }
    const card = this.read(cardId);
    card.status = entry.status;
    card.table.faceUp = entry.faceUp;
    this.undoEntries.delete(cardId);
    return this.save(card);
  }

  wake(id) {
    const target = this.read(id);
    const racing = target.status === "racing";
    for (const card of this.list()) {
      if (card.id === target.id) continue;
      if (racing && card.status === "racing") {
        card.status = "folded";
        card.table.faceUp = false;
        this.save(card);
      } else if (card.status === "primary") {
        card.status = "parked";
        this.save(card);
      }
    }
    target.status = "primary";
    target.table.faceUp = true;
    return this.save(target);
  }

  race(id) {
    const source = this.read(id);
    const question = lastQuestion(source);
    if (!question) {
      throw new Error("Race requires a card whose last user turn is a question.");
    }
    source.status = "racing";
    this.save(source);
    const now = this.nowIso();
    const contender = this.park({
      title: `${source.title} race`,
      route: source.route,
      turns: [
        {
          role: "user",
          text: question,
          html: "",
          at: now,
        },
        {
          role: "assistant",
          text: "Waiting for reply...",
          html: "",
          at: now,
          pending: true,
        },
      ],
      history: [{ role: "user", content: question }],
      status: "racing",
      table: { faceUp: true },
    });
    return {
      contender,
      question,
      source: this.read(source.id),
    };
  }
}

export function registerChatCardIpc({
  assertTrustedIpc,
  ipcMain,
  isEnabled,
  store,
} = {}) {
  if (!ipcMain?.handle || !(store instanceof ChatCardStore)) {
    throw new Error("Chat card IPC requires ipcMain and a ChatCardStore.");
  }
  function guard(event) {
    assertTrustedIpc?.(event);
    if (!isEnabled?.()) {
      throw new Error("April Fools card table is off.");
    }
  }
  ipcMain.handle("beta:cards-list", (event) => {
    guard(event);
    return store.list();
  });
  ipcMain.handle("beta:cards-park", (event, card) => {
    guard(event);
    return store.park(card);
  });
  ipcMain.handle("beta:cards-wake", (event, id) => {
    guard(event);
    return store.wake(id);
  });
  ipcMain.handle("beta:cards-fold", (event, id) => {
    guard(event);
    return store.fold(id);
  });
  ipcMain.handle("beta:cards-undo", (event, id) => {
    guard(event);
    return store.undo(id);
  });
  ipcMain.handle("beta:cards-race", (event, id) => {
    guard(event);
    return store.race(id);
  });
  ipcMain.handle("beta:cards-complete", (event, id, completion) => {
    guard(event);
    return store.complete(id, completion || {});
  });
}

function installAprilFoolsFrameBridge(settings) {
  const prior = window.__rappBetaAprilFoolsBridge;
  if (prior) {
    prior.update(settings);
    return true;
  }

  let current = settings;
  let activeHistory = null;
  let internalClear = false;
  let lastRequest = null;
  let nextRaceCardId = null;
  const pendingRequests = new Map();
  const upstreamFetch = window.fetch;

  function removeToggle() {
    document.getElementById("beta-april-fools-toggle")?.remove();
  }

  function renderToggle() {
    const panel = document.getElementById("beta-app-panel");
    if (!panel) return false;
    let button = document.getElementById("beta-april-fools-toggle");
    if (!button) {
      button = document.createElement("button");
      button.id = "beta-april-fools-toggle";
      button.className = "beta-panel-btn";
      button.type = "button";
      button.textContent = "April Fools: Card Table";
      button.addEventListener("click", (event) => {
        event.stopPropagation();
        window.parent.postMessage({
          type: "rapp-beta:set-april-fools",
          aprilFools: { on: !current.on },
        }, "*");
      });
      const updateButton = document.getElementById("beta-check-updates");
      panel.insertBefore(button, updateButton || null);
    }
    button.setAttribute("aria-pressed", String(Boolean(current.on)));
    button.textContent = `April Fools: Card Table ${current.on ? "✓" : ""}`.trim();
    return true;
  }

  function sanitizedHtml(element) {
    const container = document.createElement("div");
    const sanitizer = typeof window.sanitizeMarkdownFragment === "function"
      ? window.sanitizeMarkdownFragment
      : null;
    if (sanitizer) {
      container.appendChild(sanitizer(String(element?.innerHTML || "")));
    } else {
      container.textContent = String(element?.textContent || "");
    }
    return container.innerHTML;
  }

  function replyHtml(text) {
    const source = typeof window.marked?.parse === "function"
      ? window.marked.parse(String(text || ""))
      : String(text || "");
    const holder = document.createElement("div");
    if (typeof window.sanitizeMarkdownFragment === "function") {
      holder.appendChild(window.sanitizeMarkdownFragment(source));
    } else {
      holder.textContent = String(text || "");
    }
    return holder.innerHTML;
  }

  function transcriptTurns() {
    const now = new Date().toISOString();
    return [...document.querySelectorAll(
      "#chat .msg.user:not([data-rapp-provisional]), "
        + "#chat .msg.assistant:not(.typing-indicator):not([data-rapp-provisional])",
    )].map((message) => {
      const bubble = message.querySelector(".bubble") || message;
      return {
        role: message.classList.contains("user") ? "user" : "assistant",
        text: String(bubble.textContent || "").trim(),
        html: sanitizedHtml(bubble),
        at: now,
      };
    }).filter((turn) => turn.text);
  }

  function pendingHistory() {
    const latest = [...pendingRequests.values()].at(-1);
    if (latest) {
      return [
        ...latest.effectiveHistory,
        { role: "user", content: latest.userInput },
      ];
    }
    return activeHistory ? structuredClone(activeHistory) : [];
  }

  function captureCard() {
    const turns = transcriptTurns();
    const pending = [...pendingRequests.values()];
    for (const request of pending) {
      const alreadyRendered = turns.at(-1)?.role === "assistant";
      if (!alreadyRendered) {
        turns.push({
          role: "assistant",
          text: "Waiting for reply...",
          html: "",
          at: request.startedAt,
          pending: true,
        });
      }
    }
    const model = document.getElementById("model-select")?.value || "auto";
    return {
      title: turns.find((turn) => turn.role === "user")?.text || "Parked chat",
      turns,
      history: lastRequest?.completedHistory
        ? structuredClone(lastRequest.completedHistory)
        : pendingHistory(),
      model,
      pending: pending.length > 0,
    };
  }

  function markPendingForCard(cardId) {
    activeHistory = null;
    for (const request of pendingRequests.values()) {
      request.parkedCardId = cardId;
      request.preserveOnClear = true;
    }
  }

  function clearKernel({ preservePending = false } = {}) {
    if (preservePending) {
      for (const request of pendingRequests.values()) {
        request.preserveOnClear = true;
      }
    }
    const clear = [...document.querySelectorAll("button")]
      .find((button) => button.textContent.trim() === "Clear");
    if (!clear) throw new Error("The Brainstem Clear button is unavailable.");
    internalClear = true;
    try {
      clear.click();
    } finally {
      internalClear = false;
    }
  }

  function renderTranscript(card) {
    clearKernel();
    lastRequest = null;
    activeHistory = Array.isArray(card.history)
      ? structuredClone(card.history)
      : [];
    const chat = document.getElementById("chat");
    if (!chat) throw new Error("The Brainstem transcript is unavailable.");
    for (const turn of card.turns || []) {
      if (turn.pending) continue;
      let message = null;
      if (typeof window.appendMsg === "function") {
        message = window.appendMsg(turn.role, turn.text);
      } else {
        message = document.createElement("div");
        message.className = `msg ${turn.role}`;
        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.textContent = turn.text;
        message.appendChild(bubble);
        chat.appendChild(message);
      }
      const bubble = message?.querySelector?.(".bubble");
      if (bubble && turn.html) {
        const holder = document.createElement("div");
        holder.innerHTML = String(turn.html);
        bubble.replaceChildren(
          typeof window.sanitizeMarkdownFragment === "function"
            ? window.sanitizeMarkdownFragment(holder.innerHTML)
            : document.createTextNode(turn.text),
        );
      }
    }
    chat.classList.add("has-messages");
    chat.scrollTop = chat.scrollHeight;
    return true;
  }

  function prepareRace(cardId, question) {
    clearKernel();
    activeHistory = null;
    nextRaceCardId = cardId;
    const input = document.getElementById("input");
    if (!input) throw new Error("The Brainstem composer is unavailable.");
    input.value = String(question || "");
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.focus();
  }

  function streamReply(text) {
    let reply = "";
    for (const frame of String(text || "").split(/\r?\n\r?\n/)) {
      const data = frame.split(/\r?\n/)
        .find((line) => line.startsWith("data:"));
      if (!data) continue;
      try {
        const value = JSON.parse(data.slice(5).trim());
        if (value.type === "done") {
          reply = value.response == null ? reply : String(value.response);
        }
      } catch {
        // Non-JSON keepalive and [DONE] frames do not carry a reply.
      }
    }
    return reply;
  }

  async function responseReply(response, pathname) {
    const text = await response.clone().text();
    if (pathname === "/chat/stream") return streamReply(text);
    try {
      const value = JSON.parse(text);
      return String(value.response || "");
    } catch {
      return "";
    }
  }

  async function observeCompletion(request, response, pathname) {
    try {
      const reply = await responseReply(response, pathname);
      if (!reply) return;
      request.completedHistory = [
        ...request.effectiveHistory,
        { role: "user", content: request.userInput },
        { role: "assistant", content: reply },
      ];
      lastRequest = request;
      if (request.parkedCardId) {
        window.parent.postMessage({
          type: "rapp-beta:card-pending-complete",
          id: request.parkedCardId,
          completion: {
            reply,
            html: replyHtml(reply),
            at: new Date().toISOString(),
          },
        }, "*");
      }
    } finally {
      request.detachAbort?.();
      pendingRequests.delete(request.id);
    }
  }

  async function cardFetch(resource, options = {}) {
    let target;
    try {
      const raw = resource instanceof Request ? resource.url : String(resource);
      target = new URL(raw, window.location.href);
    } catch {
      return Reflect.apply(upstreamFetch, window, [resource, options]);
    }
    const method = String(
      options.method || (resource instanceof Request ? resource.method : "GET"),
    ).toUpperCase();
    const isChat = method === "POST"
      && (target.pathname === "/chat" || target.pathname === "/chat/stream")
      && typeof options.body === "string";
    if (!isChat) {
      return Reflect.apply(upstreamFetch, window, [resource, options]);
    }
    let body;
    try {
      body = JSON.parse(options.body);
    } catch {
      return Reflect.apply(upstreamFetch, window, [resource, options]);
    }
    if (typeof body.user_input !== "string") {
      return Reflect.apply(upstreamFetch, window, [resource, options]);
    }

    const incomingHistory = Array.isArray(body.conversation_history)
      ? body.conversation_history
      : [];
    const effectiveHistory = activeHistory
      ? [...structuredClone(activeHistory), ...incomingHistory]
      : incomingHistory;
    body.conversation_history = effectiveHistory;

    const originalSignal = options.signal
      || (resource instanceof Request ? resource.signal : null);
    const controller = new AbortController();
    const request = {
      completedHistory: null,
      effectiveHistory: structuredClone(effectiveHistory),
      id: window.crypto.randomUUID(),
      parkedCardId: nextRaceCardId,
      preserveOnClear: Boolean(nextRaceCardId),
      startedAt: new Date().toISOString(),
      userInput: body.user_input,
    };
    nextRaceCardId = null;
    const forwardAbort = () => {
      if (!request.preserveOnClear) controller.abort(originalSignal?.reason);
    };
    if (originalSignal) {
      if (originalSignal.aborted) forwardAbort();
      else originalSignal.addEventListener("abort", forwardAbort, { once: true });
      request.detachAbort = () => (
        originalSignal.removeEventListener("abort", forwardAbort)
      );
    }
    pendingRequests.set(request.id, request);
    lastRequest = request;
    const nextOptions = {
      ...options,
      body: JSON.stringify(body),
      signal: controller.signal,
    };
    try {
      const response = await Reflect.apply(
        upstreamFetch,
        window,
        [resource, nextOptions],
      );
      void observeCompletion(request, response, target.pathname);
      return response;
    } catch (error) {
      request.detachAbort?.();
      pendingRequests.delete(request.id);
      throw error;
    }
  }

  function handleClear(event) {
    const button = event.target?.closest?.("button");
    if (
      !internalClear
      && button
      && button.textContent.trim() === "Clear"
    ) {
      activeHistory = null;
      lastRequest = null;
    }
  }

  function disable() {
    removeToggle();
    document.removeEventListener("click", handleClear, true);
    window.removeEventListener("message", receive);
    if (window.fetch === cardFetch) window.fetch = upstreamFetch;
    activeHistory = null;
    pendingRequests.clear();
    delete window.__rappBetaAprilFoolsBridge;
  }

  function receive(event) {
    if (event.source !== window.parent || !event.data) return;
    if (event.data.type === "rapp-beta:april-fools-state") {
      current = event.data.aprilFools || current;
      if (!current.on) {
        disable();
      } else {
        renderToggle();
      }
      return;
    }
    if (event.data.type === "rapp-beta:card-capture") {
      try {
        event.source.postMessage({
          type: "rapp-beta:card-capture-result",
          requestId: event.data.requestId,
          ok: true,
          card: captureCard(),
        }, "*");
      } catch (error) {
        event.source.postMessage({
          type: "rapp-beta:card-capture-result",
          requestId: event.data.requestId,
          ok: false,
          error: String(error?.message || error),
        }, "*");
      }
      return;
    }
    if (event.data.type === "rapp-beta:card-parked") {
      markPendingForCard(event.data.id);
      clearKernel({ preservePending: true });
      return;
    }
    if (event.data.type === "rapp-beta:card-wake") {
      renderTranscript(event.data.card || {});
      return;
    }
    if (event.data.type === "rapp-beta:card-clear") {
      clearKernel();
      activeHistory = null;
      lastRequest = null;
      return;
    }
    if (event.data.type === "rapp-beta:card-race") {
      prepareRace(event.data.id, event.data.question);
    }
  }

  const bridge = {
    capture: captureCard,
    disable,
    renderTranscript,
    update(next) {
      current = next;
      renderToggle();
    },
  };
  window.__rappBetaAprilFoolsBridge = bridge;
  window.fetch = cardFetch;
  document.addEventListener("click", handleClear, true);
  window.addEventListener("message", receive);
  renderToggle();
  return true;
}

export function composeChatCardsFrameBridgeSource(checkpointSource, aprilFools) {
  const source = String(checkpointSource || "");
  if (!aprilFools?.on) return source;
  return `${source}\n;(${installAprilFoolsFrameBridge.toString()})(${
    JSON.stringify(normalizeAprilFoolsSettings(aprilFools))
  });`;
}
