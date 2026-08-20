import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  chmodSync,
  cpSync,
  createWriteStream,
  existsSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  realpathSync,
  readdirSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { createServer } from "node:http";
import { createRequire } from "node:module";
import { homedir, tmpdir } from "node:os";
import path from "node:path";

import { testPython } from "../../_python.mjs";
import { createDriver, DriveTrace } from "./drive.mjs";
import { startModelReplay } from "./model-replay.mjs";

const require = createRequire(import.meta.url);
const REPOSITORY_ROOT = path.resolve(import.meta.dirname, "../../../..");
const BETA_ROOT = path.join(REPOSITORY_ROOT, "beta");
const GRAIL_SOURCE = path.join(REPOSITORY_ROOT, "rapp_brainstem");
const DEFAULT_START_TIMEOUT_MS = 120_000;
const EXCLUDED_GRAIL_NAMES = new Set([
  ".brainstem_book.json",
  ".brainstem_data",
  ".brainstem_model",
  ".brainstem_secret",
  ".copilot_pending",
  ".copilot_session",
  ".copilot_token",
  ".env",
  ".pytest_cache",
  "__pycache__",
  "voice.zip",
]);

export class E2EUnavailableError extends Error {
  constructor(message) {
    super(message);
    this.name = "E2EUnavailableError";
  }
}

export function isE2EUnavailable(error) {
  return error instanceof E2EUnavailableError;
}

function writeJson(filePath, value) {
  mkdirSync(path.dirname(filePath), { recursive: true, mode: 0o700 });
  const temporary = `${filePath}.${process.pid}.tmp`;
  writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, {
    mode: 0o600,
  });
  chmodSync(temporary, 0o600);
  renameSync(temporary, filePath);
}

function copyGrail(destination) {
  cpSync(GRAIL_SOURCE, destination, {
    filter(source) {
      const relative = path.relative(GRAIL_SOURCE, source);
      if (!relative) return true;
      return !relative.split(path.sep).some((part) => (
        EXCLUDED_GRAIL_NAMES.has(part) || part.endsWith(".pyc")
      ));
    },
    preserveTimestamps: true,
    recursive: true,
  });
}

function resolveElectronBinary() {
  try {
    const executable = require("electron");
    if (typeof executable === "string" && existsSync(executable)) {
      return executable;
    }
  } catch (error) {
    throw new E2EUnavailableError(
      `Electron is not installed: ${String(error.message || error)}`,
    );
  }
  throw new E2EUnavailableError(
    "Electron is not installed; run node node_modules/electron/install.js.",
  );
}

function earlyExitIsUnavailable(output) {
  return /Missing X server|could not connect to display|cannot open display|Electron failed to install|No such file or directory.*Electron/i
    .test(output);
}

async function waitFor(predicate, {
  intervalMs = 100,
  label,
  timeoutMs = DEFAULT_START_TIMEOUT_MS,
} = {}) {
  const deadline = Date.now() + timeoutMs;
  let lastError = null;
  while (Date.now() < deadline) {
    try {
      const value = await predicate();
      if (value) return value;
    } catch (error) {
      if (error instanceof E2EUnavailableError || error?.fatal) throw error;
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
  throw new Error(
    `Timed out waiting for ${label || "condition"}: ${
      String(lastError?.message || lastError || "not ready")
    }`,
  );
}

function processAlive(pid) {
  if (!Number.isInteger(pid) || pid <= 0) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function processPairs() {
  if (process.platform === "win32") {
    const result = spawnSync(
      "powershell",
      [
        "-NoProfile",
        "-Command",
        "Get-CimInstance Win32_Process | "
          + "Select-Object ProcessId,ParentProcessId | ConvertTo-Json -Compress",
      ],
      { encoding: "utf8", windowsHide: true },
    );
    if (result.status !== 0) return [];
    const parsed = JSON.parse(result.stdout || "[]");
    return (Array.isArray(parsed) ? parsed : [parsed]).map((entry) => ({
      pid: Number(entry.ProcessId),
      ppid: Number(entry.ParentProcessId),
    }));
  }
  const result = spawnSync("ps", ["-axo", "pid=,ppid="], {
    encoding: "utf8",
  });
  if (result.status !== 0) return [];
  return String(result.stdout || "")
    .trim()
    .split(/\r?\n/)
    .map((line) => line.trim().split(/\s+/).map(Number))
    .filter(([pid, ppid]) => Number.isInteger(pid) && Number.isInteger(ppid))
    .map(([pid, ppid]) => ({ pid, ppid }));
}

function descendantPids(rootPid) {
  let pairs = [];
  try {
    pairs = processPairs();
  } catch {
    return [rootPid];
  }
  const found = new Set([rootPid]);
  let changed = true;
  while (changed) {
    changed = false;
    for (const pair of pairs) {
      if (found.has(pair.ppid) && !found.has(pair.pid)) {
        found.add(pair.pid);
        changed = true;
      }
    }
  }
  return [...found].filter((pid) => pid !== process.pid);
}

function forceTerminateProcesses(pids, processGroupPid = null) {
  if (
    process.platform !== "win32"
    && Number.isInteger(processGroupPid)
    && processGroupPid > 0
  ) {
    try {
      process.kill(-processGroupPid, "SIGKILL");
    } catch {}
  }
  for (const pid of [...new Set(pids)].reverse()) {
    if (!processAlive(pid)) continue;
    try {
      process.kill(pid, "SIGKILL");
    } catch {}
  }
}

async function waitForExit(child, timeoutMs = 20_000) {
  if (child.exitCode !== null || child.signalCode !== null) return true;
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      child.removeListener("exit", onExit);
      resolve(false);
    }, timeoutMs);
    const onExit = () => {
      clearTimeout(timer);
      resolve(true);
    };
    child.once("exit", onExit);
  });
}

