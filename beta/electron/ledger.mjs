import {
  chmodSync,
  closeSync,
  existsSync,
  mkdirSync,
  writeSync,
} from "node:fs";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";

import {
  openPrivateAppendFile,
  redactCredentialText,
} from "./log-redaction.mjs";


const AGENT_EVENT_LIMIT = 10;
const LEDGER_JSONL = "ledger.jsonl";
const LEDGER_SQLITE = "ledger.sqlite";

function privateMode(filePath) {
  if (process.platform !== "win32" && existsSync(filePath)) {
    chmodSync(filePath, 0o600);
  }
}

function redactField(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === "string") return redactCredentialText(value);
  if (typeof value === "object") {
    return redactCredentialText(JSON.stringify(value));
  }
  return value;
}

function requiredField(value, name) {
  const normalized = redactField(value);
  if (typeof normalized !== "string" || !normalized.trim()) {
    throw new TypeError(`${name} is required`);
  }
  return normalized;
}

function optionalField(value) {
  const normalized = redactField(value);
  return normalized === null ? null : String(normalized);
}

function shellQuote(value) {
  return `"${String(value).replaceAll("\\", "\\\\").replaceAll("\"", "\\\"")}"`;
}

export function describe(betaHome, recentAgents = []) {
  const databasePath = path.join(betaHome, LEDGER_SQLITE);
  const mirrorPath = path.join(betaHome, LEDGER_JSONL);
  return {
    database_path: databasePath,
    mirror_path: mirrorPath,
    recent_agents: recentAgents.slice(0, AGENT_EVENT_LIMIT),
    query_lines: [
      `sqlite3 ${shellQuote(databasePath)} "select * from agents order by at desc limit 20"`,
      `grep -i '<word>' ${shellQuote(mirrorPath)}`,
    ],
  };
}

export class Ledger {
  constructor(betaHome, {
    logger = console,
    now = () => new Date().toISOString(),
    onWrite = null,
  } = {}) {
    this.betaHome = path.resolve(betaHome);
    this.databasePath = path.join(this.betaHome, LEDGER_SQLITE);
    this.mirrorPath = path.join(this.betaHome, LEDGER_JSONL);
    this.logger = logger;
    this.now = now;
    this.onWrite = onWrite;
    this.errorReported = false;
    this.database = null;
    this.mirrorFd = null;
    this.statements = null;

    try {
      mkdirSync(this.betaHome, { recursive: true, mode: 0o700 });
      if (process.platform !== "win32") chmodSync(this.betaHome, 0o700);
      this.database = new DatabaseSync(this.databasePath);
      this.database.exec(`
        PRAGMA journal_mode = WAL;
        PRAGMA synchronous = NORMAL;
        CREATE TABLE IF NOT EXISTS turns (
          id INTEGER PRIMARY KEY,
          at TEXT NOT NULL,
          session_id TEXT,
          surface TEXT NOT NULL,
          role TEXT NOT NULL,
          content TEXT NOT NULL,
          model TEXT,
          request_id TEXT
        );
        CREATE TABLE IF NOT EXISTS agents (
          id INTEGER PRIMARY KEY,
          at TEXT NOT NULL,
          event TEXT NOT NULL,
          filename TEXT,
          tool_name TEXT,
          rappid TEXT,
          sha256 TEXT,
          source_path TEXT,
          origin TEXT,
          detail TEXT
        );
        CREATE TABLE IF NOT EXISTS tools_called (
          id INTEGER PRIMARY KEY,
          at TEXT NOT NULL,
          session_id TEXT,
          tool_name TEXT NOT NULL,
          ok INTEGER NOT NULL,
          summary TEXT
        );
        CREATE TABLE IF NOT EXISTS sources (
          sha256 TEXT NOT NULL,
          path TEXT NOT NULL,
          PRIMARY KEY (sha256, path)
        );
        CREATE INDEX IF NOT EXISTS turns_at_idx ON turns(at);
        CREATE INDEX IF NOT EXISTS agents_at_idx ON agents(at);
        CREATE INDEX IF NOT EXISTS tools_called_at_idx ON tools_called(at);
      `);
      this.statements = {
        turn: this.database.prepare(`
          INSERT INTO turns (
            at, session_id, surface, role, content, model, request_id
          ) VALUES (?, ?, ?, ?, ?, ?, ?)
        `),
        agent: this.database.prepare(`
          INSERT INTO agents (
            at, event, filename, tool_name, rappid, sha256,
            source_path, origin, detail
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        `),
        tool: this.database.prepare(`
          INSERT INTO tools_called (
            at, session_id, tool_name, ok, summary
          ) VALUES (?, ?, ?, ?, ?)
        `),
        source: this.database.prepare(`
          INSERT OR IGNORE INTO sources (sha256, path) VALUES (?, ?)
        `),
        recentAgents: this.database.prepare(`
          SELECT
            at, event, filename, tool_name, rappid, sha256,
            source_path, origin, detail
          FROM agents
          ORDER BY id DESC
          LIMIT ?
        `),
      };
      this.mirrorFd = openPrivateAppendFile(this.mirrorPath);
      this.#enforcePrivateFiles();
    } catch (error) {
      this.#disable(error);
    }
  }

  setOnWrite(onWrite) {
    this.onWrite = typeof onWrite === "function" ? onWrite : null;
  }

