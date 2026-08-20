import assert from "node:assert/strict";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
  CHAT_CARD_SCHEMA,
  ChatCardStore,
  MAX_CHAT_CARD_BYTES,
  MAX_CHAT_CARD_TURNS,
  registerChatCardIpc,
} from "../electron/chat-cards.mjs";

function fixtureStore(t, options = {}) {
  const betaHome = mkdtempSync(path.join(tmpdir(), "rapp-card-store-"));
  t.after(() => rmSync(betaHome, { recursive: true, force: true }));
  let sequence = 0;
  const store = new ChatCardStore({
    betaHome,
    idFactory: () => `card-fixture-${String(++sequence).padStart(3, "0")}`,
    ...options,
  });
  return { betaHome, store };
}

function cardFixture(question = "What should we build?") {
  const at = "2026-08-20T20:00:00.000Z";
  return {
    title: question,
    route: {
      url: "http://127.0.0.1:7071",
      rappid: "rappid:@frontier/default:abc",
      compositionHash: "abc",
      model: "auto",
    },
    turns: [
      { role: "user", text: question, html: question, at },
      {
        role: "assistant",
        text: "A useful answer.",
        html: "<p>A useful answer.</p>",
        at,
      },
    ],
    history: [
      { role: "user", content: question },
      { role: "assistant", content: "A useful answer." },
    ],
  };
}

test("card store parks atomic 0600 schema files and lists them by seat", (t) => {
  const { betaHome, store } = fixtureStore(t);
  const first = store.park(cardFixture());
  const second = store.park(cardFixture("Which model should race?"));

  assert.equal(first.schema, CHAT_CARD_SCHEMA);
  assert.equal(first.status, "parked");
  assert.equal(first.table.seat, 1);
  assert.equal(second.table.seat, 2);
  assert.equal(first.title, "What should we build?");
  assert.deepEqual(store.list().map((card) => card.id).sort(), [
    first.id,
    second.id,
  ].sort());

  const directory = path.join(betaHome, "cards");
  const file = path.join(directory, `${first.id}.json`);
  assert.equal(existsSync(file), true);
  assert.equal(JSON.parse(readFileSync(file, "utf8")).schema, CHAT_CARD_SCHEMA);
  assert.equal(
    readdirSync(directory).some((name) => name.endsWith(".tmp")),
    false,
  );
  if (process.platform !== "win32") {
    assert.equal(statSync(directory).mode & 0o777, 0o700);
    assert.equal(statSync(file).mode & 0o777, 0o600);
  }
});

test("fold keeps the card, undo lasts ten seconds, and wake picks a primary", (t) => {
  let now = new Date("2026-08-20T20:00:00.000Z");
  const { betaHome, store } = fixtureStore(t, { now: () => now });
  const first = store.park(cardFixture());
  const second = store.park(cardFixture("Can a second card win?"));

  const folded = store.fold(first.id);
  assert.equal(folded.card.status, "folded");
  assert.equal(folded.card.table.faceUp, false);
  assert.equal(existsSync(path.join(betaHome, "cards", `${first.id}.json`)), true);
  assert.equal(store.undo(first.id).status, "parked");

  store.fold(first.id);
  now = new Date(now.getTime() + 10_001);
  assert.throws(() => store.undo(first.id), /undo window has expired/);

  assert.equal(store.wake(second.id).status, "primary");
  assert.equal(store.read(first.id).status, "folded");
});

test("race creates a pending contender and waking a winner folds its rival", (t) => {
  const { store } = fixtureStore(t);
  const original = store.park(cardFixture("Which answer wins?"));
  const race = store.race(original.id);

  assert.equal(race.question, "Which answer wins?");
  assert.equal(race.source.status, "racing");
  assert.equal(race.contender.status, "racing");
  assert.equal(race.source.raceId, race.contender.raceId);
  assert.throws(
    () => store.race(race.source.id),
    /already in an unresolved race/,
  );
  assert.equal(race.contender.turns.at(-1).pending, true);
  const completed = store.complete(race.contender.id, {
    reply: "The contender replied.",
    html: "<p>The contender replied.</p>",
    requestId: "request-fixture-1",
  });

  assert.equal(completed.turns.at(-1).pending, undefined);
  assert.equal(completed.history.at(-1).content, "The contender replied.");
  const duplicate = store.complete(race.contender.id, {
    reply: "The contender replied.",
    html: "<p>The contender replied.</p>",
    requestId: "request-fixture-1",
  });
  assert.equal(duplicate.history.length, completed.history.length);

  store.wake(original.id);
  assert.equal(store.read(original.id).status, "primary");
  assert.equal(store.read(race.contender.id).status, "folded");
});

// These two were nested inside the race test above; Node cancels nested
// subtests when the parent finishes first ("cancelledByParent" on Windows).
test("a race winner folds only its paired rival", (t) => {
  let raceSequence = 0;
  const { store } = fixtureStore(t, {
    raceIdFactory: () => `race-fixture-${++raceSequence}`,
  });
  const first = store.race(store.park(cardFixture("First race?")).id);
  const second = store.race(store.park(cardFixture("Second race?")).id);

  store.wake(first.source.id);
  assert.equal(store.read(first.contender.id).status, "folded");
  assert.equal(store.read(second.source.id).status, "racing");
  assert.equal(store.read(second.contender.id).status, "racing");
});

test("a non-restorable transcript reports the reason instead of waking", (t) => {
  const { store } = fixtureStore(t);
  const card = store.park({
    ...cardFixture(),
    restorable: false,
    restoreError: "Exact wire history was not observed.",
  });
  assert.equal(card.restorable, false);
  assert.throws(() => store.wake(card.id), /wire history was not observed/);
});