async function startOccupiedPort(port) {
  const server = createServer((req, res) => {
    if (req.url === "/health") {
      const body = JSON.stringify({
        agents: [],
        status: "ok",
        version: "occupied-e2e-sentinel",
      });
      res.writeHead(200, {
        "content-length": Buffer.byteLength(body),
        "content-type": "application/json",
      });
      res.end(body);
      return;
    }
    res.writeHead(404);
    res.end();
  });
  try {
    await new Promise((resolve, reject) => {
      server.once("error", reject);
      server.listen(port, "127.0.0.1", resolve);
    });
  } catch (error) {
    if (error?.code !== "EADDRINUSE") throw error;
    return {
      owned: false,
      port,
      async stop() {},
    };
  }
  const address = server.address();
  if (!address || typeof address === "string") {
    server.close();
    throw new Error("Occupied-port sentinel did not bind a TCP port.");
  }
  return {
    owned: true,
    port: address.port,
    async stop() {
      await new Promise((resolve, reject) => {
        server.close((error) => {
          if (error) reject(error);
          else resolve();
        });
        server.closeAllConnections?.();
      });
    },
  };
}

function homeSnapshot(root, { skipDescendants = [] } = {}) {
  const skipped = new Set(skipDescendants.map((candidate) => path.resolve(candidate)));
  const output = [];
  function visit(current) {
    if (!existsSync(current)) {
      output.push({ path: path.relative(homedir(), current), state: "missing" });
      return;
    }
    let stat;
    try {
      stat = lstatSync(current);
    } catch (error) {
      output.push({
        error: String(error.code || error.message || error),
        path: path.relative(homedir(), current),
      });
      return;
    }
    output.push({
      mtimeMs: Math.trunc(stat.mtimeMs),
      path: path.relative(homedir(), current) || ".",
      size: stat.size,
      type: stat.isSymbolicLink()
        ? "symlink"
        : stat.isDirectory()
          ? "directory"
          : "file",
    });
    if (
      !stat.isDirectory()
      || stat.isSymbolicLink()
      || skipped.has(path.resolve(current))
    ) {
      return;
    }
    let children = [];
    try {
      children = readdirSync(current).sort();
    } catch {
      return;
    }
    for (const child of children) visit(path.join(current, child));
  }
  visit(root);
  return output;
}

export function snapshotProtectedHomes() {
  const brainstemRoot = path.join(homedir(), ".brainstem");
  return {
    brainstem: homeSnapshot(brainstemRoot, {
      // A developer-owned Brainstem may be running while the harness executes.
      // Record these directory entries, but do not mistake its nested cache
      // churn (or the read-only venv) for a write by the isolated child.
      skipDescendants: [
        path.join(brainstemRoot, "src"),
        path.join(brainstemRoot, "venv"),
      ],
    }),
    rapp: homeSnapshot(path.join(homedir(), ".rapp")),
  };
}

export function formatProtectedHomes(snapshot) {
  const proof = Object.fromEntries(
    Object.entries(snapshot).map(([name, entries]) => [
      name,
      {
        entries: entries.length,
        listingSha256: createHash("sha256")
          .update(JSON.stringify(entries))
          .digest("hex"),
        root: entries[0] || null,
      },
    ]),
  );
  return JSON.stringify(proof);
}

