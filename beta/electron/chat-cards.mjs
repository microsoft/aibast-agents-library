import {
  chmodSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  statSync,
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
    ...(typeof value.requestId === "string" && value.requestId
      ? { requestId: value.requestId }
      : {}),
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
    ...(typeof value.requestId === "string" && value.requestId
      ? { requestId: value.requestId }
      : {}),
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
  const completedRequestIds = Array.isArray(value.completedRequestIds)
    ? [...new Set(value.completedRequestIds.map(String).filter(Boolean))].slice(-50)
    : [];
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
    restorable: value.restorable !== false,
    restoreError: value.restorable === false
      ? String(value.restoreError || "This card has no observed wire history.")
      : null,
    raceId: typeof value.raceId === "string" && value.raceId
      ? value.raceId
      : null,
    completedRequestIds,
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
    raceIdFactory = () => `race-${randomUUID()}`,
    now = () => new Date(),
  } = {}) {
    if (!betaHome) throw new Error("A beta home is required for chat cards.");
    this.betaHome = betaHome;
    this.idFactory = idFactory;
    this.raceIdFactory = raceIdFactory;
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
      .map((name) => {
        const id = name.slice(0, -5);
        try {
          return this.read(id);
        } catch (error) {
          return normalizeChatCard({
            id,
            title: `Unavailable card: ${id}`,
            turns: [],
            history: [],
            status: "folded",
            table: { faceUp: false },
            restorable: false,
            restoreError: String(error?.message || error),
          }, {
            id,
            now: new Date(0).toISOString(),
          });
        }
      })
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
    const size = statSync(file).size;
    if (size > MAX_CHAT_CARD_BYTES) {
      throw new Error(
        `Chat card ${id} exceeds the ${MAX_CHAT_CARD_BYTES} byte limit.`,
      );
    }
    const source = readFileSync(file, "utf8");
    if (Buffer.byteLength(source) > MAX_CHAT_CARD_BYTES) {
      throw new Error(
        `Chat card ${id} exceeds the ${MAX_CHAT_CARD_BYTES} byte limit.`,
      );
    }
    let value;
    try {
      value = JSON.parse(source);
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

  parkExisting(id) {
    const card = this.read(id);
    card.status = "parked";
    card.parkedAt = this.nowIso();
    return this.save(card);
  }

  complete(id, {
    at,
    history = null,
    html = "",
    model = null,
    requestId = null,
    reply,
    userInput = "",
  } = {}) {
    const card = this.read(id);
    const completionId = String(requestId || "");
    if (completionId && card.completedRequestIds.includes(completionId)) {
      return card;
    }
    const completedAt = timestamp(at, this.nowIso());
    let pending = [...card.turns]
      .reverse()
      .find((turn) => (
        turn.role === "assistant"
        && turn.pending
        && (!completionId || turn.requestId === completionId)
      ));
    if (!pending && completionId) {
      const unboundPending = card.turns.filter((turn) => (
        turn.role === "assistant" && turn.pending && !turn.requestId
      ));
      if (unboundPending.length === 1) pending = unboundPending[0];
    }
    if (pending) {
      pending.text = String(reply || "");
      pending.html = String(html || "");
      pending.at = completedAt;
      if (completionId) pending.requestId = completionId;
      delete pending.pending;
    } else {
      const additions = userInput ? 2 : 1;
      if (card.turns.length + additions > MAX_CHAT_CARD_TURNS) {
        throw new Error(
          `Chat cards are limited to ${MAX_CHAT_CARD_TURNS} transcript turns.`,
        );
      }
      if (userInput) {
        card.turns.push({
          role: "user",
          text: String(userInput),
          html: "",
          at: completedAt,
          ...(completionId ? { requestId: completionId } : {}),
        });
      }
      card.turns.push({
        role: "assistant",
        text: String(reply || ""),
        html: String(html || ""),
        at: completedAt,
        ...(completionId ? { requestId: completionId } : {}),
      });
    }
    if (Array.isArray(history)) {
      card.history = history.map(normalizeHistoryMessage);
    } else {
      const userIndex = completionId
        ? card.history.findIndex((message) => (
            message.role === "user" && message.requestId === completionId
          ))
        : -1;
      const assistant = {
        role: "assistant",
        content: String(reply || ""),
        ...(completionId ? { requestId: completionId } : {}),
      };
      if (userIndex >= 0) card.history.splice(userIndex + 1, 0, assistant);
      else if (userInput) {
        card.history.push({
          role: "user",
          content: String(userInput),
          ...(completionId ? { requestId: completionId } : {}),
        }, assistant);
      } else {
        card.history.push(assistant);
      }
    }
    if (completionId) {
      card.completedRequestIds = [
        ...card.completedRequestIds,
        completionId,
      ].slice(-50);
    }
    if (model) card.route.model = String(model);
    if (!card.turns.some((turn) => turn.pending)) {
      for (const turn of card.turns) delete turn.requestId;
      card.history = card.history.map((message) => ({
        role: message.role,
        content: message.content,
      }));
    }
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
    if (!target.restorable) {
      throw new Error(target.restoreError || "This chat card cannot be restored.");
    }
    const raceId = target.status === "racing" ? target.raceId : null;
    for (const card of this.list()) {
      if (card.id === target.id) continue;
      if (
        raceId
        && card.status === "racing"
        && card.raceId === raceId
      ) {
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
    if (source.status === "racing") {
      throw new Error("This card is already in an unresolved race.");
    }
    const question = lastQuestion(source);
    if (!question) {
      throw new Error("Race requires a card whose last user turn is a question.");
    }
    const raceId = this.raceIdFactory();
    source.status = "racing";
    source.raceId = raceId;
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
      raceId,
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
  function trust(event) {
    assertTrustedIpc?.(event);
  }
  function guard(event) {
    trust(event);
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
  ipcMain.handle("beta:cards-park-existing", (event, id) => {
    guard(event);
    return store.parkExisting(id);
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
    trust(event);
    if (!isEnabled?.()) {
      const requestId = String(completion?.requestId || "");
      const pending = store.read(id).turns.filter((turn) => (
        turn.role === "assistant" && turn.pending
      ));
      const identified = requestId && pending.some((turn) => (
        turn.requestId === requestId
      ));
      const singleUnbound = requestId
        && pending.length === 1
        && !pending[0].requestId;
      if (!identified && !singleUnbound) {
        throw new Error(
          "Only the identified reply for an existing pending card may finish while the table is off.",
        );
      }
    }
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
  let activeCardId = null;
  let activeHistory = null;
  let conversationSequence = 0;
  let currentConversationId = null;
  let internalClear = false;
  let lastRequest = null;
  let nextRaceCardId = null;
  const completedRequests = new Map();
  const conversations = new Map();
  const pendingRequests = new Map();
  const upstreamFetch = window.fetch;
  window.__rappBetaDeferredCardCompletions ||= [];

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

  function turnFromMessage(message, requestId = null) {
    const now = new Date().toISOString();
    const bubble = message.querySelector(".bubble") || message;
    return {
      role: message.classList.contains("user") ? "user" : "assistant",
      text: String(bubble.textContent || "").trim(),
      html: sanitizedHtml(bubble),
      at: now,
      ...(requestId ? { requestId } : {}),
    };
  }

  function transcriptTurns() {
    const chat = document.getElementById("chat");
    if (!chat) return [];
    const turns = [];
    for (const child of chat.children) {
      if (
        child.classList?.contains("msg")
        && (
          child.classList.contains("user")
          || child.classList.contains("assistant")
        )
        && !child.classList.contains("typing-indicator")
        && !child.classList.contains("stream-arriving")
        && !child.hasAttribute("data-rapp-provisional")
      ) {
        const turn = turnFromMessage(
          child,
          child.dataset.rappCardRequestId || null,
        );
        if (turn.text) turns.push(turn);
        continue;
      }
      if (!child.classList?.contains("response-slot")) continue;
      const requestId = child.dataset.rappCardRequestId || null;
      const replies = [...child.querySelectorAll(
        ":scope > .msg.assistant:not(.typing-indicator)"
          + ":not(.stream-arriving):not([data-rapp-provisional])",
      )];
      for (const reply of replies) {
        const turn = turnFromMessage(reply, requestId);
        if (turn.text) turns.push(turn);
      }
      if (!replies.length && requestId && pendingRequests.has(requestId)) {
        const request = pendingRequests.get(requestId);
        turns.push({
          role: "assistant",
          text: "Waiting for reply...",
          html: "",
          at: request.startedAt,
          pending: true,
          requestId,
        });
      }
    }
    return turns;
  }

  function startConversation(baseHistory = null) {
    if (!Array.isArray(baseHistory)) {
      currentConversationId = null;
      return null;
    }
    currentConversationId = `conversation-${++conversationSequence}`;
    const conversation = {
      baseHistory: structuredClone(baseHistory),
      requests: [],
    };
    conversations.set(currentConversationId, conversation);
    return conversation;
  }

  function ensureConversation(baseHistory) {
    return conversations.get(currentConversationId)
      || startConversation(baseHistory);
  }

  function canonicalHistory(conversationId = currentConversationId) {
    const conversation = conversations.get(conversationId);
    if (!conversation) return null;
    const history = structuredClone(conversation.baseHistory);
    for (const request of conversation.requests) {
      history.push({
        role: "user",
        content: request.userInput,
        requestId: request.id,
      });
      if (request.reply !== undefined) {
        history.push({
          role: "assistant",
          content: request.reply,
          requestId: request.id,
        });
      }
    }
    return history;
  }

  function wireHistory(messages) {
    return (Array.isArray(messages) ? messages : []).map((message) => ({
      role: message.role,
      content: String(message.content || ""),
    }));
  }

  function pendingHistory() {
    const observed = canonicalHistory();
    if (observed) return observed;
    return activeHistory ? structuredClone(activeHistory) : [];
  }

  function captureCard() {
    const turns = transcriptTurns();
    const pending = [...pendingRequests.values()]
      .filter((request) => !request.parkedCardId);
    const model = document.getElementById("model-select")?.value || "auto";
    const observedHistory = canonicalHistory();
    const hasObservedHistory = Boolean(
      observedHistory
      || activeHistory,
    );
    return {
      title: turns.find((turn) => turn.role === "user")?.text || "Parked chat",
      turns,
      history: observedHistory || pendingHistory(),
      model,
      pending: pending.length > 0,
      pendingRequestIds: pending.map((request) => request.id),
      restorable: hasObservedHistory || !turns.some((turn) => turn.role === "user"),
      restoreError: hasObservedHistory
        ? null
        : "This transcript predates April Fools mode, so its exact wire history was not observed.",
    };
  }

  function completionEvent(request) {
    return {
      type: "rapp-beta:card-pending-complete",
      id: request.parkedCardId,
      requestId: request.id,
      completion: {
        ...request.completion,
        history: request.clearedFromKernel
          ? null
          : request.completion.history,
      },
      restoreInFrame: request.clearedFromKernel === true,
    };
  }

  function emitCompletion(request) {
    if (!request.parkedCardId || !request.completion) return;
    const deferred = window.__rappBetaDeferredCardCompletions;
    if (!deferred.some((entry) => entry.requestId === request.id)) {
      deferred.push(completionEvent(request));
      if (deferred.length > 50) deferred.splice(0, deferred.length - 50);
    }
    window.parent.postMessage(completionEvent(request), "*");
  }

  function drainDeferredCompletions() {
    for (const completion of window.__rappBetaDeferredCardCompletions || []) {
      window.parent.postMessage(completion, "*");
    }
  }

  function markPendingForCard(cardId, requestIds = []) {
    activeCardId = null;
    activeHistory = null;
    const ids = requestIds.length
      ? requestIds
      : [...pendingRequests.keys()];
    for (const requestId of ids) {
      const request = pendingRequests.get(requestId)
        || completedRequests.get(requestId);
      if (!request) continue;
      request.parkedCardId = cardId;
      request.preserveOnClear = true;
      request.clearedFromKernel = true;
      emitCompletion(request);
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
    activeCardId = card.id || null;
    activeHistory = Array.isArray(card.history)
      ? structuredClone(card.history)
      : [];
    startConversation(activeHistory);
    const modelSelect = document.getElementById("model-select");
    const model = String(card.route?.model || "");
    if (
      modelSelect
      && model
      && [...modelSelect.options].some((option) => option.value === model)
      && modelSelect.value !== model
    ) {
      modelSelect.value = model;
      modelSelect.dispatchEvent(new Event("change", { bubbles: true }));
    }
    const chat = document.getElementById("chat");
    if (!chat) throw new Error("The Brainstem transcript is unavailable.");
    for (const turn of card.turns || []) {
      if (turn.pending) continue;
      appendRestoredTurn(turn);
    }
    chat.classList.add("has-messages");
    chat.scrollTop = chat.scrollHeight;
    return true;
  }

  function appendRestoredTurn(turn) {
    const chat = document.getElementById("chat");
    if (!chat) throw new Error("The Brainstem transcript is unavailable.");
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
    if (turn.requestId && message) {
      message.dataset.rappCardRequestId = turn.requestId;
    }
    const bubble = message?.querySelector?.(".bubble");
    if (bubble && turn.html) {
      bubble.replaceChildren(
        typeof window.sanitizeMarkdownFragment === "function"
          ? window.sanitizeMarkdownFragment(String(turn.html))
          : document.createTextNode(turn.text),
      );
    }
    chat.classList.add("has-messages");
    chat.scrollTop = chat.scrollHeight;
    return message;
  }

  function applyLateCompletion(completion) {
    const reply = String(completion?.reply || "");
    if (!reply) return;
    activeHistory ||= [];
    const last = activeHistory.at(-1);
    if (last?.role === "assistant" && last.content === reply) return;
    activeHistory.push({ role: "assistant", content: reply });
    const conversation = conversations.get(currentConversationId);
    if (conversation) {
      conversation.baseHistory = structuredClone(activeHistory);
    }
    appendRestoredTurn({
      role: "assistant",
      text: reply,
      html: String(completion.html || ""),
    });
  }

  function prepareRace(cardId, question) {
    clearKernel();
    activeCardId = cardId;
    activeHistory = null;
    startConversation([]);
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
      request.reply = reply;
      request.completedHistory = canonicalHistory(request.conversationId)
        || [
          ...request.effectiveHistory,
          { role: "user", content: request.userInput },
          { role: "assistant", content: reply },
        ];
      request.completion = {
        reply,
        html: replyHtml(reply),
        at: new Date().toISOString(),
        history: request.completedHistory,
        model: request.model,
        requestId: request.id,
        userInput: request.userInput,
      };
      if (!request.parkedCardId) lastRequest = request;
      completedRequests.set(request.id, request);
      while (completedRequests.size > 50) {
        completedRequests.delete(completedRequests.keys().next().value);
      }
      emitCompletion(request);
    } finally {
      request.detachAbort?.();
      pendingRequests.delete(request.id);
      const conversation = conversations.get(request.conversationId);
      if (
        request.conversationId !== currentConversationId
        && conversation?.requests.every((entry) => entry.reply !== undefined)
      ) {
        conversations.delete(request.conversationId);
      }
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

    const incomingHistory = wireHistory(body.conversation_history);
    const effectiveHistory = activeHistory
      ? [...wireHistory(activeHistory), ...incomingHistory]
      : incomingHistory;
    body.conversation_history = effectiveHistory;
    const conversation = ensureConversation(effectiveHistory);

    const originalSignal = options.signal
      || (resource instanceof Request ? resource.signal : null);
    const controller = new AbortController();
    const request = {
      completedHistory: null,
      effectiveHistory: structuredClone(effectiveHistory),
      id: window.crypto.randomUUID(),
      conversationId: currentConversationId,
      parkedCardId: nextRaceCardId || activeCardId,
      preserveOnClear: Boolean(nextRaceCardId),
      model: document.getElementById("model-select")?.value || "auto",
      startedAt: new Date().toISOString(),
      userInput: body.user_input,
    };
    conversation.requests.push(request);
    const responseSlot = [...document.querySelectorAll(
      "#chat .response-slot",
    )].reverse().find((slot) => !slot.dataset.rappCardRequestId);
    if (responseSlot) responseSlot.dataset.rappCardRequestId = request.id;
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
      const failedConversation = conversations.get(request.conversationId);
      if (failedConversation) {
        failedConversation.requests = failedConversation.requests.filter(
          (entry) => entry.id !== request.id,
        );
      }
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
      if (activeCardId) {
        window.parent.postMessage({
          type: "rapp-beta:card-detached",
          id: activeCardId,
        }, "*");
      }
      activeHistory = null;
      activeCardId = null;
      lastRequest = null;
      startConversation(null);
    }
  }

  function disable() {
    removeToggle();
    document.removeEventListener("click", handleClear, true);
    window.removeEventListener("message", receive);
    if (window.fetch === cardFetch) window.fetch = upstreamFetch;
    if (activeCardId) {
      for (const request of pendingRequests.values()) {
        if (request.parkedCardId === activeCardId) {
          request.preserveOnClear = true;
          request.clearedFromKernel = true;
        }
      }
      clearKernel({ preservePending: true });
    }
    startConversation(null);
    activeCardId = null;
    activeHistory = null;
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
      markPendingForCard(event.data.id, event.data.requestIds || []);
      clearKernel({ preservePending: true });
      startConversation(null);
      return;
    }
    if (event.data.type === "rapp-beta:card-wake") {
      renderTranscript(event.data.card || {});
      return;
    }
    if (event.data.type === "rapp-beta:card-clear") {
      clearKernel();
      activeCardId = null;
      activeHistory = null;
      lastRequest = null;
      startConversation(null);
      return;
    }
    if (event.data.type === "rapp-beta:card-late-completion") {
      applyLateCompletion(event.data.completion);
      return;
    }
    if (event.data.type === "rapp-beta:card-completion-ack") {
      completedRequests.delete(event.data.requestId);
      window.__rappBetaDeferredCardCompletions = (
        window.__rappBetaDeferredCardCompletions || []
      ).filter((entry) => entry.requestId !== event.data.requestId);
      return;
    }
    if (event.data.type === "rapp-beta:card-ready") {
      drainDeferredCompletions();
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
  window.setTimeout(drainDeferredCompletions, 100);
  window.setTimeout(drainDeferredCompletions, 500);
  return true;
}

export function composeChatCardsFrameBridgeSource(checkpointSource, aprilFools) {
  const source = String(checkpointSource || "");
  if (!aprilFools?.on) return source;
  return `${source}\n;(${installAprilFoolsFrameBridge.toString()})(${
    JSON.stringify(normalizeAprilFoolsSettings(aprilFools))
  });`;
}
