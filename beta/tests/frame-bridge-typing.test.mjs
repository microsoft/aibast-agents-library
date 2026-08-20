import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";

await import("../ui/stream-follow.js");
await import("../ui/stream-pacing.js");

const { createTailFollower } = globalThis.RappStreamFollow;
const {
  createStreamPacer,
  createTextSplitter,
  splitTextPieces,
} = globalThis.RappStreamPacing;
const mainSource = readFileSync(
  new URL("../electron/main.mjs", import.meta.url),
  "utf8",
);

function extractExpression(startMarker, endMarker) {
  const declarationStart = mainSource.indexOf(startMarker);
  const expressionStart = mainSource.indexOf("=", declarationStart) + 1;
  const expressionEnd = mainSource.indexOf(endMarker, expressionStart);
  assert.ok(
    declarationStart >= 0 && expressionStart > 0 && expressionEnd > expressionStart,
    `could not extract ${startMarker}`,
  );
  return mainSource.slice(expressionStart, expressionEnd);
}

const smoothStreamCss = vm.runInNewContext(extractExpression(
  "const smoothStreamCss =",
  ";\nconst startupFingerprint",
));

function materializeBridgeSource(chatStreamMode) {
  const expression = extractExpression(
    "const BETA_FRAME_BRIDGE_SOURCE =",
    ";\nconst copilot =",
  );
  return vm.runInNewContext(expression, {
    chatStreamMode,
    createStreamPacer,
    createTailFollower,
    createTextSplitter,
    exportRedactionSource: "",
    humanizeAgentName: (value) => String(value),
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
    tasks.set(id, { at: currentTime + delay, callback, id });
    return id;
  }

  function clearTimer(id) {
    tasks.delete(id);
  }

  function runNext() {
    const next = [...tasks.values()].sort(
      (left, right) => left.at - right.at || left.id - right.id,
    )[0];
    if (!next) return false;
    tasks.delete(next.id);
    currentTime = next.at;
    next.callback();
    return true;
  }

  function runAll(limit = 10000) {
    let count = 0;
    while (runNext()) {
      count += 1;
      if (count > limit) throw new Error("Fake timer runaway.");
    }
  }

  return {
    clearTimer,
    pending: () => tasks.size,
    runAll,
    setTimer,
  };
}

function createDom() {
  const byId = new Map();

  function createElement(tagName = "div") {
    const attributes = new Map();
    const element = {
      append: () => {},
      appendChild(child) {
        child.parentNode = element;
        if (child.id) byId.set(child.id, child);
      },
      classList: {
        add: () => {},
        contains: () => false,
        toggle: () => {},
      },
      dataset: {},
      id: "",
      parentNode: null,
      querySelector: () => null,
      querySelectorAll: () => [],
      remove() {
        if (element.id) byId.delete(element.id);
        element.parentNode = null;
      },
      removeAttribute(name) {
        attributes.delete(name);
      },
      setAttribute(name, value) {
        attributes.set(name, String(value));
      },
      style: {},
      tagName: String(tagName).toUpperCase(),
      textContent: "",
    };
    return element;
  }

  const documentElement = createElement("html");
  const head = createElement("head");
  const body = createElement("body");
  return {
    addEventListener: () => {},
    body,
    createElement,
    documentElement,
    getElementById: (id) => byId.get(id) || null,
    head,
    querySelector: () => null,
    querySelectorAll: () => [],
  };
}

function installBridge({
  chatStreamMode = "smooth",
  clock = null,
  nativeFetch,
}) {
  const messageListeners = new Set();
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
  const document = createDom();
  const window = {
    addEventListener(type, listener) {
      if (type === "message") messageListeners.add(listener);
    },
    clearTimeout,
    confirm: () => true,
    crypto: { randomUUID: () => "request-id" },
    fetch: nativeFetch,
    location: { href: "http://127.0.0.1:7071/" },
    parent,
    removeEventListener(type, listener) {
      if (type === "message") messageListeners.delete(listener);
    },
    setTimeout,
  };
  const context = vm.createContext({
    clearTimeout: clock?.clearTimer || clearTimeout,
    console,
    document,
    Error,
    Headers,
    MutationObserver: class {
      observe() {}
    },
    ReadableStream,
    Request,
    Response,
    setTimeout: clock?.setTimer || setTimeout,
    TextDecoder,
    TextEncoder,
    URL,
    window,
  });
  vm.runInContext(materializeBridgeSource(chatStreamMode), context);
  return { document, window };
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

async function readAll(reader, firstRead = reader.read()) {
  const decoder = new TextDecoder();
  let output = "";
  let next = await firstRead;
  while (!next.done) {
    output += decoder.decode(next.value, { stream: true });
    next = await reader.read();
  }
  return output + decoder.decode();
}

function parseEvents(text) {
  return text
    .split("\n\n")
    .map((frame) => frame.split("\n").find((line) => line.startsWith("data:")))
    .filter(Boolean)
    .map((line) => JSON.parse(line.slice(5).trim()));
}

function nextTask() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

test("frame bridge installs only the smooth stream presentation", () => {
  const noFetch = async () => new Response("ok");
  const smooth = installBridge({ chatStreamMode: "smooth", nativeFetch: noFetch });
  const raw = installBridge({ chatStreamMode: "raw", nativeFetch: noFetch });
  const hold = installBridge({ chatStreamMode: "hold", nativeFetch: noFetch });

  const style = smooth.document.getElementById("__rappStreamStyle");
  assert.ok(style);
  assert.match(style.textContent, /mask-image:\s*none !important/);
  assert.match(style.textContent, /stream-arriving \.bubble::after/);
  assert.doesNotMatch(style.textContent, /translateY/);
  assert.equal(smooth.document.documentElement.dataset.rappStream, "smooth");
  assert.equal(raw.document.documentElement.dataset.rappStream, "raw");
  assert.equal(hold.document.documentElement.dataset.rappStream, "hold");
  assert.equal(raw.document.getElementById("__rappStreamStyle"), null);
  assert.equal(hold.document.getElementById("__rappStreamStyle"), null);
});

test("smooth mode paces a large delta with byte equality and event order", async () => {
  const clock = fakeClock();
  const upstream = controlledResponse();
  const { window } = installBridge({
    chatStreamMode: "smooth",
    clock,
    nativeFetch: async () => upstream.response,
  });
  const wrapped = await window.fetch("http://127.0.0.1:7071/chat/stream", {
    method: "POST",
    body: JSON.stringify({ user_input: "hello" }),
  });
  const firstText = `${"one two three four five ".repeat(40)}FIRST-END `;
  const secondText = "second tail 🙂";

  upstream.enqueue(sse({ type: "delta", text: firstText }));
  await nextTask();
  clock.runAll();
  upstream.enqueue(sse({ type: "agent", logs: "tool complete" }));
  upstream.enqueue(sse({ type: "delta", text: secondText }));
  await nextTask();
  clock.runAll();
  upstream.enqueue(sse({
    type: "done",
    response: firstText + secondText,
  }));
  upstream.close();

  const replay = await readAll(wrapped.body.getReader());
  const events = parseEvents(replay);
  const deltas = events.filter((event) => event.type === "delta");
  const agentIndex = events.findIndex((event) => event.type === "agent");
  const firstSecondDelta = events.findIndex(
    (event) => event.type === "delta" && event.text.includes("second"),
  );

  assert.ok(deltas.length >= 12, `expected at least 12 chunks, got ${deltas.length}`);
  assert.equal(
    deltas.map((event) => event.text).join(""),
    firstText + secondText,
  );
  assert.ok(agentIndex > 0);
  assert.ok(firstSecondDelta > agentIndex);
  assert.equal(events.at(-1).type, "done");
  console.log(
    `smooth: ${deltas.length} delta chunks, byte-equality yes, order preserved`,
  );
});

test("smooth mode flushes queued text when done arrives", async () => {
  const clock = fakeClock();
  const upstream = controlledResponse();
  const { window } = installBridge({
    chatStreamMode: "smooth",
    clock,
    nativeFetch: async () => upstream.response,
  });
  const wrapped = await window.fetch("http://127.0.0.1:7071/chat/stream", {
    method: "POST",
    body: JSON.stringify({ user_input: "hello" }),
  });
  const text = "flush every queued word when terminal done arrives";

  upstream.enqueue(sse({ type: "delta", text }));
  await nextTask();
  assert.ok(clock.pending() > 0);
  upstream.enqueue(sse({ type: "done", response: text }));
  upstream.close();

  const events = parseEvents(await readAll(wrapped.body.getReader()));
  assert.equal(
    events.filter((event) => event.type === "delta")
      .map((event) => event.text).join(""),
    text,
  );
  assert.equal(events.at(-1).type, "done");
  assert.equal(clock.pending(), 0);
  console.log("smooth terminal flush: complete text before done");
});

test("raw mode passes the native streaming response through untouched", async () => {
  const upstream = controlledResponse();
  const { window } = installBridge({
    chatStreamMode: "raw",
    nativeFetch: async () => upstream.response,
  });
  const response = await window.fetch("http://127.0.0.1:7071/chat/stream", {
    method: "POST",
    body: JSON.stringify({ user_input: "hello" }),
  });

  assert.strictEqual(response, upstream.response);
  upstream.close();
  console.log("raw: native response pass-through");
});

test("hold mode emits zero bytes before completion, then ordered replay", async () => {
  const upstream = controlledResponse();
  const { window } = installBridge({
    chatStreamMode: "hold",
    nativeFetch: async () => upstream.response,
  });
  const wrapped = await window.fetch("http://127.0.0.1:7071/chat/stream", {
    method: "POST",
    body: JSON.stringify({ user_input: "hello" }),
  });
  const frames = [
    sse({ type: "delta", text: "one" }),
    sse({ type: "delta", text: " two" }),
    sse({ type: "done", response: "one two" }),
  ];
  const reader = wrapped.body.getReader();
  const firstRead = reader.read();
  let settled = false;
  void firstRead.then(
    () => { settled = true; },
    () => { settled = true; },
  );
  frames.forEach((frame) => upstream.enqueue(frame));
  await nextTask();

  assert.equal(settled, false);
  upstream.close();
  assert.equal(await readAll(reader, firstRead), frames.join(""));
  console.log("hold: 0 bytes before completion, ordered replay");
});

test("smooth mode flushes buffered frames followed by an upstream error", async () => {
  const clock = fakeClock();
  const upstream = controlledResponse();
  const { window } = installBridge({
    chatStreamMode: "smooth",
    clock,
    nativeFetch: async () => upstream.response,
  });
  const wrapped = await window.fetch("http://127.0.0.1:7071/chat/stream", {
    method: "POST",
    body: JSON.stringify({ user_input: "hello" }),
  });

  upstream.enqueue(sse({ type: "delta", text: "partial text" }));
  await nextTask();
  upstream.error(new Error("upstream exploded"));

  const events = parseEvents(await readAll(wrapped.body.getReader()));
  assert.equal(
    events.filter((event) => event.type === "delta")
      .map((event) => event.text).join(""),
    "partial text",
  );
  assert.equal(events.at(-1).type, "error");
  assert.equal(events.at(-1).error, "upstream exploded");
});

test("non-stream chat and unrelated fetches remain untouched", async () => {
  const chatResponse = new Response('{"response":"ok"}');
  const healthResponse = new Response('{"status":"ok"}');
  const responses = [chatResponse, healthResponse];
  const { window } = installBridge({
    nativeFetch: async () => responses.shift(),
  });

  assert.strictEqual(
    await window.fetch("http://127.0.0.1:7071/chat", {
      method: "POST",
      body: JSON.stringify({ user_input: "hello" }),
    }),
    chatResponse,
  );
  assert.strictEqual(
    await window.fetch("http://127.0.0.1:7071/health"),
    healthResponse,
  );
});

test("aborting a smooth response cancels the upstream stream", async () => {
  const upstream = controlledResponse();
  const { window } = installBridge({
    chatStreamMode: "smooth",
    nativeFetch: async () => upstream.response,
  });
  const controller = new AbortController();
  const wrapped = await window.fetch("http://127.0.0.1:7071/chat/stream", {
    method: "POST",
    body: JSON.stringify({ user_input: "hello" }),
    signal: controller.signal,
  });
  const read = wrapped.body.getReader().read();

  controller.abort();

  await assert.rejects(read, (cause) => cause?.name === "AbortError");
  assert.equal(upstream.canceled, true);
  assert.equal(upstream.cancelReason?.name, "AbortError");
});
