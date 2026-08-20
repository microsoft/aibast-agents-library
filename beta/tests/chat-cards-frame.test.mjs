import assert from "node:assert/strict";
import test from "node:test";

import {
  composeChatCardsFrameBridgeSource,
} from "../electron/chat-cards.mjs";

const enabled = {
  on: true,
  table: "poker",
  customTablePath: null,
};

test("card frame bridge exists only in enabled bridge source", () => {
  const checkpoint = "window.__checkpointBridge = true;";
  assert.equal(
    composeChatCardsFrameBridgeSource(checkpoint, { ...enabled, on: false }),
    checkpoint,
  );
  const source = composeChatCardsFrameBridgeSource(checkpoint, enabled);
  assert.match(source, /window\.__rappBetaAprilFoolsBridge/);
  assert.match(source, /window\.fetch = cardFetch/);
  assert.match(source, /rapp-beta:card-capture/);
  assert.match(source, /rapp-beta:card-wake/);
  assert.match(source, /rapp-beta:card-parked/);
  assert.match(source, /pendingRequestIds/);
  assert.match(source, /__rappBetaDeferredCardCompletions/);
});

test("card capture and restore use the page sanitizer", () => {
  const source = composeChatCardsFrameBridgeSource("", enabled);
  const uses = source.match(/window\.sanitizeMarkdownFragment/g) || [];
  assert.ok(uses.length >= 4);
  assert.match(source, /sanitizedHtml\(bubble\)/);
  assert.match(source, /replyHtml\(reply\)/);
  assert.match(source, /bubble\.replaceChildren/);
});

test("wake history substitutes by prefix and clear stops future splicing", () => {
  const source = composeChatCardsFrameBridgeSource("", enabled);
  assert.match(
    source,
    /activeHistory\s*\?\s*\[\.\.\.wireHistory\(activeHistory\), \.\.\.incomingHistory\]/,
  );
  assert.match(source, /body\.conversation_history = effectiveHistory/);
  assert.match(source, /if \(\s*!internalClear[\s\S]*activeHistory = null/);
  assert.match(source, /markPendingForCard[\s\S]*activeHistory = null/);
});

test("parking preserves an accepted delayed wire while kernel Clear runs", () => {
  const source = composeChatCardsFrameBridgeSource("", enabled);
  assert.match(source, /request\.preserveOnClear/);
  assert.match(source, /controller\.abort\(originalSignal\?\.reason\)/);
  assert.match(source, /clearKernel\(\{ preservePending: true \}\)/);
  assert.match(source, /rapp-beta:card-pending-complete/);
  assert.match(source, /rapp-beta:card-completion-ack/);
  assert.match(source, /canonicalHistory/);
  assert.match(source, /rapp-beta:card-detached/);
});
