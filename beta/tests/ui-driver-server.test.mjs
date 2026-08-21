import assert from "node:assert/strict";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  utimesSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import vm from "node:vm";

import {
  startUiDriverServer,
  uiDriverInternals,
} from "../electron/ui-driver-server.mjs";
import {
  measureUiDriver,
  shellFixture,
  shellInspectMeasurements,
} from "../scripts/measure-ui-driver-v2.mjs";

function fixtureElement({
  drive = "",
  id = "",
  tag = "button",
} = {}) {
  return {
    children: [],
    dataset: drive ? { drive } : {},
    getAttribute(name) {
      return name === "data-drive" ? drive || null : null;
    },
    id,
    localName: tag,
    parentElement: null,
  };
}

function append(parent, ...children) {
  for (const child of children) {
    child.parentElement = parent;
    parent.children.push(child);
  }
}

function fakeDriverWindow({ delayMs = 0 } = {}) {
  const executed = [];
  const execute = async (source) => {
    executed.push(source);
    if (delayMs) await new Promise((resolve) => setTimeout(resolve, delayMs));
    if (source.includes('"action":"click"')) {
      return {
        __trace: {
          snapshot_after: "oafter",
          snapshot_before: "obefore",
        },
        effect: {
          added: ["@brainstem.chat.msg[r-2]:streaming"],
          changed: [],
          removed: [],
          route: null,
        },
        h: "@brainstem.send",
        ok: true,
      };
    }
    if (source.includes('"action":"autopilot"')) {
      return {
        ok: true,
        ran: 1,
        results: [{ cmd: "help", ok: true }],
      };
    }
    return {
      __trace: {
        snapshot_after: "osteady",
        snapshot_before: "osteady",
      },
      actual: "enabled",
      h: "@brainstem.send",
      ok: true,
    };
  };
  const brainstem = {
    executeJavaScript: execute,
    frames: [],
    url: "http://127.0.0.1:7071/",
  };
  const mainFrame = {
    executeJavaScript: execute,
    frames: [brainstem],
    url: "file:///frontier/index.html",
  };
  return {
    executed,
    window: {
      webContents: { mainFrame },
    },
  };
}

function commandHeaders(token) {
  return {
    authorization: ["Bearer", token].join(" "),
    "content-type": "application/json",
  };
}

async function postCommand(metadata, command, token = metadata.token) {
  const response = await fetch(
    `http://${metadata.host}:${metadata.port}/v1/command`,
    {
      body: JSON.stringify(command),
      headers: commandHeaders(token),
      method: "POST",
    },
  );
  const text = await response.text();
  return {
    payload: JSON.parse(text.trim()),
    status: response.status,
    text,
  };
}

test("visible UI driver accepts bounded v2 actions", () => {
  assert.equal(
    uiDriverInternals.validateCommand({
      action: "run",
      steps: [
        { action: "announce", text: "Opening the beta menu" },
        {
          action: "click",
          handle: "@brainstem.send",
          until: { snapshot_changed: true },
        },
        { action: "expect", handle: "@brainstem.send", state: "enabled" },
        {
          action: "swipe",
          direction: "right",
          handle: "@herd.tile[tile-fixture]",
        },
      ],
    }).action,
    "run",
  );
  for (const action of [
    "recording_status",
    "route_telemetry",
    "set_chat_lease",
    "swipe",
  ]) {
    assert.equal(
      uiDriverInternals.validateCommand({ action }).action,
      action,
    );
  }
  assert.equal(
    uiDriverInternals.frameKeyForCommand({ action: "swipe" }),
    "brainstem",
  );
  assert.equal(
    uiDriverInternals.frameKeyForCommand({
      action: "swipe",
      target: "shell",
    }),
    "shell",
  );
});

test("visible UI driver rejects unknown and unbounded commands", () => {
  assert.throws(
    () => uiDriverInternals.validateCommand({ action: "evaluate" }),
    /Unsupported UI driver action/,
  );
  assert.throws(
    () => uiDriverInternals.validateCommand({ action: "run", steps: [] }),
    /between 1 and 40 steps/,
  );
  assert.throws(
    () => uiDriverInternals.validateCommand({
      action: "run",
      steps: Array.from({ length: 41 }, () => ({ action: "click" })),
    }),
    /between 1 and 40 steps/,
  );
  assert.throws(
    () => uiDriverInternals.validateCommand({ action: "inspect", limit: 81 }),
    /between 1 and 80/,
  );
});

