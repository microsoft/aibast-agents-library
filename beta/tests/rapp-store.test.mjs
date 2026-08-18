import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import test from "node:test";

import { RappStoreClient, rappStoreInternals, STORE_SCHEMA } from "../electron/rapp-store.mjs";

const AGENT = "from agents.basic_agent import BasicAgent\n# demo singleton\n";
const AGENT_SHA = createHash("sha256").update(Buffer.from(AGENT)).digest("hex");

function fakeStore({ agentBytes = AGENT, sha = AGENT_SHA, gated404 = false } = {}) {
  const catalog = {
    schema: STORE_SCHEMA,
    generated_at: "2026-08-18",
    gated_rapplications_note: "gated entries are private",
    rapplications: [
      {
        id: "demo", name: "Demo", version: "1.0.0", summary: "s", category: "c", tags: [],
        singleton_filename: "demo_agent.py",
        singleton_url: "https://example/demo_agent.py",
        singleton_sha256: sha, singleton_bytes: agentBytes.length, quality_tier: "community",
        ui_url: "https://example/demo/index.html", ui_filename: "index.html",
      },
      {
        id: "locked", name: "Locked", singleton_filename: "locked_agent.py",
        singleton_url: "https://example/private/locked_agent.py",
        singleton_sha256: "deadbeef", access: "private", quality_tier: "private",
      },
    ],
  };
  const fetchImpl = async (url) => {
    if (url.endsWith("index.json") || url === "store") {
      return { ok: true, status: 200, json: async () => catalog };
    }
    if (url.includes("/private/")) {
      return gated404
        ? { ok: false, status: 404 }
        : { ok: true, status: 200, arrayBuffer: async () => Buffer.from(AGENT) };
    }
    return { ok: true, status: 200, arrayBuffer: async () => Buffer.from(agentBytes) };
  };
  return new RappStoreClient({ url: "store", fetchImpl });
}

test("loads the catalog and flags gated entries", async () => {
  const client = fakeStore();
  const list = await client.list();
  assert.equal(list.length, 2);
  assert.equal(list.find((e) => e.id === "demo").gated, false);
  assert.equal(list.find((e) => e.id === "locked").gated, true);
  // a RAPPlication carries its own UI (agents + specialized UI)
  assert.equal(list.find((e) => e.id === "demo").uiUrl, "https://example/demo/index.html");
});

test("download verifies the pinned sha256 before returning source", async () => {
  const ok = await fakeStore().download("demo");
  assert.equal(ok.filename, "demo_agent.py");
  assert.match(ok.source, /BasicAgent/);
  assert.equal(ok.verified, true);
  assert.equal(ok.sha256, AGENT_SHA);
});

test("a sha256 mismatch refuses to hatch", async () => {
  const client = fakeStore({ sha: "0".repeat(64) });
  await assert.rejects(() => client.download("demo"), /sha256 mismatch/);
});

test("a gated 404 surfaces an auth-needed error, not a silent miss", async () => {
  const client = fakeStore({ gated404: true });
  await assert.rejects(
    () => client.download("locked"),
    (error) => error.code === "gated" && /gated/.test(error.message),
  );
});

test("rejects an unexpected catalog schema", async () => {
  const client = new RappStoreClient({
    url: "store",
    fetchImpl: async () => ({ ok: true, status: 200, json: async () => ({ schema: "wrong", rapplications: [] }) }),
  });
  await assert.rejects(() => client.list(), /Unexpected RAPP Store schema/);
});
