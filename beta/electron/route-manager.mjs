import { createHash, randomUUID } from "node:crypto";
import {
  copyFileSync,
  chmodSync,
  existsSync,
  linkSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import net from "node:net";
import path from "node:path";

import { BrainstemProcess } from "./brainstem-process.mjs";
import {
  Hb,
  canonical,
  mintRappid,
  packEgg,
} from "./rapp-protocol.mjs";


const ROUTING_SCHEMA = "rapp-beta-routing/1";
const STACK_SCHEMA = "rapp-beta-stack/1";
const MAX_AGENT_BYTES = 512 * 1024;
const AGENT_FILE = /^[A-Za-z0-9_.-]+_agent\.py$/;
const MEMORY_FILES = new Set([
  "context_memory_agent.py",
  "manage_memory_agent.py",
]);

function ensurePrivateDirectory(directory) {
  mkdirSync(directory, { recursive: true });
  try {
    chmodSync(directory, 0o700);
  } catch {}
}

function atomicWriteJson(filePath, value) {
  ensurePrivateDirectory(path.dirname(filePath));
  const temporary = `${filePath}.${process.pid}.tmp`;
  writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, {
    mode: 0o600,
  });
  renameSync(temporary, filePath);
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function safeAgentFilename(value) {
  const filename = path.basename(String(value || "").trim());
  if (!AGENT_FILE.test(filename) || filename === "basic_agent.py") {
    throw new Error("Agent filename must be a safe *_agent.py name.");
  }
  return filename;
}

function slugFromFilename(filename) {
  const slug = filename
    .replace(/_agent\.py$/, "")
    .replaceAll("_", "-")
    .toLowerCase()
    .replace(/[^a-z0-9-]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
  return slug || "agent";
}

function stackNameFromRappid(rappid) {
  const match = String(rappid || "").match(/^rappid:@[^/]+\/([^:]+):/);
  const slug = String(match?.[1] || "stack")
    .replace(/^brainstem-/, "")
    .replace(/-stack$/, "");
  return slug || "stack";
}

function hardlinkOrCopy(source, destination) {
  try {
    linkSync(source, destination);
    return "hardlink";
  } catch {
    copyFileSync(source, destination);
    return "copy";
  }
}

function allocatePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = typeof address === "object" && address
        ? address.port
        : null;
      server.close((error) => {
        if (error) reject(error);
        else if (!port) reject(new Error("Could not allocate worker port."));
        else resolve(port);
      });
    });
  });
}

function contextMemorySource(memoryGuid) {
  return `from agents.context_memory_agent import ContextMemoryAgent


class RoutedContextMemoryAgent(ContextMemoryAgent):
    def system_context(self):
        self.storage_manager.set_memory_context(${JSON.stringify(memoryGuid)})
        return super().system_context()

    def perform(self, **kwargs):
        kwargs["user_guid"] = ${JSON.stringify(memoryGuid)}
        return super().perform(**kwargs)
`;
}

function manageMemorySource(memoryGuid) {
  return `from agents.manage_memory_agent import ManageMemoryAgent


class RoutedManageMemoryAgent(ManageMemoryAgent):
    def perform(self, **kwargs):
        kwargs["user_guid"] = ${JSON.stringify(memoryGuid)}
        return super().perform(**kwargs)
`;
}

export class BetaRouteManager {
  constructor({
    betaHome,
    brainstemConfig,
    owner = process.env.BRAINSTEM_BETA_RAPP_OWNER || "microsoft",
    onActivate = () => {},
  } = {}) {
    this.betaHome = betaHome;
    this.brainstemConfig = brainstemConfig;
    this.owner = owner;
    this.onActivate = onActivate;
    this.routingRoot = path.join(betaHome, "routing");
    this.identityFile = path.join(this.routingRoot, "identity.json");
    this.stackRoot = path.join(this.routingRoot, "stacks");
    this.objectRoot = path.join(this.routingRoot, "objects");
    this.eggRoot = path.join(this.routingRoot, "eggs");
    this.compositionRoot = path.join(this.routingRoot, "compositions");
    this.workerLogRoot = path.join(betaHome, "logs", "workers");
    this.workers = new Map();
    this.routeLocks = new Map();
    this.telemetry = [];
    this.telemetrySequence = 0;
    this.activeRoute = null;
    for (const directory of [
      this.routingRoot,
      this.stackRoot,
      this.objectRoot,
      this.eggRoot,
      this.compositionRoot,
      this.workerLogRoot,
    ]) {
      ensurePrivateDirectory(directory);
    }
  }

