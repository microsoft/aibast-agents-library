import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const renderer = readFileSync(
  new URL("../ui/renderer.js", import.meta.url),
  "utf8",
);
const cardsSource = readFileSync(
  new URL("../ui/chat-cards.js", import.meta.url),
  "utf8",
);
const shell = readFileSync(
  new URL("../ui/index.html", import.meta.url),
  "utf8",
);

test("mode off loads no card script, stylesheet, DOM, or listeners", async (t) => {
  assert.doesNotMatch(shell, /chat-cards\.(?:js|css)/);
  assert.match(
    renderer,
    /if \(state\.aprilFools\?\.on\) \{[\s\S]*syncChatCards\(state\)/,
  );
  assert.match(renderer, /else if \(window\.RappChatCards\)/);

  delete globalThis.RappChatCards;
  await import(`../ui/chat-cards.js?mode-off=${Date.now()}`);
  assert.equal(globalThis.RappChatCards.enabled(), false);
  globalThis.RappChatCards.disable();
  assert.equal(globalThis.RappChatCards.enabled(), false);
  t.diagnostic("mode-off renderer: 0 card DOM, 0 card listeners, 0 card CSS");
});

test("every card move and the Brainstem grab control has a drive handle", () => {
  assert.match(cardsSource, /dataset\.drive = "brainstem\.grab"/);
  assert.match(cardsSource, /herd\.card\[\$\{id\}\]/);
  for (const move of ["wake", "fold", "race"]) {
    assert.match(cardsSource, new RegExp(`driveCard\\(card\\.id, "${move}"\\)`));
  }
  assert.match(cardsSource, /cardTable\.deal/);
  assert.match(cardsSource, /cardTable\.theme/);
});

test("cards support drag, threshold swipes, buttons, and keyboard paths", () => {
  assert.match(cardsSource, /application\/x-rapp-brainstem-chat/);
  assert.match(cardsSource, /application\/x-rapp-chat-card/);
  assert.match(cardsSource, /movement >= 72/);
  assert.match(cardsSource, /movement <= -72/);
  assert.match(cardsSource, /event\.key === "ArrowRight"/);
  assert.match(cardsSource, /event\.key === "ArrowLeft"/);
  assert.match(cardsSource, /event\.key\.toLowerCase\(\) === "r"/);
});

test("table UI includes all themes and four deal moves", () => {
  for (const theme of ["poker", "yugioh", "pokemon", "mtg", "uno", "custom"]) {
    assert.match(cardsSource, new RegExp(`${theme}:`));
  }
  for (const deal of ["riffle", "fan", "deal-to-seats", "draw-one"]) {
    assert.match(cardsSource, new RegExp(`"${deal}"`));
  }
});
