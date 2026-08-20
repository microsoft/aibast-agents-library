import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";

const mainSource = readFileSync(
  new URL("../electron/main.mjs", import.meta.url),
  "utf8",
);

function materializeBridgeSource(chatTypingEnabled) {
  const declaration = "const BETA_FRAME_BRIDGE_SOURCE =";
  const declarationStart = mainSource.indexOf(declaration);
  const expressionStart = mainSource.indexOf("=", declarationStart) + 1;
  const expressionEnd = mainSource.indexOf(";\nconst copilot =", expressionStart);
  assert.ok(declarationStart >= 0 && expressionStart > 0 && expressionEnd > expressionStart);
  return vm.runInNewContext(
    mainSource.slice(expressionStart, expressionEnd),
    {
      chatTypingEnabled,
      exportRedactionSource: "",
      humanizeAgentName: (value) => String(value),
    },
  );
}

function createElement() {
  return {
    append: () => {},
    appendChild: () => {},
    classList: {
      add: () => {},
      contains: () => false,
      toggle: () => {},
    },
    dataset: {},
    querySelector: () => null,
    querySelectorAll: () => [],
    removeAttribute: () => {},
    setAttribute: () => {},
    style: {},
  };
}

function installBridge({ chatTypingEnabled = true, nativeFetch }) {
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
  const document = {
    addEventListener: () => {},
    body: createElement(),
    createElement,
    getElementById: () => null,
    head: createElement(),
    querySelector: () => null,
    querySelectorAll: () => [],
  };
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
    TextDecoder,
    TextEncoder,
    URL,
    window,
  });
  vm.runInContext(materializeBridgeSource(chatTypingEnabled), context);
  return window;
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

test("frame bridge emits zero bytes before completion, then replays ordered SSE", async () => {
  const upstream = controlledResponse();
  const window = installBridge({
    nativeFetch: async () => upstream.response,
  });
  const wrapped = await window.fetch("http://127.0.0.1:7071/chat/stream", {
    method: "POST",
    body: JSON.stringify({ user_input: "hello" }),
  });

  assert.notStrictEqual(wrapped, upstream.response);
  assert.equal(wrapped.status, 202);
  assert.equal(wrapped.statusText, "Accepted");
  assert.equal(wrapped.headers.get("cache-control"), "no-cache, no-transform");
  assert.equal(wrapped.headers.get("content-type"), "text/event-stream; charset=utf-8");
  assert.equal(wrapped.headers.get("x-frontier-test"), "preserved");

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
  console.log("0 bytes before completion");

  upstream.close();
  const replay = await readAll(reader, firstRead);
  assert.equal(replay, frames.join(""));
  const events = parseEvents(replay);
  assert.deepEqual(
    events.map((event) => event.type),
    ["delta", "delta", "delta", "done"],
  );
  assert.deepEqual(
    events.filter((event) => event.type === "delta").map((event) => event.text),
    ["one", " two", " three"],
  );
  console.log("ordered replay: delta one -> delta two -> delta three -> done");
});

test("frame bridge flushes buffered SSE followed by an error event", async () => {
  const upstream = controlledResponse();
  const window = installBridge({
    nativeFetch: async () => upstream.response,
  });
  const wrapped = await window.fetch("http://127.0.0.1:7071/chat/stream", {
    method: "POST",
    body: JSON.stringify({ user_input: "hello" }),
  });
  const reader = wrapped.body.getReader();
  const firstRead = reader.read();
  upstream.enqueue(sse({ type: "delta", text: "partial" }));
  await nextTask();
  upstream.error(new Error("upstream exploded"));

  const events = parseEvents(await readAll(reader, firstRead));
  assert.deepEqual(events.map((event) => event.type), ["delta", "error"]);
  assert.equal(events[0].text, "partial");
  assert.equal(events[1].error, "upstream exploded");
});

test("frame bridge passes streaming responses through when typing delivery is off", async () => {
  const upstream = controlledResponse();
  const window = installBridge({
    chatTypingEnabled: false,
    nativeFetch: async () => upstream.response,
  });
  const response = await window.fetch("http://127.0.0.1:7071/chat/stream", {
    method: "POST",
    body: JSON.stringify({ user_input: "hello" }),
  });

  assert.strictEqual(response, upstream.response);
});

test("frame bridge leaves non-stream chat and unrelated fetches untouched", async () => {
  const chatResponse = new Response('{"response":"ok"}');
  const healthResponse = new Response('{"status":"ok"}');
  const responses = [chatResponse, healthResponse];
  const window = installBridge({
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

test("aborting a buffered bridge response cancels the upstream stream", async () => {
  const upstream = controlledResponse();
  const window = installBridge({
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