test("visible UI driver bounds frame sleeps and typed input work", () => {
  for (const command of [
    { action: "announce", durationMs: 5_001 },
    { action: "click", selector: "#send", settleMs: 5_001 },
    { action: "press", key: "Enter", settleMs: 5_001 },
    { action: "type", selector: "#input", typingDelayMs: 101, value: "x" },
    {
      action: "type",
      selector: "#input",
      typingDelayMs: 100,
      value: "x".repeat(601),
    },
    {
      action: "type",
      selector: "#input",
      typingDelayMs: 0,
      value: "x".repeat((64 * 1024) + 1),
    },
    { action: "wait", selector: "#send", timeoutMs: 120_001 },
    { action: "click", selector: "#send", until: {
      handle: "@brainstem.send",
      state: "enabled",
      timeoutMs: 120_001,
    } },
    { action: "announce", frameTimeoutMs: 65 * 60 * 1000 + 1 },
    { action: "wait", selector: "#send", timeoutMs: 10_000, frameTimeoutMs: 1000 },
    {
      action: "run",
      steps: Array.from(
        { length: 40 },
        () => ({ action: "wait", selector: "#send", timeoutMs: 120_000 }),
      ),
    },
  ]) {
    assert.throws(
      () => uiDriverInternals.validateCommand(command),
      /must be|exceeds/,
    );
  }

  const instantType = uiDriverInternals.validateCommand({
    action: "type",
    selector: "#input",
    typingDelayMs: 0,
    value: "x".repeat(64 * 1024),
  });
  assert.equal(instantType.typingDelayMs, 0);
  assert.ok(
    instantType.frameTimeoutMs >= 20_000
      && instantType.frameTimeoutMs <= 65 * 60 * 1000,
  );
  assert.equal(
    uiDriverInternals.boundedFrameTimeout(1e15),
    65 * 60 * 1000,
  );
  const browserSource = uiDriverInternals.browserDriverCommand.toString();
  assert.match(browserSource, /frameBudget - 250/);
  assert.match(browserSource, /exceeded its frame time budget/);
  assert.match(
    browserSource,
    /if \(!delayMs\) \{[\s\S]*setControlValue\(element, nextValue\)/,
  );
});

test("handles resolve exactly and fallback selectors stay anchored", () => {
  const body = fixtureElement({ tag: "body" });
  const panel = fixtureElement({ drive: "shell.panel", tag: "section" });
  const group = fixtureElement({ tag: "div" });
  const first = fixtureElement();
  const second = fixtureElement();
  append(body, panel);
  append(panel, group);
  append(group, first, second);

  const elements = [panel, first, second];
  const document = {
    querySelector() {
      return null;
    },
    querySelectorAll(selector) {
      return selector === "[data-drive]" ? elements : [];
    },
  };
  const helpers = uiDriverInternals.createUiDriverHelpers({ document });
  assert.equal(helpers.resolveHandle("@shell.panel"), panel);
  assert.equal(
    helpers.selectorFor(first),
    '[data-drive="shell.panel"] > div > button:nth-of-type(1)',
  );
  assert.match(helpers.selectorFor(second), /^\[data-drive=/);
  assert.throws(
    () => helpers.resolveHandle("@shell.missing"),
    (error) => (
      error.name === "UiDriverHandleNotFoundError"
      && error.matches === 0
    ),
  );

  elements.push(fixtureElement({ drive: "shell.panel" }));
  assert.throws(
    () => helpers.resolveHandle("@shell.panel"),
    (error) => (
      error.name === "UiDriverHandleAmbiguityError"
      && error.matches === 2
    ),
  );
});

test("shell fixture produces compact deterministic outlines and diffs", () => {
  const fixture = shellFixture();
  const measurement = shellInspectMeasurements(fixture);
  const helpers = uiDriverInternals.createUiDriverHelpers();
  assert.ok(fixture.interactive.length > 0);
  assert.ok(fixture.interactive.every((item) => item.h.startsWith("@")));
  assert.ok(measurement.after.rows.length <= 60);
  assert.ok(measurement.afterBytes <= 2000);
  assert.doesNotMatch(JSON.stringify(measurement.after), /nth-of-type/);
  assert.equal(
    helpers.snapshotFor(measurement.after.rows),
    measurement.after.snapshot,
  );

  const before = measurement.after.rows.slice(0, 3);
  const after = [
    { ...before[0], state: "disabled" },
    before[1],
    {
      h: "@fixture[new].row",
      name: "New",
      role: "button",
      state: "enabled",
    },
  ];
  assert.deepEqual(helpers.diffOutlines(before, after), {
    added: ["@fixture[new].row:enabled"],
    changed: [`${before[0].h}:disabled`],
    removed: [before[2].h],
  });
  assert.deepEqual(
    helpers.diffRows(before, after).map((row) => [row.h, row.state]),
    [
      [before[0].h, "disabled"],
      ["@fixture[new].row", "enabled"],
      [before[2].h, "removed"],
    ],
  );
});

test("caps and byte budgets enforce the v2 ceilings", () => {
  const helpers = uiDriverInternals.createUiDriverHelpers();
  assert.equal(helpers.capNumber(200, 1, 80, 60), 80);
  assert.equal(helpers.capText("abcdef", 3), "abc");
  assert.equal(helpers.capText("abcdef", 3, { tail: true }), "def");
  const fitted = helpers.fitBudget(
    { text: "x".repeat(9000) },
    { handle: "@shell.agentTree", limit: 6000 },
  );
  assert.equal(fitted.truncated, true);
  assert.ok(fitted.bytes <= 6000);
  assert.match(
    fitted.value,
    /…\(\+\d+ bytes — read handle:@shell\.agentTree\)$/,
  );

  const measurements = measureUiDriver();
  assert.ok(measurements.inspect.after <= measurements.inspect.target);
  assert.ok(measurements.screenshot.after <= measurements.screenshot.target);
  assert.ok(measurements.read.after <= measurements.read.target);
  assert.ok(measurements.overhead.after <= measurements.overhead.target);
  assert.ok(measurements.overhead.detail.context <= 250);
});

test("real server enforces auth, body, heartbeat, conditions, and traces", async (t) => {
  const root = mkdtempSync(path.join(tmpdir(), "rapp-ui-driver-v2-"));
  const betaHome = path.join(root, "beta-home");
  const fake = fakeDriverWindow({ delayMs: 60 });
  const driver = await startUiDriverServer({
    brainstemHome: root,
    env: {
      BRAINSTEM_BETA_HOME: betaHome,
      BRAINSTEM_BETA_UI_DRIVER_HEARTBEAT_MS: "10",
    },
    loopbackUrl: (url) => url.startsWith("http://127.0.0.1:7071"),
    window: fake.window,
  });
  t.after(async () => {
    await driver.stop();
    rmSync(root, { force: true, recursive: true });
  });
  const metadata = JSON.parse(readFileSync(driver.metadataPath, "utf8"));
  assert.equal(metadata.version, 2);

  const unauthorized = await postCommand(
    metadata,
    { action: "expect", handle: "@brainstem.send", state: "enabled" },
    "wrong-token",
  );
  assert.equal(unauthorized.status, 401);

  const tooLarge = await postCommand(metadata, {
    action: "read",
    padding: "x".repeat((256 * 1024) + 1),
  });
  assert.equal(tooLarge.status, 400);
  assert.match(tooLarge.payload.error, /too large/);

  for (const invalid of [
    { action: "expect", handle: "@brainstem.send" },
    { action: "read", until: { snapshot_changed: true } },
    {
      action: "click",
      handle: "@brainstem.send",
      until: {
        handle: "@brainstem.send",
        state: "enabled",
        text: "Send",
      },
    },
  ]) {
    const response = await postCommand(metadata, invalid);
    assert.equal(response.status, 400);
  }

  const expected = await postCommand(metadata, {
    action: "expect",
    handle: "@brainstem.send",
    state: "enabled",
  });
  assert.equal(expected.status, 200);
  assert.deepEqual(expected.payload, {
    ok: true,
    result: {
      actual: "enabled",
      h: "@brainstem.send",
      ok: true,
    },
  });

  const autopilot = await postCommand(metadata, {
    action: "autopilot",
    script: "help",
  });
  assert.equal(autopilot.status, 200);
  assert.deepEqual(autopilot.payload, {
    ok: true,
    result: {
      ok: true,
      ran: 1,
      results: [{ cmd: "help", ok: true }],
    },
  });

  const effect = await postCommand(metadata, {
    action: "click",
    handle: "@brainstem.send",
    until: { snapshot_changed: true },
  });
  assert.equal(effect.status, 200);
  assert.equal(
    effect.payload.result.effect.added[0],
    "@brainstem.chat.msg[r-2]:streaming",
  );
  assert.equal(Object.hasOwn(effect.payload.result, "__trace"), false);

  const heartbeatResponse = await fetch(
    `http://${metadata.host}:${metadata.port}/v1/command`,
    {
      body: JSON.stringify({
        action: "expect",
        handle: "@brainstem.send",
        state: "enabled",
      }),
      headers: commandHeaders(metadata.token),
      method: "POST",
    },
  );
  const reader = heartbeatResponse.body.getReader();
  const decoder = new TextDecoder();
  const first = await reader.read();
  assert.equal(decoder.decode(first.value).trim(), "");
  let heartbeatBody = decoder.decode(first.value);
  while (true) {
    const chunk = await reader.read();
    if (chunk.done) break;
    heartbeatBody += decoder.decode(chunk.value);
  }
  assert.equal(JSON.parse(heartbeatBody.trim()).ok, true);

  const traces = readFileSync(metadata.tracePath, "utf8")
    .trim()
    .split("\n")
    .map((line) => JSON.parse(line));
  assert.ok(traces.length >= 3);
  const autopilotTrace = traces.find((entry) => entry.action === "autopilot");
  assert.deepEqual(autopilotTrace.commands, [{
    actor: null,
    cmd: "help",
    ok: true,
    reason: null,
  }]);
  for (const trace of traces) {
    const expectedKeys = [
      "action",
      "handle",
      "effect",
      "snapshot_before",
      "snapshot_after",
    ];
    if (trace.action === "autopilot") expectedKeys.push("actor", "commands");
    assert.deepEqual(Object.keys(trace), expectedKeys);
  }
  const clickTrace = traces.find((trace) => trace.action === "click");
  assert.equal(clickTrace.handle, "@brainstem.send");
  assert.equal(clickTrace.snapshot_before, "obefore");
  assert.equal(clickTrace.snapshot_after, "oafter");
});

test("visible chat waits for stable SSE replies and ignores prompt text", () => {
  const source = uiDriverInternals.browserDriverCommand.toString();
  assert.match(
    source,
    /\.msg\.assistant:not\(\.typing-indicator\):not\(\.stream-arriving\)/,
  );
  assert.match(source, /data-request-id/);
  assert.match(source, /chatLeaseLocked/);
  assert.match(source, /event\.isTrusted/);
  assert.match(source, /const errorBaseline = document\.querySelectorAll/);
  assert.match(source, /errors\.length > errorBaseline/);
  assert.match(source, /\.msg\.user,\[data-brainstem-ai-driver\]/);
  assert.doesNotMatch(
    source,
    /__rappSetNextAgentLease|__rappSetNextUserGuid|agentLease|userGuid/,
  );
});

test("driver UI opens off-canvas panels and clears faded narration", () => {
  const source = uiDriverInternals.browserDriverCommand.toString();
  assert.match(source, /if \(!panel\)/);
  assert.match(source, /panel\.classList\.add\("open"\)/);
  assert.match(source, /const CURSOR_IDLE_HIDE_MS = 4000/);
  assert.match(source, /clearTimeout\(state\.cursorIdleTimer\)/);
  assert.match(source, /cursor\.style\.opacity = "0"/);
  assert.match(source, /label\.textContent = ""/);
});

test("walkthrough recording pads with visible recap tiles", () => {
  const source = uiDriverInternals.stopWindowRecording.toString();
  assert.match(source, /minimumDurationMs/);
  assert.match(source, /brainstem-beta-walkthrough-recap/);
  assert.match(
    uiDriverInternals.walkthroughRecapChapters("baseline").join(" "),
    /Frontier Brainstem → Hippocampus → Microsoft stack/,
  );
  assert.match(
    uiDriverInternals.walkthroughRecapChapters("stack-churn").join(" "),
    /STACK_CHURN_READY/,
  );
});

test("long recordings stream to disk without base64 IPC", () => {
  const captureSource = uiDriverInternals.startCapturedWindowRecording.toString();
  const frameSource = uiDriverInternals.writeCapturedFrame.toString();
  const recorderSource = uiDriverInternals.startWindowRecording.toString();
  const serverSource = startUiDriverServer.toString();
  assert.match(frameSource, /capturePage/);
  assert.match(captureSource, /libvpx-vp9/);
  assert.match(captureSource, /image2pipe/);
  assert.match(captureSource, /framesWritten/);
  assert.match(recorderSource, /fetch\(state\.uploadUrl/);
  assert.match(recorderSource, /blob\.arrayBuffer/);
  assert.match(recorderSource, /video\/webm;codecs=vp8/);
  assert.match(serverSource, /\/v1\/recording-upload/);
  assert.match(serverSource, /createWriteStream/);
  assert.match(serverSource, /500 \* 1024 \* 1024/);
  assert.doesNotMatch(recorderSource, /FileReader|saveRecording|base64/);
});

test("a control inside its own overlay is actionable: an ancestor hit is not an occluder", () => {
  // Live regression: `click #enter` on the first-run intro returned ok:false
  // ("occluded by @shell.intro") because elementFromPoint reported the intro
  // tile — the button's own ancestor — and the walkthrough could no longer
  // dismiss the intro. Only something OUTSIDE the element's subtree and
  // ancestry occludes it.
  const source = uiDriverInternals.browserDriverCommand.toString();
  assert.match(source, /!element\.contains\(top\)\s*&&\s*!top\.contains\(element\)/);
  assert.match(source, /occluded by \$\{selectorFor\(top\)/);
});

test("click scrolls an offscreen control before testing for occlusion", async () => {
  const ids = new Map();
  const classList = () => {
    const names = new Set();
    return {
      add: (...values) => values.forEach((value) => names.add(value)),
      contains: (value) => names.has(value),
      remove: (...values) => values.forEach((value) => names.delete(value)),
    };
  };
  const uiElement = (tag) => ({
    classList: classList(),
    dataset: {},
    id: "",
    localName: tag,
    offsetWidth: 0,
    style: {},
    textContent: "",
  });
  let rect = { height: 32, left: 120, top: 2400, width: 180 };
  let clicks = 0;
  let scrolls = 0;
  const target = {
    classList: classList(),
    click() {
      clicks += 1;
    },
    contains: (element) => element === target,
    dataset: { drive: "list.below" },
    disabled: false,
    focus() {},
    getAttribute: () => null,
    getBoundingClientRect: () => rect,
    innerText: "Below the fold",
    localName: "button",
    scrollIntoView() {
      scrolls += 1;
      rect = { ...rect, top: 280 };
    },
  };
  const footer = {
    contains: () => false,
    localName: "footer",
  };
  const append = (element) => {
    if (element.id) ids.set(element.id, element);
  };
  const document = {
    activeElement: target,
    body: { appendChild: append },
    createElement: uiElement,
    elementFromPoint: () => (rect.top > 700 ? footer : target),
    getElementById: (id) => ids.get(id) || null,
    head: { appendChild: append },
    querySelectorAll: () => [],
  };
  const helpers = {
    buildOutline: () => ({ rows: [], snapshot: "steady" }),
    caps: { inspectDefault: 60 },
    diffOutlines: () => ({ added: [], changed: [], removed: [] }),
    resolveSelector: () => target,
    selectorFor: (element) => (
      element === target ? "@list.below" : element?.localName || null
    ),
  };
  const context = vm.createContext({
    CSS: { escape: (value) => value },
    clearTimeout() {},
    document,
    getComputedStyle: () => ({
      display: "block",
      opacity: "1",
      pointerEvents: "auto",
      visibility: "visible",
    }),
    innerHeight: 700,
    innerWidth: 1000,
    location: { href: "http://127.0.0.1:7071/" },
    setTimeout(callback) {
      callback();
      return 1;
    },
    window: {},
  });
  const command = vm.runInContext(
    `(${uiDriverInternals.browserDriverCommand.toString()})`,
    context,
  );

  const result = await command(
    { action: "click", selector: "#below" },
    () => helpers,
  );

  assert.equal(result.ok, true);
  assert.equal(clicks, 1);
  assert.equal(scrolls, 1);
});

test("a frame script is abandoned when its frame navigates, and the queue moves on", async () => {
  const { executeInFrame, FrameGoneError } = uiDriverInternals;
  const navigating = {
    executeJavaScript: () => new Promise(() => {}),
    frames: [],
    url: "http://127.0.0.1:7071/",
  };
  const mainFrame = { executeJavaScript: () => null, frames: [navigating], url: "file:///frontier/index.html" };
  const window = { webContents: { mainFrame } };
  setTimeout(() => { navigating.url = "http://127.0.0.1:7072/"; }, 120);
  const started = Date.now();
  await assert.rejects(
    executeInFrame(navigating, "1", { window, timeoutMs: 10_000 }),
    (error) => error instanceof FrameGoneError && /navigated/.test(error.message) && error.retryable === true,
  );
  assert.ok(Date.now() - started < 2_000, "the abandoned script must not wait for the deadline");

  const destroyed = {
    executeJavaScript: () => new Promise(() => {}),
    frames: [],
    isDestroyed: () => false,
    url: "http://127.0.0.1:7071/",
  };
  setTimeout(() => { destroyed.isDestroyed = () => true; }, 120);
  await assert.rejects(
    executeInFrame(destroyed, "1", { window: null, timeoutMs: 10_000 }),
    (error) => error instanceof FrameGoneError && /destroyed/.test(error.message),
  );

  const slow = { executeJavaScript: () => new Promise(() => {}), frames: [], url: "http://127.0.0.1:7071/" };
  await assert.rejects(
    executeInFrame(slow, "1", { window: null, timeoutMs: 300 }),
    /did not finish within/,
  );
});

test("a wedged frame command does not block the next command on the same frame", async () => {
  const root = mkdtempSync(path.join(tmpdir(), "ui-driver-wedge-"));
  const betaHome = path.join(root, "beta-launcher");
  let calls = 0;
  const brainstem = {
    executeJavaScript: () => {
      calls += 1;
      if (calls === 1) {
        // The route swaps underneath the first command: Electron never settles it.
        setTimeout(() => { brainstem.url = "http://127.0.0.1:7072/"; }, 150);
        return new Promise(() => {});
      }
      return Promise.resolve({ h: "@brainstem.composer", ok: true, text: "ready" });
    },
    frames: [],
    url: "http://127.0.0.1:7071/",
  };
  const mainFrame = { executeJavaScript: () => 0, frames: [brainstem], url: "file:///frontier/index.html" };
  const driver = await startUiDriverServer({
    brainstemHome: root,
    env: { BRAINSTEM_BETA_HOME: betaHome, BRAINSTEM_BETA_UI_DRIVER_HEARTBEAT_MS: "10" },
    loopbackUrl: (url) => url.startsWith("http://127.0.0.1:707"),
    window: { webContents: { mainFrame } },
  });
  try {
    const metadata = JSON.parse(readFileSync(path.join(betaHome, "ui-driver.json"), "utf8"));
    const started = Date.now();
    const [first, second] = await Promise.all([
      postCommand(metadata, { action: "read", selector: "#input" }),
      postCommand(metadata, { action: "read", selector: "#input" }),
    ]);
    // HTTP arrival order is not guaranteed, and the bus always answers 200 once
    // its headers are flushed; the verdict lives in the payload. Exactly one
    // command rode the navigating frame and was abandoned; the other ran on
    // the new frame.
    const payloads = [first.payload, second.payload];
    const detail = JSON.stringify(payloads);
    const abandoned = payloads.filter((payload) => payload.ok === false);
    const served = payloads.filter((payload) => payload.ok === true);
    assert.equal(abandoned.length, 1, detail);
    assert.match(abandoned[0].error, /navigated/, detail);
    assert.equal(served.length, 1, detail);
    assert.equal(served[0].result?.text, "ready", detail);
    assert.ok(Date.now() - started < 5_000, "the second command must not wait behind the wedged one");
    assert.equal(calls, 2);
  } finally {
    await driver.stop();
    rmSync(root, { force: true, recursive: true });
  }
});

test("persisted UI driver traces redact errors and rotate within bounded retention", async (t) => {
  const root = mkdtempSync(path.join(tmpdir(), "ui-driver-trace-cap-"));
  const betaHome = path.join(root, "beta-launcher");
  t.after(() => rmSync(root, { force: true, recursive: true }));
  const fakeToken = `ghp_${"A".repeat(36)}`;
  const oversized = `token=${fakeToken} ${"x".repeat(100 * 1024)}`;
  const logDir = path.join(betaHome, "logs");
  mkdirSync(logDir, { recursive: true });
  const now = Date.now();
  for (let index = 1; index <= 25; index += 1) {
    const file = path.join(logDir, `ui-driver-old-${index}.jsonl`);
    writeFileSync(file, "{}\n");
    const when = new Date(now - index * 60 * 60 * 1000);
    utimesSync(file, when, when);
  }
  const brainstem = {
    executeJavaScript: async () => {
      throw new Error(`UI target not found: ${oversized}`);
    },
    frames: [],
    url: "http://127.0.0.1:7071/",
  };
  const mainFrame = {
    executeJavaScript: async () => null,
    frames: [brainstem],
    url: "file:///frontier/index.html",
  };
  const driver = await startUiDriverServer({
    brainstemHome: root,
    env: {
      BRAINSTEM_BETA_HOME: betaHome,
      BRAINSTEM_BETA_UI_DRIVER_TRACE_MAX_BYTES: "1024",
    },
    loopbackUrl: (url) => url.startsWith("http://127.0.0.1:707"),
    window: { webContents: { mainFrame } },
  });
  t.after(() => driver.stop());
  const metadata = JSON.parse(readFileSync(driver.metadataPath, "utf8"));
  assert.equal(
    readdirSync(logDir)
      .filter((name) => /^ui-driver-.*\.jsonl(?:\.\d+)?$/.test(name))
      .length,
    20,
  );

  let response;
  for (let attempt = 0; attempt < 2; attempt += 1) {
    response = await postCommand(metadata, {
      action: "read",
      selector: oversized,
    });
    assert.equal(response.payload.ok, false);
  }

  const [trace] = readFileSync(metadata.tracePath, "utf8")
    .trim()
    .split("\n")
    .map((line) => JSON.parse(line));
  assert.ok(trace.effect.error.length <= 2000);
  assert.ok(readFileSync(metadata.tracePath).byteLength < 5000);
  assert.ok(existsSync(`${metadata.tracePath}.1`));
  const persisted = [
    readFileSync(metadata.tracePath, "utf8"),
    readFileSync(`${metadata.tracePath}.1`, "utf8"),
  ].join("\n");
  assert.doesNotMatch(persisted, /ghp_/);
  assert.doesNotMatch(persisted, new RegExp(fakeToken));
  assert.match(persisted, /\[redacted:token\]/);
  assert.equal(
    readdirSync(logDir)
      .filter((name) => /^ui-driver-.*\.jsonl(?:\.\d+)?$/.test(name))
      .length,
    21,
  );
});

test("the chat lease's aria-disabled marker does not make the send button unactionable for the driver", () => {
  const source = uiDriverInternals.browserDriverCommand.toString();
  assert.match(source, /rappChatLease === "locked"/);
  assert.match(source, /\(!leaseMarked && element\.getAttribute\?\.\("aria-disabled"\) === "true"\)/);
  assert.match(source, /send\.dataset\.rappChatLease = "locked"/);
});

test("the frame watchdog budget follows the command's own budget, never truncating a healthy chat", () => {
  const { frameBudgetMs, stepBudgetMs } = uiDriverInternals;
  // a delegated chat with a 60 s budget gets that plus grace
  assert.ok(frameBudgetMs({ action: "chat", timeoutMs: 60_000 }) >= 75_000);
  // the in-frame default for chat is 180 s, so the watchdog must not fire at 20 s
  assert.ok(frameBudgetMs({ action: "chat" }) >= 180_000);
  // a one-hour chat is honoured (capped at one hour plus grace)
  assert.ok(frameBudgetMs({ action: "chat", timeoutMs: 3_600_000 }) >= 3_600_000);
  assert.ok(frameBudgetMs({ action: "chat", timeoutMs: 99_999_999 }) <= 3_600_000 + 30_000);
  // The visible Surgeon itself defaults to a one-hour wait.
  assert.ok(frameBudgetMs({ action: "surgeon_chat" }) >= 3_600_000);
  // a run adds up its steps: typing 2000 chars at 18 ms is 36 s of legitimate work
  const typing = frameBudgetMs({ action: "run", steps: [{ action: "type", value: "x".repeat(2000) }, { action: "click", settleMs: 500 }] });
  assert.ok(typing >= 36_000 + 500);
  // a quick read keeps the 20 s floor
  assert.equal(frameBudgetMs({ action: "read", selector: "#input" }), 20_000);
  // an explicit frameTimeoutMs still wins
  assert.equal(frameBudgetMs({ action: "chat", frameTimeoutMs: 1234 }), 1234);
  assert.equal(stepBudgetMs({ action: "wait", timeoutMs: 999_999 }), 120_000);
});

test("a frame script abandoned by the watchdog stops at its next tick when a later command takes the frame", () => {
  const source = uiDriverInternals.browserDriverCommand.toString();
  assert.match(source, /state\.activeCommandId = myCommandId/);
  assert.match(source, /if \(state\.activeCommandId !== myCommandId\)/);
  assert.match(source, /UiDriverSupersededError/);
  // the id rides beside the command, not inside it (traces stay identical pass to pass)
  const server = readFileSync(new URL("../electron/ui-driver-server.mjs", import.meta.url), "utf8");
  assert.match(server, /createUiDriverHelpers\.toString\(\)\}, \$\{JSON\.stringify\(commandId\)\}, \$\{/);
  assert.match(server, /timeoutMs: frameBudgetMs\(command\)/);
});

test("every script sent to the Brainstem or a twin frame goes through the watchdog", () => {
  const server = readFileSync(new URL("../electron/ui-driver-server.mjs", import.meta.url), "utf8");
  // the only bare frame.executeJavaScript( is the one inside executeInFrame itself
  const bare = server.match(/[^.\w]frame\.executeJavaScript\(/g) || [];
  assert.equal(bare.length, 1, `bare frame.executeJavaScript calls: ${bare.length}`);
  assert.doesNotMatch(server, /activeFrame\.executeJavaScript\(/);
  assert.doesNotMatch(server, /target\.executeJavaScript\(/);
});

test("a trace that cannot be written does not turn a finished command into a failure", async () => {
  const root = mkdtempSync(path.join(tmpdir(), "ui-driver-trace-"));
  const betaHome = path.join(root, "beta-launcher");
  mkdirSync(betaHome, { recursive: true });
  // `logs` is a FILE, so every trace append fails with ENOTDIR/EEXIST
  writeFileSync(path.join(betaHome, "logs"), "not a directory\n");
  const brainstem = {
    executeJavaScript: () => Promise.resolve({ h: "@brainstem.composer", ok: true, text: "ready" }),
    frames: [],
    url: "http://127.0.0.1:7071/",
  };
  const mainFrame = { executeJavaScript: () => 0, frames: [brainstem], url: "file:///frontier/index.html" };
  const driver = await startUiDriverServer({
    brainstemHome: root,
    env: { BRAINSTEM_BETA_HOME: betaHome, BRAINSTEM_BETA_UI_DRIVER_HEARTBEAT_MS: "10" },
    loopbackUrl: (url) => url.startsWith("http://127.0.0.1:7071"),
    window: { webContents: { mainFrame } },
  });
  try {
    const metadata = JSON.parse(readFileSync(path.join(betaHome, "ui-driver.json"), "utf8"));
    const { payload } = await postCommand(metadata, { action: "read", selector: "#input" });
    assert.equal(payload.ok, true, JSON.stringify(payload));
    assert.equal(payload.result?.text, "ready");
    assert.match(String(payload.trace_error || ""), /ENOTDIR|EEXIST|ENOENT|not a directory/i);
  } finally {
    await driver.stop();
    rmSync(root, { force: true, recursive: true });
  }
});

test("outline state treats the driver-owned leased send button as enabled", () => {
  const helpers = uiDriverInternals.createUiDriverHelpers();
  const send = {
    dataset: { rappChatLease: "locked" },
    disabled: false,
    getAttribute: (name) => (name === "aria-disabled" ? "true" : null),
    localName: "button",
  };

  assert.equal(helpers.stateFor(send), "enabled");
  delete send.dataset.rappChatLease;
  assert.equal(helpers.stateFor(send), "disabled");
});

test("the chat lease blocks trusted starter-prompt clicks", async () => {
  const elements = new Map();
  const eventTarget = (id) => {
    const listeners = new Map();
    const element = {
      addEventListener(type, listener) {
        listeners.set(type, listener);
      },
      dataset: {},
      id,
      listeners,
      setAttribute() {},
    };
    elements.set(id, element);
    return element;
  };
  eventTarget("input");
  eventTarget("send");
  const starters = eventTarget("starter-prompts");
  const document = {
    activeElement: null,
    body: {
      appendChild(element) {
        elements.set(element.id, element);
      },
    },
    createElement: () => ({
      dataset: {},
      hidden: false,
      id: "",
      style: {},
      textContent: "",
    }),
    getElementById: (id) => elements.get(id) || null,
    querySelectorAll: () => [],
  };
  const helpers = {
    buildOutline: () => ({ rows: [], snapshot: "steady" }),
    caps: { inspectDefault: 60 },
    diffOutlines: () => ({ added: [], changed: [], removed: [] }),
    selectorFor: () => null,
  };
  const context = vm.createContext({
    document,
    setTimeout,
    window: {},
  });
  const command = vm.runInContext(
    `(${uiDriverInternals.browserDriverCommand.toString()})`,
    context,
  );
  await command(
    { action: "set_chat_lease", locked: true, token: "delegate" },
    () => helpers,
  );
  const trustedClick = {
    isTrusted: true,
    preventDefaultCalled: false,
    stopImmediatePropagationCalled: false,
    preventDefault() {
      this.preventDefaultCalled = true;
    },
    stopImmediatePropagation() {
      this.stopImmediatePropagationCalled = true;
    },
  };

  starters.listeners.get("click")(trustedClick);

  assert.equal(trustedClick.preventDefaultCalled, true);
  assert.equal(trustedClick.stopImmediatePropagationCalled, true);

  trustedClick.isTrusted = false;
  trustedClick.preventDefaultCalled = false;
  trustedClick.stopImmediatePropagationCalled = false;
  starters.listeners.get("click")(trustedClick);
  assert.equal(trustedClick.preventDefaultCalled, false);
  assert.equal(trustedClick.stopImmediatePropagationCalled, false);
});