test("race refuses a card whose last user turn is not a question", (t) => {
  const { store } = fixtureStore(t);
  const card = store.park(cardFixture("Build the answer."));
  assert.throws(() => store.race(card.id), /last user turn is a question/);
});

test("concurrent pending replies reconcile by request id", (t) => {
  const { store } = fixtureStore(t);
  const at = "2026-08-20T20:00:00.000Z";
  const card = store.park({
    title: "Concurrent card",
    route: cardFixture().route,
    turns: [
      { role: "user", text: "First?", html: "", at, requestId: "request-1" },
      {
        role: "assistant",
        text: "Waiting for reply...",
        html: "",
        at,
        pending: true,
        requestId: "request-1",
      },
      { role: "user", text: "Second?", html: "", at, requestId: "request-2" },
      {
        role: "assistant",
        text: "Waiting for reply...",
        html: "",
        at,
        pending: true,
        requestId: "request-2",
      },
    ],
    history: [
      { role: "user", content: "First?", requestId: "request-1" },
      { role: "user", content: "Second?", requestId: "request-2" },
    ],
  });

  store.complete(card.id, {
    reply: "Second answer.",
    requestId: "request-2",
  });
  const completed = store.complete(card.id, {
    reply: "First answer.",
    requestId: "request-1",
  });
  assert.deepEqual(
    completed.turns.map((turn) => [turn.text, turn.pending]),
    [
      ["First?", undefined],
      ["First answer.", undefined],
      ["Second?", undefined],
      ["Second answer.", undefined],
    ],
  );
  assert.deepEqual(
    completed.history.map((message) => [message.role, message.content]),
    [
      ["user", "First?"],
      ["assistant", "First answer."],
      ["user", "Second?"],
      ["assistant", "Second answer."],
    ],
  );
  assert(completed.history.every((message) => !("requestId" in message)));
});

test("card store enforces turn and 256 KiB caps before writing", (t) => {
  const { betaHome, store } = fixtureStore(t);
  const oversizedTurns = Array.from(
    { length: MAX_CHAT_CARD_TURNS + 1 },
    (_, index) => ({
      role: index % 2 ? "assistant" : "user",
      text: `turn ${index}`,
      html: "",
      at: "2026-08-20T20:00:00.000Z",
    }),
  );
  assert.throws(
    () => store.park({ ...cardFixture(), turns: oversizedTurns }),
    new RegExp(`${MAX_CHAT_CARD_TURNS} transcript turns`),
  );
  assert.throws(
    () => store.park({
      ...cardFixture(),
      turns: [{
        role: "user",
        text: "x".repeat(MAX_CHAT_CARD_BYTES),
        html: "",
        at: "2026-08-20T20:00:00.000Z",
      }],
    }),
    new RegExp(`${MAX_CHAT_CARD_BYTES} bytes`),
  );
  assert.equal(
    existsSync(path.join(betaHome, "cards", "card-fixture-001.json")),
    false,
  );
});

test("oversized or invalid on-disk cards are reported without hiding valid cards", (t) => {
  const { betaHome, store } = fixtureStore(t);
  const valid = store.park(cardFixture());
  const invalidId = "card-invalid-oversized";
  const directory = path.join(betaHome, "cards");
  mkdirSync(directory, { recursive: true });
  writeFileSync(
    path.join(directory, `${invalidId}.json`),
    " ".repeat(MAX_CHAT_CARD_BYTES + 1),
  );

  assert.throws(() => store.read(invalidId), /exceeds the 262144 byte limit/);
  const cards = store.list();
  assert(cards.some((card) => card.id === valid.id && card.restorable));
  const unavailable = cards.find((card) => card.id === invalidId);
  assert.equal(unavailable.restorable, false);
  assert.match(unavailable.restoreError, /exceeds the 262144 byte limit/);
});

test("card IPC is inert off except identified durable completions", async (t) => {
  const { store } = fixtureStore(t);
  const handlers = new Map();
  let trusted = 0;
  let enabled = false;
  registerChatCardIpc({
    assertTrustedIpc: () => { trusted += 1; },
    ipcMain: {
      handle(name, handler) {
        handlers.set(name, handler);
      },
    },
    isEnabled: () => enabled,
    store,
  });

  assert.deepEqual([...handlers.keys()].sort(), [
    "beta:cards-complete",
    "beta:cards-fold",
    "beta:cards-list",
    "beta:cards-park",
    "beta:cards-park-existing",
    "beta:cards-race",
    "beta:cards-undo",
    "beta:cards-wake",
  ]);
  assert.throws(() => handlers.get("beta:cards-list")({}), /card table is off/);
  const pending = store.park({
    ...cardFixture(),
    turns: [
      ...cardFixture().turns.slice(0, 1),
      {
        role: "assistant",
        text: "Waiting for reply...",
        html: "",
        at: "2026-08-20T20:00:00.000Z",
        pending: true,
        requestId: "request-off-1",
      },
    ],
    history: [{
      role: "user",
      content: "What should we build?",
      requestId: "request-off-1",
    }],
  });
  const completedOff = handlers.get("beta:cards-complete")(
    {},
    pending.id,
    {
      reply: "Durable while off.",
      requestId: "request-off-1",
    },
  );
  assert.equal(completedOff.history.at(-1).content, "Durable while off.");
  assert.throws(
    () => handlers.get("beta:cards-complete")(
      {},
      pending.id,
      { reply: "Unexpected.", requestId: "request-off-2" },
    ),
    /existing pending card/,
  );
  enabled = true;
  assert.equal(
    handlers.get("beta:cards-park-existing")({}, pending.id).status,
    "parked",
  );
  assert.equal(handlers.get("beta:cards-list")({})[0].id, pending.id);
  assert.equal(trusted, 5);
});
