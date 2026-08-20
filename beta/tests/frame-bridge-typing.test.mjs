import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";

await import("../ui/stream-follow.js");
await import("../ui/stream-pacing.js");
await import("../ui/chat-look.js");

const mainSource = readFileSync(
  new URL("../electron/main.mjs", import.meta.url),
  "utf8",
);
const { createTailFollower } = globalThis.RappStreamFollow;
const {
  createStreamPacer,
  createTextSplitter,
  splitTextPieces,
} = globalThis.RappStreamPacing;
const {
  applyLookStyles,
  grailFrameCss,
  inferMessageSide,
  markArrived,
  markGroupLast,
  normalizeChatLook,
} = globalThis.RappChatLook;

function extractExpression(startMarker, endMarker) {
  const declarationStart = mainSource.indexOf(startMarker);
  const expressionStart = mainSource.indexOf("=", declarationStart) + 1;
  const expressionEnd = mainSource.indexOf(endMarker, expressionStart);
  assert.ok(
    declarationStart >= 0 && expressionStart > 0 && expressionEnd > expressionStart,
  );
  return mainSource.slice(expressionStart, expressionEnd);
}

const smoothStreamCss = vm.runInNewContext(
  extractExpression("const smoothStreamCss =", ";\nconst betaHome ="),
);
const bridgeExpression = extractExpression(
  "const BETA_FRAME_BRIDGE_SOURCE =",
  ";\n\nfunction frameBridgeInstallationSource",
);

function materializeBridgeSource(chatStreamMode) {
  return vm.runInNewContext(bridgeExpression, {
    applyLookStyles,
    chatStreamMode,
    createStreamPacer,
    createTailFollower,
    createTextSplitter,
    exportRedactionSource: "",
    grailFrameCss,
    humanizeAgentName: (value) => String(value),
    inferMessageSide,
    markArrived,
    markGroupLast,
    normalizeChatLook,
    smoothStreamCss,
    splitTextPieces,
  });
}

function fakeClock() {
  let currentTime = 0;
  let sequence = 0;
  const tasks = new Map();

  function setTimer(callback, delay) {
    const id = ++sequence;
    tasks.set(id, {
      at: currentTime + delay,
      callback,
      id,
    });
    return id;
  }

  function clearTimer(id) {
    tasks.delete(id);
  }

  function runAll(limit = 10000) {
    let count = 0;
    while (tasks.size) {
      const next = [...tasks.values()].sort(
        (left, right) => left.at - right.at || left.id - right.id,
      )[0];
      tasks.delete(next.id);
      currentTime = next.at;
      next.callback();
      count += 1;
      if (count > limit) throw new Error("Fake timer runaway.");
    }
  }

  class ClockDate extends Date {
    static now() {
      return currentTime;
    }
  }

  return {
    ClockDate,
    clearTimer,
    now: () => currentTime,
    pending: () => tasks.size,
    runAll,
    setTimer,
  };
}

function createDom() {
  const byId = new Map();
  const mutationObservations = [];
  const resizeObservations = [];

  function createElement(tagName = "div") {
    const attributes = new Map();
    const listeners = new Map();
    const classes = new Set();
    const styleValues = new Map();
    const element = {
      append: () => {},
      appendChild(child) {
        child.parentNode = element;
        if (child.id) byId.set(child.id, child);
      },
      addEventListener(type, listener) {
        listeners.set(type, listener);
      },
      classList: {
        add: (...values) => values.forEach((value) => classes.add(value)),
        contains: (value) => classes.has(value),
        remove: (...values) => values.forEach((value) => classes.delete(value)),
        toggle(value, enabled) {
          if (enabled) classes.add(value);
          else classes.delete(value);
        },
      },
      closest: () => null,
      dataset: {},
      getAttribute: (name) => attributes.get(name) ?? null,
      getBoundingClientRect: () => ({ height: 0 }),
      id: "",
      isContentEditable: false,
      listeners,
      parentNode: null,
      querySelector: () => null,
      querySelectorAll: () => [],
      remove() {
        if (element.id) byId.delete(element.id);
      },
      removeAttribute: (name) => attributes.delete(name),
      setAttribute: (name, value) => attributes.set(name, String(value)),
      style: {
        getPropertyValue: (name) => styleValues.get(name) || "",
        setProperty: (name, value) => styleValues.set(name, String(value)),
      },
      tagName: String(tagName).toUpperCase(),
      textContent: "",
    };
    return element;
  }

  const documentElement = createElement("html");
  const head = createElement("head");
  const body = createElement("body");
  const chat = createElement("div");
  chat.id = "chat";
  chat.clientHeight = 400;
  chat.scrollHeight = 1000;
  chat.scrollTop = 600;
  chat.arriving = null;
  chat.querySelector = (selector) => (
    selector === ".msg.assistant.stream-arriving" ? chat.arriving : null
  );
  const footer = createElement("footer");
  footer.getBoundingClientRect = () => ({ height: 112.5 });
  byId.set("chat", chat);

  const document = {
    addEventListener: () => {},
    body,
    createElement,
    documentElement,
    getElementById: (id) => byId.get(id) || null,
    head,
    querySelector(selector) {
      if (selector === "footer") return footer;
      return null;
    },
    querySelectorAll: () => [],
  };

  class FakeMutationObserver {
    constructor(callback) {
      this.callback = callback;
    }

    observe(target, options) {
      mutationObservations.push({ observer: this, options, target });
    }
  }

  class FakeResizeObserver {
    constructor(callback) {
      this.callback = callback;
    }

    disconnect() {}

    observe(target) {
      resizeObservations.push({ observer: this, target });
    }
  }

  return {
    FakeMutationObserver,
    FakeResizeObserver,
    chat,
    document,
    footer,
    mutationObservations,
    resizeObservations,
  };
}

