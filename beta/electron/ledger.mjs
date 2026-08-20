import {
  chmodSync,
  closeSync,
  existsSync,
  mkdirSync,
  renameSync,
  writeFileSync,
  writeSync,
} from "node:fs";
import { createHash } from "node:crypto";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";

import {
  openPrivateAppendFile,
  redactCredentialText,
} from "./log-redaction.mjs";


const AGENT_EVENT_LIMIT = 10;
const LEDGER_JSONL = "ledger.jsonl";
const LEDGER_SQLITE = "ledger.sqlite";
const ROUTE_AGENT_EVENTS = new Map([
  ["composition-quarantine", { event: "quarantined", origin: "lineage" }],
  ["ephemeral-cleaned", { event: "removed", origin: "surgeon" }],
  ["ephemeral-injected", { event: "installed", origin: "surgeon" }],
  ["global-agent-removed", { event: "removed", origin: "surgeon" }],
  ["lineage-default-seeded", { event: "molted", origin: "lineage" }],
  ["lineage-promote", { event: "promoted", origin: "lineage" }],
  ["lineage-restore", { event: "restored", origin: "lineage" }],
  ["lineage-rollback", { event: "rolled_back", origin: "lineage" }],
  ["stack-agent-installed", { event: "installed", origin: "surgeon" }],
  ["stack-agent-removed", { event: "removed", origin: "surgeon" }],
]);

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

function pythonLexicalView(source) {
  const text = String(source || "");
  const strings = [];
  let code = "";
  let index = 0;
  while (index < text.length) {
    const current = text[index];
    if (current === "#") {
      while (index < text.length && text[index] !== "\n") index += 1;
      continue;
    }
    if (current !== "\"" && current !== "'") {
      code += current;
      index += 1;
      continue;
    }
    const quote = current;
    const triple = text.slice(index, index + 3) === quote.repeat(3);
    const openingLength = triple ? 3 : 1;
    let cursor = index + openingLength;
    let value = "";
    let closed = false;
    while (cursor < text.length) {
      if (triple && text.slice(cursor, cursor + 3) === quote.repeat(3)) {
        cursor += 3;
        closed = true;
        break;
      }
      if (!triple && text[cursor] === quote) {
        cursor += 1;
        closed = true;
        break;
      }
      if (text[cursor] === "\\" && cursor + 1 < text.length) {
        value += text[cursor + 1];
        cursor += 2;
        continue;
      }
      if (!triple && text[cursor] === "\n") break;
      value += text[cursor];
      cursor += 1;
    }
    if (!closed) {
      code += current;
      index += 1;
      continue;
    }
    const token = `__RAPP_STRING_${strings.length}__`;
    strings.push(value);
    code += token;
    code += "\n".repeat((value.match(/\n/g) || []).length);
    index = cursor;
  }
  return { code, strings };
}

export function inferAgentToolName(source, filename = null) {
  const lexical = pythonLexicalView(source);
  const assigned = lexical.code.match(
    /\bself\.name\s*=\s*[rRuUbBfF]*__RAPP_STRING_(\d+)__/,
  );
  const assignedName = assigned
    ? lexical.strings[Number(assigned[1])]?.trim()
    : null;
  if (assignedName) return assignedName;
  const metadataPattern =
    /__RAPP_STRING_(\d+)__\s*:\s*[rRuUbBfF]*__RAPP_STRING_(\d+)__/g;
  for (const match of lexical.code.matchAll(metadataPattern)) {
    if (lexical.strings[Number(match[1])] !== "name") continue;
    const metadataName = lexical.strings[Number(match[2])]?.trim();
    if (metadataName) return metadataName;
  }
  const className = lexical.code.match(
    /\bclass\s+([A-Za-z_][A-Za-z0-9_]*Agent)\b/,
  );
  if (className?.[1]) return className[1];
  return filename
    ? path.basename(filename, path.extname(filename))
    : null;
}

