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
const FIRST_REPLY = "FIRST_TILE_REPLY: preserve the delayed dimension.";
const SECOND_REPLY = "SECOND_TILE_REPLY: compare a fresh dimension.";
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

function readTiles(tilesDirectory) {
  if (!existsSync(tilesDirectory)) return [];
  return readdirSync(tilesDirectory)
    .filter((name) => /^tile-.*\.json$/.test(name))
    .map((name) => JSON.parse(readFileSync(path.join(tilesDirectory, name), "utf8")));
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

frontierTest("dimension tiles preserve delayed races, wake history, folds, and herd identity", async () => {
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
    scenario: "dimension-tiles",
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

    await sendBrainstem(app, "agent arena");
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
      selector: ".dimension-tile",
      target: "shell",
      text: QUESTION,
      timeoutMs: 10_000,
    });
    const tilesDirectory = path.join(app.paths.betaHome, "tiles");
    await waitFor(() => readTiles(tilesDirectory).length === 1, {
      label: "first parked tile file",
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

    const twoTiles = await waitFor(() => {
      const tiles = readTiles(tilesDirectory);
      return tiles.length === 2
        && tiles.some((tile) => tile.history.at(-1)?.content === FIRST_REPLY)
        && tiles.some((tile) => tile.history.at(-1)?.content === SECOND_REPLY)
        ? tiles
        : null;
    }, {
      label: "both complete tile files",
      timeoutMs: 15_000,
    });
    const first = twoTiles.find((tile) => (
      tile.history.at(-1)?.content === FIRST_REPLY
    ));
    const second = twoTiles.find((tile) => (
      tile.history.at(-1)?.content === SECOND_REPLY
    ));
    assert(first);
    assert(second);
    assert.equal(first.turns.at(-1).pending, undefined);

    await app.driver.run([{
      action: "swipe",
      direction: "right",
      distance: 110,
      handle: `@herd.tile[${first.id}]`,
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
      const saved = readTiles(tilesDirectory).find((tile) => tile.id === first.id);
      return saved?.history.at(-1)?.content === FOLLOW_UP_REPLY ? saved : null;
    }, { label: "active tile continuation to persist" });

    await app.driver.run([{
      action: "click",
      handle: `@herd.tile[${second.id}].fold`,
      settleMs: 120,
    }], { target: "shell" });
    await waitFor(
      () => readTiles(tilesDirectory).find((tile) => (
        tile.id === second.id && tile.status === "folded"
      )),
      { label: "folded tile file" },
    );

    await sendBrainstem(app, "herd");
    await waitFor(async () => {
      const outline = await app.driver.inspect({ target: "shell" });
      return outline.rows.some((row) => String(row.h).startsWith("@herd.tile["))
        ? null
        : outline;
    }, { label: "tile handles to disappear" });
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
    assert.equal(readTiles(tilesDirectory).length, 2);

    await sendBrainstem(app, "agent arena");
    await app.driver.expect({
      selector: `[data-dimension-tile="${first.id}"]`,
      target: "shell",
      text: first.title,
      timeoutMs: 10_000,
    });
    assert.equal(readTiles(tilesDirectory).length, 2);
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
    scenario: "dimension-tiles-race",
  });
  try {
    await app.driver.run([{
      action: "click",
      optional: true,
      selector: "#enter",
      settleMs: 100,
    }], { target: "shell" });
    await sendBrainstem(app, "agent arena");
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
    const tilesDirectory = path.join(app.paths.betaHome, "tiles");
    const [source] = await waitFor(() => {
      const tiles = readTiles(tilesDirectory);
      return tiles.length === 1 ? tiles : null;
    }, { label: "race source tile" });

    await app.driver.run([{
      action: "click",
      handle: `@herd.tile[${source.id}].race`,
      settleMs: 100,
    }], { target: "shell" });
    await app.driver.run([{
      action: "expect",
      selector: "#input",
      state: "filled",
    }]);
    const staged = await waitFor(() => {
      const tiles = readTiles(tilesDirectory);
      return tiles.length === 2
        && tiles.every((tile) => tile.status === "racing")
        ? tiles
        : null;
    }, { label: "paired racing tiles" });
    const contender = staged.find((tile) => tile.id !== source.id);
    assert.equal(contender.raceId, staged.find((tile) => tile.id === source.id).raceId);

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
      const saved = readTiles(tilesDirectory).find((tile) => (
        tile.id === contender.id
      ));
      return saved?.history.at(-1)?.content === contenderReply ? saved : null;
    }, { label: "race contender completion" });
    const transcript = await app.driver.command({
      action: "read",
      selector: "#chat",
    });
    assert.equal(transcript.text.split(contenderReply).length - 1, 1);
    assert.equal(readTiles(tilesDirectory).length, 2);

    await app.driver.run([{
      action: "swipe",
      direction: "right",
      distance: 110,
      handle: `@herd.tile[${contender.id}]`,
      settleMs: 150,
    }], { target: "shell" });
    await waitFor(() => {
      const tiles = readTiles(tilesDirectory);
      const winner = tiles.find((tile) => tile.id === contender.id);
      const rival = tiles.find((tile) => tile.id === source.id);
      return winner?.status === "primary" && rival?.status === "folded"
        ? tiles
        : null;
    }, { label: "race winner and folded rival" });
    assert.equal(readTiles(tilesDirectory).length, 2);

    await app.driver.run([{
      action: "click",
      targetText: "Clear",
      settleMs: 100,
    }]);
    await waitFor(() => {
      const saved = readTiles(tilesDirectory).find((tile) => (
        tile.id === contender.id
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
    const afterClearTiles = await waitFor(() => {
      const tiles = readTiles(tilesDirectory);
      return tiles.length === 3 ? tiles : null;
    }, { label: "new tile after manual Clear" });
    assert.equal(
      afterClearTiles.find((tile) => tile.id === contender.id)
        .history.at(-1).content,
      contenderReply,
    );
  } finally {
    await app.stop();
  }
});
