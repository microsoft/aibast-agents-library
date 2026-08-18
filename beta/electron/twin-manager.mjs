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

export class TwinManager {
  constructor({ brainstemConfig, betaHome, routeManager = null, storeClient, onEvent = () => {} }) {
    if (!brainstemConfig) throw new Error("TwinManager needs a brainstemConfig.");
    if (!storeClient) throw new Error("TwinManager needs a RAPP Store client.");
    this.brainstemConfig = brainstemConfig;
    this.betaHome = betaHome;
    this.routeManager = routeManager;
    this.store = storeClient;
    this.onEvent = onEvent;
    this.twins = new Map();
    this.seq = 0;
    this.maxTwins = 8;   // cap concurrent workers so a runaway can't exhaust the machine
    this.twinsRoot = path.join(betaHome, "twins");
    // Clear stale twin dirs left by a crashed previous session (their workers,
    // if any, are orphaned and will be reaped by the OS; we start clean).
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

  // The wire: POST /chat to the twin's own worker (loopback, single-flight).
  async chat(id, prompt, { sessionId = null } = {}) {
    const twin = this.get(id);
    const body = { user_input: String(prompt || "") };
    if (sessionId) body.session_id = sessionId;
    const response = await fetch(`${twin.url}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error(`Twin ${id} /chat returned HTTP ${response.status}.`);
    }
    return response.json();
  }

  // A bounded autonomous loop driven by the Brainstem over /chat. P1 proves the
  // loop end-to-end; the specialized Copilot Studio deploy loop is P2.
  async run(id, instruction, { maxRounds = 4 } = {}) {
    const twin = this.get(id);
    if (twin.running) throw new Error(`Twin ${id} is already looping.`);
    twin.running = true;
    this.#setStatus(twin, "working");
    let outcome = "ready";
    try {
      let prompt = String(instruction || "");
      for (let round = 0; round < maxRounds; round += 1) {
        this.#log(twin, `→ ${prompt}`.slice(0, 200));
        const reply = await this.chat(id, prompt, { sessionId: `twin-loop-${id}` });
        const text = String(reply.assistant_response || reply.response || reply.result || "").trim();
        this.#log(twin, `← ${text}`.slice(0, 400));
        // The one visible, user-owned auth step (e.g. PAC device login). Pause
        // the loop here rather than spinning — the user completes it, then the
        // caller resumes with run() again.
        if (/device\s*code|device login|sign in|authenticat|pac auth|not authenticated/i.test(text)) {
          outcome = "needs-auth";
          this.emit({ type: "twin-needs-auth", id, message: text.slice(0, 400) });
          break;
        }
        if (/\b(done|complete|completed|finished|no further|draft (is )?ready)\b/i.test(text) || !text) {
          outcome = "done";
          break;
        }
        prompt = "Continue. If the task is complete, say DONE. If you need the user to sign in, say exactly what auth is required.";
      }
    } finally {
      twin.running = false;
      this.#setStatus(twin, outcome === "needs-auth" ? "needs-auth" : "ready");
    }
    return this.descriptor(twin);
  }

  async close(id) {
    const twin = this.twins.get(String(id));
    if (!twin) return { ok: true };
    this.twins.delete(String(id));
    await twin.worker.stop().catch(() => {});
    try {
      rmSync(twin.dir, { recursive: true, force: true });
    } catch {
      // best effort
    }
    this.emit({ type: "twin-closed", id: twin.id });
    return { ok: true };
  }

  async stopAll() {
    const twins = Array.from(this.twins.values());
    this.twins.clear();
    await Promise.allSettled(twins.map((twin) => twin.worker.stop()));
  }
}

export const twinManagerInternals = { allocatePort, twinSlug };
