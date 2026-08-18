// Twin manager — hatches RAPPlications from the RAPP Store as concurrent,
// long-lived Brainstem workers ("twins"), each on its own loopback port.
//
// Canon (crawled kody-w/rapp-spine — see docs/twins/COMPLIANCE.md):
//   * A herd of twins is Leviathan sense (A): one mind, many brainstem bodies.
//   * Chat is the ONLY wire (Art. XXV): a twin is driven only over its worker's
//     `/chat`. We add NO route, never the legacy `/api/agent` (a known RCE).
//   * The shippable unit is the `rapp-cart/1.0` cartridge (the store's
//     `singleton_url` agent.py + optional `egg_url` .egg); ports/twins stay
//     under the hood.
//   * Twin workers bind 127.0.0.1 only (rapp-kernel-boundary/1.0).
//   * RAPPID mint-once via the route manager's UUID-anchor packageAgent.
//
// Unlike BetaRouteManager's single-active-composition model (workers retire on
// activate), twins are kept alive concurrently in a registry until closed.
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import net from "node:net";
import path from "node:path";

import { BrainstemProcess } from "./brainstem-process.mjs";

function allocatePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : null;
      server.close((error) => {
        if (error) reject(error);
        else if (!port) reject(new Error("Could not allocate a twin port."));
        else resolve(port);
      });
    });
  });
}

function twinSlug(value) {
  return String(value || "twin")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40) || "twin";
}

// A twin needs the user only for a genuine, user-owned sign-in — match an auth
// REQUEST, not incidental auth vocabulary in an otherwise normal answer (so a
// reply like "users authenticate with their org account" doesn't abort a loop).
const NEEDS_AUTH_RE = /\b(please sign in|sign in (?:to continue|required|and continue|first)|device login|device code|run device login|not authenticated|authentication (?:required|needed)|authenticate (?:first|to continue)|pac auth login|you (?:need|must) to (?:sign in|authenticate)|requires? (?:you to )?(?:sign in|authenticate))\b/i;

// Completion detection for a twin's own reply (run()): not fooled by negation
// ("I am not done") and never treats an empty reply as success.
function saysDone(text) {
  const t = String(text || "").trim();
  if (!t) return false;
  if (/\b(?:not|isn'?t|cannot|can'?t|won'?t|unable to|couldn'?t|never|no longer)\s+(?:\w+\s+){0,3}(?:done|complete|completed|finished)\b/i.test(t)) return false;
  return /\b(done|complete|completed|finished|no further (?:action|steps)|draft (?:is )?ready)\b/i.test(t);
}

// The planner is told to answer "DONE — …"; accept it at the start of the reply
// or on its own line (tolerating a short preamble) so completion isn't missed
// and the "DONE — …" line is never forwarded to the twin as an instruction.
const planIsDone = (plan) => /(^|\n)\s*DONE\b/i.test(String(plan || ""));

export class TwinManager {
  constructor({ brainstemConfig, betaHome, routeManager = null, storeClient, brainstemUrl = null, onEvent = () => {} }) {
    if (!brainstemConfig) throw new Error("TwinManager needs a brainstemConfig.");
    if (!storeClient) throw new Error("TwinManager needs a RAPP Store client.");
    this.brainstemConfig = brainstemConfig;
    // Resolver for the *current* visible Brainstem's base URL — used when the
    // Brainstem drives a two-brain loop with a twin. Defaults to the config URL;
    // main passes () => state.url so a routed Brainstem is honored.
    this.brainstemUrl = brainstemUrl || (() => this.brainstemConfig.url);
    this.betaHome = betaHome;
    this.routeManager = routeManager;
    this.store = storeClient;
    this.onEvent = onEvent;
    this.twins = new Map();
    this.seq = 0;
    this.maxTwins = 8;   // cap concurrent workers so a runaway can't exhaust the machine
    this.twinsRoot = path.join(betaHome, "twins");
    // Clear stale twin dirs left by a crashed previous session. NOTE: this only
    // removes directories — it does NOT reap an orphaned worker process from a
    // hard-killed prior session (that stays until the OS reclaims its port); we
    // just start this session's bookkeeping clean.
    try { rmSync(this.twinsRoot, { recursive: true, force: true }); } catch { /* ignore */ }
  }