  recordTurn({
    at = this.now(),
    sessionId = null,
    session_id = sessionId,
    surface,
    role,
    content,
    model = null,
    requestId = null,
    request_id = requestId,
  }) {
    return this.#write(() => {
      const row = {
        table: "turns",
        at: requiredField(at, "at"),
        session_id: optionalField(session_id),
        surface: requiredField(surface, "surface"),
        role: requiredField(role, "role"),
        content: requiredField(content, "content"),
        model: optionalField(model),
        request_id: optionalField(request_id),
      };
      this.statements.turn.run(
        row.at,
        row.session_id,
        row.surface,
        row.role,
        row.content,
        row.model,
        row.request_id,
      );
      this.#appendMirror(row);
      return row;
    });
  }

  recordAgent({
    at = this.now(),
    event,
    filename = null,
    toolName = null,
    tool_name = toolName,
    rappid = null,
    sha256 = null,
    sourcePath = null,
    source_path = sourcePath,
    origin = null,
    detail = null,
  }) {
    return this.#write(() => {
      const row = {
        table: "agents",
        at: requiredField(at, "at"),
        event: requiredField(event, "event"),
        filename: optionalField(filename),
        tool_name: optionalField(tool_name),
        rappid: optionalField(rappid),
        sha256: optionalField(sha256),
        source_path: optionalField(source_path),
        origin: optionalField(origin),
        detail: optionalField(detail),
      };
      this.statements.agent.run(
        row.at,
        row.event,
        row.filename,
        row.tool_name,
        row.rappid,
        row.sha256,
        row.source_path,
        row.origin,
        row.detail,
      );
      this.#appendMirror(row);
      if (row.sha256 && row.source_path) {
        this.#recordSource({
          sha256: row.sha256,
          path: row.source_path,
        });
      }
      return row;
    });
  }

  recordToolCall({
    at = this.now(),
    sessionId = null,
    session_id = sessionId,
    toolName = null,
    tool_name = toolName,
    ok = false,
    summary = null,
  }) {
    return this.#write(() => {
      const row = {
        table: "tools_called",
        at: requiredField(at, "at"),
        session_id: optionalField(session_id),
        tool_name: requiredField(tool_name, "tool_name"),
        ok: ok ? 1 : 0,
        summary: optionalField(summary),
      };
      this.statements.tool.run(
        row.at,
        row.session_id,
        row.tool_name,
        row.ok,
        row.summary,
      );
      this.#appendMirror(row);
      return row;
    });
  }

  recordSource({ sha256, path: sourcePath }) {
    return this.#write(() => this.#recordSource({
      sha256: requiredField(sha256, "sha256"),
      path: requiredField(sourcePath, "path"),
    }));
  }

  recentAgentEvents(limit = AGENT_EVENT_LIMIT) {
    if (!this.database || !this.statements) return [];
    try {
      const bounded = Math.max(0, Math.min(Number(limit) || 0, 100));
      return this.statements.recentAgents.all(bounded);
    } catch (error) {
      this.#reportOnce(error);
      return [];
    }
  }

  describe() {
    return describe(this.betaHome, this.recentAgentEvents());
  }

  close() {
    try {
      if (this.mirrorFd !== null) closeSync(this.mirrorFd);
    } catch (error) {
      this.#reportOnce(error);
    } finally {
      this.mirrorFd = null;
    }
    try {
      this.database?.close();
    } catch (error) {
      this.#reportOnce(error);
    } finally {
      this.database = null;
      this.statements = null;
    }
  }

  #recordSource({ sha256, path: sourcePath }) {
    const row = {
      table: "sources",
      sha256,
      path: sourcePath,
    };
    const result = this.statements.source.run(row.sha256, row.path);
    if (Number(result.changes) > 0) this.#appendMirror(row);
    return row;
  }

  #write(operation) {
    if (!this.database || !this.statements || this.mirrorFd === null) {
      return null;
    }
    try {
      const row = operation();
      this.#enforcePrivateFiles();
      if (row && this.onWrite) {
        try {
          this.onWrite(row, this);
        } catch (error) {
          this.#reportOnce(error);
        }
      }
      return row;
    } catch (error) {
      this.#reportOnce(error);
      return null;
    }
  }

  #appendMirror(row) {
    writeSync(this.mirrorFd, `${JSON.stringify(row)}\n`);
  }

  #enforcePrivateFiles() {
    privateMode(this.databasePath);
    privateMode(this.mirrorPath);
    privateMode(`${this.databasePath}-wal`);
    privateMode(`${this.databasePath}-shm`);
  }

  #disable(error) {
    try {
      if (this.mirrorFd !== null) closeSync(this.mirrorFd);
    } catch {
      // Initialization is already failing; report the original error once.
    }
    try {
      this.database?.close();
    } catch {
      // Initialization is already failing; report the original error once.
    }
    this.database = null;
    this.mirrorFd = null;
    this.statements = null;
    this.#reportOnce(error);
  }

  #reportOnce(error) {
    if (this.errorReported) return;
    this.errorReported = true;
    const message = redactCredentialText(error?.message || String(error));
    this.logger?.error?.(`[ledger] ${message}`);
  }
}

export function openLedger(betaHome, options = {}) {
  return new Ledger(betaHome, options);
}