  identity() {
    if (existsSync(this.identityFile)) {
      const identity = JSON.parse(readFileSync(this.identityFile, "utf8"));
      let changed = false;
      if (!identity.active_stack_rappid) {
        identity.active_stack_rappid = identity.default_stack_rappid;
        changed = true;
      }

      if (!Array.isArray(identity.overlay_stack_rappids)) {
        identity.overlay_stack_rappids = [];
        changed = true;
      }
      if (changed) atomicWriteJson(this.identityFile, identity);
      return identity;
    }
    const caller = mintRappid(this.owner, "brainstem-beta");
    const rootStack = mintRappid(this.owner, "brainstem-default-stack");
    const identity = {
      schema: ROUTING_SCHEMA,
      caller_rappid: caller.rappid,
      memory_guid: caller.uuidAnchor,
      default_stack_rappid: rootStack.rappid,
      active_stack_rappid: rootStack.rappid,
      overlay_stack_rappids: [],
      created_utc: new Date().toISOString(),
    };
    atomicWriteJson(this.identityFile, identity);
    atomicWriteJson(this.stackPath(rootStack.rappid), {
      schema: STACK_SCHEMA,
      rappid: rootStack.rappid,
      owner_rappid: caller.rappid,
      name: "default",
      parent_rappid: null,
      overlay_rappids: [],
      agents: [],
    });
    return identity;
  }

  recordTelemetry(type, details = {}) {
    const event = {
      sequence: ++this.telemetrySequence,
      timestamp: new Date().toISOString(),
      type,
      ...details,
    };
    this.telemetry.push(event);
    if (this.telemetry.length > 500) this.telemetry.shift();
    return event;
  }

  telemetrySnapshot() {
    const activeWorker = this.activeRoute
      ? this.workers.get(this.activeRoute.compositionHash)
      : null;
    return {
      sequence: this.telemetrySequence,
      active_route: this.activeRoute
        ? {
            url: this.activeRoute.url,
            composition_hash: this.activeRoute.transientCompositionHash
              || this.activeRoute.compositionHash,
            base_composition_hash: this.activeRoute.compositionHash,
          }
        : null,
      worker_count: this.workers.size,
      stack_count: this.stacks().length,
      stack_tree: this.stackTree(),
      active_composition_fingerprint: activeWorker
        ? this.compositionFingerprint(activeWorker)
        : null,
      object_count: readdirSync(this.objectRoot).length,
      egg_count: readdirSync(this.eggRoot).length,
      events: [...this.telemetry],
    };
  }

  compositionFingerprint(worker) {
    const files = readdirSync(worker.agentDirectory)
      .filter((filename) => filename.endsWith(".py"))
      .sort();
    const hash = createHash("sha256");
    for (const filename of files) {
      hash.update(filename);
      hash.update("\0");
      hash.update(readFileSync(path.join(worker.agentDirectory, filename)));
      hash.update("\0");
    }
    const manifestPath = path.join(
      worker.compositionDirectory,
      "complete.json",
    );
    const manifest = readFileSync(manifestPath);
    hash.update("complete.json");
    hash.update("\0");
    hash.update(manifest);
    return {
      agent_directory: worker.agentDirectory,
      files,
      manifest_path: manifestPath,
      source_hash: hash.digest("hex"),
    };
  }

  stackPath(rappid) {
    return path.join(this.stackRoot, `${sha256(Buffer.from(rappid))}.json`);
  }

  normalizeStack(stack, filePath) {
    let changed = false;
    if (!stack.name) {
      stack.name = stackNameFromRappid(stack.rappid);
      changed = true;
    }
    if (!Array.isArray(stack.overlay_rappids)) {
      stack.overlay_rappids = [];
      changed = true;
    }
    if (!Array.isArray(stack.agents)) {
      stack.agents = [];
      changed = true;
    }
    if (changed) atomicWriteJson(filePath, stack);
    return stack;
  }

  loadStack(rappid) {
    const filePath = this.stackPath(rappid);
    if (!existsSync(filePath)) throw new Error(`Unknown stack RAPPID: ${rappid}`);
    return this.normalizeStack(
      JSON.parse(readFileSync(filePath, "utf8")),
      filePath,
    );
  }

  stacks() {
    return readdirSync(this.stackRoot)
      .filter((filename) => filename.endsWith(".json"))
      .map((filename) => {
        const filePath = path.join(this.stackRoot, filename);
        return this.normalizeStack(
          JSON.parse(readFileSync(filePath, "utf8")),
          filePath,
        );
      })
      .sort((left, right) => left.name.localeCompare(right.name));
  }