  emit(event) {
    this.onEvent({ timestamp: new Date().toISOString(), ...event });
  }

  descriptor(twin) {
    return {
      id: twin.id,
      storeId: twin.storeId,
      name: twin.name,
      rappid: twin.rappid,
      port: twin.port,
      url: twin.url,
      status: twin.status,
      license: twin.license,
      uiUrl: twin.uiUrl,
      hasCustomUi: Boolean(twin.uiHtml),
      loopLog: twin.loopLog.slice(-40),
      createdUtc: twin.createdUtc,
    };
  }

  list() {
    return Array.from(this.twins.values(), (twin) => this.descriptor(twin));
  }

  get(id) {
    const twin = this.twins.get(String(id));
    if (!twin) throw new Error(`No twin "${id}".`);
    return twin;
  }

  // The rapplication's own static UI HTML (to inject into its twin's iframe).
  uiHtml(id) {
    return this.twins.get(String(id))?.uiHtml || null;
  }

  #log(twin, line) {
    twin.loopLog.push({ at: new Date().toISOString(), line: String(line).slice(0, 600) });
    this.emit({ type: "twin-log", id: twin.id, line, status: twin.status });
  }

  #setStatus(twin, status) {
    if (twin.closed) return;   // a closed twin must not re-emit and resurrect its tile
    twin.status = status;
    this.emit({ type: "twin-status", id: twin.id, status, twin: this.descriptor(twin) });
  }

  // Hatch a RAPPlication FROM THE STORE into its own long-lived worker.
  async hatch(storeId, { instruction = null } = {}) {
    const cartridge = await this.store.download(storeId);   // sha256-verified
    const filename = cartridge.filename && /_agent\.py$/.test(cartridge.filename)
      ? cartridge.filename
      : `${twinSlug(cartridge.id || storeId)}_agent.py`;
    return this.#hatchComposed({
      idBase: cartridge.id || storeId,
      name: cartridge.entry?.name || cartridge.id || storeId,
      storeId: cartridge.id || storeId,
      agentSources: [{ filename, source: cartridge.source }],
      egg: cartridge.egg || null,
      resources: [],
      license: cartridge.entry?.license || null,
      uiUrl: cartridge.entry?.uiUrl || null,
      note: `Verified ${filename} (sha256 ${cartridge.sha256.slice(0, 12)}…)`,
    }, { instruction });
  }

  // Hatch a twin from LOCAL agent sources (e.g. the bundled Copilot Studio
  // Factory + Deploy agents) — a Frontier-owned specialized twin, not a store
  // pull. Same worker/port/loop machinery; nothing is downloaded.
  async hatchLocal({
    id: idBase = "twin",
    name = idBase,
    agentSources = [],
    resources = [],
    license = null,
  } = {}, { instruction = null } = {}) {
    if (!agentSources.length) throw new Error("hatchLocal needs at least one agent source.");
    return this.#hatchComposed({
      idBase, name, storeId: null, agentSources, egg: null, resources, license, uiUrl: null,
      note: `Composed ${agentSources.map((a) => a.filename).join(", ")}`,
    }, { instruction });
  }

  // Shared core: compose an isolated AGENTS_PATH, start a dedicated worker on
  // its own loopback port, register it, and (optionally) kick its async loop.
  async #hatchComposed(spec, { instruction = null } = {}) {
    if (this.twins.size >= this.maxTwins) {
      throw new Error(`You have ${this.maxTwins} twins open — close one before hatching another.`);
    }
    const id = `${twinSlug(spec.idBase)}-${++this.seq}`;
    const dir = path.join(this.twinsRoot, id);
    const agentsDir = path.join(dir, "agents");
    mkdirSync(agentsDir, { recursive: true });
    for (const agent of spec.agentSources) {
      writeFileSync(path.join(agentsDir, agent.filename), agent.source, { mode: 0o600 });
    }
    if (spec.egg) writeFileSync(path.join(dir, `${id}.egg`), spec.egg, { mode: 0o600 });
    // Materialize any resource files (e.g. parity cases / industry matrix) into
    // the twin dir so its agents can read them locally.
    const resourcePaths = {};
    for (const resource of spec.resources || []) {
      const target = path.join(dir, resource.name);
      writeFileSync(target, resource.bytes, { mode: 0o600 });
      resourcePaths[resource.name] = target;
    }

    // Mint a mint-once RAPPID from the first agent (UUID-anchor; rapp/1 §6.2).
    let rappid = null;
    try {
      const first = spec.agentSources[0];
      rappid = this.routeManager?.packageAgent
        ? this.routeManager.packageAgent({ filename: first.filename, source: first.source }).agent_rappid
        : null;
    } catch {
      rappid = null;
    }

    const port = await allocatePort();
    const url = `http://127.0.0.1:${port}`;
    const worker = new BrainstemProcess({
      ...this.brainstemConfig,
      port,
      url,
      logFile: path.join(this.betaHome, "logs", "twins", `${id}.log`),
      env: {
        ...(this.brainstemConfig.env || {}),
        AGENTS_PATH: agentsDir,
        BRAINSTEM_BETA_ROUTED_WORKER: "1",
        BRAINSTEM_BETA_TWIN: id,
        // A twin runs sha-pinned-but-still-third-party store code — it must ALWAYS
        // bind loopback, never inherit the main Brainstem's LAN mode and expose
        // itself on 0.0.0.0 (rapp-kernel-boundary/1.0: twins are loopback-only).
        BRAINSTEM_LAN_MODE: "0",
      },
    });

    const twin = {
      id,
      storeId: spec.storeId,
      name: spec.name,
      rappid,
      port,
      url,
      status: "hatching",
      license: spec.license,
      uiUrl: spec.uiUrl,
      dir,
      resourcePaths,
      worker,
      uiHtml: null,
      loopLog: [],
      running: false,
    };
    this.twins.set(id, twin);
    this.emit({ type: "twin-hatched", id, twin: this.descriptor(twin) });
    this.#log(twin, `${spec.note} — hatching on ${url}`);

    try {
      await worker.start();
    } catch (error) {
      this.#setStatus(twin, "error");
      this.#log(twin, `Failed to start: ${error.message}`);
      throw error;
    }
    this.#setStatus(twin, "ready");
    this.#log(twin, `Twin ready on ${url}`);

    // If the rapplication ships its OWN UI (static HTML), fetch it and keep it.
    // The tile loads the twin's Grail UI (same origin as the twin) and then
    // wipes it and injects this HTML in its place — so the custom UI's relative
    // /chat hits the twin directly (same origin, no server, no proxy, no CORS).
    if (spec.uiUrl) {
      try {
        twin.uiHtml = await fetch(spec.uiUrl).then((r) => (r.ok ? r.text() : Promise.reject(new Error(`HTTP ${r.status}`))));
        this.#log(twin, `Custom rapplication UI ready (${twin.uiHtml.length} bytes) — overrides the default Grail chat`);
        this.emit({ type: "twin-status", id, status: twin.status, twin: this.descriptor(twin) });
      } catch (error) {
        this.#log(twin, `Custom UI unavailable (${error.message}); using the default Grail chat.`);
      }
    }

    if (instruction) {
      // Kick its autonomous loop, but DO NOT block on it — the caller (and the
      // main Brainstem/Surgeon chat) stays free while the twin works.
      this.run(id, instruction).catch((error) => this.#log(twin, `Loop error: ${error.message}`));
    }
    return this.descriptor(twin);
  }

  // The wire: POST /chat to the twin's own worker (loopback). Every exchange is
  // emitted as a twin-message so the tile shows a live MULTIPLAYER transcript —
  // the Brainstem loop, the Brain Surgeon, and the user all talking to the same
  // rapplication in one room. Default session is shared per twin ("the room").
  async chat(id, prompt, { author = "you", sessionId = null } = {}) {
    const twin = this.get(id);
    const text = String(prompt || "");
    this.emit({ type: "twin-message", id, author, role: "user", text });
    // The kernel /chat is STATELESS — session_id does not accumulate turns
    // server-side; conversation_history is the only continuity mechanism. Carry a
    // per-twin room history so the loop, the Surgeon, and the user all build on
    // prior turns instead of speaking to a memoryless twin each time.
    if (!Array.isArray(twin.roomHistory)) twin.roomHistory = [];
    const body = {
      user_input: text,
      session_id: sessionId || `twin-room-${id}`,
      conversation_history: twin.roomHistory.slice(-40),
    };
    let data;
    try {
      const response = await fetch(`${twin.url}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) throw new Error(`Twin ${id} /chat returned HTTP ${response.status}.`);
      data = await response.json();
    } catch (error) {
      this.emit({ type: "twin-message", id, author: twin.name || "twin", role: "error", text: error.message });
      throw error;
    }
    const reply = String(data.response || data.assistant_response || data.result || "");
    twin.roomHistory.push({ role: "user", content: text }, { role: "assistant", content: reply });
    if (twin.roomHistory.length > 80) twin.roomHistory.splice(0, twin.roomHistory.length - 80);
    this.emit({ type: "twin-message", id, author: twin.name || "twin", role: "assistant", text: reply });
    return data;
  }

  // A bounded autonomous loop driven by the Brainstem over /chat. P1 proves the
  // loop end-to-end; the specialized Copilot Studio deploy loop is P2.
  async run(id, instruction, options = {}) {
    const { maxRounds = 4 } = options;
    const twin = this.get(id);
    if (twin.running) throw new Error(`Twin ${id} is already looping.`);
    twin.running = true;
    this.#setStatus(twin, "working");
    let outcome = "ready";
    const author = options.author || "Brainstem";
    const task = String(instruction || "").trim();
    try {
      let prompt = task;
      for (let round = 0; round < maxRounds; round += 1) {
        if (twin.closed) break;
        const reply = await this.chat(id, prompt, { author });
        if (twin.closed) break;
        const text = String(reply.response || reply.assistant_response || reply.result || "").trim();
        // The one visible, user-owned auth step (e.g. PAC device login). Pause
        // only on a genuine auth REQUEST — completion is checked first so a
        // finished reply that merely mentions sign-in isn't hijacked.
        if (saysDone(text)) { outcome = "done"; break; }
        if (NEEDS_AUTH_RE.test(text)) {
          outcome = "needs-auth";
          this.emit({ type: "twin-needs-auth", id, message: text.slice(0, 400) });
          break;
        }
        if (!text) {   // an empty reply is a failure, not success
          this.emit({ type: "twin-message", id, author, role: "error", text: "Twin returned an empty reply; stopping." });
          outcome = "ready";
          break;
        }
        // The twin now carries room memory (chat()), so restate the task rather
        // than a bare "Continue" to a memoryless worker.
        prompt = `Continue toward this task: ${task.slice(0, 300)}\n` +
          `If it is complete, reply DONE. If you need the user to sign in, say exactly what auth is required.`;
      }
    } finally {
      twin.running = false;
      this.#setStatus(twin, outcome === "needs-auth" ? "needs-auth" : "ready");
    }
    return this.descriptor(twin);
  }

  // Ask the visible Brainstem, over ITS /chat, for the next thing to say to the
  // twin. A dedicated planner session keeps this control chatter out of the
  // user's own Brainstem thread. Returns the Brainstem's raw text.
  async #brainstemPlan(sessionId, prompt, history = []) {
    const base = String(this.brainstemUrl() || "").replace(/\/$/, "");
    if (!base) throw new Error("No Brainstem URL to plan with.");
    const response = await fetch(`${base}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // The planner is stateless too — carry its running transcript so it never
      // loses the goal or what it already told the twin (see chat()).
      body: JSON.stringify({ user_input: String(prompt || ""), session_id: sessionId, conversation_history: history.slice(-40) }),
    });
    if (!response.ok) throw new Error(`Brainstem /chat returned HTTP ${response.status}.`);
    const data = await response.json();
    return String(data.response || data.assistant_response || data.result || "").trim();
  }

  // A GENUINE two-brain autonomous loop: the visible Brainstem plans each turn,
  // the twin executes it, the Brainstem reads the result and plans the next —
  // until it declares the goal met (or maxRounds). Unlike run() (which feeds the
  // twin a canned "Continue"), here the real Brainstem is in the loop. Both sides
  // are /chat only (canon: chat is the only wire); the host just relays. Every
  // turn streams into the twin room as a twin-message, so the user watches the
  // Brainstem <-> twin exchange unfold live and can interject at any time.
  async loop(id, goal, options = {}) {
    const { maxRounds = 6 } = options;
    const twin = this.get(id);
    if (twin.running) throw new Error(`Twin ${id} is already looping.`);
    const goalText = String(goal || "").trim();
    if (!goalText) {   // surface, don't throw-then-swallow (the caller's .catch would hide it)
      this.emit({ type: "twin-message", id, author: "Brainstem", role: "error",
        text: "I need a goal to loop on — tell me what to have the twin do." });
      return this.descriptor(twin);
    }
    twin.running = true;
    this.#setStatus(twin, "working");
    const planSession = `twin-loop-${id}`;
    const twinName = twin.name || "the twin";
    const brief =
      `You are steering a specialist agent called "${twinName}" over chat to accomplish a goal for the user, hands-off. ` +
      `Each turn you send ${twinName} ONE concrete instruction, read its reply, and decide the next step. ` +
      `Goal: ${goalText}`;
    // The planner's own running transcript — passed as conversation_history every
    // turn so the stateless kernel never loses the goal or what it already sent.
    const planHistory = [];
    const plan = async (prompt) => {
      const reply = await this.#brainstemPlan(planSession, prompt, planHistory);
      planHistory.push({ role: "user", content: prompt }, { role: "assistant", content: reply });
      return reply;
    };
    let outcome = "ready";
    try {
      // Opening move: the Brainstem's first instruction to the twin.
      let instruction = await plan(
        `${brief}\n\nReply with ONLY the first message to send to ${twinName} — a single concrete instruction, addressed to ${twinName}, no preamble.`);
      for (let round = 0; round < maxRounds; round += 1) {
        if (twin.closed || !instruction) break;
        // The twin executes; its reply streams into the room as its own turn,
        // the instruction as a "Brainstem" turn.
        const reply = await this.chat(id, instruction, { author: "Brainstem" });
        if (twin.closed) break;
        const twinText = String(reply.response || reply.assistant_response || reply.result || "").trim();
        // Pause only on a genuine, user-owned auth REQUEST.
        if (NEEDS_AUTH_RE.test(twinText)) {
          outcome = "needs-auth";
          this.emit({ type: "twin-needs-auth", id, message: twinText.slice(0, 400) });
          break;
        }
        // The Brainstem reads the twin's reply and plans the next move — the goal
        // is restated (belt-and-suspenders) alongside the forwarded history.
        const next = await plan(
          `Goal (unchanged): ${goalText}\n\n` +
          `${twinName} replied:\n"""\n${twinText.slice(0, 4000)}\n"""\n\n` +
          `If the goal is fully met, reply with exactly: DONE — <one short line on the result>. ` +
          `Otherwise reply with ONLY the next single instruction to send to ${twinName} (addressed to it, no preamble).`);
        if (twin.closed) break;
        if (planIsDone(next)) {
          this.emit({ type: "twin-message", id, author: "Brainstem", role: "assistant", text: next.trim() });
          outcome = "done";
          break;
        }
        instruction = next;
        if (round === maxRounds - 1) {
          this.emit({ type: "twin-message", id, author: "Brainstem", role: "assistant",
            text: `Paused after ${maxRounds} rounds — steer me or say continue to keep going.` });
        }
      }
    } catch (error) {
      if (!twin.closed) {
        this.emit({ type: "twin-message", id, author: "Brainstem", role: "error", text: `Loop error: ${error.message}` });
      }
      outcome = "ready";
    } finally {
      twin.running = false;
      this.#setStatus(twin, outcome === "needs-auth" ? "needs-auth" : "ready");
    }
    return this.descriptor(twin);
  }

  async close(id) {
    const key = String(id);
    const twin = this.twins.get(key);
    // Signal any in-flight loop/run to stop BEFORE teardown so its next status
    // emit can't resurrect the tile after we remove it.
    if (twin) { twin.closed = true; twin.running = false; }
    this.twins.delete(key);
    if (twin?.worker) await twin.worker.stop().catch(() => {});
    if (twin?.dir) {
      try { rmSync(twin.dir, { recursive: true, force: true }); } catch { /* best effort */ }
    }
    // Always emit — even for an already-absent id — so a stale tile is dismissable.
    this.emit({ type: "twin-closed", id: key });
    return { ok: true };
  }

  async stopAll() {
    const twins = Array.from(this.twins.values());
    this.twins.clear();
    await Promise.allSettled(twins.map((twin) => twin.worker.stop()));
  }
}

export const twinManagerInternals = { allocatePort, twinSlug };
