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
    this.twinsRoot = path.join(betaHome, "twins");
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

  #log(twin, line) {
    twin.loopLog.push({ at: new Date().toISOString(), line: String(line).slice(0, 600) });
    this.emit({ type: "twin-log", id: twin.id, line, status: twin.status });
  }

  #setStatus(twin, status) {
    twin.status = status;
    this.emit({ type: "twin-status", id: twin.id, status, twin: this.descriptor(twin) });
  }

  // Hatch a RAPPlication from the store into its own long-lived worker.
  async hatch(storeId, { instruction = null, createdUtc = null } = {}) {
    const cartridge = await this.store.download(storeId);   // sha256-verified
    const id = `${twinSlug(cartridge.id || storeId)}-${++this.seq}`;
    const agentsDir = path.join(this.twinsRoot, id, "agents");
    mkdirSync(agentsDir, { recursive: true });
    const filename = cartridge.filename && /_agent\.py$/.test(cartridge.filename)
      ? cartridge.filename
      : `${twinSlug(cartridge.id || storeId)}_agent.py`;
    writeFileSync(path.join(agentsDir, filename), cartridge.source, { mode: 0o600 });
    // Provenance: keep the pinned egg beside the agent (state-seeding is P2).
    if (cartridge.egg) {
      writeFileSync(path.join(this.twinsRoot, id, `${id}.egg`), cartridge.egg, { mode: 0o600 });
    }

    // Mint a mint-once RAPPID for the twin (route manager, UUID-anchor; §6.2).
    let rappid = null;
    try {
      rappid = this.routeManager?.packageAgent
        ? this.routeManager.packageAgent({ filename, source: cartridge.source }).agent_rappid
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
      storeId: cartridge.id || storeId,
      name: cartridge.entry?.name || cartridge.id || storeId,
      rappid,
      port,
      url,
      status: "hatching",
      license: cartridge.entry?.license || null,
      uiUrl: cartridge.entry?.uiUrl || null,
      dir: path.join(this.twinsRoot, id),
      worker,
      loopLog: [],
      createdUtc: createdUtc || null,
      running: false,
    };
    this.twins.set(id, twin);
    this.emit({ type: "twin-hatched", id, twin: this.descriptor(twin) });
    this.#log(twin, `Verified ${filename} (sha256 ${cartridge.sha256.slice(0, 12)}…) — hatching on ${url}`);

    try {
      await worker.start();
    } catch (error) {
      this.#setStatus(twin, "error");
      this.#log(twin, `Failed to start: ${error.message}`);
      throw error;
    }
    this.#setStatus(twin, "ready");
    this.#log(twin, `Twin ready on ${url}`);

    if (instruction) {
      // Kick its autonomous loop, but do not block hatch on it.
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
    try {
      let prompt = String(instruction || "");
      for (let round = 0; round < maxRounds; round += 1) {
        this.#log(twin, `→ ${prompt}`.slice(0, 200));
        const reply = await this.chat(id, prompt, { sessionId: `twin-loop-${id}` });
        const text = String(reply.assistant_response || reply.response || reply.result || "").trim();
        this.#log(twin, `← ${text}`.slice(0, 400));
        if (/\b(done|complete|finished|no further)\b/i.test(text) || !text) break;
        prompt = "Continue. If the task is complete, say DONE.";
      }
    } finally {
      twin.running = false;
      if (twin.status === "working") this.#setStatus(twin, "ready");
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