  stackTree() {
    const identity = this.identity();
    const stacks = this.stacks();
    const byRappid = new Map(stacks.map((stack) => [stack.rappid, stack]));
    const children = new Map();
    for (const stack of stacks) {
      if (stack.parent_rappid && !byRappid.has(stack.parent_rappid)) {
        throw new Error(`Unknown parent stack RAPPID: ${stack.parent_rappid}`);
      }
      const parent = stack.parent_rappid || null;
      if (!children.has(parent)) children.set(parent, []);
      children.get(parent).push(stack);
    }
    for (const siblings of children.values()) {
      siblings.sort((left, right) => (
        left.name.localeCompare(right.name)
        || left.rappid.localeCompare(right.rappid)
      ));
    }
    const buildNode = (stack, lineage = new Set()) => {
      if (lineage.has(stack.rappid)) {
        throw new Error("Stack parent cycle detected.");
      }
      const nextLineage = new Set(lineage);
      nextLineage.add(stack.rappid);
      const overlayIndex = identity.overlay_stack_rappids.indexOf(stack.rappid);
      return {
        name: stack.name,
        rappid: stack.rappid,
        parent_rappid: stack.parent_rappid,
        active: stack.rappid === identity.active_stack_rappid,
        overlay_order: overlayIndex >= 0 ? overlayIndex + 1 : null,
        agent_count: stack.agents.length,
        children: (children.get(stack.rappid) || []).map(
          (child) => buildNode(child, nextLineage),
        ),
      };
    };
    return (children.get(null) || []).map((stack) => buildNode(stack));
  }

  stackLineage(rappid) {
    const lineage = [];
    const seen = new Set();
    let current = rappid;
    while (current) {
      if (seen.has(current)) throw new Error("Stack parent cycle detected.");
      seen.add(current);
      const stack = this.loadStack(current);
      lineage.unshift(stack);
      current = stack.parent_rappid;
    }
    return lineage;
  }

