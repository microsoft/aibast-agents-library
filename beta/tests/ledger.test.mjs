import assert from "node:assert/strict";
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";
import test from "node:test";

import {
  describe,
  openLedger,
} from "../electron/ledger.mjs";


function scratch(t, prefix = "rapp-ledger-") {
  const root = mkdtempSync(path.join(tmpdir(), prefix));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  return root;
}

function rows(databasePath, sql) {
  const database = new DatabaseSync(databasePath, { readOnly: true });
  try {
    return database.prepare(sql).all().map((row) => ({ ...row }));
  } finally {
    database.close();
  }
}

test("ledger creates private WAL storage with the documented schema and queries", (t) => {
  const betaHome = scratch(t);
  const ledger = openLedger(betaHome);
  t.after(() => ledger.close());

  const databasePath = path.join(betaHome, "ledger.sqlite");
  const mirrorPath = path.join(betaHome, "ledger.jsonl");
  const tableNames = rows(
    databasePath,
    "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name",
  ).map(({ name }) => name);
  assert.deepEqual(
    tableNames.filter((name) => !name.startsWith("sqlite_")),
    ["agents", "sources", "tools_called", "turns"],
  );
  const database = new DatabaseSync(databasePath, { readOnly: true });
  try {
    assert.equal(database.prepare("PRAGMA journal_mode").get().journal_mode, "wal");
  } finally {
    database.close();
  }
  if (process.platform !== "win32") {
    assert.equal(statSync(betaHome).mode & 0o777, 0o700);
    assert.equal(statSync(databasePath).mode & 0o777, 0o600);
    assert.equal(statSync(mirrorPath).mode & 0o777, 0o600);
  }

  const summary = ledger.describe();
  assert.deepEqual(summary, describe(betaHome));
  assert.match(summary.query_lines[0], /^sqlite3 .*ledger\.sqlite/);
  assert.match(summary.query_lines[0], /select \* from agents/);
  assert.match(summary.query_lines[1], /^grep -i '<word>' .*ledger\.jsonl/);
});

test("ledger mirrors turns, tools, agents, and source locations synchronously", (t) => {
  const betaHome = scratch(t);
  const writes = [];
  const ledger = openLedger(betaHome, {
    now: () => "2026-08-20T20:12:00.000Z",
    onWrite: (row) => writes.push(row.table),
  });
  t.after(() => ledger.close());

  ledger.recordTurn({
    sessionId: "session-1",
    surface: "brainstem",
    role: "user",
    content: "what's the weather here",
    model: "scripted",
    requestId: "request-1",
  });
  ledger.recordToolCall({
    sessionId: "session-1",
    toolName: "WeatherAgent",
    ok: true,
    summary: "forecast returned",
  });
  ledger.recordAgent({
    event: "installed",
    filename: "weather_agent.py",
    toolName: "WeatherAgent",
    rappid: "rapp:test:weather",
    sha256: "abc123",
    sourcePath: "/tmp/composition/weather_agent.py",
    origin: "store",
    detail: { stack: "default" },
  });

  assert.deepEqual(writes, ["turns", "tools_called", "agents"]);
  assert.deepEqual(
    rows(
      ledger.databasePath,
      "SELECT session_id, surface, role, content, model, request_id FROM turns",
    ),
    [{
      session_id: "session-1",
      surface: "brainstem",
      role: "user",
      content: "what's the weather here",
      model: "scripted",
      request_id: "request-1",
    }],
  );
  assert.deepEqual(
    rows(
      ledger.databasePath,
      "SELECT session_id, tool_name, ok, summary FROM tools_called",
    ),
    [{
      session_id: "session-1",
      tool_name: "WeatherAgent",
      ok: 1,
      summary: "forecast returned",
    }],
  );
  assert.deepEqual(
    rows(ledger.databasePath, "SELECT sha256, path FROM sources"),
    [{
      sha256: "abc123",
      path: "/tmp/composition/weather_agent.py",
    }],
  );
  assert.equal(ledger.recentAgentEvents().length, 1);
  assert.equal(ledger.describe().recent_agents[0].tool_name, "WeatherAgent");

  const mirror = readFileSync(ledger.mirrorPath, "utf8")
    .trim()
    .split("\n")
    .map((line) => JSON.parse(line));
  assert.deepEqual(
    mirror.map(({ table }) => table),
    ["turns", "tools_called", "agents", "sources"],
  );
  assert.equal(mirror[2].detail, '{"stack":"default"}');
});

test("every persisted ledger field passes through credential redaction", (t) => {
  const betaHome = scratch(t);
  const ledger = openLedger(betaHome, {
    now: () => "2026-08-20T20:13:00.000Z",
  });
  t.after(() => ledger.close());
  const credential = "******";

  ledger.recordTurn({
    sessionId: "session-redaction",
    surface: "surgeon",
    role: "user",
    content: `use token=${credential}`,
    model: "scripted",
    requestId: "request-redaction",
  });
  ledger.recordToolCall({
    sessionId: "session-redaction",
    toolName: "WeatherAgent",
    ok: false,
    summary: `Authorization: ******`,
  });
  ledger.recordAgent({
    event: "installed",
    filename: "weather_agent.py",
    toolName: "WeatherAgent",
    sha256: "abc123",
    sourcePath: "/tmp/weather_agent.py",
    origin: "surgeon",
    detail: `password=${credential}`,
  });

  const persisted = [
    readFileSync(ledger.mirrorPath, "utf8"),
    JSON.stringify(rows(
      ledger.databasePath,
      "SELECT content FROM turns UNION ALL SELECT summary FROM tools_called UNION ALL SELECT detail FROM agents",
    )),
  ].join("\n");
  assert.doesNotMatch(persisted, /ghp_/);
  assert.doesNotMatch(persisted, /authorizationSecret/);
  assert.match(persisted, /\[redacted:token\]/);
  assert.match(persisted, /\[redacted:authorization\]/);
  assert.match(persisted, /\[redacted:password\]/);
});

test("ledger initialization and write failures are isolated and logged once", (t) => {
  const root = scratch(t, "rapp-ledger-failure-");
  const blocked = path.join(root, "not-a-directory");
  writeFileSync(blocked, "occupied");
  const messages = [];

  let ledger;
  assert.doesNotThrow(() => {
    ledger = openLedger(blocked, {
      logger: { error: (message) => messages.push(message) },
    });
  });
  assert.doesNotThrow(() => {
    ledger.recordTurn({
      surface: "brainstem",
      role: "user",
      content: "still serving",
    });
    ledger.recordAgent({ event: "installed" });
    ledger.recordToolCall({ toolName: "TestAgent", ok: true });
    ledger.close();
  });
  assert.equal(messages.length, 1);
  assert.match(messages[0], /^\[ledger\] /);

  const writable = path.join(root, "writable");
  mkdirSync(writable);
  const invalidRows = [];
  const writableLedger = openLedger(writable, {
    logger: { error: (message) => invalidRows.push(message) },
  });
  t.after(() => writableLedger.close());
  assert.equal(writableLedger.recordTurn({
    surface: "",
    role: "user",
    content: "invalid surface",
  }), null);
  assert.equal(writableLedger.recordToolCall({
    toolName: "",
    ok: true,
  }), null);
  assert.equal(invalidRows.length, 1);
});