function installBridge({
  chatLook = "messages",
  chatStreamMode = "smooth",
  chatTypingEnabled = chatStreamMode === "hold",
  clock = fakeClock(),
  nativeFetch,
} = {}) {
  const messageListeners = new Set();
  const dom = createDom();
  const parent = {
    postMessage(message) {
      if (message.type !== "rapp-beta:lineage-chat") return;
      queueMicrotask(() => {
        const event = {
          source: parent,
          data: {
            type: "rapp-beta:lineage-chat-result",
            requestId: message.requestId,
            ok: true,
            result: { intercepted: false },
          },
        };
        for (const listener of messageListeners) listener(event);
      });
    },
  };
  const window = {
    __rappBetaChatLookConfig: {
      chatLook,
      chatTypingEnabled,
    },
    addEventListener: () => {},
    alert: () => {},
    clearTimeout: clock.clearTimer,
    confirm: () => true,
    crypto: { randomUUID: () => "request-id" },
    document: dom.document,
    fetch: nativeFetch,
    location: { href: "http://127.0.0.1:7071/" },
    parent,
    removeEventListener(type, listener) {
      if (type === "message") messageListeners.delete(listener);
    },
    setTimeout: clock.setTimer,
  };
  window.addEventListener = (type, listener) => {
    if (type === "message") messageListeners.add(listener);
  };
  const context = vm.createContext({
    console,
    Date: clock.ClockDate,
    document: dom.document,
    Error,
    Headers,
    MutationObserver: dom.FakeMutationObserver,
    performance: { now: clock.now },
    ReadableStream,
    Request,
    ResizeObserver: dom.FakeResizeObserver,
    Response,
    setTimeout: clock.setTimer,
    clearTimeout: clock.clearTimer,
    TextDecoder,
    TextEncoder,
    URL,
    window,
  });
  vm.runInContext(materializeBridgeSource(chatStreamMode), context);
  return { clock, dom, window };
}

function controlledResponse({
  headers = {
    "Cache-Control": "no-cache, no-transform",
    "Content-Type": "text/event-stream; charset=utf-8",
    "X-Frontier-Test": "preserved",
  },
} = {}) {
  let controller;
  let canceled = false;
  let cancelReason;
  const stream = new ReadableStream({
    start(nextController) {
      controller = nextController;
    },
    cancel(reason) {
      canceled = true;
      cancelReason = reason;
    },
  });
  return {
    response: new Response(stream, {
      status: 202,
      statusText: "Accepted",
      headers,
    }),
    enqueue(text) {
      controller.enqueue(new TextEncoder().encode(text));
    },
    close() {
      controller.close();
    },
    error(cause) {
      controller.error(cause);
    },
    get canceled() {
      return canceled;
    },
    get cancelReason() {
      return cancelReason;
    },
  };
}

function sse(event) {
  return `data: ${JSON.stringify(event)}\n\n`;
}

async function nextTask() {
  await new Promise((resolve) => setImmediate(resolve));
}

async function readChunks(reader) {
  const decoder = new TextDecoder();
  const chunks = [];
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    chunks.push(decoder.decode(value, { stream: true }));
  }
  const tail = decoder.decode();
  if (tail) chunks.push(tail);
  return chunks;
}

function parseEvents(text) {
  return text
    .split(/\r?\n\r?\n/)
    .map((frame) => frame.split(/\r?\n/).find((line) => line.startsWith("data:")))
    .filter(Boolean)
    .map((line) => JSON.parse(line.slice(5).trim()));
}