export async function launch({
  env: envOverrides = {},
  modelMode = "script",
  modelScript = { steps: [] },
  initialStoreSource = null,
  occupyPort = null,
  replayCassette = null,
  scenario = "frontier",
  surgeonScript = {
    sessions: [{
      match: {},
      turns: [{ final: "Fake Brain Surgeon is ready." }],
    }],
  },
  timeoutMs = DEFAULT_START_TIMEOUT_MS,
} = {}) {
  const root = mkdtempSync(path.join(tmpdir(), `frontier-e2e-${scenario}-`));
  const paths = {
    betaHome: path.join(root, "beta-home"),
    brainstemHome: path.join(root, "brainstem-home"),
    driverMetadata: path.join(root, "beta-home", "ui-driver.json"),
    electronUserData: path.join(root, "electron-user-data"),
    grail: path.join(root, "grail", "rapp_brainstem"),
    lineageHome: path.join(root, "lineage"),
    osHome: path.join(root, "os-home"),
    root,
    stopFile: path.join(root, "control", "stop"),
    surgeonScript: path.join(root, "harness", "surgeon-script.json"),
    trace: path.join(root, "traces", `${scenario}.jsonl`),
  };
  for (const directory of [
    paths.betaHome,
    paths.brainstemHome,
    paths.electronUserData,
    path.dirname(paths.grail),
    paths.lineageHome,
    paths.osHome,
    path.dirname(paths.stopFile),
    path.dirname(paths.surgeonScript),
    path.dirname(paths.trace),
    path.join(root, "xdg-runtime"),
  ]) {
    mkdirSync(directory, { recursive: true, mode: 0o700 });
    try {
      chmodSync(directory, 0o700);
    } catch {}
  }

  let model = null;
  let occupied = null;
  let child = null;
  const observedPids = new Set();
  let processTracker = null;
  let outputStream = null;
  let output = "";
  let stopped = false;
  const electronLog = path.join(root, "logs", "electron.log");
  mkdirSync(path.dirname(electronLog), { recursive: true, mode: 0o700 });
  const trackProcessTree = () => {
    if (!child?.pid) return;
    for (const pid of descendantPids(child.pid)) observedPids.add(pid);
  };
  const stopProcessTracker = () => {
    if (!processTracker) return;
    clearInterval(processTracker);
    processTracker = null;
  };

  try {
    copyGrail(paths.grail);
    const realGrail = realpathSync(paths.grail);
    writeJson(paths.surgeonScript, surgeonScript);
    if (initialStoreSource) {
      writeJson(
        path.join(paths.betaHome, "store-source.json"),
        initialStoreSource,
      );
    }
    model = await startModelReplay({
      cassettePath: replayCassette,
      mode: modelMode,
      normalizeOptions: { roots: [root, REPOSITORY_ROOT, homedir(), tmpdir()] },
      script: modelScript,
    });
    occupied = await startOccupiedPort(occupyPort ?? 0);
    const configuredPort = occupied.port;

    const githubToken = "frontier-e2e-github-token";
    writeJson(path.join(paths.grail, ".copilot_session"), {
      endpoint: model.endpoint,
      expires_at: 4_102_444_800,
      github_token_fingerprint: createHash("sha256")
        .update(githubToken)
        .digest("hex"),
      token: "frontier-e2e-copilot-token",
    });
    if (modelMode !== "record") {
      writeFileSync(
        path.join(paths.grail, ".brainstem_model"),
        "frontier-e2e-model\n",
        { mode: 0o600 },
      );
    }

    const executable = resolveElectronBinary();
    const childEnv = {
      ...process.env,
      APPDATA: path.join(root, "appdata"),
      BRAINSTEM_BETA_E2E: "1",
      // A never-shown window is fine on macOS and Windows, but on Linux the
      // cross-origin Brainstem frame inside a hidden window never receives a
      // viewport (every rect is 0x0, the composer is "not visible"). Under
      // xvfb there IS a display — use it.
      ...(process.platform === "linux" && process.env.DISPLAY
        ? {}
        : { BRAINSTEM_BETA_HEADLESS: "1" }),
      BRAINSTEM_BETA_HOME: paths.betaHome,
      BRAINSTEM_BETA_OWN_PORT: "1",
      BRAINSTEM_BETA_PORT: String(configuredPort),
      BRAINSTEM_BETA_PYTHON: path.resolve(testPython()),
      BRAINSTEM_BETA_SOURCE_DIR: realGrail,
      BRAINSTEM_BETA_E2E_STOP_FILE: paths.stopFile,
      BRAINSTEM_BETA_SURGEON_RUNTIME: "fake",
      BRAINSTEM_BETA_SURGEON_SCRIPT: paths.surgeonScript,
      BRAINSTEM_BETA_UI_DRIVER_FILE: paths.driverMetadata,
      BRAINSTEM_HOME: paths.brainstemHome,
      ELECTRON_DISABLE_SECURITY_WARNINGS: "1",
      GITHUB_MODEL: modelMode === "record" ? "auto" : "frontier-e2e-model",
      GITHUB_TOKEN: githubToken,
      HOME: paths.osHome,
      LOCALAPPDATA: path.join(root, "localappdata"),
      NO_PROXY: "127.0.0.1,localhost",
      PORT: String(configuredPort),
      PYTHONDONTWRITEBYTECODE: "1",
      RAPP_LINEAGE_HOME: paths.lineageHome,
      TEMP: path.join(root, "tmp"),
      TMP: path.join(root, "tmp"),
      TMPDIR: path.join(root, "tmp"),
      USERPROFILE: paths.osHome,
      XDG_CACHE_HOME: path.join(root, "xdg-cache"),
      XDG_CONFIG_HOME: path.join(root, "xdg-config"),
      XDG_DATA_HOME: path.join(root, "xdg-data"),
      XDG_RUNTIME_DIR: path.join(root, "xdg-runtime"),
      no_proxy: "127.0.0.1,localhost",
      ...envOverrides,
    };
    delete childEnv.ELECTRON_RUN_AS_NODE;
    for (const directory of [
      childEnv.APPDATA,
      childEnv.LOCALAPPDATA,
      childEnv.TEMP,
      childEnv.XDG_CACHE_HOME,
      childEnv.XDG_CONFIG_HOME,
      childEnv.XDG_DATA_HOME,
    ]) {
      mkdirSync(directory, { recursive: true, mode: 0o700 });
    }

    outputStream = createWriteStream(electronLog, {
      flags: "a",
      mode: 0o600,
    });
    const args = [
      `--user-data-dir=${paths.electronUserData}`,
      ...(process.platform === "linux" ? ["--no-sandbox"] : []),
      BETA_ROOT,
    ];
    child = spawn(executable, args, {
      cwd: BETA_ROOT,
      detached: process.platform !== "win32",
      env: childEnv,
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
    });
    let spawnError = null;
    child.once("error", (error) => {
      spawnError = error;
    });
    trackProcessTree();
    processTracker = setInterval(
      trackProcessTree,
      process.platform === "win32" ? 1_000 : 250,
    );
    processTracker.unref();
    child.once("exit", stopProcessTracker);
    const capture = (chunk) => {
      const text = chunk.toString("utf8");
      output += text;
      if (output.length > 200_000) output = output.slice(-200_000);
      outputStream.write(chunk);
    };
    child.stdout.on("data", capture);
    child.stderr.on("data", capture);

    const metadata = await waitFor(() => {
      if (spawnError) {
        throw new E2EUnavailableError(
          `Electron could not start: ${String(spawnError.message || spawnError)}`,
        );
      }
      if (child.exitCode !== null || child.signalCode !== null) {
        const message = `Electron exited before the driver was ready.\n${output}`;
        if (earlyExitIsUnavailable(output)) {
          throw new E2EUnavailableError(message);
        }
        const error = new Error(message);
        error.fatal = true;
        throw error;
      }
      if (!existsSync(paths.driverMetadata)) return null;
      const value = JSON.parse(readFileSync(paths.driverMetadata, "utf8"));
      return value?.token && value?.port ? value : null;
    }, {
      label: "Frontier driver token",
      timeoutMs,
    });
    const trace = new DriveTrace({
      filePath: paths.trace,
      roots: [root, REPOSITORY_ROOT, homedir(), tmpdir()],
    });
    const driver = createDriver(metadata, { timeoutMs, trace });
    const route = await waitFor(async () => {
      const telemetry = await driver.routeTelemetry({ trace: false });
      if (!telemetry?.active_route?.url) return null;
      const response = await fetch(`${telemetry.active_route.url}/health`, {
        signal: AbortSignal.timeout(2_000),
      });
      if (!response.ok) return null;
      const health = await response.json();
      return Array.isArray(health?.agents)
        ? { health, telemetry, url: telemetry.active_route.url }
        : null;
    }, {
      label: "owned Brainstem /health",
      timeoutMs,
    });
    await driver.expect({ selector: "#input", timeoutMs, trace: false });
    // Present is not enough: the composer must be laid out and visible before
    // a scenario types into it (slow runners lay the frame out late).
    const visibleDeadline = Date.now() + timeoutMs;
    for (;;) {
      let visible = false;
      try {
        const [result] = await driver.run(
          // A condition only matches a visible element; an empty text is the
          // "is it visible" question (state names are enabled/empty/...).
          [{ action: "expect", selector: "#input", text: "" }],
          { retryMs: 0 },
        );
        visible = result?.ok === true;
      } catch {
        visible = false;
      }
      if (visible) break;
      if (Date.now() >= visibleDeadline) {
        throw new Error("The Brainstem composer never became visible after launch.");
      }
      await new Promise((resolve) => setTimeout(resolve, 200));
    }

    const logs = {
      electron: electronLog,
      modelRequests: model.requests,
      output: () => output,
      twins: path.join(paths.betaHome, "logs", "twins"),
      workers: path.join(paths.betaHome, "logs", "workers"),
    };

    const app = {
      driver,
      env: childEnv,
      health: route.health,
      logs,
      model,
      occupiedPort: occupied
        ? { owned: occupied.owned, port: occupied.port }
        : null,
      paths,
      route,
      realPaths: {
        grail: realGrail,
        root: realpathSync(paths.root),
      },
      trace,
      async stop() {
        if (stopped) return;
        stopped = true;
        const failures = [];
        trackProcessTree();
        stopProcessTracker();
        const pids = [...observedPids];
        try {
          if (child && processAlive(child.pid)) {
            writeFileSync(paths.stopFile, "stop\n", { mode: 0o600 });
            const exited = await waitForExit(child);
            if (!exited) {
              child.kill("SIGTERM");
              await waitForExit(child, 5_000);
              failures.push("Electron did not honor the E2E stop file.");
            }
          }
          await waitFor(() => (
            pids.every((pid) => !processAlive(pid)) ? true : null
          ), {
            intervalMs: 100,
            label: `Electron descendants to exit (${pids.join(", ")})`,
            timeoutMs: 10_000,
          });
        } catch (error) {
          failures.push(String(error.message || error));
        }

        const survivors = pids.filter(processAlive);
        if (survivors.length) {
          failures.push(
            `Child processes survived graceful teardown: ${survivors.join(", ")}`,
          );
          forceTerminateProcesses(survivors, child?.pid);
          try {
            await waitFor(() => (
              survivors.every((pid) => !processAlive(pid)) ? true : null
            ), {
              intervalMs: 100,
              label: `forced Electron descendants to exit (${survivors.join(", ")})`,
              timeoutMs: 5_000,
            });
          } catch (error) {
            failures.push(String(error.message || error));
          }
        }

        try {
          await Promise.allSettled([
            model?.stop(),
            occupied?.stop(),
          ]);
          if (outputStream) {
            await new Promise((resolve) => outputStream.end(resolve));
            outputStream = null;
          }
          if (process.env.BRAINSTEM_BETA_E2E_KEEP_ROOT !== "1") {
            rmSync(root, {
              force: true,
              maxRetries: 10,
              recursive: true,
              retryDelay: 100,
            });
          }
        } catch (error) {
          failures.push(`Harness cleanup failed: ${String(error.message || error)}`);
        }

        const remaining = pids.filter(processAlive);
        if (remaining.length) {
          failures.push(`Child processes survived forced teardown: ${remaining.join(", ")}`);
        }
        if (failures.length) throw new Error(failures.join("\n"));
      },
    };
    return app;
  } catch (error) {
    trackProcessTree();
    stopProcessTracker();
    const pids = [...observedPids];
    if (child && processAlive(child.pid)) {
      child.kill("SIGTERM");
      await waitForExit(child, 5_000);
    }
    forceTerminateProcesses(pids.filter(processAlive), child?.pid);
    await Promise.allSettled([model?.stop(), occupied?.stop()]);
    if (outputStream) {
      await new Promise((resolve) => outputStream.end(resolve));
      outputStream = null;
    }
    if (process.env.BRAINSTEM_BETA_E2E_KEEP_ROOT !== "1") {
      try {
        rmSync(root, {
          force: true,
          maxRetries: 10,
          recursive: true,
          retryDelay: 100,
        });
      } catch {}
    }
    throw error;
  }
}