  async createStack({ name, parentRappid = null }) {
    const normalizedName = String(name || "")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9-]/g, "-")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "");
    if (!normalizedName) throw new Error("Stack name is required.");
    const identity = this.identity();
    const parent = parentRappid || identity.active_stack_rappid;
    this.loadStack(parent);
    const minted = mintRappid(
      this.owner,
      `brainstem-${normalizedName}-stack`,
    );
    const stack = {
      schema: STACK_SCHEMA,
      rappid: minted.rappid,
      owner_rappid: identity.caller_rappid,
      name: normalizedName,
      parent_rappid: parent,
      overlay_rappids: [],
      agents: [],
    };
    this.saveStack(stack);
    this.recordTelemetry("stack-created", {
      parent_rappid: parent,
      stack_rappid: stack.rappid,
    });
    return stack;
  }

  async selectStack({ stackRappid, overlayRappids = [] }) {
    const identity = this.identity();
    const leaf = String(stackRappid || "").trim();
    if (!leaf) throw new Error("A leaf stack RAPPID is required.");
    this.loadStack(leaf);
    if (!Array.isArray(overlayRappids)) {
      throw new Error("Overlay stack RAPPIDs must be an ordered array.");
    }
    const overlays = [];
    for (const overlay of overlayRappids) {
      if (overlay === leaf) {
        throw new Error("The selected leaf stack cannot also be an overlay.");
      }
      this.loadStack(overlay);
      if (!overlays.includes(overlay)) overlays.push(overlay);
    }
    identity.active_stack_rappid = leaf;
    identity.overlay_stack_rappids = overlays;
    atomicWriteJson(this.identityFile, identity);
    this.recordTelemetry("stack-selected", {
      active_stack_rappid: leaf,
      overlay_stack_rappids: identity.overlay_stack_rappids,
    });
    return {
      caller_rappid: identity.caller_rappid,
      memory_guid: identity.memory_guid,
      active_stack_rappid: leaf,
      overlay_stack_rappids: identity.overlay_stack_rappids,
      stack_tree: this.stackTree(),
    };
  }

  saveStack(stack) {
    atomicWriteJson(this.stackPath(stack.rappid), stack);
  }

  async removeStack({ stackRappid }) {
    const identity = this.identity();
    const target = String(stackRappid || "").trim();
    if (!target) throw new Error("A stack RAPPID is required.");
    if (target === identity.default_stack_rappid) {
      throw new Error("The default stack cannot be removed.");
    }
    if (target === identity.active_stack_rappid) {
      throw new Error("The active stack cannot be removed.");
    }
    if (identity.overlay_stack_rappids.includes(target)) {
      throw new Error("An active overlay stack cannot be removed.");
    }
    const stack = this.loadStack(target);
    if (stack.agents.length) {
      throw new Error("Remove every stack agent before removing the stack.");
    }
    if (this.stacks().some((candidate) => candidate.parent_rappid === target)) {
      throw new Error("A stack with child stacks cannot be removed.");
    }
    rmSync(this.stackPath(target), { force: true });
    this.recordTelemetry("stack-removed", {
      stack_rappid: target,
    });
    return {
      removed_stack_rappid: target,
      stack_tree: this.stackTree(),
    };
  }

  cacheSource(source) {
    const bytes = Buffer.from(source, "utf8");
    if (!bytes.length || bytes.length > MAX_AGENT_BYTES) {
      throw new Error("Agent source must be between 1 byte and 512 KiB.");
    }
    const address = Hb("rapp/1:egg", bytes);
    const objectPath = path.join(this.objectRoot, `${address}.py`);
    if (!existsSync(objectPath)) {
      writeFileSync(objectPath, bytes, { mode: 0o600 });
    }
    return { address, bytes, objectPath };
  }

  packageAgent({ filename, source, existingRappid = null }) {
    const safeName = safeAgentFilename(filename);
    const cached = this.cacheSource(source);
    const identity = existingRappid
      ? { rappid: existingRappid }
      : mintRappid(this.owner, slugFromFilename(safeName));
    const rappidJson = Buffer.from(canonical({ rappid: identity.rappid }), "utf8");
    const egg = packEgg({
      variant: "rapplication",
      rappid: identity.rappid,
      createdUtc: new Date().toISOString(),
      files: {
        "rappid.json": rappidJson,
        [safeName]: cached.bytes,
      },
    });
    const eggAddress = Hb("rapp/1:egg", egg);
    const eggPath = path.join(this.eggRoot, `${eggAddress}.egg`);
    if (!existsSync(eggPath)) writeFileSync(eggPath, egg, { mode: 0o600 });
    return {
      filename: safeName,
      agent_rappid: identity.rappid,
      egg_address: eggAddress,
      source_address: cached.address,
      object_path: cached.objectPath,
    };
  }

  ephemeralAgentEntry({ filename, source }) {
    const safeName = safeAgentFilename(filename);
    const bytes = Buffer.from(String(source || ""), "utf8");
    if (!bytes.length || bytes.length > MAX_AGENT_BYTES) {
      throw new Error("Agent source must be between 1 byte and 512 KiB.");
    }
    return {
      filename: safeName,
      address: Hb("rapp/1:egg", bytes),
      bytes,
      scope: "ephemeral",
    };
  }

  async installScopedAgent({ filename, source, stackRappid = null }) {
    const identity = this.identity();
    const stack = this.loadStack(
      stackRappid || identity.active_stack_rappid,
    );
    const safeName = safeAgentFilename(filename);
    const previous = stack.agents.find((agent) => agent.filename === safeName);
    const packaged = this.packageAgent({
      filename: safeName,
      source,
      existingRappid: previous?.agent_rappid || null,
    });
    stack.agents = [
      ...stack.agents.filter((agent) => agent.filename !== packaged.filename),
      packaged,
    ].sort((left, right) => left.filename.localeCompare(right.filename));
    this.saveStack(stack);
    this.recordTelemetry("stack-agent-installed", {
      filename: packaged.filename,
      stack_rappid: stack.rappid,
    });
    return {
      user_rappid: identity.caller_rappid,
      memory_guid: identity.memory_guid,
      stack_rappid: stack.rappid,
      agent: packaged,
    };
  }

  async listScopedAgents({ stackRappid = null } = {}) {
    const identity = this.identity();
    const stack = this.loadStack(stackRappid || identity.active_stack_rappid);
    const descriptor = this.compositionDescriptor();
    return {
      user_rappid: identity.caller_rappid,
      memory_guid: identity.memory_guid,
      active_stack_rappid: identity.active_stack_rappid,
      overlay_stack_rappids: identity.overlay_stack_rappids,
      selected_stack: stack,
      stack_lineage: descriptor.selectedStacks.map((item) => item.rappid),
      stack_tree: this.stackTree(),
      composition_hash: descriptor.compositionHash,
      agents: stack.agents,
    };
  }

  async removeScopedAgent({ filename, stackRappid = null }) {
    const identity = this.identity();
    const stack = this.loadStack(
      stackRappid || identity.active_stack_rappid,
    );
    const safeName = safeAgentFilename(filename);
    const before = stack.agents.length;
    stack.agents = stack.agents.filter((agent) => agent.filename !== safeName);
    if (stack.agents.length === before) {
      throw new Error(`Scoped agent not found: ${safeName}`);
    }
    this.saveStack(stack);
    this.recordTelemetry("stack-agent-removed", {
      filename: safeName,
      stack_rappid: stack.rappid,
    });
    return {
      removed: safeName,
      stack_rappid: stack.rappid,
    };
  }

  async removeActiveAgent({ filename }) {
    const safeName = safeAgentFilename(filename);
    const active = this.activeAgentFiles().find(
      (agent) => agent.filename === safeName,
    );
    if (!active) throw new Error(`Active agent not found: ${safeName}`);
    if (active.scope === "memory") {
      throw new Error(
        `${safeName} is generated from the beta identity and cannot be deleted.`,
      );
    }
    if (active.scope === "ephemeral") {
      throw new Error(
        `${safeName} is temporary and is removed automatically after its request.`,
      );
    }
    if (active.scope === "global") {
      const globalDirectory = path.resolve(
        this.brainstemConfig.brainstemDir,
        "agents",
      );
      const sourcePath = path.resolve(globalDirectory, safeName);
      if (path.dirname(sourcePath) !== globalDirectory) {
        throw new Error("Global agent path escaped the agents directory.");
      }
      if (!existsSync(sourcePath)) {
        throw new Error(`Global agent source not found: ${safeName}`);
      }
      rmSync(sourcePath, { force: true });
      this.recordTelemetry("global-agent-removed", {
        filename: safeName,
      });
      return { removed: safeName, scope: active.scope };
    }
    if (active.scope.startsWith("stack:")) {
      const stackRappid = active.scope.slice("stack:".length);
      const result = await this.removeScopedAgent({
        filename: safeName,
        stackRappid,
      });
      return { ...result, scope: active.scope };
    }
    throw new Error(`Unsupported agent scope: ${active.scope}`);
  }

  globalAgentEntries(memoryGuid) {
    const globalDirectory = path.join(this.brainstemConfig.brainstemDir, "agents");
    const entries = [];
    for (const filename of readdirSync(globalDirectory).sort()) {
      if (!filename.endsWith("_agent.py") || filename.startsWith("__")) continue;
      if (MEMORY_FILES.has(filename)) continue;
      const source = readFileSync(path.join(globalDirectory, filename), "utf8");
      entries.push({
        filename,
        ...this.cacheSource(source),
        scope: "global",
      });
    }
    for (const [filename, source] of [
      ["context_memory_agent.py", contextMemorySource(memoryGuid)],
      ["manage_memory_agent.py", manageMemorySource(memoryGuid)],
    ]) {
      entries.push({
        filename,
        ...this.cacheSource(source),
        scope: "memory",
      });
    }
    return entries;
  }

  compositionDescriptor({ ephemeralAgent = null } = {}) {
    const identity = this.identity();
    const stack = this.loadStack(identity.active_stack_rappid);
    const entries = this.globalAgentEntries(identity.memory_guid);
    const selectedStacks = [];
    for (const candidate of [
      stack.rappid,
      ...identity.overlay_stack_rappids,
    ]) {
      for (const inherited of this.stackLineage(candidate)) {
        if (!selectedStacks.some((item) => item.rappid === inherited.rappid)) {
          selectedStacks.push(inherited);
        }
      }
    }
    for (const selected of selectedStacks) {
      for (const agent of selected.agents) {
        entries.push({
          filename: agent.filename,
          address: agent.source_address,
          objectPath: agent.object_path,
          scope: `stack:${selected.rappid}`,
        });
      }
    }
    const ephemeralNonce = ephemeralAgent ? randomUUID() : null;
    if (ephemeralAgent) entries.push(this.ephemeralAgentEntry(ephemeralAgent));

    const byFilename = new Map();
    for (const entry of entries) {
      if (byFilename.has(entry.filename)) {
        throw new Error(
          `Agent composition collision for ${entry.filename}; `
          + "explicit override policy is required.",
        );
      }
      byFilename.set(entry.filename, entry);
    }
    const ordered = [...byFilename.values()].sort(
      (left, right) => left.filename.localeCompare(right.filename),
    );
    const compositionDocument = {
      caller_rappid: identity.caller_rappid,
      memory_guid: identity.memory_guid,
      stack_rappid: stack.rappid,
      overlay_stack_rappids: identity.overlay_stack_rappids,
      stack_lineage: selectedStacks.map((selected) => selected.rappid),
      agents: ordered.map((entry) => ({
        filename: entry.filename,
        address: entry.address,
        scope: entry.scope,
      })),
    };
    if (ephemeralNonce) {
      compositionDocument.ephemeral_nonce = ephemeralNonce;
    }
    const compositionHash = sha256(
      Buffer.from(canonical(compositionDocument)),
    );
    return {
      compositionHash,
      entries: ordered,
      identity,
      stack,
      selectedStacks,
      ephemeral: Boolean(ephemeralAgent),
      ephemeralNonce,
    };
  }

  compositionIsComplete(descriptor, agentDirectory, manifest) {
    if (
      manifest?.composition_hash !== descriptor.compositionHash
      || !Array.isArray(manifest.agents)
      || manifest.agents.length !== descriptor.entries.length
    ) {
      return false;
    }
    const expected = new Map(
      descriptor.entries.map((entry) => [entry.filename, entry]),
    );
    return manifest.agents.every((agent) => {
      const entry = expected.get(agent.filename);
      return Boolean(
        entry
        && agent.address === entry.address
        && agent.scope === entry.scope
        && existsSync(path.join(agentDirectory, agent.filename)),
      );
    });
  }

  materializeComposition(descriptor) {
    const compositionDirectory = path.join(
      this.compositionRoot,
      descriptor.compositionHash,
    );
    const agentDirectory = path.join(compositionDirectory, "agents");
    const completeFile = path.join(compositionDirectory, "complete.json");
    if (existsSync(completeFile)) {
      try {
        const manifest = JSON.parse(readFileSync(completeFile, "utf8"));
        if (this.compositionIsComplete(descriptor, agentDirectory, manifest)) {
          return { compositionDirectory, agentDirectory };
        }
      } catch {}
    }
    rmSync(compositionDirectory, { recursive: true, force: true });
    ensurePrivateDirectory(agentDirectory);
    const links = [];
    for (const entry of descriptor.entries) {
      const destination = path.join(agentDirectory, entry.filename);
      let method;
      if (entry.scope === "ephemeral") {
        writeFileSync(destination, entry.bytes, { mode: 0o600 });
        method = "ephemeral";
      } else {
        method = hardlinkOrCopy(entry.objectPath, destination);
      }
      links.push({
        filename: entry.filename,
        method,
        address: entry.address,
        scope: entry.scope,
      });
    }
    atomicWriteJson(completeFile, {
      schema: ROUTING_SCHEMA,
      composition_hash: descriptor.compositionHash,
      caller_rappid: descriptor.identity.caller_rappid,
      memory_guid: descriptor.identity.memory_guid,
      stack_rappid: descriptor.stack.rappid,
      overlay_stack_rappids: descriptor.identity.overlay_stack_rappids,
      stack_lineage: descriptor.selectedStacks.map((stack) => stack.rappid),
      agents: links,
    });
    return { compositionDirectory, agentDirectory };
  }

  async startWorker(descriptor) {
    const existing = this.workers.get(descriptor.compositionHash);
    if (existing) {
      existing.lastUsed = Date.now();
      return existing.route;
    }
    const materialized = this.materializeComposition(descriptor);
    const port = await allocatePort();
    const config = {
      ...this.brainstemConfig,
      port,
      url: `http://127.0.0.1:${port}`,
      logFile: path.join(
        this.workerLogRoot,
        `${descriptor.compositionHash}.log`,
      ),
      env: {
        AGENTS_PATH: materialized.agentDirectory,
        BRAINSTEM_BETA_ROUTED_WORKER: "1",
      },
    };
    const process = new BrainstemProcess(config);
    const result = await process.start();
    const route = {
      url: config.url,
      port,
      compositionHash: descriptor.compositionHash,
      callerRappid: descriptor.identity.caller_rappid,
      memoryGuid: descriptor.identity.memory_guid,
      stackRappid: descriptor.stack.rappid,
      overlayStackRappids: descriptor.identity.overlay_stack_rappids,
      stackLineage: descriptor.selectedStacks.map((stack) => stack.rappid),
      health: result.health,
    };
    this.workers.set(descriptor.compositionHash, {
      activeRequests: 0,
      agentDirectory: materialized.agentDirectory,
      compositionDirectory: materialized.compositionDirectory,
      process,
      route,
      lastUsed: Date.now(),
      ephemeral: descriptor.ephemeral,
    });
    this.recordTelemetry("worker-started", {
      composition_hash: descriptor.compositionHash,
      url: route.url,
      worker_count: this.workers.size,
    });
    return route;
  }

  async waitForWorkerIdle(worker, timeoutMs = 30000) {
    const deadline = Date.now() + timeoutMs;
    while (worker.activeRequests > 0 && Date.now() < deadline) {
      await new Promise((resolve) => setTimeout(resolve, 50));
    }
    if (worker.activeRequests > 0) {
      throw new Error("The superseded Brainstem worker is still handling a request.");
    }
  }

  async retireInactiveWorker(compositionHash) {
    const worker = this.workers.get(compositionHash);
    if (!worker || worker.route === this.activeRoute) return;
    await this.waitForWorkerIdle(worker);
    if (worker.route === this.activeRoute) return;
    this.workers.delete(compositionHash);
    await worker.process.stop();
    if (worker.retiredCompositionDirectory) {
      rmSync(worker.retiredCompositionDirectory, {
        recursive: true,
        force: true,
      });
    }
    this.recordTelemetry("worker-stopped", {
      composition_hash: compositionHash,
      url: worker.route.url,
      worker_count: this.workers.size,
    });
  }

  async activate(route) {
    this.activeRoute = route;
    this.recordTelemetry("route-activated", {
      active_composition_hash: route.transientCompositionHash
        || route.compositionHash,
      base_composition_hash: route.compositionHash,
      url: route.url,
    });
    await this.onActivate(route);
    return route;
  }

  async startDefaultUnlocked() {
    const previous = this.activeRoute;
    const descriptor = this.compositionDescriptor();
    const route = await this.activate(await this.startWorker(descriptor));
    if (
      previous
      && previous.compositionHash !== route.compositionHash
    ) {
      await this.retireInactiveWorker(previous.compositionHash);
    }
    return route;
  }

  async startDefault() {
    return this.withRouteLock(
      "__lifecycle__",
      () => this.startDefaultUnlocked(),
    );
  }

  async withRouteLock(key, callback) {
    const previous = this.routeLocks.get(key) || Promise.resolve();
    this.recordTelemetry("lock-wait", {
      key,
      queued: this.routeLocks.has(key),
    });
    let release;
    const current = new Promise((resolve) => {
      release = resolve;
    });
    const tail = previous.then(() => current);
    this.routeLocks.set(key, tail);
    await previous;
    this.recordTelemetry("lock-acquired", { key });
    try {
      return await callback();
    } finally {
      release();
      if (this.routeLocks.get(key) === tail) this.routeLocks.delete(key);
      this.recordTelemetry("lock-released", { key });
    }
  }

  async withActiveEphemeral(descriptor, callback) {
    return this.withRouteLock("__lifecycle__", () => {
      const route = this.activeRoute;
      const worker = route
        ? this.workers.get(route.compositionHash)
        : null;
      if (!worker) throw new Error("No active Brainstem worker is available.");
      return this.withRouteLock(route.compositionHash, async () => {
        const entry = descriptor.entries.find(
          (candidate) => candidate.scope === "ephemeral",
        );
        if (!entry) throw new Error("The ephemeral agent entry is missing.");
        const destination = path.join(worker.agentDirectory, entry.filename);
        if (existsSync(destination)) {
          throw new Error(
            `Agent composition collision for ${entry.filename}; `
            + "explicit override policy is required.",
          );
        }
        const manifestPath = path.join(
          worker.compositionDirectory,
          "complete.json",
        );
        const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
        writeFileSync(destination, entry.bytes, { mode: 0o600 });
        manifest.active_composition_hash = descriptor.compositionHash;
        manifest.agents.push({
          filename: entry.filename,
          method: "ephemeral",
          address: entry.address,
          scope: entry.scope,
        });
        atomicWriteJson(manifestPath, manifest);
        route.transientCompositionHash = descriptor.compositionHash;
        worker.activeRequests += 1;
        this.recordTelemetry("ephemeral-injected", {
          active_composition_hash: descriptor.compositionHash,
          base_composition_hash: route.compositionHash,
          egg_count: readdirSync(this.eggRoot).length,
          filename: entry.filename,
          manifest_agent_count: manifest.agents.length,
          object_count: readdirSync(this.objectRoot).length,
          url: route.url,
        });
        await this.activate(route);
        try {
          this.recordTelemetry("ephemeral-callback-start", {
            active_composition_hash: descriptor.compositionHash,
            filename: entry.filename,
            url: route.url,
          });
          const result = await callback(route);
          this.recordTelemetry("ephemeral-callback-end", {
            active_composition_hash: descriptor.compositionHash,
            filename: entry.filename,
            request_id: result?.requestId || null,
            url: route.url,
          });
          return result;
        } catch (error) {
          this.recordTelemetry("ephemeral-callback-error", {
            active_composition_hash: descriptor.compositionHash,
            error: String(error?.message || error),
            filename: entry.filename,
            url: route.url,
          });
          throw error;
        } finally {
          rmSync(destination, { force: true });
          rmSync(path.join(worker.agentDirectory, "__pycache__"), {
            recursive: true,
            force: true,
          });
          const retiredManifest = JSON.parse(
            readFileSync(manifestPath, "utf8"),
          );
          retiredManifest.agents = retiredManifest.agents.filter(
            (agent) => agent.scope !== "ephemeral",
          );
          delete retiredManifest.active_composition_hash;
          atomicWriteJson(manifestPath, retiredManifest);
          worker.activeRequests = Math.max(0, worker.activeRequests - 1);
          delete route.transientCompositionHash;
          this.recordTelemetry("ephemeral-cleaned", {
            active_composition_hash: descriptor.compositionHash,
            egg_count: readdirSync(this.eggRoot).length,
            filename: entry.filename,
            file_exists: existsSync(destination),
            manifest_has_ephemeral: retiredManifest.agents.some(
              (agent) => agent.scope === "ephemeral",
            ),
            object_count: readdirSync(this.objectRoot).length,
            url: route.url,
          });
          await this.activate(route);
        }
      });
    });
  }

  async retireEphemeralWorker(descriptor) {
    const worker = this.workers.get(descriptor.compositionHash);
    if (!worker) return this.startDefaultUnlocked();
    for (const entry of descriptor.entries.filter(
      (candidate) => candidate.scope === "ephemeral",
    )) {
      rmSync(path.join(worker.agentDirectory, entry.filename), { force: true });
    }
    rmSync(path.join(worker.agentDirectory, "__pycache__"), {
      recursive: true,
      force: true,
    });
    const retiredManifestPath = path.join(
      worker.compositionDirectory,
      "complete.json",
    );
    if (existsSync(retiredManifestPath)) {
      const retiredManifest = JSON.parse(
        readFileSync(retiredManifestPath, "utf8"),
      );
      retiredManifest.agents = retiredManifest.agents.filter(
        (agent) => agent.scope !== "ephemeral",
      );
      retiredManifest.retired_ephemeral = true;
      atomicWriteJson(retiredManifestPath, retiredManifest);
    }

    const defaultDescriptor = this.compositionDescriptor();
    this.materializeComposition(defaultDescriptor);
    const previousDefault = this.workers.get(defaultDescriptor.compositionHash);
    if (previousDefault && previousDefault !== worker) {
      await this.waitForWorkerIdle(previousDefault);
      this.workers.delete(defaultDescriptor.compositionHash);
      await previousDefault.process.stop();
      if (previousDefault.retiredCompositionDirectory) {
        rmSync(previousDefault.retiredCompositionDirectory, {
          recursive: true,
          force: true,
        });
      }
    }

    this.workers.delete(descriptor.compositionHash);
    worker.ephemeral = false;
    worker.lastUsed = Date.now();
    worker.retiredCompositionDirectory = worker.compositionDirectory;
    worker.route.compositionHash = defaultDescriptor.compositionHash;
    worker.route.stackRappid = defaultDescriptor.stack.rappid;
    worker.route.overlayStackRappids = defaultDescriptor.identity.overlay_stack_rappids;
    worker.route.stackLineage = defaultDescriptor.selectedStacks.map(
      (stack) => stack.rappid,
    );
    this.workers.set(defaultDescriptor.compositionHash, worker);
    return this.activate(worker.route);
  }

  async withRoute(options, callback) {
    const descriptor = this.compositionDescriptor({
      ephemeralAgent: options?.ephemeralAgent || null,
    });
    if (
      descriptor.ephemeral
      && this.activeRoute
      && this.workers.has(this.activeRoute.compositionHash)
    ) {
      return this.withActiveEphemeral(descriptor, callback);
    }
    return this.withRouteLock("__lifecycle__", async () => {
      const route = await this.startWorker(descriptor);
      const worker = this.workers.get(descriptor.compositionHash);
      if (worker) worker.activeRequests += 1;
      await this.activate(route);
      try {
        this.recordTelemetry("route-callback-start", {
          composition_fingerprint: this.compositionFingerprint(worker),
          composition_hash: descriptor.compositionHash,
          url: route.url,
        });
        const result = await callback(route);
        this.recordTelemetry("route-callback-end", {
          agent_logs_preview: String(result?.agentLogs || "").slice(0, 2000),
          composition_fingerprint: this.compositionFingerprint(worker),
          composition_hash: descriptor.compositionHash,
          request_id: result?.requestId || null,
          response_preview: String(result?.response || "").slice(0, 1000),
          url: route.url,
        });
        return result;
      } catch (error) {
        this.recordTelemetry("route-callback-error", {
          composition_hash: descriptor.compositionHash,
          error: String(error?.message || error),
          url: route.url,
        });
        throw error;
      } finally {
        if (worker) worker.activeRequests = Math.max(0, worker.activeRequests - 1);
        if (descriptor.ephemeral) {
          await this.retireEphemeralWorker(descriptor);
        }
      }
    });
  }

  activeAgentFiles() {
    if (!this.activeRoute) return [];
    const worker = this.workers.get(this.activeRoute.compositionHash);
    const manifestPath = worker
      ? path.join(worker.compositionDirectory, "complete.json")
      : path.join(
          this.compositionRoot,
          this.activeRoute.compositionHash,
          "complete.json",
        );
    return JSON.parse(readFileSync(manifestPath, "utf8")).agents;
  }

  readActiveAgent(filename) {
    const safeName = safeAgentFilename(filename);
    if (!this.activeRoute) throw new Error("No active beta route.");
    const worker = this.workers.get(this.activeRoute.compositionHash);
    const filePath = worker
      ? path.join(worker.agentDirectory, safeName)
      : path.join(
          this.compositionRoot,
          this.activeRoute.compositionHash,
          "agents",
          safeName,
        );
    if (!existsSync(filePath)) throw new Error(`Active agent not found: ${safeName}`);
    return readFileSync(filePath, "utf8");
  }

  async stop() {
    const workers = [...this.workers.values()];
    this.workers.clear();
    await Promise.allSettled(workers.map((worker) => worker.process.stop()));
    for (const worker of workers) {
      if (worker.retiredCompositionDirectory) {
        rmSync(worker.retiredCompositionDirectory, {
          recursive: true,
          force: true,
        });
      }
    }
  }
}

export const routeManagerInternals = {
  safeAgentFilename,
  slugFromFilename,
  stackNameFromRappid,
};