function largeReply(length = 1600) {
  const phrase = "Smooth streams every word, emoji 🙂, and punctuation cleanly. ";
  return phrase.repeat(Math.ceil(length / phrase.length)).slice(0, length);
}

test("smooth bridge paces a large delta byte-equally before done", async () => {
  const upstream = controlledResponse();
  const installed = installBridge({
    chatStreamMode: "smooth",
    nativeFetch: async () => upstream.response,
  });
  const wrapped = await installed.window.fetch(
    "http://127.0.0.1:7071/chat/stream",
    {
      method: "POST",
      body: JSON.stringify({ user_input: "hello" }),
    },
  );
  const text = largeReply();
  upstream.enqueue(sse({ type: "delta", text }));
  await nextTask();
  installed.clock.runAll();
  upstream.enqueue(sse({ type: "agent", logs: "tool complete" }));
  upstream.enqueue(sse({ type: "done", response: text }));
  upstream.close();

  const chunks = await readChunks(wrapped.body.getReader());
  const events = parseEvents(chunks.join(""));
  const deltas = events.filter((event) => event.type === "delta");
  assert.ok(deltas.length >= 24, `expected >=24 chunks, got ${deltas.length}`);
  assert.equal(deltas.map((event) => event.text).join(""), text);
  assert.deepEqual(
    events.slice(-2).map((event) => event.type),
    ["agent", "done"],
  );
  console.log(
    `smooth: ${deltas.length} delta chunks; byte-equality yes; `
      + `order ${events.at(-2).type}->${events.at(-1).type}`,
  );
});

test("smooth done flushes queued text before upstream EOF", async () => {
  const upstream = controlledResponse();
  const installed = installBridge({
    chatStreamMode: "smooth",
    nativeFetch: async () => upstream.response,
  });
  const wrapped = await installed.window.fetch(
    "http://127.0.0.1:7071/chat/stream",
    {
      method: "POST",
      body: JSON.stringify({ user_input: "hello" }),
    },
  );
  const text = "terminal done flushes every queued word immediately";
  const reader = wrapped.body.getReader();

  upstream.enqueue(sse({ type: "delta", text }));
  const first = await reader.read();
  assert.ok(installed.clock.pending() > 0);
  upstream.enqueue(sse({ type: "done", response: text }));
  await nextTask();
  const second = await reader.read();
  const third = await reader.read();
  const decoder = new TextDecoder();
  const events = parseEvents(
    decoder.decode(first.value)
      + decoder.decode(second.value)
      + decoder.decode(third.value),
  );

  assert.equal(
    events.filter((event) => event.type === "delta")
      .map((event) => event.text)
      .join(""),
    text,
  );
  assert.equal(events.at(-1).type, "done");
  assert.equal(installed.clock.pending(), 0);
  upstream.close();
  assert.equal((await reader.read()).done, true);
  console.log("smooth done flush: queued text emitted before upstream EOF");
});

