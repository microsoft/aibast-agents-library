import assert from "node:assert/strict";
import {
  existsSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
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
  assert.equal(race.contender.turns.at(-1).pending, true);
  const completed = store.complete(race.contender.id, {
    reply: "The contender replied.",
    html: "<p>The contender replied.</p>",
  });
  assert.equal(completed.turns.at(-1).pending, undefined);
  assert.equal(completed.history.at(-1).content, "The contender replied.");

  store.wake(original.id);
  assert.equal(store.read(original.id).status, "primary");
  assert.equal(store.read(race.contender.id).status, "folded");
});

test("race refuses a card whose last user turn is not a question", (t) => {
  const { store } = fixtureStore(t);
  const card = store.park(cardFixture("Build the answer."));
  assert.throws(() => store.race(card.id), /last user turn is a question/);
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

test("card IPC is trusted and inert while April Fools mode is off", async (t) => {
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
    "beta:cards-race",
    "beta:cards-undo",
    "beta:cards-wake",
  ]);
  assert.throws(() => handlers.get("beta:cards-list")({}), /card table is off/);
  enabled = true;
  assert.deepEqual(handlers.get("beta:cards-list")({}), []);
  assert.equal(trusted, 2);
});
