import assert from "node:assert/strict";
import {
  existsSync,
  readFileSync,
  readdirSync,
} from "node:fs";
import path from "node:path";

import { launch } from "./harness/launch.mjs";
import { frontierTest } from "./harness/test-support.mjs";

const QUESTION = "Which path wins?";
const FIRST_REPLY = "FIRST_CARD_REPLY: preserve the delayed dimension.";
const SECOND_REPLY = "SECOND_CARD_REPLY: compare a fresh dimension.";
const FOLLOW_UP = "What did the first dimension answer?";
const FOLLOW_UP_REPLY = "FOLLOW_UP_REPLY: the first history was restored.";
const CHECKPOINT_OUTLINE = JSON.parse(readFileSync(
  new URL("./fixtures/frontier-checkpoint-herd-outline.json", import.meta.url),
  "utf8",
));

async function waitFor(predicate, {
  intervalMs = 100,
  label = "condition",
  timeoutMs = 20_000,
} = {}) {
  const deadline = Date.now() + timeoutMs;
  let lastError = null;
  while (Date.now() < deadline) {
    try {
      const value = await predicate();
      if (value) return value;
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
  throw new Error(
    `Timed out waiting for ${label}: ${String(lastError?.message || lastError || "")}`,
  );
}

function readCards(cardsDirectory) {
  if (!existsSync(cardsDirectory)) return [];
  return readdirSync(cardsDirectory)
    .filter((name) => /^card-.*\.json$/.test(name))
    .map((name) => JSON.parse(readFileSync(path.join(cardsDirectory, name), "utf8")));
}

function stableOutline(outline) {
  return (outline.rows || []).map((row) => ({
    h: row.h,
    name: row.name,
    role: row.role,
    state: row.state,
  }));
}

async function sendBrainstem(app, text, {
  settleMs = 60,
} = {}) {
  await app.driver.run([
    {
      action: "type",
      selector: "#input",
      typingDelayMs: 0,
      value: text,
    },
    {
      action: "click",
      selector: "#send",
      settleMs,
    },
  ]);
}

frontierTest("chat cards preserve delayed races, wake history, folds, and off identity", async () => {
  const app = await launch({
    modelScript: {
      steps: [
        {
          when: { index: 1, lastUser: QUESTION },
          response: { delayMs: 1600, text: FIRST_REPLY },
        },
        {
          when: { index: 2, lastUser: QUESTION },
          response: { delayMs: 120, text: SECOND_REPLY },
        },
        {
          when: { index: 3, lastUser: FOLLOW_UP },
          response: { delayMs: 80, text: FOLLOW_UP_REPLY },
        },
      ],
    },
    scenario: "chat-cards",
  });
  try {
    await app.driver.run([{
      action: "click",
      optional: true,
      selector: "#enter",
      settleMs: 100,
    }], { target: "shell" });
    const initialOutline = stableOutline(
      await app.driver.inspect({ target: "shell" }),
    );
    assert.deepEqual(initialOutline, CHECKPOINT_OUTLINE);

    await sendBrainstem(app, "april fools");
    await app.driver.expect({
      selector: "#brainstem-chat-grab",
      target: "shell",
      text: "Park chat",
      timeoutMs: 10_000,
    });
    await app.driver.run([{
      action: "click",
      targetText: "Clear",
      settleMs: 100,
    }]);

    await sendBrainstem(app, QUESTION, { settleMs: 40 });
    await waitFor(() => app.model.requests.length >= 1, {
      label: "first delayed model request to be accepted",
    });
    await app.driver.run([{
      action: "click",
      handle: "@brainstem.grab",
      settleMs: 80,
    }], { target: "shell" });
    await app.driver.expect({
      selector: ".chat-card",
      target: "shell",
      text: QUESTION,
      timeoutMs: 10_000,
    });
    const cardsDirectory = path.join(app.paths.betaHome, "cards");
    await waitFor(() => readCards(cardsDirectory).length === 1, {
      label: "first parked card file",
    });
    await app.driver.run([{
      action: "expect",
      selector: "#input",
      state: "empty",
    }]);

    await sendBrainstem(app, QUESTION);
    await app.driver.expect({
      selector: "#chat",
      text: SECOND_REPLY,
      timeoutMs: 10_000,
    });
    await app.driver.run([{
      action: "click",
      handle: "@brainstem.grab",
      settleMs: 80,
    }], { target: "shell" });

    const twoCards = await waitFor(() => {
      const cards = readCards(cardsDirectory);
      return cards.length === 2
        && cards.some((card) => card.history.at(-1)?.content === FIRST_REPLY)
        && cards.some((card) => card.history.at(-1)?.content === SECOND_REPLY)
        ? cards
        : null;
    }, {
      label: "both complete card files",
      timeoutMs: 15_000,
    });
    const first = twoCards.find((card) => (
      card.history.at(-1)?.content === FIRST_REPLY
    ));
    const second = twoCards.find((card) => (
      card.history.at(-1)?.content === SECOND_REPLY
    ));
    assert(first);
    assert(second);
    assert.equal(first.turns.at(-1).pending, undefined);

    await app.driver.run([{
      action: "swipe",
      direction: "right",
      distance: 110,
      handle: `@herd.card[${first.id}]`,
      settleMs: 150,
    }], { target: "shell" });
    await app.driver.expect({
      selector: "#chat",
      text: FIRST_REPLY,
      timeoutMs: 10_000,
    });

    await sendBrainstem(app, FOLLOW_UP);
    await app.driver.expect({
      selector: "#chat",
      text: FOLLOW_UP_REPLY,
      timeoutMs: 10_000,
    });
    const followRequest = app.model.requests.find((request) => (
      request.request.messages.some((message) => (
        message.role === "user" && message.content === FOLLOW_UP
      ))
    ));
    assert(followRequest, "the follow-up model request must be captured");
    const conversationPrefix = followRequest.request.messages
      .filter((message) => ["user", "assistant"].includes(message.role))
      .slice(0, 3)
      .map((message) => [message.role, message.content]);
    assert.deepEqual(conversationPrefix, [
      ["user", QUESTION],
      ["assistant", FIRST_REPLY],
      ["user", FOLLOW_UP],
    ]);
    await waitFor(() => {
      const saved = readCards(cardsDirectory).find((card) => card.id === first.id);
      return saved?.history.at(-1)?.content === FOLLOW_UP_REPLY ? saved : null;
    }, { label: "active card continuation to persist" });

    await app.driver.run([{
      action: "click",
      handle: `@herd.card[${second.id}].fold`,
      settleMs: 120,
    }], { target: "shell" });
    await waitFor(
      () => readCards(cardsDirectory).find((card) => (
        card.id === second.id && card.status === "folded"
      )),
      { label: "folded card file" },
    );

    await sendBrainstem(app, "april fools");
    await waitFor(async () => {
      const outline = await app.driver.inspect({ target: "shell" });
      return outline.rows.some((row) => String(row.h).startsWith("@herd.card["))
        ? null
        : outline;
    }, { label: "card handles to disappear" });
    const offOutline = stableOutline(
      await app.driver.inspect({ target: "shell" }),
    );
    assert.deepEqual(offOutline, CHECKPOINT_OUTLINE);
    await assert.rejects(
      app.driver.command({
        action: "read",
        selector: "#surgeon-herd",
        target: "shell",
      }),
      /not found/,
    );
    assert.equal(readCards(cardsDirectory).length, 2);

    await sendBrainstem(app, "april fools");
    await app.driver.expect({
      selector: `[data-chat-card="${first.id}"]`,
      target: "shell",
      text: first.title,
      timeoutMs: 10_000,
    });
    assert.equal(readCards(cardsDirectory).length, 2);
  } finally {
    await app.stop();
  }
});

frontierTest("Race stages one contender, renders one reply, and folds only its rival", async () => {
  const raceQuestion = "Can these models race?";
  const originalReply = "RACE_ORIGINAL_REPLY";
  const contenderReply = "RACE_CONTENDER_REPLY";
  const afterClearQuestion = "Does Clear detach the winner?";
  const afterClearReply = "AFTER_CLEAR_REPLY";
  const app = await launch({
    modelScript: {
      steps: [
        {
          when: { index: 1, lastUser: raceQuestion },
          response: { text: originalReply },
        },
        {
          when: { index: 2, lastUser: raceQuestion },
          response: { text: contenderReply },
        },
        {
          when: { index: 3, lastUser: afterClearQuestion },
          response: { text: afterClearReply },
        },
      ],
    },
    scenario: "chat-cards-race",
  });
  try {
    await app.driver.run([{
      action: "click",
      optional: true,
      selector: "#enter",
      settleMs: 100,
    }], { target: "shell" });
    await sendBrainstem(app, "april fools");
    await app.driver.expect({
      selector: "#brainstem-chat-grab",
      target: "shell",
      text: "Park chat",
      timeoutMs: 10_000,
    });
    await app.driver.run([{
      action: "click",
      targetText: "Clear",
      settleMs: 100,
    }]);

    await sendBrainstem(app, raceQuestion);
    await app.driver.expect({
      selector: "#chat",
      text: originalReply,
      timeoutMs: 10_000,
    });
    await app.driver.run([{
      action: "click",
      handle: "@brainstem.grab",
      settleMs: 100,
    }], { target: "shell" });
    const cardsDirectory = path.join(app.paths.betaHome, "cards");
    const [source] = await waitFor(() => {
      const cards = readCards(cardsDirectory);
      return cards.length === 1 ? cards : null;
    }, { label: "race source card" });

    await app.driver.run([{
      action: "click",
      handle: `@herd.card[${source.id}].race`,
      settleMs: 100,
    }], { target: "shell" });
    await app.driver.run([{
      action: "expect",
      selector: "#input",
      state: "filled",
    }]);
    const staged = await waitFor(() => {
      const cards = readCards(cardsDirectory);
      return cards.length === 2
        && cards.every((card) => card.status === "racing")
        ? cards
        : null;
    }, { label: "paired racing cards" });
    const contender = staged.find((card) => card.id !== source.id);
    assert.equal(contender.raceId, staged.find((card) => card.id === source.id).raceId);

    await app.driver.run([{
      action: "click",
      selector: "#send",
      settleMs: 60,
    }]);
    await app.driver.expect({
      selector: "#chat",
      text: contenderReply,
      timeoutMs: 10_000,
    });
    await waitFor(() => {
      const saved = readCards(cardsDirectory).find((card) => (
        card.id === contender.id
      ));
      return saved?.history.at(-1)?.content === contenderReply ? saved : null;
    }, { label: "race contender completion" });
    const transcript = await app.driver.command({
      action: "read",
      selector: "#chat",
    });
    assert.equal(transcript.text.split(contenderReply).length - 1, 1);
    assert.equal(readCards(cardsDirectory).length, 2);

    await app.driver.run([{
      action: "swipe",
      direction: "right",
      distance: 110,
      handle: `@herd.card[${contender.id}]`,
      settleMs: 150,
    }], { target: "shell" });
    await waitFor(() => {
      const cards = readCards(cardsDirectory);
      const winner = cards.find((card) => card.id === contender.id);
      const rival = cards.find((card) => card.id === source.id);
      return winner?.status === "primary" && rival?.status === "folded"
        ? cards
        : null;
    }, { label: "race winner and folded rival" });
    assert.equal(readCards(cardsDirectory).length, 2);

    await app.driver.run([{
      action: "click",
      targetText: "Clear",
      settleMs: 100,
    }]);
    await waitFor(() => {
      const saved = readCards(cardsDirectory).find((card) => (
        card.id === contender.id
      ));
      return saved?.status === "parked" ? saved : null;
    }, { label: "cleared winner to detach" });
    await sendBrainstem(app, afterClearQuestion);
    await app.driver.expect({
      selector: "#chat",
      text: afterClearReply,
      timeoutMs: 10_000,
    });
    await app.driver.run([{
      action: "click",
      handle: "@brainstem.grab",
      settleMs: 100,
    }], { target: "shell" });
    const afterClearCards = await waitFor(() => {
      const cards = readCards(cardsDirectory);
      return cards.length === 3 ? cards : null;
    }, { label: "new card after manual Clear" });
    assert.equal(
      afterClearCards.find((card) => card.id === contender.id)
        .history.at(-1).content,
      contenderReply,
    );
  } finally {
    await app.stop();
  }
});