test("smooth style and follow observers exist only in smooth mode", () => {
  const smooth = installBridge({
    chatStreamMode: "smooth",
    nativeFetch: async () => new Response("ok"),
  });
  const style = smooth.dom.document.getElementById("__rappStreamStyle");
  assert.ok(style);
  assert.match(style.textContent, /-webkit-mask-image:\s*none !important/);
  assert.match(style.textContent, /mask-image:\s*none !important/);
  assert.match(style.textContent, /stream-arriving \.bubble::after/);
  assert.match(style.textContent, /padding-bottom:\s*var\(--rapp-stream-footer-clearance/);
  assert.doesNotMatch(style.textContent, /translateY/);
  assert.equal(
    smooth.dom.document.documentElement.dataset.rappStream,
    "smooth",
  );
  assert.equal(
    smooth.dom.document.documentElement.style.getPropertyValue(
      "--rapp-stream-footer-clearance",
    ),
    "112.5px",
  );
  assert.ok(smooth.window.__rappSmoothTailFollow);
  assert.ok(
    smooth.dom.mutationObservations.some(({ target }) => target === smooth.dom.chat),
  );
  assert.ok(
    smooth.dom.resizeObservations.some(({ target }) => target === smooth.dom.footer),
  );

  for (const mode of ["raw", "hold"]) {
    const installed = installBridge({
      chatStreamMode: mode,
      nativeFetch: async () => new Response("ok"),
    });
    assert.equal(
      installed.dom.document.getElementById("__rappStreamStyle"),
      null,
    );
    assert.equal(installed.window.__rappSmoothTailFollow, undefined);
    assert.equal(
      installed.dom.document.documentElement.style.getPropertyValue(
        "--rapp-stream-footer-clearance",
      ),
      "",
    );
  }
  console.log("smooth-only style, exact 112.5px clearance, and observers present");
});

test("raw bridge passes the native stream response through unchanged", async () => {
  const upstream = controlledResponse();
  const installed = installBridge({
    chatStreamMode: "raw",
    nativeFetch: async () => upstream.response,
  });
  const response = await installed.window.fetch(
    "http://127.0.0.1:7071/chat/stream",
    {
      method: "POST",
      body: JSON.stringify({ user_input: "hello" }),
    },
  );

  assert.strictEqual(response, upstream.response);
  console.log("raw: native response pass-through");
});

test("hold emits zero bytes before completion and replays ordered SSE", async () => {
  const upstream = controlledResponse();
  const installed = installBridge({
    chatStreamMode: "hold",
    nativeFetch: async () => upstream.response,
  });
  const wrapped = await installed.window.fetch(
    "http://127.0.0.1:7071/chat/stream",
    {
      method: "POST",
      body: JSON.stringify({ user_input: "hello" }),
    },
  );
  const frames = [
    sse({ type: "delta", text: "one" }),
    sse({ type: "delta", text: " two" }),
    sse({ type: "delta", text: " three" }),
    sse({ type: "done", response: "one two three" }),
  ];
  const reader = wrapped.body.getReader();
  const firstRead = reader.read();
  let settled = false;
  void firstRead.then(
    () => { settled = true; },
    () => { settled = true; },
  );
  for (const frame of frames) upstream.enqueue(frame);
  await nextTask();
  assert.equal(settled, false);

  upstream.close();
  const first = await firstRead;
  const remaining = await readChunks(reader);
  const decoder = new TextDecoder();
  const replay = decoder.decode(first.value) + remaining.join("");
  assert.equal(replay, frames.join(""));
  console.log("hold: 0 bytes before completion; ordered replay yes");
});

test("frame bridge injects and removes Messages look without a reload", () => {
  const installed = installBridge({
    chatLook: "messages",
    nativeFetch: async () => new Response("ok"),
  });
  const { window } = installed;
  const marker = window.__rappBetaFrameBridge;

  assert.ok(window.document.getElementById("__rappChatLook"));
  assert.equal(
    window.document.documentElement.getAttribute("data-rapp-look"),
    "messages",
  );
  console.log("inject: Messages style and html[data-rapp-look] present");

  const applied = window.__rappBetaApplyChatLook("business", false);
  assert.equal(applied.chatLook, "business");
  assert.equal(applied.chatTypingEnabled, false);
  assert.equal(window.__rappBetaFrameBridge, marker);
  assert.equal(window.document.getElementById("__rappChatLook"), null);
  assert.equal(
    window.document.documentElement.getAttribute("data-rapp-look"),
    null,
  );
  console.log("remove: Messages style and root attribute removed without reload");

  const business = installBridge({
    chatLook: "business",
    chatTypingEnabled: false,
    nativeFetch: async () => new Response("ok"),
  });
  assert.equal(
    business.window.document.getElementById("__rappChatLook"),
    null,
  );
  assert.equal(
    business.window.document.documentElement.getAttribute("data-rapp-look"),
    null,
  );
  console.log("business injects nothing");
});

test("smooth upstream error flushes queued text followed by error", async () => {
  const upstream = controlledResponse();
  const installed = installBridge({
    chatStreamMode: "smooth",
    nativeFetch: async () => upstream.response,
  });
  const wrapped = await installed.window.fetch(
    "http://127.0.0.1:7071/chat/stream",
    {
      method: "POST",
      body: JSON.stringify({ user_input: "hello" }),
    },
  );
  const text = "partial words remain byte equal";
  upstream.enqueue(sse({ type: "delta", text }));
  await nextTask();
  upstream.error(new Error("upstream exploded"));

  const events = parseEvents((await readChunks(wrapped.body.getReader())).join(""));
  assert.equal(
    events.filter((event) => event.type === "delta")
      .map((event) => event.text)
      .join(""),
    text,
  );
  assert.equal(events.at(-1).type, "error");
  assert.equal(events.at(-1).error, "upstream exploded");
});

test("aborting a smooth response cancels upstream", async () => {
  const upstream = controlledResponse();
  const installed = installBridge({
    chatStreamMode: "smooth",
    nativeFetch: async () => upstream.response,
  });
  const controller = new AbortController();
  const wrapped = await installed.window.fetch(
    "http://127.0.0.1:7071/chat/stream",
    {
      method: "POST",
      body: JSON.stringify({ user_input: "hello" }),
      signal: controller.signal,
    },
  );
  const read = wrapped.body.getReader().read();

  controller.abort();

  await assert.rejects(read, (cause) => cause?.name === "AbortError");
  assert.equal(upstream.canceled, true);
  assert.equal(upstream.cancelReason?.name, "AbortError");
});