export function parseAgentLogs(agentLogs) {
  if (Array.isArray(agentLogs)) {
    return agentLogs.flatMap((entry) => {
      if (!entry || typeof entry !== "object") return [];
      const toolName = entry.tool_name || entry.toolName || entry.name;
      if (!toolName) return [];
      return [{
        tool_name: String(toolName),
        ok: entry.ok !== false && entry.success !== false,
        summary: String(entry.summary || entry.result || entry.content || ""),
      }];
    });
  }
  return String(agentLogs || "")
    .split(/\r?\n/)
    .flatMap((line) => {
      const match = line.match(/^\[([^\]]+)]\s*(.*)$/);
      if (!match || match[1] === "?") return [];
      const summary = match[2].trim();
      return [{
        tool_name: match[1].trim(),
        ok: !/^(?:ERROR|Error):/.test(summary),
        summary: summary.slice(0, 2000),
      }];
    });
}

export function recordCompletedTurn(ledger, {
  at = null,
  agentLogs = "",
  model = null,
  requestId = null,
  response,
  sessionId = null,
  surface,
  userInput,
} = {}) {
  if (!ledger) return { tools: [], turns: [] };
  const timestamp = at || ledger.now?.() || new Date().toISOString();
  const turns = [
    ledger.recordTurn({
      at: timestamp,
      sessionId,
      surface,
      role: "user",
      content: userInput,
      model,
      requestId,
    }),
    ledger.recordTurn({
      at: timestamp,
      sessionId,
      surface,
      role: "assistant",
      content: response,
      model,
      requestId,
    }),
  ].filter(Boolean);
  const tools = parseAgentLogs(agentLogs)
    .map((tool) => ledger.recordToolCall({
      at: timestamp,
      sessionId,
      ...tool,
    }))
    .filter(Boolean);
  return { tools, turns };
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

  archiveAgentSource({ filename, source }) {
    if (!this.database) return null;
    try {
      const safeName = path.basename(String(filename || "agent.py"));
      const redacted = Buffer.from(
        redactCredentialText(Buffer.from(source).toString("utf8")),
        "utf8",
      );
      const digest = createHash("sha256").update(redacted).digest("hex");
      const directory = path.join(this.betaHome, "ledger-sources", digest);
      mkdirSync(directory, { recursive: true, mode: 0o700 });
      if (process.platform !== "win32") chmodSync(directory, 0o700);
      const sourcePath = path.join(directory, safeName);
      if (!existsSync(sourcePath)) {
        const temporary = `${sourcePath}.${process.pid}.tmp`;
        writeFileSync(temporary, redacted, { mode: 0o600 });
        renameSync(temporary, sourcePath);
      }
      privateMode(sourcePath);
      return { path: sourcePath, sha256: digest };
    } catch (error) {
      this.#reportOnce(error);
      return null;
    }
  }

  recordRouteEvent(event) {
    const mapping = ROUTE_AGENT_EVENTS.get(String(event?.type || ""));
    if (!mapping) return [];
    const hasAgentRows = Object.hasOwn(event, "agent_rows");
    let rows = Array.isArray(event.agent_rows) ? event.agent_rows : [];
    if (hasAgentRows && !rows.length) return [];
    if (!hasAgentRows && !rows.length && Array.isArray(event.excluded_files)) {
      rows = event.excluded_files;
    }
    if (!rows.length) rows = [event];
    return rows
      .map((row) => this.recordAgent({
        at: event.timestamp || this.now(),
        event: mapping.event,
        filename: row.filename ?? event.filename ?? null,
        toolName: row.tool_name ?? row.toolName ?? event.tool_name ?? null,
        rappid: row.rappid
          ?? row.agent_rappid
          ?? row.ring_rappid
          ?? event.rappid
          ?? event.ring_rappid
          ?? null,
        sha256: row.sha256 ?? event.sha256 ?? null,
        sourcePath: row.source_path
          ?? row.sourcePath
          ?? event.source_path
          ?? null,
        origin: row.origin ?? event.origin ?? mapping.origin,
        detail: { ...event, agent_rows: undefined },
      }))
      .filter(Boolean);
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
